#import random
#name=input("Enter the names:")
#a=name.split(",")
#b=random.choice(a)
#print(b)

#without using choice function

import random
name=input("Enter the name separated by commas:")
list=name.split(",")
len=len(list)
a=random.randint(0,len-1)
b=list[a]
print(b)