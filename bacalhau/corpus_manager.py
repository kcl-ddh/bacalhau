# -*- coding: utf-8 -*-

from operator import itemgetter
import nltk
import os
import pickle


class CorpusManager(object):

    WORK_DIR = 'work'

    def __init__(self, corpuspath, manager,
            tokenizer=nltk.tokenize.regexp.WordPunctTokenizer(),
            stopwords=nltk.corpus.stopwords.words('english'),
            workpath=WORK_DIR):
        """Creates a new CorpusManager for the given path, using the given
        document Manager to process the files."""
        self._path = os.path.abspath(corpuspath)
        self._manager = manager
        self._tokenizer = tokenizer
        self._stopwords = stopwords
        self._work_path = os.path.abspath(workpath)
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
        self._textcollection = nltk.text.TextCollection(self._corpus)

        for f in self._corpus.fileids():
            tf_idf_dict = {}

            for w in self._corpus.words(fileids=f):
                tf_idf_dict[w] = self._textcollection.tf_idf(w,
                        self._textcollection)

            tf_idf_dict = sorted(tf_idf_dict.iteritems(), key=itemgetter(1),
                    reverse=True)

            tf_idf_file = open(os.path.join(self._work_path, f + '-tf_id.pkl'),
                'wb')
            pickle.dump(tf_idf_dict, tf_idf_file)
            tf_idf_file.close()

            hypernyms_dict = {}

            for idx, item in enumerate(tf_idf_dict):
                word = item[0]
                hypernyms_dict[word] = []

                if idx >= 10:
                    break

                synsets = nltk.corpus.wordnet.synsets(word)

                while len(synsets) > 0:
                    syn = synsets[0]
                    name = syn.name
                    hypernyms_dict[word].append(name[:name.find('.')])
                    synsets = syn.hypernyms()

            hypernyms_file = open(os.path.join(self._work_path,
                f + '-syn.pkl'), 'wb')
            pickle.dump(hypernyms_dict, hypernyms_file)
            hypernyms_file.close()

    def prepare(self):
        """Prepares the corpus for the topic tree generation."""
        try:
            os.mkdir(self._work_path)
        except OSError:
            pass

        for (path, dirs, files) in os.walk(self._path):
            for filename in files:
                manager = self._manager(os.path.join(path, filename),
                        self._work_path)
                manager.extract_texts()
