#!/bin/bash

# Koo and NanScan
#export PYTHONPATH=/home/albert/python/lib/python:../../bin:../../..
# NanScan
export PYTHONPATH=..:/home/albert/d/koo
export LD_LIBRARY_PATH=/usr/lib
./planta.py $1
