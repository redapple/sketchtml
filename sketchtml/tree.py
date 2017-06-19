import re

from lxml import etree as ET
from lxml.html import fromstring, HtmlComment


_re_xpath_positional = re.compile('\[\d+\]')


class TreeHelper(object):

    tagpath_join = '/'
    tagseq_close = '!'

    def __init__(self, textonly=True, textpaths=False):
        self.textonly = textonly
        self.textpaths = textpaths

    @staticmethod
    def make_tree(text):
        return fromstring(text).getroottree()

    def tagpaths(self, text, strip_positional=False):
        tree = self.make_tree(text)
        if self.textonly:
            predicate = ('[not(self::script or self::style)]'
                         '[normalize-space(text())]')
        else:
            predicate = None
        for path in self._tagpaths(tree, predicate,
                                   strip_positional=strip_positional):
            yield path

    def tagseq(self, text, with_closing=False):
        tree = self.make_tree(text)
        for tag in self._tagseq(tree, with_closing=with_closing):
            yield tag

    def _tagpaths(self, tree, predicate, strip_positional=False):
        for leaf in tree.xpath('/descendant-or-self::*{}'.format(
                               predicate or '')):
            path = tree.getpath(leaf)
            if strip_positional:
                yield _re_xpath_positional.sub('', path)
            else:
                yield path

    def _tagseq(self, tree, with_closing=False):
        for action, e in ET.iterwalk(tree, events=("start", "end"),
                                     tag="*"):
            if isinstance(e, HtmlComment):
                continue
            if action == 'end' and with_closing:
                yield self.tagseq_close + e.tag
            else:
                yield e.tag
