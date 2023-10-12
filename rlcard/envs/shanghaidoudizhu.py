from collections import Counter, OrderedDict
import numpy as np

from rlcard.envs.env import Env
from rlcard.games.shanghaidoudizhu.utils import ACTION_2_ID, ACTIONS


class ShanghaiDouDiZhuEnv(Env):
    def __init__(self, config):
        from rlcard.games.shanghaidoudizhu.utils import ACTION_2_ID
        from rlcard.games.shanghaidoudizhu import Game
        self.name = 'shanghai-doudizhu'
        self.game = Game()
        super().__init__(config)
        self.state_shape = [[5861], [5861], [5861], [5861]]
        self.action_shape = [[56 + 4] for _ in range(self.num_players)]

    def _extract_state(self, state):
        trace = np.zeros((100, 58), dtype=np.int8)
        for i, (pid, cards) in enumerate(state['trace']):
            trace[i] = np.concatenate((_number2onehot(pid, 2), _cards2array(cards)))

        obs = np.concatenate((_cards2array(state['current_hand']),
                              _number2onehot(state['id'], 2),
                              _number2onehot(state['landlord_id'] + 1, 3),
                              trace.flatten()
                              ))
        print(obs.shape)

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


def _number2onehot(number, length):
    return np.array([int(i) for i in f'{number:0{length}b}'])


CARD_POSITION = {'3': 0, '4': 4, '5': 8, '6': 12, '7': 16, '8': 20, '9': 24, 'T': 28,
                 'J': 32, 'Q': 36, 'K': 40, 'A': 44, '2': 48, 'B': 52, 'R': 54}
BID_POSITION = 56
REPORT_POSITION = 58


def _cards2array(cards):
    array = np.zeros(56, dtype=np.int8)
    if cards != 'pass':
        for card, num_times in Counter(cards).items():
            length = 2 if card in 'BR' else 4
            index = CARD_POSITION[card]
            array[index:index + length] = _number2onehot(num_times, length)

    return array


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
