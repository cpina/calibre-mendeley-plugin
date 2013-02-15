#!/bin/bash

rm *.zip 

VERSION=$(./get-plugin-version.py)
PACKAGE="mendeley-$VERSION.zip"

zip -r "$PACKAGE" * --exclude @exclude.lst

echo
echo "Generated: $PACKAGE"
