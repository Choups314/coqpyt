""" This file contains all the functions that interact with the coqtop process.
If the process die, an exception will be raised in any API function call to
prevent any unexpected behaviour. The API user may then re-call the initCoq()
function. """

import subprocess
import os
import signal
import xml.etree.ElementTree as XMLFactory

""" The coqtop process. If a function try to use it while it is None, an
exception is raised. """
_coqtop = None

def isRunning():
    global _coqtop
    return _coqtop != None

""" Each time the coqtop process is about to start, we first store the result of
'coqtop --version' in _coqtopVersion. """
_coqtopVersion = ''

def kill():
    """ This function kill the current coqtop process (if there is one running)
    """
    global _coqtop
    if isRunning():
        try:
            _coqtop.terminate()
            _coqtop.communicate() 	# Clear the pipe
        except OSError:
            pass
    _coqtop = None

def launch(args):
    """ This function launch a new process of coqtop """
    global _coqtop
    global _coqtopVersion
    kill()
    _coqtopVersion = subprocess.check_output(['coqtop', '--version'])
    _coqtop = subprocess.Popen(
            # We need -ide-slave to be able to send XML queries
            ['coqtop', '-ideslave'] + args,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            preexec_fn = lambda:signal.signal(signal.SIGINT, signal.SIG_IGN))

def sendXML(xml):
    """ First, check wether the coq process is still running.
    Then, send the XML command, and finally wait for the response """
    global _coqtop
    if _coqtop == None:
        raise
    try:
        _coqtop.stdin.write(XMLFactory.tostring(xml, 'utf-8'))
    except IOError:
        kill()
        return None
    response = ''
    file = _coqtop.stdout.fileno()
    while True:
        try:
            response += os.read(file, 0x4000)
            try:
                rep = XMLFactory.fromstring(response)
                return rep
            except XMLFactory.ParseError:
                continue
        except OSError:
            return None

