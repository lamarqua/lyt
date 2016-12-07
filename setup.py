from setuptools import setup, find_packages

def readme():
	with open("README.md") as f:
		return f.read()

setup(
	name='lyt',
	version='0.2',
	packages=find_packages(),
	description='Simple literate programming in Markdown',
	long_description=readme(),
	url='https://github.com/lamarqua/lyt',
	author='Adrien Lamarque',
	author_email='ad@lamarque.fr',
	license='GPLv3',
	py_modules=['lyt'],
	install_requires=[
		'Click',
	],
	entry_points='''
		[console_scripts]
		lyt=lyt:lyt
	''',
)
