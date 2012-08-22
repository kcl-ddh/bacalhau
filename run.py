#!/usr/bin/env python

# -*- coding: utf-8 -*-

from bacalhau import TopicHierarchyGenerator
from teimanager import TEIManager

CORPUS_PATH = 'corpus'

if __name__ == "__main__":
    thg = TopicHierarchyGenerator(CORPUS_PATH, TEIManager)
    thg.extract()
    print(thg._corpus.words())
