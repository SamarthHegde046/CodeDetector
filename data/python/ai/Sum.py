# Program to calculate sum, average, area, and comparison of two numbers

# Input
n1 = int(input("Enter the first number: "))
n2 = int(input("Enter the second number: "))

# Sum
total = n1 + n2
print("Sum of two numbers:", total)

# Average
avg = total / 2
print("Average of two numbers:", avg)

# Area (assuming numbers as rectangle sides)
area = n1 * n2
print("Area:", area)

# Comparison
print("Is first number greater than or equal to second number?", n1 >= n2)
