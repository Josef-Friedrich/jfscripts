#! /usr/bin/env python3

from unittest import mock

def setup(**kwargs):
    return kwargs


with mock.patch('setup'):
    import setup
