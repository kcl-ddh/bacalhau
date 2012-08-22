# -*- coding: utf-8 -*-

import nltk
import os
import re


class TopicHierarchyGenerator(object):

    WORK_DIR = 'work'

    def __init__(self, corpuspath, manager,
            tokenizer=nltk.tokenize.regexp.WordPunctTokenizer(),
            stopwords=nltk.corpus.stopwords.words('english')):
        """Creates a new CorpusManager for the given path, using the given
        Manager to process the files."""
        self._path = os.path.abspath(corpuspath)
        self._manager = manager
        self._tokenizer = tokenizer
        self._stopwords = stopwords
        self._work_path = os.path.abspath(self.WORK_DIR)
        self._corpus = None
        self._textcollection = None

    def generate(self):
        """Generates topic tree: creates hypernym paths for the target terms,
        generates topic tree for the hypernym paths, compresses the topic
        tree."""
        self.extract()

        return

    def extract(self):
        """Extracts target tems from the texts: selects nouns, computes tf.idf,
        merges the target terms into a unique list."""
        self.prepare()

        self._corpus = nltk.corpus.PlaintextCorpusReader(self._work_path, '.*')
        #self._textcollection = nltk.text.TextCollection(self._corpus)

    def prepare(self):
        """Prepares the corpus for the topic tree generation: tokenizes each
        text, removes stop words, and removes unknown words."""
        try:
            os.mkdir(self.WORK_DIR)
        except OSError:
            pass

        for (path, dirs, files) in os.walk(self._path):
            for filename in files:
                manager = self._manager(os.path.join(path, filename))
                tokens = self.tokenize(manager.get_text())
                tokens = self.prune_tokens(tokens)
                work_file = open(os.path.join(self._work_path, filename), 'w')
                work_file.write('\n'.join(tokens))
                work_file.close()

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

            if not nltk.corpus.wordnet.synsets(token):
                continue

            pruned_tokens.append(token)

        return pruned_tokens
