from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError # FOR ETHEREUM WALLET TYPE
from Crypto.Hash import SHA256
import base64
import json

class Transaction:
    def __init__(self, sender_address, receiver_address, type_of_transaction, nonce, amount, message=None):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        if type_of_transaction not in ['coin', 'message']:
            raise ValueError("Value can only be 'coin' or 'message'")
        self.type_of_transaction = type_of_transaction
        if type_of_transaction == 'message':
            self.message = message
            self.amount = len(message)
        else:
            self.amount = amount
            self.message = None
        self.nonce = nonce
        self.transaction_id = self.hash_transaction()
        self.signature = None



    def sign_transaction(self, private_key_string):
        """
        Sign the transaction with the sender's private key.
        """

        # Convert the private key from a string to a key object
        private_key = RSA.import_key(private_key_string)

        signer = pkcs1_15.new(private_key)
        h = SHA256.new(self.transaction_id.encode())
        self.signature = base64.b64encode(signer.sign(h)).decode()



    def verify_signature(self):
        """
        Verify the signature of the transaction.
        """
        public_key = RSA.import_key(self.sender_address)
        verifier = pkcs1_15.new(public_key)
        h = SHA256.new(self.transaction_id.encode())
        try:
            verifier.verify(h, base64.b64decode(self.signature.encode()))
            return True
        except (ValueError, TypeError):
            return False
        
    # FOR ETHEREUM WALLET TYPE
    # def sign_transaction(self, private_key_string):
    #     """
    #     Sign the transaction with the sender's private key.
    #     """
    #     # Convert the private key from a string to a key object
    #     private_key = SigningKey.from_string(bytes.fromhex(private_key_string), curve=SECP256k1)

    #     h = SHA256.new(self.transaction_id.encode())
    #     self.signature = base64.b64encode(private_key.sign(h.digest())).decode()

    # def verify_signature(self):
    #     """
    #     Verify the signature of the transaction.
    #     """
    #     public_key = VerifyingKey.from_string(bytes.fromhex(self.sender_address), curve=SECP256k1)

    #     h = SHA256.new(self.transaction_id.encode())
    #     try:
    #         public_key.verify(base64.b64decode(self.signature.encode()), h.digest())
    #         return True
    #     except BadSignatureError:
    #         return False



    def hash_transaction(self):
        """
        Hashes the transaction details to generate a unique transaction ID.
        """
        transaction_details = {
        'sender_address': self.sender_address,
        'recipient_address': self.receiver_address,
        'type_of_transaction': self.type_of_transaction,
        'amount': self.amount,
        'message': self.message,
        'nonce': self.nonce,
    }
        transaction_string = json.dumps(transaction_details, sort_keys=True)
        h = SHA256.new(transaction_string.encode())
        return h.hexdigest()
    


    def to_dict(self):
        """
        Return the transaction as a dictionary.
        """
        return {
            'sender_address': self.sender_address,
            'recipient_address': self.receiver_address,
            'type_of_transaction': self.type_of_transaction,
            'amount': self.amount,
            'message': self.message,
            'nonce': self.nonce,
            'transaction_id': self.transaction_id,
            'signature': self.signature
        }
    

    
    @classmethod
    def from_dict(cls, transaction_dict):
        """
        Create a Transaction object from a dictionary.
        """
        transaction = cls(
            transaction_dict['sender_address'],
            transaction_dict['recipient_address'],
            transaction_dict['type_of_transaction'],
            transaction_dict['nonce'],
            transaction_dict['amount'],
            transaction_dict['message']
        )
        transaction.transaction_id = transaction_dict['transaction_id']
        transaction.signature = transaction_dict['signature']
        return transaction
        
