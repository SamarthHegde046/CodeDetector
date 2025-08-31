class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def insert(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def reverse(self):
        prev, current = None, self.head
        while current:
            nxt = current.next
            current.next = prev
            prev = current
            current = nxt
        self.head = prev

    def display(self):
        temp = self.head
        while temp:
            print(temp.data, end=" -> ")
            temp = temp.next
        print("None")


# Example
ll = LinkedList()
for i in [1, 2, 3, 4]:
    ll.insert(i)
ll.display()   # 4 -> 3 -> 2 -> 1 -> None
ll.reverse()
ll.display()   # 1 -> 2 -> 3 -> 4 -> None
