#!/usr/bin/env bash

pip install anytree
pip install requests

python ../tree_view_fre.py --server=$1  --fre_id=$2 --label=$3 >graph.log