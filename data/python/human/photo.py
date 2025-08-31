height=int(input("Enter ur height:"))
bill=0
if(height>=3):
    print("You can ride")
    age=int(input("Enter ur age:"))
    if(age<12):
        bill=150
        print("Pay 150rs")
    elif(age<=18):
        bill=200
        print("Pay 200rs")
    else:
        bill=500
        print("Pay 500rs")
    pic=input("Do u want to take photos(Y/N):")
    if pic == "y" or "Y":
        bill = bill+50
        print("your total bill is",bill)

else:
    print("you can't ride")
