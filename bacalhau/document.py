import abc
import os


class Document:
    """Abstract class to read from/write to files. Different implementations
    should extend this class and override the abstract methods."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, filepath, tokenizer, stopwords):
        """Creates a new `Document` for the given file path.

        :param filepath: path to the file.
        :type filepath: `str`
        :param tokenizer: tokenizer used to tokenize the files in the corpus.
        :type tokenizer: `nltk.tokenize.api.TokenizerI`
        :param stopwords: words to be removed from the texts.
        :type stopwords: `list`
        """
        self._path = os.path.abspath(filepath)
        self._document_id = os.path.splitext(os.path.basename(self._path))[0]
        self._base_filepath = os.path.splitext(self._path)[0]
        self._tokenizer = tokenizer
        self._stopwords = stopwords
        self._texts = self.get_texts()

    @abc.abstractmethod
    def get_texts(self):
        """Returns a list of `bacalhau.text.Text` objects within this
        document.

        :returns: list of `bacalhau.text.Text` objects.
        :rtype: `list`
        """
        return

    @abc.abstractmethod
    def get_term_data(self):
        """Returns term data for each `bacalhau.text.Text` within this document.

        :returns: `dict`
        """
        return

    def get_text_count(self):
        """Returns the number of `bacalhau.text.Text` objects for this
        `.Document`.

        :returns: number of `bacalhau.text.Text` objects.
        :rtype: `int`
        """
        return len(self._texts)
