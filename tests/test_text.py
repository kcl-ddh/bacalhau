from bacalhau.text import Text
import nltk
import unittest


class TestText(unittest.TestCase):

    def setUp(self):
        self.text_id = 'id'
        self.text = Text(self.text_id,
                'The quick brown fox jumps over the lazy dog, dogs.',
                nltk.tokenize.regexp.WordPunctTokenizer(),
                nltk.corpus.stopwords.words('english'))

    def test_get_term_data(self):
        term_data = self.text.get_term_data()
        self.assertEqual(term_data['fox'][self.text_id]['count'], 1)
        self.assertEqual(term_data['fox'][self.text_id]['frequency'],
                0.5)
        self.assertEqual(term_data['dog'][self.text_id]['count'], 2)
        self.assertEqual(term_data['dog'][self.text_id]['frequency'],
                1)

    def test__is_valid_token(self):
        self.assertTrue(self.text._is_valid_token('dog'))
        self.assertTrue(self.text._is_valid_token('dogs'))
        self.assertTrue(self.text._is_valid_token('fox'))
        self.assertTrue(self.text._is_valid_token('brown'))
        self.assertFalse(self.text._is_valid_token('the'))
        self.assertFalse(self.text._is_valid_token('lazy'))
        self.assertFalse(self.text._is_valid_token('.'))

if __name__ == '__main__':
    unittest.main()
