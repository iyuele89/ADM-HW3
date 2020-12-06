import json
from scripts.utilities import TextTools
import heapq
import math
import pandas as pd



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



class SearchEngine:

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
        self.use_tfidf = use_tfidf
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


    def _search(self, query):
        query_words = list(set(TextTools.pre_process(query).split(' ')))
        query_len = len(query_words)
        try:
            posting_lists = [self.i_index[str(self.vocabulary[word])] for word in query_words]
        except:
            print('No results :(')
            return []
        documents = {k:1 for k in posting_lists[0]}
        for l in posting_lists[1:]:
            for doc in l:
                if doc in documents:
                    documents[doc] += 1
        return [k for k in documents if documents[k] == query_len]
        

    def _search_tfidf(self, query):
        query_words = list(set(TextTools.pre_process(query).split(' ')))
        query_len = len(query_words)
        try:
            posting_lists = [self.i_index[str(self.vocabulary[word])] for word in query_words]
        except:
            print('No results :(')
            return []
        documents = {k[0]:[k[1]] for k in posting_lists[0]}
        for l in posting_lists[1:]:
            for doc in l:
                if doc[0] in documents:
                    documents[doc[0]].append(doc[1])
        documents = {k:documents[k] for k in documents.keys() if len(documents[k]) == query_len}
        with open(self.doc_magnitude_path, 'r') as doc_magnitude_file:
            doc_magnitude = json.load(doc_magnitude_file)
        cosine_sim = lambda d_vec, d_mag: round(sum(d_vec) / d_mag, 3)
        return [DocScore([int(k), -cosine_sim(documents[k], doc_magnitude[str(k)])]) for k in documents]


    def _top_k_docs(self, doc_scores, k):
        heapq.heapify(doc_scores)
        len_scores = len(doc_scores)
        i = 0
        top_k_docs = []
        while i < k and i < len_scores:
            top_k_docs.append(heapq.heappop(doc_scores))
            i += 1
        return top_k_docs


    def search(self, query, dataset, k=10, new_score=False, additional_query=None):
        if self.use_tfidf:
            doc_scores = self._search_tfidf(query)
            top_k_docs = self._top_k_docs(doc_scores, k)
            if new_score:
                result = pd.DataFrame()
                for d in top_k_docs:
                    result = pd.concat([result, dataset[dataset['file_num']==d.doc_score[0]][['bookTitle', 'Plot', 'Url']]])
                top_k_docs = self._new_scoring_fun(result, top_k_docs, additional_query, k)
            result = pd.DataFrame()
            for d in top_k_docs:
                result = pd.concat([result, dataset[dataset['file_num']==d.doc_score[0]][['bookTitle', 'Plot', 'Url']]])
            result.loc[:, 'Similarity'] = [-d.doc_score[1] for d in top_k_docs]
            return result
        else:
            result = self._search(query)
            return dataset[dataset['file_num'].isin(result)][['bookTitle', 'Plot', 'Url']].head(10)

    def _word_present(self, words, query):
        for word in words:
            if word in query:
                return 1
        return 0

    def _score_title(self, title, query):
        title_words = TextTools.pre_process(title).split(' ')
        return self._word_present(title_words, query)

    
    def _score_author(self, author, query):
        try:
            if author == None or author == '':
                return 0
            author_words = TextTools.pre_process(author).split(' ')
            return self._word_present(author_words, query)
        except:
            print('Error author')
            return 0
    

    def _score_characters(self, characters, query):
        try:
            if characters == None or characters == '':
                return 0
            characters_words = TextTools.pre_process(characters).split(' ')
            return self._word_present(characters_words, query)
        except:
            return 0


    def _score_series(self, series, query):
        try:
            if series == None or series == '':
                return 0
            series_words = TextTools.pre_process(series).split(' ')
            return self._word_present(series_words, query)
        except:
            return 0
    

    def _new_scoring_fun(self, dataset, top_k_docs, query, k):
        query_words = set(TextTools.pre_process(query).split(' '))
        for i in range(k):
            title_score = self._score_title(dataset.iloc[i]['bookTitle'], query_words)
            author_score = self._score_author(dataset.iloc[i]['bookAuthors'], query_words)
            char_score = self._score_characters(dataset.iloc[i]['Characters'], query_words)
            series_score = self._score_series(dataset.iloc[i]['bookSeries'], query_words)
            new_score = round(-top_k_docs[i].doc_score[1] * 0.4 + title_score * 0.3 + \
                        author_score * 0.07 + char_score * 0.05 + series_score * 0.03 + \
                        (dataset.iloc[i]['ratingValue'] / 5 * (30001 - dataset.iloc[i]['file_num']) / 30000) * 0.15, 3) 
            top_k_docs[i].doc_score[1] = -new_score
        return self._top_k_docs(top_k_docs, k)
        



# engine = SearchEngine()
# engine.select_mode(use_tfidf=True)
# print(sorted(engine.search('survival games')))
# engine.test()


# l1 = [1,2,5,6,7,10,23,45]
# l2 = [1,3,4,7,12,17,23,44]

# # res = search(l1, l2)
# print([l2[i] for i in res[1]])


# d1 = DocScore([1, 0.4])
# d2 = DocScore([2, 0.8])
# d3 = DocScore([3, 0.3])
# print(sorted([d1,d2,d3]))
# arr = [d1,d2,d3]
# print(arr)
# heapq.heapify(arr)
# print(heapq.heappop(arr))
# print(heapq.heappop(arr))
# print(heapq.heappop(arr))
