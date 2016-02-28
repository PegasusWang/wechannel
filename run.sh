#!/bin/bash

PREFIX=$(cd "$(dirname "$0")"; pwd)
cd $PREFIX

rm -r ./_templates/*
./app.py
