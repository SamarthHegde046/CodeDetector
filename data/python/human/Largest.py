a=int(input("Enter a value : "))
b=int(input("Enter b value : "))
c=int(input("Enter c value : "))
if(a>b and a>c):
    largest=a
elif(b>c):
    largest=b
else:
    largest=c
    
print("Largest is :",largest)

if(largest%2==0):
    print("Largest is even")
else:
    print("Largest is odd")
    
if(largest%7==0):
    print("Largest is multiple of 7")
else:
    print("Largest is not multiple of 7")
