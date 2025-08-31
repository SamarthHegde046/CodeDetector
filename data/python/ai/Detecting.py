class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def push(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def detect_cycle(self):
        slow = fast = self.head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow == fast:
                return True
        return False


# Example
ll = LinkedList()
ll.push(10)
ll.push(20)
ll.push(30)

# create a loop (30 -> 10)
ll.head.next.next.next = ll.head
print("Cycle Detected:", ll.detect_cycle())  # True
