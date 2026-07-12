from ctypes import windll

import cv2
import numpy as np
import win32gui
import win32ui


def _capture_win32_gpu(handle):
    """
    通过win32方式截图，并且无视硬件加速
    https://stackoverflow.com/questions/19695214/screenshot-of-inactive-window-printwindow-win32gui
    """
    windll.user32.SetProcessDPIAware()  # 抑制缩放

    rect = win32gui.GetWindowRect(handle)
    width, height = rect[2] - rect[0], rect[3] - rect[1]

    hwnd_dc = win32gui.GetWindowDC(handle)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()
    save_bit_map = win32ui.CreateBitmap()

    save_bit_map.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(save_bit_map)

    windll.user32.PrintWindow(handle, save_dc.GetSafeHdc(), 3)  # 如果仍然是黑屏，尝试修改数字 ‘3’ (从0开始...)
    bmpinfo = save_bit_map.GetInfo()
    bmpstr = save_bit_map.GetBitmapBits(True)

    capture = np.frombuffer(bmpstr, dtype=np.uint8).reshape((bmpinfo["bmHeight"], bmpinfo["bmWidth"], 4))
    capture = np.ascontiguousarray(capture)[..., :-1]

    win32gui.DeleteObject(save_bit_map.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(handle, hwnd_dc)

    capture = cv2.cvtColor(capture, cv2.COLOR_RGBA2RGB)
    return capture

