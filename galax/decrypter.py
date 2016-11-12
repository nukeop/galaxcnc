import base64
import json
import logging

logger = logging.getLogger(__name__)

class Decrypter(object):
    """IRC messages will necessarily be fragmented.
    This utility keeps track of the last few messages from each client, reconstructs ciphertexts, and attempts to decrypt them.
    """
    def __init__(self, server):
        self.msgs = {}
        self.server = server
        logger.info("Decrypting module initialized")

    def add_msg(self, user, msg):
        msg = json.loads(base64.urlsafe_b64decode(msg).decode('utf-8'))

        if self.msgs.get(user) is None:
            self.msgs[user] = dict()

        if self.msgs[user].get(msg['id']) is None:
            self.msgs[user][msg['id']] = [msg]
        else:
            self.msgs[user][msg['id']].append(msg)
            #Check if we already have all parts of the message
            if len(self.msgs[user][msg['id']]) == msg['total']:
                complete = ""
                for part in sorted(self.msgs[user][msg['id']], key=(lambda x: x['part'])):
                    complete += part['content']
                complete = complete.encode('utf-8')

                try:
                    complete = self.server.crypto.decrypt(complete)
                    del self.msgs[user][msg['id']]
                    return complete
                except:
                    logger.debug("Could not decrypt the message from {}".format(user))

        return None
