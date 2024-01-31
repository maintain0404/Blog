#!/bin/bash

# Move git project root directory.
cd $(git rev-parse --show-toplevel)

# Build
hugo

# Move public submodule
cd public

# commit submodule
git add .
git commit
