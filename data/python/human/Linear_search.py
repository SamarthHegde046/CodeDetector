arr=[]
for i in range(5):
    ele=int(input("input :"))
    arr.append(ele)
key=int(input("key :"))
flag=0
f=0
r=len(arr)
for i in range(r):
    if(arr[i]==key):
        flag=1
        break
print(arr)
if(flag==1):
    print("key found at ",i)
else:
    print("key not found")
    
    