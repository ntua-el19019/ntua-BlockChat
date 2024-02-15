import time
import json
from Crypto.Hash import SHA256
from transaction import Transaction

class Block:
    def __init__(self, index, previous_hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.transactions = []
        self.current_hash = self.hash_block()
        self.validator = None


    def add_transaction(self, transaction, capacity):
        self.transactions.append(transaction)
        if len(self.transactions) >= capacity:
            return True # Block is full
        return False
    
    def hash_block(self):
        block_json = {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "transactions": self.transactions #TODO: it may want ids instead of transactions
        }
        block_json = json.dumps(block_json, sort_keys=True)
        return SHA256.new(block_json.encode()).hexdigest()
    
def genesis(bootstrap_node_address, n):
    genesis_block = Block(0, 1)
    genesis_block.validator = 0
    genesis_transaction = Transaction(
        sender_address='0', 
        receiver_address=bootstrap_node_address, 
        type_of_transaction='coin', 
        amount=1000*n, 
        nonce=0) 
    genesis_block.transactions.append(genesis_transaction)
    return genesis_block
