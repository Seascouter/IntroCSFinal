# IMPORTS
import socket
import select
import random
import accounts.accounts as accounts
import main

# VARIABLES
HEADER_LENGTH = 10
PORT = 44421


# FUNCTIONS
def receive_message(cs):
    try:
        message_header = cs.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode().strip())

        return {'header': message_header, 'data': cs.recv(message_length)}

    except:
        return False


def command_parse(msg):
    msg = msg.split("|")
    for i in range(len(msg)):
        msg[i] = msg[i].split(",")
    return msg


# MAIN CODE

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

accounts.get_users()

server_socket.bind(('', PORT))

server_socket.listen()

sockets_list = [server_socket]
clients = {}

print(f'Server open on {PORT}')

un = ''
pw = ''

while True:
    read_s, _, exception_s = select.select(sockets_list, [], sockets_list)

    for notified in read_s:
        if notified == server_socket:
            client, caddr = server_socket.accept()
            if client not in clients:
                user = receive_message(client)
                if user is False:
                    continue
                user['data'] = user['data'].decode()
                user['data'] = command_parse(user['data'])
                if user['data'][0][0] == 'un':
                    un = user['data'][0][1]
                if user['data'][1][0] == 'pw':
                    pw = user['data'][1][1]
                for i in accounts.unpw:
                    if un == i and pw == accounts.unpw[i]:
                        sockets_list.append(client)
                        user['header'] = str(len(user['data'][0][1])).encode()
                        user['data'] = user['data'][0][1].encode()
                        clients[client] = user
                        print(f"OPENED CONNECTION {clients[client]['data'].decode()}")
        else:
            message = receive_message(notified)
            if message is False:
                print(f"CLOSED CONNECTION {clients[notified]['data'].decode()}")
                sockets_list.remove(notified)
                del clients[notified]
            else:
                user = clients[notified]
                message['data'] = message['data'].decode()
                cmd = command_parse(message['data'])
                if cmd[0][0] == 'bk':
                    aa = accounts.adjust_amounts(user['data'].decode(), int(cmd[0][1]), int(cmd[0][2]))
                    if aa == False:
                        print("Couldn't Adjust Amounts")
                    else:
                        print('Adjusted Amounts')
                elif cmd[0][0] == 'su':
                    su = accounts.set_users()
                    if su == False:
                        print("Error setting users!")
                elif cmd[0][0] == 'jn':
                    main.players[notified] = 'joining'
                    main.init_players()
                    print(main.players)
                else:
                    print(f"{user['data'].decode()} > {message['data']}")

        for exception in exception_s:
            sockets_list.remove(exception)
            del clients[exception]

