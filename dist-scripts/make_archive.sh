#!/bin/sh

if [ "$1" == '-h' ] ; then
    echo "Usage: `basename $0` [version]"
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VERSION=`cat $SCRIPT_DIR/../VERSION`
VERSION=${1:-$VERSION}

ARCHIVE_DIR="meetlogindex-${VERSION}"

rm -rf $ARCHIVE_DIR
mkdir $ARCHIVE_DIR

cp -p --parents ./dist-scripts/{*.spec,*.cfg} $ARCHIVE_DIR
cp -p --parents ./meetlogindex/*.py $ARCHIVE_DIR
cp -p ./README.* ./LICENSE MANIFEST.in $ARCHIVE_DIR
cp -p ./setup.py $ARCHIVE_DIR

tar -pczvf "${ARCHIVE_DIR}.tar.gz" $ARCHIVE_DIR

rm -rf $ARCHIVE_DIR

