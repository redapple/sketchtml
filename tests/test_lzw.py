#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sketchtml` package."""


import unittest

from sketchtml.lzw import fingerprint, hexfp


class TestLzw(unittest.TestCase):
    """Tests for `sketchtml.lzw` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_fingerprint(self):
        """Test Hachenberg & Gottron HTML tag sequence fingerprint."""

        test = '''html, body, p, b, b, p, p, strong, strong, p, p, big, big, p, p, em, em, p, p, i, i, p, p, small, small, p, p, sub, sub, sup, sup, p, body, html'''.split(', ')
        fp = fingerprint(test)
        self.assertListEqual(fp, [0, 0, 0, 0, 4, 3, 0, 3, 0, 9, 3, 0, 8, 0, 8, 0, 8, 0, 0, 19, 2])
        self.assertEqual(hexfp(fp), '000000000403000300090300080008000800001302')
