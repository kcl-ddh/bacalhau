from bacalhau.corpus.base import Corpus
import nltk


class TEICorpus(Corpus):

    def __init__(self, corpuspath, document_class, xpath,
            tokenizer=nltk.tokenize.regexp.WordPunctTokenizer(),
            stopwords=nltk.corpus.stopwords.words('english'),
            workpath=Corpus.WORK_DIR):
        """Creates a new TEICorpus for the given path, using the
        given Document class to process the files."""
        self._xpath = xpath
        self._document_args = [self._xpath]
        super(TEICorpus, self).__init__(corpuspath, document_class, tokenizer,
                stopwords, workpath)
