import datetime
date=datetime.date.today()
year=date.year
name=input("Enter the name of the person :")
byear=int(input("Enter the birth year :"))
age=year-byear
if age>=60:
    print(f"{name} is a Senior citizen")
else:
    print(f"{name} is not a Senior citizen")