#!/usr/bin/env python
import os
import sys


def like_cheese():
    var = input("Hi! I like cheese! Do you like cheese?").lower()
    if var == "yes":
        print("That's awesome!")


if __name__ == '__main__':
    like_cheese()
    # Run a new iteration of the current script, providing any command line args from the current iteration.
    os.execv(__file__, sys.argv)
    exit()
