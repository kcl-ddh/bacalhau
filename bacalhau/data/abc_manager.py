# -*- coding: utf-8 -*-

import abc
import os


class ABCManager:
    """Abstract class to read from/write to files. Different implementations
    should extend this class and override the abstract methods."""
    __metaclass__ = abc.ABCMeta

    TEI_NAMESPACE = 'http://www.tei-c.org/ns/1.0'
    XML_NAMESPACE = 'http://www.w3.org/XML/1998/namespace'
    NS_MAP = {'tei': TEI_NAMESPACE, 'xml': XML_NAMESPACE}

    @classmethod
    def __init__(self, filepath):
        """Creates a new TEIManager for the given file path."""
        self._path = os.path.abspath(filepath)

    @abc.abstractmethod
    def get_text(self):
        """Returns a list of strings representing the desired content extracted
        from the TEI document."""
        return
