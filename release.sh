#! /usr/bin/env bash

set -eu -o pipefail

# Verify that PyPi package display is valid
echo "Checking PyPi package HTML"
if ! python setup.py --long-description | rst2html.py --strict > /dev/null; then
    echo
    echo "Error: invalid package display; check README.md"
    exit 1
fi

# Create git tag
VERSION=$(python -c "import pylastfm; print(pylastfm.__version__)")
git fetch --tags origin
if git show $VERSION 2> /dev/null; then
    echo "pylastfm $VERSION has already been released; please make another commit to bump the version" >&2
    exit 1
else
    git tag -a $VERSION -m "Release $VERSION" HEAD
    git push --tags origin
fi

# Build package
rm -rf build dist
python setup.py sdist bdist_wheel

# Upload to PyPi
twine upload -u thesquelched dist/*
