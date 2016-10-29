__author__="nukeop"

import argparse
import logging
import logging.config
import sys

from galax.server import GalaxServer

global logger

def main(args=None):
    gs = GalaxServer()
    gs.cleanup()


def config_logging(args=None):
    global logger
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[%(levelname)s] - %(asctime)s - %(name)s - "
    "%(message)s") 
    logger = logging.getLogger()

    level = logging.NOTSET
    if args is not None:
        level = int(args.verbosity) * 10

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbosity', help='log verbosity (0-5)', default=2)
    args = parser.parse_args()

    config_logging(args)
    logger.info("Starting Galax C&C")
    main(args)
