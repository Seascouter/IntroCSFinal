# IMPORTS
import socket
import select
import accounts.accounts as accounts
import main
import signal
import time

# VARIABLES
HEADER_LENGTH = 10
PORT = 44421

wait_list = []

timedout = False

# CLASSES
class TimeOutException(Exception):
    pass


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

def alarm_handler(signum, frame):
    raise Exception('XYZZYX')

def reset_time(time):
    signal.alarm(time)




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


    currPLen = len(main.players)

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
                currUserLen = len(clients)
                for i in accounts.unpw:
                    if un == i and pw == accounts.unpw[i]:
                        sockets_list.append(client)
                        user['header'] = str(len(user['data'][0][1])).encode()
                        user['data'] = user['data'][0][1].encode()
                        clients[client] = user
                        lnmsg = 'sl'
                        print(f"OPENED CONNECTION {clients[client]['data'].decode()}")
                if currUserLen == len(clients):
                    lnmsg = 'wl'
                    print('Wrong Login')
                lnmsg = {'header': f"{len(lnmsg):<{HEADER_LENGTH}}".encode(), 'data': lnmsg.encode()}
                lnmsg = lnmsg['header'] + lnmsg['data']
                client.send(lnmsg)

        else:
            message = receive_message(notified)
            if message is False:
                print(f"CLOSED CONNECTION {clients[notified]['data'].decode()}")
                sockets_list.remove(notified)
                del clients[notified]
                if notified in main.players:
                    del main.players[notified]
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
                    for player in clients:
                        jnmsg = f'wt,{user["data"].decode()},Waiting for players ({len(main.players)}/3)'.encode()
                        jnmsg = {'header':f"{len(jnmsg):<{HEADER_LENGTH}}".encode(), 'data':jnmsg}
                        jnmsg = jnmsg['header']+jnmsg['data']
                        player.send(jnmsg)
                    if len(main.players) == 3:
                        reset_time(10)

                else:
                    print(f"{user['data'].decode()} > {message['data']}")

    signal.signal(signal.SIGALRM, alarm_handler)
    if len(main.players) >= 3:
        print('herehere')
        try:
            print(currPLen, len(main.players))
            if currPLen == len(main.players):
                print('wait')
                time.sleep(1)
            else:
                reset_time(10)
        except Exception as ex:
            print(ex)
            reset_time(0)
            print('start game')
            main.init_players()
            print(len(main.players))




        for exception in exception_s:
            sockets_list.remove(exception)
            del clients[exception]






print('how did you even get here?')