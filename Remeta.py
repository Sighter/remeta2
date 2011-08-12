#!/usr/bin/python3

# Remeta.py -- main file for remeta
# @Author:      The Sighter (sighter@resource-dnb.de)
# @License:     GPL
# @Created:     2011-07-18.
# @Revision:    0.1

import sys

from Helpers import ePrint

from Settings import Settings
from Main import Main

def Remeta():


    # create an settings object and, which parses
    # arguemnts and sets default options
    ePrint(0, Remeta.__name__, "parsing arguments")
    settings = Settings(sys.argv[1:])

    # create a main instance and run it
    main = Main(settings)

    main.Run()


if __name__ == "__main__":
    Remeta()

