#!/bin/bash 
set -euo pipefail


SOURCE=$(readlink -f ${BASH_SOURCE[0]})
DIR=$(dirname "${SOURCE}")

cd "${DIR}/../";
mkdir "_build" || true 2>/dev/null;
cd "_build";
cmake ..;
make -j;
cd "${DIR}"; 

