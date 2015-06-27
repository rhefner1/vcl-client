#!/usr/bin/env bash

if [[ $RUN_PYLINT == true ]]
then
    echo -e "\n### Running pylint"
    pylint vcl_client --disable=no-member --disable too-few-public-methods --disable unused-argument
    pylint tests --disable=no-member --disable too-few-public-methods --disable unused-argument --disable missing-docstring --disable protected-access --disable no-self-use
fi
