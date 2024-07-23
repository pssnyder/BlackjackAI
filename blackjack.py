import random

# Define the card values and suits
card_values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']

# Create the deck of cards
deck = [(value, suit) for value in card_values for suit in suits]

# Initialize player's chips
player_chips = 1000

# Function to calculate the value of a hand
def calculate_hand_value(hand):
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
    return deck.pop()

# Function to display the hands
def display_hands(player_hand, dealer_hand, reveal_dealer=False):
    print("\nPlayer's hand:", player_hand, "Value:", calculate_hand_value(player_hand))
    if reveal_dealer:
        print("Dealer's hand:", dealer_hand, "Value:", calculate_hand_value(dealer_hand))
    else:
        print("Dealer's hand: [({}, {})]".format(dealer_hand[0][0], dealer_hand[0][1]), "[Hidden]")

# Function to place a bet
def place_bet():
    global player_chips
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

# Main game function
def play_blackjack():
    global player_chips
    
    # Shuffle the deck
    random.shuffle(deck)
    
    # Place a bet
    bet = place_bet()
    
    # Deal initial cards
    player_hand = [deal_card(deck), deal_card(deck)]
    dealer_hand = [deal_card(deck), deal_card(deck)]
    
    # Display initial hands
    display_hands(player_hand, dealer_hand)
    
    # Player's turn
    while calculate_hand_value(player_hand) < 21:
        choice = input("Do you want to 'hit' or 'stand'? ").lower()
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
        player_chips -= bet
        return
    
    # Dealer's turn
    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(deal_card(deck))
    
    # Display final hands
    display_hands(player_hand, dealer_hand, reveal_dealer=True)
    
    # Determine the winner
    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)
    
    if dealer_value > 21:
        print("Dealer busts! Player wins.")
        player_chips += bet
    elif player_value > dealer_value:
        print("Player wins!")
        player_chips += bet
    elif player_value < dealer_value:
        print("Dealer wins!")
        player_chips -= bet
    else:
        print("It's a tie!")

# Start the game
if __name__ == "__main__":
    while player_chips > 0:
        play_blackjack()
        if player_chips <= 0:
            print("You have run out of chips! Game over.")
            break
        continue_playing = input("Do you want to play another round? You have {player_chips} chips. (yes/no): ").lower()
        if continue_playing != 'yes':
            print(f"You leave the game with {player_chips} chips.")
            break