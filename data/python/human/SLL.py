class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
class SLL:
    def __init__(self):
        self.head=None
    def append(self,data):
        newnode=Node(data)
        if self.head is None:
            self.head=newnode
            return
        last=self.head
        while last.next:
            last=last.next
        last.next=newnode
    def insert(self,data):
        newnode=Node(data)
        newnode.next=self.head
        self.head=newnode
    def remove(self,data):
        cur=self.head
        if cur and cur.data==data:
            self.head=cur.next
            cur=None
            return
        prev=None
        while cur and cur.data!=data:
            prev=cur    
            cur=cur.next
            if cur is None:
                return
            prev.next=cur.next
            cur=None
            
    def display(self):
        cur=self.head
        while cur:
            print(cur.data,end=" ")
            cur=cur.next
        print(None)
        
sll=SLL()
sll.append(1)
sll.append(2)
sll.append(3)
sll.display()
sll.insert(0)
sll.display()
sll.remove(2)
sll.display()