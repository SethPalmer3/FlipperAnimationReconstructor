# FlipperAnimationReconstructor
---
This is a simple program that takes a directory of flipper bitmap files and a `meta.txt` file and produces a gif file that plays the animation.

## Usage

`python3 main.py flipper_directory [other_directories...] -o [output_file]`

This will go through all specified directories and creates the outputted gif files at `output_file`. If more than one directory is given the the output file will be prefixed with an index 

## WIP
Currently working on fleshing out the remove flag for the command to remove the png files that were generated.
