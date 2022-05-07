import math
import os
import time
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import nltk
nltk.download('punkt')
nltk.download('stopwords')
# Class node for linked list unit that contains fields : data,next and skip.
# skip : pointer pointing to the node after root(n) nodes or None


class Node:
    """Class node for linked list unit that contains fields : data,next and skip.
        skip : pointer pointing to the node after root(n) nodes or None
    """
    data = None
    next = None
    skip = None

    def __init__(self,data,next = None,skip = None):
        self.data = data
        self.next = next
        self.skip = skip

# Class LinkedList to support posting list.
class LinkedList:
    """Class LinkedList to support posting list.
    """
    # head : the first node of the linked list
    head = None
    pointer = head
    # size : size of the LinkedList
    size = 0
    # insert : insert data by creating a node at the end of linked list
    def insert(self,data):
        """ Insert any data into the LinkedList

        Args:
            data (Any): data to be stored in the LinkedList
        """
        self.size+=1
        if self.head == None:
            self.head = Node(data)
            self.pointer = self.head
        else:
            self.pointer.next = Node(data)
            self.pointer = self.pointer.next
    
    # buildSkipList : build the skip list pointers in the present linked list 
    def buildSkipList(self):
        """build the skip list pointers in the present linked list
        """
        n = int(math.sqrt(self.size))
        x = 0
        self.pointer = self.head
        present = self.head
        while self.pointer!=None:
            self.pointer = self.pointer.next
            x+=1
            if x == n:
                present.skip = self.pointer
                present = self.pointer
                x = 0

    # print_List : print the entire list including skip list for debugging purpose.
    def print_List(self):
        """print the entire list including skip list for debugging purpose.
        """
        self.pointer = self.head
        up = ""
        while self.pointer!=None:
            up+=(str(self.pointer.data) + ",")
            if self.pointer.skip!=None:
                up+=(str(self.pointer.skip.data))
            else:
                up+=("None")
            up+=" -> "
            self.pointer = self.pointer.next
        print(up)

# class InfoRetSystem : Class that has the Database filelist, InvertedIndex for faster
## data retrieval and K-gram Index for wildcard search management
class InfoRetSystem:
    """Class that has the Database filelist, InvertedIndex for faster data retrieval and K-gram Index for wildcard search management
    """
    fileList = os.listdir("data")
    invertedIndex = dict()
    kGramIndex = dict()
    # _preprocess : convert the incoming words to lowercase, punctuation free, and reduced
    ## to base form using porter stemming
    def remove_stopwords(self, data):
        """remove stopwords from a list

        Args:
            data (List): List that stop words should be eliminated of

        Returns:
            List: list that is filtered of stop words
        """
        return list(set(data) - set(stopwords.words()))

    def stemmer(self,data):
        """ apply porter stemmer rules to the list of words data

        Args:
            data (List): list that needs to be stemmed

        Returns:
            List: stemmed words list
        """
        porter = PorterStemmer()
        return list(map(lambda x:porter.stem(x),data))

    def _preprocess(self,data):
        """convert the incoming words to lowercase, punctuation free, and reduced to base form using porter stemming

        Args:
            data (string): preprocess the words

        Returns:
            List: all words that need to be keys of inverted index
        """
        #convert to lowercase
        data = data.lower()
        import string
        # Remove punctuations
        data = "".join([x for x in data if x not in string.punctuation])
        
        # Tokenizing and stopword filtering and portersteming
        porter = PorterStemmer()
        data = set(word_tokenize(data))

        return self.remove_stopwords([porter.stem(x) for x in data if not x.isnumeric()])


    # buildIRSyestem : build the inverted index by reading all the words preprocessing
    ## and storing in the inverted index with key as word and value as linked list of documents
    def buildIRSystem(self):
        """build the inverted index by reading all the words preprocessing and storing in the inverted index with key as word and value as linked list of documents
        """
        start = time.time()
        for i in range(len(self.fileList)):
            # open file
            f = open("data/"+self.fileList[i],'r')
            # read the data in the file
            data = f.read()
            wordsInFile = self._preprocess(data)
            # put each word doc information in the inverted index
            for x in wordsInFile:
                if x not in self.invertedIndex:
                    self.invertedIndex[x] = LinkedList()
                self.invertedIndex[x].insert(i)
            if i%10 == 0 or i == len(self.fileList)-1:
                print("added to invertedindex of", i, "in ",time.time() - start)
            f.close()
        # build skip list for all the doc linkedlists.
        for x in self.invertedIndex:
            self.invertedIndex[x].buildSkipList()
        end = time.time()
        print("IRSystem succesfully built in",end-start,"s")

    # buildKGramIndex : build 1gram, 2gram, 3gram indexes for wildcard search queries
    def buildKGramIndex(self):
        """build 3gram indexes for wildcard search queries
        """
        # take each word
        for x in sorted(self.invertedIndex.keys()):
            # convert to corresponding k-grams
            # 1 grams
            if ("$" + x[0]) not in self.kGramIndex:
                self.kGramIndex["$"+x[0]] = LinkedList()
            self.kGramIndex["$"+x[0]].insert(x)
            i = 1
            while i<(len(x)-1):
                if (x[i]) not in self.kGramIndex:
                    self.kGramIndex[x[i]] = LinkedList()
                self.kGramIndex[x[i]].insert(x)
                i+=1
            if (x[-1]+"$") not in self.kGramIndex:
                self.kGramIndex[x[-1]+"$"] = LinkedList()
            self.kGramIndex[x[-1]+"$"].insert(x)

            # 2 grams
            if len(x)>=2:
                if ("$" + x[0:2]) not in self.kGramIndex:
                    self.kGramIndex["$"+x[0:2]] = LinkedList()
                self.kGramIndex["$"+x[0:2]].insert(x)
                i = 1
                while i<(len(x)-2):
                    if (x[i:i+2]) not in self.kGramIndex:
                        self.kGramIndex[x[i:i+2]] = LinkedList()
                    self.kGramIndex[x[i:i+2]].insert(x)
                    i+=1
                if (x[len(x)-2:]+"$") not in self.kGramIndex:
                    self.kGramIndex[x[len(x)-2:]+"$"] = LinkedList()
                self.kGramIndex[x[len(x)-2:]+"$"].insert(x)

            # 3 grams
            if len(x)>=3:
                if ("$" + x[0:3]) not in self.kGramIndex:
                    self.kGramIndex["$"+x[0:3]] = LinkedList()
                self.kGramIndex["$"+x[0:3]].insert(x)
                i = 1
                while i<(len(x)-3):
                    if (x[i:i+3]) not in self.kGramIndex:
                        self.kGramIndex[x[i:i+3]] = LinkedList()
                    self.kGramIndex[x[i:i+3]].insert(x)
                    i+=1
                if (x[len(x)-3:]+"$") not in self.kGramIndex:
                    self.kGramIndex[x[len(x)-3:]+"$"] = LinkedList()
                self.kGramIndex[x[len(x)-3:]+"$"].insert(x)
        print("Succesfully built 3-gram index")