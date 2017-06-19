#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sketchtml` package."""


import unittest

from lxml import etree as ET

from sketchtml.tree import TreeHelper


class TestHelper(unittest.TestCase):
    """Tests tagpaths variations."""

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

    def setUp(self):
        """Set up test fixtures, if any."""
        self.helper = TreeHelper()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_make_tree(self):
        tree = self.helper.make_tree(self.sample)
        self.assertTrue(isinstance(tree, ET._ElementTree))


class TestTagPaths(unittest.TestCase):
    """Tests tagpaths variations."""

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

    def setUp(self):
        """Set up test fixtures, if any."""
        self.helper = TreeHelper()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_text_nodes_paths_default(self):
        """Test that helper returns text nodes paths by default."""
        tagpaths = list(self.helper.tagpaths(self.sample))
        self.assertListEqual(
            tagpaths,
            ['/html/head/title', '/html/body/h1', '/html/body/p[1]', '/html/body/p[1]/a', '/html/body/p[2]', '/html/body/p[2]/a']
        )

    def test_text_nodes_paths_positional_stripped(self):
        tagpaths = list(self.helper.tagpaths(self.sample, strip_positional=True))
        self.assertListEqual(
            tagpaths,
            ['/html/head/title', '/html/body/h1', '/html/body/p', '/html/body/p/a', '/html/body/p', '/html/body/p/a']
        )


class TestTagSequences(unittest.TestCase):
    """Tests tag sequences variations."""

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

    def setUp(self):
        """Set up test fixtures, if any."""
        self.helper = TreeHelper()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_tag_sequence_default(self):
        tagseq = list(self.helper.tagseq(self.sample))
        self.assertListEqual(
            tagseq,
            ['html', 'head', 'title', 'title', 'head', 'body', 'h1', 'h1', 'p', 'a', 'a', 'p', 'p', 'a', 'a', 'p', 'body', 'html']
        )

    def test_tag_sequence_closing_tags(self):
        tagseq = list(self.helper.tagseq(self.sample, with_closing=True))
        self.assertListEqual(
            tagseq,
            ['html', 'head', 'title', '!title', '!head', 'body', 'h1', '!h1', 'p', 'a', '!a', '!p', 'p', 'a', '!a', '!p', '!body', '!html']
        )
