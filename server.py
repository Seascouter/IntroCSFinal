# IMPORTS
import socket
import select
import accounts.accounts as accounts
import main
import time

# VARIABLES
HEADER_LENGTH = 10
PORT = 44421

gameNow = False

wait_list = []

cpi = 0
gameRound = 0

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

def adjust(userHand):
    output = ''
    for card in userHand:
        if card[1] == 'H':
            output += f'{card[0]}♥'
        elif card[1] == 'D':
            output += f'{card[0]}♦'
        elif card[1] == 'S':
            output += f'{card[0]}♠'
        elif card[1] == 'C':
            output += f'{card[0]}♣'
    return output

def getPlayerStatus():
    outputStr = ''
    for p in main.order:
        if main.stillIn[p] is True:
            outputStr += f'{clients[p]["data"].decode()}~i~{main.bets[p]};'
        else:
            outputStr += f'{clients[p]["data"].decode()}~o;'
    return outputStr[:-1]

def cleanUp():
    global gameNow, cpi, gameRound
    gameNow = False
    cpi = 0
    gameRound = 0
    main.cleanUpMain()






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
                    if not gameNow:
                        if len(main.players) < 6:
                            main.players[notified] = 'joining'
                            for player in main.players:
                                jnmsg = f'wt,{user["data"].decode()},Waiting for players ({len(main.players)}/3)'.encode()
                                jnmsg = {'header':f"{len(jnmsg):<{HEADER_LENGTH}}".encode(), 'data':jnmsg}
                                jnmsg = jnmsg['header']+jnmsg['data']
                                player.send(jnmsg)
                            print(f"\033[32m{user['data'].decode()} joined\033[0m")
                            if len(main.players) == 3:
                                print('3')
                        elif len(main.players) >= 6:
                            fmsg = f'wt,{user["data"].decode()},Game full...adding to wait queue'.encode()
                            fmsg = {'header': f"{len(fmsg):<{HEADER_LENGTH}}".encode(), 'data': fmsg}
                            fmsg = fmsg['header'] + fmsg['data']
                            notified.send(fmsg)
                            wait_list.append(notified)
                            print(len(wait_list), 'nogame')
                    else:
                        gmsg = f'wt,{user["data"].decode()},Game already started...adding to wait queue'.encode()
                        gmsg = {'header': f"{len(gmsg):<{HEADER_LENGTH}}".encode(), 'data': gmsg}
                        gmsg = gmsg['header'] + gmsg['data']
                        notified.send(gmsg)
                        wait_list.append(notified)
                        print(len(wait_list), 'game')
                elif cmd[0][0] == 'rs':
                    if gameNow:
                        if int(cmd[0][1]) <= accounts.users[clients[notified]['data'].decode()][0]:
                            main.bets[notified] = int(cmd[0][1])
                            print('rs')
                        else:
                            main.bets[notified] = accounts.users[clients[notified]['data'].decode()][0]
                    else:
                        lsmsg = f'wt,{clients[notified]["data"].decode()},You lost!'.encode()
                        lsmsg = {'header': f"{len(lsmsg):<{HEADER_LENGTH}}".encode(), 'data': lsmsg}
                        lsmsg = lsmsg['header'] + lsmsg['data']
                        notified.send(lsmsg)
                        time.sleep(0.25)
                        notified.send(lsmsg)
                elif cmd[0][0] == 'cl':
                    if gameNow:
                        main.bets[notified] = main.currentHigh
                        print('cl')
                    else:
                        lsmsg = f'wt,{clients[notified]["data"].decode()},You lost!'.encode()
                        lsmsg = {'header': f"{len(lsmsg):<{HEADER_LENGTH}}".encode(), 'data': lsmsg}
                        lsmsg = lsmsg['header'] + lsmsg['data']
                        notified.send(lsmsg)
                        time.sleep(0.25)
                        notified.send(lsmsg)
                elif cmd[0][0] == 'fd':
                    if gameNow:
                        main.stillIn[notified] = False
                        print('fd')
                    else:
                        lsmsg = f'wt,{clients[notified]["data"].decode()},You lost!'.encode()
                        lsmsg = {'header': f"{len(lsmsg):<{HEADER_LENGTH}}".encode(), 'data': lsmsg}
                        lsmsg = lsmsg['header'] + lsmsg['data']
                        notified.send(lsmsg)
                        time.sleep(0.25)
                        notified.send(lsmsg)
                else:
                    print(f"{user['data'].decode()} > {message['data']}")

        for exception in exception_s:
            sockets_list.remove(exception)
            del clients[exception]

        prev = 0
        for bets in main.bets:
            if main.bets[bets] > prev:
                prev = main.bets[bets]
        main.currentHigh = prev

        if not gameNow:
            print(len(main.players))
            if len(main.players) >= 3:
                gameNow = True
                main.create_deck(main.deck)
                main.init_players()
                main.deal_hands()
                print('dealt hands')
                if main.stillIn[main.order[cpi]] is True:
                    yourturn = f'yt,{main.currentHigh},{adjust(main.currentTable)},{adjust(main.players[main.order[cpi]].hand)},{getPlayerStatus()}'.encode()
                    yourturn = {'header': f"{len(yourturn):<{HEADER_LENGTH}}".encode(), 'data': yourturn}
                    yourturn = yourturn['header'] + yourturn['data']
                    main.order[cpi].send(yourturn)
                cpi+=1

        else:
            amtIn = main.get_amt_in()
            if amtIn == 1 and gameRound >= 3:
                for p in main.stillIn:
                    if main.stillIn[p] == True:
                        totalB = main.get_total_bets()
                        accounts.users[clients[p]['data'].decode()][0] += totalB
                        winmsg = f'wn,{totalB},{accounts.users[clients[p]["data"].decode()][0]}'.encode()
                        winmsg = {'header': f"{len(winmsg):<{HEADER_LENGTH}}".encode(), 'data': winmsg}
                        winmsg = winmsg['header'] + winmsg['data']
                        p.send(winmsg)
                        su = accounts.set_users()
                        if su == False:
                            print("Error setting users!")
                cleanUp()
                continue
            elif (amtIn == 2 and gameRound >=3) or gameRound >= 11:
                main.score_all_players()
                topScore = 0
                for p in main.players:
                    if main.players[p].topScore > topScore:
                        topScore = main.players[p].topScore
                winners = 0
                for p in main.players:
                    if main.players[p].topScore == topScore:
                        winners += 1
                if winners == 1:
                    for p in main.players:
                        if main.players[p].topScore == topScore:
                            totalB = main.get_total_bets()
                            accounts.users[clients[p]['data'].decode()][0] += totalB
                            winmsg = f'wn,{totalB},{accounts.users[clients[p]["data"].decode()][0]}'.encode()
                            winmsg = {'header': f"{len(winmsg):<{HEADER_LENGTH}}".encode(), 'data': winmsg}
                            winmsg = winmsg['header'] + winmsg['data']
                            p.send(winmsg)
                            su = accounts.set_users()
                            if su == False:
                                print("Error setting users!")
                else:
                    playerWinners = []
                    for p in main.players:
                        if main.players[p].topScore == topScore:
                            playerWinners.append(p)
                    totalB = main.get_total_bets()
                    for pw in playerWinners:
                        accounts.users[clients[pw]['data'].decode()][0] += round(totalB/3,0)
                        winmsg = f'wn,{totalB},{accounts.users[clients[pw]["data"].decode()][0]}'.encode()
                        winmsg = {'header': f"{len(winmsg):<{HEADER_LENGTH}}".encode(), 'data': winmsg}
                        winmsg = winmsg['header'] + winmsg['data']
                        pw.send(winmsg)
                        su = accounts.set_users()
                        if su == False:
                            print("Error setting users!")
                    for pl in main.players:
                        if pl not in playerWinners:
                            lsmsg = f'wt,{clients[pl]["data"].decode()},You lost!'.encode()
                            lsmsg = {'header': f"{len(lsmsg):<{HEADER_LENGTH}}".encode(), 'data': lsmsg}
                            lsmsg = lsmsg['header'] + lsmsg['data']
                            pl.send(lsmsg)

            gameRound += 1
            if cpi >= len(main.order):
                cpi = 0
                print('reset cpi')

            if gameRound == 3:
                main.deal_table(3)
            elif gameRound == 6:
                main.deal_table(1)
            elif gameRound == 9:
                main.deal_table(1)
            while main.stillIn[main.order[cpi]] is False:
                cpi += 1
            yourturn = f'yt,{main.currentHigh},{adjust(main.currentTable)},{adjust(main.players[main.order[cpi]].hand)},{getPlayerStatus()}'.encode()
            yourturn = {'header': f"{len(yourturn):<{HEADER_LENGTH}}".encode(), 'data': yourturn}
            yourturn = yourturn['header'] + yourturn['data']
            main.order[cpi].send(yourturn)
            cpi += 1
















print('how did you even get here?')