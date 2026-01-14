import sys

def print_error(message: str) -> None:
    '''
    Prints an error to stderr.
    
    :param message: The error to print
    :type message: str
    '''
    print(message, file=sys.stderr)
    