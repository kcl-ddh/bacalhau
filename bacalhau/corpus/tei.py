from bacalhau.corpus.base import Corpus
import nltk


class TEICorpus(Corpus):
    """`Corpus` object for TEI files."""

    def __init__(self, corpuspath, document_class, xpath,
            tokenizer=nltk.tokenize.regexp.WordPunctTokenizer(),
            stopwords=nltk.corpus.stopwords.words('english')):
        """Creates a new `.TEICorpus` for the given path, using the
        given Document class to process the files.

        :param corpus_path: path to the files.
        :type corpus_path: `str`
        :param document_class: document class used to process the corpus files.
        :type document_class: `bacalhau.document.base.Document`
        :param xpath: XPath where to get the `Text` from the TEI files.
        :type xpath: `str`
        :param tokenizer: tokenizer used to tokenize the files in the corpus,
            defaults to `nltk.tokenize.regexp.WordPunctTokenizer`.
        :type tokenizer: `nltk.tokenize.api.TokenizerI`
        :param stopwords: words to be removed from the texts, defaults to
            `nltk.corpus.stopwords.words(\'english\')`.
        :type stopwords: `list`
        """
        self._xpath = xpath
        self._document_args = [self._xpath]
        super(TEICorpus, self).__init__(corpuspath, document_class, tokenizer,
                stopwords)
