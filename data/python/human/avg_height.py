num=input("Enter the values:")
a=num.split(",")
b=len(a)
sum=0
count=0
for i in a:
    sum=sum+int(i)

for i in a:
    count=count+1
print(round(sum/b))

