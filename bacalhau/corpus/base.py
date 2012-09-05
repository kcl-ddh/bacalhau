from collections import defaultdict
from math import log
from operator import itemgetter
import os

import nltk

from bacalhau.topic_tree import TopicTree


class Corpus(object):

    WORK_DIR = 'work'

    def __init__ (self, corpus_path, document_class,
                  tokenizer=nltk.tokenize.regexp.WordPunctTokenizer(),
                  stopwords=nltk.corpus.stopwords.words('english'),
                  workpath=WORK_DIR):
        """Creates a new Corpus for the given path, using the given
        Document class to process the files."""
        self._corpus_path = os.path.abspath(corpus_path)
        self._document_class = document_class
        self._tokenizer = tokenizer
        self._stopwords = stopwords
        self._textcollection = None
        self._texts = {}
        self._documents = self._get_documents(os.path.abspath(corpus_path))
        # Total number of texts (not documents) in the corpus.
        self._text_count = self._get_text_count()

    def _get_documents (self, corpus_path):
        """Returns a list of `Document` objects in this corpus."""
        documents = []
        for (path, dirs, files) in os.walk(corpus_path):
            for filename in files:
                document = self._document_class(
                    os.path.join(path, filename), self._tokenizer,
                    self._stopwords, *self._document_args)
                documents.append(document)
        return documents

    def get_term_data (self):
        """Returns term data for all of the `Document` objects in this
        corpus."""
        term_data = defaultdict(dict)
        for document in self._documents:
            document_term_data = document.get_term_data()
            for term, new_term_data in document_term_data.items():
                term_data[term].update(new_term_data)
        return term_data

    def _get_text_count (self):
        """Returns a float of the number of `Text` objects in this
        corpus."""
        count = 0
        for document in self._documents:
            count += document.get_text_count()
        return float(count)

    def add_tf_idf (self, term_data):
        """Returns `term_data` with a TF.IDF value added to each
        term/text combination."""
        for term, text_frequencies in term_data.items():
            # Number of texts containing the term.
            matches = len(text_frequencies)
            idf = log(self._text_count / matches)
            for text, text_data in text_frequencies.items():
                text_data['tf.idf'] = text_data['frequency'] * idf
        return term_data

    def generate_topic_tree(self, n_target_terms=10, nodes_to_prune=[],
            min_children=2):
        """Generates the topic tree for the corpus."""
        self.extract(n_target_terms)
        self._tree = self.generate(nodes_to_prune, min_children)

        return self._tree

    def extract(self, n_target_terms=10):
        """Extracts target tems from the texts: selects nouns, computes tf.idf,
        and creates hypernym paths for the target terms."""
        self._corpus = nltk.corpus.PlaintextCorpusReader(self._work_path, '.*')
        self._textcollection = nltk.text.TextCollection(self._corpus)

        for f in self._corpus.fileids():
            tf_idf_dict = {}

            for w in self._corpus.words(fileids=f):
                tf_idf_dict[w] = self._textcollection.tf_idf(w,
                        self._textcollection)

            text = self._texts[f]
            text._tf_idf_dict = tf_idf_dict

            tf_idf_dict = sorted(tf_idf_dict.iteritems(), key=itemgetter(1),
                    reverse=True)

            hypernyms_dict = {}

            for idx, item in enumerate(tf_idf_dict):
                if idx >= n_target_terms:
                    break

                word = item[0]
                hypernyms_dict[word] = []
                hypernyms_dict[word].append(word)

                synsets = nltk.corpus.wordnet.synsets(word)

                while len(synsets) > 0:
                    syn = synsets[0]
                    name = syn.name
                    hypernyms_dict[word].append(name)
                    synsets = syn.hypernyms()

            text._hypernyms_dict = hypernyms_dict

    def generate(self, nodes_to_prune=[], min_children=2):
        """Generates topic tree: creates hypernym paths for the target terms,
        generates topic tree for the hypernym paths, compresses the topic
        tree."""
        tree = TopicTree()

        for text in self._texts.values():
            for hypernym in text._hypernyms_dict.values():
                if len(hypernym) > 0:
                    tree.add_nodes_from(hypernym)
                    tree.node[hypernym[0]]['is_leaf'] = True
                    tree.node[hypernym[0]]['group'] = 'leaf'
                    tree.node[hypernym[len(hypernym) - 1]]['is_root'] = True
                    tree.node[hypernym[len(hypernym) - 1]]['group'] = 'root'
                    hypernym.reverse()
                    tree.add_path(hypernym)

        tree = self._compress_and_prune_tree(tree, nodes_to_prune,
                min_children)

        for text in self._texts.values():
            text._tree = tree

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
