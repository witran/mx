from bs4 import BeautifulSoup
import time

FILE_NAME = '.tmp/1911.02782.pdf.tei.xml'
# FILE_NAME = '.tmp/test.html'


def process_file():
    start = time.time()
    stack = []

    def visit(node):
        for child_node in node.children:
            pass

    with open(FILE_NAME, 'r') as f:
        soup = BeautifulSoup(f, 'lxml')
        print(soup.title)
        print(soup.descendants)
        for node in soup.descendants:
            if (not node.name and node.parent and node.parent.name != 'ref') or node.name == 'ref':
                text = str(node).strip()
                if text:
                    stack.append(text)

        print(stack)
        print(len(' '.join(stack)))
        # print(soup.body.findAll(text=True))
        # print(soup.body.findAll('body', recursive=True))
        # visit(soup.body)
        # children = soup.find('body', recursive=False).findChildren(
        #     '', recursive=False)
        # for child_node in children:
        #     print(child_node)
        # print(soup.body.find('div').findChildren())
        # print(soup.body.find('div').findAll(text=True))
        # print([node for node in soup.body.find('div').descendants])

        print(time.time() - start, 's')


process_file()
