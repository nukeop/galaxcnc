import binascii
import logging
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding


logger = logging.getLogger(__name__)

PRIV_KEY_FILE = "privkey.pem"
PUB_KEY_FILE = "pubkey.pem"


class Crypto(object):
    """Handles server's cryptography.
    Stores a public/private key pair and saves/loads it to/from the disk.
    Can sign, encrypt, and decrypt messages.
    """
    def __init__(self, keyfile=PRIV_KEY_FILE):
        if os.path.exists(keyfile):
            logger.info("Loading a key from {}".format(keyfile))
            with open(keyfile, 'rb') as keyfile:

                self.private_key = serialization.load_pem_private_key(
                    keyfile.read(),
                    password=None,
                    backend=default_backend()
                )
                self.public_key = self.private_key.public_key()

        else:
            logger.info("Generating a new key and storing it in"
            " {}".format(keyfile)) 
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=default_backend()
            )
            pem = self.private_key_as_text()
            with open(keyfile, 'wb') as keyfile:
                keyfile.write(pem)

            self.public_key = self.private_key.public_key()
            pubpem = self.public_key_as_text()
            with open(PUB_KEY_FILE, 'wb') as keyfile:
                keyfile.write(pubpem)


    def private_key_as_text(self):
        return self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
        )

    def public_key_as_text(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )


    def encrypt(self, text, key=None):
        if key is None:
            key = self.public_key

        text = bytes(text.encode('utf-8'))
        ciphertext = key.encrypt(
            text,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        )
        ciphertext = binascii.hexlify(ciphertext)
        return ciphertext


    def decrypt(self, text, key=None):
        if key is None:
            key = self.private_key

        text = binascii.unhexlify(text)
        plaintext = key.decrypt(
            text,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        ).decode('utf-8')
        return plaintext

    def sign(self, text, key=None):
        if key is None:
            key = self.private_key

        text = text.encode('utf-8')
        signature = key.sign(
            text,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        signature = binascii.hexlify(signature)
        return signature

    def verify(self, text, sig, key=None):
        if key is None:
            key = self.public_key

        sig = binascii.unhexlify(sig)
        key.verify(
            sig,
            text.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
