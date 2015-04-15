""" The CoqInterface class wrap all the API high-level functions that allow to
interact with the coqtop process. """

import process
import query

class CoqInterface:

    def __init__(self):
        if not process.isRunning():
            raise

    # Interp functions
    def interp(self, code):
        """ Send Vernacular code as if it was typed in the coqtop input. """
        return query.interp(code)

    # Misc functions
    def alive(self):
        """ Return True if the coqtop proccess is still runing, False otherwise.
        """
        return process.isRunning()

