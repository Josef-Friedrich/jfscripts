{{ badge.pypi }}

{{ badge.github_workflow() }}

{{ badge.readthedocs }}

*********
jfscripts
*********

A collection of my personal Python scripts.

{% for command in [
                   'dns-ipv6-prefix.py',
                   'extract-pdftext.py',
                   'find-dupes-by-size.py',
                   'list-files.py',
                   'mac-to-eui64.py',
                   'pdf-compress.py',
                   'image-into-pdf.py'
                  ]
%}

``{{ command }}``

{{ cli('{} --help'.format(command)) | literal }}
{% endfor %}
