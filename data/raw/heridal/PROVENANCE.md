# HERIDAL Dataset: Provenance

## Source
- Mirror: Zenodo record 5662351, "HERIDAL dataset in keras-retinanet PASCAL VOC format"
- Uploader: Pasi Pyrrö
- DOI: 10.5281/zenodo.5662351
- URL: https://zenodo.org/records/5662351
- Direct file: https://zenodo.org/records/5662351/files/heridal_keras_retinanet_voc.zip
- Repackaged for use with the Accenture/AIR detector (https://github.com/Accenture/AIR)

## Original dataset
- HERIDAL database, IPSAR project, University of Split (FESB)
- Original page: http://ipsar.fesb.unist.hr/HERIDAL database.html
- Citation: Bozic-Stulic, D., Marusic, Z., Gotovac, S. "Deep Learning Approach on
  Aerial Imagery in Supporting Land Search and Rescue Missions." International
  Journal of Computer Vision, 2019.
- License: CC BY 3.0 Unported (per IPSAR page)

## File
- Filename: heridal_keras_retinanet_voc.zip
- Size: 8,311,735,812 bytes (7.74 GiB)
- MD5: c2b625ae986898a870b9d8a907aefe45 (checked against Zenodo's published metadata — matches)
- SHA256: 63ea51b29d67f9b95cc600674c6ccfa719688594404b5311a9164fb41a0448a3

## Download
- Date: 2026-09-04
- Downloaded via: wget, WSL2 Ubuntu 24.04

## Content (per project execution guide)
- 1546 train + 101 test full-size 4000x3000 images, VOC XML annotations
- Single class: person
- 3229 annotations total
- The ~68k pre-cropped patches in the original release are not used here — this
  full-image VOC set is the part relevant to detection training.
