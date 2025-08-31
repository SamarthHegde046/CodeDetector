def pattern_1(n):
    """Print a right-angled triangle of asterisks."""
    if n <= 0:
        raise ValueError("Number of rows must be positive")
    for i in range(1, n + 1):
        print("* " * i)

def pattern_2(n):
    """Print a right-angled triangle of asterisks (same as pattern_1)."""
    if n <= 0:
        raise ValueError("Number of rows must be positive")
    for i in range(1, n + 1):
        print("* " * i)

def pattern_3(n):
    """Print a right-angled triangle of numbers (1 to i in each row)."""
    if n <= 0:
        raise ValueError("Number of rows must be positive")
    for i in range(1, n + 1):
        for j in range(1, i + 1):
            print(j, end=" ")
        print()

def pattern_4(n):
    """Print a square pattern of asterisks."""
    if n <= 0:
        raise ValueError("Number of rows must be positive")
    for i in range(n):
        print("* " * n)

def pattern_5(n):
    """Print a right-angled triangle of alphabets (A, AB, ABC, ...)."""
    if n <= 0:
        raise ValueError("Number of rows must be positive")
    for i in range(n):
        char = ord('A')
        for j in range(i + 1):
            print(chr(char), end=' ')
            char += 1
        print()

def main():
    """Main function to select and run a pattern."""
    while True:
        print("\nPattern Menu:")
        print("1. Pattern 1: Right-angled triangle of asterisks")
        print("2. Pattern 2: Right-angled triangle of asterisks (same as Pattern 1)")
        print("3. Pattern 3: Right-angled triangle of numbers")
        print("4. Pattern 4: Square of asterisks")
        print("5. Pattern 5: Right-angled triangle of alphabets")
        print("6. Exit")
        
        try:
            choice = int(input("Enter your choice (1-6): "))
            if choice == 6:
                print("Exiting program.")
                break
            if choice < 1 or choice > 6:
                print("Invalid choice. Please enter a number between 1 and 6.")
                continue
            
            if choice == 3:
                n = int(input("Enter the number of rows: "))
            else:
                n = int(input("Enter the number of rows (default 5 for Pattern 1/4, 4 for Pattern 2/5): ") or 
                        (5 if choice in [1, 4] else 4))
            
            print(f"\nPattern {choice}:")
            if choice == 1:
                pattern_1(n)
            elif choice == 2:
                pattern_2(n)
            elif choice == 3:
                pattern_3(n)
            elif choice == 4:
                pattern_4(n)
            elif choice == 5:
                pattern_5(n)
                
        except ValueError as ve:
            print(f"Error: {ve if str(ve) else 'Please enter a valid integer.'}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()