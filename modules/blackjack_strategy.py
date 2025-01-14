def calculate_optimal_action(player_hand, dealer_card, card_count):
    """
    Calculate the optimal action for the player based on their hand, the dealer's visible card, and the card count.
    :param player_hand: List of player card ranks (e.g., ['Ace', '7']).
    :param dealer_card: Rank of the dealer's visible card (e.g., '10').
    :param card_count: Current card count (Hi-Lo system).
    :return: String (Optimal action: 'Hit', 'Stand', 'Split', 'Double', or 'Surrender').
    """

    def hand_value(hand):
        """
        Calculate the total value of a Blackjack hand.
        Aces can count as 1 or 11.
        """
        value = 0
        aces = 0

        for card in hand:
            if card in ['J', 'Q', 'K']:
                value += 10
            elif card == 'A':
                aces += 1
                value += 11
            else:
                value += int(card)

        # Adjust for aces
        while value > 21 and aces:
            value -= 10
            aces -= 1

        return value

    player_total = hand_value(player_hand)
    dealer_value = 10 if dealer_card in ['Jack', 'Queen', 'King'] else (11 if dealer_card == 'Ace' else int(dealer_card))

    # Adjust for positive or negative card count
    aggressive_threshold = 1 if card_count > 0 else -1

    # Basic Strategy
    if player_total >= 17:
        return "Stand"
    elif 13 <= player_total <= 16:
        if dealer_value >= 7:  # Strong dealer card
            return "Hit" if card_count <= aggressive_threshold else "Stand"
        else:
            return "Stand"
    elif player_total == 12:
        if 4 <= dealer_value <= 6:  # Weak dealer card
            return "Stand"
        else:
            return "Hit"
    elif 9 <= player_total <= 11:
        return "Double" if player_total + card_count <= 21 else "Hit"
    elif player_total <= 8:
        return "Hit"
    elif len(player_hand) == 2 and player_hand[0] == player_hand[1]:  # Pairs
        if player_hand[0] in ['8', 'Ace']:
            return "Split"
        elif player_hand[0] in ['2', '3', '7'] and dealer_value <= 7:
            return "Split"
        elif player_hand[0] == '6' and dealer_value <= 6:
            return "Split"
        elif player_hand[0] == '9' and dealer_value not in [7, 10, 'Ace']:
            return "Split"
        else:
            return "Stand"
    else:
        return "Hit"
