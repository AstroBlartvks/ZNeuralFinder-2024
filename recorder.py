import win32gui
import dxcam
import cv2
import keyboard

import time
from datetime import datetime

def get_winname(name_window):
    foreground_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    for part in name_window:
        if part.lower() in foreground_window.lower(): return foreground_window
    return ""

def get_forname():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())

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

def main():
    screen_recorder = dxcam.create()

    while True:
        time.sleep(1/64)
        if keyboard.is_pressed("F"):
            win_name = get_forname()
            #if win_name == "":
            #    continue
            
            (window_rect, screenshot) = get_screenshot(win_name, screen_recorder)
            if isinstance(window_rect, bool) or sum(window_rect) == 0:
                continue

            screen_cv2 = cv2.resize(screenshot, dsize = (640, 416))
            screen_cv2 = cv2.cvtColor(screen_cv2, cv2.COLOR_RGB2BGR)
            name_file = str(datetime.now().strftime("%d_%m_%Y_%H_%M_%S")) + ".png"
            cv2.imwrite("D:\\projects\\NowProjects\\FindPlayer\\not_annotated\\"+name_file, screen_cv2)
            print("FILE SAVED: D:\\projects\\NowProjects\\FindPlayer\\not_annotated\\"+name_file)
            time.sleep(15/60)

main()
#с 24 минут дальше я не трогал 