# Print prime numbers between 2 and 9
for i in range(2, 10):
    is_prime = True
    for j in range(2, i):
        if i % j == 0:
            is_prime = False
            break
    if is_prime:
        print(i)
