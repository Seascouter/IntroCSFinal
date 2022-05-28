

class Player:
    # values
    hand = []
    rankHand = []
    pairs = []
    points = {
        'rsf': False,
        'sf': False,
        'four': False,
        'fh': False,
        'f': False,
        's': False,
        'three': False,
        'twop': False,
        'pair': False,
        'highcard': ()
    }
    cardVals = {}
    highScore = ''
    topScore = 0

    # checks for royal straight flush
    def getRSF(self):
        hasAce = False
        for i in range(len(self.hand)):
            if self.hand[i][0] == 'A':
                hasAce = True
                break
        if hasAce and self.points['sf']:
            self.points['rsf'] = True

    # checks on straight flush
    def getStraightFlush(self):
        if self.points['s'] == True and self.points['f'] == True:
            self.points['sf'] = True

    # checks for 4 of a kind
    def getFourKind(self):
        for i in self.cardVals:
            if self.cardVals[i] >= 4:
                self.points['four'] = True

    # checks for full house
    def getFullHouse(self):
        card3 = 0
        if self.points['three']:
            for i in self.cardVals:
                if self.cardVals[i] >= 3:
                    card3 = str(i)
            if self.points['pair']:
                for i in range(len(self.pairs)):
                    if self.pairs[i][0][0] != card3:
                        self.points['fh'] = True

    # checks for flush
    def getFlush(self):
        suits = {
            'H':0,
            'D':0,
            'C':0,
            'S':0
        }
        for i in range(len(self.hand)):
            suits[self.hand[i][1]]+=1
        for i in suits:
            if suits[i] >= 5:
                self.points['f'] = True

    # checks for straight
    def getStraight(self):
        lowestVal = 14
        if len(self.rankHand) >= 5:
            for i in range(len(self.rankHand)):
                if self.rankHand[i][0] < lowestVal:
                    lowestVal = self.rankHand[i][0]
            straightVals = {}
            for i in range(lowestVal, lowestVal+5):
                straightVals[i] = 0
            for i in range(len(self.rankHand)):
                if self.rankHand[i][0] in straightVals:
                    straightVals[self.rankHand[i][0]]+=1
            corrCount = 0
            for i in straightVals:
                if straightVals[i] == 1:
                    corrCount += 1
            if corrCount == 5:
                self.points['s'] = True

    # checks for 3 of a kind
    def getThreeKind(self):
        for i in range(len(self.hand)):
            self.cardVals[self.hand[i][0]] = 0
        for i in range(len(self.hand)):
            self.cardVals[self.hand[i][0]]+=1
        for i in self.cardVals:
            if self.cardVals[i] >= 3:
                self.points['three'] = True

    # checks for pair or 2pair
    def getPairs(self):
        if len(self.hand) >= 2:
            for i in range(len(self.hand)):
                for j in range(len(self.hand)):
                    if self.hand[i] != self.hand[j]:
                        if self.hand[i][0] == self.hand[j][0] and [self.hand[j], self.hand[i]] not in self.pairs:
                            self.pairs.append([self.hand[i], self.hand[j]])
            if len(self.pairs) >= 1:
                self.points['pair'] = True
            if len(self.pairs) >= 2:
                self.points['twop'] = True

    # gets the high card
    def getHighCards(self):
        self.rankHand.sort(reverse=True)
        self.points['highcard'] = self.rankHand

    # gets all of the ranks for the face cards
    def getRankHand(self):
        for i in range(len(self.hand)):
            if self.hand[i][0] == 'A':
                self.rankHand.append((14, self.hand[i][1]))
            elif self.hand[i][0] == 'K':
                self.rankHand.append((13, self.hand[i][1]))
            elif self.hand[i][0] == 'Q':
                self.rankHand.append((12, self.hand[i][1]))
            elif self.hand[i][0] == 'J':
                self.rankHand.append((11, self.hand[i][1]))
            else:
                self.rankHand.append((int(self.hand[i][0]), self.hand[i][1]))

    # checks for each hand
    def getPoints(self):
        self.getHighCards()
        self.getPairs()
        self.getThreeKind()
        self.getStraight()
        self.getFlush()
        self.getFullHouse()
        self.getFourKind()
        self.getStraightFlush()
        self.getRSF()

    # sets the high score of the hand
    def getHighScore(self):
        self.highScore = self.points['highcard']
        self.topScore = 1
        if self.points['pair']:
            self.highScore = 'pair'
            self.topScore = 2
        if self.points['twop']:
            self.highScore = 'twop'
            self.topScore = 3
        if self.points['three']:
            self.highScore = 'three'
            self.topScore = 4
        if self.points['s']:
            self.highScore = 's'
            self.topScore = 5
        if self.points['f']:
            self.highScore = 'f'
            self.topScore = 6
        if self.points['fh']:
            self.highScore = 'fh'
            self.topScore = 7
        if self.points['four']:
            self.highScore = 'four'
            self.topScore = 8
        if self.points['sf']:
            self.highScore = 'sf'
            self.topScore = 9
        if self.points['rsf']:
            self.highScore = 'rsf'
            self.topScore = 10

# ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
# suits = ['S','C','H','D']