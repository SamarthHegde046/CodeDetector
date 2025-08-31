# name = int(input("Enter:"))
# import math

# lst=[]
# while name!=11:
#     if(math.sqrt(name)**2==name):
#         lst.append(name)
#         name=name+1
# print(lst)

import math
name = int(input("Enter:"))

count=0
lst=[]
while count<10:
    if((math.sqrt(name))**2==name):
        lst.append(name)
        lst.append(",")
        name=name+1
        count+=1
    name+=1
lst.pop()
for i in lst:
    print(i, end="")

                          # Reading input from STDIN
         # Writing output to STDOUT