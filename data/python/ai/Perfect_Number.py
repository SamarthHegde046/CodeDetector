str1 = input("Enter: ")

if len(str1) == 6 and str1[:3].isupper() and str1[3:].isdigit():
    print("older")
elif len(str1) == 7 and str1[:4].isupper() and str1[4:].isdigit():
    print("newer")
else:
    print("Invalid")
