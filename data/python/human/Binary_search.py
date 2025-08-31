class Mycalss:
    def BS():
        arr=[]
        for i in range(5):
            ele=int(input("input : "))
            arr.append(ele)
        key=int(input("Key : "))
        flag=0
        f=0
        r=len(arr)-1
        while(f<=r):
            mid=(f+r)//2
            if(arr[mid]==key):
                return mid
                break
            elif(arr[mid]<key):
                r=mid-1
            else:
                f=mid+1
        return -1

    res=BS()
    if(res!=-1):
        print("key found at ",res)
    else:
        print("key not found")