# -*- coding: utf-8 -*-

import abc
import os


class ABCManager:
    """Abstract class to read from/write to files. Different implementations
    should extend this class and override the abstract methods."""
    __metaclass__ = abc.ABCMeta

    @classmethod
    def __init__(self, filepath, workpath, tokenizer, stopwords):
        """Creates a new TEIManager for the given file path."""
        self._path = os.path.abspath(filepath)
        self._key = os.path.splitext(os.path.basename(self._path))[0]
        self._base_filepath = os.path.splitext(self._path)[0]
        self._work_path = os.path.abspath(workpath)
        self._tokenizer = tokenizer
        self._stopwords = stopwords
        self._texts = {}

    def get_texts(self):
        """Returns the dictionary of all the `Text` objects of the manager."""
        return self._texts

    def get_text(self, key):
        """Returns the text for the given key."""
        return self._texts[key]

    @abc.abstractmethod
    def extract_texts(self):
        """Extracts text sections from the current file and it creates a
        `Text` object for each one and adds it to the texts dictionary."""
        return
