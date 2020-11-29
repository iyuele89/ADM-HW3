import os
from bs4 import BeautifulSoup as bs
import re
from utilities import FileContentGetter
import pandas as pd



def book_scraping(html_source): # this takes the html content and returns a list with the useful info
    soup = bs(html_source, features='lxml')    
    bookTitle = soup.find_all('h1', id='bookTitle')[0].contents[0].strip()
    bookSeries = ''
    try:
        bookSeries = soup.find_all('h2', id='bookSeries')[0].contents[1].contents[0].strip()[1:-1]
    except Exception:
        pass
    bookAuthors = soup.find_all('span', itemprop='name')[0].contents[0].strip()
    descr = soup.find_all('div', id='description')[0].contents
    descr_fil= list(filter(lambda s: s!='\n', descr))
    if len(descr_fil) == 1:
        Plot = ''.join(descr_fil[0].contents[0])
    else:
        descr_fil = descr_fil[1:-1]
        x = [j for i in descr_fil for j in i.contents if (isinstance(j, str)==True)]
        Plot = ''.join(x)
    NumberofPages = soup.find_all('span', itemprop='numberOfPages')[0].contents[0].split()[0]
    ratingValue = soup.find_all('span', itemprop='ratingValue')[0].contents[0].strip()
    ratings_reviews = soup.find_all('a', href='#other_reviews')
    for i in ratings_reviews:
        if i.find_all('meta',itemprop='ratingCount'):
            ratingCount = i.contents[2].split()[0]
        if i.find_all('meta',itemprop='reviewCount'):
            reviewCount = i.contents[2].split()[0]
    pub = soup.find_all('div', class_='row')[1].contents[0].split()[1:4]
    Published = ' '.join(pub)
    char = soup.find_all('a', href=re.compile('characters')) # find the regular expression(re) 'characters' within the attribute href 
    if len(char) == 0:
         Characters = ''
    else:
        Characters = ', '.join([i.contents[0] for i in char])
    sett = soup.find_all('a', href=re.compile('places')) # find the regular expression(re) 'places' within the attribute href 
    if len(sett) == 0:
        Setting = ''
    else:
        Setting = ', '.join([i.contents[0] for i in sett])
    Url = soup.find_all('link', rel='canonical')[0].get('href')
    return [bookTitle, bookSeries, bookAuthors, ratingValue, ratingCount, reviewCount, Plot, NumberofPages, Published, Characters, Setting, Url]


# for i in range(1, 301):
#     new_dir = f'./data/tsv/{i}' 
#     if not os.path.isdir(new_dir):
#         os.mkdir(new_dir)


content_getter = FileContentGetter('./data/html/*/*.html')
fields = ['bookTitle', 'bookSeries', 'bookAuthors', 'ratingValue', 'ratingCount', 'reviewCount', 'Plot', 'NumberofPages', 'Published', 'Characters', 'Setting', 'Url']
while True:
    html_content, dir_num, file_num = content_getter.get(file_ext='html')
    if html_content is None:
        break
    try:
        book_info = book_scraping(html_content)
    except:
        with open('./log/log_tsv.txt', 'a') as log:
            log.write(f'html/{dir_num}/article_{file_num}.html')
        continue
    book_info = [field.replace('\n', ' ') for field in book_info]
    data = dict.fromkeys(fields)
    for field, info in zip(fields, book_info):
        data[field] = [info]
    book_info_df = pd.DataFrame(data)
    book_info_df.to_csv('./data/tsv/' + dir_num + '/article_' + file_num + '.tsv', sep='\t', index=False)


# content_getter = FileContentGetter('./data/html/1/article_00001.html')
# html_content, _, _ = content_getter.get(file_ext='html')
# print(book_scraping(html_content))
