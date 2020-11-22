from scripts.data_collection import DataCollector


all_pages = input('Collect all the pages? (Write n to select a specific range) [y/n]:\t')


if all_pages == 'y':
    print('\n'*3)
    dc = DataCollector(all_pages=True)
    dc.get_html_pages()
    
else:
    try:
        block = int(input('\nProvide a block of pages number to start from (counting from 0 to 2):\t'))
    except:
        print('Input not valid: not an integer!')
        exit(-1)

    try:
        page = int(input('\nProvide a page number to start from (counting from 0 to 99):\t'))
    except:
        print('Input not valid: not an integer!')
        exit(-1)

    try:
        line = int(input('\nProvide a line number to start from (counting from 0 to 99):\t'))
    except:
        print('Input not valid: not an integer!')
        exit(-1)
    print('\n'*3)
    dc = DataCollector(block_number=block, page_number=page, line_number=line)
    dc.get_html_pages()
