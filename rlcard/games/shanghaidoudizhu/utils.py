import json
from pathlib import Path
import re
from functools import lru_cache
from rlcard.utils import init_54_deck

CARDS = '3456789TJQKA2BR'

ROOT_PATH = Path(__file__).resolve().parent

# Action space
ACTIONS = open(ROOT_PATH / 'action_space.txt').read().split()
ACTION_2_ID = dict([(action, i) for i, action in enumerate(ACTIONS)])

# Action pattern
ACTION_PATTERNS = [re.compile(pattern) for pattern in open(ROOT_PATH / 'card_pattern.txt').read().split()]

# a map of card to its type. Also return both dict and list to accelerate
CARD_TYPE = json.load(open(ROOT_PATH / 'card_type.json'))

# a map of type to its cards
TYPE_CARD = json.load(open(ROOT_PATH / 'type_card.json'))


def init_108_deck():
    return init_54_deck() * 2


def sort_cards(cards):
    return sorted(cards, key=lambda c: CARDS.index(str(c)[0]))


def cards2str(cards):
    return ''.join([str(card)[0] for card in cards])


@lru_cache(512)
def get_playable_cards(cards: str, allow_bomb: bool, reported_cards: str):
    '''
    args:
        cards: SORTED cards string

    return:
        list of string of playable cards
    '''
    playable_cards = []
    if len(reported_cards) > 0:
        playable_cards.extend(reported_cards.split(','))
    reported_cards_set = set([c[0] for c in reported_cards.replace(',', '')])

    for i, p in enumerate(ACTION_PATTERNS):
        if p.pattern not in reported_cards and p.search(cards):
            playable_cards.append(ACTIONS[i])

    if not allow_bomb:
        playable_cards = list(filter(lambda x: CARD_TYPE[x]['type'] != 'bomb', playable_cards))

    return playable_cards


@lru_cache(512)
def get_gt_cards(current_cards: str, target_cards: str, allow_bomb: bool, reported_cards: str):
    '''
    args:
        current_cards: SORTED cards string
        target_cards: target cards
        allowed_bomb_number: allowed number of bombs

    return:
        list of string of playable cards
    '''

    target_type = CARD_TYPE[target_cards]

    if target_type['type'] == 'bomb' and not allow_bomb:
        return []

    gt_cards = []
    for cards in get_playable_cards(current_cards, allow_bomb, reported_cards):
        cards_type = CARD_TYPE[cards]
        if (cards_type['type'] == target_type['type'] and cards_type['rank'] > target_type['rank']) \
                or (target_type['type'] != 'bomb' and cards_type['type'] == 'bomb'):
            gt_cards.append(cards)

    return gt_cards


@ lru_cache(32)
def get_reported_cards(current_cards: str):
    '''
        得到7张以上炸弹的数量,用于判断地主是否能报到
    '''
    min_rank = CARD_TYPE['3' * 7]['rank']
    playable_cards = get_playable_cards(current_cards, allow_bomb=True, reported_cards='')
    reported_cards = []
    for cards in playable_cards:
        if CARD_TYPE[cards]['type'] == 'bomb' and CARD_TYPE[cards]['rank'] >= min_rank:
            reported_cards.append(cards)
    return reported_cards
