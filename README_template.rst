{{ badge.pypi }}

{{ badge.github_workflow() }}

{{ badge.readthedocs }}

jfscripts
=========

{{ github.description | wordwrap }}

{% for command in [
                   'dns-ipv6-prefix.py',
                   'extract-pdftext.py',
                   'find-dupes-by-size.py',
                   'list-files.py',
                   'mac-to-eui64.py',
                   'image-into-pdf.py'
                  ]
%}

{{ command | heading(2) }}

{{ cli('{} --help'.format(command)) | literal }}
{% endfor %}
