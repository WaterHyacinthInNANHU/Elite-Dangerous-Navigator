# -*-encoding:utf-8-*-
from win32api import PostThreadMessage,mouse_event,SetCursorPos,keybd_event,GetCursorPos
from win32gui import EnumWindows, GetWindowText, ShowWindow,SetCapture,SetForegroundWindow,IsWindowVisible,SetActiveWindow,FindWindow
from win32con import SW_SHOWDEFAULT,SW_MAXIMIZE,SW_SHOWMAXIMIZED,SW_SHOWMINIMIZED,SW_SHOW,MOUSEEVENTF_MOVE,MOUSEEVENTF_ABSOLUTE,\
    MOUSEEVENTF_LEFTDOWN,MOUSEEVENTF_LEFTUP,WM_SHOWWINDOW,KEYEVENTF_KEYUP
from json import load
from time import sleep
import win32com.client
from PIL import ImageGrab
from ..OCR.OCR import OCR
from pathlib import Path
from numpy import array
import ctypes
import pyautogui as auto
import pydirectinput as auto_input
from collections import Iterable

class Pid(object):
    def __init__(self,p=0,i=0,d=0,target=0,history_length=10):
        self.p = p
        self.i = i
        self.d = d
        self.target = target
        self.history_length = history_length
        self.history = []
        for i in range(self.history_length):
            self.history.append(0)

    def predict(self,now_value):
        error = self.target - now_value
        output = self.p*error + self.i*sum(self.history) + self.d*(error-self.history[-1])
        self.history.append(error)
        self.history = self.history[1:]
        return output

class Controller(object):
    def __init__(self):
        #Avoid subjecting to DPI virtualization  see:
        # https://stackoverflow.com/questions/32541475/win32api-is-not-giving-the-correct-coordinates-with-getcursorpos-in-python
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        root_path = Path(__file__).parent
        self.shell = win32com.client.Dispatch("WScript.Shell")
        with open(root_path / '../configuration.json', 'r', encoding='utf8')as fp:
            self.configuration = load(fp)['Controller']
        with open(root_path / './vk_code.json', 'r', encoding='utf8')as fp:
            self.VK_CODE = load(fp)
        for i in self.VK_CODE:
            self.VK_CODE[i] = self.str2hex(self.VK_CODE[i])
        self.hwnd = None
        self.ocr = OCR()
        self.shell = win32com.client.Dispatch("WScript.Shell")

        pass

    def list_windows(self):
        def callback(hwnd,para):
            print(GetWindowText(hwnd))
        EnumWindows(callback,None)

    def get_hwnd(self,name=None):
        hd = []
        if name is None:
            name = self.configuration['window_name']

        def callback(hwnd, hd):
            if name == GetWindowText(hwnd):
                # print("find!")
                hd.append(hwnd)

        EnumWindows(callback, hd)

        if hd is []:
            raise Exception("Controller: can't find window")
        else:
            self.hwnd = hd[0]
        return hd[0]

    def show_maximized(self,hwnd=None):
        if hwnd is None:
            hwnd = self.hwnd
        self.shell.SendKeys('%')
        SetForegroundWindow(hwnd)

    # def get_mouse_position(self):
    #     return GetCursorPos()
    #
    # def mouse_move_to(self,x,y):
    #     SetCursorPos([x,y])

    # def mouse_click_at(self,x,y):
    #     if not x is None and not y is None:
    #         self.mouse_move_to(x, y)
    #         sleep(0.05)
    #     mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    #     mouse_event(MOUSEEVENTF_LEFTUP, 0, 0)

    def click(self,x,y):
        auto_input.click(x, y)

    def move_to(self,x,y,duration=None):
        auto_input.moveTo(x,y,duration)
        # auto.moveTo(x,y,duration)

    def type(self,str):
        if isinstance(str, list):
            for char in str:
                auto_input.keyDown(char)
                auto_input.keyUp(char)
        else:
            auto_input.keyDown(str)
            auto_input.keyUp(str)

    def key_depress(self,char):
        auto_input.keyDown(char)

    def key_release(self, char):
        auto_input.keyUp(char)

    def SetForegroundWindow(self,hwnd):
        self.shell.SendKeys('%')
        SetForegroundWindow(hwnd)

    def foucusOnTheWindow(self,throwExp=False):
        hwnd = FindWindow(None, self.configuration['window_name'])
        if(hwnd==0):
            if(throwExp):
                raise Exception("Can't find window")
            # self.log("can't find Mumu window")
            return False
        self.SetForegroundWindow(hwnd)
        return True

    def str2hex(self,s):
        odata = 0
        su = s.upper()
        for c in su:
            if c == '0' or c == 'X':
                continue
            tmp = ord(c)
            if tmp <= ord('9'):
                odata = odata << 4
                odata += tmp - ord('0')
            elif ord('A') <= tmp <= ord('F'):
                odata = odata << 4
                odata += tmp - ord('A') + 10
        return odata

    # def key_depress(self,c):
    #     keybd_event(self.VK_CODE[c], 0, 0, 0)
    #
    # def key_release(self,c):
    #     keybd_event(self.VK_CODE[c], 0, KEYEVENTF_KEYUP, 0)
    #
    # def key_input(self,str):
    #     for c in str:
    #         keybd_event(self.VK_CODE[c], 0, 0, 0)
    #         keybd_event(self.VK_CODE[c], 0, KEYEVENTF_KEYUP, 0)
    #         # sleep(0.01)

    def grab_screen(self,region):
        """
        grab image from screen by region
        :param region: eg:(0,0,100,100)
        :return: opencv image
        """
        pillow_image = ImageGrab.grab(bbox=region, include_layered_windows=False, all_screens=False)
        return array(pillow_image)

    def region_ocr(self,region,mode='local'):
        """
        ocr in specified region
        :param region: eg:(0,0,100,100)
        :param mode: 'baidu' or 'local'
        :return: If pass 'baidu' to mode, return a list of words recognized;
                 If pass 'local' to mode, return a combination of all the raw words recognized
        """
        image = self.grab_screen(region)
        if mode is 'local':
            return self.ocr.local_ocr(image)
        elif mode is 'baidu':
            return self.ocr.baidu_ocr(image)

