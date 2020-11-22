import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm

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
    from a txt file. There are two ways of usage:
        - call DataCollector(block_number, page_number, line_number) 
    """
    def __init__(self, block_number, page_number, line_number):
        self.block_number = block_number # block number: 0 -> pages in range 1-100, 1 -> in range 101-200, 2 -> in range 201-300
        self.page_number = page_number # page number: inside a block, offset 0-99; e.g. page 134 -> block_number=1 * 100 + page_number=34
        self.line_number = line_number # line_number: inside a page, offset 0-99; e.g. 57th book inside a page
        self.root_dir = './data/' # root directory to the data
        self.html_dir = os.path.join(self.root_dir, f'html/{self.block_number * 100 + self.page_number}') # directory for html files


    def __make_dir(self, dir_number):
        self.html_dir = os.path.join(self.root_dir, f'html/{dir_number}')
        if not os.path.isdir(self.html_dir):
            os.mkdir(self.html_dir)


    def save_html_pages(self):
        with open(os.path.join(self.root_dir, 'url_list.txt'), 'r') as urls_file:
            start_from = (self.block_number * 100 + self.page_number) * 100 + self.line_number
            end_after = (100 - self.page_number) * 100 + (100 - self.line_number) + start_from
            try:
                urls = urls_file.readlines()[start_from : ]
            except:
                print('Error: reached file end')
                exit(-1)
            for url, i in tqdm(zip(urls, range(start_from, end_after))):
                if i % 100 == 0:
                    self.__make_dir(i)
                driver.get(url)
                page_html = driver.page_source
                with open(os.path.join(self.html_dir, f'{i % 100 + 1}.html'), 'w') as out_file:
                    out_file.write(page_html)
            driver.close()
