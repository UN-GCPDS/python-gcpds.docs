# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath('../../gcpds'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'GCPDS - Docs'
copyright = '2024, Yeison Cardona'
author = 'Yeison Cardona'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'nbsphinx',
    'dunderlab.docs',
]

templates_path = ['_templates']
exclude_patterns = ['_build', '**.ipynb_checkpoints']

html_logo = '_static/logo.svg'
html_favicon = '_static/favicon.ico'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

html_theme_options = {
    'caption_font_family': 'Noto Sans',
    'font_family': 'Noto Sans',
    'head_font_family': 'Noto Sans',
    'page_width': '1280px',
    'sidebar_width': '350px',
}

dunderlab_color_links = '#FC4DB5'
dunderlab_code_reference = True

autodoc_mock_imports = ["ipywidgets", "IPython", "ipython_secrets"]
# add_module_names = False

dunderlab_custom_index = f"""

Documentation Overview
======================

This guide offers a comprehensive framework for documenting Python projects
within the GCPDS initiative, covering everything from initial setup and
configuration to best practices in code implementation.

.. toctree::
   :glob:
   :maxdepth: 2
   :name: mastertoc3
   :caption: Setting Up the Development Environment

   notebooks/01_set_up/*


.. toctree::
   :glob:
   :maxdepth: 2
   :name: mastertoc3
   :caption: Repository Structure Setup

   notebooks/02_repository_structure/*


.. toctree::
   :glob:
   :maxdepth: 2
   :name: mastertoc3
   :caption: Writing Your Python Module

   notebooks/03_python_module/*


.. toctree::
   :glob:
   :maxdepth: 2
   :name: mastertoc3
   :caption: Best Practices for Code Implementation

   notebooks/04_best_practices/*
    """


