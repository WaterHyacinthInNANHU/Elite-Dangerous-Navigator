from ..Controller.Controller import Controller, Pid
import numpy as np
import cv2
from pathlib import Path
from json import load


class CompassReader(object):
    def __init__(self):
        self.root_path = str(Path(__file__).parent)
        with open(self.root_path + '\\..\\configuration.json', 'r', encoding='utf8')as fp:
            self.configuration = load(fp)['CompassReader']
        for name in self.configuration['templates']:
            self.configuration['templates'][name] = cv2.imread(self.root_path + self.configuration['templates'][name],
                                                               cv2.CV_8U)
            pass
        self.controller = Controller()
        self.read_compass_region = None
        self.compass = {"center_compass":None, "center_navpoint":None, "is_front":None}
        pass

    def get_compass(self, image=None, region=None):
        # parameters
        parameters = self.configuration['get_compass']
        bia = parameters['bia']
        filter_threshold = parameters['filter_threshold']
        center_bia_x = parameters['center_bia_x']
        center_bia_y = parameters['center_bia_y']
        temp = self.configuration['templates']['compass']
        xsize = temp.shape[0]
        ysize = temp.shape[1]
        # detect the center
        if image is None:
            frame = self.controller.grab_screen(region)
        else:
            if region is not None:
                frame = image[region[0]:region[2], region[1]:region[3], :]
            else:
                frame = image
        filtered = cv2.inRange(frame,
                               np.array([filter_threshold[0] - bia,
                                         filter_threshold[1] - bia,
                                         filter_threshold[2] - bia]),
                               np.array([filter_threshold[0] + bia,
                                         filter_threshold[1] + bia,
                                         filter_threshold[2] + bia]))
        res = cv2.matchTemplate(filtered, temp, cv2.TM_CCOEFF_NORMED)
        loc = cv2.minMaxLoc(res)
        left_up = (loc[3][0], loc[3][1])
        right_down = (loc[3][0] + xsize, loc[3][1] + ysize)
        center = (left_up[0] + center_bia_x, left_up[1] + center_bia_y)
        confidence = loc[1]
        return left_up, right_down, center, confidence, frame

    def get_navpoint_back(self, image=None, region=None):
        # parameters
        parameters = self.configuration['get_navpoint_back']
        bia = parameters['bia']
        filter_threshold = parameters['filter_threshold']
        center_bia_x = parameters['center_bia_x']
        center_bia_y = parameters['center_bia_y']
        temp = self.configuration['templates']['navpoint_back']
        xsize = temp.shape[0]
        ysize = temp.shape[1]
        # detect the center
        if image is None:
            frame = self.controller.grab_screen(region)
        else:
            if region is not None:
                frame = image[region[1]:region[3], region[0]:region[2], :]
            else:
                frame = image
        filtered = cv2.inRange(frame,
                               np.array([filter_threshold[0] - bia,
                                         filter_threshold[1] - bia,
                                         filter_threshold[2] - bia]),
                               np.array([filter_threshold[0] + bia,
                                         filter_threshold[1] + bia,
                                         filter_threshold[2] + bia]))
        res = cv2.matchTemplate(filtered, temp, cv2.TM_CCOEFF_NORMED)
        loc = cv2.minMaxLoc(res)
        left_up = (loc[3][0], loc[3][1])
        right_down = (loc[3][0] + xsize, loc[3][1] + ysize)
        center = (left_up[0] + center_bia_x, left_up[1] + center_bia_y)
        confidence = loc[1]
        return left_up, right_down, center, confidence, frame

    def get_navpoint_front(self, image=None, region=None):
        # parameters
        parameters = self.configuration['get_navpoint_front']
        bia = parameters['bia']
        filter_threshold = parameters['filter_threshold']
        center_bia_x = parameters['center_bia_x']
        center_bia_y = parameters['center_bia_y']
        temp = self.configuration['templates']['navpoint_front']
        xsize = temp.shape[0]
        ysize = temp.shape[1]
        # detect the center
        if image is None:
            frame = self.controller.grab_screen(region)
        else:
            if region is not None:
                frame = image[region[1]:region[3], region[0]:region[2], :]
            else:
                frame = image
        filtered = cv2.inRange(frame,
                               np.array([filter_threshold[0] - bia,
                                         filter_threshold[1] - bia,
                                         filter_threshold[2] - bia]),
                               np.array([filter_threshold[0] + bia,
                                         filter_threshold[1] + bia,
                                         filter_threshold[2] + bia]))
        res = cv2.matchTemplate(filtered, temp, cv2.TM_CCOEFF_NORMED)
        loc = cv2.minMaxLoc(res)
        left_up = (loc[3][0], loc[3][1])
        right_down = (loc[3][0] + xsize, loc[3][1] + ysize)
        center = (left_up[0] + center_bia_x, left_up[1] + center_bia_y)
        confidence = loc[1]
        return left_up, right_down, center, confidence, frame

    def read(self):
        if self.read_compass_region is None:
            screen_region = self.configuration['read_compass']['region_start']
        else:
            screen_region = self.read_compass_region
        isshow = self.configuration['read_compass']['show'] == 'True'
        paint = None
        center_navpoint = None
        is_front = None
        left_up_compass, right_down_compass, center_compass, confidence_compass, frame_compass = self.get_compass(
            region=screen_region)
        if confidence_compass < 0.5:
            center_compass = None
        if isshow:
            paint = frame_compass.copy()
            if center_compass is not None:
                cv2.circle(paint, center_compass, 2, (0, 0, 255), 2)
                cv2.rectangle(paint, left_up_compass, right_down_compass, (0, 0, 255), 3)

        left_up_nav_front, right_down_nav_front, center_nav_front, confidence_nav_front, frame_nav_front = self.get_navpoint_front(
            region=(left_up_compass[0], left_up_compass[1], right_down_compass[0], right_down_compass[1]),
            image=frame_compass)
        left_up_nav_back, right_down_nav_back, center_nav_back, confidence_nav_back, frame_nav_back = self.get_navpoint_back(
            region=(left_up_compass[0], left_up_compass[1], right_down_compass[0], right_down_compass[1]),
            image=frame_compass)
        if confidence_nav_back >= confidence_nav_front:
            if confidence_nav_back >= 0.5:
                center_navpoint = (center_nav_back[0] + left_up_compass[0], center_nav_back[1] + left_up_compass[1])
                is_front = False
                if isshow:
                    cv2.circle(paint, center_navpoint, 2, (0, 255, 0), 2)
        else:
            if confidence_nav_front >= 0.5:
                center_navpoint = (center_nav_front[0] + left_up_compass[0], center_nav_front[1] + left_up_compass[1])
                is_front = True
                if isshow:
                    cv2.circle(paint, center_navpoint, 2, (255, 0, 0), 2)

        if isshow:
            cv2.imshow('read compass', paint)
            cv2.waitKey(1)

        # reset coordinates
        if center_compass is not None:
            center_compass = (center_compass[0] + screen_region[0], center_compass[1] + screen_region[1])
        if center_navpoint is not None:
            center_navpoint = (center_navpoint[0] + screen_region[0], center_navpoint[1] + screen_region[1])

        #reset scan region
        track_range = self.configuration['read_compass']['track_range']
        if center_compass is not None:
            self.read_compass_region = (center_compass[0] - track_range[0], center_compass[1] - track_range[1], center_compass[0] + track_range[2], center_compass[1] + track_range[3])
        else:
            self.read_compass_region = None
        self.compass['center_compass'] = center_compass
        self.compass['center_navpoint'] = center_navpoint
        self.compass['is_front'] = is_front
        return center_compass, center_navpoint, is_front