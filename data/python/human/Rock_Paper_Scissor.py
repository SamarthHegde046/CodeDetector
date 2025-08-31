import random

def play_game():
    choices=["rock","paper","scissor"]
    print("Welcome to Rock Paper Scissor !")
    print("Type 'rock','paper','scissor', Type 'exit' to quit")
    
    while True:
        user=input("You : ").lower()
        if user=='exit':
            print("Thanks for playing.")
            break
        if user not in choices:
            print("Invalid choice, try again.")
            continue
        
        computer=random.choice(choices)
        print(f"Computer : {computer}")
        
        if user==computer:
            print("Its a tie!")
        elif (user=='rock' and computer=='scissor') or (user=='scissor' and computer=='paper') or (user=='paper' and computer=='rock'):
            print("You win!")
        else:
            print("You lose!")
play_game()