x=0
y=0
z=0
a="()"
b="[]"
c="{}"
st="()()"
for i in st:
    if i in a:
        x=x+1
    else:
        x=x-1
    if i in b:
        y=y+1
    else:
        y=y-1
    if i in c:
        z=z+1
    else:
        z=z-1
if x==0 and y==0 and z==0 :
    print("Valid")
else:
    print("Invalid")
        