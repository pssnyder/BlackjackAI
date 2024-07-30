import os
import random
import logging
import csv
import json
import datetime

# Configuration Section
PLAY_TYPE = 1  # 0 for player control, 1 for AI control
NUM_GAMES = 1000  # Set the number of games to simulate
STRATEGIES = [0]  # An array of numbers representing the strategies to simulate this run
LOG_FILE = './logs/blackjack_game_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.log'
CSV_RESULTS_FILE = './results/blackjack_ai_results_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.csv'
JSON_RESULTS_FILE = './results/blackjack_ai_results_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.json'

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the card values and suits
card_values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']

# Create the deck of cards
deck = [(value, suit) for value in card_values for suit in suits]

# Function to calculate the value of a hand
def calculate_hand_value(hand):
    value = 0
    ace_count = 0
    for card, _ in hand:
        if card in ['Jack', 'Queen', 'King']:
            value += 10
        elif card == 'Ace':
            ace_count += 1
            value += 11
        else:
            value += int(card)
    while value > 21 and ace_count:
        value -= 10
        ace_count -= 1
    return value

# Function to deal a card
def deal_card(deck):
    return deck.pop()

# Function to display the hands
def display_hands(player_hand, dealer_hand, reveal_dealer=False):
    print("\nPlayer's hand:", player_hand, "Value:", calculate_hand_value(player_hand))
    if reveal_dealer:
        print("Dealer's hand:", dealer_hand, "Value:", calculate_hand_value(dealer_hand))
    else:
        print("Dealer's hand: [({}, {})]".format(dealer_hand[0][0], dealer_hand[0][1]), "[Hidden]")

# Function to place a bet
def place_bet(player_chips):
    while True:
        try:
            bet = int(input(f"You have {player_chips} chips. Place your bet: "))
            if bet > player_chips:
                print("You cannot bet more than you have.")
            elif bet <= 0:
                print("Bet must be greater than 0.")
            else:
                return bet
        except ValueError:
            print("Invalid input. Please enter a number.")

# Function to simulate a game of blackjack
def play_blackjack(player_chips, strategy):
    global deck
    random.shuffle(deck)
    bet = place_bet(player_chips) if PLAY_TYPE == 0 else 10  # Default bet for AI
    player_hand = [deal_card(deck), deal_card(deck)]
    dealer_hand = [deal_card(deck), deal_card(deck)]
    display_hands(player_hand, dealer_hand)
    
    # Player's turn
    while calculate_hand_value(player_hand) < 21:
        if PLAY_TYPE == 0:
            choice = input("Do you want to 'hit' or 'stand'? ").lower()
        else:
            choice = ai_strategy(player_hand, dealer_hand, strategy)
        if choice == 'hit':
            player_hand.append(deal_card(deck))
            display_hands(player_hand, dealer_hand)
        elif choice == 'stand':
            break
        else:
            print("Invalid choice. Please choose 'hit' or 'stand'.")
    
    # Check if player busts
    if calculate_hand_value(player_hand) > 21:
        print("Player busts! Dealer wins.")
        return player_chips - bet, 'loss'
    
    # Dealer's turn
    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(deal_card(deck))
    
    display_hands(player_hand, dealer_hand, reveal_dealer=True)
    
    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)
    
    if dealer_value > 21:
        print("Dealer busts! Player wins.")
        return player_chips + bet, 'win'
    elif player_value > dealer_value:
        print("Player wins!")
        return player_chips + bet, 'win'
    elif player_value < dealer_value:
        print("Dealer wins!")
        return player_chips - bet, 'loss'
    else:
        print("It's a tie!")
        return player_chips, 'tie'

# AI strategy function
def ai_strategy(player_hand, dealer_hand, strategy):
    # Implement different strategies based on the strategy parameter
    if strategy == 0:
        if calculate_hand_value(player_hand) < 17:
            return 'hit'
        else:
            return 'stand'
    # Add more strategies as needed
    return 'stand'

# Function to simulate multiple games
def simulate_games(num_games, strategies):
    results = []
    for strategy in strategies:
        player_chips = 1000
        for i in range(num_games):
            logging.debug(f"Starting game {i+1} with strategy {strategy}")
            player_chips, result = play_blackjack(player_chips, strategy)
            results.append({
                'game_number': i + 1,
                'strategy': strategy,
                'result': result,
                'player_chips': player_chips
            })
            logging.debug(f"Game {i+1} ended with {player_chips} chips")
    return results

# Function to save results to CSV
def save_results_to_csv(results):
    if not os.path.exists(CSV_RESULTS_FILE):
        with open(CSV_RESULTS_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Strategy', 'Game Number', 'Result', 'Player Chips'])
    with open(CSV_RESULTS_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        for result in results:
            writer.writerow([result['strategy'], result['game_number'], result['result'], result['player_chips']])
    logging.debug(f'Results appended to {CSV_RESULTS_FILE}')

# Function to save results to JSON
def save_results_to_json(results):
    if os.path.exists(JSON_RESULTS_FILE):
        with open(JSON_RESULTS_FILE, 'r') as file:
            existing_data = json.load(file)
    else:
        existing_data = []
    existing_data.extend(results)
    with open(JSON_RESULTS_FILE, 'w') as file:
        json.dump(existing_data, file, indent=4)
    logging.debug(f'Results saved to {JSON_RESULTS_FILE}')

if __name__ == '__main__':
    logging.debug(f"#### Beginning {len(STRATEGIES)} Strategy Testing ####")
    print("#### Beginning", len(STRATEGIES), "Strategy Tests ####")
    for strategy in STRATEGIES:
        logging.debug(f"## ## Simulation beginning for {NUM_GAMES} games using strategy #{strategy} ## ##")
        results = simulate_games(NUM_GAMES, [strategy])
        save_results_to_csv(results)
        save_results_to_json(results)
        avg_chips = sum(result['player_chips'] for result in results) / NUM_GAMES
        win_rate = sum(1 for result in results if result['result'] == 'win') / NUM_GAMES * 100
        logging.debug(f"## ## Simulation ended for {NUM_GAMES} games using strategy #{strategy} ## ##")
        print(f"Strategy Deployed: {strategy}, Games Simulated: {NUM_GAMES}, Average Chips: {round(avg_chips, 2)}, Win Rate: {round(win_rate, 2)}%")
    print("#### All Simulations Have Ended ####")
    logging.debug(f"#### #### All Simulations Have Ended #### ####")