try:
    # Input a string from the user
    str1 = input("Enter the string: ").strip()

    # Check if the string is empty
    if not str1:
        raise ValueError("Empty string entered. Please provide a valid string.")

    # Print the length of the string
    print(f"Length of the string: {len(str1)}")

    # Count and print the number of 's' (case-insensitive) in the string
    count_s = str1.lower().count('s')
    print(f"Number of 's' in the string: {count_s}")

except ValueError as ve:
    print(f"Error: {ve}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")