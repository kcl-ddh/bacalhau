from bacalhau.document import Document
from bacalhau.text import Text
from collections import defaultdict
from lxml import etree


class TEIDocument (Document):
    """Implementation of the abstract
    `bacalhau.document.Document` class to work with TEI files."""

    TEI_NAMESPACE = 'http://www.tei-c.org/ns/1.0'
    TEI = '{%s}' % TEI_NAMESPACE
    XML_NAMESPACE = 'http://www.w3.org/XML/1998/namespace'
    XML = '{%s}' % (XML_NAMESPACE)
    NS_MAP = {'tei': TEI_NAMESPACE, 'xml': XML_NAMESPACE}

    def __init__(self, filepath, tokenizer, stopwords, xpath,
                 ns_map=NS_MAP):
        """Creates a new `.TEIDocument` for the given file path.

        :param filepath: path to the file.
        :type filepath: `str`
        :param tokenizer: tokenizer used to tokenize the files in the corpus.
        :type tokenizer: `nltk.tokenize.api.TokenizerI`
        :param stopwords: words to be removed from the texts.
        :type stopwords: `list`
        :param xpath: XPath where to get the `bacalhau.text.Text` from the TEI files.
        :type xpath: `str`
        :param ns_map: namespaces used in the `.TEIDocument`.
        :type ns_map: `dict`
        """
        self._xpath = xpath
        self._ns_map = ns_map
        super(TEIDocument, self).__init__(filepath, tokenizer, stopwords)

    def get_texts(self):
        """Returns a list of `bacalhau.text.Text` objects within this
        document.

        :returns: `bacalhau.text.Text` objects within this document.
        :rtype: `list`
        """
        texts = []
        tree = etree.parse(self._path)
        text_elements = tree.xpath(self._xpath, namespaces=self._ns_map)
        for text_element in text_elements:
            xml_id = text_element.get(self.XML + 'id')
            text_id = '%s-%s' % (self._document_id, xml_id)
            content = etree.tostring(text_element, encoding='utf-8',
                                     method='text')
            texts.append(Text(text_id, content, self._tokenizer,
                              self._stopwords))
        return texts

    def get_term_data(self):
        """Returns term data for each `bacalhau.text.Text` within this
        document.

        :rtype: `dict`
        """
        term_data = defaultdict(dict)
        for text in self._texts:
            text_term_data = text.get_term_data()
            for term, new_term_data in text_term_data.items():
                term_data[term].update(new_term_data)
        return term_data
