"""
Methods to serialize an euchre round data_model to/from Json as well and check if the json is valid.

Note: Should probably have been implemented with python pickle, but this supports players in other languages.
"""
import json
from euchre.data_model import Suite, Card, PlayerCards, Trick, Round


def game_to_json(f_round: Round) -> str:
    """
    Serializes a full round object to a json string, checking for correctness
    :param f_round:  Full round game state information
    :return:  Json String
    """

    game_dict = dict()
    game_dict['players'] = [{'index': player.index,
                             'order': player.order,
                             'hand': [card.value for card in player.hand],
                             'dropped_card': player.dropped_card.value if player.dropped_card is not None else None}
                            for player in f_round.players_cards]
    game_dict['deck'] = [card.value for card in f_round.kitty]
    game_dict['tricks'] = [] if f_round.tricks is None else \
        [{'start_index': r.start_index,
          'cards': [card.value for card in r.cards]}
         for r in f_round.tricks]
    game_dict['trump_caller'] = f_round.trump_caller
    game_dict['trump'] = f_round.trump
    return json.dumps(game_dict)


def json_to_game(json_string: str) -> Round:
    """
    Parses a Json string into a round object, checking for correctness

    :param json_string: Input string
    :return: Round object represented by the json string.
    """

    is_game_json_valid(json_string)  # Check for validity
    game_dict = json.loads(json_string)

    players_cards = [PlayerCards(p['index'], p['order'], [Card.with_value(c) for c in p['hand']], p['dropped_card'])
                     for p in game_dict['players']]
    deck = [Card.with_value(c) for c in game_dict['deck']]
    tricks = []
    if game_dict['tricks'] is not None:
        for r in game_dict['tricks']:
            if r['cards'] is not None:
                tricks.append(Trick(r['start_index'], [Card.with_value(c) for c in r['cards']]))
            else:
                tricks.append(Trick(r['start_index'], []))
    trump = Suite(game_dict['trump']) if game_dict['trump'] is not None else None
    return Round(players_cards, deck, tricks, game_dict['trump_caller'], trump)


def is_game_json_valid(json_str: str) -> None:
    """Checks for the minimum amount of information needed to construct a game object.  Ignores extra keys"""
    game_dict = json.loads(json_str)

    valid_keys = {'players', 'deck', 'tricks', 'trump_caller', 'trump'}
    if not set(game_dict.keys()).issuperset(valid_keys):
        raise ValueError("Json game dict missing a top level key: " + str(valid_keys))

    players = game_dict['players']
    if players is None or len(game_dict['players']) != 4:
        raise ValueError("Must have 4 players in the game dict")

    player_keys = {'index', 'order', 'hand', 'dropped_card'}
    for p in players:
        if not set(p.keys()).issuperset(player_keys):
            raise ValueError("player dict is missing a key")

    player_values = {0, 1, 2, 3}
    if set([p['order'] for p in players]) != player_values:
        raise ValueError("Must have 4 players with orders 0, 1, 2, 3")
    if set([p['index'] for p in players]) != player_values:
        raise ValueError("Must have 4 players with player values 0, 1, 2, 3")
    for p in players:
        if p['hand'] is None or len(p['hand']) != 5:
            raise ValueError("Player " + str(p['order']) + " must have 5 cards in hand")
        if p['order'] != 3 and p['dropped_card'] is not None:
            raise ValueError("Only the dealer can have a dropped card")

    if len(game_dict['deck']) != 4:
        raise ValueError("Deck must have 4 cards dealt!")

    trump_values = {0, 1, 2, 3, None}
    if not trump_values.issuperset({game_dict['trump_caller']}):
        raise ValueError("Invalid Trump caller value")
    trump = game_dict['trump']
    if not trump_values.issuperset({trump}):
        raise ValueError("Invalid Trump value")
    # check if suite matches when card is picked up or not

    card_values = {suite + face for face in range(6) for suite in [0, 8, 16, 24]}

    game_dict['trump_caller']
    cards_dealt = game_dict['deck']
    for p in game_dict['players']:
        cards_dealt.extend(p['hand'])
        if p['order'] == 3 and p['dropped_card'] is not None:
            if not set(p['hand'] + [p['dropped_card']]).issuperset(set([game_dict['deck'][0]])):
                raise ValueError("Dealer did not pick up the top card on the deck")
            cards_dealt.append(p['dropped_card'])

    if set(cards_dealt) != card_values:
        raise ValueError("Cards dealt are not values equal to a euchre deck")

    tricks = game_dict['tricks']
    trick_keys = {'start_index', 'cards'}
    trick_cards = []
    if len(tricks) > 0 and (game_dict['trump_caller'] is None or trump is None):
            raise ValueError('Trump and a trump caller must be set for there to be valid tricks of play')
    if len(tricks) > 5:
        raise ValueError("Can't have more than 5 tricks")
    for r_ind in range(len(tricks)):
        trick = tricks[r_ind]
        if set(trick.keys()) != trick_keys:
            raise ValueError("Round is missing a dictionary key")
        start_index = trick['start_index']
        if not {0, 1, 2, 3}.issuperset({start_index}):
            raise ValueError("Player start value is invalid")
        if r_ind == 0:
            left_dealer_index = next((p['index'] for p in players if p['order'] == 0), None)
            if start_index != left_dealer_index:  # will be different when "going" alone
                raise ValueError("Player to left of dealer must go first")
        else:
            pass  # Future check using vm if trick winner is correct
        cards = trick['cards']
        if cards is not None:
            if len(cards) > 4:
                raise ValueError("Only 4 cards can be played in a trick!")
            for c in cards:
                trick_cards.append(c)
                player_hand = next((p['hand'] for p in players if p['index'] == start_index), None)
                if not set(player_hand).issuperset({c}):
                    raise ValueError("Player " + str(start_index) + " played a card not in their hand")
                start_index = (start_index + 1) % 4

    if len(set(trick_cards)) != len(trick_cards):
        raise ValueError("A player played a card twice!")


