#!/bin/bash

rm *.zip 

VERSION=$(./get-plugin-version.py)
PACKAGE="mendeley-$VERSION.zip"

zip -r "$PACKAGE" * --exclude @exclude.lst

echo
echo "Generated: $PACKAGE"
echo "Perhaps you want: scp $PACKAGE carles@pina.cat:/var/www/carles.pina.cat/calibre"
echo "Link: http://pinux.info/calibre/$PACKAGE"
