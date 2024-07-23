import random
import json
import psutil  # For monitoring system performance
import time
import sys

# Define the card values and suits
card_values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']

# Function to create a deck of cards
def create_deck(num_decks=1):
    """
    Creates a deck of cards with the specified number of decks.
    
    Parameters:
    num_decks (int): Number of decks to include in the deck.
    
    Returns:
    list: A list of tuples representing the deck of cards.
    """
    return [(value, suit) for value in card_values for suit in suits] * num_decks

# Function to calculate the value of a hand
def calculate_hand_value(hand):
    """
    Calculates the total value of a hand, considering the special case of Aces.
    
    Parameters:
    hand (list): A list of tuples representing the hand of cards.
    
    Returns:
    int: The total value of the hand.
    """
    value = 0
    ace_count = 0
    for card, suit in hand:
        if card in ['Jack', 'Queen', 'King']:
            value += 10
        elif card == 'Ace':
            ace_count += 1
            value += 11
        else:
            value += int(card)
    
    # Adjust for Aces if value is over 21
    while value > 21 and ace_count:
        value -= 10
        ace_count -= 1
    
    return value

# Function to deal a card
def deal_card(deck):
    """
    Deals a card from the deck.
    
    Parameters:
    deck (list): The deck of cards.
    
    Returns:
    tuple: A tuple representing the dealt card.
    """
    return deck.pop()

# Function to determine the action based on the strategy chart
def get_strategy_action(player_hand, dealer_upcard):
    """
    Determines the action to take based on the strategy chart.
    
    Parameters:
    player_hand (list): The player's hand.
    dealer_upcard (tuple): The dealer's upcard.
    
    Returns:
    str: The action to take ('H', 'S', 'D', 'Y', 'SUR').
    """
    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value([dealer_upcard])
    
    # Determine if the player has a pair
    if len(player_hand) == 2 and player_hand[0][0] == player_hand[1][0]:
        pair = player_hand[0][0]
        if pair == 'Ace':
            return 'Y'
        elif pair == '10':
            return 'N'
        elif pair == '9':
            return 'Y' if dealer_value in [2, 3, 4, 5, 6, 8, 9] else 'N'
        elif pair == '8':
            return 'Y'
        elif pair == '7':
            return 'Y' if dealer_value in [2, 3, 4, 5, 6, 7] else 'H'
        elif pair == '6':
            return 'Y' if dealer_value in [2, 3, 4, 5, 6] else 'H'
        elif pair == '5':
            return 'D' if dealer_value in [2, 3, 4, 5, 6, 7, 8, 9] else 'H'
        elif pair == '4':
            return 'Y' if dealer_value in [5, 6] else 'H'
        elif pair == '3' or pair == '2':
            return 'Y' if dealer_value in [2, 3, 4, 5, 6, 7] else 'H'
    
    # Determine if the player has a soft total
    if any(card == 'Ace' for card, suit in player_hand):
        if player_value == 20:
            return 'S'
        elif player_value == 19:
            return 'D' if dealer_value == 6 else 'S'
        elif player_value == 18:
            if dealer_value in [2, 3, 4, 5, 6]:
                return 'D'
            elif dealer_value in [9, 10, 11]:
                return 'H'
            else:
                return 'S'
        elif player_value == 17:
            return 'D' if dealer_value in [3, 4, 5, 6] else 'H'
        elif player_value == 16 or player_value == 15:
            return 'D' if dealer_value in [4, 5, 6] else 'H'
        elif player_value == 14 or player_value == 13:
            return 'D' if dealer_value in [5, 6] else 'H'
    
    # Determine action for hard totals
    if player_value >= 17:
        return 'S'
    elif player_value >= 13:
        return 'S' if dealer_value in [2, 3, 4, 5, 6] else 'H'
    elif player_value == 12:
        return 'S' if dealer_value in [4, 5, 6] else 'H'
    elif player_value == 11:
        return 'D'
    elif player_value == 10:
        return 'D' if dealer_value in [2, 3, 4, 5, 6, 7, 8, 9] else 'H'
    elif player_value == 9:
        return 'D' if dealer_value in [3, 4, 5, 6] else 'H'
    else:
        return 'H'

# Function to simulate a single game of Blackjack
def simulate_game(deck, player_chips, bet):
    """
    Simulates a single game of Blackjack and logs the decisions.
    
    Parameters:
    deck (list): The deck of cards.
    player_chips (int): The player's chips.
    bet (int): The bet amount.
    
    Returns:
    tuple: Updated player chips, game log, and result ('win', 'loss', 'tie').
    """
    game_log = []
    
    # Deal initial cards
    player_hand = [deal_card(deck), deal_card(deck)]
    dealer_hand = [deal_card(deck), deal_card(deck)]
    
    # Log initial hands
    game_log.append({
        'player_hand': player_hand,
        'dealer_hand': dealer_hand,
        'action': 'initial_deal'
    })
    
    # Player's turn
    while calculate_hand_value(player_hand) < 21:
        action = get_strategy_action(player_hand, dealer_hand[0])
        game_log.append({
            'player_hand': player_hand.copy(),
            'dealer_hand': dealer_hand.copy(),
            'action': action
        })
        
        if action == 'H':
            player_hand.append(deal_card(deck))
        elif action == 'S':
            break
        elif action == 'D':
            if player_chips >= bet * 2:
                player_chips -= bet
                bet *= 2
                player_hand.append(deal_card(deck))
                break
            else:
                player_hand.append(deal_card(deck))
        elif action == 'Y':
            break
        elif action == 'SUR':
            break
    
    # Check if player busts
    if calculate_hand_value(player_hand) > 21:
        player_chips -= bet
        game_log.append({
            'player_hand': player_hand,
            'dealer_hand': dealer_hand,
            'action': 'bust'
        })
        return player_chips, game_log, 'loss'
    
    # Dealer's turn
    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(deal_card(deck))
    
    # Log final hands
    game_log.append({
        'player_hand': player_hand,
        'dealer_hand': dealer_hand,
        'action': 'final_hands'
    })
    
    # Determine the winner
    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)
    
    if dealer_value > 21:
        player_chips += bet
        game_log.append({
            'player_hand': player_hand,
            'dealer_hand': dealer_hand,
            'action': 'dealer_bust'
        })
        return player_chips, game_log, 'win'
    elif player_value > dealer_value:
        player_chips += bet
        game_log.append({
            'player_hand': player_hand,
            'dealer_hand': dealer_hand,
            'action': 'win'
        })
        return player_chips, game_log, 'win'
    elif player_value < dealer_value:
        player_chips -= bet
        game_log.append({
            'player_hand': player_hand,
            'dealer_hand': dealer_hand,
            'action': 'loss'
        })
        return player_chips, game_log, 'loss'
    else:
        game_log.append({
            'player_hand': player_hand,
            'dealer_hand': dealer_hand,
            'action': 'tie'
        })
        return player_chips, game_log, 'tie'

# Function to simulate multiple games and log results
def simulate_games(num_games, num_decks):
    """
    Simulates multiple games of Blackjack and logs the results.
    
    Parameters:
    num_games (int): Number of games to simulate.
    num_decks (int): Number of decks to use in the simulation.
    
    Returns:
    tuple: Results and logs of the simulations.
    """
    initial_chips = 1000
    results = []
    logs = []
    
    for i in range(num_games):
        deck = create_deck(num_decks)
        random.shuffle(deck)
        player_chips = initial_chips
        bet = 10
        
        player_chips, game_log, result = simulate_game(deck, player_chips, bet)
        results.append(result)
        logs.append(game_log)
        
        # Update progress bar and monitor performance
        if (i + 1) % 100 == 0 or i == num_games - 1:
            progress = (i + 1) / num_games * 100
            print(f"Progress: {progress:.2f}% ({i + 1}/{num_games} games)")
            monitor_performance()
    
    return results, logs

# Function to monitor system performance
def monitor_performance():
    """
    Monitors and prints the system's CPU load, memory usage, and GPU load.
    """
    cpu_load = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    print(f"CPU Load: {cpu_load}% | Memory Usage: {memory_usage}%")

# Main function to run the simulation
if __name__ == "__main__":
    num_games = 500
    num_decks_list = [1, 2, 4, 6, 8]
    
    for num_decks in num_decks_list:
        print(f"Simulating {num_games} games with {num_decks} deck(s)...")
        results, logs = simulate_games(num_games, num_decks)
        
        # Save results and logs to JSON files
        with open(f'simulation_results_{num_decks}_decks.json', 'w') as f:
            json.dump(results, f)
        
        with open(f'simulation_logs_{num_decks}_decks.json', 'w') as f:
            json.dump(logs, f)
        
        print(f"Simulation with {num_decks} deck(s) completed.")