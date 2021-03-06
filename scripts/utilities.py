import os
import glob
import pandas as pd 
import nltk


class FileContentGetter:
    """
    This class is a general-purpose helper to get the content of a file.
    The methods implemented so far handle the content of .html files
    or .tsv files. Other methods will be added if needed.

    The public API is:
        - FileContentGetter(data_path)
            *   data_path: this parameter is a string corresponding to the path
                to the requested data. It is compliant to the path format of the 
                Python library 'glob'. E.g.:
                    ./root_dir/*/*.html gets all the files of type .html
                    in any directory within root_dir/
        - get_files_iter(): get the iterator of the files in the data path provided.
            It is a wrapper to glob.iglob.(data_path)
        - get(fields, file_ext): get the file content of the files with the specified 
            extension
            *   fields: for .tsv only, specify the fields (columns) to get from the file
            *   file_ext: file type to handle
    """
    
    def __init__(self, data_path):
        self.__data_path = data_path # save the data_path for further usage
        self.__files_iter = glob.iglob(data_path) # save the iterator of the files in the data_path

    
    def __get_tsv(self, fields=None) -> pd.DataFrame: # return DataFrame or None if __files_iter is empty
        try:
            data_path = next(self.__files_iter)
            file_num = data_path[-9:-4]
            file_content = pd.read_table(data_path, usecols=fields, engine='c', delimiter='\t') # read the next .tsv file in __files_iter
            file_content['file_num'] = [int(file_num)]
            return file_content
        except:
            return None

    
    def __get_html(self):
        try:
            file_path = next(self.__files_iter) # get the file path
            dir_num = file_path.split('/')[-2] # extract the folder number from the file path
            file_num = file_path[-10:-5] # extract the file number from the file path
            file_html = open(file_path, 'r') # open the next file in __files_iter
            html = ''.join(file_html.readlines()) # make a string concatenating the whole content of the file
            file_html.close()
            return html, dir_num, file_num
        except:
            return None, None, None # there are no more files to return

        
    def get_files_iter(self):
        return self.__files_iter # return the iterator containing all the files in __data_path


    def get(self, fields=None, file_ext='tsv'): # decide which routine call
        if file_ext == 'tsv': 
            return self.__get_tsv(fields)
        return self.__get_html()




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