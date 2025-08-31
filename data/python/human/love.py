name1=input("Enter your name:")
name2=input("Enter his/her name:")
add=name1 + name2
low=add.lower()
t=low.count("t")
r=low.count("r")
u=low.count("u")
e=low.count("e")
res1 = t + r + u + e
l=low.count("l")
o=low.count("o")
v=low.count("v")
e=low.count("e")
res2 = l + o + v + e
res=str(res1) + str(res2)
print("Your love rate is",res)