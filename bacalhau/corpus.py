from collections import defaultdict
from math import log
import os

import nltk

from bacalhau.topic_tree import TopicTree


class Corpus(object):
    """A manager class to generate topic hierarchies from files."""

    def __init__(self, corpus_path, document_class,
            tokenizer=nltk.tokenize.regexp.WordPunctTokenizer(),
            stopwords=nltk.corpus.stopwords.words('english'),
            **document_kwargs):
        """Creates a new `.Corpus` for the given path, using the given
        `bacalhau.document.Document` class to process the files.

        :param corpus_path: path to the files.
        :type corpus_path: `str`
        :param document_class: document class used to process the
            corpus files.
        :type document_class: `bacalhau.document.Document`
        :param tokenizer: tokenizer used to tokenize the files in the
            corpus, defaults to
            `nltk.tokenize.regexp.WordPunctTokenizer`.
        :type tokenizer: `nltk.tokenize.api.TokenizerI`
        :param stopwords: words to be removed from the texts, defaults
            to `nltk.corpus.stopwords.words(\'english\')`.
        :type stopwords: `list`
        """
        self._corpus_path = os.path.abspath(corpus_path)
        self._document_class = document_class
        self._tokenizer = tokenizer
        self._stopwords = stopwords
        self._document_kwargs = document_kwargs
        self._documents = self._get_documents()
        # Total number of texts (not documents) in the corpus.
        self._text_count = self._get_text_count()
        self._hypernyms = None
        self._tree = None

    def _get_documents(self):
        """Creates a `bacalhau.document.Document` object for each
        of the files in the corpus, and returns them in a `list`.

        :param corpus_path: path to the corpus files.
        :type corpus_path: `str`
        :returns: documents in this corpus.
        :rtype: `list`
        """
        documents = []

        for (path, dirs, files) in os.walk(self._corpus_path):
            for filename in files:
                document = self._document_class(
                        os.path.join(path, filename), self._tokenizer,
                        self._stopwords, **self._document_kwargs)
                documents.append(document)

        return documents

    def _get_text_count(self):
        """Returns the number of `bacalhau.text.Text` objects in this
        corpus.

        :rtype: `float`
        """
        count = 0

        for document in self._documents:
            count += document.get_text_count()

        return float(count)

    def generate_topic_tree(self, n_terms):
        """Generates a `bacalhau.topic_tree.TopicTree` for the corpus,
        using a maximum of `n_terms` from each
        `bacalhau.text.Text`. First extracts top terms; second gets
        hypernyms for each of the terms; third creates the
        `bacalhau.topic_tree.TopicTree` using the hypernyms.

        :param n_terms: maximum number of terms to be used from each
            `Text`.
        :type n_terms: `int`
        :returns: the generated topic tree.
        :rtype: `bacalhau.topic_tree.TopicTree`
        """
        top_terms = self.get_top_terms(n_terms)
        hypernyms = self.get_hypernyms(top_terms)
        tree = self.get_topic_tree(hypernyms)

        self._hypernyms = hypernyms
        self._tree = tree

        return tree

    def get_top_terms(self, n_terms):
        """Returns a dictionary with the highest `n_terms` for each
        `bacalhau.text.Text` from the term data dictionary.

        :param n_terms: maximum number of terms to be used from each
            text.
        :type n_terms: `int`
        :returns: `dict`
        """
        term_data = self._add_tf_idf(self._get_term_data())
        top_terms = defaultdict(list)
        top_terms_meta = defaultdict(dict)

        for term, data in term_data.iteritems():
            for text, v in data.iteritems():
                count = len(top_terms[text])
                tf_idf = v['tf.idf']

                if count < n_terms:
                    top_terms[text].append(term)
                    top_terms_meta[text][tf_idf] = term
                else:
                    lower_tf_idf = sorted(top_terms_meta[text])[0]

                    if tf_idf > lower_tf_idf:
                        lower_term = top_terms_meta[text][lower_tf_idf]
                        top_terms[text].remove(lower_term)
                        top_terms[text].append(term)
                        top_terms_meta[text].pop(lower_tf_idf)
                        top_terms_meta[text][tf_idf] = term

        return top_terms

    def _get_term_data(self):
        """Returns term data for all of the
        `bacalhau.document.Document` objects in this corpus.

        :rtype: `dict`
        """
        term_data = defaultdict(dict)
        for document in self._documents:
            document_term_data = document.get_term_data()
            for term, new_term_data in document_term_data.items():
                term_data[term].update(new_term_data)

        return term_data

    def _add_tf_idf(self, term_data):
        """Returns `term_data` with a TF.IDF value added to each
        term/text combination.

        :param term_data: dict with term/text combination.
        :type term_data: `dict`
        :rtype: `dict`
        """
        for term, text_frequencies in term_data.items():
            # Number of texts containing the term.
            matches = len(text_frequencies)
            idf = log(self._text_count / matches)
            for text, text_data in text_frequencies.items():
                text_data['tf.idf'] = text_data['frequency'] * idf

        return term_data

    def get_hypernyms(self, top_terms):
        """Returns a dictionary with the hypernyms for the given terms.

        :param top_terms: dict with term/text information.
        :type top_terms: `dict`
        :returns: {text: {term: hypernym}}.
        :rtype: `dict`
        """
        hypernyms = defaultdict(dict)
        cache = {}

        for text, terms in top_terms.iteritems():
            for term in terms:
                h = cache.get(term)

                if h is None:
                    h = self._get_hypernym(term)
                    h.reverse()
                    cache[term] = h

                hypernyms[text][term] = h

        return hypernyms

    def _get_hypernym(self, word):
        """Returns a list of the hypernyms for the given word.

        :param word: the word to get the hypernym for.
        :type word: `str`
        :rtype: `list`
        """
        hypernym = [word]

        synsets = nltk.corpus.wordnet.synsets(word)
        while len(synsets) > 0:
            s = synsets[0]
            hypernym.append(s.name)
            synsets = s.hypernyms()

        return hypernym

    def get_topic_tree(self, hypernyms):
        """Generates and returns a `bacalhau.topic_tree.TopicTree` for
        the given hypernyms.

        :param hypernyms: dictionary of hypernyms.
        :type hypernyms: `dict`
        :rtype: `bacalhau.topic_tree.TopicTree`
        """
        tree = TopicTree()

        for text, data in hypernyms.iteritems():
            for term, hypernym in data.iteritems():
                tree.add_nodes_from(hypernym)
                tree.node[hypernym[len(hypernym) - 1]]['is_leaf'] = True
                tree.node[hypernym[0]]['is_root'] = True
                tree.add_path(hypernym)

        return tree

    def annotate_topic_tree(self):
        """Annotates the nodes in the `bacalhau.topic_tree.TopicTree`
        with information about which `bacalhau.text.Text` and counts
        the nodes relate to.

        :rtype: `bacalhau.topic_tree.TopicTree`
        """
        hypernyms = self._hypernyms
        tree = self._tree

        for text, data in hypernyms.iteritems():
            for hypernym in data.values():
                for node in tree.nbunch_iter(hypernym):
                    texts = tree.node[node].setdefault('texts', [])
                    texts.append(text)

                    if 'count' not in tree.node[node]:
                        tree.node[node]['count'] = 0
                    tree.node[node]['count'] += 1

        return tree
