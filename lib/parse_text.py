from bs4 import BeautifulSoup
import time
from lxml import etree

TEXT_FILE = '.tmp/1911.02782.pdf.tei.xml'
# TEXT_FILE = '.tmp/test.html'


def is_ref(node):
    tag = node.tag.replace(tag_ns, '')
    # print(tag, node.attrib['type'] if 'type' in node.attrib else None)
    return tag == 'ref' and 'type' in node.attrib and node.attrib['type'] == 'bibr' and 'target' in node.attrib


def is_text(node):
    tag = node.tag.replace(tag_ns, '')
    return tag


def is_bib(node):
    tag = node.tag.replace(tag_ns, '')
    return tag == 'biblStruct'


tag_ns = '{http://www.tei-c.org/ns/1.0}'
attr_ns = '{http://www.w3.org/XML/1998/namespace}'


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

    bibs = {}
    listTagName = tag_ns + 'listBibl'
    rawRefTagName = tag_ns + 'note'
    idAttrName = attr_ns + 'id'

    for node in root.iter():
        if node.tag == listTagName:
            for b in list(node):
                raw = None
                for elem in list(b):
                    # print(elem.attrib)
                    if elem.tag == rawRefTagName and 'type' in elem.attrib and elem.attrib['type'] == 'raw_reference':
                        raw = elem.text
                        break
                bibs[b.attrib[idAttrName]] = raw
            break
    # [print(ref) for ref in refs]
    # [print(k, ':', bibs[k]) for k in bibs]

    print('finished parsing text in {:.4f}'.format(time.time() - start))
    return refs, bibs


# text = process_file(TEXT_FILE)
