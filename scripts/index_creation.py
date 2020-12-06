import glob
import json
import math
import os

import nltk
import pandas as pd
from tqdm import tqdm # nice progress bar or 

from scripts.utilities import FileContentGetter, TextTools

# nltk.download('punkt')
# nltk.download('stopwords') 


class IndexBuilder:

    def __init__(self, vocabulary_path='./data/vocabulary.json', i_index_path='./data/inverted_index_2_1_1.json', \
                i_index_tfidf_path='./data/inverted_index_2_2_1.json'):
        
        self.vocabulary_path = vocabulary_path
        self.i_index_path = i_index_path
        self.i_index_tfidf_path = i_index_tfidf_path


    def concatenate_dataset(self, data_path, fields):
        """
        Read all the .tsv files, making use of the utility FileContentGetter, 
        and return a pandas.DataFrame containing all of them sorted by the file number
        """
        content_getter = FileContentGetter(data_path) # helper object to get the content of .tsv files
        article = content_getter.get(fields=fields, file_ext='tsv') # initialize article
        articles = []
        while article is not None: # content_getter.get() returns None if there are no more files
            articles.append(article) # list of DataFrames containing articles
            article = content_getter.get(fields=fields, file_ext='tsv') # get an article
        return pd.concat(articles).sort_values(by='file_num', ignore_index=True) # concatenate the DataFrames and sort them by article number


    def create_vocabulary(self, dataset):
        vocabulary = dict() # create the vocabulary as dictionary; convenient data structure to produce a JSON file as output 
        term_id = 0 # counter for term IDs
        for plot in dataset['Plot']:
            words_list = plot.split(' ') # split the plot into words
            for word in words_list:
                if word not in vocabulary: # a word is encountered for the very first time
                    vocabulary[word] = term_id # assign an ID to the word
                    term_id += 1 # increase ID
        with open(self.vocabulary_path, 'w') as vocabulary_file:
            json.dump(vocabulary, vocabulary_file) # save the vocabulary into a JSON file
                

    def create_index(self, dataset):
        with open(self.vocabulary_path, 'r') as vocabulary_file:
            vocabulary = json.load(vocabulary_file) # open the vocabulary and store it into a dictionary
        inverted_index = dict()
        for plot, document_id in zip(dataset['Plot'], dataset['file_num']):
            words_list = plot.split(' ') # list of words in plot 
            for word in words_list:
                if vocabulary[word] not in inverted_index: # a word is encoutnered for the very first time
                    inverted_index[vocabulary[word]] = [] # initialize the word's posting list
                inverted_index[vocabulary[word]].append(document_id) # append the document number to the posting list
        for key in inverted_index.keys():
            inverted_index[key] = sorted(list(set(inverted_index[key]))) # keep unique values into posting lists and sort them in ascending order
        with open(self.i_index_path, 'w') as index_file:
            json.dump(inverted_index, index_file) # dump the inverted index dictionary into a JSON file
            

    def create_index_tfidf(self, dataset):
        with open(self.vocabulary_path, 'r') as vocabulary_file:
            vocabulary = json.load(vocabulary_file)
        with open(self.i_index_path, 'r') as simple_i_index_file:
            simple_i_index = json.load(simple_i_index_file)
        with open('./data/precomputed/idf.json', 'r') as idf_file:
            idf = json.load(idf_file) # precomputed IDF
        i_index_tfidf = {key : [] for key in list(map(int, simple_i_index.keys()))} # create a dictionary with the keys of the first inverted index
        doc_magn = dict() # dictionary that is going to hold the documents' magnitude
        for plot, document_id in tqdm(zip(dataset['Plot'], dataset['file_num'])): # for each record (book)
            doc_magn[document_id] = 0 # initialize the magnitude 
            words_list = plot.split(' ') # split the plot into the list of its words
            plot_len = len(words_list)
            words = pd.Series(words_list, name='words_count').value_counts() # count the freaquency of each word
            for word, count in zip(words.index, words):
                tfidf = round(count / plot_len * idf[str(vocabulary[word])], 3) # compute the TF-IDF
                i_index_tfidf[vocabulary[word]].append([document_id, tfidf]) 
                doc_magn[document_id] += tfidf**2 # take the square of each component of the document vector (cfr. bag of words)
            doc_magn[document_id] = math.sqrt(doc_magn[document_id]) # compute the magnitude
        with open(self.i_index_tfidf_path, 'w') as index_file:
            json.dump(i_index_tfidf, index_file) # save the inverted index into a JSON file
        with open('./data/precomputed/doc_magnitude.json', 'w') as doc_magn_file:
            json.dump(doc_magn, doc_magn_file) # save the documents' magnitudes into a JSON file


    def store_idf(self, n_docs, i_idx_path, out_path): # compute and save the IDF of the words
        with open(i_idx_path, 'r') as i_idx_file:
            i_idx = json.load(i_idx_file)
        idf = dict()
        for key in tqdm(i_idx.keys()):
            idf[key] = round(math.log(n_docs / len(i_idx[key])), 3) # the number of document in which a word is present is equal to the length of its posting list
        with open(out_path, 'w') as out_file:
            json.dump(idf, out_file) # save the IDF of the words into a JSON file
