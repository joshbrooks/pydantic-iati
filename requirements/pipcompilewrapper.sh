#!/bin/sh
export CUSTOM_COMPILE_COMMAND="./pipcompilewrapper"
pip-compile -U base.in
pip-compile -U test.in
pip-compile -U dev.in
pip-compile -U jupyterlab.in
