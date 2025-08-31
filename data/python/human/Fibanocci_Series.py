n = int(input("Enter the n value: "))
def fibonacci_series(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci_series(n-1) + fibonacci_series(n-2)
print(fibonacci_series(n))
