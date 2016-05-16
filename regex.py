import re, string

# Constants

_loglim = 50

class SedError(Exception):
    """
    Raised when the format for substituion is incorrect
    """
    pass

def _validate_slashes(segments):
    """
    Determines whether the input uses the correct formatting
    for replacement cases.

    If everything is fine, nothing happens. If there
    is an error, the SedError exception is raised.
    """
    if len(segments) != 3:
        raise SedError("Missing \'/\' in the body of pattern.")

def _validate_flags(segments):
    """
    Determines whether the input uses valid
    flags for regular expressions.

    If everything is fine, nothing happens. If there
    is an error, the SedError exception is raised.
    """
    if re.findall('[^ig]', segments[2]):
        raise SedError("Unknown flag for regular expression.")

def _parse_log(expression, loglist):
    """
    Find the most recent match of the user-
    input regular expression in the log.

    There is a hard cutoff for this (Default: 50).

    Returns a boolean True and the match if found
    otherwise returns False and None.
    """
    for i in range(1,_loglim+1):
        match = loglist[-i]['message']
        if expression.findall(match):
            return True, loglist[-i]
    else:
        return False, None

def _positions(text, char):
    """
    A function to determine the indices in a string where
    characters are located.

    Returns a list of indices.
    """
    return [pos for pos, c in enumerate(text) if c == char]

def _sedsplit(text):
    """
    A function rigged to only split sed strings at non-escaped slashes.

    Returns a list of strings, separating `text` at the sed-style
    / separators.
    """
    split = []
    newstring = ""
    indices = _positions(text, "/")
    lastind = 0
    for i in range(0, len(indices)):
        if text[indices[i]-1] == "\\":
            newstring += text[lastind:indices[i]-1] + "/"
        else:
            newstring += text[lastind:indices[i]]
            split.append(newstring)
            newstring = ""
        lastind = indices[i] + 1
    if text[lastind:]:
        split.append(text[lastind:])
    else:
        split.append("")
    return split

class Regex():
    """
    A class that evaluates regular expression substitutions
    for IRC messages.

    The syntax for replacements is that of GNU `sed`:

    s/<Regex for text to be changed>/<Replacement text>/
    """

    def __init__(self, logger):
        self.log = logger

    def replace(self, content):
        """
        The actual substitution function.

        Given the user message, validate the format
        then determine the appropriate line to substitute
        using parse_log.

        The multiline flag is not included in this function
        because for this purpose it seems illogical.
        """
        text = content['message']
        text = re.sub('s/', '', text)
        segments = _sedsplit(text)
        chanlog = self.log.data[content['channel']]
        try:
            _validate_slashes(segments)
        except SedError:
            content['message'] = "Your use of slashes is incorrect."
            return content
        try:
            _validate_flags(segments)
        except SedError:
            content['message'] = "\'" + segments[2] + "\' contains invalid flags."
            return content
        try:
            if 'i' in segments[2]:
                test = re.compile(segments[0], re.IGNORECASE)
            else:
                test = re.compile(segments[0])
            matchconfirm, matcheddict = _parse_log(test, chanlog)
            if not matchconfirm:
                content['message'] = "A recent match was not found."
                return content
            if 'g' in segments[2]:
                out, _ = test.subn(segments[1], matcheddict['message'])
            else:
                out, _ = test.subn(segments[1], matcheddict['message'], count=1)
            content['message'] = "<" + matcheddict['name'] + "> " + out
            return content
        except re.error:
            content['message'] = "The regular expression incurred an error."
            return content
