""" This file only contains the init function that import all the other files.
It is not intended to contain more functions. """

import process
import interface

def initCoq(args):
    """ This function launch the coq process and initialize an interface object
    to communicate with the process.
    It is the entry point of the API.
    If this function is called several times, it clear all the previously
    instanciated objects. """
    process.launch(args)
    return interface.CoqInterface()

