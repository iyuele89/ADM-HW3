import json
import heapq
import math
import pandas as pd
from scripts.utilities import TextTools



class DocScore:
    """
    This class is used to hold the tuple (document_ID, score)
    and to make use of the overloading of the operators
    """
    def __init__(self, doc_score:list):
        self.doc_score = doc_score # initialize the object with the doc_ID and the score

    def __lt__(self, other):
        return self.doc_score[1] < other.doc_score[1] # compare scores
    
    def __le__(self, other):
        return self.doc_score[1] <= other.doc_score[1] # compare scores

    def __eq__(self, other):
        return self.doc_score[0] == other.doc_score[0] # compare scores

    def __repr__(self): 
        return str(self.doc_score) # nice print

    def __hash__(self):
        return hash(self.doc_score[0]) # to pass as a key of a dictionary



class SearchEngine:
    """
    This class contains the logic for querying the system.
    Its constructor takes the paths to files that are used for index documents and words.
    Interface:
        * select_mode() : change the behaviour of the search engine; use inverted TF-IDF index 
                            or simple index
        * search() : make a query; select how to sort the results
    """
    def __init__(self, vocabulary_path='./data/vocabulary.json',\
                i_index_path='./data/inverted_index_2_1_1.json',\
                i_index_tfidf_path='./data/inverted_index_2_2_1.json',\
                doc_magnitude_path='./data/precomputed/doc_magnitude.json'):
        with open(vocabulary_path, 'r') as vocabulary_file:
            self.vocabulary = json.load(vocabulary_file)
        self.i_index_path = i_index_path
        self.i_index_tfidf_path = i_index_tfidf_path
        self.doc_magnitude_path = doc_magnitude_path


    def select_mode(self, use_tfidf=False):
        self.use_tfidf = use_tfidf # boolean variable to change the inverted index file
        if use_tfidf:
            with open(self.i_index_tfidf_path, 'r') as i_index_tfidf_file:
                self.i_index = json.load(i_index_tfidf_file)
        else:    
            with open(self.i_index_path, 'r') as i_index_file:
                self.i_index = json.load(i_index_file)


    def _search(self, query):
        query_words = list(set(TextTools.pre_process(query).split(' '))) # don't care about the frequency of a word in the query
        query_len = len(query_words) # number of unique words in the query
        try:
            posting_lists = [self.i_index[str(self.vocabulary[word])] for word in query_words] # list containing the posting lists of the words in the query
        except:
            print('No results :(') # one or more words in the query didn't be found
            return []
        documents = {k:1 for k in posting_lists[0]} # dictionary whose keys are the IDs of the documents in the first posting list
        for l in posting_lists[1:]: # for the remaining posting lists
            for doc in l: # for each document
                if doc in documents: # if a document ID in the current posting list is present in the first posting list, then increase the dictionary value
                    documents[doc] += 1
        return [k for k in documents if documents[k] == query_len] # keep only the documents that are present in all the posting lists
        

    def _search_tfidf(self, query):
        query_words = list(set(TextTools.pre_process(query).split(' '))) # don't care about the frequency of a word in the query
        query_len = len(query_words) # number of unique words in the query
        try:
            posting_lists = [self.i_index[str(self.vocabulary[word])] for word in query_words] # list containing the posting lists of the words in the query
        except:
            print('No results :(') # one or more words in the query didn't be found
            return []
        documents = {k[0]:[k[1]] for k in posting_lists[0]} # dictionary whose keys are the IDs of the documents in the first posting list
        for l in posting_lists[1:]: # for the remaining posting lists
            for doc in l: # for each document
                if doc[0] in documents: # if a document ID in the current posting list is present in the first posting list, then append the i-th component 
                    documents[doc[0]].append(doc[1])
        documents = {k:documents[k] for k in documents.keys() if len(documents[k]) == query_len} # keep only the documents that are present in all the posting lists
        with open(self.doc_magnitude_path, 'r') as doc_magnitude_file:
            doc_magnitude = json.load(doc_magnitude_file) # file containing the magnitude of the documents' vectors
        cosine_sim = lambda d_vec, d_mag: round(sum(d_vec) / d_mag, 3) # since invariant with respect to the documents, ignore the query vector magnitude
        return [DocScore([int(k), -cosine_sim(documents[k], doc_magnitude[str(k)])]) for k in documents] # return a list of DocScore(docID, score); the opposite 
        # of the score is considered, since the library heapq provides only a MinHeap data structure


    def _top_k_docs(self, doc_scores, k): # return the top k documents, popping them from the heap
        heapq.heapify(doc_scores) # build the MinHeap
        len_scores = len(doc_scores) # number of documents in the result 
        i = 0
        top_k_docs = []
        while i < k and i < len_scores:
            top_k_docs.append(heapq.heappop(doc_scores)) # get the minimum of the heap, i.e. the maximum absolute value of the score
            i += 1
        return top_k_docs


    def search(self, query, dataset, k=10, new_score=False, additional_query=None):
        """
        Make a query. 
        Parameters: 
            * query : supposed to be a string
            * dataset : supposed to be a pandas.DataFrame
            * k : integer, number of documents to return at most
            * new_score : use the custom score metric
            * additional_query : provide some additional information to sort the result
        """
        if self.use_tfidf:
            doc_scores = self._search_tfidf(query) # get the documents that correspond to the query
            top_k_docs = self._top_k_docs(doc_scores, k) # get the k most pertinent documents
            if new_score:
                result = pd.DataFrame()
                for d in top_k_docs:
                    result = pd.concat([result, dataset[dataset['file_num']==d.doc_score[0]]]) # get the documents records, sorted as top_k_docs
                top_k_docs = self._new_scoring_fun(result, top_k_docs, additional_query, k) # sort the k top documents with respect to the custom metric
            result = pd.DataFrame()
            for d in top_k_docs:
                result = pd.concat([result, dataset[dataset['file_num']==d.doc_score[0]][['bookTitle', 'Plot', 'Url']]]) # get the documents records, sorted as top_k_docs
            result.loc[:, 'Similarity'] = [-d.doc_score[1] for d in top_k_docs] # add the scores to the dataframe; take the positive cosine similarity
            return result
        else:
            result = self._search(query) # get the documents in which are present all the words of the query
            return dataset[dataset['file_num'].isin(result)][['bookTitle', 'Plot', 'Url']].head(k) # return first k documents (in ascending order by position)


    def _word_present(self, words, query):
        for word in words:
            if word in query: # at least one word of words is in the query: then return 1
                return 1
        return 0


    def _score_title(self, title, query):
        title_words = TextTools.pre_process(title).split(' ')
        return self._word_present(title_words, query)

    
    def _score_author(self, author, query):
        try:
            if author == None or author == '': # author missing
                return 0
            author_words = TextTools.pre_process(author).split(' ')
            return self._word_present(author_words, query)
        except:
            return 0 # something went wrong
    

    def _score_characters(self, characters, query):
        try:
            if characters == None or characters == '': # characters missing
                return 0
            characters_words = TextTools.pre_process(characters).split(' ')
            return self._word_present(characters_words, query)
        except:
            return 0 # something went wrong


    def _score_series(self, series, query):
        try:
            if series == None or series == '': # series missing
                return 0
            series_words = TextTools.pre_process(series).split(' ')
            return self._word_present(series_words, query)
        except:
            return 0 # something went wrong
    

    def _new_scoring_fun(self, dataset, top_k_docs, query, k):
        query_words = set(TextTools.pre_process(query).split(' ')) # keep unique words in the query
        for i in range(k):
            title_score = self._score_title(dataset.iloc[i]['bookTitle'], query_words) 
            author_score = self._score_author(dataset.iloc[i]['bookAuthors'], query_words)
            char_score = self._score_characters(dataset.iloc[i]['Characters'], query_words)
            series_score = self._score_series(dataset.iloc[i]['bookSeries'], query_words)
            new_score = round(-top_k_docs[i].doc_score[1] * 0.4 + title_score * 0.3 + \ 
                        author_score * 0.07 + char_score * 0.05 + series_score * 0.03 + \ 
                        (dataset.iloc[i]['ratingValue'] / 5 * (30001 - dataset.iloc[i]['file_num']) / 30000) * 0.15, 3) # linear combination of the scores
                        # as defined in the report
            top_k_docs[i].doc_score[1] = -new_score # make the score positive
        return self._top_k_docs(top_k_docs, k)