import json

# Function to load simulation results
def load_results(num_decks):
    """
    Loads simulation results from a JSON file.
    
    Parameters:
    num_decks (int): Number of decks used in the simulation.
    
    Returns:
    list: List of results from the simulation.
    """
    with open(f'simulation_results_{num_decks}_decks.json', 'r') as f:
        results = json.load(f)
    return results

# Function to analyze results
def analyze_results(num_games, num_decks_list):
    """
    Analyzes the simulation results to calculate win, loss, and tie rates.
    
    Parameters:
    num_games (int): Number of games simulated.
    num_decks_list (list): List of deck configurations used in the simulation.
    
    Returns:
    dict: Analysis of the simulation results.
    """
    analysis = {}
    
    for num_decks in num_decks_list:
        results = load_results(num_decks)
        wins = results.count('win')
        losses = results.count('loss')
        ties = results.count('tie')
        
        win_rate = wins / num_games
        loss_rate = losses / num_games
        tie_rate = ties / num_games
        
        analysis[num_decks] = {
            'wins': wins,
            'losses': losses,
            'ties': ties,
            'win_rate': win_rate,
            'loss_rate': loss_rate,
            'tie_rate': tie_rate
        }
    
    return analysis

# Main function to run the analysis
if __name__ == "__main__":
    num_games = 10000
    num_decks_list = [1, 2, 4, 6, 8]
    
    analysis = analyze_results(num_games, num_decks_list)
    
    # Save analysis results to JSON file
    with open('analysis_results.json', 'w') as f:
        json.dump(analysis, f, indent=4)
    
    # Print analysis results
    for num_decks, stats in analysis.items():
        print(f"Decks: {num_decks}")
        print(f"  Wins: {stats['wins']} ({stats['win_rate']*100:.2f}%)")
        print(f"  Losses: {stats['losses']} ({stats['loss_rate']*100:.2f}%)")
        print(f"  Ties: {stats['ties']} ({stats['tie_rate']*100:.2f}%)")