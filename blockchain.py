import json
import time
import hashlib


# ---- class Block ----
class Block:
    def __init__(self, data, previous_hash):
        self.transactions = data
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.hash = ''
        self.nonce = 0

    def calculate_hash(self):
        st = str(self.transactions) + self.previous_hash + str(self.timestamp) + str(self.nonce)
        return hashlib.sha256(st.encode("utf-8")).hexdigest()

    def mine_block(self, difficulty):
        newHash = self.hash
        while newHash[:difficulty] != "0" * difficulty:
            self.nonce += 1
            newHash = self.calculate_hash()
        self.hash = newHash

    def __str__(self):  # formate to JSON
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

# ---- end of class Block ----


# ---- class Wallet ----
class Wallet:
    def __init__(self, name):
        self.name = name
        self.UTXOs = []

    def send_funds(self, recipient, value):
        bill = value
        neededUTXOs = []
        for utxo in self.UTXOs:
            if bill > 0:
                bill -= utxo.UTXO
                neededUTXOs.append(utxo)
        transaction = Transaction(self.name, recipient.name, value, neededUTXOs)
        for UTXO in neededUTXOs:
            self.UTXOs.remove(UTXO)
        self.UTXOs.append(TransactionInput(transaction.outputs[0]))
        recipient.UTXOs.append(TransactionInput(transaction.outputs[1]))
        return transaction

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
# ---- end of class Wallet ----   


# ---- class Transaction ----
class Transaction:
    def __init__(self, sender, recipient, value, inputs):
        self.sender = sender
        self.recipient = recipient
        self.value = value
        self.id = self.calculate_hash()
        self.inputs = inputs
        self.outputs = self.process_transaction()

    def calculate_hash(self):
        text = str(self.sender)+str(self.recipient)+str(self.value)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def __str__(self):  # formate to JSON
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def process_transaction(self):
        coinsInInputs = 0
        for input in self.inputs:
            coinsInInputs += input.UTXO
        if coinsInInputs < self.value:
            raise ValueError("There is not enough coins in wallet!")
        cashback = coinsInInputs - self.value
        outputs = [TransactionOutput(self.sender, cashback, self.id), TransactionOutput(self.recipient, self.value, self.id)]
        return outputs

# ---- end of class Transaction ----


# ---- class TransactionInput ----
class TransactionInput:
    def __init__(self,transactionOutput):
        self.UTXO = transactionOutput.value
        self.transactionOutputId= transactionOutput.id

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


# ---- end of class TransactionInput ----   


# ---- class TransactionOutput ----
class TransactionOutput:
    def __init__(self, recipient, value, parent_transaction_id):
        self.recipient = recipient
        self.value = value
        self.parentTransactionId = parent_transaction_id
        self.id = self.calculate_hash()

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def calculate_hash(self):
        text = str(self.recipient)+str(self.value)+str(self.parentTransactionId)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

# ---- end of class TransactionOutput ----   


# ---- main program main ----

def is_chain_valid(blockchain):
    prev_hash = "0"
    for block in blockchain:
        if block.hash != block.calculate_hash() or block.previous_hash != prev_hash:
            return False
        prev_hash = block.hash
    return True


walletA = Wallet("Alice")
walletB = Wallet("Bob")
genesisTransaction = Transaction("0", "Alice", 100, [TransactionInput(TransactionOutput("0", 100, "0"))])
walletA.UTXOs = [TransactionInput(genesisTransaction.outputs[1])]
transaction1 = walletA.send_funds(walletB, 50)
transaction2 = walletB.send_funds(walletA, 30)
transaction3 = walletA.send_funds(walletB, 10)


print("genesisTransaction:")
print(genesisTransaction)
print("transaction1:")
print(transaction1)
print("transaction2:")
print(transaction2)
print("transaction3:")
print(transaction3)
print("walletA:")
print(walletA)
print("walletB:")
print(walletB)
def print_blockchain(blockchain):
    print("\nBlockchain:")
    for block in blockchain:
        # every block is written in console
        print(block)


difficulty = 3
blockchain = []

genesisBlock = Block(genesisTransaction, "0")
genesisBlock.mine_block(difficulty)
blockchain.append(genesisBlock)

genesisBlock = Block(transaction1,blockchain[-1].hash)
genesisBlock.mine_block(difficulty)
blockchain.append(genesisBlock)

genesisBlock = Block(transaction2, blockchain[-1].hash)
genesisBlock.mine_block(difficulty)
blockchain.append(genesisBlock)

genesisBlock = Block(transaction3, blockchain[-1].hash)
genesisBlock.mine_block(difficulty)
blockchain.append(genesisBlock)
print_blockchain(blockchain)
print("\nIs chain valid? " + str(is_chain_valid(blockchain)))

print("---------------------------------------------------------------------------")
