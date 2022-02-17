import binascii
import Crypto
import Crypto.Random
from Crypto.PublicKey import RSA


class Wallet:
    def __init__(self):
        random_gen = Crypto.Random.new().read
        self.private_key = RSA.generate(1024, random_gen)
        self.public_key = self.private_key.publickey()

    def get_public_key(self):
        return binascii.hexlify(self.public_key.exportKey(format='DER')).decode('ascii')

    def get_private_key(self):

        return binascii.hexlify(self.private_key.exportKey(format='DER')).decode('ascii')


w = Wallet()
print(w.get_public_key())
