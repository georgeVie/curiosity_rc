from inputs import get_gamepad
from Car import Car
from Camera import Cam
from Driver import Driver
from Dashboard import Dashboard
import concurrent.futures
import time
import sys

def main():
    #Initialize classes and controll variables
    PiDashboard = Dashboard()
    PiDashboard.addInfo("Started!")
    PiCar = Car(7, 15, 13, 11, PiDashboard)
    turned_on = True
    recording = False
    auto_pilot = False
    speed_limit = False
    try:
        #Get the controller inputs
        while turned_on:
            events = get_gamepad()
            for event in events:
                if event.code == "BTN_WEST" and event.state==0:
                    #Button pressed to calibrate the steering center angle
                    PiCar.calibrateSteer()
                elif event.code == "ABS_RZ":
                    #Button pressed to move the Car forwards
                    PiCar.setMotorSpeed(event.state,1)
                elif event.code == "ABS_Z":
                    #Button pressed to move the Car in reverse
                    PiCar.setMotorSpeed(event.state,0)
                elif event.code == "BTN_TR" and event.state==1:
                    #Button pressed to set speed limit
                    if speed_limit:
                        PiCar.setSpeedLimit(1)
                    else: 
                        PiCar.setSpeedLimit(0.70)
                    speed_limit = not speed_limit
                elif event.code == "ABS_X":
                    #Button pressed to change the steering angle
                    PiCar.setSteer(event.state)
                elif event.code == "BTN_EAST" and event.state==1:
                    #Button pressed to start/stop recording
                    PiCar.setSteer(PiCar.center_steering+1,True)
                    time.sleep(1)
                    if not recording:
                        recording = True
                        PiDashboard.mode = "Camera"
                        PiCam = Cam(PiDashboard) #Open and start camera
                        #Open a thread to run the camera and keep controll of the car
                        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                        e = executor.submit(PiCam.startRecording,PiCar)
                        executor.shutdown(wait=False)
                    else:
                        PiDashboard.addInfo("Stopping")
                        recording = False
                        PiCam.stop() #Stop the camera
                        time.sleep(1)
                        e.cancel()
                        PiDashboard.mode = "User"
                    PiCar.setSteer(PiCar.center_steering,True)
                elif event.code == "BTN_SOUTH" and event.state==1:
                    #Button pressed to delete last seconds of Recording
                    if recording:
                        PiDashboard.addInfo("Deleting frames...")
                        PiCam.deleteLastSec()

                elif event.code == "BTN_NORTH" and event.state==1:
                    #Button pressed to start/stop auto pilot
                    PiCar.setSteer(PiCar.center_steering-1,True)
                    time.sleep(1)
                    if not auto_pilot:
                        PiDriver = Driver(PiCar,PiDashboard)
                        auto_pilot = True
                        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                        e = executor.submit(PiDriver.autoPilot3)
                        executor.shutdown(wait=False)
                    else:
                        PiDashboard.addInfo("Stopping auto pilot")
                        auto_pilot = False
                        PiDriver.auto_pilot = False
                        time.sleep(2)
                        e.cancel()
                    PiCar.setSteer(PiCar.center_steering,True)
                elif event.code == "BTN_SELECT" and event.state==1:
                    #Emergency motor stop-lock
                    PiCar.motor_lock = not PiCar.motor_lock
                    PiDashboard.addInfo("Car motor lock: {}".format(PiCar.motor_lock))
                elif event.code == "BTN_START" and event.state==0:
                    #Button pressed to turn off the car
                    PiDriver.PiCar.turnOffCar()
                    turned_on = False

    except:
        print("Unexpected error:", sys.exc_info())

    finally:
        #Check if the car is turned on
        if turned_on:
            PiDashboard.addInfo("The car wasn't turned off, turning off now")
            PiCar.turnOffCar()
        if recording:
            PiDashboard.addInfo("The camera wasn't stopped, stopping now")
            PiCam.stop()
            time.sleep(1)
            e.cancel()
        if auto_pilot:
            PiDashboard.addInfo("The auto pilot wasn't stopped, stopping now")
            PiDriver.auto_pilot = False
            time.sleep(1)
            e.cancel()
        PiDashboard.addInfo("Exiting")
        exit()


if __name__ == "__main__":
    main()
