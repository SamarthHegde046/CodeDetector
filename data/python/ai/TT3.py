def is_valid(st):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    
    for char in st:
        if char in "([{":   # opening bracket
            stack.append(char)
        elif char in ")]}": # closing bracket
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()
    
    return len(stack) == 0


# Example usage
st = input("Enter a bracket string: ")

if is_valid(st):
    print("✅ Valid")
else:
    print("❌ Invalid")
