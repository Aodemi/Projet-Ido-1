import pigpio
import threading
import time
 
 
 
 
seq_full = [
    [1,0,0,1],
    [1,1,0,0],
    [0,1,1,0],
    [0,0,1,1]
]
M1,M2,M3,M4 = 8,9,10,7
EN1, IN1, IN2 = 16, 20, 21
EN2, IN3, IN4 = 16, 27, 17
dc_motor_args1 = {
    "EN" : EN1,
    "IN-1" : IN1,
    "IN-2" : IN2
   
}
dc_motor_args2 = {
    "EN" : EN2,
    "IN-1" : IN3,
    "IN-2" : IN4
}
step_motor_args = {
    "M1": M1,
    "M2" : M2,
    "M3" : M3,
    "M4" : M4,
    "seq" : seq_full
}
 
 
pi = pigpio.pi()
 
class StepMotor(threading.Thread):
    def __init__(self, group = None, target = None, name = None, args = ..., kwargs = None, *, daemon = None, pi = None, step_args = {} ):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.pi = pi
        self.step_args = step_args
        
    def run(self):
        self.kill = False
        self.pi.set_mode(self.step_args["M1"],pigpio.OUTPUT)
        self.pi.set_mode(self.step_args["M2"],pigpio.OUTPUT)
        self.pi.set_mode(self.step_args["M3"],pigpio.OUTPUT)
        self.pi.set_mode(self.step_args["M4"],pigpio.OUTPUT)
        self.pi.write(self.step_args["M1"], 0)
        self.pi.write(self.step_args["M2"], 0)
        self.pi.write(self.step_args["M3"], 0)
        self.pi.write(self.step_args["M4"], 0)
        count = 0
        while count < (2 * 2048):
            for step in self.step_args["seq"]:
                self.pi.write(self.step_args["M1"], step[0])
                self.pi.write(self.step_args["M2"], step[1])
                self.pi.write(self.step_args["M3"], step[2])
                self.pi.write(self.step_args["M4"], step[3])
                count += 1
                time.sleep(0.002)
            if count == 2048:
                self.step_args["seq"].reverse()
        if count > (2 * 2048):
            count = 0
        self.pi.write(self.step_args["M1"], 0)
        self.pi.write(self.step_args["M2"], 0)
        self.pi.write(self.step_args["M3"], 0)
        self.pi.write(self.step_args["M4"], 0)
        self.kill = True
 
 
 
class DcMotor(threading.Thread):
    def __init__(self, group = None, target = None, name = None, args = ..., kwargs = None, *, daemon = None, pi = None, dc_args= {} ):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.pi = pi
        self.dc_args = dc_args
        self.kill = False
    def run(self):
        self.pi.set_mode(self.dc_args["EN"],pigpio.OUTPUT)
        self.pi.set_mode(self.dc_args["IN-1"],pigpio.OUTPUT)
        self.pi.set_mode(self.dc_args["IN-2"],pigpio.OUTPUT)
        self.pi.set_PWM_range(self.dc_args["EN"], 255)
        # while not self.kill:
        #     self.pi.write(self.dc_args["IN-1"], 0)
        #     self.pi.write(self.dc_args["IN-2"], 1)
        #     self.pi.set_PWM_dutycycle(self.dc_args["EN"],200)
        #     time.sleep(0.15)
        #     self.pi.write(self.dc_args["IN-1"], 1)
        #     self.pi.write(self.dc_args["IN-2"], 0)
        # self.pi.write(self.dc_args["IN-1"], 0)
        # self.pi.write(self.dc_args["IN-2"], 0)
        # self.pi.write(self.dc_args["EN"], 0)
class DcMotorWave(DcMotor):
    def run(self):
        super().run()
        while not self.kill:
            # # Sens de rotation
            
            self.pi.write(self.dc_args["IN-1"], 1)
            self.pi.write(self.dc_args["IN-2"], 0)

            # Envoyer le courant
            #pi.write(EN1, 1)
            time.sleep(0.30)
            self.pi.write(self.dc_args["IN-1"], 0)
            self.pi.write(self.dc_args["IN-2"], 1)
            time.sleep(0.28)
        self.pi.write(self.dc_args["IN-1"], 0)
        self.pi.write(self.dc_args["IN-2"], 0)
        self.pi.write(self.dc_args["EN"], 0)
class DcMotorFish(DcMotor):
    def run(self):
        super().run()
        while not self.kill:
            # # Sens de rotation
            
            self.pi.write(self.dc_args["IN-1"], 1)
            self.pi.write(self.dc_args["IN-2"], 0)

            # Envoyer le courant
            #pi.write(EN1, 1)
            time.sleep(5.0)
            self.pi.write(self.dc_args["IN-1"], 0)
            self.pi.write(self.dc_args["IN-2"], 1)
            time.sleep(5.0)
        self.pi.write(self.dc_args["IN-1"], 0)
        
        self.pi.write(self.dc_args["IN-2"], 0)
        self.pi.write(self.dc_args["EN"], 0)

class Button:
    def __init__(self, pin,pi) -> None:
        self.pi = pi
        self.pin = pin
        self.isPressed = False
        self.count = 0
        pi.set_mode(pin,pigpio.INPUT)
        pi.set_pull_up_down(pin,pigpio.PUD_UP)
       
    def detectPress(self): # need to be called every loop to detect key presses
        if self.pi.read(self.pin) == 0:
            if not self.isPressed:
                self.count += 1
                if self.count >= 4:
                    self.isPressed = True
        else:
            self.count = 0
            self.isPressed = False
    def getState(self): # gets the current status of the button
        return self.isPressed
 
 
#off_button = Button(pin=21,pi=pi) unused
 
step_motor_tread = StepMotor(pi=pi, step_args=step_motor_args)
dc_motor_thread1 = DcMotorWave(pi=pi,dc_args=dc_motor_args1)
#dc_motor_thread2 = DcMotorFish(pi=pi,dc_args=dc_motor_args2) Unused

threads = [step_motor_tread,dc_motor_thread1]
 
 
for i in threads: #starts the threads
    i.start()
print("threads started")
 
 
try:
    while True:
        if step_motor_tread.kill:
            step_motor_tread.run()
        # off_button.detectPress()
        # if off_button.getState():
        #     break
        time.sleep(1)
except KeyboardInterrupt:
    pass
 
 
 
#check if all threads have been ended
threads_amount = len(threads)
all_threads_ended_number = threading.active_count() - threads_amount
for i in threads:
    i.kill = True
while threading.active_count() > all_threads_ended_number:
    print("waiting for {0} threads".format(str(threading.active_count() - all_threads_ended_number)))
    time.sleep(1)
 
 
print("Program end")