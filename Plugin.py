import threading
from ctypes import CDLL, c_int, c_char_p,c_float,c_char
import json
lock2 = threading.RLock()
from log import Log
logger = Log().get_log()
class Plugin:
    yoloInitSuccess = False
    ocrInitSuccess = False
    dllPath = ""
    modelPath = ""
    
    def __init__(self,dllPath,modelPath) -> None:
        try:
            self.dllPath = dllPath
            self.modelPath = modelPath
            self.dllObject = CDLL(dllPath)
            if not self.ocrInitSuccess:
                self.loadOCR()
        except Exception as e:
            logger.error(f"模型初始化出错:{str(e)}")

    #加载yolo
    def loadYolo(self):
        self.dllObject.initModel.argtypes = [c_char_p,c_int]
        print(f"yolo 加载{self.modelPath}")
        ret = self.dllObject.initModel((self.modelPath).encode("utf-8"),c_int(1))
        self.yoloInitSuccess = ret == 0
        print(f"yolo 加载{self.modelPath}结果:{self.yoloInitSuccess}")
        return self.yoloInitSuccess

    #加载ocr
    def loadOCR(self):
        try:
            self.dllObject.initTextModel.argtypes = [c_char_p, c_int]
            res = self.dllObject.initTextModel((self.modelPath).encode("utf-8"), c_int(1))
            self.ocrInitSuccess = res == 0
            self.dllObject.OCRRect.argtypes = [c_int, c_int, c_int, c_int, c_int]
            self.dllObject.OCRRect.restype = c_char_p
        except Exception as e:
            logger.error(f"loadOCR出错:{str(e)}")


        return self.ocrInitSuccess
    #识别区域
    def detectYoloObject(self,wnd,clsName,confidence=0.5):
        if not self.yoloInitSuccess:
            self.loadYolo()
        if self.yoloInitSuccess:
            self.dllObject.detectObject.argtypes = [c_int,c_float]
            self.dllObject.detectObject.restype = c_char_p
            result = self.dllObject.detectObject(c_int(wnd),c_float(confidence))
            sResult = result.decode("utf-8")
            print(f"所有识别结果图片:{sResult}")
            return []
            '''jsonResult = json.loads(sResult)
            if len(clsName) == 0:
                return jsonResult
            #根据id查类名
            idx = -1
            for i in range(0,len(self.clsNames)):
                if clsName == self.clsNames[i]:
                    idx = i
            print(f"name={clsName} idx={idx}")
            key = f"{idx}"
            if idx >= 0 and key in jsonResult.keys():
                print(jsonResult[key])
                return jsonResult[key]'''
        return []
    
    #识别区域
    def detectRectYoloObject(self,wnd,clsName,x,y,w,h,confidence=0.2):
        if not self.yoloInitSuccess:
            self.loadYolo()
        if self.yoloInitSuccess:
            self.dllObject.detectObject2.argtypes = [c_int,c_float,c_int,c_int,c_int,c_int]
            self.dllObject.detectObject2.restype = c_char_p
            result = self.dllObject.detectObject2(c_int(wnd),c_float(confidence),c_int(x),c_int(y),c_int(w),c_int(h))
            sResult = result.decode("utf-8")
            print(f"图片所有识别结果----------------:{sResult}")
            jsonResult = json.loads(sResult)
            if len(clsName) == 0:
                return jsonResult
            #根据id查类名
            idx = -1
            for i in range(0,len(self.clsNames)):
                if clsName == self.clsNames[i]:
                    idx = i
            print(f"name={clsName} idx={idx}")
            key = f"{idx}"
            if idx >= 0 and key in jsonResult.keys():
                print(jsonResult[key])
                return jsonResult[key]
        return []


    #全屏识字
    def detectText(self,wnd):
        if self.ocrInitSuccess:
            self.dllObject.OCR.argtypes = [c_int]
            self.dllObject.OCR.restype = c_char_p
            return self.dllObject.OCR(c_int(wnd)).decode("utf-8")
        return "{}"

    #识别区域文字
    def detectRectText(self,wnd,x,y,w,h):
        result = ""
        try:
            lock2.acquire()
            result = self.dllObject.OCRRect(c_int(wnd), c_int(x), c_int(y), c_int(w), c_int(h))
            result =result.decode("utf-8")
            return result
        except Exception as e:
            logger.error(f"识别区域文字出错:{str(e)}")
        finally:
            lock2.release()
            return result


class GlobalData:
    plugin = None
    def __init__(self):
        #调试
        #self.plugin = Plugin("../tpwPlugin/x64/Release/tpwPlugin.dll","../tpwPlugin/models/")
        #dll和py在同目录
        self.plugin = Plugin("./models/VCRUNT1ME140_2.dll","./models/")

shareData = GlobalData()