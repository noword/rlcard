import numpy as np
from .dealer import ShanghaiDoudizhuDealer
from .utils import cards2str, sort_cards


class ShanghaiDoudizhuRound:
    def __init__(self, np_random):
        self.np_random = np_random
        self.num_players = 4
        self.trace = []

        self.current_player_id = 0
        self.greater_player = None

    def initiate(self):
        self.current_player_id = self.np_random.random_integers(0, 3)
        return self.current_player_id

    def proceed_round(self, players, action):
        '''
        Call functions from other classes to keep one round running

        Args:
            players (list): The list of players that play the game
            action (str/int): An legal action taken by the player

        Returns:
            (int): The game_pointer that indicates the next player
        '''
        player = players[self.current_player_id]
        if action != 'pass':
            self.trace.append((self.current_player_id, action, cards2str(sort_cards(player.current_hand))))
        if action.startswith('report'):
            return self.current_player_id
        elif action.startswith('bid'):
            player.bid_level = int(action[-1])
            if action[-1] != '0':
                self.greater_player = player
        else:
            if action != 'pass':
                self.greater_player = player
                player.played_cards = action
            player.play_cards(action)

        # print('proceed_round', self.current_player, action)
        self.current_player_id = (self.current_player_id + 1) % self.num_players
        return self.current_player_id
