name=input("Enter the name :")
usn=input("Enter the USN :")
print("Enter the 3 Subject Marks :")
list=[]
for i in range(1,4):
    i=int(input())
    list.append(i)
print("Student Name :",name)
print("Student USN :",usn)
print("Student Total marks for three subjects :",sum(list))
print("Student Percentage :",sum(list)/3)


    
    