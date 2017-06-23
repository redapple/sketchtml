#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sketchtml` package."""

from binascii import hexlify
import unittest

from sketchtml.signature import mailhash, stripped_xpath_list


class TestMailHash(unittest.TestCase):
    """Tests MailHash signature on ordered list of XPaths to text nodes."""

    sample = u'''<!DOCTYPE html>
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

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_basic(self):
        self.assertEqual(hexlify(mailhash(self.sample)), b'5853cb2f58a23451')


class TestStrippedXPaths(unittest.TestCase):
    """
    Tests stripped-XPaths from "Structural Clustering of
    Machine-Generated Mail".
    """

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_basic(self):
        sample = u'''<!DOCTYPE html>
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
        self.assertListEqual(stripped_xpath_list(sample),
                             ['/html/head/title',
                              '/html/body/h1',
                              '/html/body/p',
                              '/html/body/p/a',
                              '/html/body/p',
                              '/html/body/p/a'])


    def test_repeating_paragraphs(self):
        sample = u'''<!DOCTYPE html>
<html>
  <head>
    <title>Sample page</title>
  </head>
  <body>
    <h1>Sample page</h1>
    <p>This is a simple sample.</p>
    <p>This is another simple paragraph!</p>
    <!-- this is a comment -->
  </body>
</html>'''
        self.assertListEqual(stripped_xpath_list(sample),
                             ['/html/head/title',
                              '/html/body/h1',
                              '/html/body/p'])

    def test_table_rows(self):
        sample = u'''<!DOCTYPE html>
<html>
  <head>
    <title>Sample page</title>
  </head>
  <body>
    <h1>Awesome header!</h1>
    <p>Some cool text ;-)</>
    <table>
      <tr>
        <td>John</td>
        <td>Doe</td>
      </tr>
      <tr>
        <td>Jane</td>
        <td>Doe</td>
      </tr>
    </table>
  </body>
</html>'''
        self.assertListEqual(stripped_xpath_list(sample),
                             ['/html/head/title',
                              '/html/body/h1',
                              '/html/body/p',
                              '/html/body/table/tr/td'])
