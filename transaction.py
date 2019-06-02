import datetime
import hashlib
from fastecdsa import keys, curve, ecdsa


NOT_SIGNED = 0

def get_amount():
    
    try:
        n = int(input('How much to send? Please write positive number : '))
        if (n <= 0):
            raise Exception('Error : amount should be a positive number')
        return n
    except ValueError:
        raise Exception('Error : amount should be a positive number')
    

def get_recipient():
    address = input('Write address of recipient : ')
    return address

def add_to_queue(transaction):
    pass

class Transaction():
    """
    _from    : string
    _to      : string
    _amount  : int
    _timestamp : datetime
    _signature
    _status  : string 
    """
    def __init__(self, _from, _to, _amount):
        self._from = _from
        self._to = _to
        self._amount = _amount
        self._signature = NOT_SIGNED
        self._status = 'waiting for signature'
        self._timestamp = datetime.datetime.now()

    def calculate_hash(self):
        to_hash = "".join([
                            str(self._from),
                            str(self._to),
                            str(self._amount),
                            str(self._timestamp)])
        sha = hashlib.sha256()
        sha.update(to_hash.encode('utf-8'))
        return sha.hexdigest()

    def show(self):
        print('Generated transaction : ',
                '\n From the member: ', self._from,
                '\n To the member: ', self._to,
                '\n With amount : ', self._amount,
                '\n at : ', self._timestamp,
                '\n Status : ', self._status)

    def is_signed(self):
        return self.signature != NOT_SIGNED

    def check_signature(self):
        if not self.is_signed():
            return 0
        to_sign = self.calculate_hash()  
        return ecdsa.verify(self.signature, to_sign, self._from)

    def send(self):
        if not self.check_signature():
            raise Exception('Error : you need to sign transaction before sending')
        add_to_queue(self)

        print('Transaction was successfully added to the queue')

    