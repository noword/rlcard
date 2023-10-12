from .utils import cards2str, sort_cards, CARD_TYPE


class ShanghaiDouDiZhuPlayer:
    def __init__(self, player_id, np_random):
        self.np_random = np_random
        self.player_id = player_id
        self.initial_hand = None
        self._current_hand = []
        self.played_cards = None
        self.bid_level = -1
        self.allow_bomb_number = 1
        # record cards removed from self._current_hand for each play()
        # and restore cards back to self._current_hand when play_back()
        self.recorded_played_cards = []
        self.reported = False

    @property
    def current_hand(self):
        return self._current_hand

    def set_current_hand(self, value):
        self._current_hand = sort_cards(value)
        self.initial_hand = cards2str(self._current_hand)

    def available_actions(self, greater_player=None, judger=None, need_bid=False):
        if need_bid:
            # 叫牌
            if greater_player:
                actions = ['bid_0', ]
                for i in range(greater_player.bid_level + 1, 4):
                    actions.append(f'bid_{i}')
            else:
                actions = ['bid_0', 'bid_1', 'bid_2', 'bid_3']
            # print('available_actions', self.player_id, greater_player.player_id if greater_player else None, actions)
            return actions
        elif len(self._current_hand) == 33 \
                and len(judger.get_reported_cards(self)) > 0 \
                and not self.reported:
            # 报到, 地主手里有33张牌, 且手里有大于等于7张的炸弹, 且没有报到过
            self.reported = True
            return ['report_0', 'report_1']
        elif greater_player is None or greater_player.player_id == self.player_id:  # 出任意牌
            return judger.get_playable_cards(self)

        return ['pass',] + judger.get_gt_cards(self, greater_player)

    def play_cards(self, cards):
        if cards != 'pass':
            if CARD_TYPE[cards]['type'] == 'bomb':
                self.allow_bomb_number -= 1

            remain_cards = self._current_hand.copy()
            for card in cards:
                for i, remain in enumerate(remain_cards):
                    if str(remain)[0] == card:
                        remain_cards.pop(i)
                        break

            self._current_hand = remain_cards
        self.recorded_played_cards.append(cards)

    def get_state(self, actions):
        return {'actions': actions,
                'id': self.player_id,
                'current_hand': cards2str(sort_cards(self._current_hand))
                }
