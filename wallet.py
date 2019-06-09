import os
from fastecdsa import keys, curve, ecdsa
from transaction import *
from fastecdsa.keys import export_key, import_key

DEFAULT_KEY = 0

class Wallet():
    """
    _public_key
    _private_key
    """

    def __init__(self):
        self._public_key = DEFAULT_KEY
        self._private_key = DEFAULT_KEY

    def validate_keys(self):
        if self._private_key == DEFAULT_KEY:
            raise Exception('please firstly init your keys')

    def set_random_key(self):
        self._private_key, self._public_key = keys.gen_keypair(curve.P256)
        print('private and public keys were successfully reset')

    def set_custom_key(self):
        try:
            new_private_key = int(input('please write a new private key '))
            new_public_key = keys.get_public_key(new_private_key, curve.P256)
            self._private_key = new_private_key
            self._public_key = new_public_key
            print('private and public keys were successfully reset')
        except ValueError:
            print('Reseting keys failed : no number found')

    def save_keys_to_file(self):
        try:
            self.validate_keys()
            fname = input('write a file name : ') + '.private'
            export_key(self._private_key, curve=curve.P256, filepath= fname)
            print('private and public keys were successfully saved to ', fname)
        except Exception as err:
            print('Keys saving failed : ', err)

    def set_key_from_file(self):
        fname = input('write a file name : ')
        try:
            self._private_key, self._public_key = import_key(fname + '.private', curve=curve.P256)
            print('private and public keys were successfully reset')
        except Exception as err:
            print('Reseting keys failed : ', err)

    def sign_transaction(self, transaction):
        if input('Do you want to sign this transaction?(y/n)') != 'y':
            raise Exception('Error : Signing transaction was denied')
        self.validate_keys()        
        if SEC1Encoder.decode_public_key(transaction._from, curve=curve.P256 ) != self._public_key:
            raise Exception('Error : tried to sign a strange transaction (public keys don\'t match)')
        to_sign = transaction.calculate_hash()
        transaction._signature  = ecdsa.sign(to_sign, self._private_key)
        print('Transaction was successfully signed')

    def create_transaction(self):
        # send more then you have when you're signing it?
        try:
            self.validate_keys()
            new_transaction = Transaction(
                                SEC1Encoder.encode_public_key(self._public_key),
                                get_address(),
                                get_number(1, 10000, 'amount'))
            new_transaction.show()
            self.sign_transaction(new_transaction)
            new_transaction.send()
        except Exception as err:
            print(err, '; transaction was canceled')

    def check_balance(self):
        pass
    
    usage = {
            '-set-random' : set_random_key,
            '-set-input' : set_custom_key,
            '-set-file' : set_key_from_file,
            '-balance' : check_balance,
            '-send' : create_transaction,
            '-save-keys' : save_keys_to_file}

def help():
    print('Usage : wallet.py\n',
            ' -exit          :press to terminate program\n',
            ' --help         :press to get the usage\n',
            ' -set-random    :set random keys to this account\n',
            ' -set-input     :set a private key from input\n',
            ' -set-file      :set private and public keys from the protected file\n',
            ' -balance       :check a balance of this account\n',
            ' -send          :send coints to a user\n',
            ' -save-keys     :save your private and public keys to the protected file')

me = Wallet()
line = input('Hey, user! Please, write a command (use --help to see usage)\n')

try:
    while not line == '-exit':
        if line == '--help':
            help()
        elif line in Wallet.usage.keys():
            Wallet.usage[line](me)
        else:
            print('Please, write a valid instraction')
        line = input('')

except Exception as err:
    print('Terminated by ', err)
