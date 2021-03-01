#!/bin/bash

set -ex

cd dockers
./build.sh
cd ..

# Note: add "-it" after "run" to run bash
docker run --rm --privileged --platform=linux/arm -v$(pwd):/root/src:Z display:0.1 ls

