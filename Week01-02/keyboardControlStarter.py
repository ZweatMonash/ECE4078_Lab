# teleoperate the robot through keyboard control
# getting-started code

import math

import cv2
import numpy as np

from pynput.keyboard import Key, KeyCode, Listener
from sympy import Eq, solve, symbols


class Keyboard:
    # feel free to change the speed, or add keys to do so
    wheel_vel_forward = 100
    wheel_vel_rotation = 20

    def __init__(self, ppi=None):
        # storage for key presses
        self.directions = [False for _ in range(4)]
        self.signal_stop = False
        self.toggle = True #when false change forward_vel, true changes rotation_vel 

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
        elif key == KeyCode.from_char('i'):
            self.toggle = not self.toggle
        elif key == KeyCode.from_char('o'):
            if(self.toggle):
                self.wheel_vel_forward -= 10  
            else:
                self.wheel_vel_rotation -= 10
        elif key == KeyCode.from_char('p'):
            if(self.toggle):
                self.wheel_vel_forward += 10 
            else:
                self.wheel_vel_rotation += 10


        self.send_drive_signal()
        
    def get_drive_signal(self):           
        # translate the key presses into drive signals
        v = 0
        w = 0

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

        key_symbols = ['forward','backward','left','right','stop']
        keyboard_states = np.array(keyboard_control.directions)
        key_pressed = np.where(keyboard_states)[0]
        key_display = 'stop'
        if not (key_pressed.size == 0) :
            key_display = key_symbols[key_pressed.item()]
        else:
            key_display = key_symbols[4]
        # feel free to add more GUI texts
        cv2.putText(resized, 'PenguinPi', (15, 50), font, font_scale, font_col, line_type)
        cv2.putText(resized, key_display, (15, 100), font, font_scale, font_col, line_type)
        cv2.putText(resized, "[vl,vr] : "+str(keyboard_control.wheel_vels), (15, 150), font, font_scale, font_col, line_type)
        cv2.putText(resized, "[linear,angular] : "+str([keyboard_control.wheel_vel_forward, keyboard_control.wheel_vel_rotation] ), (15, 200), font, font_scale, font_col, line_type)
        cv2.putText(resized, "toggle : " + "linear" if(keyboard_control.toggle) else "angular", (15, 250), font, font_scale, font_col, line_type)
        cv2.putText(resized, 'i: toggle linear/angular speed adjust' , (15, 570), font, font_scale, font_col, line_type)
        cv2.putText(resized, 'o: - speed by 10' , (15, 620), font, font_scale, font_col, line_type)
        cv2.putText(resized, 'p: + speed by 10' , (15, 670), font, font_scale, font_col, line_type)
        cv2.imshow('video', resized)
        cv2.waitKey(1)

        continue
