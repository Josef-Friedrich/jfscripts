#! /bin/sh

if [ -z "$1" ]; then
	echo "Usage: ./pick-test.sh pdf_compress.py

or

./pick-test.sh pdf_compress.py:TestIntegration

or

./pick-test.sh pdf_compress.py:TestIntegration.test_command_line_interface

"

	exit 1
fi

tox -e py3 -- test/test_$1
