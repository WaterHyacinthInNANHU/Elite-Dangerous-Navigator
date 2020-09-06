# -*-encoding:utf-8-*-
from aip import AipOcr
import PIL.Image
from io import BytesIO
def BaiduOCR(picture, APP_ID, API_KEY, SECRET_KEY):
    """利用百度api识别文本，并保存提取的文字
    picfile:    图片文件名
    outfile:    输出文件
    """
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    if isinstance(picture, str):
        with open(picture, 'rb') as file:
            img = file.read()
            message = client.basicGeneral(img)  # 通用文字识别，每天 50 000 次免费
            # message = client.basicAccurate(img)   # 通用文字高精度识别，每天 800 次免费
            print("baidu ocr message: "+message)
            if message.get('words_result')[0] is not None:
                return [word['words'].replace(' ','') for word in message.get('words_result')]
            else:
                raise Exception("Failed to recognize")
        pass

    elif isinstance(picture, PIL.Image.Image):
        buf = BytesIO()
        picture.save(buf, format='PNG')
        img = buf.getvalue() #转换为字节流
        message = client.basicGeneral(img)  # 通用文字识别，每天 50 000 次免费
        # message = client.basicAccurate(img)   # 通用文字高精度识别，每天 800 次免费
        print("baidu ocr message: " + message)
        if message.get('words_result')[0] is not None:
            return [word['words'].replace(' ','') for word in message.get('words_result')]
        else:
            raise Exception("Failed to recognize")
    else:
        raise Exception("Wrong picture data type")
