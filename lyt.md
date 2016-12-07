# lyt: simple literate programming in Markdown
## Description
`lyt` is a python tool that extracts fenced code blocks from Markdown documents. This allows us to write Markdown documents that contain programs and interlard prose with code. The practice of writing prose to explain code is called *literate programming*. A *literate program* embeds that code within the text, rather than the more common opposite. `lyt` is only a small tool in a long lineage of tools designed for literate programming, back to WEB (and its successor CWEB), the original tool created by professor Donald Knuth.

In particular, `lyt` was inspired directly by `markdown-unlit`, a Haskell tool that does the exact same thing, but only for Haskell source code. I decided to write `lyt` in order to support more languages, and I used python for its good text manipulation capabilities and ease of use. 

`lyt` is based on the [CommonMark spec](http://commonmark.org/), in which fenced code blocks start with three or more backticks (```) or tildes (~~~), and end with the same amount of backticks (in our case, ```) or tildes, whichever was chosen as the opener. Optionally, the opener can be followed by non-backtick character: this text, up to the newline character, is called the infostring, and the first word of the infostring is used to annotate which language the code inside the block is written into. See [section 4.5 of the spec](http://spec.commonmark.org/0.26/#fenced-code-blocks) for a detailed description.

## Code
This document contains the totality of `lyt`'s code, which you can extract with `lyt` itself.

We'll start with the standard shebang, followed by the GPLv3 notice, and the docstring for the module itself.

```python
#!/usr/bin/python

# Copyright (C) 2016  Adrien Lamarque

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""lyt is a literate programming tool, written in Python, that extracts fenced code blocks from Markdown documents. It is meant to be used as a preprocess tool before a conventional build.
"""
```
lyt depends on `click` in addition to standard modules.

```python
import re
import collections
import click
import sys
import os.path

```

Here we have two tables, that should contain the same number of entries. The first ones gives us the extension for a given language name (as found in the fenced code block infostring).

```python 
DEFAULT_EXT = "txt"
matching_extensions = {
	'python': 'py',
	'c++': 'cpp',
	'c': 'c',
	'c#': 'cs',
	'haskell': 'hs',
	'ruby': 'rb',
	'go': 'go',
	'rust': 'rs',
	'racket': 'rkt',
}

DEFAULT_COMMENT_SYMBOL = "#"
comment_symbols = collections.defaultdict(lambda: DEFAULT_COMMENT_SYMBOL, {
	'python': '#',
	'c++': '//',
	'c': '//',
	'c#': '//',
	'haskell': '--',
	'ruby': '#',
	'go': '//',
	'rust': '//',
	'racket': ';',
})

```

`click` gives us `click.echo`, which handles python 2 / 3 inconsistencies when writing to the console.

```python
e = click.echo

```

The main regexps were ported from the official javascript implementation of the CommonMark spec. They match 3 backticks or quotes, followed potentially by an infostring.

```python
code_open_re = re.compile(r'^`{3,}(?!.*`)|^~{3,}(?!.*~)', re.MULTILINE) # /^`{3,}(?!.*`)|^~{3,}(?!.*~)/
code_close_re = re.compile(r'^(?:`{3,}|~{3,})(?= *$)', re.MULTILINE) # /^(?:`{3,}|~{3,})(?= *$)/

```

The `click` decorators are used to specify the arguments that your command-line tool takes. `click` will do the parsing automatically, and forward the parsed arguments to your decorated function.
```python
@click.command()
@click.argument("input_file", type=click.File('r'))
@click.option("--force", is_flag=True)

```

This is the main function of the code. We start with a bunch of initializations, and read the whole file into `lines`.
```python
def lyt(input_file, force):
	"""lyt extracts fenced code blocks from Markdown documents."""
	out = collections.defaultdict(str)
	lines = input_file.read()
	start_pos = 0

```


In the main loop, we're going to try to extract blocks by:
 - matching for the beginning of a block
 - optionally matching for the end of a block (the CommonMark allows a block to stay open at the end of the file.)
 - extract the relevant source and add it to the `out` dictionary, indexed by language. The language is determined by the infostring.

```python
	while True:
		open_match = code_open_re.search(lines, start_pos)
		if not open_match:
			break
		start_pos = open_match.end()
		fence_char = lines[open_match.start()]
		infostring_end_idx = lines.find("\n", open_match.end())
		infostring = lines[open_match.end():infostring_end_idx]
		
		if infostring:
			lang = infostring.split()[0]
		else:
			lang = "unknown"
		start_pos = infostring_end_idx

		found = False
		while not found:
			close_match = code_close_re.search(lines, start_pos)
			if not close_match:
				found = True
				out[lang] += lines[start_pos:]
				# Turns out it's valid to have a 'dangling' fenced block quote according to the CommonMark spec
				# e("Mismatched fenced block quotes! Check that your Markdown is valid.")
				# sys.exit(1)

			if lines[close_match.start()] == fence_char:
				found = True
				out[lang] += lines[start_pos+1:close_match.start()]
		start_pos = close_match.end()

```
We then have another loop, that will output the various values in `out` to file with the same name as the original Markdown file and extension as defined by the source language. 


```python
	lpy_ext_idx = input_file.name.rfind(".") + 1
	basename = input_file.name[:lpy_ext_idx]

	for (language, source) in out.items():
		language = language.lower()
		if language in matching_extensions:
			ext = matching_extensions[language]
		else:
			if language == "unknown":
				e("WARNING! The following blocks didn't have an infostring specifying the language. They were aggregated together and will be written to a .%s file." % DEFAULT_EXT)
				e(source)
				ext = DEFAULT_EXT
			else:
				e("Couldn't find extension to use for language %s. Using the first three letters: %s" % (language, language[:3]))
				ext = language[:3]

		output_filename = basename + ext

		if os.path.isfile(output_filename) and not force:
			e("WARNING! The file %s already exists. To allow overwriting, re-launch lyt with the --force option." % output_filename)
		else:
			with open(output_filename, "w") as output_file:
				output_file.write(comment_symbols[language] + " This file was autogenerated from %s. Please do not edit!\n" % input_file.name)
				output_file.write(source)
				e("Wrote %s." % output_filename)

```

And we finish with the standard main function.
```python
if __name__ == "__main__":
	lyt()
```

That's it!
Now go write some literate programs with `lyt`!

-- Adrien