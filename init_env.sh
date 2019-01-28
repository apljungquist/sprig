#!/usr/bin/env bash

if [[ ! -e venv ]] ; then
    python -m venv --prompt $(basename $(pwd)) venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

export PATH="$(pwd)/bin:${PATH}"
