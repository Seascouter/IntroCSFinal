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

logFile = f'logs/{time.ctime()}'

# FUNCTIONS
# writes to the log file
def writeToLog(msg):
    with open(logFile, 'a') as f:
        f.write(f"{time.ctime()} | {msg}\n")

# receives the message and either returns false if no message or the header and the message
def receive_message(cs):
    try:
        message_header = cs.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode().strip())

        return {'header': message_header, 'data': cs.recv(message_length)}

    except:
        return False

# parses the command by splitting it by its | and its ,
def command_parse(msg):
    msg = msg.split("|")
    for i in range(len(msg)):
        msg[i] = msg[i].split(",")
    return msg

# turns the letters in the cards of a hand to unicode characters
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

# turns the player statuses in a game from a dictionary to a string of players, their status, and their bets.
def getPlayerStatus():
    outputStr = ''
    for p in main.order:
        if main.stillIn[p] is True:
            outputStr += f'{clients[p]["data"].decode()}~i~{main.bets[p]};'
        else:
            outputStr += f'{clients[p]["data"].decode()}~o;'
    return outputStr[:-1]

# resets all values of the game for the next game
def cleanUp():
    global gameNow, cpi, gameRound
    gameNow = False
    cpi = 0
    gameRound = 0
    main.cleanUpMain()






# MAIN CODE

# sets up the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# gets the user information
accounts.get_users()

server_socket.bind(('', PORT))

server_socket.listen()

# sets up more variables
sockets_list = [server_socket]
clients = {}



print(f'Server open on {PORT}')

un = ''
pw = ''

while True:

    currPLen = len(main.players)
    # gets the reading and exception sockets
    read_s, _, exception_s = select.select(sockets_list, [], sockets_list)
    for notified in read_s:
        # if the notified socket is the server
        if notified == server_socket:
            # opens the client
            client, caddr = server_socket.accept()
            # if it is not logged in
            if client not in clients:
                # receive the message
                user = receive_message(client)
                if user is False:
                    continue
                # gets the data
                user['data'] = user['data'].decode()
                user['data'] = command_parse(user['data'])
                # get the username and password
                if user['data'][0][0] == 'un':
                    un = user['data'][0][1]
                if user['data'][1][0] == 'pw':
                    pw = user['data'][1][1]
                currUserLen = len(clients)
                # loops thru all of the accounts and sees if it is in the accounts
                for i in accounts.unpw:
                    if un == i and pw == accounts.unpw[i]:
                        # if it is, it gets logged in, logged on the ledger life, and sends a success message back
                        sockets_list.append(client)
                        user['header'] = str(len(user['data'][0][1])).encode()
                        user['data'] = user['data'][0][1].encode()
                        clients[client] = user
                        lnmsg = f'sl,{accounts.users[user["data"].decode()][0]},{accounts.users[user["data"].decode()][1]}'
                        print(f"OPENED CONNECTION {clients[client]['data'].decode()}")
                        writeToLog(f"OPENED CONNECTION {clients[client]['data'].decode()}")
                    # if it isnt, sends a message back that says it didn't work and the client needs to try again
                if currUserLen == len(clients):
                    lnmsg = 'wl'
                    print('Wrong Login')
                    writeToLog(f"Wrong Login")
                lnmsg = {'header': f"{len(lnmsg):<{HEADER_LENGTH}}".encode(), 'data': lnmsg.encode()}
                lnmsg = lnmsg['header'] + lnmsg['data']
                client.send(lnmsg)

        else:
            # if it is logged in, the message is checked if it is a disconnect or a command
            message = receive_message(notified)
            if message is False:
                print(f"CLOSED CONNECTION {clients[notified]['data'].decode()}")
                writeToLog(f"CLOSED CONNECTION {clients[notified]['data'].decode()}")
                sockets_list.remove(notified)
                del clients[notified]
                if notified in main.players:
                    del main.players[notified]
            else:
                # parses the command
                user = clients[notified]
                message['data'] = message['data'].decode()
                cmd = command_parse(message['data'])
                # if it is bk, it will adjust amounts between balances
                if cmd[0][0] == 'bk':
                    aa = accounts.adjust_amounts(user['data'].decode(), int(cmd[0][1]), int(cmd[0][2]))
                    if aa == False:
                        print("Couldn't Adjust Amounts")
                    else:
                        print('Adjusted Amounts')
                        writeToLog('Adjusted Amounts')
                # if it is su, it will set the new values in the accounts file
                elif cmd[0][0] == 'su':
                    su = accounts.set_users()
                    writeToLog('Set User Amounts in accounts.csv')
                    if su == False:
                        print("Error setting users!")
                # if it is jn, it will join the game
                elif cmd[0][0] == 'jn':
                    if not gameNow:
                        if len(main.players) < 3:
                            main.players[notified] = 'joining'
                            for player in main.players:
                                jnmsg = f'wt,{user["data"].decode()},Waiting for players ({len(main.players)}/3)'.encode()
                                jnmsg = {'header':f"{len(jnmsg):<{HEADER_LENGTH}}".encode(), 'data':jnmsg}
                                jnmsg = jnmsg['header']+jnmsg['data']
                                player.send(jnmsg)
                            print(f"\033[32m{user['data'].decode()} joined\033[0m")
                            writeToLog(f"{user['data'].decode()} joined")
                            if len(main.players) == 3:
                                print('3')
                        elif len(main.players) >= 6:
                            fmsg = f'wt,{user["data"].decode()},Game happening right now...try later'.encode()
                            fmsg = {'header': f"{len(fmsg):<{HEADER_LENGTH}}".encode(), 'data': fmsg}
                            fmsg = fmsg['header'] + fmsg['data']
                            notified.send(fmsg)
                            wait_list.append(notified)

                    else:
                        gmsg = f'wt,{user["data"].decode()},Game happening right now...try later'.encode()
                        gmsg = {'header': f"{len(gmsg):<{HEADER_LENGTH}}".encode(), 'data': gmsg}
                        gmsg = gmsg['header'] + gmsg['data']
                        notified.send(gmsg)
                        wait_list.append(notified)
                # if it is rs, it will raise by the amount specified
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
                # if it is cl, it will meet the previous raised amount
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
                # if it is fd, it will fold
                elif cmd[0][0] == 'fd':
                    if gameNow:
                        main.stillIn[notified] = False
                        lsmsg = f'wt,{clients[notified]["data"].decode()},'.encode()
                        lsmsg = {'header': f"{len(lsmsg):<{HEADER_LENGTH}}".encode(), 'data': lsmsg}
                        lsmsg = lsmsg['header'] + lsmsg['data']
                        notified.send(lsmsg)
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

        # for all exception sockets, it will remove them from the list and dictionary of sockets
        for exception in exception_s:
            sockets_list.remove(exception)
            del clients[exception]

        # this gets the highest current bet
        prev = 0
        for bets in main.bets:
            if main.bets[bets] > prev:
                prev = main.bets[bets]
        main.currentHigh = prev

        # if there isnt a game now,
        if not gameNow:
            # and there is enough people
            if len(main.players) >= 3:
                # there is a game, deck and players and hands are created, and the first person is played
                gameNow = True
                main.create_deck(main.deck)
                main.init_players()
                main.deal_hands()
                print('dealt hands')
                writeToLog(f"Deck created, players initialized, hands dealt")
                if main.stillIn[main.order[cpi]] is True:
                    yourturn = f'yt,{main.currentHigh},{adjust(main.currentTable)},{adjust(main.players[main.order[cpi]].hand)},{getPlayerStatus()}'.encode()
                    yourturn = {'header': f"{len(yourturn):<{HEADER_LENGTH}}".encode(), 'data': yourturn}
                    yourturn = yourturn['header'] + yourturn['data']
                    main.order[cpi].send(yourturn)
                cpi+=1

        else:
            # if there is a game, it will check for winners at certain intervals first
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
                writeToLog(f"{clients[p]['data'].decode()} won")
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
                            writeToLog(f"{clients[p]['data'].decode()} won")
                else:
                    playerWinners = []
                    for p in main.players:
                        if main.players[p].topScore == topScore:
                            playerWinners.append(p)
                    totalB = main.get_total_bets()
                    for pw in playerWinners:
                        accounts.users[clients[pw]['data'].decode()][0] += int(round(totalB/3,0))
                        winmsg = f'wn,{totalB},{accounts.users[clients[pw]["data"].decode()][0]}'.encode()
                        winmsg = {'header': f"{len(winmsg):<{HEADER_LENGTH}}".encode(), 'data': winmsg}
                        winmsg = winmsg['header'] + winmsg['data']
                        pw.send(winmsg)
                        su = accounts.set_users()
                        if su == False:
                            print("Error setting users!")
                        writeToLog(f"{clients[pw]['data'].decode()} won")
                    for pl in main.players:
                        if pl not in playerWinners:
                            lsmsg = f'wt,{clients[pl]["data"].decode()},You lost!'.encode()
                            lsmsg = {'header': f"{len(lsmsg):<{HEADER_LENGTH}}".encode(), 'data': lsmsg}
                            lsmsg = lsmsg['header'] + lsmsg['data']
                            pl.send(lsmsg)
                            accounts.users[clients[pl]['data']][0] -= main.bets[pl]
            # game round is increased and cpi is checked to see if it is above the amount of players (if it is it is reset)
            gameRound += 1
            if cpi >= len(main.order):
                cpi = 0
                print('reset cpi')
            # if there are no winners yet, game round is increased and cards are dealt to table accordingly
            if gameRound == 3:
                main.deal_table(3)
            elif gameRound == 6:
                main.deal_table(1)
            elif gameRound == 9:
                main.deal_table(1)
            while main.stillIn[main.order[cpi]] is False:
                cpi += 1
            # allows client to have their turn
            yourturn = f'yt,{main.currentHigh},{adjust(main.currentTable)},{adjust(main.players[main.order[cpi]].hand)},{getPlayerStatus()}'.encode()
            yourturn = {'header': f"{len(yourturn):<{HEADER_LENGTH}}".encode(), 'data': yourturn}
            yourturn = yourturn['header'] + yourturn['data']
            main.order[cpi].send(yourturn)
            cpi += 1
















print('how did you even get here?')