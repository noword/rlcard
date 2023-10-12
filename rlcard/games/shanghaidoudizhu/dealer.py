from .utils import init_108_deck


class ShanghaiDoudizhuDealer:
    def __init__(self, np_random):
        self.np_random = np_random
        self.deck = init_108_deck()
        self.landlord = None
        self.hole_cards = []

    def shuffle(self):
        ''' Randomly shuffle the deck
        '''
        self.np_random.shuffle(self.deck)

    def deal_cards(self):
        '''
        4个玩家, 每人25张, 底牌8张
        '''
        cards = []
        for i in range(4):
            cards.append(self.deck[i * 25: (i + 1) * 25])
        cards.append(self.deck[100:])

        return cards
