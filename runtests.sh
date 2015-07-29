#! /bin/bash

pushd tests/h_t_comp
python ./hypomod_taup_comparison.py || exit 1
popd

