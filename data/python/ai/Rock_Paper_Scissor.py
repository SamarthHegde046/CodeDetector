import random

def play_game():
    choices = ["rock", "paper", "scissor"]
    
    print("\n🎮 Welcome to Rock, Paper, Scissors!")
    print("👉 Type 'rock', 'paper', or 'scissor'")
    print("👉 Type 'exit' to quit the game\n")
    
    while True:
        user = input("You: ").lower().strip()
        
        if user == 'exit':
            print("\n👋 Thanks for playing! Goodbye.")
            break
        
        if user not in choices:
            print("⚠️ Invalid choice! Try again.\n")
            continue
        
        computer = random.choice(choices)
        print(f"Computer: {computer}")
        
        if user == computer:
            print("🤝 It's a tie!\n")
        elif (
            (user == 'rock' and computer == 'scissor') or
            (user == 'scissor' and computer == 'paper') or
            (user == 'paper' and computer == 'rock')
        ):
            print("🎉 You win!\n")
        else:
            print("😢 You lose!\n")

# Run the game
play_game()
