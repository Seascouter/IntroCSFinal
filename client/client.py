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

sent = False

currentPlayers = ''
currentHand = ''
currentMax = 0


def command_parse(msg):
    msg = msg.split("|")
    for i in range(len(msg)):
        msg[i] = msg[i].split(",")
    return msg

def multiSplit(string, mode):
    outputStr = ''
    if mode == 't' or mode == 'h':
        temp = string.split(';')
        for x in range(len(temp)):
            outputStr += f'{temp[x]} '
    elif mode == 'p':
        temp = string.split(';')
        for x in temp:
            x = x.split('~')
            if x[1] == 'i':
                #\033[32m
                outputStr += f'\033[32m{x[0]} [{x[2]}]\033[0m '
            elif x[1] == 'o':
                #\033[31m
                outputStr += f'\033[31m{x[0]}\033[0m '
    return outputStr




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
            elif message[0][0] == 'yt':
                print("\033c", end="")
                cmdBack = ''
                currentMax = int(message[0][1])
                currentTable = multiSplit(message[0][2], 't')
                currentHand = multiSplit(message[0][3], 'h')
                currentPlayers = multiSplit(message[0][4], 'p')
                sent = False
                while not sent:
                    print(f'Players: {currentPlayers}')
                    print(f'Table: {currentTable}')
                    print(f'{currentHand}')
                    print('-'*30)
                    print('[r] Raise')
                    print('[c] Call')
                    print('[f] Fold')
                    choice = input(' > ')
                    if choice == 'r':
                        try:
                            raiseAmt = int(input(f'Raise to how much (min {currentMax+1})? '))
                        except:
                            continue
                        if raiseAmt <= currentMax:
                            print("\033c", end="")
                            continue
                        else:
                            cmdBack += f'rs,{raiseAmt}'
                            cmdBack = cmdBack.encode()
                            cmdBack = {'header': f"{len(cmdBack):<{HEADER_LENGTH}}".encode(), 'data': cmdBack}
                            cmdBack = cmdBack['header'] + cmdBack['data']
                            client_socket.send(cmdBack)
                            sent = True
                    elif choice == 'c':
                        cmdBack += f'cl,{currentMax}'
                        cmdBack = cmdBack.encode()
                        cmdBack = {'header': f"{len(cmdBack):<{HEADER_LENGTH}}".encode(), 'data': cmdBack}
                        cmdBack = cmdBack['header'] + cmdBack['data']
                        client_socket.send(cmdBack)
                        sent = True
                    elif choice == 'f':
                        cmdBack += 'fd'
                        cmdBack = cmdBack.encode()
                        cmdBack = {'header': f"{len(cmdBack):<{HEADER_LENGTH}}".encode(), 'data': cmdBack}
                        cmdBack = cmdBack['header'] + cmdBack['data']
                        client_socket.send(cmdBack)
                        sent = True
                    else:
                        print("\033c", end="")
                        print('Input valid option')
                        print(' ')

            elif message[0][0] == 'wn':
                print("\033c", end="")
                print('-'*30)
                print('Game results:')
                print(f'You won {message[0][1]}')
                print(f'Your new balance is {message[0][2]}')
                print('-'*30)
                time.sleep(3)
                waiting = False

                            



    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        continue
    except Exception as e:
        print('Reading error: {}'.format(str(e)))
        sys.exit()
