# -*- coding: utf-8 -*-

from networkx import DiGraph
import pygraphviz


class TopicTree(DiGraph):
    """Represents a TopicTree. Extends networkx.DiGraph."""

    def __init__(self, data=None, **attr):
        super(TopicTree, self).__init__(data, **attr)

    def render(self, filepath, format='svg', prog='dot', attributes={}):
        """Renders the topic tree into the file at filepath."""
        agraph = pygraphviz.AGraph(strict=True, directed=True)
        agraph.node_attr['shape'] = 'box'
        agraph.node_attr['style'] = 'filled'
        agraph.node_attr['fillcolor'] = 'lemonchiffon'

        agraph.add_nodes_from(self.nodes())
        agraph.add_edges_from(self.edges())

        agraph.draw(filepath, format=format, prog=prog)
