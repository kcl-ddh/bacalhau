# -*- coding: utf-8 -*-

from lxml import etree
from abc_manager import ABCManager
import re


class TEIManager(ABCManager):
    """Implementation of the abstract Manager class to work with TEI files."""

    XPATH = '//tei:body/tei:head//text()[not(ancestor::tei:note)]'

    def get_text(self):
        """Returns a list of strings, each representing a tei:body/tei:head
        element."""
        tree = etree.parse(self._path)
        text_list = tree.xpath(self.XPATH, namespaces=self.NS_MAP)
        text = ' '.join([text for text in text_list])
        text = re.sub(r'\s+', ' ', text)

        return text
