import numpy as np
from .player import ShanghaiDouDiZhuPlayer as Player
from .round import ShanghaiDoudizhuRound as Round
from .judger import ShanghaiDoudizhuJudger as Judger
from .dealer import ShanghaiDoudizhuDealer as Dealer
from .utils import ACTIONS

# 上海斗地主规则: https://www.17dp.com/down/gamelist/id/201
# 适当简化了一些记分规则


class ShanghaiDoudizhuGame:
    def __init__(self, allow_step_back=False):
        if allow_step_back:
            raise NotImplementedError

        self.allow_step_back = allow_step_back
        self.np_random = np.random.RandomState()
        self.num_players = 4
        self.judger = Judger()
        self.dealer = Dealer(self.np_random)

    def init_game(self):
        self.winner_id = None
        self.landlord_id = -1
        self.reported = []

        self.players = [Player(num, self.np_random) for num in range(self.num_players)]

        # 发牌
        cards = self.dealer.deal_cards()
        for i in range(4):
            self.players[i].set_current_hand(cards[i])
        self.hole_cards = cards[-1]

        self.round = Round(self.np_random)
        self.first_bidder = self.round.initiate()

        self.state = self.get_state(self.round.current_player_id)
        return self.state, self.round.current_player_id

    @property
    def need_bid(self):
        return self.landlord_id < 0

    def get_num_players(self):
        ''' Return the number of players in doudizhu

        Returns:
            int: the number of players in doudizhu
        '''
        return self.num_players

    def is_over(self):
        ''' Judge whether a game is over

        Returns:
            Bool: True(over) / False(not over)
        '''
        return self.winner_id is not None

    def step(self, action):
        ''' Perform one draw of the game

        Args:
            action (str): specific action of doudizhu. Eg: '33344'

        Returns:
            dict: next player's state
            int: next player's id
        '''
        if self.allow_step_back:
            # TODO: don't record game.round, game.players, game.judger if allow_step_back not set
            raise NotImplementedError

        current_id = self.round.current_player_id

        # for p in self.players:
        #     from .utils import sort_cards, cards2str
        #     print(cards2str(sort_cards(p.current_hand)))

        if action == 'report_1':
            self.reported = self.judger.get_reported_cards(self.players[current_id])

        next_id = self.round.proceed_round(self.players, action)

        if self.landlord_id == -1 and min([p.bid_level for p in self.players]) > -1:
            self.set_landlord()
            next_id = self.landlord_id

        if self.judger.judge_game(self.players, current_id):
            self.winner_id = current_id

        self.state = self.get_state(next_id)
        return self.state, next_id

    def set_landlord(self):
        bids = [p.bid_level for p in self.players]
        self.round.current_player_id = self.landlord_id = bids.index(max(bids))
        self.round.greater_player = None
        landload = self.players[self.landlord_id]
        landload.set_current_hand(landload.current_hand + self.hole_cards)

        free_bomb = False
        for i in range(4):
            n = (self.first_bidder + i) % self.num_players
            player = self.players[n]
            if n == self.landlord_id:
                player.allow_bomb_number = 0xf
                free_bomb = (player.bid_level == 3)
            elif free_bomb:
                player.allow_bomb_number = 0xf
            elif player.bid_level == 2:
                player.allow_bomb_number = 2
            else:
                player.allow_bomb_number = 1

    def get_state(self, player_id):
        ''' Return player's state

        Args:
            player_id (int): player id

        Returns:
            (dict): The state of the player
        '''
        player = self.players[player_id]
        # others_hands = self._get_others_current_hand(player)
        # num_cards_left = [len(self.players[i].current_hand) for i in range(self.num_players)]
        if self.is_over():
            actions = []
        else:
            actions = list(player.available_actions(self.round.greater_player, self.judger, self.need_bid))
        # print('get_state', player_id, actions)
        state = player.get_state(actions)
        state['landlord_id'] = self.landlord_id
        state['trace'] = self.round.trace
        state['bid_levels'] = [p.bid_level for p in self.players]
        state['allow_bomb_number'] = [p.allow_bomb_number for p in self.players]
        state['cards_number'] = [len(p.current_hand) for p in self.players]
        return state

    @staticmethod
    def get_num_actions():
        ''' Return the total number of abstract acitons

        Returns:
            int: the total number of abstract actions of shanghai doudizhu
        '''
        return len(ACTIONS)

    def get_player_id(self):
        ''' Return current player's id

        Returns:
            int: current player's id
        '''
        return self.round.current_player_id

    def get_payoffs(self):
        # 未考虑头撩、荒番、摊打、明王的情况
        # 为了简化计算, 只加分，不扣分
        payoffs = np.zeros(4)
        score = self.players[self.landlord_id].bid_level
        if len(self.reported) > 0:
            # 报到局
            if self.winner_id == self.landlord_id:
                # 地主赢
                payoffs[self.landlord_id] = score * (len(self.reported) + 1) * 3
        else:
            if self.winner_id == self.landlord_id:
                payoffs[self.landlord_id] = score * 3
            else:
                for i in range(4):
                    if i != self.landlord_id:
                        payoffs[i] = score

        return payoffs
