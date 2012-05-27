#!/bin/bash

#Install an actual solver
aptitude install glpk

#Install the python wrapper
aptitude install pip
pip install pulp
