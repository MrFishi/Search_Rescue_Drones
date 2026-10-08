"""Read DJI Lito X1 telemetry from stills, video SRT files and the MP4 `djmd` track.

Pure Python (struct, re, Pillow, pandas): no ffmpeg, no exiftool, no ROS2.

Sources, and what each one gives (see thesis_docs/dev_notes.md, 2026-10-07):
    still JPG   EXIF + XMP   GPS, altitude, gimbal pitch/yaw/roll, exposure
    video SRT   sidecar      ms timestamp, shutter, tint, ISO, colour temp, GPS, altitude
    video djmd  MP4 track    per-frame gimbal orientation (the SRT has no pitch), GPS, altitude

The `djmd` track is undocumented DJI protobuf. Field numbers below were inferred by
comparison with the SRT on the Lito X1 (zero mismatches over 15,457 frames) and may
differ on other drones or firmware: run `extract.py --check` on new footage first.

Conventions: altitudes in metres, pitch in degrees measured DOWN from the horizon
(90 = nadir). Stills store pitch with the opposite sign (XMP -90 = nadir); this module
converts it so stills and video agree.
"""
import math
import re
import struct
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

EARTH_R = 6371000.0


# --- protobuf (just enough to read djmd) -------------------------------------------

def _varint(buf, i):
    result = shift = 0
    while True:
        b = buf[i]
        i += 1
        result |= (b & 0x7F) << shift
        shift += 7
        if b < 0x80:
            return result, i


def _pb(buf):
    """Decode one protobuf message level into {field: first value}.

    Wire type 1 is read as a double and 5 as a float, which is how DJI stores its
    reals; length-delimited fields stay as bytes for the caller to descend into.
    """
    out, i = {}, 0
    while i < len(buf):
        key, i = _varint(buf, i)
        field, wire = key >> 3, key & 7
        if wire == 0:
            val, i = _varint(buf, i)
        elif wire == 1:
            val = struct.unpack_from("<d", buf, i)[0]
            i += 8
        elif wire == 5:
            val = struct.unpack_from("<f", buf, i)[0]
            i += 4
        elif wire == 2:
            n, i = _varint(buf, i)
            val = bytes(buf[i:i + n])
            i += n
        else:
            raise ValueError(f"unsupported wire type {wire}")
        out.setdefault(field, val)
    return out


def _sub(d, field):
    v = d.get(field)
    return _pb(v) if isinstance(v, bytes) else {}


def _signed(v):
    return v - (1 << 64) if isinstance(v, int) and v >= 1 << 63 else v


# --- MP4 sample extraction ----------------------------------------------------------

_CONTAINERS = {"moov", "trak", "mdia", "minf", "stbl"}


def _boxes(f, start, end):
    pos = start
    while pos + 8 <= end:
        f.seek(pos)
        size, kind = struct.unpack(">I4s", f.read(8))
        head = 8
        if size == 1:
            size = struct.unpack(">Q", f.read(8))[0]
            head = 16
        elif size == 0:
            size = end - pos
        if size < head:
            return
        yield kind.decode("latin1"), pos + head, pos + size
        pos += size


def _walk_tracks(f, start, end, cur=None):
    """Yield one dict of sample-table boxes per track in the file."""
    for kind, body, stop in _boxes(f, start, end):
        if kind == "trak":
            track = {}
            yield from _walk_tracks(f, body, stop, track)
            yield track
        elif kind in _CONTAINERS:
            yield from _walk_tracks(f, body, stop, cur)
        elif cur is not None and kind in ("stsd", "stsz", "stsc", "stco", "co64"):
            f.seek(body)
            cur[kind] = f.read(stop - body)


def read_track_samples(path, fourcc):
    """Return the raw samples of the MP4 track whose sample format is `fourcc`, or None."""
    with open(path, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        for t in _walk_tracks(f, 0, size):
            if "stsd" not in t or t["stsd"][12:16].decode("latin1") != fourcc:
                continue
            sample_size, count = struct.unpack(">II", t["stsz"][4:12])
            sizes = ([sample_size] * count if sample_size
                     else list(struct.unpack(f">{count}I", t["stsz"][12:12 + 4 * count])))
            n_stsc = struct.unpack(">I", t["stsc"][4:8])[0]
            runs = [struct.unpack(">III", t["stsc"][8 + 12 * k:20 + 12 * k]) for k in range(n_stsc)]
            if "co64" in t:
                n, = struct.unpack(">I", t["co64"][4:8])
                chunks = struct.unpack(f">{n}Q", t["co64"][8:8 + 8 * n])
            else:
                n, = struct.unpack(">I", t["stco"][4:8])
                chunks = struct.unpack(f">{n}I", t["stco"][8:8 + 4 * n])
            samples, s = [], 0
            for ci, off in enumerate(chunks, start=1):
                per = [r[1] for r in runs if r[0] <= ci][-1]
                for _ in range(per):
                    if s >= len(sizes):
                        break
                    f.seek(off)
                    samples.append(f.read(sizes[s]))
                    off += sizes[s]
                    s += 1
            return samples
    return None


# --- video: djmd track --------------------------------------------------------------

def _quat_to_pitch(x, y, z, w):
    """Gimbal pitch, degrees down from the horizon (checked: 45.4 in a 45 deg pass)."""
    return math.degrees(math.asin(max(-1.0, min(1.0, 2 * (w * y - z * x)))))


def read_djmd(path):
    """Per-frame DataFrame from the djmd track, or None if the file has no such track."""
    samples = read_track_samples(path, "djmd")
    if samples is None:
        return None
    rows, header = [], {}
    for i, s in enumerate(samples):
        try:
            top = _pb(s)
            if i == 0 and not header:
                v = _sub(_sub(top, 2), 3)
                header = {"width": v.get(1), "height": v.get(2), "fps": v.get(3)}
            fr = _sub(top, 3)
            cam, gps, att = _sub(fr, 2), _sub(fr, 3), _sub(fr, 4)
            pos = _sub(gps, 4)
            ll = _sub(pos, 1)
            q = _sub(att, 4)
            quat = [q.get(k, np.nan) for k in (1, 2, 3, 4)]
            rows.append({
                "frame": i + 1,
                "t_us": _sub(cam, 1).get(6, np.nan),
                "lat": ll.get(2, np.nan),
                "lon": ll.get(3, np.nan),
                "abs_alt_m": _signed(pos.get(2, np.nan)) / 1000,
                "rel_alt_m": _sub(gps, 5).get(1, np.nan) / 1000,
                "iso": _sub(cam, 9).get(1, np.nan),
                "ev": _sub(cam, 31).get(1, np.nan),
                "ct_k": _sub(cam, 32).get(1, np.nan),
                "qx": quat[0], "qy": quat[1], "qz": quat[2], "qw": quat[3],
                "pitch_deg": _quat_to_pitch(*quat) if not np.isnan(quat).any() else np.nan,
            })
        except (ValueError, KeyError, IndexError, struct.error):
            rows.append({"frame": i + 1})
    df = pd.DataFrame(rows)
    df["t_s"] = (df["t_us"] - df["t_us"].iloc[0]) / 1e6
    df.attrs.update(header)
    return df


# --- video: SRT ---------------------------------------------------------------------

def read_srt(path):
    """Per-frame DataFrame from a DJI .SRT sidecar."""
    text = Path(path).read_text(errors="ignore")
    rows = []
    for block in re.split(r"\n\s*\n", text.strip()):
        m = re.search(r"FrameCnt:\s*(\d+)", block)
        if not m:
            continue
        row = {"frame": int(m.group(1))}
        t = re.search(r"(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+)", block)
        row["time_local"] = t.group(1) if t else None
        for inner in re.findall(r"\[([^\]]+)\]", block):
            for k, v in re.findall(r"(\w+):\s*([^\s,\]]+)", inner):
                row[k] = v
        rows.append(row)
    df = pd.DataFrame(rows)
    out = pd.DataFrame({"frame": df["frame"], "time_local": df["time_local"]})

    def num(col):
        return pd.to_numeric(df[col], errors="coerce") if col in df else np.nan

    den = df["shutter"].str.extract(r"1/([\d.]+)")[0].astype(float) if "shutter" in df else np.nan
    out["lat"], out["lon"] = num("latitude"), num("longitude")
    out["rel_alt_m"], out["abs_alt_m"] = num("rel_alt"), num("abs_alt")
    out["iso"], out["shutter_s"] = num("iso"), 1 / den
    out["fnum"], out["ev"] = num("fnum"), num("ev")
    out["focal_mm"], out["ct_k"], out["tint"] = num("focal_len"), num("ct"), num("tint")
    return out


# --- video: merged per-frame table --------------------------------------------------

_SHARED = ["lat", "lon", "rel_alt_m", "abs_alt_m", "iso", "ev", "ct_k"]
_COLS = ["frame", "t_s", "time_local", "lat", "lon", "rel_alt_m", "abs_alt_m", "iso",
         "shutter_s", "fnum", "ev", "ct_k", "tint", "focal_mm", "pitch_deg",
         "qx", "qy", "qz", "qw", "speed_mps", "srt_present", "djmd_present"]


def ground_speed(df, window_s=0.5):
    """GPS-derived ground speed in m/s (central difference; not drone-reported)."""
    fps = 1 / df["t_s"].diff().median() if df["t_s"].notna().any() else 59.94
    k = max(1, int(round(window_s * fps)))
    x = np.radians(df["lon"]) * EARTH_R * np.cos(np.radians(df["lat"]))
    y = np.radians(df["lat"]) * EARTH_R
    dist = np.hypot(x.shift(-k) - x.shift(k), y.shift(-k) - y.shift(k))
    return dist / (2 * k / fps)


def read_clip(path):
    """Merged per-frame table for one video. SRT values win where both sources have them
    (identical, but the SRT has ms timestamps, shutter and tint); djmd supplies pitch."""
    path = Path(path)
    srt_path = next((p for p in (path.with_suffix(".SRT"), path.with_suffix(".srt"))
                     if p.exists()), None)
    srt = read_srt(srt_path) if srt_path else None
    dj = read_djmd(path)
    if srt is None and dj is None:
        return None
    if srt is not None and dj is not None and len(srt) != len(dj):
        print(f"  ! {path.name}: SRT has {len(srt)} frames, djmd {len(dj)}; using the shorter")
        n = min(len(srt), len(dj))
        srt, dj = srt.iloc[:n], dj.iloc[:n]
    base = (srt if srt is not None else dj).reset_index(drop=True).copy()
    if srt is not None and dj is not None:
        dj = dj.reset_index(drop=True)
        for c in ["t_s", "pitch_deg", "qx", "qy", "qz", "qw"]:
            base[c] = dj[c]
    elif dj is not None:
        base["time_local"] = None
    for c in _COLS:
        if c not in base:
            base[c] = np.nan
    base["srt_present"] = srt is not None
    base["djmd_present"] = dj is not None
    if base["t_s"].isna().all():
        base["t_s"] = (base["frame"] - 1) / 59.94
    base["speed_mps"] = ground_speed(base)
    out = base[_COLS]
    if dj is not None:
        out.attrs.update(dj.attrs)
    return out


def check_srt_vs_djmd(path):
    """Count frames where djmd disagrees with the SRT, per shared field. None if a
    source is missing. Run this on any new drone or firmware before trusting djmd."""
    path = Path(path)
    srt_path = next((p for p in (path.with_suffix(".SRT"), path.with_suffix(".srt"))
                     if p.exists()), None)
    dj = read_djmd(path)
    if srt_path is None or dj is None:
        return None
    srt = read_srt(srt_path)
    n = min(len(srt), len(dj))
    tol = {"lat": 1.1e-6, "lon": 1.1e-6, "rel_alt_m": 1.1e-3, "abs_alt_m": 1.1e-3,
           "iso": 0.5, "ev": 0.06, "ct_k": 0.5}
    res = {"frames_srt": len(srt), "frames_djmd": len(dj)}
    for c in _SHARED:
        diff = (srt[c].iloc[:n].to_numpy() - dj[c].iloc[:n].to_numpy())
        res[c] = int((~(np.abs(diff) <= tol[c])).sum())
    return res


def clip_summary(df, path):
    """One manifest-style row per clip (the P2.4 granularity)."""
    path = Path(path)
    pitch = df["pitch_deg"]
    sh = df["shutter_s"]
    one_hz = df.iloc[:: max(1, int(round(1 / df["t_s"].diff().median())))] \
        if df["t_s"].notna().any() else df
    x = np.radians(one_hz["lon"]) * EARTH_R * np.cos(np.radians(one_hz["lat"]))
    y = np.radians(one_hz["lat"]) * EARTH_R
    return {
        "clip": path.name,
        "srt_present": bool(df["srt_present"].iloc[0]),
        "djmd_present": bool(df["djmd_present"].iloc[0]),
        "frames": len(df),
        "duration_s": round(float(df["t_s"].iloc[-1]), 2),
        "width": df.attrs.get("width"), "height": df.attrs.get("height"),
        "fps": round(df.attrs["fps"], 2) if df.attrs.get("fps") else np.nan,
        "start_local": df["time_local"].iloc[0],
        "lat_start": df["lat"].iloc[0], "lon_start": df["lon"].iloc[0],
        "rel_alt_start_m": df["rel_alt_m"].iloc[0], "rel_alt_end_m": df["rel_alt_m"].iloc[-1],
        "rel_alt_min_m": df["rel_alt_m"].min(), "rel_alt_max_m": df["rel_alt_m"].max(),
        "pitch_mean_deg": pitch.mean(), "pitch_min_deg": pitch.min(),
        "pitch_max_deg": pitch.max(),
        "pitch_const": bool(pitch.std() < 1.0) if pitch.notna().any() else np.nan,
        "path_len_m": round(float(np.hypot(x.diff(), y.diff()).sum()), 1),
        "speed_mean_mps": df["speed_mps"].mean(), "speed_max_mps": df["speed_mps"].max(),
        "iso_max": df["iso"].max(),
        "shutter_slowest_s": sh.max(), "shutter_fastest_s": sh.min(),
        "ct_mean_k": df["ct_k"].mean(),
    }


# --- stills -------------------------------------------------------------------------

def _xmp(path):
    with open(path, "rb") as f:
        head = f.read(300000)
    i, j = head.find(b"<x:xmpmeta"), head.find(b"</x:xmpmeta>")
    if i < 0 or j < 0:
        return {}
    return dict(re.findall(r'(?:drone-dji|xmp|tiff):(\w+)="([^"]*)"', head[i:j].decode("utf8", "ignore")))


def read_still(path):
    """One-row dict for a still (EXIF for exposure, XMP for position and gimbal)."""
    path = Path(path)
    x = _xmp(path)
    im = Image.open(path)
    exif = im.getexif()
    ifd = exif.get_ifd(0x8769)

    def f(key):
        try:
            return float(x[key])
        except (KeyError, ValueError):
            return np.nan

    pitch = f("GimbalPitchDegree")
    return {
        "file": path.name,
        "time_local": ifd.get(0x9003),
        "width": im.width, "height": im.height,
        "lat": f("GpsLatitude"), "lon": f("GpsLongitude"),
        "rel_alt_m": f("RelativeAltitude"), "abs_alt_m": f("AbsoluteAltitude"),
        "pitch_deg": -pitch,
        "gimbal_yaw_deg": f("GimbalYawDegree"), "gimbal_roll_deg": f("GimbalRollDegree"),
        "flight_yaw_deg": f("FlightYawDegree"),
        "speed_x_mps": f("FlightXSpeed"), "speed_y_mps": f("FlightYSpeed"),
        "speed_z_mps": f("FlightZSpeed"),
        "iso": ifd.get(0x8827), "shutter_s": ifd.get(0x829A), "fnum": ifd.get(0x829D),
        "ev": ifd.get(0x9204), "focal_mm": ifd.get(0x920A), "focal_35mm": ifd.get(0xA405),
        "ct_k": f("WhiteBalanceCCT"), "sensor_temp_c": f("SensorTemperature"),
        "make": exif.get(271), "model": exif.get(272),
    }
