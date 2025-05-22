import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

project = 'artwork-embedder'
copyright = '2025, Your Name'
author = 'Your Name'
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'alabaster'
html_static_path = ['_static']

