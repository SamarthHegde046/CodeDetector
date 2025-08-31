pizza=int(input("1.Small Pizza\n2.Medium Pizza\n3.Large Pizza\nEnter the pizza u want(1/2/3):"))
pp=0
ch=0
if pizza==1:
    pp=100
    print("pay 100RS\-")
    a=input("Do u want pepperon(y/n):")
    if a=="y" or a=="Y":
        pp=pp+30
        print("Your total cost is",pp)
        b=input("Do u want extra cheese(y/n):")
        if b=="Y" or b=="y":
            ch=pp+20
            print("your total cost is:",ch)
        else:
            print("ok Thank you......")


    elif a=="N" or "n":
        print("ok Thank you......")
elif pizza==2:
    pp=200
    print("pay 200RS\-")
    a=input("Do u want pepperon(y/n):")
    if a=="y" or a=="Y":
        pp=pp+50
        print("Your total cost is",pp)
        b=input("Do u want extra cheese(y/n):")
        if b=="Y" or b=="y":
            ch=pp+20
            print("your total cost is:",ch)
        else:
            print("ok Thank you......")
    else:
        print("ok Thank you......")
elif pizza==3:
    pp=300
    print("pay 300RS\-")
    a=input("Do u want pepperon(y/n):")
    if a=="y" or a=="Y":
        pp=pp+70
        print("Your total cost is",pp)
        b=input("Do u want extra cheese(y/n):")
        if b=="y" or b=="y":
            ch=pp+20
            print("your total cost is:",ch)
        else:
            print("ok Thank you......")
    else:
        print("You entered invalid choice")

