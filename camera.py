from pynq.overlays.base import BaseOverlay
from pynq.lib.video import *
import os
import cv2
import numpy as np
import time as t

# monitor (output) frame buffer size
frame_out_w = 1920
frame_out_h = 1080
# camera (input) configuration
frame_in_w = 640
frame_in_h = 480

def setup():
    global frame_out_w
    global frame_out_h
    global frame_in_w
    global frame_in_h

    base = BaseOverlay("base.bit")

    # monitor configuration: 640*480 @ 60Hz
    Mode = VideoMode(640,480,24)
    hdmi_out = base.video.hdmi_out
    hdmi_out.configure(Mode,PIXEL_BGR)
    hdmi_out.start()

    os.environ["OPENCV_LOG_LEVEL"]="SILENT"
    # initialize camera from OpenCV

    videoIn = cv2.VideoCapture(0)
    videoIn.set(cv2.CAP_PROP_FRAME_WIDTH, frame_in_w)
    videoIn.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_in_h)

    print("Capture device is open: " + str(videoIn.isOpened()))
    
    return hdmi_out

def get_frame(videoIn):
    global frame_out_w
    global frame_out_h
    global frame_in_w
    global frame_in_h

    # Capture webcam image
    ret,frame_vga = videoIn.read()

    if (ret):
        return frame_vga[0:frame_in_h-1,frame_in_w-1:0:-1,:]
    return False

def clean_up(videoIn, hdmi_out):
    hdmi_out.stop()
    del hdmi_out
    videoIn.release()
    
def run_capture(videoIn, hdmi_out):
    global frame_out_w
    global frame_out_h
    global frame_in_w
    global frame_in_h

    try:
        while 1:
            # Capture webcam image
            ret,frame_vga = videoIn.read()

            # Display webcam image via HDMI Out
            if (ret):      
                outframe = hdmi_out.newframe()
                outframe[0:frame_in_h-1,0:frame_in_w-1,:] = frame_vga[0:frame_in_h-1,frame_in_w-1:0:-1,:]
                hdmi_out.writeframe(outframe)
            else:
                raise RuntimeError("Failed to read from camera.")

            print("Picture Update")
    finally:
        hdmi_out.stop()
        del hdmi_out
        videoIn.release()