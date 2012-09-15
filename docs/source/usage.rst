.. _usage:

Usage
=====

To generate a topic hierarchy for a corpus, run the ``bacalhau``
script with the appropriate arguments. These are documented in the
script; use ``bacalhau -h`` to see them.

Handling new document formats
-----------------------------

If the corpus files are not TEI XML, an implementation of the
``bacalhau.document.Document`` class must be written. The name of this
class (with complete package path; for example,
``bacalhau.tei_document.TEIDocument``) is passed to the ``bacalhau``
script with ``--document`` option.

Corpora with documents of more than a single type are not supported.
