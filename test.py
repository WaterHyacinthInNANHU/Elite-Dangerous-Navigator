# -*-encoding:utf-8-*-
from Navigator.Controller.Controller import Controller
from Navigator.Operator.Operator import Operator
from Navigator.Operator.CompassReader import CompassReader
# c = Controller()
# print(c.region_ocr((100,100,150,150),mode='local'))
import keyboard
import cv2
import numpy as np
import pydirectinput as auto_input
import pyautogui as auto
def show_HSV():
    op = Operator()
    while True:
        # keyboard.wait(' ')
        pos = op.controller.get_mouse_position()
        frame = op.controller.grab_screen((pos[0]-50,pos[1]-50,pos[0]+50,pos[1]+50))
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)
        # cv2.imshow('hhh', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        # cv2.waitKey(1)
        tuple = hsv[50,50,:]
        val = list(tuple)
        # print(val)
        img = np.empty([100,100,3],dtype=np.uint8)
        # print(img.shape)
        for i in range(0,100):
            for j in range(0,100):
                for k in range(0,3):
                    img[i,j,k] = val[k]
        # print(img.shape)
        res = cv2.cvtColor(img,cv2.COLOR_LAB2BGR)
        print(img[0,0])
        cv2.imshow('hhh', res)
        cv2.waitKey(1)

def show_RGB():
    op = Operator()
    while True:
        # keyboard.wait(' ')
        pos = op.controller.get_mouse_position()
        frame = op.controller.grab_screen((pos[0] - 50, pos[1] - 50, pos[0] + 50, pos[1] + 50))
        rgb = np.array(frame)
        # cv2.imshow('hhh', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        # cv2.waitKey(1)
        tuple = rgb[50, 50, :]
        val = list(tuple)
        # print(val)
        img = np.empty([100, 100, 3], dtype=np.uint8)
        # print(img.shape)
        for i in range(0, 100):
            for j in range(0, 100):
                for k in range(0, 3):
                    img[i, j, k] = val[k]
        # print(img.shape)
        res = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        print(img[0, 0])
        cv2.imshow('hhh', res)
        cv2.waitKey(1)

def get_compass_jpg():
    op = Operator()
    while True:
        bia = 100
        # frame = op.controller.grab_screen((629, 730, 838, 946))
        frame = op.controller.grab_screen(None)
        filtered = cv2.inRange(frame, np.array([255 - bia, 152 - bia, 85 - bia]),
                               np.array([255 + bia, 152 + bia, 85 + bia]))
        cv2.imshow('hhh', filtered)
        cv2.waitKey(1)

def get_navpoint_jpg():
    op = Operator()
    while True:
        bia = 100  #[179 223 253]
        frame = op.controller.grab_screen((629, 730, 838, 946))
        filtered = cv2.inRange(frame, np.array([179 - bia, 223 - bia, 253 - bia]),
                               np.array([179 + bia, 223 + bia, 253 + bia]))
        cv2.imshow('hhh', filtered)
        cv2.waitKey(1)


# op = Operator()
# while True:
#     # keyboard.wait(' ')
#     pos = op.controller.get_mouse_position()
#     frame = op.controller.grab_screen((pos[0]-50,pos[1]-50,pos[0]+50,pos[1]+50))
#     gray = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
#     print(gray[50,50,:])
#     cv2.imshow('hhh', frame)
#     cv2.waitKey(1)
# while True:
#     keyboard.wait(' ')
#     pos = op.controller.get_mouse_position()

# op.controller.mouse_move_to(1535,863)


# rd = CompassReader()
# rd.controller.foucusOnTheWindow()
# while True:
#     rd.read()


# op = Operator()
# op.get_target()

# get_compass_jpg()
# get_navpoint_jpg()

# show_HSV()

# show_RGB()


# op = Operator()
# op.controller.foucusOnTheWindow()
# while True:
#     op.align_compass()

# op = Operator()
# op.controller.list_windows()

# op = Operator()
# op.start_services()
# op.controller.foucusOnTheWindow()
# auto_input.FAILSAFE = False
# while True:
#     op.align_compass()

auto_input.FAILSAFE = False
op = Operator()
op.start_services()
op.controller.foucusOnTheWindow()
op.service_change_status('service_take_off','activate')
while True:
    pass
