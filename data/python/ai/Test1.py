class Solution:
    def romanToInt(self, s: str) -> int:
        """Convert a Roman numeral string to an integer."""
        # Dictionary mapping Roman numerals to their values
        roman_values = {
            'I': 1,
            'V': 5,
            'X': 10,
            'L': 50,
            'C': 100,
            'D': 500,
            'M': 1000
        }
        
        result = 0
        prev_value = 0
        
        # Iterate through the string from right to left
        for char in reversed(s):
            current_value = roman_values.get(char)
            # Validate character
            if current_value is None:
                raise ValueError(f"Invalid Roman numeral character: {char}")
            
            # If current value is greater than or equal to previous, add it
            if current_value >= prev_value:
                result += current_value
            # If current value is less than previous, subtract it
            else:
                result -= current_value
            prev_value = current_value
        
        # Validate result is positive and reasonable
        if result <= 0:
            raise ValueError("Invalid Roman numeral: result is not positive")
        
        return result

def main():
    try:
        # Input Roman numeral string
        s = input("Enter a Roman numeral (e.g., IV, IX, MMXXI): ").strip().upper()
        if not s:
            raise ValueError("Input string cannot be empty")
        
        # Create Solution object and convert
        solution = Solution()
        result = solution.romanToInt(s)
        print(f"The integer value of {s} is: {result}")
        
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()