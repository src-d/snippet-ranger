## Snippet ranger

[![Build Status](https://travis-ci.org/src-d/snippet-ranger.svg)](https://travis-ci.org/src-d/snippet-ranger) [![codecov](https://codecov.io/github/src-d/snippet-ranger/coverage.svg)](https://codecov.io/gh/src-d/snippet-ranger)

This tool is built on top of [ast2vec](https://github.com/src-d/ast2vec) Machine Learning models.

Provides API and tools to train and use models for ecosystem exploratory snippet mining.
It can help you to learn new libraries faster and speed up coding speed.
The module allows you to train and use hierarchical topic model on top of
[babelfish](https://github.com/bblfsh) UAST for any library you want.

Now Snippet ranger is under active development.

## Install

```
pip3 install git+https://github.com/src-d/snippet-ranger
```

## Usage

The project exposes two interfaces: API and command line. The command line is

```
snippet_ranger --help
```
There is an example of using Python API.
#TODO(zurk): Make an example.

## Contributions
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)

We use [PEP8](https://www.python.org/dev/peps/pep-0008/) with line length 99 and ". All the tests
must pass:

```
unittest discover /path/to/ast2vec
```

## License

Apache 2.0.
