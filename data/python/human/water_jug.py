capacity1=3
capacity2=5
target=4
jug1=0
jug2=0
visited=set()
path=[]

def dfs(jug1,jug2):
    if (jug1,jug2) in visited:
        return False
    visited.add((jug1,jug2))
    path.append((jug1,jug2))
    
    if jug1==target or jug2==target:
        return True
    
    if jug1!=capacity1 and dfs(capacity1,jug2):
        return True
    if jug2!=capacity2 and dfs(jug1,capacity2):
        return True
    if jug1!=0 and dfs(0,jug2):
        return True
    if jug2!=0 and dfs(jug1,0):
        return True
    if jug1>0 and jug2<capacity2:
        transfer=min(jug1,capacity2-jug2)
        if dfs(jug1-transfer,jug2+transfer):
            return True
    if jug2>0 and jug1<capacity1:
        transfer=min(jug2,capacity1-jug1)
        if dfs(jug1+transfer,jug2-transfer):
            return True
    path.pop()
    return False

solution_found=dfs(jug1,jug2)
if solution_found:
    print("Solution Found :")
    for i in path:
        print(i)
else:
    print("Solution not found")
    
