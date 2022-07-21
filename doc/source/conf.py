import sphinx_rtd_theme

import jfscripts

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

extensions = []
extensions += ["sphinx.ext.autodoc"]
extensions += ["sphinx.ext.intersphinx"]
extensions += ["sphinx.ext.viewcode"]
extensions += ["sphinxarg.ext"]

templates_path = ["_templates"]
source_suffix = ".rst"

master_doc = "index"

project = "jfscripts"
copyright = "2018, Josef Friedrich"
author = "Josef Friedrich"
version = jfscripts.__version__
release = jfscripts.__version__
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"
todo_include_todos = False
html_static_path = []
htmlhelp_basename = "jfscriptsdoc"
autodoc_default_flags = [
    "members",
    "undoc-members",
    "private-members",
    "show-inheritance",
]
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
