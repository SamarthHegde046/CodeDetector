import heapq

def is_valid_state(miss_left, cann_left):
    """Check if a state is valid: no missionaries are outnumbered by cannibals."""
    miss_right = 3 - miss_left
    cann_right = 3 - cann_left
    if miss_left < 0 or miss_right < 0 or cann_left < 0 or cann_right < 0:
        return False
    if (miss_left > 0 and miss_left < cann_left) or (miss_right > 0 and miss_right < cann_right):
        return False
    return True

def get_successors(state):
    """Generate valid successor states for the given state."""
    miss_left, cann_left, boat = state
    successors = []
    possible_moves = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]  # Valid boat moves
    if boat == 1:  # Boat on left, move to right
        for m, c in possible_moves:
            if m + c <= 2 and m + c >= 1:  # Boat can carry 1 or 2 people
                new_miss_left = miss_left - m
                new_cann_left = cann_left - c
                new_state = (new_miss_left, new_cann_left, 0)
                if is_valid_state(new_miss_left, new_cann_left):
                    successors.append(new_state)
    else:  # Boat on right, move to left
        for m, c in possible_moves:
            if m + c <= 2 and m + c >= 1:
                new_miss_left = miss_left + m
                new_cann_left = cann_left + c
                new_state = (new_miss_left, new_cann_left, 1)
                if is_valid_state(new_miss_left, new_cann_left):
                    successors.append(new_state)
    return successors

def heuristic(state):
    """Heuristic: number of missionaries and cannibals on the left."""
    miss_left, cann_left, _ = state
    return miss_left + cann_left

def describe_state(state, prev_state=None):
    """Return a human-readable description of the state transition."""
    miss_left, cann_left, boat = state
    miss_right = 3 - miss_left
    cann_right = 3 - cann_left
    boat_side = "left" if boat == 1 else "right"
    state_str = f"Left: {miss_left}M {cann_left}C | Right: {miss_right}M {cann_right}C | Boat: {boat_side}"
    
    if prev_state:
        prev_miss_left, prev_cann_left, prev_boat = prev_state
        miss_diff = prev_miss_left - miss_left
        cann_diff = prev_cann_left - cann_left
        direction = "right" if prev_boat == 1 else "left"
        if miss_diff == 0 and cann_diff == 0:
            return state_str  # No move description for initial state
        move_str = f"Move {abs(miss_diff)} missionary(ies) and {abs(cann_diff)} cannibal(s) to the {direction}"
        return f"{move_str}\n{state_str}"
    return state_str

def a_star():
    """Solve the Missionaries and Cannibals problem using A* search."""
    initial_state = (3, 3, 1)  # 3 missionaries, 3 cannibals, boat on left
    goal_state = (0, 0, 0)     # All on right, boat on right
    priority_queue = []
    heapq.heappush(priority_queue, (heuristic(initial_state), 0, initial_state, []))
    visited = set()
    
    while priority_queue:
        _, cost, state, path = heapq.heappop(priority_queue)
        if state in visited:
            continue
        visited.add(state)
        new_path = path + [state]
        
        if state == goal_state:
            return new_path
        
        for successor in get_successors(state):
            if successor not in visited:
                new_cost = cost + 1  # Each move has a cost of 1
                priority = new_cost + heuristic(successor)
                heapq.heappush(priority_queue, (priority, new_cost, successor, new_path))
    
    return None

def main():
    """Run the A* search and display the solution."""
    try:
        solution = a_star()
        if solution:
            print("Solution found:")
            for i, state in enumerate(solution):
                prev_state = solution[i-1] if i > 0 else None
                print(f"Step {i}:")
                print(describe_state(state, prev_state))
                print()
        else:
            print("No solution found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()