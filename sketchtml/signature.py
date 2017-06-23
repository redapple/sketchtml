# -*- coding: utf-8 -*-
import hashlib
from itertools import groupby

from sketchtml.tree import TreeHelper


def mailhash(html):
    helper = TreeHelper()
    text_paths = helper.tagpaths(html)
    m = hashlib.md5()
    m.update(' '.join(text_paths).encode('utf-8'))
    return m.digest()[-8:]


def stripped_xpath_list(html):
    helper = TreeHelper()
    text_paths = helper.tagpaths(html, strip_positional=True)
    return [x[0] for x in groupby(text_paths)]
