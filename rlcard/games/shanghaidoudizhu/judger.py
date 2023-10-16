from .utils import (cards2str,
                    sort_cards,
                    get_playable_cards,
                    get_gt_cards,
                    get_reported_cards,
                    ACTION_PATTERNS,
                    ACTIONS,
                    CARD_TYPE,
                    TYPE_CARD,
                    ACTION_2_ID)


class ShanghaiDoudizhuJudger:
    def get_playable_cards(self, player):
        return get_playable_cards(cards2str(sort_cards(player.current_hand)),
                                  player.allow_bomb_number > 0,
                                  ','.join(player.reported_cards)
                                  )

    def get_gt_cards(self, player, greater_player):
        current_cards = cards2str(sort_cards(player.current_hand))
        target_cards = greater_player.played_cards
        return get_gt_cards(current_cards, target_cards,
                            player.allow_bomb_number > 0,
                            ','.join(player.reported_cards))

    def get_reported_cards(self, player):
        '''
            得到7张以上炸弹的数量,用于判断地主是否能报到
        '''
        return get_reported_cards(cards2str(sort_cards(player.current_hand)))

    @staticmethod
    def judge_game(players, player_id):
        ''' Judge whether the game is over

        Args:
            players (list): list of DoudizhuPlayer objects
            player_id (int): integer of player's id

        Returns:
            (bool): True if the game is over
        '''
        player = players[player_id]
        return len(player.current_hand) == 0
