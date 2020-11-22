from scripts.data_collection import DataCollector


try:
    block = int(input('Provide a block of pages number to start from (counting from 0 to 2). Write -1 to collect all the pages:\t'))
except:
    print('Input not valid: not an integer!')
    exit(-1)

try:
    page = int(input('Provide a page number to start from (counting from 1 to 100):\t'))
except:
    print('Input not valid: not an integer!')
    exit(-1)

try:
    line = int(input('Provide a line number to start from (counting from 1 to 100).\
                    \nMind that this is an offset\
                    \n\nE.g.: if page number=100 and line number = 34, then start from 134th item:\t'))
except:
    print('Input not valid: not an integer!')
    exit(-1)

print('\n'*3)

dc = DataCollector(block_number=block, page_number=page, line_number=line)
dc.save_html_pages()
