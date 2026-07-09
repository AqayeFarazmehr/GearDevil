#!/bin/bash

# Install Nuitka if not present
#pip install nuitka 2>/dev/null

# Compile with Nuitka
nuitka \
    --standalone \
    --onefile \
    --enable-plugin=tk-inter \
    --remove-output \
    --assume-yes-for-downloads \
    --windows-disable-console \
    --output-dir="dist" \
    geardevil.py

echo "Build complete! Executable in dist/ folder"
