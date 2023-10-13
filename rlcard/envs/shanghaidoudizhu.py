from collections import Counter, OrderedDict
import numpy as np
from functools import lru_cache
from rlcard.envs.env import Env
from rlcard.games.shanghaidoudizhu.utils import ACTION_2_ID, ACTIONS


class ShanghaiDouDiZhuEnv(Env):
    def __init__(self, config):
        from rlcard.games.shanghaidoudizhu.utils import ACTION_2_ID
        from rlcard.games.shanghaidoudizhu import Game
        self.name = 'shanghai-doudizhu'
        self.game = Game()
        super().__init__(config)
        self.state_shape = [[1405,], [1405,], [1405,], [1405,]]
        self.action_shape = [[59] for _ in range(self.num_players)]

    def _extract_state(self, state):
        trace = np.zeros((110, 12), dtype=np.int8)
        for i, (pid, cards) in enumerate(state['trace']):
            trace[i] = _number2onehot(pid << 10 | ACTION_2_ID[cards], 12)
            # trace[i] = np.concatenate((_number2onehot(pid, 2), _number2onehot(ACTION_2_ID[cards], 10)))

        bid_levels = np.array([_number2onehot(level if level >= 0 else 0, 2) for level in state['bid_levels']])
        allow_bomb_number = np.array([_number2onehot(b, 4) for b in state['allow_bomb_number']])

        obs = np.concatenate((_cards2array(state['current_hand']),
                              _number2onehot(state['id'], 2),
                              _number2onehot(state['landlord_id'] if state['landlord_id'] >= 0 else 0, 3),
                              trace.flatten(),
                              bid_levels.flatten(),
                              allow_bomb_number.flatten(),
                              ))

        return {'obs': obs,
                'legal_actions': self._get_legal_actions(),
                'raw_legal_actions': state['actions'],
                }

    def _get_legal_actions(self):
        ''' Get all legal actions for current state

        Returns:
            legal_actions (list): a list of legal actions' id
        '''
        legal_actions = self.game.state['actions']
        legal_actions = {ACTION_2_ID[action]: _action2array(action) for action in legal_actions}
        return legal_actions

    def _decode_action(self, action_id):
        return ACTIONS[action_id]

    def get_payoffs(self):
        ''' Get the payoffs of players. Must be implemented in the child class.

        Returns:
            payoffs (list): a list of payoffs for each player
        '''
        return self.game.get_payoffs()

    def get_action_feature(self, action):
        return _action2array(self._decode_action(action))


def _number2onehot(number, length):
    return np.array([int(i) for i in f'{number:0{length}b}'])


CARD_POSITION = {'3': 0, '4': 4, '5': 8, '6': 12, '7': 16, '8': 20, '9': 24, 'T': 28,
                 'J': 32, 'Q': 36, 'K': 40, 'A': 44, '2': 48, 'B': 52, 'R': 54}
BID_POSITION = 56
REPORT_POSITION = 58


@ lru_cache(650)
def _cards2array(cards):
    array = np.zeros(56, dtype=np.int8)
    if cards != 'pass':
        for card, num_times in Counter(cards).items():
            length = 2 if card in 'BR' else 4
            index = CARD_POSITION[card]
            array[index:index + length] = _number2onehot(num_times, length)

    return array


@ lru_cache(660)
def _action2array(action):
    array = np.zeros(59, dtype=np.int8)
    if action != 'pass':
        if action.startswith('report'):
            array[REPORT_POSITION] = _number2onehot(int(action[-1]), 1)
        elif action.startswith('bid'):
            array[BID_POSITION:BID_POSITION + 2] = _number2onehot(int(action[-1]), 2)
        else:
            array[:BID_POSITION] = _cards2array(action)

    return array
