#!/bin/bash
set -e

CONFIG=$1

GET_PIP="https://bootstrap.pypa.io/get-pip.py"
VERSION_CFG="https://raw.githubusercontent.com/eea/eea.plonebuildout.core/master/buildout-configs/versions.cfg"

PIP=$(curl -sL $VERSION_CFG | grep "pip\s*=\s*" | sed 's/^.*\=\s*//g')
SETUPTOOLS=$(curl -SL $VERSION_CFG | grep "setuptools\s*\=\s*" | sed 's/ *//g' | sed 's/=//g' | sed 's/[a-z]//g')
ZCBUILDOUT=$(curl -SL $VERSION_CFG | grep "zc\.buildout\s*=\s*" | sed 's/^.*\=\s*//g')

if [ -z "$CONFIG" ]; then
  if [ -s "development.cfg" ]; then
    CONFIG="development.cfg"
  else
    CONFIG="buildout.cfg"
  fi
fi

echo ""
echo "Using $CONFIG"
echo ""

if [ -z "$PIP" ]; then
  PIP="9.0.1"
fi

echo "Using pip $PIP"
echo ""

if [ -z "$SETUPTOOLS" ]; then
  SETUPTOOLS="33.1.1"
fi

echo "Using setuptools $SETUPTOOLS"
echo ""

if [ -z "$ZCBUILDOUT" ]; then
  ZCBUILDOUT="2.9.3"
fi

echo "Using zc.buildout $ZCBUILDOUT"
echo ""

if [ -z "$PYTHON" ]; then
  PYTHON="/usr/bin/env python2.7"
fi

# Make sure python is 2.7 or later
PYTHON_OK=`$PYTHON -c 'import sys
print (sys.version_info >= (2, 7) and "1" or "0")'`

if [ "$PYTHON_OK" = '0' ]; then
    echo "ERROR: Python 2.7 or later is required"
    echo "       EXAMPLE USAGE: PYTHON=/path/to/python2.7 ./install.sh"
    exit 0
fi

echo "Using Python: $($PYTHON --version)"

echo "Adding eggs directory"
mkdir -vp eggs

if [ ! -s "get-pip.py" ]; then
  curl -o "get-pip.py" -SL $GET_PIP
fi

if [ -s "bin/activate" ]; then

  echo ""
  echo "WARNING: Already a virtualenv environment."
  echo "WARNING: Please remove bin/activate if you want to reinitiate it."
  echo ""

else

  echo "Installing virtualenv"
  # NOTE: virtualenv now doesn't download anything by default, so we need to provide setuptools
  curl -o "/tmp/virtualenv.py" -SL "https://raw.githubusercontent.com/pypa/virtualenv/15.1.0/virtualenv.py"

  echo "Running: $PYTHON /tmp/virtualenv.py --clear --no-setuptools --no-pip --no-wheel ."
  $PYTHON /tmp/virtualenv.py --clear --no-setuptools --no-pip --no-wheel .
  rm -v /tmp/virtualenv.py*

  echo "Running: bin/python get-pip.py pip==$PIP setuptools==$SETUPTOOLS zc.buildout==$ZCBUILDOUT"
  ./bin/python get-pip.py pip==$PIP setuptools==$SETUPTOOLS zc.buildout==$ZCBUILDOUT

fi

echo "Disabling the SSL CERTIFICATION for git"
git config --global http.sslVerify false

echo ""
echo "========================================================================="
echo "All set. Now you can run ./bin/buildout -c $CONFIG"
echo "========================================================================="
echo ""
