from Node import Node

class LinkedList():
    def __init__(self,vals=[]):
        self.head = None
        self.tail = None
        self.length = 0
        
        for val in vals:
            self.push(val)
    
    def print_nodes(self):
        current_node = self.head
        while current_node is not None:
            print(current_node.data)
            current_node = current_node.next_node
            
    def index_out_of_bounds(self,idx,with_equals=True):
        if not with_equals:
            if idx > self.length or idx < 0:
                raise Exception("Index Out Of Bounds")
        else:
            if idx >= self.length or idx < 0:
                raise Exception("Index Out Of Bounds")
        return False
    
    def push(self,val):
        new_node = Node(val)
        
        if not self.head:
            self.head = new_node
            self.tail = self.head
        else:
            temp_node = self.tail
            self.tail.next_node = new_node
            self.tail = new_node
            self.tail.prev_node = temp_node
        self.length += 1
    
    def get_node(self,idx):
        current_node = self.head
        node_count = 0
        
        while current_node != None and node_count != idx:
            current_node = current_node.next_node
            node_count += 1
        
        return current_node

    def add_to_start(self,val):
        new_node = Node(val)
        
        if self.head == None:
            self.head = new_node
        else:
            self.head.prev = new_node
            new_node.next_node = self.head
            self.head = new_node
        if self.length == 0:
            self.tail = self.head
        self.length += 1
        
    def pop(self):
        popped_val = self.remove_at(self.length -1)
        if popped_val:
            return popped_val
        else:
            raise Exception("No Node To Pop")
    
    def shift(self):
        return self.removeAt(0)
    
    def get_at(self,idx):
        if not self.index_out_of_bounds(idx):
            found_node = self.get_node(idx)
            return found_node
    
    def set_at(self,idx,val):
        if not self.index_out_of_bounds(idx):
            found_node = self.get_node(idx)
            found_node.data = val
    
    def insert_at(self,idx,val):
        if not self.index_out_of_bounds(idx,False):
            if idx == 0:
                return self.add_to_start(val)
            if idx == self.length:
                return self.push(val)
            
            new_prev = self.get_node(idx).prev_node
            new_node = Node(val)
            temp_node = new_prev.next_node
            
            new_prev.next_node = new_node
            new_node.prev_node = new_prev
            new_node.next_node = temp_node
            temp_node.prev_node = new_node
            
            self.length += 1
            
    def remove_at(self,idx):
        if not self.index_out_of_bounds(idx):
            if idx == 0:
                val = self.head.data
                self.head = self.head.next_node
                if self.length > 1 and self.head.prev_node:
                    self.head.prev_node = None
                self.length -= 1
                if self.length < 2:
                    self.tail = self.head
                return val
            
            node_at_idx = self.get_node(idx)
            
            if idx == self.length - 1:
                val = node_at_idx.data
                self.tail = node_at_idx.prev_node
                self.tail.next_node = None
                self.length -= 1
                return val
            else:
                val = node_at_idx.data
                node_at_idx.prev_node.next_node.next_node.prev_node = node_at_idx.prev_node
                node_at_idx.prev_node.next_node = node_at_idx.prev_node.next_node.next_node
                self.length -= 1
                return val
    
    def has_node_data(self,data):
        current_node = self.head
        while current_node is not None:
            if current_node.data == data:
                return True
            current_node = current_node.next_node
        return False

