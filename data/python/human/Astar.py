Graph_nodes={
    'A':[('B',2),('E',3)],
    'B':[('C',1),('G',9)],
    'C':[],
    'E':[('D',6)],
    'D':[('G',1)],
    'G':[]
}

def heuristic(n):
    H_dist={
        'A':11,
        'B':6,
        'C':99,
        'D':1,
        'E':7,
        'G':0
    }
    return H_dist[n]

def get_neighbors(v):
    return Graph_nodes.get(v,[])

def Astaralgo(start,end):
    open_set=set([start])
    closed_set=set()
    g={start:0}
    parents={start:start}
    
    while open_set:
        n=None
        for v in open_set:
            if n is None or g[v]+heuristic(v)<g[n]+heuristic(n):
                n=v
        if n is None:
            print("Path does not exist")
            return None
        if n==end:
            path=[]
            while n!=start:
                path.append(n)
                n=parents[n]
            path.append(start)
            path.reverse()
            print("Path found :",path)
            return path
        for (m,weight) in get_neighbors(n):
            if m not in open_set and m not in closed_set:
                open_set.add(m)
                parents[m]=n
                g[m]=g[n]+weight
            else:
                if  g[m]>g[n]+weight:
                    g[m]=g[n]+weight
                    parents[m]=n
                    if m in closed_set:
                        closed_set.remove(m)
                        open_set.add(m)
        open_set.remove(n)
        closed_set.add(n)
    print("path does not exist")
    return None
path=Astaralgo('A','G')
                        
                
        