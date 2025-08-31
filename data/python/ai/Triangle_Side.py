def triangle(a, b, c):
    # Check Triangle Inequality Theorem
    if a + b > c and b + c > a and c + a > b:
        print("✅ The given sides can form a triangle.")
    else:
        print("❌ The given sides cannot form a triangle.")

# Input
a = int(input("Enter side a: "))
b = int(input("Enter side b: "))
c = int(input("Enter side c: "))

# Function call
triangle(a, b, c)
