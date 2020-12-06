import json
from utilities import TextTools
import heapq
import math

class DocScore:
    def __init__(self, doc_score:list):
        self.doc_score = doc_score

    def __lt__(self, other):
        return self.doc_score[1] < other.doc_score[1]
    
    def __le__(self, other):
        return self.doc_score[1] <= other.doc_score[1]

    def __eq__(self, other):
        return self.doc_score[0] == other.doc_score[0]

    def __repr__(self): 
        return str(self.doc_score)

    def __hash__(self):
        return hash(self.doc_score[0])


def binary_search(arr, x): 
    low = 0
    high = len(arr) - 1
    mid = 0
  
    while low <= high: 
  
        mid = (high + low) // 2
  
        # Check if x is present at mid 
        if arr[mid] < x: 
            low = mid + 1
  
        # If x is greater, ignore left half 
        elif arr[mid] > x: 
            high = mid - 1
  
        # If x is smaller, ignore right half 
        else: 
            return mid
  
    # If we reach here, then the element was not present 
    return -1


def common_el(l1, l2):
    result = ([], [])
    l = [l1, l2]
    idx_min = 0 if len(l1) < len(l2) else 1
    for i in range(len(l[idx_min])):
        j = binary_search(l[1 - idx_min], l[idx_min][i])
        if j != -1:
            result[idx_min].append(i)
            result[1 - idx_min].append(j)
    return result


class SearchEngine:

    def __init__(self, vocabulary_path='./data/vocabulary.json',\
                i_index_path='./data/inverted_index_2_1_1.json',\
                i_index_tfidf_path='./data/inverted_index_2_2_1.json',\
                doc_magnitude_path='./data/precomputed/doc_magnitude.json'
                ):
        with open(vocabulary_path, 'r') as vocabulary_file:
            self.vocabulary = json.load(vocabulary_file)
        self.i_index_path = i_index_path
        self.i_index_tfidf_path = i_index_tfidf_path
        self.doc_magnitude_path = doc_magnitude_path


    def select_mode(self, use_tfidf=False):
        if use_tfidf:
            with open(self.i_index_tfidf_path, 'r') as i_index_tfidf_file:
                self.i_index = json.load(i_index_tfidf_file)
        else:    
            with open(self.i_index_path, 'r') as i_index_file:
                self.i_index = json.load(i_index_file)

    
    # def search(self, query):
    #     query_words = TextTools.pre_process(query).split(' ')
    #     posting_lists = [self.i_index[str(self.vocabulary[word])] for word in query_words]
    #     idxs = []
    #     for i in range(len(posting_lists[0])):
    #         idxs.append([i])
    #         for l in posting_lists[1:]:
    #             j = 0
    #             found = False
    #             while posting_lists[0][i][0] <= l[j][0] and not found:
    #                 if posting_lists[0][i][0] == l[j][0]:
    #                     found = True
    #                     idxs[-1].append(j)
    #                 j += 1
    #             if not found:
    #                 idxs.pop()
    #                 break
    #     doc_vectors = {}
    #     print(idxs)
    #     for doc_idx in idxs:
    #         doc_vectors[posting_lists[0][doc_idx[0]][0]] = []
    #         for i in range(len(doc_idx)):
    #             doc_vectors[posting_lists[0][doc_idx[0]][0]].append(posting_lists[i][doc_idx[i]][1])
        
    #     print(doc_vectors)

        # # doc_set = set(self.i_index[str(self.vocabulary[query_words[0]])])
        # first_posting_list = self.i_index[str(self.vocabulary[query_words[0]])]
        # posting_lists = [self.i_index[str(self.vocabulary[word])] for word in query_words[1:]]
        # for num in first_posting_list:
        #     pass

        #     # doc_set.intersection_update(set(self.i_index[str(self.vocabulary[word])]))
        # # print(sorted(list(doc_set)))

    
    # def test(self):
        # doc_scores0 = set([DocScore(item) for item in self.i_index[str(self.vocabulary['surviv'])]])
        # doc_scores1 = set([DocScore(item) for item in self.i_index[str(self.vocabulary['game'])]])
        # doc_scores0.intersection_update(doc_scores1)
        # doc_scores = list(doc_scores0)
        # # print(doc_scores0)
        # heapq._heapify_max(doc_scores)
        # print(heapq._heappop_max(doc_scores))
        

    def search(self, query):
        query_words = TextTools.pre_process(query).split(' ')
        query_len = len(query_words)
        posting_lists = [self.i_index[str(self.vocabulary[word])] for word in query_words]
        documents = {k[0]:[k[1]] for k in posting_lists[0]}
        for l in posting_lists[1:]:
            for doc in l:
                if doc[0] in documents:
                    documents[doc[0]].append(doc[1])
        documents = {k:documents[k] for k in documents if len(documents[k]) == query_len}
        cosine_sim = lambda x: sum(x) / (sum([c**2 for c in x])**0.5 * query_len**0.5)
        doc_scores = [DocScore([int(k),-cosine_sim(documents[k])]) for k in documents]
        heapq.heapify(doc_scores)
        for k in range(5):
            print(heapq.heappop(doc_scores))

    


engine = SearchEngine()
engine.select_mode(use_tfidf=True)
engine.search('hunger games')
# engine.test()


# l1 = [1,2,5,6,7,10,23,45]
# l2 = [1,3,4,7,12,17,23,44]

# # res = search(l1, l2)
# print([l2[i] for i in res[1]])