import socket
import select
import errno
import sys
import time

HEADER_LENGTH = 10
IP = '192.168.7.240'
PORT = 44421

loggedIn = False

waiting = False


def command_parse(msg):
    msg = msg.split("|")
    for i in range(len(msg)):
        msg[i] = msg[i].split(",")
    return msg



while loggedIn is False:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))

    client_socket.setblocking(False)
    my_username = input('Username: ')
    my_password = input('Password: ')

    login = f"un,{my_username}|pw,{my_password}".encode()
    loginHeader = f"{len(login):<{HEADER_LENGTH}}".encode()
    client_socket.send(loginHeader+login)

    try:
        while True:
            time.sleep(0.25)
            lnmessage_header = client_socket.recv(HEADER_LENGTH)

            if not len(lnmessage_header):
                print("Connection closed by the server")
                sys.exit()
            lnmessage_length = int(lnmessage_header.decode().strip())
            lnmessage = client_socket.recv(lnmessage_length).decode()
            if lnmessage == 'sl':
                loggedIn = True
                break
            elif lnmessage == 'wl':
                continue

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        if loggedIn is False:
            continue
        else:
            break
    except Exception as e:
        print('Reading error: {}'.format(str(e)))
        sys.exit()



while True:

    if waiting is False:
        omessage = input(f'{my_username} >  ')
    else:
        omessage = 'no'

    if omessage != 'no':
        omessage = omessage.encode()
        omessage_header = f"{len(omessage):<{HEADER_LENGTH}}".encode()
        client_socket.send(omessage_header + omessage)

    else:
        pass

    try:
        while True:
            time.sleep(0.25)
            message_header = client_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                print("Connection closed by the server")
                sys.exit()
            message_length = int(message_header.decode().strip())
            message = client_socket.recv(message_length).decode()
            message = command_parse(message)

            if message[0][0] == 'wt':
                if message[0][1] == my_username:

                    if waiting is True:
                        waiting = False
                    else:
                        waiting = True

            print(f'{message[0][2]}')

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        continue
    except Exception as e:
        print('Reading error: {}'.format(str(e)))
        sys.exit()
