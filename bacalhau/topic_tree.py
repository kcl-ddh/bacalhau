# -*- coding: utf-8 -*-

from networkx.readwrite import json_graph
import networkx as nx


class TopicTree(nx.DiGraph):
    """Represents a TopicTree. Extends `networkx.DiGraph`."""

    def __init__(self, data=None, **attr):
        """Creates a new `.TopicTree`.

        :param data: data to initialize the tree with. If no data is supplied
            an empty tree is created.
        :type data: `list`, `.TopicTree` or any `networkx` graph object.
        :param attr: keyword arguments to add to the tree.
        :type attr: key/value pairs.
        """
        super(TopicTree, self).__init__(data, **attr)

    def compress(self, min_children=2):
        """Compresses the tree based on the castanet algorithm: 1. starting
        from the leaves, recursively eliminate a parent that has fewer than
        `min_children`, unless the parent is the root; 2. eliminate a child
        whose name appears within the parent's name.

        :param min_children: minimum number of children that a parent should
            have, defaults to 2.
        :type min_children: int.
        """
        for n in self.nodes(data=True):
            if 'is_leaf' in n[1]:
                self._eliminate_parents(n[0], min_children)

        for n in self.nodes(data=True):
            if 'is_leaf' in n[1]:
                self._eliminate_child_with_parent_name(n[0])

    def _eliminate_parents(self, node, min_children):
        """Recursively eliminates a parent of the current node that has fewer
        than min_children children, unless the parent is the root.

        :param node: name of node to process.
        :type node: str.
        :param min_children: minimum number of children that a parent should
            have
        :type min_children: int.
        """
        for p in self.predecessors(node):
            if self.has_node(p):
                n_children = len(self.out_edges(p))
                has_parent = len(self.predecessors(p)) > 0

                if n_children < min_children and has_parent:
                    ancestor = self.predecessors(p)[0]
                    children = self.successors(p)

                    self.remove_node(p)

                    for child in children:
                        self.add_edge(ancestor, child)

                    self._eliminate_parents(node, min_children)
                else:
                    self._eliminate_parents(p, min_children)

    def _eliminate_child_with_parent_name(self, node):
        """Eliminate a child node whose name appears within the parent's
        name.

        :param node: name of node to process.
        :type node: str.
        """
        for p in self.predecessors(node):
            if self.has_node(p):
                node_name = node[:node.find('.')]
                p_name = p[:p.find('.')]

                if node_name in p_name or p_name in node_name:
                    children = self.successors(node)
                    self.remove_node(node)

                    for child in children:
                        self.add_edge(p, child)

                    self._eliminate_child_with_parent_name(p)
                else:
                    self._eliminate_child_with_parent_name(p)

    def prune(self, nodes):
        """Removes the given nodes from the tree.

        :param nodes: names of the nodes to be remove from the tree.
        :type nodes: list of str.
        """
        for node in nodes:
            if self.has_node(node):
                self.remove_node(node)

    def render(self, filepath, format='svg', prog='dot', attributes={}):
        """Renders the tree into the file at `filepath`.

        `filepath` may also be a File-like object."""
        agraph = nx.to_agraph(self)

        for key, value in attributes.iteritems():
            agraph.node_attr[key] = value

        agraph.draw(filepath, format=format, prog=prog)

    def to_json(self, filepath):
        """Serializes the TopicTree to JSON Graph format and writes it
        to a file.

        `filepath` is a file path or File-like object."""
        if isinstance(filepath, basestring):
            json_file = open(filepath, 'w')
        else:
            json_file = filepath
        json_file.write(json_graph.dumps(self))
        if isinstance(filepath, basestring):
            json_file.close()
