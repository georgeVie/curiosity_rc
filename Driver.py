from Car import Car
from Dashboard import Dashboard
from Camera import Cam
from tflite_runtime.interpreter import Interpreter
import time
import cv2
import numpy as np


class Driver:
    def __init__(self,Car,dashboard):
        #Setting up the car
        self.PiCar = Car
        self.Dashboard = dashboard
        self.auto_pilot = True

    #Initialize Auto Pilot
    def __start__(self):
        self.Dashboard.mode = "Auto Pilot"
        self.Dashboard.addInfo("Auto pilot starting")
        self.PiCam = Cam(self.Dashboard)
        self.class_names = ['L', 'M', 'N', 'R']
        self.interpreter = Interpreter(model_path='type3.tflite')
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def __predictDiraction__(self):
        #Get a frame from the camera
        frame = self.PiCam.getFrame()
        #Prepare the image array for the model
        frame = cv2.resize(frame,dsize=(85,85), interpolation = cv2.INTER_CUBIC)
        img_array = np.expand_dims(frame, 0) # Create a batch
        img_array = np.float32(img_array)
        #Get the predictions
        self.interpreter.set_tensor(self.input_details[0]['index'],img_array)
        self.interpreter.invoke()
        self.score = self.interpreter.get_tensor(self.output_details[0]['index'])
        #Get the predicted diraction and steer
        self.go = self.class_names[np.argmax(self.score)]
        self.Dashboard.auto_pilot_msg = "This image most likely belongs to {} with a {:.2f} percent confidence".format(self.class_names[np.argmax(self.score)], 100 * np.max(self.score))

    def __stop__(self):
        self.PiCar.setMotorSpeed(0,1,duty=True)
        self.PiCar.setSteer(a,duty=True)
        self.PiCam.stop()
        self.Dashboard.addInfo("Auto pilot stopped")

    def autoPilot(self):
        self.__start__()
        start = time.time()
        i = 0
        center_steering = self.PiCar.center_steering
        while self.auto_pilot:
            self.__predictDiraction__()
            confidence = np.amax(self.score)
            throttle = 70 - (15*confidence)
            if self.go == 'M':
                self.PiCar.setSteer(center_steering,duty=True)
                throttle = 67
            elif self.go == 'L':
                angle = round(1.2*confidence,2)
                self.PiCar.setSteer(center_steering+angle,duty=True)
            elif self.go == 'R':
                angle = round(1.2*confidence,2)
                self.PiCar.setSteer(center_steering-angle,duty=True)
            else:
                throttle = 0
            throttle = round(throttle)
            self.PiCar.setMotorSpeed(throttle,1,duty=True)
            i += 1
        finish = time.time()
        self.Dashboard.mode = "User"
        self.Dashboard.addInfo("Captured {} frames at {:.2f}fps".format(i,i / (finish - start)))
        self.__stop__()

if __name__ == "__main__":
    
    a = Dashboard()
    p = Car(7, 15, 13, 11, a)
    d = Driver(p,a)
    d.autoPilot()




