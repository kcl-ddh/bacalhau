# -*- coding: utf-8 -*-

from corpus_manager import CorpusManager
import nltk
import os


class TEICorpusManager(CorpusManager):

    def __init__(self, corpuspath, manager, xpath,
            tokenizer=nltk.tokenize.regexp.WordPunctTokenizer(),
            stopwords=nltk.corpus.stopwords.words('english'),
            workpath=CorpusManager.WORK_DIR):
        """Creates a new TEICorpusManager for the given path, using the given
        document Manager to process the files."""
        super(TEICorpusManager, self).__init__(corpuspath, manager, tokenizer,
                stopwords, workpath)
        self._xpath = xpath

    def prepare(self):
        """Prepares the corpus for the topic tree generation."""
        try:
            os.mkdir(self._work_path)
        except OSError:
            pass

        for (path, dirs, files) in os.walk(self._path):
            for filename in files:
                manager = self._manager(os.path.join(path, filename),
                        self._work_path, self._tokenizer, self._stopwords,
                        self._xpath)
                texts = manager.extract_texts()

                for text in texts:
                    self._texts[text._key] = text
