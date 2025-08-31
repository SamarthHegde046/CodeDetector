height=float(input("Enter the height:"))
weight=float(input("Enter the weight:"))
result=(weight/(height**2))
print(f"youre bmi is {result}")
if(result<18.5):
    print("underwight")
elif(result<25.0):
    print("Normal weight")
elif(result<30):
    print("overweight")
else:
    print("you are clinically obessed")