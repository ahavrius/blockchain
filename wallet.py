import os
from fastecdsa import keys, curve, ecdsa
from transaction import *

DEFAULT_KEY = 0

class Wallet():
    """
    _public_key
    _private_key
    _name
    """
    
    def __init__(self):
        self._public_key = DEFAULT_KEY
        self._private_key = DEFAULT_KEY

    def validate_keys(self):
        if self._private_key == DEFAULT_KEY:
            raise Exception('please firstly init your keys')
        if self._public_key != keys.get_public_key(self._private_key, curve.P256):
            raise Exception('your keys don\'t match, please reset them')

    def set_random_key(self):
        self._private_key, self._public_key = keys.gen_keypair(curve.P256)
        print('current private key : ', self._private_key)

    def set_custom_key(self):
        try:
            new_private_key = int(input('please write a new private key '))
            new_public_key = keys.get_public_key(new_private_key, curve.P256)
            self._private_key = new_private_key
            self._public_key = new_public_key
            print('private and public keys were successfully reset')
        except ValueError:
            print('Reseting keys failed : no number found')
    
    def set_key_from_file(self):
        fname = input('write file name : ')
        try:
            with open(fname) as f:
                new_private_key = int(f.readline())
            new_public_key = keys.get_public_key(new_private_key, curve.P256)
            self._private_key = new_private_key
            self._public_key = new_public_key
            print('private and public keys were successfully reset')
        except OSError:
            print('Reseting keys failed : file wasn\'t found')
        except ValueError:
            print('Reseting keys failed : no number found')

    def sign_transaction(self, transaction):
        self.validate_keys()
        if transaction._from != self._public_key:
            raise Exception('Error : tried to sign a strange transaction (public keys don\'t match)')
        to_sign = transaction.calculate_hash()
        transaction.signature  = ecdsa.sign(to_sign, self._private_key)
        transaction.statuse = 'signed, waiting for departure'
        print('Transaction was successfully signed')

    def create_transaction(self):
        self.validate_keys()
        try:
            new_transaction = Transaction(
                                self._public_key,
                                get_recipient(),
                                get_amount())
            new_transaction.show()
            self.sign_transaction(new_transaction)
            new_transaction.send()
        except Exception as err:
            print(err, '; transaction was canceled')
try:
    me = Wallet()
    me.set_random_key()
    me.create_transaction()


except Exception as err:
    print('Terminated by ', err)
