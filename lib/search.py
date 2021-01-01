import cv2
import math
import time
from . import parse_query, parse_text

FILE_PATTERN = './tmp/crop_fixed.png'
FILE_TEXT = './tmp/1911.02782.pdf.tei.xml'
MX, MY = 1271, 120


def global_alignment_score(s1, s2):
    n1 = len(s1) + 1
    n2 = len(s2) + 1
    f = [[0 for _ in range(n2)] for _ in range(n1)]
    for i in range(n1):
        f[i][0] = -i

    for i in range(n2):
        f[0][i] = -i

    for i in range(1, n1):
        for j in range(1, n2):
            f[i][j] = max(
                f[i][j - 1] - 1,
                f[i - 1][j] - 1,
                f[i - 1][j - 1] + (1 if s1[i - 1] == s2[j - 1] else -2))

    # [print(''.join(map(lambda v: str(v).ljust(4), f[i]))) for i in range(n1)]

    return f[n1 - 1][n2 - 1]


def min_edit_alignment(pattern, text):
    # find a substring in text that has minimum edit distance to pattern
    pass


def search(img, mx, my, file_name):
    start0 = time.time()
    queries = parse_query.get_queries(img, mx, my)
    # print('QUERIES')
    # [print(query) for query in queries]
    refs, bibs = parse_text.process_file(file_name)
    # print('REFS')
    # [print(ref) for ref in refs]
    if len(queries) == 0:
        print('empty queries')
        return

    if len(refs) == 0:
        print('empty refs')
        return

    best_score = -math.inf
    best_pair = None

    start = time.time()

    for query in queries:
        for ref in refs:
            _, _, ref_text = ref
            score = global_alignment_score(query, ref_text)
            # print(query, ':', ref_text, ':', score)
            # print('--------')

            if score > best_score:
                best_score = score
                best_pair = query, ref

    print('best score:', best_score)
    print('best pair:', best_pair)
    best_key = best_pair[1][1].replace('#', '')
    # print('-----------')
    # print('raw ref:', bibs[best_key])
    # print('-----------')
    print('alignment score computation time: {:.4f}s'.format(
        time.time() - start))
    print('total search time: {:.4f}s'.format(time.time() - start0))
    return bibs[best_key]


# search(cv2.imread(FILE_PATTERN), MX, MY, FILE_TEXT)
