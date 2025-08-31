class Solution:
    def romanToInt(self, c):
        if(c=='I'):
            return 1
        elif(c=='V'):
            return 5
        elif(c=='X'):
            return 10
        elif(c=='L'):
            return 50
        elif(c=='C'):
            return 100
        elif(c=='D'):
            return 500
        elif(c=='M'):
            return 1000
s="IV"
r=0
for i in s:
    r+=Solution().romanToInt(i)
print(r)


        