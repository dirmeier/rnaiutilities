#!/usr/bin/env python3

# -*- coding: utf-8 -*-
#
# rnaiutilities documentation build configuration file, created by
# sphinx-quickstart on Tue Jul  4 09:13:48 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

import os
import sys
import sphinx_fontawesome

sys.path.insert(0, os.path.abspath('../../'))


extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.mathjax',
              'sphinx.ext.viewcode',
              'sphinxcontrib.fulltoc',
              'sphinx_fontawesome']
templates_path = ['_templates']
suppress_warnings = ['image.nonlocal_uri']

source_suffix = '.rst'
master_doc = 'index'

project = 'rnaiutilities'
copyright = '2017, Simon Dirmeier'
author = 'Simon Dirmeier'


language = None

exclude_patterns = []


pygments_style = 'sphinx'
todo_include_todos = False

html_show_sourcelink = False
html_show_sphinx = False

html_theme = 'alabaster'
html_theme_options = {
    'show_powered_by': False,
    'github_user': 'dirmeier',
    'note_bg': '#FFF59C',
    'sidebarwidth': 5
}
html_sidebars = {
    'index':    ['logo.html', 'sidebarintro.html'],
    '**':       ['logo.html', 'localtoc.html']
}
html_title = ""
html_static_path = ['_static']
htmlhelp_basename = 'rnaiutilitiesdoc'
