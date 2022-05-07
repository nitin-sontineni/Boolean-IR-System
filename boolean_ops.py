from Inverted_index import LinkedList
def AND_Evaluater(node1,node2):
    """Performs AND operation between the given two linkedlists

    Args:
        node1 (LinkedList): LinkedList containing the list of documents that have first word
        node2 (LinkedList): LinkedList containing the list of documents that have second word

    Returns:
        LinkedList : Resulted LinkedList after perfoming the AND operation
    """
    node1 = node1.head
    node2 = node2.head

    llist = LinkedList()
    while node1 is not None and node2 is not None:
        if(node1.data == node2.data):   
            #If data in both nodes of the lists is same inserting node1 data
            llist.insert(node1.data)
            node1 = node1.next   
            #incrementing both nodes
            node2 = node2.next            
        elif(node1.data < node2.data):  
            if(node1.skip is not None and node1.skip.data < node2.data):
                node1 = node1.skip   
                #Skipping if required conditions satisfied
            else:
                node1 = node1.next
        elif(node1.data > node2.data):
            if(node2.skip is not None and node2.skip.data < node1.data):
                node2 = node2.skip   
                #Skipping if required conditions satisfied
            else:
                node2 = node2.next
           
    llist.buildSkipList()   
    #Building skiplist for the result
    return llist

#OR Evaluater
def OR_Evaluater(node1,node2):
    """Performs OR operation between the given two linkedlists

    Args:
        node1 (LinkedList): LinkedList containing the list of documents that have first word
        node2 (LinkedList): LinkedList containing the list of documents that have second word

    Returns:
        LinkedList : Resulted LinkedList after perfoming the OR operation
    """
    node1 = node1.head
    node2 = node2.head
    llist = LinkedList()
    while node1 is not None and node2 is not None:
        #If data at both nodes is same, inserting node1 value and incrementing both
        if(node1.data == node2.data):
            llist.insert(node1.data)
            node1 = node1.next
            node2 = node2.next
            #Inserting the node with lesser data value and incrementing it
        elif node1.data < node2.data:  
            llist.insert(node1.data)
            node1 = node1.next                
        elif node1.data > node2.data:
            llist.insert(node2.data)
            node2 = node2.next

    #Inserting the left over nodes if any among the two lists
    while node1 is not None:
        llist.insert(node1.data)
        node1 = node1.next
        
    while node2 is not None:
        llist.insert(node2.data)
        node2 = node2.next

    llist.buildSkipList()   
    #Building skiplist for the result
    return llist

def NOT_Evaluater(docs,Total_Docs):
    """Performs NOT operation for the given LinkedList

    Args:
        docs (LinkedList): LinkedList containing the list of documents that have the word 
        Total_Docs (int): Total number of documents in the database

    Returns:
        LinkedList : Resulted LinkedList after perfoming the AND operation
    """
    docs = docs.head
    #print("Performing NOT operation")
    llist = LinkedList()
    i = 0
    #Considering all the docs and then removing the required docs
    while(i < Total_Docs and docs is not None):
        if(docs.data != i):
            llist.insert(i)
        else:
            docs = docs.next
        i = i + 1    
    
    while(i < Total_Docs):
        llist.insert(i)
        i = i + 1

    llist.buildSkipList()   
    #Building skiplist for the result
    return llist
