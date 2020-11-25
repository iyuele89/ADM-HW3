import pandas as pd 
import glob
import os
from scripts.utilities import FileContentGetter


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

fg = FileContentGetter('./data/html/*/*.html')
print(fg.get(file_ext='html')[10000:10800])

