from nltk.stem.porter import PorterStemmer
from Inverted_index import Node,LinkedList,InfoRetSystem
from boolean_ops import AND_Evaluater,OR_Evaluater,NOT_Evaluater
IR_System = InfoRetSystem()
IR_System.buildIRSystem()
IR_System.buildKGramIndex()
print()
print("System ready for queries")
print()
all_words = IR_System.invertedIndex.keys()

def editDist(str1, str2):
    """Finds edit distance between the given two strings

    Args:        str1 (string): First String
        str2 (string): Second String

    Returns:
        int : Edit distance
    """
    m = len(str1)
    n = len(str2)
    dp = [[0 for x in range(n + 1)] for x in range(m + 1)]

    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j
                
            elif j == 0:
                dp[i][j] = i

            elif str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]

            else:
                dp[i][j] = 1 + min(dp[i][j-1],#For Insert
                                dp[i-1][j], #For Remove
                                dp[i-1][j-1]) #For Replace

    return dp[m][n]


def Filter(close_words,op):
    """Does OR or AND operation on all linkedlists in the list close_words

    Args:
        closewords (List[LinkedList]): List that AND or OR operation to happen
        op (string) = "AND"|"OR" : operation AND or OR 

    Returns:
        LinkedList: The end result of the operation
    """

    if len(close_words) == 0:
        return LinkedList()
    result = IR_System.invertedIndex[close_words[0][0]]
    
    for x in close_words[1:]:
        if op == "OR":
            result = OR_Evaluater(result,IR_System.invertedIndex[x[0]])
        
        elif op == "AND":
            result = AND_Evaluater(result,IR_System.invertedIndex[x[0]])

    result.buildSkipList()        
    return result


def Filterx(close_words,op):
    """Function for applying "OR" or "AND" operations between the obtained wild card query words

    Args:
        closewords (List[LinkedList]): List that AND or OR operation to happen
        op (string) = "AND"|"OR" : operation AND or OR 

    Returns:
        LinkedList: The end result of the operation
    """
    if close_words.size == 0:
        return None
    result = IR_System.invertedIndex[close_words.head.data]
    pointer = close_words.head.next

    
    while pointer!=None:
        if op == "OR":
            result = OR_Evaluater(result,IR_System.invertedIndex[pointer.data])
        
        elif op == "AND":
            result = AND_Evaluater(result,IR_System.invertedIndex[pointer.data])
        pointer = pointer.next

    result.buildSkipList()      
    return result


def postFiltering(words,reg):
    """Performs postfiltering after k-gram wild card searching
        Returns those words which matches with the regex given'''

    Args:
        words (List[string]): list of words to match the  string pattern
        reg (string): the regular expression that the string need to match

    Returns:
        LinkedList: the words that match the regex in a linked list
    """
    import re
    reg = reg.replace("*","[a-z]*")

    pattern = re.compile(reg)
    pointer = words.head
    output = LinkedList()
    while pointer!=None:
        if re.fullmatch(pattern,pointer.data):
            output.insert(pointer.data)
        pointer = pointer.next
        
    output.buildSkipList()
    return output
    
def wildCard(word):
    """ get words that matches the wildcard query of the user using the K gram Index.

    Args:
        word (string): the wildcard query

    Returns:
        LinkedList: linkedlist that contains the doc IDS that has words that match the wildcard query
    """
    query = word
    ''' splittting the query with *'''
    search_terms = query.replace('*',' * ').split()

    ''' if search term is only "*": then return all the documents'''
    if len(search_terms)==1:
        allDocLinkedList = LinkedList()
        for i in range(len(IR_System.fileList)):
            allDocLinkedList.insert(i)
        return allDocLinkedList

    firstStar = 1 if search_terms[0] == "*" else 0
    lastStar = 1 if search_terms[-1] == "*" else 0

    k_terms = []
    for x in search_terms:
        if x!="*":
            if len(x) <= 3:
                k_terms.append(x)
            else:
                pointer = 0
                while pointer<=len(x)-3:
                    k_terms.append(x[pointer:pointer+3])
                    pointer+=1
    
    if firstStar == 0:
        k_terms[0] = "$" + k_terms[0]
    if lastStar == 0:
        k_terms[-1]+="$"
    
    '''get linked list of words, of each k-gram'''
    try:
        _words = list(map(lambda x:IR_System.kGramIndex[x],k_terms))
    except:
        print("No words found")
        return LinkedList()

    from functools import reduce
    '''AND opeartor on all words and post filtering'''
    matched_words = postFiltering(reduce(lambda a,b:AND_Evaluater(a,b),_words),query)
    
    poin = matched_words.head
    wor = ""
    while poin!=None:
        wor+=(poin.data+", ")
        poin = poin.next
    print("Matched Words:",wor)
    return Filterx(matched_words,"OR")

def findCloseWords(stem_word,x):
    """ find the closest words if the given word is not present in the inverted index

    Args:
        stem_word (string): query word after the porter stemming
        x (string): raw query word

    Returns:
        Linkedlist: Linked list that contains doc IDs of the closest words
    """
    print()
    print("Finding closer words for "+ x)

    close_words = [] 

    for check_word in all_words:
        #Calculating edit distance for each key
        dist = editDist(check_word,stem_word)
        if(dist <= 3):   #Keeping threshold edit distance as 3
            close_words.append([check_word,dist])

    close_words = sorted(close_words,key=lambda x:x[1])  

    if len(close_words) > 5:   #Selecting top 5 closer words if there are more than 5.
        close_words = close_words[:5]
    print()
    print(x + " is being replaced by close words : ",close_words)
    return Filter(close_words,"OR")  #Performing "OR" operation betweeen all close words found

#Query Parser
def parse(query):
    """parses the user input and processes the query

    Args:
        query (String): Information Retrieval query by the user

    Returns:
        LinkedList: all the DocIDs that satisfy the query
    """
    #Breaking down the given query into list of words
    query = "(" + query + ")"
    query = query.replace('(',' ( ')
    query = query.replace(')', ' ) ')
    query = query.split()

    stack = []
    for x in query:
        if(x != ')'):
            if(x == "AND" or x=="OR" or x == "NOT"):
                stack.append(x)
                
            elif('*' in x):
                stack.append(wildCard(x.lower()))
                           
            elif(x != '('):
                #Appending the word into stack after Stemming 
                porter = PorterStemmer()
                stem_word = porter.stem(x.lower())

                #Performing NOT operation while query parsing and appending the result into the stack
                if len(stack) > 0 and stack[-1] == "NOT":
                    stack.pop()
                    
                    if stem_word not in all_words:
                        cw = findCloseWords(stem_word,x)   #finding closer words if stem word is not in the inverted index keys
                    else:
                        cw = IR_System.invertedIndex[stem_word]
                    result = NOT_Evaluater(cw,len(IR_System.fileList))
                    stack.append(result)
                else:
                    if(stem_word in all_words):
                        stack.append(IR_System.invertedIndex[stem_word])
                    else:
                        #finding closer words if stem word is not in the inverted index keys and appending them into stack
                        stack.append(findCloseWords(stem_word,x))  
            
        elif(x == ')'):
            words,ops = [],[]
            #Separating words and operations into different lists
            while(len(stack) > 0 and stack[-1] != '('):
                if stack[-1] == "AND" or stack[-1] == "OR":
                    ops.append(stack.pop())
                else:
                    words.append(stack.pop())
            
            result = words[0]
            for i in range(len(words[1:])):
                if ops[i] == "AND":
                    result = AND_Evaluater(result,words[i+1])  #performing AND if op is "AND" iteratively
                    
                elif ops[i] == "OR":
                    result = OR_Evaluater(result,words[i+1])  #performing OR if op is "OR" iteratively
            stack.append(result)
    return stack[0]

#Function to retrieve the docs
def doc_retriever(files):
    """Function to retrieve the required docs

    Args:
        files (LinkedList): LinkedList having list of documents that satisfy the user query
    """
    print(files.size,"Documents found relevant for your search : ")
    print()
    pointer,i = files.head,1
    while pointer!=None:
        print(str(i)+".",IR_System.fileList[pointer.data])
        i+=1
        pointer = pointer.next
    print()

def retrieved_docs(files):
    pointer = files.head
    docs = []
    while pointer != None:
        docs.append(IR_System.fileList[pointer.data])
        pointer = pointer.next

    return docs

def retrieveResults(query):
    """Function to retrieve the required results

    Args:
        query (string): Query given by the user
    """
    #return doc_retriever(parse(query))
    results = retrieved_docs(parse(query))
    nodes = []
    for i in range(len(results)):
        node_no = int(results[i][4:-4])
        nodes.append(node_no)
    return nodes
