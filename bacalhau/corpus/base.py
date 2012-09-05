from bacalhau.topic_tree import TopicTree
from collections import defaultdict
from math import log
import nltk
import os


class Corpus(object):

    WORK_DIR = 'work'

    def __init__(self, corpus_path, document_class,
                  tokenizer=nltk.tokenize.regexp.WordPunctTokenizer(),
                  stopwords=nltk.corpus.stopwords.words('english'),
                  workpath=WORK_DIR):
        """Creates a new Corpus for the given path, using the given
        Document class to process the files."""
        self._corpus_path = os.path.abspath(corpus_path)
        self._document_class = document_class
        self._tokenizer = tokenizer
        self._stopwords = stopwords
        self._documents = self._get_documents(os.path.abspath(corpus_path))
        # Total number of texts (not documents) in the corpus.
        self._text_count = self._get_text_count()
        self._hypernyms = None
        self._tree = None

    def _get_documents(self, corpus_path):
        """Returns a list of `Document` objects in this corpus."""
        documents = []
        for (path, dirs, files) in os.walk(corpus_path):
            for filename in files:
                document = self._document_class(
                    os.path.join(path, filename), self._tokenizer,
                    self._stopwords, *self._document_args)
                documents.append(document)
        return documents

    def _get_text_count(self):
        """Returns a float of the number of `Text` objects in this
        corpus."""
        count = 0
        for document in self._documents:
            count += document.get_text_count()
        return float(count)

    def generate_topic_tree(self, n_terms=10, nodes_to_prune=[],
            min_children=2):
        """Generates the topic tree for the corpus."""
        top_terms = self.get_top_terms(n_terms)
        hypernyms = self.get_hypernyms(top_terms)
        tree = self.get_topic_tree(hypernyms, nodes_to_prune, min_children)

        self._hypernyms = hypernyms
        self._tree = tree

        return tree

    def get_top_terms(self, n_terms):
        """Returns a list with the highest `n_terms` for each text from the
        term data dictionary."""
        term_data = self.add_tf_idf(self.get_term_data())
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

    def get_term_data(self):
        """Returns term data for all of the `Document` objects in this
        corpus."""
        term_data = defaultdict(dict)
        for document in self._documents:
            document_term_data = document.get_term_data()
            for term, new_term_data in document_term_data.items():
                term_data[term].update(new_term_data)
        return term_data

    def add_tf_idf(self, term_data):
        """Returns `term_data` with a TF.IDF value added to each
        term/text combination."""
        for term, text_frequencies in term_data.items():
            # Number of texts containing the term.
            matches = len(text_frequencies)
            idf = log(self._text_count / matches)
            for text, text_data in text_frequencies.items():
                text_data['tf.idf'] = text_data['frequency'] * idf
        return term_data

    def get_hypernyms(self, top_terms):
        """Returns the hypernyms for the given terms."""
        hypernyms = defaultdict(dict)

        for text, terms in top_terms.iteritems():
            for term in terms:
                hypernyms[text][term] = self.get_hypernym(term)

        return hypernyms

    def get_hypernym(self, word):
        """Returns a list of the hypernyms for the given word."""
        hypernym = [word]

        synsets = nltk.corpus.wordnet.synsets(word)
        while len(synsets) > 0:
            s = synsets[0]
            hypernym.append(s.name)
            synsets = s.hypernyms()

        return hypernym

    def get_topic_tree(self, hypernyms, nodes_to_prune=[], min_children=2):
        """Generates and returns a `TopicTree` for the given hypernyms."""
        tree = TopicTree()

        for text, data in hypernyms.iteritems():
            for term, hypernym in data.iteritems():
                tree.add_nodes_from(hypernym)
                tree.node[hypernym[0]]['is_leaf'] = True
                tree.node[hypernym[len(hypernym) - 1]]['is_root'] = True
                hypernym.reverse()
                tree.add_path(hypernym)

        tree = self._compress_and_prune_tree(tree, nodes_to_prune,
                min_children)

        return tree

    def _compress_and_prune_tree(self, tree, nodes_to_prune, min_children):
        """Compresses the tree using the castanet algorithm:
        1. starting from the leaves, recursively eliminate a parent that has
        fewer than 2 children, unless the parent is the root
        2. eliminate a child whose name appears within the parent's name."""
        for n in tree.nodes(data=True):
            if 'is_leaf' in n[1]:
                tree = self._eliminate_parents(tree, n[0], min_children)

        for n in tree.nodes(data=True):
            if 'is_leaf' in n[1]:
                tree = self._eliminate_child_with_parent_name(tree, n[0])

        tree = self._prune_tree(tree, nodes_to_prune)

        return tree

    def _eliminate_parents(self, tree, node, min_children=2):
        """Recursively eliminates a parent of the current node that has fewer
        than min_children children, unless the parent is the root."""
        for p in tree.predecessors(node):
            if tree.has_node(p):
                n_children = len(tree.out_edges(p))
                has_parent = len(tree.predecessors(p)) > 0

                if n_children < min_children and has_parent:
                    ancestor = tree.predecessors(p)[0]
                    children = tree.successors(p)

                    tree.remove_node(p)

                    for child in children:
                        tree.add_edge(ancestor, child)

                    self._eliminate_parents(tree, node)
                else:
                    self._eliminate_parents(tree, p)

        return tree

    def _eliminate_child_with_parent_name(self, tree, node):
        """Eliminate a child whose name appears within the parent's name."""
        for p in tree.predecessors(node):
            if tree.has_node(p):
                node_name = node[:node.find('.')]
                p_name = p[:p.find('.')]

                if node_name in p_name or p_name in node_name:
                    children = tree.successors(node)
                    tree.remove_node(node)

                    for child in children:
                        tree.add_edge(p, child)

                    self._eliminate_child_with_parent_name(tree, p)
                else:
                    self._eliminate_child_with_parent_name(tree, p)

        return tree

    def _prune_tree(self, tree, nodes):
        """Removes the nodes from the tree."""
        for node in nodes:
            if tree.has_node(node):
                tree.remove_node(node)

        return tree

    def annotate_topic_tree(self):
        hypernyms = self._hypernyms
        tree = self._tree

        for text, data in hypernyms.iteritems():
            for hypernym in data.values():
                for node in tree.nbunch_iter(hypernym):
                    if 'texts' not in tree.node[node]:
                        tree.node[node]['texts'] = []
                    tree.node[node]['texts'].append(text)

                    if 'count' not in tree.node[node]:
                        tree.node[node]['count'] = 0
                    tree.node[node]['count'] = tree.node[node]['count'] + 1

        return tree

