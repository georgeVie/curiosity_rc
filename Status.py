#A better way to dispay info on the console
class Status:
    def __init__(self):
        self.mode = "None"#Mode of the car ex. User,Recording,Auto pilot
        self.angle = 6
        self.diraction = "None"
        self.speed = 0

    def printStatus(self, additional=""):
        print("[MODE] {} \n[CONTROLLS] Angle:{} Speed:{}-{}\n{}".format(self.mode,self.angle,self.diraction,self.speed,additional),end='\r')

    def printInfo(self, info):
        info = "[INFO] {}".format(info)
        self.printStatus(additional=info)