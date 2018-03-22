import sphinx_rtd_theme
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]
templates_path = ['_templates']
source_suffix = '.rst'

master_doc = 'index'

project = u'jfscripts'
copyright = u'2016, Josef Friedrich'
author = u'Josef Friedrich'
version = u'0.0.5'
release = u'0.0.5'
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = False
html_static_path = []
htmlhelp_basename = 'jfscriptsdoc'
