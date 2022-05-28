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
# creates the deck from suits and ranks
def create_deck(d):
    for suit in suits:
        for rank in ranks:
            d.append((rank, suit))
    random.shuffle(d)

# deals 2 cards to every player
def deal_hands():
    for p in players:
        phand = []
        for x in range(2):
            phand.append(deck.pop())
        players[p].hand = phand

# gets the number of people who are in
def get_amt_in():
    amtIn = 0
    for p in stillIn:
        if stillIn[p] == True:
            amtIn += 1
    return amtIn

# gets the total pot of the bets
def get_total_bets():
    total = 0
    for p in bets:
        total += bets[p]
    return total

# deals a number of cards to the table
def deal_table(x):
    for i in range(x):
        currentTable.append(deck.pop(0))

# for all players in players, if their value is joining, it will set them to an object
def init_players():
    for player in players:
        if players[player] == 'joining':
            players[player] = hands.Player()
            order.append(player)
            stillIn[player] = True
            bets[player] = 0

#  this gets the hand score of all of the players still in
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

# this cleans up all of the variables in this file
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
