# IMPORTS
import random
import hands

# VARIABLES
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
suits = ['S', 'C', 'H', 'D']

players = {}
stillIn = {}
order = []

# FUNCTIONS
def create_deck(d):
    for suit in suits:
        for rank in ranks:
            d.append((rank, suit))
    random.shuffle(d)

def init_players():
    for player in players:
        if players[player] == 'joining':
            players[player] = hands.Player()
        order.append(player)
        stillIn[player] = True

# MAIN CODE
