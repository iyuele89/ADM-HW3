import pandas as pd 
import glob
import os
import nltk
from utilities import FileContentGetter
from sklearn.feature_extraction.text import TfidfVectorizer
import json


nltk.download('punkt')
nltk.download('stopwords') 

class TextTools:

    @staticmethod
    def tokenize(text):
        return nltk.word_tokenize(text)


    @staticmethod
    def alphanum(text:list): 
        text_result = []
        for w in text:
            if w.isalnum():
                text_result.append(w.lower())
        return text_result


    @staticmethod
    def stopword(text:list):
        text_result = []
        stop_words = nltk.corpus.stopwords.words('english')
        for w in text:
            if w not in stop_words:
                text_result.append(w)
        return text_result


    @staticmethod
    def stemming(text:list):
        stemmer = nltk.stem.PorterStemmer()
        return [stemmer.stem(w) for w in text]

    
    @staticmethod
    def pre_process(text:str):
        return ' '.join(TextTools.stemming(TextTools.stopword(TextTools.alphanum(TextTools.tokenize(text)))))


# class VocabularyBuilder:

#     def __init__(self):
#         pass


#     def __save_vocabulary(self, words_list, documents_list):
#         bag_of_words = pd.DataFrame({'words':words_list, 'documents':documents_list})
        
#         bag_of_words.to_json('./data/vocabulary.json')

    
#     def build_bag_of_words(self, data_path, fields):
#         content_getter = FileContentGetter(data_path)
#         dataframe, num_file = content_getter.get(fields=fields, file_ext='tsv')
#         words_list = []
#         documents_list = []
#         while dataframe is not None:
#             for field in fields:
#                 words_list += stemming(stopword(alphanum(tokenize(dataframe.at[0, field])))) # add text processing
#                 documents_list += [num_file]*len(words_list)
#             dataframe, num_file = content_getter.get(fields=fields, file_ext='tsv')
#         self.__save_vocabulary(words_list, documents_list)



class IndexBuilder:

    def __init__(self, vocabulary=None):
        self.count_vect = TfidfVectorizer(vocabulary=vocabulary, use_idf=True)


    def concatenate_dataset(self, data_path, fields):
        content_getter = FileContentGetter(data_path)
        article, _ = content_getter.get(fields=fields, file_ext='tsv')
        articles = []
        while article is not None:
            articles.append(article)
            article, _ = content_getter.get(fields=fields, file_ext='tsv')
        return pd.concat(articles, ignore_index=True)
    

    def vectorize_dataset(self, dataset):
        self.document_term_matrix = self.count_vect.fit_transform(dataset)


    def save_vocabulary(self, file_path='./data/vocabulary.json'):
        with open(file_path, 'w') as vocabulary:
            json.dump(self.count_vect.vocabulary_, vocabulary)


    def load_vocabulary(self, file_path='./data/vocabulary.json'):
        with open(file_path, 'r') as vocabulary:
            vocabulary = json.load(vocabulary)
            self.count_vect = TfidfVectorizer(vocabulary=vocabulary, use_idf=True)
    

    def __select_index_type(self, document_index, term_id, tfidf):
        if tfidf:
            self.inverted_index[term_id].append((document_index, self.document_term_matrix[document_index, term_id]))
        else:
            if self.document_term_matrix[document_index, term_id] != 0:
                    self.inverted_index[term_id].append(document_index)


    def save_inverted_index(self, file_path='./data/inverted_index_2_1_2.json', tfidf=False):
        self.inverted_index = dict()
        for term_id in range(self.document_term_matrix.shape[1]):
            self.inverted_index[term_id] = []
            for document_index in range(self.document_term_matrix.shape[0]):
                self.__select_index_type(document_index, term_id, tfidf)
        with open(file_path, 'w') as out_file:
            json.dump(self.inverted_index, out_file)



index_builder = IndexBuilder()

dataset = index_builder.concatenate_dataset('./data/tsv/*/*.tsv', ['Plot'])

dataset['Plot'] = dataset['Plot'].map(TextTools.pre_process)

index_builder.vectorize_dataset(dataset['Plot'])

index_builder.save_vocabulary()

index_builder.save_inverted_index()