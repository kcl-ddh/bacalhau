from bacalhau.tei_document import TEIDocument
import nltk
import unittest


class TestDocument(unittest.TestCase):

    def setUp(self):
        self.filepath = 'tests/corpus/a.xml'
        self.doc = TEIDocument(self.filepath, 
                nltk.tokenize.regexp.WordPunctTokenizer(),
                nltk.corpus.stopwords.words('english'),
                '//tei:body/tei:div[@type = "dummy"]')

    def test_get_text_count(self):
        self.assertEqual(2, self.doc.get_text_count())

    def test_get_texts(self):
        texts = self.doc.get_texts()
        self.assertEqual(2, len(texts))

    def test_get_term_data(self):
        term_data = self.doc.get_term_data()
        self.assertIsNotNone(term_data)

if __name__ == '__main__':
    unittest.main()
