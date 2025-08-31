#Pattern 1
n=5
for i in range(1,n+1):
    print("* "* i)
    
#Pattern 2
def pattern_2(n):
    for i in range(1,n+1):
        print("* "*i)
pattern_2(4)

#Pattern 3
def pattern_3():
    n=int(input("Enter the value of n :"))
    for i in range(1,n+1):
        for j in range(1,i+1):
            print(j,end=" ")
        print()
pattern_3()

#Pattern 4
def square_pattern(n):
    for i in range(n):
        print('* ' * n)
square_pattern(5)

#Pattern 5

def abcd_pattern(n):
    for i in range(n):
        char = ord('A')
        for j in range(i + 1):
            print(chr(char), end=' ')
            char += 1
        print()
abcd_pattern(4)
