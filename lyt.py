"""Lyt is a literate programming script written in Python. It uses Markdown as a textual language and extracts fenced block quotes from the Markdown file into source code files. It takes a list of Markdown-formatted files as input, and from each file, will extract all the fenced block quotes into a file with the same name but the extension of the language in the fenced code block. To detect the language, it will either use the infostring (if present), or autodetect if not. It is possible to also just specify the language as part of the command line options. In case multiple languages are present in the same Markdown file, it will try to extract various source files with the same name, but different extensions.

"""


import re
import collections
import click
import sys

matching_extensions = {
	'python': 'py',
	'c++': 'cpp',
	'c': 'c',
}

e = click.echo

code_open_re = re.compile(r'^`{3,}(?!.*`)|^~{3,}(?!.*~)', re.MULTILINE) # /^`{3,}(?!.*`)|^~{3,}(?!.*~)/
code_close_re = re.compile(r'^(?:`{3,}|~{3,})(?= *$)', re.MULTILINE) # /^(?:`{3,}|~{3,})(?= *$)/


@click.command()
@click.argument("input_file", type=click.File('r'))
def lyt(input_file) -> None:
	"""Literate programming using python."""
	out = collections.defaultdict(str)
	lines = input_file.read()
	start_pos = 0

	while True:
		open_match = code_open_re.search(lines, start_pos)
		if not open_match:
			break
		start_pos = open_match.end()
		fence_char = lines[open_match.start()]
		infostring_end_idx = lines.find("\n", open_match.end())
		infostring = lines[open_match.end():infostring_end_idx]
		lang = infostring.split()[0]
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
				out[lang] += lines[start_pos:close_match.start()]
		start_pos = close_match.end()

	for (language, source) in out.items():
		lpy_ext_idx = input_file.name.rfind(".") + 1
		output_filename = input_file.name[:lpy_ext_idx] + matching_extensions[language.lower()]
		# e(output_filename)
		# e(source)
		with open(output_filename, "w") as output_file:
			e("Wrote %s." % output_filename)
			output_file.write(source)



if __name__ == "__main__":
	lyt()
