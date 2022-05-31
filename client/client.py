import socket
import select
import errno
import sys
import time

# VARIABLES
HEADER_LENGTH = 10
IP = ''
PORT = 44421

ipCorrect = False
loggedIn = False

bal = 0
bank = 0

waiting = False

sent = False

currentPlayers = ''
currentHand = ''
currentMax = 0

# FUNCTIONS
# parses command and splits it based on | and ,
def command_parse(msg):
    msg = msg.split("|")
    for i in range(len(msg)):
        msg[i] = msg[i].split(",")
    return msg

# splits up the cards sent or the players sent
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



# while the client isnt logged in
while loggedIn is False:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # gets the ip address
    if ipCorrect is True:
        client_socket.connect((IP, PORT))
    while ipCorrect is False:
        try:
            IP = input('Input server IP address here: ')
            client_socket.connect((IP, PORT))
            ipCorrect = True
        except:
            print('IP incorrect, try again')


    client_socket.setblocking(False)
    # input username and password
    my_username = input('Username: ')
    my_password = input('Password: ')

    # sends the login
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
            lnmessage = command_parse(lnmessage)
            # if the received message is sl, it gets the bal, bank, and sets logged in to true
            if lnmessage[0][0] == 'sl':
                loggedIn = True
                bal = int(lnmessage[0][1])
                bank = int(lnmessage[0][2])
                break
            # otherwise, makes you try again
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


# main loop
while True:
    # if you arent waiting, allows you to send commands
    if waiting is False:
        print('\033c', end="")
        print(f'To join game, type "jn". Current balance: {bal}')
        omessage = input(f'{my_username} >  ')
    else:
        omessage = 'no'
    # if you arent waiting and you sent a command, sends command to server
    if omessage != 'no':
        omessage = omessage.encode()
        omessage_header = f"{len(omessage):<{HEADER_LENGTH}}".encode()
        client_socket.send(omessage_header + omessage)

    else:
        pass

    # tries to receive a message from the server
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
            # checks message if it is wt, if it is, sets wait to true and prints out optional message
            if message[0][0] == 'wt':
                if message[0][1] == my_username:

                    if waiting is True:
                        waiting = False
                    else:
                        waiting = True
                    try:
                        print(f'{message[0][2]}')
                    except:
                        pass
            # if message is yt
            elif message[0][0] == 'yt':
                # gets all values from command
                print("\033c", end="")
                cmdBack = ''
                currentMax = int(message[0][1])
                currentTable = multiSplit(message[0][2], 't')
                currentHand = multiSplit(message[0][3], 'h')
                currentPlayers = multiSplit(message[0][4], 'p')
                sent = False
                while not sent:
                    # prints out interface
                    print(f'Players: {currentPlayers}')
                    print(f'Table: {currentTable}')
                    print(f'{currentHand}')
                    print('-'*30)
                    print('[r] Raise')
                    print('[c] Call')
                    print('[f] Fold')
                    choice = input(' > ')
                    # sends back respective choice of r for raise, c for call, and f for fold
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
                        # otherwise, clear screen and redo interface
                        print("\033c", end="")
                        print('Input valid option')
                        print(' ')

            # if command is wn, print the win screen
            elif message[0][0] == 'wn':
                print("\033c", end="")
                print('-'*30)
                print('Game results:')
                print(f'You won {message[0][1]}')
                print(f'Your new balance is {message[0][2]}')
                bal = int(message[0][2])
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
