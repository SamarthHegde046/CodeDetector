import heapq
def is_valid_state(miss_left,cann_left):
    miss_right=3-miss_left
    cann_right=3-cann_left
    if miss_left<0 or miss_right<0 or cann_left<0 or cann_right<0:
        return False
    if (miss_left>0 and miss_left<cann_left) or (miss_right>0 and miss_left<cann_right):
        return False
    return True
def get_successor(state):
    miss,cann,boat=state
    possible_moves=[(0,1),(0,2),(1,0),(2,0),(1,1)]
    successor=[]
    for m,c in possible_moves:
        if boat:
            new_state=(miss-m,cann-c,0)
        else:
            new_state=(miss+m,cann+c,1)
            if is_valid_state(*new_state):
                successor.append(new_state)
    return successor
def heuristic(state):
    miss_left,cann_left,_=state
    return miss_left+cann_left

def bfs():
    initial_state=(3,3,1)
    goal_state=(0,0,0)
    priority_queue=[]
    heapq.heappush(priority_queue,(heuristic(initial_state),initial_state,[]))
    visited=set()
    path=[]
    while priority_queue:
        _,state,path=heapq.heappop(priority_queue)
        if state in visited:
            continue
        visited.add(state)
        new_path=path+[state]
        if state==goal_state:
            return new_path
        for successor in get_successor(state):
            heapq.heappush(priority_queue,(heuristic(successor),successor,new_path))
    return None
solution=bfs()
for i in solution:
    print(i)