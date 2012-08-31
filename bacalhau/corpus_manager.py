# -*- coding: utf-8 -*-

from operator import itemgetter
import networkx
import nltk
import os


class CorpusManager(object):

    WORK_DIR = 'work'

    def __init__(self, corpuspath, manager,
            tokenizer=nltk.tokenize.regexp.WordPunctTokenizer(),
            stopwords=nltk.corpus.stopwords.words('english'),
            workpath=WORK_DIR):
        """Creates a new CorpusManager for the given path, using the given
        document Manager to process the files."""
        self._path = os.path.abspath(corpuspath)
        self._manager = manager
        self._tokenizer = tokenizer
        self._stopwords = stopwords
        self._work_path = os.path.abspath(workpath)
        self._corpus = None
        self._textcollection = None
        self._texts = {}

    def generate_topic_tree(self, n_target_terms=10, nodes_to_prune=[],
            min_children=2):
        """Generates the topic tree for the corpus."""
        self.prepare()
        self.extract(n_target_terms)

        return self.generate(nodes_to_prune, min_children)

    def prepare(self):
        """Prepares the corpus for the topic tree generation."""
        try:
            os.mkdir(self._work_path)
        except OSError:
            pass

        for (path, dirs, files) in os.walk(self._path):
            for filename in files:
                manager = self._manager(os.path.join(path, filename),
                        self._work_path)
                texts = manager.extract_texts()

                for text in texts:
                    self._texts[text._key] = text

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
        hypernyms_dict = {}
        tree = networkx.DiGraph()

        for text in self._texts.values():
            hypernyms_dict = dict(hypernyms_dict.items() + \
                    text._hypernyms_dict.items())

        for hypernym in hypernyms_dict.values():
            if len(hypernym) > 0:
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
