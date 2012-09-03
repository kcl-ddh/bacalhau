# -*- coding: utf-8 -*-

import networkx as nx


class TopicTree(nx.DiGraph):
    """Represents a TopicTree. Extends networkx.DiGraph."""

    def __init__(self, data=None, **attr):
        super(TopicTree, self).__init__(data, **attr)

    def render(self, filepath, format='svg', prog='dot', attributes={}):
        """Renders the topic tree into the file at filepath."""
        agraph = nx.to_agraph(self)

        for key, value in attributes.iteritems():
            agraph.node_attr[key] = value

        agraph.draw(filepath, format=format, prog=prog)

    def to_json(self, filepath):
        """Serializes the TopicTree to JSON Graph format."""
        json_file = open(filepath, 'w')
        json_file.write(nx.readwrite.json_graph.dumps(self))
        json_file.close()
