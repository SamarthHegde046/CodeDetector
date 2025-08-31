num=[4,8,1,2,5,6]
for i in num:
    print(i)
    if i==5:
        break
else:
    print("Execution is success")

#in for else loop else part eill execute only for loop is completely terminated
#in the above case else part should not be execute because when 5 hits loop will be break still 6 is not terminated so for lopp is not completely terminated so else part will not execute