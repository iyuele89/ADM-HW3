import os
import glob
import pandas as pd 



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
            return pd.read_table(next(self.__files_iter), usecols=fields, engine='c') # read the next .tsv file in __files_iter
        except:
            return None

    
    def __get_html(self):
        try:
            file_html = open(next(self.__files_iter), 'r') # open the next file in __files_iter
            html = ''.join(file_html.readlines()) # make a string conatining the whole content of the file
            file_html.close()
            return html
        except:
            return None

        
    def get_files_iter(self):
        return self.__files_iter # return the iterator containing all the files in __data_path


    def get(self, fields=None, file_ext='tsv'): # decide which routine call
        if file_ext == 'tsv': 
            return self.__get_tsv(fields)
        return self.__get_html()