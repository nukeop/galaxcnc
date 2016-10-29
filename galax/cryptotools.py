"""This module contains loose functions helping with various aspects of
handling cryptography, which is especially useful when writing small workers
that do not need the full functionality of crypto.py.
"""

import binascii

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def serialize_private_key(privkey):
    """Serializes a private key in the "armored" text format.
    """
    return privkey.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )


def serialize_public_key(pubkey):
    """Serializes a public key in the "armored" text format.
    """
    return pubkey.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def deserialize_private_key(data):
    """Loads a private key from unencrypted bytes.
    """
    return serialization.load_pem_private_key(
        data,
        password=None,
        backend=default_backend()
    )


def deserialize_public_key(data):
    """Loads a public key from unencrypted bytes.
    """
    return serialization.load_pem_public_key(
        data,
        backend=default_backend()
    )


def encrypt(data, pubkey):
    """Encrypts data with a public key and returns ciphertext.
    The ciphertext is converted to hexadecimal form from raw bytes.
    """
    data = data.encode('utf-8')
    ciphertext = pubkey.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        )
    )
    return binascii.hexlify(ciphertext)
