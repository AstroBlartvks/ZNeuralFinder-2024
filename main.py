from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
import win32gui, win32api, win32con
import pyautogui, threading
import dxcam, keyboard, winsound
import cv2

import time

def get_winname(name_window):
    foreground_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    for part in name_window:
        if part.lower() in foreground_window.lower(): return foreground_window
    return ""

def get_screenshot(win_name, screen):
    window_handle = win32gui.FindWindow(None, win_name)
    window_rect   = win32gui.GetWindowRect(window_handle) 
    if (window_rect[2] + window_rect[0] <= 1920 and \
        window_rect[3] + window_rect[1] <= 1080) and \
        (window_rect[2] > 1920 or window_rect[3] > 1080):
        window_rect = (0, 0, 1920, 1080)
    elif (window_rect[2] > 1920 or window_rect[3] > 1080) or (window_rect[0] < 0 or window_rect[1] < 0):
        return (False, False)

    return (window_rect, screen.grab(region = window_rect))

def draw_box(HDC, xywh, xof, yof, KWidth, KHeight, draw):
    color = win32api.RGB(255, 0, 0)
    [x1, y1, w, h] = list([int(xywh[i].item() * (KWidth*((i+1)%2) + KHeight*(i%2))) for i in range(4)])
    x1 = xof + x1 - w//2
    y1 = yof + y1 - h//2
    XOff = int(x1 + w//2)
    YOff = int(y1 + h//2)
    if draw:
        for x in range(0, w, 2):
            win32gui.SetPixel(HDC, x1+x, y1, color)
            win32gui.SetPixel(HDC, x1+x, y1+h, color)
        for y in range(0, h, 2):
            win32gui.SetPixel(HDC, x1, y1+y, color)
            win32gui.SetPixel(HDC, x1+w, y1+y, color)
    
    return XOff, YOff


def clicker():
    CLICK = False
    while True:
        if CLICK:
            pyautogui.click()
        if keyboard.is_pressed("X"):
            CLICK = not(CLICK)
            if CLICK: winsound.Beep(5000, 100)
            else: winsound.Beep(500, 100)
            time.sleep(0.16)
        time.sleep(1/2048)


def main():
    screen_recorder = dxcam.create()
    model = YOLO('D:\\projects\\NowProjects\\FindPlayer\\model.pt')
    model = model.to('cuda')
    HDC = win32gui.GetDC(None)
    TURN = False
    SHOWNN = False
    DRAW = False
    FOV = 200.0
    threading.Thread(target=clicker).start()

    while True:
        try:
             
            time.sleep(1/2048)
            start = time.time()
            win_name = get_winname(["vime", "minecraft", "1.12.2", "1.16.5", "1.7.10", "1.8.9"])
            if win_name == "":
                continue

            (window_rect, screenshot) = get_screenshot(win_name, screen_recorder)
            if isinstance(window_rect, bool) or sum(window_rect) == 0  or isinstance(screenshot, type(None)) or 0 in list([screenshot.shape[x] for x in range(len(screenshot.shape))]):
                continue
            
            KWidth = (window_rect[2] - window_rect[0]) / 640.0
            KHeight = (window_rect[3] - window_rect[1]) / 416.0
            
            screen_cv2 = cv2.resize(screenshot, dsize = (640, 416))

            result_image = model(screen_cv2)


            for result in result_image:
                if SHOWNN:
                    annotator = Annotator(screen_cv2)
                boxes = result.boxes

                for box in boxes:
                    to_x, to_y = draw_box(HDC, box.xywh[0], window_rect[0], window_rect[1], KWidth, KHeight, DRAW)
                    
                    cx = window_rect[0] + (window_rect[2] - window_rect[0]) // 2
                    cy = window_rect[1] + (window_rect[3] - window_rect[1]) // 2
                    dist = ((cx - to_x) * (cx - to_x) + (cy - to_y) * (cy - to_y)) ** (1/2)
                    
                    if dist < FOV and TURN:
                        win32api.SetCursorPos((to_x, to_y))
                    if SHOWNN:
                        class_box = box.cls
                        annotator.box_label(box.xyxy[0], model.names[int(class_box)])
            
            if SHOWNN:
                end = time.time()
                screen_cv2 = cv2.putText(screen_cv2, str(round(1 / (end - start)))+" FPS", (10, 100), 1, 4, (255, 0, 0))
                screen_cv2 = annotator.result()  
                screen_cv2 = cv2.cvtColor(screen_cv2, cv2.COLOR_RGB2BGR)
                cv2.imshow('ZerruKupeNN', screen_cv2)
                if cv2.waitKey(1) & 0xFF == ord(' '):
                    break

            if keyboard.is_pressed("Z"):
                TURN = not(TURN)
                if TURN: winsound.Beep(10000, 100)
                else: winsound.Beep(1000, 100)
                time.sleep(0.16)

            

        except Exception as exp:
            print(exp)

main()
