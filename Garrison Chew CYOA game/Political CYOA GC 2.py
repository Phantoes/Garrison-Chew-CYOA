import random  # For random stats and success rolls
import time    # For text animation delays
import os      # For clearing terminal screen
import json    # For loading scenario data

# Initial questions
mark = input("What mark will this game get? (Legally binding, give integer) ")
if int(mark) < 80:
    print("Guess you can't play the game.")
else: 
    print("Alright, let's play the game.")
    # Math challenge
    mathx = input("But first, you need to solve a math problem. Please give me all real roots of the polynomial, x^4 - 5x^2 + 4 = 0 (you should answer with your roots seperated by commas in ascending order, for example, 1, 2, 3 ..) ")
    if mathx != "-2, -1, 1, 2": # Check for correct answers
        print("You should finish studying math before you start playing games...")
    else: 
        print("Alright, you must've finished your study. Have fun playing.")
        
        class GameState:
            def __init__(self):
                self.current_scenario = 1  # Tracks current scenario ID
                self.choices = []  # Stores all player decisions
                # Dual-axis reputation system
                self.reputation = {
                    'corruption': 0,  # Tracks unethical choices
                    'integrity': 0    # Tracks ethical choices
                }
                # Randomized character stats
                self.stats = {
                    'charisma': random.randint(1, 6),  # Affects persuasion
                    'judgment': random.randint(1, 6)   # Affects decision quality
                }
                self.ending = None  # Will store ending achieved
                self.choice_history = []  # Stores complete choice history

            def record_choice(self, choice_key, choice_data, outcome, scenario_id, scenario_title):
                """Records complete choice details for history"""
                self.choice_history.append({
                    'scenario_id': scenario_id,
                    'scenario_title': scenario_title,
                    'choice_key': choice_key,
                    'choice_text': next((text for text, data in scenarios[str(scenario_id)]['choices'].items() 
                                       if data == choice_data), "Unknown Choice"),
                    'outcome': outcome,
                    'stats': self.stats.copy(),
                    'reputation': self.reputation.copy()
                })

        # Displays text with typewriter effect
        def display_text_letter_by_letter(text, delay=0.01):
            for char in text:
                print(char, end='', flush=True)
                time.sleep(delay)
            print()

        # Clears terminal screen cross-platform
        def clear_screen():
            os.system('cls' if os.name == 'nt' else 'clear')

        def show_choice_history(game_state):
            """Displays complete choice history with context"""
            clear_screen()
            display_text_letter_by_letter("=== YOUR DECISION HISTORY ===")
            display_text_letter_by_letter("Review your political journey:\n")
            
            for i, entry in enumerate(game_state.choice_history, 1):
                display_text_letter_by_letter(f"{i}. {entry['scenario_title']}")
                display_text_letter_by_letter(f"   Choice: {entry['choice_text']}")
                display_text_letter_by_letter(f"   Outcome: {entry['outcome'].upper()}")
                display_text_letter_by_letter(f"   Stats at time: Charisma={entry['stats']['charisma']}, Judgment={entry['stats']['judgment']}")
                display_text_letter_by_letter(f"   Reputation: Integrity={entry['reputation']['integrity']}, Corruption={entry['reputation']['corruption']}")
                display_text_letter_by_letter("-" * 50)
            
            input("\nPress Enter to return to main menu...")

        # Loads and validates scenario JSON
        def load_scenarios(filename):
            try:
                with open(filename, 'r') as file:
                    data = file.read()
                    if not data.strip():
                        raise ValueError(f"The file '{filename}' is empty.")
                    return json.loads(data)
            except FileNotFoundError:
                raise FileNotFoundError(f"The file '{filename}' was not found.")
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in '{filename}': {e}")
            except Exception as e:
                raise ValueError(f"An error occurred while loading '{filename}': {e}")

        # Shows current scenario and player status
        def display_scenario(scenario, game_state):
            clear_screen()
            display_text_letter_by_letter(scenario['scene'])
            
            # Display reputation scores
            display_text_letter_by_letter("\nYour Political Capital:")
            display_text_letter_by_letter(f"- Integrity: {game_state.reputation['integrity']}")
            display_text_letter_by_letter(f"- Corruption: {game_state.reputation['corruption']}")
            # Display character stats
            display_text_letter_by_letter(f"\nYour Stats - Charisma: {game_state.stats['charisma']}, Judgment: {game_state.stats['judgment']}")

        # Calculates success probability for choices
        def calculate_success_chance(game_state, choice_data):
            base_chance = 60  # Base success rate
            
            # Apply reputation modifiers
            if 'integrity' in choice_data:
                base_chance += game_state.reputation['integrity'] * 2
            if 'corruption' in choice_data:
                base_chance -= game_state.reputation['corruption'] * 1.5
            
            # Apply stat bonuses if present
            if 'charisma_effect' in choice_data:
                base_chance += game_state.stats['charisma'] * choice_data['charisma_effect']
            if 'judgment_effect' in choice_data:
                base_chance += game_state.stats['judgment'] * choice_data['judgment_effect']
            
            # Keep within 20-90% bounds
            return max(20, min(90, base_chance))

        # Sets up new game session
        def initialize_game():
            player_name = input("Enter your character's name: ")
            game_state = GameState()
            # Show starting stats
            print(f"\nWelcome, {player_name}! Your natural abilities:")
            print(f"- Charisma: {game_state.stats['charisma']}")
            print(f"- Judgment: {game_state.stats['judgment']}")
            # Explain reputation system
            print("\nYour choices will build either:")
            print("- Corruption: Through shady deals and compromises")
            print("- Integrity: Through moral stands and honesty")
            input("\nPress Enter to begin your political journey...")
            return player_name, game_state

        # Main game processing loop
        def main():
            player_name, game_state = initialize_game()
            global scenarios  # Make scenarios global for choice history
            current_folder = os.path.dirname(os.path.abspath(__file__))
            filePath = os.path.join(current_folder, 'scenarios.json')
            scenarios = load_scenarios(filePath)

            while not game_state.ending:
                scenario = scenarios[str(game_state.current_scenario)]
                display_scenario(scenario, game_state)
                if 'choices' in scenario:
                    choices = list(scenario['choices'].items())
                    
                    # Display available options
                    print("\nOptions:")
                    for i, (choice_text, _) in enumerate(choices, 1):
                        print(f"{i}. {choice_text}")

                    try:
                        # Process player choice
                        choice_idx = int(input("Your choice: ")) - 1
                        choice_key, choice_data = choices[choice_idx]
                        
                        # Update reputation based on choice
                        if 'integrity' in choice_data:
                            game_state.reputation['integrity'] += choice_data['integrity']
                        if 'corruption' in choice_data:
                            game_state.reputation['corruption'] += choice_data['corruption']
                        
                        # Determine outcome
                        success_chance = calculate_success_chance(game_state, choice_data)
                        success = random.randint(1, 100) <= success_chance
                        outcome = "success" if success else "failure"
                        
                        # Record choice in history with scenario title
                        scenario_title = scenario.get('title', f"Scenario {game_state.current_scenario}")
                        game_state.record_choice(choice_key, choice_data, outcome, game_state.current_scenario, scenario_title)
                        
                        # Handle success/failure paths
                        if success:
                            next_scene = choice_data['next_scene']
                            display_text_letter_by_letter("\nSuccess! Your choice was effective.")
                        else:
                            # Apply failure consequences
                            game_state.reputation['corruption'] += 1
                            game_state.reputation['integrity'] = max(0, game_state.reputation['integrity'] - 1)
                            game_state.stats['charisma'] = max(1, game_state.stats['charisma'] - 1)
                            game_state.stats['judgment'] = max(1, game_state.stats['judgment'] - 1)
                            next_scene = choice_data['next_scene']  # Same as success path
                            display_text_letter_by_letter("\nYour choice has failed. Corruption increases, while integrity, charisma and judgment decrease.")
                        
                        # Record choice and advance
                        game_state.choices.append(choice_key)
                        game_state.current_scenario = next_scene

                        # Check for ending condition
                        if str(game_state.current_scenario).startswith('ending_'):
                            game_state.ending = str(game_state.current_scenario)
                            clear_screen()
                            display_text_letter_by_letter("=== FINAL OUTCOME ===")
                            display_text_letter_by_letter("\n" + scenarios[game_state.ending]['scene'])
                            # Show final reputation
                            display_text_letter_by_letter("\nYour Final Political Legacy:")
                            display_text_letter_by_letter(f"- Integrity: {game_state.reputation['integrity']}")
                            display_text_letter_by_letter(f"- Corruption: {game_state.reputation['corruption']}")
                            display_text_letter_by_letter("\nThis concludes your political journey.")
                            input("\nPress Enter to continue...")
                            break
                            
                    except (ValueError, IndexError):
                        print("Invalid choice. Please enter a valid number.")
                        time.sleep(1)
                        continue
                else:
                    # Handle scenarios without choices (some endings)
                    if str(game_state.current_scenario).startswith('ending_'):
                        game_state.ending = str(game_state.current_scenario)
                        clear_screen()
                        display_text_letter_by_letter("=== FINAL OUTCOME ===")
                        display_text_letter_by_letter("\n" + scenarios[game_state.ending]['scene'])
                        # Show final reputation
                        display_text_letter_by_letter("\nYour Final Political Legacy:")
                        display_text_letter_by_letter(f"- Integrity: {game_state.reputation['integrity']}")
                        display_text_letter_by_letter(f"- Corruption: {game_state.reputation['corruption']}")
                        display_text_letter_by_letter("\nThis concludes your political journey.")
                        input("\nPress Enter to continue...")
                    break
            
            # Replay option and history viewing
            while True:
                action = input("\nPlay again? (y/n/history): ").lower()
                if action == 'y':
                    main()
                    break
                elif action == 'history':
                    show_choice_history(game_state)
                else:
                    print("Thanks for playing!")
                    break

        # Entry loop
        if __name__ == "__main__":
            scenarios = None  # Global scenarios variable for history
            main() 