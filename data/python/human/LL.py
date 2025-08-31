class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class SLL:
    def __init__(self):
        self.head = None
    
    def create(self,n):
        for i in range(n):
            new_node = Node(int(input()))
            if self.head is None:
                self.head=new_node
            else:
                temp=self.head
                while(temp.next!=None):
                    temp=temp.next
                temp.next=new_node
        return n
    def search(self,key):
            temp=self.head
            while(temp.next!=None):
                if key==temp.data:
                    print("Key found")
                    return
                temp=temp.next
            print("key not found")
            

    def display(self):
        print("Contents of List :")
        temp=self.head
        while(temp!=None):
            print(temp.data)
            temp=temp.next
            
    def insert_front(self,ele):
        new_node=Node(ele)
        if self.head==None:
            head=new_node
        else:
            temp=self.head
            new_node.next=temp
            self.head=new_node
            
    def insert_pos(self,ele,pos):
        if pos==1:
            L.insert_front(ele)
        else:
            temp=self.head
            new_node=Node(ele)
            p=2
            while(temp.next!=None):
                if p==pos:
                    ntemp=temp.next
                    temp.next=new_node
                    new_node.next=ntemp
                    return
                temp=temp.next
                p=p+1
                
    def delete_front(self):
        if self.head==None:
            print("List is empty")
        else:
            
            temp=self.head
            print("Deleted element : ",temp.data)
            self.head=self.head.next
            temp=None
            return self.head
        
    def delete_end(self):
        if self.head==None:
            print("List is empty")
        elif self.head.next==None:
            print("Deleted element : ",self.head.data)
            self.head=None
            return self.head
        else:
            temp=self.head
            while(temp.next.next!=None):
                temp=temp.next
            print("Deleted element : ",temp.next.data)
            temp.next=None
            
    def count(self):
        count=0
        temp=self.head
        while(temp!=None):
            count=count+1
            temp=temp.next
        return count
        
            
    def delete_pos(self,pos):
        if pos<=0 or pos>L.count():
            print("Invalid Position")
        if pos==1:
            L.delete_front()
        else:
            temp=self.head
            p=2
            while(temp.next!=None):
                if p==pos:
                    print("Deleted element : ",temp.next.data)
                    ntemp=temp.next.next
                    temp.next=ntemp
                    temp=None
                    return
                temp=temp.next
                p+=1
            
                
L = SLL()
L.create(5)
# L.display()
# L.search(1)
# L.insert_front(30)
# L.insert_pos(40,5)
# L.delete_end()
L.delete_pos(10)
# L.display()