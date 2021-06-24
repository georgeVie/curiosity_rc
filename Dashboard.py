from os import system
import time


class Dashboard:
    def __init__(self):
        self.mode = 'User'
        self.diraction = 'N'
        self.speed = 0
        self.angle = 6
        self.calibration_value = 6
        self.auto_pilot_msg = ''
        self.info_list = []
        self.display()

    def addInfo(self, info):
        list_len = 10
        if len(self.info_list)>list_len:
            self.info_list.pop(0)
        self.info_list.append(info)
        self.display()
    
    def display(self):
        #Poor autopilot performance when using system clear
        #Increases latency
        #if self.mode != 'Auto Pilot':
            #system('clear')
        str_to_print = "MODE: {} \nSPEED: {}-{} ANGLE: {}".format(self.mode,self.diraction,self.speed,self.angle)
        print(str_to_print)
        if self.mode == 'Calibration':
            print("Center steering value: {}".format(self.calibration_value))
        if self.mode == 'Auto Pilot':
            print(self.auto_pilot_msg)
        else:
            print("*****Info*****")
            for info in self.info_list:
                print(info)

if __name__ == '__main__':
    d = Dashboard()
    for i in range(20):
        d.addInfo(i)
        d.display()
        time.sleep(1)
