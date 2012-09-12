from bacalhau.topic_tree import TopicTree
import os
import unittest


class TestTopicTree(unittest.TestCase):

    def setUp(self):
        self.tree = TopicTree()
        self.tree.add_nodes_from(['a', 'b', 'cc', 'c', 'd', 'e', 'f',
            'g', 'h', 'ii', 'i', 'j', 'k'])
        self.tree.add_path(['a', 'b', 'e', 'f', 'g'])
        self.tree.add_path(['a', 'cc', 'c', 'h'])
        self.tree.add_path(['a', 'cc', 'ii', 'i'])
        self.tree.add_path(['a', 'd', 'j'])
        self.tree.add_path(['a', 'd', 'k'])
        self.tree.node['g']['is_leaf'] = True
        self.tree.node['h']['is_leaf'] = True
        self.tree.node['i']['is_leaf'] = True
        self.tree.node['j']['is_leaf'] = True
        self.tree.node['k']['is_leaf'] = True

    def test_compress(self):
        number_of_nodes = self.tree.number_of_nodes()
        self.tree.compress()
        compressed_number_of_nodes = self.tree.number_of_nodes()
        self.assertLess(compressed_number_of_nodes, number_of_nodes)

    def test_render(self):
        filename = 'test.svg'

        self.addCleanup(os.remove, filename)
        self.tree.render(filename)

        try:
            open(filename, 'r')
        except IOError:
            self.fail()

if __name__ == '__main__':
    unittest.main()
