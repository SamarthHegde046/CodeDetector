class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class SLL:
    def __init__(self):
        self.head = None
    
    def create(self, n):
        """Create a linked list with n nodes by taking user input."""
        if n <= 0:
            print("Invalid number of nodes. Must be positive.")
            return 0
        try:
            for i in range(n):
                data = int(input(f"Enter data for node {i+1}: "))
                new_node = Node(data)
                if self.head is None:
                    self.head = new_node
                else:
                    temp = self.head
                    while temp.next:
                        temp = temp.next
                    temp.next = new_node
            return n
        except ValueError:
            print("Error: Please enter valid integer values.")
            return 0

    def search(self, key):
        """Search for a key in the linked list."""
        temp = self.head
        position = 1
        while temp:
            if temp.data == key:
                print(f"Key {key} found at position {position}")
                return
            temp = temp.next
            position += 1
        print(f"Key {key} not found")

    def display(self):
        """Display all nodes in the linked list."""
        if not self.head:
            print("List is empty")
            return
        print("Contents of List:")
        temp = self.head
        while temp:
            print(temp.data, end=" -> ")
            temp = temp.next
        print("None")

    def insert_front(self, ele):
        """Insert a node with given element at the front."""
        new_node = Node(ele)
        new_node.next = self.head
        self.head = new_node
        print(f"Inserted {ele} at the front")

    def insert_pos(self, ele, pos):
        """Insert a node with given element at the specified position."""
        if pos <= 0 or pos > self.count() + 1:
            print("Invalid position")
            return
        if pos == 1:
            self.insert_front(ele)
            return
        new_node = Node(ele)
        temp = self.head
        for i in range(1, pos - 1):
            if not temp:
                print("Invalid position")
                return
            temp = temp.next
        if not temp:
            print("Invalid position")
            return
        new_node.next = temp.next
        temp.next = new_node
        print(f"Inserted {ele} at position {pos}")

    def delete_front(self):
        """Delete the first node of the linked list."""
        if not self.head:
            print("List is empty")
            return
        temp = self.head
        self.head = self.head.next
        print(f"Deleted element: {temp.data}")
        temp = None  # Free memory

    def delete_end(self):
        """Delete the last node of the linked list."""
        if not self.head:
            print("List is empty")
            return
        if not self.head.next:
            print(f"Deleted element: {self.head.data}")
            self.head = None
            return
        temp = self.head
        while temp.next.next:
            temp = temp.next
        print(f"Deleted element: {temp.next.data}")
        temp.next = None

    def count(self):
        """Return the number of nodes in the linked list."""
        count = 0
        temp = self.head
        while temp:
            count += 1
            temp = temp.next
        return count

    def delete_pos(self, pos):
        """Delete a node at the specified position."""
        if not self.head:
            print("List is empty")
            return
        if pos <= 0 or pos > self.count():
            print("Invalid position")
            return
        if pos == 1:
            self.delete_front()
            return
        temp = self.head
        for i in range(1, pos - 1):
            if not temp.next:
                print("Invalid position")
                return
            temp = temp.next
        if not temp.next:
            print("Invalid position")
            return
        print(f"Deleted element: {temp.next.data}")
        temp.next = temp.next.next

# Example usage
if __name__ == "__main__":
    L = SLL()
    try:
        n = int(input("Enter number of nodes to create: "))
        L.create(n)
        L.display()
        # Uncomment to test other methods
        # L.search(1)
        # L.insert_front(30)
        # L.insert_pos(40, 5)
        # L.delete_end()
        # L.delete_pos(10)
        # L.display()
    except ValueError:
        print("Error: Please enter a valid integer for the number of nodes.")