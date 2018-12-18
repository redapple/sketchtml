from collections import defaultdict, deque, namedtuple
from io import BytesIO
import re

from lxml import etree as ET
from lxml.html import fromstring, HtmlComment


_re_xpath_positional = re.compile('\[\d+\]')


_Node = namedtuple('_Node', 'tag doc_order child_position attribs element')
class Node(_Node):
    def __hash__(self):
       return hash(self.element)


class TreeHelper(object):

    tagpath_prefix = '/'
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

    def iter_tagpaths(self, text, node_repr=lambda n: n.tag):
        for nodepath in self.iter_nodepaths(text):
            yield self.tagpath_prefix + self.tagpath_join.join(map(node_repr, nodepath))

    def iter_nodepaths(self, text, keep_element_refs=False):
        if not isinstance(text, bytes):
            text = text.encode('utf8')
        # a few state variables
        doc_order = 1
        # current path from root
        path = deque()
        # stack holding children counts per tag
        ancestors = deque()
        children_counts = defaultdict(int)
        ancestors.append(children_counts)
        for action, e in ET.iterparse(BytesIO(text),
                                      events=("start", "end"),
                                      tag="*",
                                      html=True, no_network=True):
            # we skip comments but they could hold some information
            if isinstance(e, HtmlComment):
                continue

            if action == 'start':
                tag = e.tag
                doc_order += 1
                children_counts[tag] += 1
                n = Node(e.tag,
                         doc_order=doc_order,
                         child_position=children_counts[tag],
                         attribs=dict(e.attrib),
                         element=e if keep_element_refs else None)
                path.append(n)
                if not self.textonly or e.text.strip():
                    yield tuple(path)

                children_counts = defaultdict(int)
                ancestors.append(children_counts)

            elif action == 'end':
                path.pop()
                ancestors.pop()
                children_counts = ancestors[-1]

    def tagseq(self, text, with_closing=False):
        tree = self.make_tree(text)
        for tag in self._tagseq(tree, with_closing=with_closing):
            yield tag

    def iter_tagseq(self, text, with_closing=False):
        if not isinstance(text, bytes):
            text = text.encode('utf8')
        for action, e in ET.iterparse(BytesIO(text),
                                      events=("start", "end"),
                                      tag="*",
                                      html=True, no_network=True):
            if isinstance(e, HtmlComment):
                continue
            if action == 'end' and with_closing:
                yield self.tagseq_close + e.tag
            else:
                yield e.tag

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
