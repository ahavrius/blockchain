import datetime
import hashlib
from transaction import *
from termcolor import colored

difficulty_hash = 0x00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
blockchain_file = 'block.chain'


def block_to_file(block):
    with open(blockchain_file, 'a') as f:
        json.dump(block.__dict__(), f)
        f.write('\n')

def json_to_block(json_data):
    transaction = json_to_transaction(json_data["data"])
    block = Block(transaction, json_data["prev_hash"])
    block._nonce = json_data["nonce"]
    block._timestamp = json_data["timestamp"]
    block._hash = json_data["hash"]
    return block

class Block:
    def __init__(self, data, prev_hash):
        self._data = data
        self._prev_hash = prev_hash
        self._nonce = 0
        self._timestamp = datetime.datetime.now()
        self._hash = self.calculate_hash()

    def __dict__(self):
        dc = {}
        if self._data:
            dc["data"]  = self._data.__dict__()
        else:
            dc["data"]  = self._data
        dc["prev_hash"] = str(self._prev_hash)
        dc["nonce"]     = str(self._nonce)
        dc["timestamp"] = str(self._timestamp)
        dc["hash"]      = str(self._hash)
        return dc

    def __str__(self):
        return json.dumps(self.__dict__())

    def calculate_hash(self):
        to_hash = "".join([
                            str(self._data),
                            str(self._prev_hash),
                            str(self._nonce),
                            str(self._timestamp)])
        sha = hashlib.sha256()
        sha.update(to_hash.encode('utf-8'))
        return sha.hexdigest()

    def is_valid(self):
        if self._data.check_signature() == 0:
            return 0
        return self._hash == self.calculate_hash()

    def proof_of_work(self, difficulty):
        while int(self._hash, 16) >= difficulty_hash:
            self._nonce += 1
            self._hash = self.calculate_hash()

class Blockchain:

    def __init__(self):
        self._chain = [self.genesis_block()]
        self.get_blockchain_from_file()
        self._difficulty = difficulty_hash
        self._mining_reward = 10

    def genesis_block(self):
        gen_block = Block(0, 0)
        gen_block._timestamp = 0
        gen_block._hash = gen_block.calculate_hash()
        return gen_block

    def chain_height(self):
        return len(self._chain)

    def block_by_id(self):
        try:
            id = get_number(0, self.chain_height() - 1, 'index')
            return str(self._chain[id])
        except Exception as err:
            print(err, ', request was denied')

    def block_by_hash(self):
        try:
            hash = input('Write the address : ')
            for block in self._chain:
                if hash == block._hash:
                    return str(block)
            return 'block was not found'
        except Exception as err:
            print(err, ', request was denied')

    def last_block_hash(self):
        return self._chain[-1]._hash

    def inner_balance_by_address(self, address):
        balance = 0
        for block in self._chain:
            if type(block._data) is Transaction and block._data._from == address:
                balance -= block._data._amount
            if type(block._data) is Transaction and block._data._to == address:
                balance += block._data._amount
        return balance

    def balance_by_address(self):
        try:
            address = get_address()
            return self.inner_balance_by_address(address)
        except Exception as err:
            print(err, ', request was denied')

    def history_by_address(self):
        try:
            address = get_address()
            print(colored('---History :', 'blue'))
            for block in self._chain:
                if type(block._data) is Transaction and \
                    address in (block._data._from, block._data._to):
                    block._data.show()
        except Exception as err:
            print(err, ', request was denied')

    def mine_block(self):
        try:
            address = get_address()
            new_transaction = get_from_queue()
            new_transaction.check_signature()
            new_block = Block(new_transaction, self.last_block_hash())
            new_block.proof_of_work(self._difficulty)
            self._chain.append(new_block)
            block_to_file(new_block)
            revard_transaction = Transaction(NULL_BYTE, address, 1)
            add_to_queue(revard_transaction)
            return('Successfully mined')
        except Exception as err:
            print(err, ', mining was canceled')

    def get_blockchain_from_file(self):
        #if doesn't exist
        if not os.path.isfile(blockchain_file):
            return False
        with open(blockchain_file, 'r') as f:
            for line in f:
                json_data = json.loads(line)
                block = json_to_block(json_data)
                self._chain.append(block)

    def is_chain_valid(self):
        prev_hash = 0
        for block in self._chain:
            if block._hash != block.calculate_hash() or \
                block._prev_hash != prev_hash:
                return False #excrption
            prev_hash = block._hash
        return True

    usage = {
            '-height' : chain_height,
            '-last-hash' : last_block_hash,
            '-info-id' : block_by_id,
            '-info-hash' : block_by_hash,
            '-balance' : balance_by_address,
            '-history' : history_by_address,
            '-mine' : mine_block,
            '-valid' : is_chain_valid}
