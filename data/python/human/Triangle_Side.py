def triangle(a,b,c):
    if(a+b>c and b+c>a and c+a>b):
        print("Sides can form a triangle")
    else:
        print("Sides cannot form a triangle")

a=int(input("Enter the value of a :"))
b=int(input("Enter the value of b :"))
c=int(input("Enter the value of c :"))
triangle(a,b,c)
    