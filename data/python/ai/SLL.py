class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class SLL:
    def __init__(self):
        self.head = None

    # Append at end
    def append(self, data):
        newnode = Node(data)
        if self.head is None:
            self.head = newnode
            return
        last = self.head
        while last.next:
            last = last.next
        last.next = newnode

    # Insert at beginning
    def insert(self, data):
        newnode = Node(data)
        newnode.next = self.head
        self.head = newnode

    # Remove a node by value
    def remove(self, data):
        cur = self.head

        # If head node itself is to be deleted
        if cur and cur.data == data:
            self.head = cur.next
            cur = None
            return

        prev = None
        while cur and cur.data != data:
            prev = cur
            cur = cur.next

        # If data not found
        if cur is None:
            return

        # Unlink the node
        prev.next = cur.next
        cur = None

    # Display linked list
    def display(self):
        cur = self.head
        while cur:
            print(cur.data, end=" -> ")
            cur = cur.next
        print("None")


# Example usage
sll = SLL()
sll.append(1)
sll.append(2)
sll.append(3)
sll.display()       # 1 -> 2 -> 3 -> None
sll.insert(0)
sll.display()       # 0 -> 1 -> 2 -> 3 -> None
sll.remove(2)
sll.display()       # 0 -> 1 -> 3 -> None
