import logging
import os
import time

import galax.channels
import galax.crypto
import galax.database
import galax.decrypter

logger = logging.getLogger(__name__)


class GalaxServer(object):
    """Main class initializing and performing high level tasks.
    Loads communication channels
    """
    def __init__(self):
        logger.info("Creating Galax server instance")

        self.crypto = galax.crypto.Crypto()
        self.decrypter = galax.decrypter.Decrypter(self)
        self.db = galax.database.Database()

        self.channels = []
        self.import_channels()

        for channel in galax.channels.channel.Channel.__subclasses__():
            channelinst = channel(self, self.on_msg)
            self.channels.append(channelinst)

        logger.info("All comms channels initialized")

        self.run()


    def import_channels(self):
        logger.info("Scanning channels...")
        files = os.listdir(os.path.join(os.path.dirname(__file__),
                                        galax.channels.__name__.split('.')[-1]))
        files = [os.path.splitext(x)[0] for x in files if
                 os.path.splitext(x)[1] == ".py"
                 and "__init__" not in x]

        for module in files:
            logger.info("Detected channel: {}".format(module))
            try:
                __import__("galax.channels.{}".format(module))
            except Exception as e:
                logger.error("Invalid channel: %s", module)
                logger.error(str(e))


    def run(self):
        """Main execution loop.
        """
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Received Ctrl-C, cleaning up and quitting")
            self.cleanup()


    def send_plaintext(self, msg):
        """Send a plaintext message on all channels.
        """
        for channel in self.channels:
            channel.send_plaintext(msg)


    def send_encrypted(self, msg):
        """Send an encrypted message on all channels.
        """
        for channel in self.channels:
            channel.send_encrypted(msg)


    def on_msg(self, source, text):
        logger.debug("{}: {}".format(source, text))
        decrypted = self.decrypter.add_msg(source, text)
        if decrypted is not None:
            self.handle_decrypted(decrypted[0], decrypted[1])


    def handle_decrypted(self, user, msg):
        logger.info("Got message from {}: {}".format(user, msg))


    def cleanup(self):
        """Clean up everything.
        """
        for channel in self.channels:
            channel.cleanup()

        self.db.cleanup()
