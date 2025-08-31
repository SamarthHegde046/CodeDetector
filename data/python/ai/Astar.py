# Define the graph with weighted edges
graph = {
    'A': [('B', 2), ('E', 3)],
    'B': [('C', 1), ('G', 9)],
    'C': [],
    'E': [('D', 6)],
    'D': [('G', 1)],
    'G': []
}

# Heuristic values for each node
def heuristic(node):
    h_values = {
        'A': 11,
        'B': 6,
        'C': 99,
        'D': 1,
        'E': 7,
        'G': 0
    }
    return h_values.get(node, float('inf'))

# Get neighbors of a node
def get_neighbors(node):
    return graph.get(node, [])

# A* algorithm implementation
def astar(start, goal):
    open_set = set([start])
    closed_set = set()
    g_score = {start: 0}
    parent = {start: None}

    while open_set:
        current = min(open_set, key=lambda x: g_score[x] + heuristic(x))

        if current == goal:
            path = []
            while current:
                path.append(current)
                current = parent[current]
            path.reverse()
            print("Path found:", path)
            return path

        open_set.remove(current)
        closed_set.add(current)

        for neighbor, weight in get_neighbors(current):
            tentative_g = g_score[current] + weight

            if neighbor in closed_set and tentative_g >= g_score.get(neighbor, float('inf')):
                continue

            if tentative_g < g_score.get(neighbor, float('inf')) or neighbor not in open_set:
                parent[neighbor] = current
                g_score[neighbor] = tentative_g
                open_set.add(neighbor)

    print("Path does not exist")
    return None

# Run the algorithm
path = astar('A', 'G')