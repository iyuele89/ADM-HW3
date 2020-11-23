import pandas as pd 
import glob
import os


class FileContentGetter:
    
    def __init__(self, data_path, file_ext='tsv'):
        self.__data_path = data_path
        self.__files_iter = glob.iglob(data_path)

    
    def get_files_iter(self):
        return self.__files_iter

    
    def __get_tsv(self, fields=None) -> pd.DataFrame:
        try:
            return pd.read_table(next(self.__files_iter), usecols=fields, engine='c')
        except:
            return None

    
    def __get_html(self):
        try:
            file_html = open(next(self.__files_iter), 'r')
            html = ''.join(file_html.readlines())
            file_html.close()
            return html
        except:
            return None


    def get(self, fields=None, file_ext='tsv'):
        if file_ext == 'tsv':
            return self.__get_tsv(fields)
        return self.__get_html()


class VocabularyBuilder:

    def __init__(self):
        self.__bag_of_words = set()


    def __save_vocabulary(self):
        print(self.__bag_of_words)

    
    def build_bag_of_words(self, data_path, fields):
        content_getter = FileContentGetter(data_path)
        dataframe = content_getter.get(fields=fields)
        while dataframe != None:
            for field in fields:
                words_list = (dataframe.at[0, field]).split(' ')
                self.__bag_of_words.update(words_list)
        self.__save_vocabulary()

    

vb = VocabularyBuilder()
vb.build_bag_of_words('../test.txt', fields=['Setting',])

fg = FileContentGetter('../test.tsv')
print(fg.get(fields=['Setting',]))