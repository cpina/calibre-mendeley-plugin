#!/bin/bash

rm -f mendeley.zip
zip -r mendeley.zip * --exclude @exclude.lst
