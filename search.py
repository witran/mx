import cv2
# from .lib import parse_query
from lib.parse_query import get_query

FILE_PATTERN = '.tmp/crop_fixed.png'
FILE_TEXT = '.tmp/1911.02782.pdf.tei.xml'
# mx, my = (1078, 110)
mx, my = 1271, 120


def global_alignment_score(s1, s2):
    pass


def min_edit_alignment(pattern, text):
    # find a substring in text that has minimum edit distance to pattern
    pass


if __name__ == '__main__':
    queries = get_query(cv2.imread(FILE_PATTERN), mx, my)
    # [print(query) for query in queries]
    print(queries)
    text, bibs, refs = parse_text.get_text(FILE_TEXT)
