#numbers=[1,5,3,[2,4,6],7,8]
#a=len(numbers)
#print(numbers[2:3])

#Hiding money execise

list=[[ 1, 1, 1 ],[ 1, 1, 1 ],[ 1, 1, 1 ]]
row=int(input("Enter the row:"))
col=int(input("Enter the column:"))
list[row-1][col-1]="X"
print(list[0])
print(list[1])
print(list[2])