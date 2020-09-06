from ..Controller.Controller import Controller, Pid
from .CompassReader import CompassReader
import numpy as np
import cv2
from pathlib import Path
from json import load
import threading
from time import sleep
import os
import pyautogui as auto


class Operator(object):
    def __init__(self):
        self.root_path = str(Path(__file__).parent)
        self.tags_dir = self.root_path + '\\tags\\'
        with open(self.root_path + '\\..\\configuration.json', 'r', encoding='utf8')as fp:
            self.configuration = load(fp)['Operator']
        self.LPF_pre_val = [0, 0, 0, 0, 0]

        #asyncio parameters
        self.controller = Controller()
        self.compass_reader = CompassReader()
        self.pid_x = Pid(self.configuration['pid_x']['p'],self.configuration['pid_x']['i'],self.configuration['pid_x']['d'])
        self.pid_y = Pid(self.configuration['pid_y']['p'],self.configuration['pid_y']['i'],self.configuration['pid_y']['d'])
        self.compass = {"center_compass":None, "center_navpoint":None, "is_front":None}
        self.service_status = {"service_read_compass":{"status": "sleep"},
                               "service_joystick":{"status":"sleep","frequency_x":0,"frequency_y":0,"x_key":'',"y_key":''},
                               "service_align_compass": {"status": "sleep"},
                               "service_take_off": {"status": "sleep"}
                               }
        self.semaphore = threading.Semaphore(1)
        pass

    def LPF(self, num, value, rate):
        res = value * rate + self.LPF_pre_val[num] * (1 - rate)
        self.LPF_pre_val[num] = value
        return res

    def start_services(self):
        threading.Thread(target=self.service_read_compass, args=()).start()
        threading.Thread(target=self.service_joystick, args=()).start()
        threading.Thread(target=self.service_align_compass, args=()).start()
        threading.Thread(target=self.service_take_off, args=()).start()

    def euclidean_distance(self, coords1, coords2):
        dist = 0
        for (x, y) in zip(coords1, coords2):
            dist += (x - y) ** 2
        return dist ** 0.5

    def getTag(self,name,confidence=0.9):
        path = self.tags_dir + name + '.jpg'
        return auto.locateCenterOnScreen(path,grayscale=False,confidence=confidence)

    def service_change_status(self,service,new_status):
        self.semaphore.acquire()
        self.service_status[service]["status"] = new_status
        self.semaphore.release()

    def service_read_compass(self):
        while True:
            self.semaphore.acquire()
            status = self.service_status['service_take_off']["status"]
            interval = self.configuration['service_sleep_interval']
            self.semaphore.release()
            if status is 'activate':
                center_compass, center_navpoint, is_front = self.compass_reader.read()
                self.semaphore.acquire()
                self.compass['center_compass'] = center_compass
                self.compass['center_navpoint'] = center_navpoint
                self.compass['is_front'] = is_front
                self.semaphore.release()
            elif status is 'sleep':
                sleep(interval)

    def service_joystick(self):
        while True:
            self.semaphore.acquire()
            status = self.service_status['service_take_off']["status"]
            interval = self.configuration['service_sleep_interval']
            frequency_x = self.service_status['service_joystick']["frequency_x"]
            frequency_y = self.service_status['service_joystick']["frequency_y"]
            x_key = self.service_status['service_joystick']["x_key"]
            y_key = self.service_status['service_joystick']["y_key"]
            self.semaphore.release()
            if status is 'activate':
                if frequency_x is not 0:
                    if x_key is "right":
                        self.controller.key_depress('right')
                        sleep(1 / frequency_x)
                        self.controller.key_release('right')
                    else:
                        self.controller.key_depress('left')
                        sleep(1 / frequency_x)
                        self.controller.key_release('left')
                if frequency_y is not 0:
                    if y_key is "down":
                        self.controller.key_depress('down')
                        sleep(1 / frequency_y)
                        self.controller.key_release('down')
                    else:
                        self.controller.key_depress('up')
                        sleep(1 / frequency_y)
                        self.controller.key_release('up')
            elif status is 'sleep':
                sleep(interval)

    def service_align_compass(self):
        while True:
            self.semaphore.acquire()
            status = self.service_status['service_take_off']["status"]
            interval = self.configuration['service_sleep_interval']
            self.semaphore.release()
            if status is 'activate':
                self.semaphore.acquire()
                center_compass, center_navpoint, is_front = self.compass['center_compass'], self.compass[
                    'center_navpoint'], self.compass['is_front']
                self.semaphore.release()
                if center_compass is not None and center_navpoint is not None and is_front is not None:
                    error_x = center_compass[0] - center_navpoint[0]
                    error_y = center_compass[1] - center_navpoint[1]
                    distance = self.euclidean_distance(center_navpoint, center_compass)
                    distance_teminate = self.configuration["align_terminate_error_by_pixel"]

                    if distance > distance_teminate or not is_front:
                        if not is_front:
                            if error_y > 0:
                                self.controller.key_depress('up')
                            else:
                                self.controller.key_depress('down')
                        else:
                            if error_x < 0:
                                self.controller.key_release('left')
                                self.controller.key_depress('right')
                            else:
                                self.controller.key_release('right')
                                self.controller.key_depress('left')
                            if error_y < 0:
                                self.controller.key_release('up')
                                self.controller.key_depress('down')
                            else:
                                self.controller.key_release('down')
                                self.controller.key_depress('up')
                    else:
                        self.controller.key_release('up')
                        self.controller.key_release('down')
                        self.controller.key_release('left')
                        self.controller.key_release('right')
                else:
                    self.controller.key_release('up')
                    self.controller.key_release('down')
                    self.controller.key_release('left')
                    self.controller.key_release('right')
            elif status is 'sleep':
                sleep(interval)


    def service_take_off(self):
        while True:
            self.semaphore.acquire()
            status = self.service_status['service_take_off']["status"]
            interval = self.configuration['service_sleep_interval']
            self.semaphore.release()
            if status is 'activate':
                while self.getTag('AUTO LAUNCH') is None:
                    self.controller.type('down')
                self.controller.type(' ')

                #sleep
                self.semaphore.acquire()
                self.service_status['service_take_off']["status"] = 'sleep'
                self.semaphore.release()
            elif status is 'sleep':
                sleep(interval)


























    # def align_compass(self):
    #     self.semaphore.acquire()
    #     center_compass, center_navpoint, is_front = self.compass['center_compass'], self.compass['center_navpoint'], self.compass['is_front']
    #     self.semaphore.release()
    #     if center_compass is not None and center_navpoint is not None and is_front is not None:
    #         error_x = center_compass[0] - center_navpoint[0]
    #         error_y = center_compass[1] - center_navpoint[1]
    #         distance = self.euclidean_distance(center_navpoint,center_compass)
    #         distance_teminate = self.configuration["align_terminate_error_by_pixel"]
    #         center_x = self.configuration['center_of_screen'][0]
    #         center_y = self.configuration['center_of_screen'][1]
    #         if distance > distance_teminate or not is_front:
    #             if not is_front:
    #                 self.controller.move_to(center_x, center_y)
    #                 self.controller.key_depress('up')
    #             else:
    #                 self.controller.key_release('up')
    #                 # self.controller.click(center_x, center_y)
    #                 self.pid_x.target = center_compass[0]
    #                 x = -self.pid_x.predict(center_navpoint[0])
    #                 self.pid_y.target = center_compass[1]
    #                 y = -self.pid_y.predict(center_navpoint[1])
    #                 self.controller.move_to(center_x + x, center_y + y)
    #                 print(error_x,error_y)
    #                 print('pridict',x,y)

    # def align_compass(self):
    #     self.semaphore.acquire()
    #     center_compass, center_navpoint, is_front = self.compass['center_compass'], self.compass['center_navpoint'], self.compass['is_front']
    #     self.semaphore.release()
    #     if center_compass is not None and center_navpoint is not None and is_front is not None:
    #         error_x = center_compass[0] - center_navpoint[0]
    #         error_y = center_compass[1] - center_navpoint[1]
    #         distance = self.euclidean_distance(center_navpoint,center_compass)
    #         distance_teminate = self.configuration["align_terminate_error_by_pixel"]
    #         center_x = self.configuration['center_of_screen'][0]
    #         center_y = self.configuration['center_of_screen'][1]
    #         if distance > distance_teminate or not is_front:
    #             if not is_front:
    #                 self.controller.key_depress('up')
    #                 self.controller.move_to(center_x, center_y)
    #             else:
    #                 self.controller.key_release('up')
    #                 self.controller.click(center_x, center_y)
    #                 self.pid_x.target = center_compass[0]
    #                 x = self.pid_x.predict(center_navpoint[0])
    #                 self.pid_y.target = center_compass[1]
    #                 y = self.pid_y.predict(center_navpoint[1])
    #
    #                 self.semaphore.acquire()
    #
    #                 self.service_status['service_joystick']["frequency_x"] = x
    #                 if x < 0:
    #                     self.service_status['service_joystick']["x_key"] = 'right'
    #                 else:
    #                     self.service_status['service_joystick']["x_key"] = 'left'
    #
    #                 self.service_status['service_joystick']["frequency_y"] = y
    #                 if y < 0:
    #                     self.service_status['service_joystick']["y_key"] = 'down'
    #                 else:
    #                     self.service_status['service_joystick']["y_key"] = 'up'
    #
    #                 self.semaphore.release()
    #
    #                 print(error_x,error_y)
    #                 print('pridict',center_x + x,center_y + y)
