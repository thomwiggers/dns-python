#!/bin/bash

set -e

case "$(python3 --version 2>&1)" in
    *" 3.4"*)
        echo "Correct python3 version, using python 3.4"
        ;;
    *)
        echo "Wrong python3 version! exiting"
        exit 1
        ;;
esac

echo ""

virtualenv -p `which python3` /tmp/virtualenv
source /tmp/virtualenv/bin/activate

pip install -e .

python3 ./setup.py test

./tests/test_client.sh
./tests/test_server.sh
