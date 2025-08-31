try:
    # Part 1: Check if L1 is a palindrome
    L1 = ["Sana", "Sana"]
    L2 = L1.copy()  # Create a copy of L1
    print(f"Original copied list L2: {L2}")

    L1.reverse()  # Reverse L1
    if L1 == L2:
        print("The list is a Palindrome")
    else:
        print("The list is not a Palindrome")

    # Part 2: Analyze the Grade list
    Grade = ["A", "A", "C", "D", "F", "A", "B", "C", "D", "F"]
    print(f"Number of 'A' grades: {Grade.count('A')}")
    
    Grade.sort()  # Sort the Grade list
    print(f"Sorted Grade list: {Grade}")

except Exception as e:
    print(f"An error occurred: {e}")