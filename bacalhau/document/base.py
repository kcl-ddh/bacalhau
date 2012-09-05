import abc
import os


class Document:
    """Abstract class to read from/write to files. Different implementations
    should extend this class and override the abstract methods."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, filepath, tokenizer, stopwords):
        """Creates a new Document for the given file path."""
        self._path = os.path.abspath(filepath)
        self._document_id = os.path.splitext(os.path.basename(self._path))[0]
        self._base_filepath = os.path.splitext(self._path)[0]
        self._tokenizer = tokenizer
        self._stopwords = stopwords
        self._texts = self._get_texts(self._document_id)

    @abc.abstractmethod
    def get_term_data(self):
        """Returns term data for each `Text` within this document."""
        return

    def get_text_count(self):
        return len(self._texts)

    @abc.abstractmethod
    def _get_texts(self, document_id):
        """Returns a list of `Text` objects within this document."""
        return
