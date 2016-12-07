# Lyt : simple literate programming in Markdown.

Lyt is a literate programming tool, written in Python, that extracts fenced code blocks from Markdown documents. It is meant to be used as a preprocess tool before a conventional build.

It is licensed under the GPLv3. See the LICENSE.txt file in this repo.

## Installation


## Usage
Open your favorite command line:
`$ lyt file.md`

For more information, use `--help`:
`$ lyt --help`

## Goals
 - Stay python 2 and 3 compatible.
 - Stay simple.
     + In particular, handling several files at a time isn't a goal
     + Nor is handling the dependency between generated files and the source.
     
## Future
 - Add support for more languages.
 - Allow autodetection of languages.
 - Add better tests.
 - Add static types and validate with mypy.
 - Maybe allow hierarchical embedding?
