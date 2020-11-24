import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm
import datetime

driver = None

## Try to import Chrome driver or Firefox driver
try:
    import chromedriver_binary  
    from selenium.webdriver.chrome.options import Options
    options = Options()                                 # change some default options of the web browser
    options.headless = True                             # avoid opening a browser window
    options.add_argument('--window-size=1920,1200')     # set a fake window
    driver = webdriver.Chrome(options=options)          # get a Chrome driver with custom options
except ImportError:
    from webdriver_manager.firefox import GeckoDriverManager 
    from selenium.webdriver.firefox.options import Options
    options = Options()                                 # change some default options of the web browser
    options.headless = True                             # avoid opening a browser window
    options.add_argument('--window-size=1920,1200')     # set a fake window
    driver = webdriver.Firefox(options=options)         # get a Firefox driver with custom options                                     
except:
    print('Web driver not supported!')



class DataCollector:
    """
    This class collects and saves the html pages, after reading the corresponding urls 
    from a txt file.
        - create DataCollector(block_number, page_number, line_number)
            Since the number of pages is equal to 300, 
            there are 3 blocks of 100 pages each.
            Each page contains 100 books.
            Specify:
                * block number: set the block of pages to retrieve
                * page number: 0 to collect all the pages within a block
                * line number: 0 to collect all the books within a page
                * all_pages: True to collect all the pages from 0 to 300
    """
    
    def __init__(self, block_number=0, page_number=0, line_number=0, all_pages=False):
        self.block_number = block_number # block number: 0 -> pages in range 1-100, 1 -> in range 101-200, 2 -> in range 201-300
        self.page_number = page_number # page number: inside a block, offset 0-99; e.g. page 134 -> block_number=1 * 100 + page_number=34
        self.line_number = line_number # line_number: inside a page, offset 0-99; e.g. 57th book inside a page
        self.root_dir = './data/' # root directory to the data
        self.html_dir = os.path.join(self.root_dir, f'html/{self.block_number * 100 + self.page_number}') # directory for html files
        self.all = all_pages


    def __make_dir(self, dir_number):
        self.html_dir = os.path.join(self.root_dir, f'html/{dir_number}')
        if not os.path.isdir(self.html_dir):
            os.mkdir(self.html_dir)


    def __save_html_pages(self, start_from, stop_at):
        """
        Start collecting from line start_from and stop at line stop_at.
        """
        with open(os.path.join(self.root_dir, 'url_list.txt'), 'r') as urls_file:
            try:
                urls = urls_file.readlines()[start_from : ] # select the line from which start collecting
            except:
                print('Error: reached file end!')
                exit(-1)
            for url, i in zip(urls, tqdm(range(start_from, stop_at))): # 
                if i % 100 == 0:
                    self.__make_dir(i // 100 + 1)
                try:
                    driver.get(url)
                    page_html = driver.page_source
                    with open(os.path.join(self.html_dir, f'article_{i + 1:05d}.html'), 'w') as out_file:
                        out_file.write(page_html)
                except:
                    with open('./log/log.csv', 'a') as log:
                        log.write(f'[{datetime.datetime.now()}], {i+1}, {url}\n')
                    continue
            driver.close()


    def get_html_pages(self): 
        """
        Save the html pages. Collect all pages if self.all is True. 
        Otherwise, compute the offsets for the requested chunk of books:
            - start_from:
                * each block contains 100 pages
                * each page contains 100 books (urls)
                Point to the requested URL inside the urls_file.txt
            - stop_at: 
                Stop at the end of the specified block
        """
        start_from = 0 if self.all else (self.block_number * 100 + self.page_number) * 100 + self.line_number # line from which start collecting 
        stop_at = 30000 if self.all else (100 - self.page_number) * 100 - self.line_number + start_from # line at which stop collecting
        self.__save_html_pages(start_from, stop_at)