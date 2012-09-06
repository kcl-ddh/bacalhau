# -*- coding: utf-8 -*-

from networkx.readwrite import json_graph
import networkx as nx


class TopicTree(nx.DiGraph):
    """Represents a TopicTree. Extends networkx.DiGraph."""

    def __init__(self, data=None, **attr):
        super(TopicTree, self).__init__(data, **attr)

    def compress(self, min_children=2):
        """Compresses the tree using the castanet algorithm:
        1. starting from the leaves, recursively eliminate a parent that has
        fewer than 2 children, unless the parent is the root
        2. eliminate a child whose name appears within the parent's name."""
        for n in self.nodes(data=True):
            if 'is_leaf' in n[1]:
                self._eliminate_parents(n[0], min_children)

        for n in self.nodes(data=True):
            if 'is_leaf' in n[1]:
                self._eliminate_child_with_parent_name(n[0])

    def _eliminate_parents(self, node, min_children=2):
        """Recursively eliminates a parent of the current node that has fewer
        than min_children children, unless the parent is the root."""
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

                    self._eliminate_parents(node)
                else:
                    self._eliminate_parents(p)

    def _eliminate_child_with_parent_name(self, node):
        """Eliminate a child whose name appears within the parent's name."""
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
        """Removes the given nodes from the tree."""
        for node in nodes:
            if self.has_node(node):
                self.remove_node(node)

    def render(self, filepath, format='svg', prog='dot', attributes={}):
        """Renders the topic tree into the file at filepath."""
        agraph = nx.to_agraph(self)

        for key, value in attributes.iteritems():
            agraph.node_attr[key] = value

        agraph.draw(filepath, format=format, prog=prog)

    def to_json(self, filepath):
        """Serializes the TopicTree to JSON Graph format."""
        json_file = open(filepath, 'w')
        json_file.write(json_graph.dumps(self))
        json_file.close()
