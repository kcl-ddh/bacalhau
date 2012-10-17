from bacalhau.corpus import Corpus
from bacalhau.tei_document import TEIDocument
import unittest


class TestCorpus(unittest.TestCase):

    def setUp(self):
        corpus_path = 'tests/corpus'
        kwargs = {}
        kwargs['xpath'] = '//tei:body/tei:div[@type = "dummy"]'
        self.corpus = Corpus(corpus_path, TEIDocument, **kwargs)

    def test__get_documents(self):
        docs = self.corpus._get_documents()
        self.assertIsNotNone(docs)
        self.assertEqual(2, len(docs))

    def test__get_text_count(self):
        count = self.corpus._get_text_count()
        self.assertEqual(3, count)

    def test_generate_topic_tree(self):
        tree = self.corpus.generate_topic_tree(n_terms=10)
        self.assertIsNotNone(tree)
        self.assertGreater(tree.number_of_nodes, 0)

    def test_get_top_terms(self):
        terms = self.corpus.get_top_terms(n_terms=10)
        self.assertIsNotNone(terms)
        self.assertGreater(len(terms), 0)

    def test__get_term_data(self):
        term_data = self.corpus._get_term_data()
        self.assertIsNotNone(term_data)
        self.assertGreater(len(term_data), 0)

    def test__add_tf_idf(self):
        term_data = self.corpus._get_term_data()
        tf_idf = self.corpus._add_tf_idf(term_data)
        self.assertIsNotNone(tf_idf)
        self.assertGreater(len(tf_idf), 0)
        self.assertTrue('tf.idf' in tf_idf.values()[0].values()[0])

    def test_get_hypernyms(self):
        terms = self.corpus.get_top_terms(n_terms=10)
        hypernyms = self.corpus.get_hypernyms(terms)
        self.assertIsNotNone(hypernyms)
        self.assertGreater(len(hypernyms), 0)

    def test_get__hypernym(self):
        hypernym = self.corpus._get_hypernym('dog')
        self.assertIsNotNone(hypernym)
        self.assertGreater(len(hypernym), 0)

    def test_get_topic_tree(self):
        terms = self.corpus.get_top_terms(n_terms=10)
        hypernyms = self.corpus.get_hypernyms(terms)
        tree = self.corpus.get_topic_tree(hypernyms)
        self.assertIsNotNone(tree)
        self.assertGreater(tree.number_of_nodes, 0)

    def test_annotate_topic_tree(self):
        tree = self.corpus.generate_topic_tree(n_terms=10)
        tree = self.corpus.annotate_topic_tree(tree)
        self.assertIsNotNone(tree)
        self.assertGreater(tree.number_of_nodes, 0)
        self.assertTrue('texts' in tree.node[tree.nodes()[0]])
        self.assertTrue('count' in tree.node[tree.nodes()[0]])

if __name__ == '__main__':
    unittest.main()
