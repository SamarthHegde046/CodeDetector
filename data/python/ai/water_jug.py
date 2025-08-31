# Water Jug Problem using DFS

capacity1 = 3   # Jug 1 capacity
capacity2 = 5   # Jug 2 capacity
target = 4      # Target amount

jug1, jug2 = 0, 0
visited = set()
path = []


def dfs(jug1, jug2):
    # Avoid revisiting same state
    if (jug1, jug2) in visited:
        return False
    visited.add((jug1, jug2))
    path.append((jug1, jug2))

    # Check target
    if jug1 == target or jug2 == target:
        return True

    # 1. Fill jug1
    if jug1 != capacity1 and dfs(capacity1, jug2):
        return True

    # 2. Fill jug2
    if jug2 != capacity2 and dfs(jug1, capacity2):
        return True

    # 3. Empty jug1
    if jug1 != 0 and dfs(0, jug2):
        return True

    # 4. Empty jug2
    if jug2 != 0 and dfs(jug1, 0):
        return True

    # 5. Pour jug1 -> jug2
    if jug1 > 0 and jug2 < capacity2:
        transfer = min(jug1, capacity2 - jug2)
        if dfs(jug1 - transfer, jug2 + transfer):
            return True

    # 6. Pour jug2 -> jug1
    if jug2 > 0 and jug1 < capacity1:
        transfer = min(jug2, capacity1 - jug1)
        if dfs(jug1 + transfer, jug2 - transfer):
            return True

    # Backtrack
    path.pop()
    return False


# Run DFS
solution_found = dfs(jug1, jug2)

if solution_found:
    print("✅ Solution Found:")
    for state in path:
        print(state)
else:
    print("❌ Solution not found")
