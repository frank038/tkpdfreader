#!/bin/bash
thisdir=$(dirname "$0")
cd $thisdir
./pdfViewer.py "$@"
