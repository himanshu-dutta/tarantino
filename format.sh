#!/bin/sh -e

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place  tarantino --exclude="*/__init__.py","imports.py"
black tarantino
isort tarantino