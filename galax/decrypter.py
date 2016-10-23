import logging

logger = logging.getLogger(__name__)

class Decrypter(object):
    """IRC messages will necessarily be fragmented.
    This utility keeps track of the last few messages from each client, reconstructs ciphertexts, and attempts to decrypt them.
    """
    def __init__(self, server):
        self.msgs = {}
        self.msg_limit = 4
        self.server = server
        logger.info("Decrypting module initialized")

    def add_msg(self, user, msg):
        try:
            self.msgs[user].append(msg)
        except KeyError:
            self.msgs[user] = [msg]

        if len(self.msgs[user]) == self.msg_limit:
            msg = "".join(self.msgs[user])
            msg = self.server.crypto.decrypt(msg)
            return (user, msg)

        return None
