#num=input("Enter the no separated by comma:")
#lst=num.split(",")
#count=0
#for i in lst:
#    count=count+1
#for j in range(count):
#    lst[j]=int(lst[j])
#max=lst[0]
#for n in lst:
#    if n>max:
#        max=n
#print(max)

num=input("Enter the no separated by comma:")
lst=num.split(",")
lst.sort()
a=lst[-1]
print(a)




