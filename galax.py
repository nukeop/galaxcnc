__author__="nukeop"

import argparse
import logging
import logging.config
import sys

from galax.server import GalaxServer

global logger

def main():
    parser = argparse.ArgumentParser()
    gs = GalaxServer()
    gs.cleanup()


def config_logging():
    global logger
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[%(levelname)s] - %(asctime)s - %(name)s - "
    "%(message)s") 
    logger = logging.getLogger()

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.NOTSET)

if __name__=='__main__':
    config_logging()
    logger.info("Starting Galax C&C")
    main()
