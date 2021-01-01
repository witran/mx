from bs4 import BeautifulSoup
import time
from lxml import etree

TEXT_FILE = '.tmp/1911.02782.pdf.tei.xml'
# TEXT_FILE = '.tmp/test.html'


def is_ref(node):
    tag = node.tag.replace(ns, '')
    # print(tag, node.attrib['type'] if 'type' in node.attrib else None)
    return tag == 'ref' and 'type' in node.attrib and node.attrib['type'] == 'bibr' and 'target' in node.attrib


def is_text(node):
    tag = node.tag.replace(ns, '')
    return tag


ns = '{http://www.tei-c.org/ns/1.0}'


def process_file(file_name):
    start = time.time()
    stack = []
    refs = []

    tree = etree.parse(file_name)
    etree.tostring(tree.getroot())

    root = tree.getroot()
    for node in root.iter():
        if is_ref(node):
            text = node.text.strip()
            # print('ref', text.strip())
            if text:
                refs.append((len(stack), node.attrib['target'], text))
                stack.append(text)

        elif is_text(node) and node.text:
            text = node.text.strip()
            # print('text', text.strip())
            if text:
                stack.append(text)

    # [print(ref) for ref in refs]

    print('finished parsing text in {:.4f}'.format(time.time() - start))
    return refs


# text = process_file(TEXT_FILE)
# text = process_file_2(TEXT_FILE)
