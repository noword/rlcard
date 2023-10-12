import sys
import json
from collections import OrderedDict

# rule: https://www.17dp.com/down/gamelist/id/201

if sys.version_info < (3, 6):
    raise Exception('The minimum supported Python version is 3.6')


CHAIN_CARDS = 'A23456789TJQKA'
NORMAL_CARDS = '3456789TJQKA2'

SOLO = list('3456789TJQKA2BR')
PAIR = [c * 2 for c in SOLO]
TRIO = [c * 3 for c in '3456789TJQKA2']


def sort_cards(s):
    s = ''.join(s)
    return ''.join(sorted(s, key=lambda x: SOLO.index(x)))


def gen_chain(number, length):
    assert 1 <= number <= 3
    length_valid = {1: (5, 14), 2: (2, 14), 3: (2, 12)}
    assert length_valid[number][0] <= length_valid[number][1]

    cards = [c * number for c in CHAIN_CARDS]
    res = []
    for i in range(len(cards) - length + 1):
        res.append(sort_cards(cards[i:i + length]))
    return res


def gen_trio_pair(card):
    card *= 3
    res = []
    for p in PAIR:
        if p[0] != card[0]:
            res.append(sort_cards(card + p))
    return res


def gen_bomb(card, number):
    assert 4 <= number <= 8
    return card * number


def gen_patterns(s):
    res = ''
    last = s[0]
    for c in s:
        if c != last:
            res += '.*'
        res += c
        last = c
    return res


SOLO_CHAIN = OrderedDict()
for i in range(5, 15):
    SOLO_CHAIN[i] = gen_chain(1, i)

PAIR_CHAIN = OrderedDict()
for i in range(3, 15):
    PAIR_CHAIN[i] = gen_chain(2, i)

TRIO_CHAIN = OrderedDict()
for i in range(2, 12):
    TRIO_CHAIN[i] = gen_chain(3, i)

TRIO_PAIR = []
for c in NORMAL_CARDS:
    TRIO_PAIR.append(gen_trio_pair(c))

_PARI_CHAIN = OrderedDict()
for i in range(2, 15):
    _PARI_CHAIN[i] = gen_chain(2, i)


def gen_trio_pair_chain(length):
    trio_chain = TRIO_CHAIN[length]
    pair_chain = _PARI_CHAIN[length]
    res = []
    for t in trio_chain:
        tp = []
        for p in pair_chain:
            if len(set(t) & set(p)) == 0:
                tp.append(sort_cards(t + p))
        if len(tp) > 0:
            res.append(tp)
    return res


TRIO_PAIR_CHAIN = OrderedDict()
for i in range(2, 7):
    TRIO_PAIR_CHAIN[i] = gen_trio_pair_chain(i)

BOMB = []
for i in range(4, 9):
    for c in NORMAL_CARDS:
        BOMB.append(gen_bomb(c, i))
BOMB.append('BBRR')

TYPE_CARD = OrderedDict()
TYPE_CARD['solo'] = dict((i, [card]) for i, card in enumerate(SOLO))
TYPE_CARD['pair'] = dict((i, [card]) for i, card in enumerate(PAIR))
TYPE_CARD['trio'] = dict((i, [card]) for i, card in enumerate(TRIO))
for i, chain in SOLO_CHAIN.items():
    TYPE_CARD[f'solo_chain_{i}'] = dict((i, [card]) for i, card in enumerate(chain))
for i, chain in PAIR_CHAIN.items():
    TYPE_CARD[f'pair_chain_{i}'] = dict((i, [card]) for i, card in enumerate(chain))
for i, chain in TRIO_CHAIN.items():
    TYPE_CARD[f'trio_chain_{i}'] = dict((i, [card]) for i, card in enumerate(chain))
for i, chain in TRIO_PAIR_CHAIN.items():
    TYPE_CARD[f'trio_pair_chain_{i}'] = dict((i, card) for i, card in enumerate(chain))
TYPE_CARD['bomb'] = dict((i, [card]) for i, card in enumerate(BOMB))

json.dump(TYPE_CARD, open('type_card.json', 'w'), indent=4)


CARD_TYPE = OrderedDict()
ACTIONS = []
CARD_PATTERNS = []
for name, rank_pair in TYPE_CARD.items():
    for rank, cards in rank_pair.items():
        for c in cards:
            CARD_TYPE[c] = {'type': name, 'rank': rank}
            ACTIONS.append(c)
            CARD_PATTERNS.append(gen_patterns(c))


json.dump(CARD_TYPE, open('card_type.json', 'w'), indent=4)

ACTIONS.extend(['pass', 'bid_0', 'bid_1', 'bid_2', 'bid_3', 'report_0', 'report_1'])  # 过牌, 不叫, 1档, 2档, 3档, 不报道, 报到
open('action_space.txt', 'w').write(' '.join(ACTIONS))
open('card_pattern.txt', 'w').write(' '.join(CARD_PATTERNS))
