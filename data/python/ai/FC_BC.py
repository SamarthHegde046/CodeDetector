def forward_chaining(rules, facts, goal):
    inferred = set(facts)
    updated = True

    while updated:
        updated = False
        for conditions, conclusion in rules:
            if all(c in inferred for c in conditions) and conclusion not in inferred:
                inferred.add(conclusion)
                updated = True
                if conclusion == goal:
                    return True
    return False

def backward_chaining(rules, facts, goal):
    def ask(query):
        if query in facts:
            return True
        for conditions, conclusion in rules:
            if conclusion == query and all(ask(c) for c in conditions):
                return True
        return False
    return ask(goal)

rules = [
    (['hair', 'live young'], 'mammal'),
    (['feathers', 'fly'], 'bird')
]

# Forward chaining example
facts = ['hair', 'live young']
goal = 'mammal'
if forward_chaining(rules, facts, goal):
    print("The cat is classified as Mammal")
else:
    print("The cat is not classified as Mammal")

# Backward chaining example
facts = ['feathers', 'fly']
goal = 'bird'
if backward_chaining(rules, facts, goal):
    print("The pigeon is classified as Bird")
else:
    print("The pigeon is not classified as Bird")