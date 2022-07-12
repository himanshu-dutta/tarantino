#!/bin/sh -e

target=$1

if [ -z "$target" ]
  then
    target="tarantino"
fi


autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place  $target --exclude="*/__init__.py","imports.py"
black $target
isort $target
docformatter --in-place $target/*.py
docformatter --in-place $target/http/*.py
docformatter --in-place $target/websocket/*.py