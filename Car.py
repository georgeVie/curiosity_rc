from inputs import get_gamepad
from Dashboard import Dashboard
import RPi.GPIO as GPIO
import json
import time

class Car:
    def __init__(self, servo_pin, enb_pin, in3_pin, in4_pin, dashboard):
        self.servo_pin = servo_pin
        self.enb_pin = enb_pin
        self.in3_pin = in3_pin
        self.in4_pin = in4_pin
        self.speed_limit = 1
        self.speed = 0
        self.angle = 0
        self.diraction = 'N'
        self.steer_side = 'M'
        self.motor_lock = False
        self.Dashboard = dashboard
        #Setting up the GPIO pins
        self.gpioSetup()
        #Reading the calibrated angle from settings.json
        self.readSteer()
        #Centering the steering 
        self.setSteer(self.center_steering,True)
        self.Dashboard.addInfo("The Car is ready to use")

    def __dashboard__(self):
        self.Dashboard.diraction = self.diraction
        self.Dashboard.speed = self.speed
        self.Dashboard.angle = self.steer_duty
        self.Dashboard.display()

    def gpioSetup(self):
        GPIO.setmode(GPIO.BOARD)
        #Servo
        GPIO.setup(self.servo_pin,GPIO.OUT)
        self.servo = GPIO.PWM(self.servo_pin,50)
        #Motor
        GPIO.setup(self.enb_pin,GPIO.OUT)
        GPIO.setup(self.in3_pin,GPIO.OUT)
        GPIO.setup(self.in4_pin,GPIO.OUT)
        self.motor = GPIO.PWM(self.enb_pin,1000)
        #Starting Motor and Servo
        self.servo.start(0)
        self.motor.start(0)
    
    def readSteer(self):
        with open('settings.json') as f:
            data = json.load(f)
        self.center_steering = data['angle']
        f.close()
        self.Dashboard.addInfo("Car settings have been loaded")

    def setSteer(self,value,duty=False):
        if not duty:
            #Normalizing the controller value to [0,1]
            value = value/32770
            angle = round((value*-1.2)+self.center_steering,2)
        else:
            angle = value
        self.steer_duty = angle
        self.servo.ChangeDutyCycle(self.steer_duty)
        
        # %of steering angle
        self.angle = round((abs(angle-self.center_steering)/1.2)*100)
        if angle > self.center_steering:
            self.steer_side = 'L'
        elif angle < self.center_steering:
            self.steer_side = 'R'
        else:
            self.steer_side = 'M'
        
        self.__dashboard__()

    def calibrateSteer(self):
        self.setSteer(8,True)
        time.sleep(0.5)
        self.setSteer(self.center_steering,True)
        angle = self.center_steering
        self.Dashboard.mode = 'Calibration'
        self.Dashboard.addInfo("Calibration started")
        while 1:
            events = get_gamepad()
            for event in events:
                if event.code == "ABS_HAT0X" and event.state!=0:
                    n = event.state
                    if n == -1:
                        if angle+0.05 <= 9:
                            angle = angle+0.05
                        else:
                            self.Dashboard.addInfo("Error! Too far")
                    elif n == 1:
                        if angle-0.05 >= 5.5:
                            angle = angle-0.05
                        else:
                            self.Dashboard.addInfo("Error! Too far")
                    self.Dashboard.calibration_value = round(angle,2)
                    self.setSteer(round(angle,2),True)
                if event.code == "BTN_SOUTH":
                    with open('settings.json', "w") as f:
                        json.dump({"angle": round(angle,2)}, f)
                    self.Dashboard.mode = 'User'
                    self.Dashboard.addInfo("Saved center steering value: {}".format(round(angle,2)))
                    f.close()
                    self.center_steering = round(angle,2)
                    return

    def setMotorSpeed(self,value,direction=1,duty=False):
        if not duty:
            min_duty = 35
            #Normalizing the controller value to [0,1]
            val = value/255
            val = val*self.speed_limit
            speed = round((val*(100-min_duty))+min_duty)
            if value<2:
                #if the controller input is low stop the motor
                speed = 0
        else:
            speed = value
        if self.motor_lock:
            speed = 0
        #If speed is 0 then break the motor
        if speed == 0:
            #GPIO.output(self.in3_pin,GPIO.LOW)
            #GPIO.output(self.in4_pin,GPIO.LOW)
            self.motor.ChangeDutyCycle(0)
            self.diraction = 'N'
        else:
            #Forwards
            if direction:
                GPIO.output(self.in3_pin,GPIO.LOW)
                GPIO.output(self.in4_pin,GPIO.HIGH)
                self.diraction = 'F'
            #Backwards
            else:
                GPIO.output(self.in3_pin,GPIO.HIGH)
                GPIO.output(self.in4_pin,GPIO.LOW)
                self.diraction = 'B'
            self.motor.ChangeDutyCycle(speed)
            # %of throttle speed
        
        self.speed = speed
        self.__dashboard__()

    def setSpeedLimit(self,value):
        #%of available power
        if value<=1:
            self.speed_limit = value
            self.Dashboard.addInfo("Speed limit set to: {}".format(value))
        else:
            self.Dashboard.addInfo("Error! Speed limit accepts values [0,1]")
    
    def getStatus(self):
        status = [self.diraction,self.speed,self.steer_side,self.angle]
        return status

    def turnOffCar(self):
        self.setSteer(self.center_steering-1,True)
        time.sleep(0.5)
        self.setSteer(self.center_steering,True)
        time.sleep(0.5)
        self.setSteer(self.center_steering+1,True)
        time.sleep(0.5)
        self.setSteer(self.center_steering,True)
        self.Dashboard.addInfo("Turning off the car")
        time.sleep(0.5)
        self.setSteer(0,True)
        self.setMotorSpeed(0,True)
        self.motor.stop()
        self.servo.stop()
        GPIO.cleanup()
        self.Dashboard.addInfo("Car turned off")