import os
import time
import glob
import numpy as np
from datetime import datetime
from PIL import Image
from picamera import PiCamera
from picamera.array import PiRGBArray
from Car import Car
from Dashboard import Dashboard

class Cam:
    def __init__(self,dashboard):
        #Initialize all the camera parameters and start the camera
        self.camera = PiCamera()
        self.camera.resolution = (160,128) #(width,height)
        self.camera.framerate = 40 # Frames per second
        self.rawCapture = PiRGBArray(self.camera, size=self.camera.resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="rgb", use_video_port=True) #Video port allows for better framerate but worst quality

        #Variables to controll the camera from another thread
        self.recording = True
        self.frame = None
        self.deleting = False

        self.Dashboard = dashboard
        self.Dashboard.addInfo("The camera is starting, say cheese!")
        time.sleep(2)

    def __saveImg__(self,frame,i,status):
        #Save the frame to an image file
        frame = frame[25:110] #cut the horizon and wheels
        img = Image.fromarray(frame)
        location = '{}/img{}_{}_{}_{}_{}_.jpg'.format(self.savedir,i,status[0],status[1],status[2],status[3])
        img.save(location)

    def startRecording(self,car):
        #Start to capture frames
        self.frame_num = 0
        self.car = car
        dt = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
        self.savedir = 'imgs/{}'.format(dt)
        os.mkdir(self.savedir)
        start = time.time()
        for frame in self.stream:
            self.frame = frame.array
            self.__saveImg__(self.frame,self.frame_num,self.car.getStatus())
            self.rawCapture.truncate(0)
            self.frame_num+=1
            if not self.recording:
                break

        finish = time.time()
        self.Dashboard.addInfo("Captured {} frames at {:.2f}fps".format(self.frame_num, self.frame_num / (finish - start)))

    def deleteLastSec(self,sec = 5):
        self.deleting = True
        frames_to_del = sec*self.camera.framerate #seconds*frames/second = frames
        frames_to_del = int(frames_to_del)
        fn = self.frame_num
        for i in range(frames_to_del):
            num = fn - i
            like = "{}/img{}*".format(self.savedir,num)
            for filename in glob.glob(like):
                os.remove(filename)
        self.frame_num = fn-frames_to_del if fn-frames_to_del>0 else 0
        self.Dashboard.addInfo('Deleted the last {}sec / {} frames'.format(sec,frames_to_del))
        self.deleting = False

    def getFrame(self,cut_frame=True):
        #Get a single frame from the camera
        frame = next(self.stream)
        frame = frame.array
        self.rawCapture.truncate(0)
        if cut_frame:
            frame = frame[25:110]
        return frame

    def stop(self):
        #Stop the camera and release resources
        self.Dashboard.addInfo("Stopping the camera")
        if self.recording:
            self.recording = False
            time.sleep(1)
        self.stream.close()
        self.rawCapture.close()
        self.camera.close()
    
if __name__ == "__main__":
    c = Cam()
    p = Car(7, 15, 13, 11)
    c.start(p)
    c.deleteLastSec()
    c.stop()