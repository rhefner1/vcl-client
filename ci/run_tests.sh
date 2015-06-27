#!/usr/bin/env bash

if [[ $RUN_TESTS == true ]]
then
    echo -e "\n### Running unit tests"
    python -m unittest discover
fi
