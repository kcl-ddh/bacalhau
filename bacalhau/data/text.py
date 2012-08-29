# -*- coding: utf-8 -*-

from nltk.corpus import wordnet
import nltk
import re

class Text(object):
    """Represents a text unit from a file managed by an `ABCManager`."""

    def __init__(self, key, filepath, content, tokenizer, stopwords):
        """Creates a new Text object."""
        self._key = key
        self._filepath = filepath
        self._content = content
        self._tokenizer = tokenizer
        self._stopwords = stopwords

        tokens = self.tokenize(content)
        tokens = self.prune_tokens(tokens)
        unique_tokens = sorted(list(set(tokens)))

        text_file = open(filepath, 'w')
        text_file.write('\n'.join(unique_tokens))
        text_file.close()

    def tokenize(self, text):
        """Returns a list of tokens, in lowercase, from the text."""
        return [t.lower() for t in self._tokenizer.tokenize(text)]

    def prune_tokens(self, tokens):
        """Returns a list of tokens without stopwords, punctuation and tokens
        that are not in WordNet."""
        pruned_tokens = []

        for token in tokens:
            if token in self._stopwords:
                continue

            if re.search(r'[^A-Za-z]', token):
                continue

            if not wordnet.synsets(token, pos=wordnet.NOUN):
                continue

            pruned_tokens.append(token)

        return pruned_tokens
