import random
import json
import time
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from tqdm import tqdm

num_games = 1000 # Number of games to simulate per decks in the shoe
num_decks_list = [1, 2, 6, 7, 8] # Number of decks per shoe (Default: 1, 2, 6, 7, 8)
num_threads = 1 # Default: =1 threading disabled, >1 threading enabled

# Define the card values and suits
card_values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']

# Function to create a deck of cards
def create_deck(num_decks):
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
    
    # Deal initial cards
    player_hand = [deal_card(deck), deal_card(deck)]
    dealer_hand = [deal_card(deck), deal_card(deck)]
    while calculate_hand_value(player_hand) < 21:
        action = get_strategy_action(player_hand, dealer_hand[0])
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
        elif action == 'Y':
            break
        elif action == 'SUR':
            break
    
    # Check if player busts
    if calculate_hand_value(player_hand) > 21:
        player_chips -= bet
        return player_chips, 'loss'
    
    # Dealer's turn
    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(deal_card(deck))
    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)
    
    if dealer_value > 21:
        player_chips += bet
        logging.info({'player_hand': player_hand, 'dealer_hand': dealer_hand, 'action': 'dealer_bust'})
        return player_chips, 'win'
    elif player_value > dealer_value:
        player_chips += bet
        logging.info({'player_hand': player_hand, 'dealer_hand': dealer_hand, 'action': 'win'})
        return player_chips, 'win'
    elif player_value < dealer_value:
        player_chips -= bet
        logging.info({'player_hand': player_hand, 'dealer_hand': dealer_hand, 'action': 'loss'})
        return player_chips, 'loss'
    else:
        logging.info({'player_hand': player_hand, 'dealer_hand': dealer_hand, 'action': 'tie'})
        return player_chips, 'tie'

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
    
    # Wrap the range with tqdm for progress bar
    for i in tqdm(range(num_games), desc="Simulating games"):
        deck = create_deck(num_decks)
        random.shuffle(deck)
        player_chips = initial_chips
        bet = 10
        player_chips, result = simulate_game(deck, player_chips, bet)
        results.append(result)
    
    return results, logs

def simulate_games_worker(num_games, num_decks, results, logs, thread_id):
    try:
        initial_chips = 1000
        local_results = []
        
        # Wrap the range with tqdm for progress bar
        for i in tqdm(range(num_games), desc=f"Thread {thread_id}"):
            deck = create_deck(num_decks)
            random.shuffle(deck)
            player_chips = initial_chips
            bet = 10
            player_chips, result = simulate_game(deck, player_chips, bet)
            local_results.append(result)
        
        results.extend(local_results)
    except Exception as e:
        logging.error(f"Thread {thread_id} encountered an error: {e}")
    
def append_to_json_file(file_path, data):
    """
    Function to append results to a JSON file

    Args:
        file_path (string): path to json file
        data (list): Shared list to store logs or results
    """
    try:
        with open(file_path, 'r') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = []
    existing_data.extend(data)
    with open(file_path, 'w') as f:
        json.dump(existing_data, f, indent=4)

# Main function to run the simulation
if __name__ == "__main__":
    for num_decks in num_decks_list:
        if num_threads > 1:
            print(f"Simulating {num_games} games with {num_decks} deck(s) using {num_threads} threads...")
            logging.info(f"Simulating {num_games} games with {num_decks} deck(s) using {num_threads} threads...")
        
            # Shared lists to store results and logs
            results = []
            
            # Calculate the number of games each thread should simulate
            games_per_thread = num_games // num_threads
            
            # Use ThreadPoolExecutor to manage threads
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []
                for thread_id in range(num_threads):
                    futures.append(executor.submit(simulate_games_worker, games_per_thread, num_decks, results, logs, thread_id))
                
                # Wait for all threads to complete
                for future in as_completed(futures):
                    try:
                        future.result()  # This will raise any exceptions caught in the worker
                    except Exception as e:
                        logging.error(f"Error in thread: {e}")
        else:
            print(f"Simulating {num_games} games with {num_decks} deck(s)...")
            results = simulate_games(num_games, num_decks)
        append_to_json_file(f'./results/simulation_results_{num_decks}_decks.json', results)
        print(f"Simulation with {num_decks} deck(s) completed.")
        logging.info(f"Simulation with {num_decks} deck(s) completed.")