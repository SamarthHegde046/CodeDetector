class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

def merge_sorted_lists(l1, l2):
    dummy = Node(0)
    tail = dummy
    while l1 and l2:
        if l1.data < l2.data:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next
    tail.next = l1 if l1 else l2
    return dummy.next

def print_list(head):
    while head:
        print(head.data, end=" -> ")
        head = head.next
    print("None")


# Example
a = Node(1); a.next = Node(3); a.next.next = Node(5)
b = Node(2); b.next = Node(4); b.next.next = Node(6)

merged = merge_sorted_lists(a, b)
print_list(merged)  # 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> None
