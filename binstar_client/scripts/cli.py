'''
Binstar command line utility
'''
from __future__ import print_function, unicode_literals
from argparse import ArgumentParser
from binstar_client import __version__ as version
from binstar_client.commands import sub_commands
from binstar_client.commands.login import interactive_login
from binstar_client.errors import BinstarError, ShowHelp, Unauthorized
from binstar_client.utils import USER_LOGDIR
from binstar_client.utils.handlers import MyStreamHandler
from logging.handlers import RotatingFileHandler
from os import makedirs
from os.path import join, exists
import logging


logger = logging.getLogger('binstar')

def setup_logging(args):
    if not exists(USER_LOGDIR): makedirs(USER_LOGDIR)

    logger = logging.getLogger('binstar')
    logger.setLevel(logging.DEBUG)

    error_logfile = join(USER_LOGDIR, 'cli.log')
    hndlr = RotatingFileHandler(error_logfile, maxBytes=10 * (1024 ** 2), backupCount=5,)
    hndlr.setLevel(logging.INFO)
    logger.addHandler(hndlr)

    shndlr = MyStreamHandler()
    shndlr.setLevel(args.log_level)
    logger.addHandler(shndlr)

def main(args=None, exit=True):
    
    
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--show-traceback', action='store_true')
    parser.add_argument('-t', '--token')
    parser.add_argument('-v', '--verbose',
                        action='store_const', help='print debug information ot the console',
                        dest='log_level',
                        default=logging.INFO, const=logging.DEBUG)
    parser.add_argument('-q', '--quiet',
                        action='store_const', help='Only show warnings or errors the console',
                        dest='log_level', const=logging.WARNING)
    parser.add_argument('-V', '--version', action='version',
                        version="%%(prog)s Command line client (version %s)" % (version,))
    subparsers = parser.add_subparsers(help='commands')

    for command in sub_commands():
        command.add_parser(subparsers)

    args = parser.parse_args(args)

    setup_logging(args)
    try:
        try:
            return args.main(args)
        except Unauthorized as err:
            if not args.token:
                logger.info('The action you are performing requires authentication, please sign in:')
                interactive_login()
                return args.main(args)
            else:
                raise

    except ShowHelp as err:
        args.sub_parser.print_help()
        if exit:
            raise SystemExit(1)
        else:
            return 1
        
    except (BinstarError, KeyboardInterrupt) as err:
        if args.show_traceback:
            raise
        if hasattr(err,'message'):
            logger.exception(err.message)
        elif hasattr(err,'args'):
            logger.exception(err.args[0] if err.args else '')
        else:
            logger.exception(str(err))
        if exit:
            raise SystemExit(1)
        else:
            return 1 
        
