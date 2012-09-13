from nltk.corpus import wordnet
import re


class Text(object):
    """Represents a text unit from a `bacalhau.document.Document`."""

    def __init__(self, text_id, content, tokenizer, stopwords):
        """Creates a new `.Text` object.

        :param text_id: id of the `.Text`.
        :type text_id: `str`
        :param content: content of the `.Text`.
        :type content: `str`
        :param tokenizer: tokenizer used to tokenize the files in the corpus.
        :type tokenizer: `nltk.tokenize.api.TokenizerI`
        :param stopwords: words to be removed from the texts.
        :type stopwords: `list` of words.
        """
        self._text_id = text_id
        self._content = content.lower()
        self._tokenizer = tokenizer
        self._stopwords = stopwords

    def get_term_data(self):
        """Returns term data for this text.

        The term's data are the unnormalised and normalised frequency
        counts of the term in this text. The former uses the "count"
        key, the latter "frequency".

        The data is structured as a nested dictionary (term -> text ->
        counts) for easy merging of the term data from multiple
        `.Text`\s.

        :rtype: `dict`

        """
        term_data = {}
        tokens = self._tokenizer.tokenize(self._content)
        max_token_count = 0
        # This provides a "term count" that is unnormalised, meaning
        # that the length of the text is not accounted for.
        for token in tokens:
            if self._is_valid_token(token):
                token_data = term_data.setdefault(token,
                        {self._text_id: {'count': 0}})
                if (token_data[self._text_id]['count'] + 1) > max_token_count:
                    max_token_count += 1
                term_data[token][self._text_id]['count'] += 1
        # Normalise the term counts to provide a "term frequency" for
        # each term.
        for term, text_data in term_data.items():
            count = float(text_data[self._text_id]['count'])
            text_data[self._text_id]['frequency'] = count / max_token_count
        return term_data

    def _is_valid_token(self, token):
        """Checks if the `token` is suitable for processing.

        :param token: the token to validate.
        :type token: `str`
        :returns: True if `token` is valid.
        :rtype: `bool`

        """
        if token in self._stopwords:
            return False
        if re.search(r'[^A-Za-z]', token):
            return False
        if not wordnet.synsets(token, pos=wordnet.NOUN):
            return False
        return True
