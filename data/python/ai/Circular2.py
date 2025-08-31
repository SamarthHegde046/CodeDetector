class Node:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None

class CircularDoublyLinkedList:
    def __init__(self):
        self.head = None

    def insert(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            new_node.next = new_node
            new_node.prev = new_node
            return
        last = self.head.prev
        new_node.next = self.head
        new_node.prev = last
        last.next = new_node
        self.head.prev = new_node

    def display(self):
        if not self.head:
            return
        temp = self.head
        while True:
            print(temp.data, end=" <-> ")
            temp = temp.next
            if temp == self.head:
                break
        print("(back to head)")


# Example
cdll = CircularDoublyLinkedList()
cdll.insert(10)
cdll.insert(20)
cdll.insert(30)
cdll.display()   # 10 <-> 20 <-> 30 <-> (back to head)
