try:
    # Input three numbers from the user
    a = int(input("Enter a value: "))
    b = int(input("Enter b value: "))
    c = int(input("Enter c value: "))

    # Find the largest number
    largest = a
    if b > largest:
        largest = b
    if c > largest:
        largest = c

    # Print the largest number
    print(f"Largest is: {largest}")

    # Check if the largest number is even or odd
    print(f"Largest is {'even' if largest % 2 == 0 else 'odd'}")

    # Check if the largest number is a multiple of 7
    print(f"Largest is {'a multiple of 7' if largest % 7 == 0 else 'not a multiple of 7'}")

except ValueError:
    print("Error: Please enter valid integer values.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")