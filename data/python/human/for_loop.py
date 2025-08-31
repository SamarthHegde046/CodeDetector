#names="sanketh","sachin"
#for name in names:
#      print([name])

numbers=[2,5,7,8,9]
list=[]
for i in numbers:
    square=i**2
    list.append(square)
print(list)


num=input("Enter the no:")
lst=num.split(",")
list=[]
count=0
for j  in range(len(lst)):
    lst[j]=int(lst[j])
for i in lst:
    square=i**2
    list.append(square)
print(list)

