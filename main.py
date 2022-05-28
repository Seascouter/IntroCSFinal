# IMPORTS
import random
import hands

# VARIABLES
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
suits = ['S', 'C', 'H', 'D']

players = {}
stillIn = {}
bets = {}
order = []
currentHigh = 0
currentTable = []
deck = []


# FUNCTIONS
def create_deck(d):
    for suit in suits:
        for rank in ranks:
            d.append((rank, suit))
    random.shuffle(d)

def deal_hands():
    for p in players:
        phand = []
        for x in range(2):
            phand.append(deck.pop())
        players[p].hand = phand

def get_amt_in():
    amtIn = 0
    for p in stillIn:
        if stillIn[p] == True:
            amtIn += 1
    return amtIn

def get_total_bets():
    total = 0
    for p in bets:
        total += bets[p]
    return total

def deal_table(x):
    for i in range(x):
        currentTable.append(deck.pop(0))

def init_players():
    for player in players:
        if players[player] == 'joining':
            players[player] = hands.Player()
            order.append(player)
            stillIn[player] = True
            bets[player] = 0

def score_all_players():
    while len(currentTable) < 5:
        currentTable.append(deck.pop(0))
    for p in stillIn:
        if stillIn[p] == True:
            temphand = players[p].hand
            for i in range(len(currentTable)):
                temphand.append(currentTable[i])
            players[p].hand = temphand

            players[p].getRankHand()
            players[p].getPoints()
            players[p].getHighScore()

def cleanUpMain():
    global players, stillIn, bets, order, currentTable, currentHigh, deck
    players = {}
    stillIn = {}
    bets = {}
    order = []
    currentHigh = 0
    currentTable = []
    deck = []


# MAIN CODE
