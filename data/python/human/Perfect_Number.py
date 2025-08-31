import string
str1=input("Enter :")
if string.ascii_uppercase(str1[0:3]) and string.digits(str1[3:6]):
    print("older")
elif str1[0:4]==string.ascii_uppercase and str1[4:7]==string.digits :
    print("newer")
else:
    print("Invalid")
