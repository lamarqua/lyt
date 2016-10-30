from setuptools import setup

setup(
	name='lyt',
	version='0.1',
	py_modules=['lyt'],
	install_requires=[
		'Click',
	],
	entry_points='''
		[console_scripts]
		lyt=lyt:lyt
	''',
)
