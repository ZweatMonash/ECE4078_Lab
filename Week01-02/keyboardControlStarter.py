# teleoperate the robot through keyboard control
# getting-started code

from pynput.keyboard import Key, Listener, KeyCode
import cv2
import numpy as np
import math
from sympy import symbols, Eq, solve

class Keyboard:
    # feel free to change the speed, or add keys to do so
    wheel_vel_forward = 100
    wheel_vel_rotation = 20

    def __init__(self, ppi=None):
        # storage for key presses
        self.directions = [False for _ in range(4)]
        self.signal_stop = False 

        # connection to PenguinPi robot
        self.ppi = ppi
        self.wheel_vels = [0, 0]

        self.listener = Listener(on_press=self.on_press).start()

    def on_press(self, key):
        print(key)
        self.directions = [False for _ in range(4)]
        self.signal_stop = False
        # use arrow keys to drive, space key to stop
        # feel free to add more keys
        if key == Key.up:
            self.directions[0] = True
        elif key == Key.down:
            self.directions[1] = True
        elif key == Key.left:
            self.directions[2] = True
        elif key == Key.right:
            self.directions[3] = True
        elif key == Key.space:
            self.signal_stop = True

        self.send_drive_signal()
        
    def get_drive_signal(self):           
        # translate the key presses into drive signals


        if self.signal_stop:
            v = 0
            w = 0  
        elif self.directions[0]:
            v = self.wheel_vel_forward
            w =  0 
        elif self.directions[1]:
            v = -self.wheel_vel_forward
            w = 0   
        elif self.directions[2]:
            v = 0
            w =  self.wheel_vel_rotation
        elif self.directions[3]:
            v = 0
            w = -self.wheel_vel_rotation   

        # compute drive_forward and drive_rotate using wheel_vel_forward and wheel_vel_rotation
        # drive_forward = wheel_vel_forward #v
        # drive_rotate = wheel_vel_rotation #omega

        vr, vl = symbols('vr vl')
        eq1 = Eq(vr + vl - v)
        eq2 = Eq(vr - vl - w)
        solution = solve((eq1,eq2),(vr, vl))

        # translate drive_forward and drive_rotate into left_speed and right_speed
        left_speed = solution[vl]
        right_speed = solution[vr]

        print("left v:", left_speed, "   right v:",right_speed )
        return left_speed, right_speed
    
    def send_drive_signal(self):
        if not self.ppi is None:
            lv, rv = self.get_drive_signal()
            lv, rv = self.ppi.set_velocity(lv, rv)
            self.wheel_vels = [lv, rv]
            
    def latest_drive_signal(self):
        return self.wheel_vels
    

if __name__ == "__main__":
    import penguinPiC
    ppi = penguinPiC.PenguinPi()

    keyboard_control = Keyboard(ppi)

    cv2.namedWindow('video', cv2.WINDOW_NORMAL);
    cv2.setWindowProperty('video', cv2.WND_PROP_AUTOSIZE, cv2.WINDOW_AUTOSIZE);

    while True:
        # font display options
        font = cv2.FONT_HERSHEY_SIMPLEX
        location = (0, 0)
        font_scale = 1
        font_col = (255, 255, 255)
        line_type = 2

        # get velocity of each wheel
        wheel_vels = keyboard_control.latest_drive_signal();
        L_Wvel = wheel_vels[0]
        R_Wvel = wheel_vels[1]

        # get current camera frame
        curr = ppi.get_image()

        # scale to 144p
        # feel free to change the resolution
        resized = cv2.resize(curr, (960, 720), interpolation = cv2.INTER_AREA)

        # feel free to add more GUI texts
        cv2.putText(resized, 'PenguinPi', (15, 50), font, font_scale, font_col, line_type)

        cv2.imshow('video', resized)
        cv2.waitKey(1)

        continue
