""" This file contains the functions that create and parse query to/from XML.
Each query is an XML element ("call") with a "val" attribute. This attribute can
take the following values :
    - rewind
    - goal
    - evars
    - status
    - search
    - getoptions
    - setoptions
    - inloadpath
    - mkcases
    - hints
    - quit
    - about """

import xml.etree.ElementTree as XMLFactory
import process
from response import CoqResponse

""" This function skip  whitespaces, comments and strings from the 'fromPos'
position given. It returns the new *relevant* position.
If an error is detected, the function returns an error code which is one of
the following :
    -1: Empty bufer (no characters)
    -2: Empty buffer (only whitespaces)
    -3: Unterminated comment """

def skipComment(string, fromPos):
    """ This function return the index in the string when the comment ends. """
    # If there are several comments nested, we use a stack
    endComment = fromPos + 1
    stack = 1
    while stack > 0 and endComment < len(string):
        start_occ = string.find("(*", endComment)
        end_occ = string.find("*)", endComment)
        if end_occ > -1:
            if start_occ != -1 and start_occ < end_occ:
                stack += 1
                endComment = start_occ + 2
            else:
                stack -= 1
                endComment = end_occ + 2
        else: break
    # If stack is not 0, then the remaining code is only comment ...
    if stack > 0:
        return -3
    return endComment

def skipWhitespaces(string, fromPos):

    if len(string) == 0:
        return -1
    i = fromPos
    relevantPosFound = False
    relevantPos = -1
    while i<len(string) and not relevantPosFound:
        if string[i].strip() != '':
            relevantPos = i
            relevantPosFound = True
            break
        i += 1
    # If relevantPos==-1, then there are only whitespaces remaining ..
    if relevantPos == -1:
        return -2
    return relevantPos


def getChunk(buf, fromPos):
    """ Return either ,:
        - The code between 'fromPos' and the next dot
        - The next comment
    The dots included in comments, strings or in import path, and the nested
    comments  are ignored. Returns the chunk in a string
    of the chunk in the buffer, or False if it fails """
    relevantPos = skipWhitespaces(buf, fromPos)
    if relevantPos == -1:
        # Buffer is empty !
        return False
    elif relevantPos == -1:
        # Only whitespaces !
        return False
    (remaining, skipped) = (buf[relevantPos:], relevantPos - fromPos)
    # First, we switch depending on the next chunk type
    if remaining[:2] == "(*":
        # If it is a comment, we return it
        commentEnd = skipComment(buf, relevantPos)
        if commentEnd == -3:
            # Unterminated comment !
            return False
        return buf[fromPos : commentEnd]
    else:
        # If it's not a comment, we try to reach the next *relevant* point
        # (i.e. ignoring comments, strings and import paths)
        dotPos = 0
        while dotPos < len(remaining):
            comment_occ = remaining.find("(*", dotPos)
            string_occ = remaining.find("\"", dotPos)
            dot_occ = remaining.find(".", dotPos)
            if dot_occ == -1:
                # No ending dot !
                return False
            if(comment_occ != -1 and (string_occ == -1 or
                    comment_occ < string_occ) and comment_occ < dot_occ):
                commentEnd = skipComment(remaining, comment_occ)
                if commentEnd == -3:
                    # Unterminated comment !
                    return False
                dotPos = commentEnd
            elif(string_occ != -1 and (comment_occ == -1 or
                    string_occ < comment_occ) and string_occ < dot_occ):
                dotPos = remaining.find("\"", string_occ + 1) + 1
                if dotPos == 0: # /!\ Not -1 because we added 1 !
                    # Unterminated string !
                    return False
            else:
                # A dot is relevant only if it is followed by a space, or if it
                # is the last character of the line
                if ((remaining[dot_occ + 1:dot_occ + 2].strip() == "") or
                        (remaining[dot_occ + 1] == '\n')):

                    chunkEndPos = skipped + dot_occ + fromPos + 1
                    return buf[fromPos : chunkEndPos]
                else:
                    dotPos = dot_occ + 1
        # No ending dot !
        return False

def interp(code):
    """ This function send of piece of code as if it was typed from the coqIDE
    editor. It splits the code into coq chunks (i.e. split with the dots), and
    then send all these chunks. """
    if not process.isRunning():
        raise
    def sendChunk(chunk):
        xml = XMLFactory.Element('call')
        xml.set('val', 'interp')
        xml.set('id', '0')
        xml.text = chunk.decode('utf-8')
        return CoqResponse(process.sendXML(xml))
    # Split the code while there are chunks ..
    i = 0
    reps = []
    while i < len(code):
        chunk = getChunk(code, i)
        print(" --" + chunk + "  \n", i, code, code[i:])
        if chunk and len(chunk) >= 0:
            print(chunk + "  \n")
            reps.append(sendChunk(chunk))
            i += len(chunk)
        else:
            break
    return reps

