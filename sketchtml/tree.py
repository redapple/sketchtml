import re

from lxml import etree as ET
from lxml.html import fromstring, HtmlElement, HtmlComment


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
            predicate = '[not(self::script or self::style)][normalize-space(text())]'
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
        for leaf in tree.xpath('/descendant-or-self::*{}'.format(predicate or '')):
            path = tree.getpath(leaf)
            if strip_positional:
                yield _re_xpath_positional.sub('', path)
            else:
                yield path

    def _tagseq(self, tree, with_closing=False):
        for action, e in ET.iterwalk(tree, events=("start", "end"), tag="*"):
            if isinstance(e, HtmlComment):
                continue
            if action=='end' and with_closing:
                yield self.tagseq_close + e.tag
            else:
                yield e.tag


if __name__ == '__main__':
    sample = '''<!DOCTYPE html>
<html>
  <head>
    <title>Sample page</title>
  </head>
  <body>
    <h1>Sample page</h1>
    <p>This is a <a href="demo.html">simple</a> sample.</p>
    <p>This is another <a href="foo.html">simple</a> paragraph!</p>
    <!-- this is a comment -->
  </body>
</html>'''
    helper = TreeHelper()
    tree = helper.make_tree(sample)
    assert isinstance(tree, ET._ElementTree)

    # default is to consider only text nodes
    tagpaths = list(helper.tagpaths(sample))
    assert tagpaths == ['/html/head/title', '/html/body/h1', '/html/body/p[1]', '/html/body/p[1]/a', '/html/body/p[2]', '/html/body/p[2]/a'], tagpaths

    tagpaths = list(helper.tagpaths(sample, strip_positional=True))
    assert tagpaths == ['/html/head/title', '/html/body/h1', '/html/body/p', '/html/body/p/a', '/html/body/p', '/html/body/p/a'], tagpaths

    helper = TreeHelper(textonly=False)
    tagpaths = list(helper.tagpaths(sample))
    assert tagpaths == ['/html', '/html/head', '/html/head/title', '/html/body', '/html/body/h1', '/html/body/p[1]', '/html/body/p[1]/a', '/html/body/p[2]', '/html/body/p[2]/a'], tagpaths

    helper = TreeHelper()
    tagseq = list(helper.tagseq(sample))
    assert tagseq == ['html', 'head', 'title', 'title', 'head', 'body', 'h1', 'h1', 'p', 'a', 'a', 'p', 'p', 'a', 'a', 'p', 'body', 'html'], tagseq

    tagseq = list(helper.tagseq(sample, with_closing=True))
    assert tagseq == ['html', 'head', 'title', '!title', '!head', 'body', 'h1', '!h1', 'p', 'a', '!a', '!p', 'p', 'a', '!a', '!p', '!body', '!html'], tagseq
