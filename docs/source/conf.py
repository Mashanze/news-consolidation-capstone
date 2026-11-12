# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Django News Application'
copyright = '2026, News Application Developer'
author = 'News Application Developer'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']


import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "news_project.settings")

# Provide documentation-only configuration without committing secrets.
os.environ.setdefault(
    "DJANGO_SECRET_KEY",
    "sphinx-documentation-only-placeholder-not-for-production",
)

import django
django.setup()

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
