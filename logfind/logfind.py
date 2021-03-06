from argparse import ArgumentParser
from os import path, listdir, getcwd
from re import compile

verbosity = 0


def debug_print( s, lvl = 0 ):
    """ Prints out the given string if the verbosity level is greater than
        lvl
        * s: the string to print
        * lvl: (optional) the verbosity level required to print
    """
    global verbosity

    # don't print this if we're above the verbosity limit
    if lvl > verbosity :
        return

    print( "** {}".format( s ) )


def create_argument_parser():
    """ Creates our program's argument parser
        Add new arguments here!
    """
    parser = ArgumentParser( description = 'Prints a list of log files containing the given strings' )
    parser.add_argument( 
        'search', 
        help = 'gets files containing the given words', 
        nargs = '+' 
    )
    parser.add_argument(
        '-c', '--config',
        help = 'specifies a different config file (default .logfind)',
        default = '.logfind'
    )
    parser.add_argument( 
        '-o', 
        help = 'uses OR logic when searching files', 
        action = 'store_true' 
    )
    parser.add_argument( 
        '-v', '--verbose', 
        help = 'prints more verbose debug information', 
        action = 'count',
    )
    return parser
    

def parse_arguments( args = None ):
    """ Parses the arguments passed into our program
        * args: (optional) arguments to use other than argv
    """
    parser = create_argument_parser()
    return parser.parse_args( args )


def read_config_file( file ):
    """ Reads the contents of the given configuration file and returns a
        list of filename regexes to search for
    """
    # make sure we've received an actual file
    if not file :
        debug_print(
            'error reading config file: config file was None',
            lvl = 1
        )
        return []

    fnames = []

    # loop over the file line by line
    for line in file :
        fname = path.split( line[:-1] ) # separate directories and filenames
        try :
            if not fname[1]:
                # if we don't have a filename, match everything
                fname = ( fname[0], compile('.+') )
            else :
                fname = ( fname[0], compile( fname[1] ) )

            fnames.append( fname )
        except sre_constants.error as e :
            debug_print( 
                'error in regex: {}\nthe line was skipped'.format( e ), 
                lvl = 1 
            )

    return fnames


def get_matching_files( fname ):
    """ Returns a list of files matching the given split path and regex
    """
    if not path.exists( fname[0] ):
        debug_print(
            'directory does not exist: {}\nskipping...'.format( fname[0] ),
            lvl = 1
        )
        return []
    
    fname = ( path.join( getcwd(), fname[0] ), fname[1] )
    files = listdir( fname[0] )
    newfiles = []

    for file in files :
        fullfile = path.normpath( path.join( fname[0], file ) )
        if path.isfile( fullfile ) and fname[1].fullmatch( file ):
            newfiles.append( fullfile )

    return newfiles


def get_files_with_words( files, words, use_or = False ):
    """ Returns a list of files with the given args in them
    """
    newfiles = []
    for filename in files :
        with open( filename ) as f :
            if use_or :
                # when doing an or search, add it if we find any word
                for word in words:
                    if word in f.read():
                        newfiles.append( filename )
                        break
            else :
                # otherwise we have to check that every word passes
                for word in words:
                    if not word in f.read():
                        break
                else :
                    newfiles.append( filename )

    return newfiles


def main():
    global verbosity

    # get our arguments
    args = parse_arguments()
    verbosity = args.verbose

    # get the list of files we're checking
    filenames = []
    with open(args.config) as f:
        fsearch = read_config_file( f )
        for fname in fsearch :
            filenames += get_matching_files( fname )

    # filter down to the files with our arguments
    files = get_files_with_words( filenames, args.search, use_or = args.o )
    for file in files:
        print( file )


if __name__ == "__main__" :
    main()
