def forward_chaining(rules,facts,goal):
    inferred_facts=set(facts)
    new_facts=True
    
    while new_facts:
        new_facts=False
        for rule in rules:
            condition,result=rule
            if all(cond in inferred_facts for cond in condition) and result not in inferred_facts:
                inferred_facts.add(result)
                new_facts=True
                if result==goal:
                    return True
    return False

def backward_chaining(rules,facts,goal):
    def ask(query):
        if query in facts:
            return True
        
        for rule in rules:
            condition,result=rule
            if result==query and all(ask(cond) for cond in condition):
                return True
        return False
    return ask(goal)

rules=[
    (['hair','live young'],'mammal'),(['feathers','fly'],'bird')
]

facts=['hair','live young']
goal='mammal'

is_mammal=forward_chaining(rules,facts,goal)
if is_mammal:
    print("The cat is classified as Mammal")
else:
    print("The cat is not classified as Mammal")
    
facts=['feathers','fly']
goal='bird'
is_bird=backward_chaining(rules,facts,goal)
if is_bird:
    print("The pigeon classified as bird")
else:
    print("The pigeon not classified as bird")