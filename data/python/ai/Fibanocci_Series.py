n = int(input("Enter the n value: "))

def fibonacci_series(n):
    if n < 0:
        return "Invalid input, n must be non-negative"
    if n == 0:
        return 0
    if n == 1:
        return 1
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

print(fibonacci_series(n))