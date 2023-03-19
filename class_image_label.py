
import os
import glob
import shutil
import numpy as np

import cv2

import json

import argparse

class ParamMouse(object):
    def __init__(self,img,wname,intiSize):
        self.g_window_name = wname  # 窗口名
        self.g_image_show,s = self.resize_image(img, intiSize)
        self.g_window_wh = [self.g_image_show.shape[1],self.g_image_show.shape[0]]  # 窗口宽高
        # self.g_window_wh=[2*self.g_window_wh_init[0],2*self.g_window_wh_init[1]] if self.g_window_wh_init[0]>img.shape[1] else [img.shape[1],img.shape[0]]
        self.g_location_win = [0, 0]  # 相对于大图，窗口在图片中的位置
        self.location_win = [0, 0]  # 鼠标左键点击时，暂存g_location_win
        self.g_location_click, self.g_location_release = [0, 0], [0, 0]  # 相对于窗口，鼠标左键点击和释放的位置

        self.g_zoom, self.g_step = s, 0.1  # 图片缩放比例和缩放系数
        self.g_image_original = img  # 原始图片，建议大于窗口宽高（800*600）
        self.g_image_zoom = img.copy()  # 缩放后的图片
        # self.g_image_show = self.g_image_original[self.g_location_win[1]:self.g_location_win[1] + self.g_window_wh[1],
        #                self.g_location_win[0]:self.g_location_win[0] + self.g_window_wh[0]]  # 实际显示的图片
    def resize_image(self, image, width=1000):
        h, w = image.shape[:2]
        s = float(width) / max(h, w)
        h = int(s * h)
        w = int(s * w)
        image = cv2.resize(image, (w, h))
        return image, s

class CVUI(object):
    def __init__(self,img,wname=" ",initSize=1200):
        self.paramMouse = ParamMouse(img, wname,initSize)

    def show(self):
        cv2.namedWindow(self.paramMouse.g_window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.paramMouse.g_window_name, self.paramMouse.g_window_wh[0], self.paramMouse.g_window_wh[1])
        cv2.moveWindow(self.paramMouse.g_window_name, 0, 0)  # 设置窗口在电脑屏幕中的位置

        cv2.setMouseCallback(self.paramMouse.g_window_name, self._mouse_callback, self.paramMouse)

        key = cv2.waitKey()
        return key

    def destroyWindow(self):
        cv2.destroyWindow(self.paramMouse.g_window_name)

    # 矫正窗口在图片中的位置
    # img_wh:图片的宽高, win_wh:窗口的宽高, win_xy:窗口在图片的位置
    def _check_location(self,img_wh, win_wh, win_xy):
        for i in range(2):
            if win_xy[i] < 0:
                win_xy[i] = 0
            elif win_xy[i] + win_wh[i] > img_wh[i] and img_wh[i] > win_wh[i]:
                win_xy[i] = img_wh[i] - win_wh[i]
            elif win_xy[i] + win_wh[i] > img_wh[i] and img_wh[i] < win_wh[i]:
                win_xy[i] = 0
        # print(img_wh, win_wh, win_xy)

    # 计算缩放倍数
    # flag：鼠标滚轮上移或下移的标识, step：缩放系数，滚轮每步缩放0.1, zoom：缩放倍数
    def _count_zoom(self,flag, step, zoom):
        if flag > 0:  # 滚轮上移
            zoom += step
            if zoom > 1 + step * 20:  # 最多只能放大到3倍
                zoom = 1 + step * 20
        else:  # 滚轮下移
            zoom -= step
            if zoom < step:  # 最多只能缩小到0.1倍
                zoom = step
        zoom = round(zoom, 2)  # 取2位有效数字
        return zoom

    def _mouse_callback(self,event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
            param.g_location_click = [x, y]  # 左键点击时，鼠标相对于窗口的坐标
            param.location_win = [param.g_location_win[0],
                                  param.g_location_win[1]]  # 窗口相对于图片的坐标，不能写成location_win = g_location_win
        elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):  # 按住左键拖曳
            param.g_location_release = [x, y]  # 左键拖曳时，鼠标相对于窗口的坐标
            h1, w1 = param.g_image_zoom.shape[0:2]  # 缩放图片的宽高
            w2, h2 = param.g_window_wh  # 窗口的宽高
            show_wh = [0, 0]  # 实际显示图片的宽高
            if w1 < w2 and h1 < h2:  # 图片的宽高小于窗口宽高，无法移动
                show_wh = [w1, h1]
                param.g_location_win = [0, 0]
            elif w1 >= w2 and h1 < h2:  # 图片的宽度大于窗口的宽度，可左右移动
                show_wh = [w2, h1]
                param.g_location_win[0] = param.location_win[0] + param.g_location_click[0] - param.g_location_release[
                    0]
            elif w1 < w2 and h1 >= h2:  # 图片的高度大于窗口的高度，可上下移动
                show_wh = [w1, h2]
                param.g_location_win[1] = param.location_win[1] + param.g_location_click[1] - param.g_location_release[
                    1]
            else:  # 图片的宽高大于窗口宽高，可左右上下移动
                show_wh = [w2, h2]
                param.g_location_win[0] = param.location_win[0] + param.g_location_click[0] - param.g_location_release[
                    0]
                param.g_location_win[1] = param.location_win[1] + param.g_location_click[1] - param.g_location_release[
                    1]
            self._check_location([w1, h1], [w2, h2], param.g_location_win)  # 矫正窗口在图片中的位置
            param.g_image_show = param.g_image_zoom[param.g_location_win[1]:param.g_location_win[1] + show_wh[1],
                                 param.g_location_win[0]:param.g_location_win[0] + show_wh[0]]  # 实际显示的图片
        elif event == cv2.EVENT_MOUSEWHEEL:  # 滚轮
            z = param.g_zoom  # 缩放前的缩放倍数，用于计算缩放后窗口在图片中的位置
            param.g_zoom = self._count_zoom(flags, param.g_step, param.g_zoom)  # 计算缩放倍数
            w1, h1 = [int(param.g_image_original.shape[1] * param.g_zoom),
                      int(param.g_image_original.shape[0] * param.g_zoom)]  # 缩放图片的宽高
            w2, h2 = param.g_window_wh  # 窗口的宽高
            param.g_image_zoom = cv2.resize(param.g_image_original, (w1, h1), interpolation=cv2.INTER_AREA)  # 图片缩放
            show_wh = [0, 0]  # 实际显示图片的宽高
            if w1 < w2 and h1 < h2:  # 缩放后，图片宽高小于窗口宽高
                show_wh = [w1, h1]
                cv2.resizeWindow(param.g_window_name, w1, h1)
            elif w1 >= w2 and h1 < h2:  # 缩放后，图片高度小于窗口高度
                show_wh = [w2, h1]
                cv2.resizeWindow(param.g_window_name, w2, h1)
            elif w1 < w2 and h1 >= h2:  # 缩放后，图片宽度小于窗口宽度
                show_wh = [w1, h2]
                cv2.resizeWindow(param.g_window_name, w1, h2)
            else:  # 缩放后，图片宽高大于窗口宽高
                show_wh = [w2, h2]
                cv2.resizeWindow(param.g_window_name, w2, h2)
            param.g_location_win = [int((param.g_location_win[0] + x) * param.g_zoom / z - x),
                                    int((param.g_location_win[1] + y) * param.g_zoom / z - y)]  # 缩放后，窗口在图片的位置
            self._check_location([w1, h1], [w2, h2], param.g_location_win)  # 矫正窗口在图片中的位置
            # print(g_location_win, show_wh)
            param.g_image_show = param.g_image_zoom[param.g_location_win[1]:param.g_location_win[1] + show_wh[1],
                                 param.g_location_win[0]:param.g_location_win[0] + show_wh[0]]  # 实际的显示图片
        cv2.imshow(param.g_window_name, param.g_image_show)

###########################################################################################################################

def cv_imread(file):
    cvImg=cv2.imdecode(np.fromfile(file,dtype=np.uint8),-1)
    return cvImg

class ImageLabelOne(object):
    def __init__(self,pathCfg):
        with open(pathCfg) as f:
            dataJ = json.load(f)
            print("Config:", dataJ)
        self.labels = dataJ["labels"] # dict label:key
        self.dirImg = dataJ["dirImg"]
        self.keyLabel={ord(key):label for label,key in self.labels.items()}
        self.labeledFiles=[]
        self._load_labeled_file()

    def label_begin(self):
        files = glob.glob(os.path.join(self.dirImg, "*"))
        txtSave = os.path.abspath(self.dirImg) + "_label.txt"
        for index, file in enumerate(files):
            if self._is_labeled(file):
                continue
            print(f"{index} : {file}")
            strLabel = self._select_file(file)
            if strLabel is not None:
                with open(txtSave, "a") as f:
                    f.write(f"{os.path.basename(file)}:{strLabel}\n")

    def _load_labeled_file(self):
        txtSave = os.path.abspath(self.dirImg) + "_label.txt"
        if not os.path.exists(txtSave):
            return
        with open(txtSave) as f:
            lines = f.readlines()
        self.labeledFiles = [line.split(":")[0] for line in lines]

    def _is_labeled(self,file):
        return os.path.basename(file) in self.labeledFiles

    def _select_file(self,path):
        image = cv_imread(path)
        wname = os.path.basename(path)
        print("shape:", image.shape)

        mUI = CVUI(image, wname)
        key = mUI.show()
        print("key:", key)
        mUI.destroyWindow()
        if key == 32:
            return None
        return self._parse_label(key)

    def _parse_label(self,value):
        if value not in self.keyLabel.keys():
            print("Warning:the label not be defined.")
            return None
        return str(self.keyLabel[value])

class ImageLabelMultiple(object):
    def __init__(self,pathCfg):
        with open(pathCfg) as f:
            dataJ=json.load(f)
            print("Config:", dataJ)
        self.labels=dataJ["labels"]
        self.dirImg=dataJ["dirImg"]
        self.labeledFiles = []
        self._load_labeled_file()

    def label_begin(self):
        files = glob.glob(os.path.join(self.dirImg, "*"))
        txtSave = os.path.abspath(self.dirImg) + "_label.txt"
        for index, file in enumerate(files):
            if self._is_labeled(file):
                continue
            print(f"{index} : {file}")
            strLabel = self._select_file(file)
            if strLabel is not None:
                with open(txtSave, "a") as f:
                    f.write(f"{os.path.basename(file)}:{strLabel}\n")

    def _load_labeled_file(self):
        txtSave = os.path.abspath(self.dirImg) + "_label.txt"
        if not os.path.exists(txtSave):
            return
        with open(txtSave) as f:
            lines = f.readlines()
        self.labeledFiles = [line.split(":")[0] for line in lines]

    def _is_labeled(self, file):
        return os.path.basename(file) in self.labeledFiles

    def _parse_label(self,value):
        strL=str(bin(value)).replace("0b","")
        strL=strL.zfill(len(self.labels))
        return " ".join(strL)

    def _select_file(self,path):
        image = cv_imread(path)
        wname = os.path.basename(path)
        print("shape:", image.shape)
        # image=resize_image(image)

        mUI = CVUI(image, wname)
        key = mUI.show()
        print("key:", key)
        mUI.destroyWindow()
        if key == 32:
            return None
        return self._parse_label(key - 48)

def create_ImageLabelOne_cfg():
    path="ImageLabelOne.json"
    data={
        "labels":{
            "label0":"q",
            "label1":"w",
            "label2":"e"
        },
        "dirImg":"dirImg"
    }
    with open(path,"w") as f:
        json.dump(data,f)

def create_ImageLabelMultiple_cfg():
    path="ImageLabelMultiple.json"
    data={
        "labels":[
            "label0","label1","label2"
        ],
        "dirImg":"dirImg"
    }
    with open(path,"w") as f:
        json.dump(data,f)

def main_create_cfg():
    create_ImageLabelOne_cfg()
    create_ImageLabelMultiple_cfg()

if __name__ == "__main__":
    '''
    Space key means skip.
    The mod is supported max 3 labels for assign image multiple labels.
    '''
    parse=argparse.ArgumentParser()
    parse.add_argument("--pathCfg",type=str,default=f"{os.path.dirname(__file__)}/ImageLabelOne.json",
                       help="The config Path,can refer to the ImageLabelOne.json or ImageLabelMultiple.json in dir of exe file")
    parse.add_argument("--mod",type=int,default=0,
                       help="The label mod,0 is the assign image one label,1 is the assign image multiple labels.")
    arg=parse.parse_args()

    if arg.mod == 0:
        print("Start ImageLabelOne mod...")
        mlabel=ImageLabelOne(arg.pathCfg)
        mlabel.label_begin()
    if arg.mod == 1:
        print("Start ImageLabelMultiple mod...")
        mlabel = ImageLabelMultiple(arg.pathCfg)
        mlabel.label_begin()
    else:
        print("Input mod Error.")