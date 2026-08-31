# connection IPs
ssh rishi@192.168.68.113          # ip for Fishi wifi at home

# Terminal for all simulation stuff integrated
cd ~/Search_Rescue_Drones/sar_drone_ws     # move into the workspace
colcon build --symlink-install             # build the ROS2 packages, symlink so edits to .py files don't need a rebuild
source install/setup.bash                  # load the freshly built workspace into this shell
ros2 launch sar_drone sim.launch.py        # start the sim launch file

# kill everything
pkill -9 -f 'px4|gz sim|gz-sim|MicroXRCEAgent|QGroundControl'   # force-kill any of these processes still running

# check everything is killed (should return empty)
ps aux | grep -E 'px4|gz|MicroXRCE|QGround' | grep -v grep      # list matching processes, empty output means the kill worked


# start of session checks
sudo nvpmodel -q                  # confirm MAXN_SUPER is the active power mode
jtop                              # open the live dashboard, press 'q' to quit
sudo jetson_clocks                # lock clocks at max, only needed before benchmarking, resets every reboot

# camera
ls /dev/video*                    # list video devices, confirms the camera is detected at all (looking for /dev/video0)
v4l2-ctl --list-formats-ext       # ask the camera what resolutions/formats it supports, confirms the driver works

# grab exactly one frame from the camera at 1080p in UYVY format and save it as a raw file
v4l2-ctl --device=/dev/video0 --set-fmt-video=width=1920,height=1080,pixelformat=UYVY \
  --stream-mmap --stream-count=1 --stream-to=test_frame.raw

# convert that raw file into a normal viewable PNG
ffmpeg -f rawvideo -pixel_format uyvy422 -video_size 1920x1080 -i test_frame.raw test_frame.png

# inference
# run YOLO11n on the captured frame and save an annotated copy with bounding boxes drawn on it
python3 -c "from ultralytics import YOLO; m = YOLO('yolo11n.pt'); m.predict('test_frame.png', save=True)"
ls ~/runs/detect/                 # find which numbered predict folder the result landed in (predict, predict-2, etc)

# pull files off the Jetson, run from WSL2, not the SSH session
scp rishi@192.168.68.113:~/runs/detect/predict/test_frame.jpg "/mnt/c/Users/royri/Documents/Thesis/"
# copies the annotated image to your Windows machine so you can open it
# scp has to run from the machine receiving the file, not from inside the Jetson SSH session

# shutdown
sudo shutdown -h now              # wait for LED to go dark before unplugging