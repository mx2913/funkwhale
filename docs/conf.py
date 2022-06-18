#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# funkwhale documentation build configuration file, created by
# sphinx-quickstart on Sun Jun 25 18:49:23 2017.
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
import datetime

sys.path.insert(0, os.path.abspath("../api"))
sys.path.insert(0, os.path.abspath("../api/config"))

import funkwhale_api  # NOQA

FUNKWHALE_CONFIG = {
    "FUNKWHALE_URL": "mypod.funkwhale",
    "FUNKWHAL_PROTOCOL": "https",
    "DATABASE_URL": "postgres://localhost:5432/db",
    "AWS_ACCESS_KEY_ID": "my_access_key",
    "AWS_SECRET_ACCESS_KEY": "my_secret_key",
    "AWS_STORAGE_BUCKET_NAME": "my_bucket",
}
for key, value in FUNKWHALE_CONFIG.items():
    os.environ[key] = value
# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.graphviz",
    "sphinx.ext.autodoc",
    "myst_parser",
    "sphinx_panels",
    "sphinx_multiversion",
]
autodoc_mock_imports = [
    "celery",
    "django_auth_ldap",
    "ldap",
    "persisting_theory",
    "rest_framework",
]
add_module_names = False
# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The root toctree document.
root_doc = "index"

# Autogenerate anchors

myst_heading_anchors = 3

# General information about the project.
year = datetime.datetime.now().year
project = "funkwhale"
copyright = "{}, The Funkwhale Collective".format(year)
author = "The Funkwhale Collective"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
# Read version from the API
version = funkwhale_api.__version__
release = version

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}
html_context = {
    "display_gitlab": True,
    "gitlab_host": "dev.funkwhale.audio",
    "gitlab_repo": "funkwhale",
    "gitlab_user": "funkwhale",
    "gitlab_version": "stable",
    "conf_py_path": "/docs/",
    "gitlab_url": "https://dev.funkwhale.audio/funkwhale/funkwhale",
}
html_logo = "logo.svg"
html_favicon = "../front/public/favicon.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = [
    "css/translation-hint.css",
]
html_js_files = [
    "js/translation-hint.js",
]

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "funkwhaledoc"


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        root_doc,
        "funkwhale.tex",
        "funkwhale Documentation",
        "The Funkwhale Collective",
        "manual",
    )
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(root_doc, "funkwhale", "funkwhale Documentation", [author], 1)]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        root_doc,
        "funkwhale",
        "funkwhale Documentation",
        author,
        "funkwhale",
        "One line description of project.",
        "Miscellaneous",
    )
]

# -- Build legacy redirect files -------------------------------------------

# Define list of redirect files to be build in the Sphinx build process

redirect_list = []
with open('redirects.txt', 'r') as fp:
    data_list = [tuple(line.strip().split(",")) for line in fp]

# Generate redirect template

redirect_template = """\
<html>
  <head>
    <meta http-equiv="refresh" content="1; url={new}" />
    <script>
      window.location.href = "{new}"
    </script>
  </head>
</html>
"""

# Tell Sphinx to copy the files


def copy_legacy_redirects(app, docname):
    if app.builder.name == "html":
        for html_src_path, new in data_list:
            page = redirect_template.format(new=new)
            target_path = app.outdir + "/" + html_src_path
            if not os.path.exists(os.path.dirname(target_path)):
                os.makedirs(os.path.dirname(target_path))
            with open(target_path, "w") as f:
                f.write(page)


def setup(app):
    app.connect("build-finished", copy_legacy_redirects)


smv_tag_whitelist = None
smv_branch_whitelist = r"(stable|develop)$"

# Internationalization settings
locale_dirs = ["locales/"]
gettext_compact = False
