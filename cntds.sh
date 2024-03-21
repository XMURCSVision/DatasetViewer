#! /bin/bash
cd $(dirname $0)
python ./src/cnt.py $*
cd -
