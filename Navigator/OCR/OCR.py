# -*-encoding:utf-8-*-
# import pytesseract
from .BaiduOCR import BaiduOCR
from json import load
from pathlib import Path
class OCR(object):
    def __init__(self):
        root_path = Path(__file__).parent
        with open(root_path / '../configuration.json', 'r', encoding='utf8') as fp:
            self.configuration = load(fp)

    def baidu_ocr(self, picture):
        """
        using baidu api to recoginze
        :param picture: Image instance of PIL or a path
        :return:
        """
        return BaiduOCR(picture,
                 self.configuration['APP_ID'],
                 self.configuration['API_KEY'],
                 self.configuration['SECRET_KEY'])

    def local_ocr(self, picture):
        """
        using local ocr tool to recognize
        :param picture:
        :return:
        """
        # return pytesseract.image_to_string(picture)
        pass

# from PIL import ImageGrab
# import pyautogui as auto
# import keyboard
# def proc():
#     print("start  ")
#     keyboard.wait(' ')
#     pos1 = auto.position()
#     print("get 1/2")
#     print(pos1)
#     keyboard.wait(' ')
#     pos2 = auto.position()
#     print("get 2/2")
#     print(pos2)
#     box = (pos1.x, pos1.y, pos2.x, pos2.y)
#     im = ImageGrab.grab(bbox=box, include_layered_windows=False, all_screens=False, xdisplay=None)
#     res = BaiduOCR(im, "18792693", "8g9IrnI7rALgBs7B6sY9pffL", "oVT3cD5Hu840TgI6mWswbBoZrmCDKqFi")
#     print(res)