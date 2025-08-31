import datetime

# Get today's year
current_year = datetime.date.today().year

# Input details
name = input("Enter the name of the person: ")
byear = int(input("Enter the birth year: "))

# Calculate age
age = current_year - byear

# Check senior citizen status
if age >= 60:
    print(f"{name} is a Senior Citizen (Age: {age})")
else:
    print(f"{name} is not a Senior Citizen (Age: {age})")
