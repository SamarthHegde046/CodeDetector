import random
user_choice=int(input("1.Rock\n2.Scissor\n3.Paper\nEnter your choice:"))
print("Your choice is",user_choice)
com_choice=random.randint(1,3)
print("computer choice is",com_choice)
if(user_choice==com_choice):
    print("Match is draw")
elif(com_choice>user_choice):
    print("You lose")
elif(user_choice>com_choice):
    print("You won")
elif(user_choice==0 and com_choice==2):
    print("You won")
elif(user_choice==2 and com_choice==0):
    print("You lose")
else:
    print("You entered invalid choice")



