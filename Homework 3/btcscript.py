import sys
from datetime import datetime
import json
from hashlib import sha256
from datetime import datetime
import math 

merkleTransactions = [] # contains merkle hashes
merkleTree = [None]
num_txn = 0
magicNumber_FINAL = 3652501241
transactions_merkle = []
transaction_bytes = []
previous_header_hash = []

txn = []

fileName = sys.argv[1]
f = open(fileName, mode='rb')
bytes_master = f.read()
f.close()




def readFile(numBytes):
    global bytes_master
    res = bytes_master[:numBytes]
    bytes_master = bytes_master[numBytes:]
    global txn
    txn += res
    return res

def compactSize(flag):
    global transaction_bytes
    b = readFile(1) # read first byte
    dec = int.from_bytes(b, 'little')
    # print("DEBUG dec: ", dec,b)
    if dec >= 0 and dec < 253:
        if flag:
            transaction_bytes += bytearray(b)
        return dec
    elif dec == 253:
        b = readFile(2)
        if flag:
            transaction_bytes += bytearray(b)
        return int.from_bytes(b, 'little')
    elif dec == 254:
        b = readFile(4)
        if flag:
            transaction_bytes += bytearray(b)
        return int.from_bytes(b, 'little')
    else:
        b = readFile(8)
        if flag:
            transaction_bytes += bytearray(b)
        return int.from_bytes(b, 'little')



class Preamble:
    def __init__(self):
        self.magic_number = None
        self.size = None
    def getMagicNumber(self):
        bytes = readFile(4)
        self.magic_number = int.from_bytes(bytes, 'little')
    def getSize(self):
        bytes = readFile(4)
        self.size = int.from_bytes(bytes, 'little')

        
        


class Block:
    def __init__(self, height):
        self.height = height
        self.version = None
        self.previous_hash = None
        self.merkle_hash = None
        self.timestamp = None
        self.timestamp_readable = None
        self.nbits = None
        self.nonce = None

        self.txn_count = None
        self.transactions = []
        
    def getHeader(self): # order matters
        # self.header = Header()
        self.getVersion()
        self.getPrevHash()
        self.getMerkleRootHash()
        self.getTime()
        self.getTimereadable()
        self.GetnBits()
        self.getNonce()

    def getTransaction(self):
        tran = Transaction()

        tran.getVersion()
        tran.getTXInput_Count()
        tran.getTXInputs()
        tran.getTXOutput_Count()
        tran.getTXOutputs()
        tran.getLockTime()
        return tran

    def getTransactionCount(self):
        self.txn_count = compactSize(False)

    # HEADER METHODS
    def getVersion(self):
        bytes_array = bytearray(readFile(4))
        bytes_array.reverse()
        self.version = int.from_bytes(bytes(bytes_array), byteorder='big')

    def getPrevHash(self):
        bytes_array = bytearray(readFile(32))
        bytes_array.reverse() # reverse the endianess of these bytes
        self.previous_hash = str(bytes(bytes_array).hex())

    def getMerkleRootHash(self):
        bytes_array = bytearray(readFile(32))
        bytes_array.reverse()
        self.merkle_hash = str(bytes(bytes_array).hex())
    def getTime(self):
        bytes = readFile(4)
        self.timestamp = int.from_bytes(bytes, 'little', signed=False)
    def getTimereadable(self):
        self.timestamp_readable = datetime.utcfromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def GetnBits(self):
        bytes_array = bytearray(readFile(4))
        bytes_array.reverse()
        self.nbits = bytes(bytes_array).hex()
    def getNonce(self):
        bytes = readFile(4)
        self.nonce = int.from_bytes(bytes, 'little', signed=False)


class TransactionOutput:
    def __init__(self):
        self.satoshis = None
        self.output_script_size = None
        self.output_script_bytes = None
    def getValue(self):
        b = readFile(8)
        self.satoshis = int.from_bytes(b, 'little')

        global transaction_bytes
        transaction_bytes += bytearray(bytes(b))
    def getOutScriptBytes(self):
        self.output_script_size = compactSize(True)

        global transaction_bytes

    def getOutScript(self):
        b = readFile(self.output_script_size)
        self.output_script_bytes = b.hex()

        global transaction_bytes
        transaction_bytes += bytearray(b)


        

class TransactionInput:
    def __init__(self):
        self.utxo_hash = None
        self.index = None
        self.input_script_size = None
        self.input_script_bytes = None
        self.sequence = None
    def getHash(self):
        bytes_array = bytearray(readFile(32))

        global transaction_bytes
        transaction_bytes += bytes_array

        bytes_array.reverse()
        self.utxo_hash = str(bytes(bytes_array).hex())

    def getIndex(self):
        b = readFile(4)
        self.index = int.from_bytes(b,'little')

        global transaction_bytes
        transaction_bytes += bytearray(b)

    def getInScriptBytes(self):
        self.input_script_size = compactSize(True)


    def getSignatureScript(self):
        b = readFile(self.input_script_size)
        self.input_script_bytes = b.hex()

        global transaction_bytes
        transaction_bytes += bytearray(bytes(b))


    def getSequence(self):
        b = readFile(4)
        self.sequence = int.from_bytes(b, 'little')

        global transaction_bytes
        transaction_bytes += bytearray(bytes(b))



class Blocks:
    def __init__(self):
        self.blocks = []
        self.height = None

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def getBlock(self, height):
        bl = Block(height)
        bl.getHeader()
        bl.getTransactionCount()
        for _ in range(bl.txn_count):
            bl.transactions.append(bl.getTransaction())
            
        self.blocks.append(bl)

    def finalizeHeight(self, h):
        self.height = h


class Transaction:
    def __init__(self):
        self.version = None
        self.txn_in_count = None
        self.txn_inputs = []
        self.txn_out_count = None
        self.txn_outputs = []
        self.lock_time = None

    def getVersion(self):
        bytes_array = bytearray(readFile(4))
        global transaction_bytes
        transaction_bytes += bytes_array
        bytes_array.reverse()
        self.version = int.from_bytes(bytes(bytes_array), 'big')

    def getTXInput_Count(self):
        self.txn_in_count = compactSize(True)

    def getTXInputs(self):
        for _ in range(self.txn_in_count):
            tr = TransactionInput()
            tr.getHash()
            tr.getIndex()
            tr.getInScriptBytes()
            tr.getSignatureScript()
            tr.getSequence()
            self.txn_inputs.append(tr)
    
    def getTXOutput_Count(self):
        self.txn_out_count = compactSize(True)

    def getTXOutputs(self):
        for _ in range(self.txn_out_count):
            tr = TransactionOutput()
            tr.getValue()
            tr.getOutScriptBytes()
            tr.getOutScript()
            self.txn_outputs.append(tr)        
    def getLockTime(self):
        b = readFile(4)
        self.lock_time = int.from_bytes(b, 'little')

        global transaction_bytes
        transaction_bytes += bytearray(b)

        transactions_merkle.append(bytes(transaction_bytes).hex())
        transaction_bytes.clear()

# -------- MERKLE TREE ---------- #
def computeLength(num_txn):
    return pow(2, math.ceil(math.log(num_txn)/math.log(2)));

def addHashes(nums): # hash later
    global num_txn, merkleTree
    
    num_txn = len(nums) # if odd we duplicate last, if even we add normally
    length = computeLength(num_txn) # this will determine length of our necessary merkle tree array
    if length > len(merkleTree): # extend the tree
        extraNone = [None] * (length - len(merkleTree))
        merkleTree += extraNone
        for txn in nums:
            # print("return", computeHash(txn))
            # print(str(txn))
            # print(txn)
            merkleTree.append(txn)
        if num_txn % 2 != 0:
            merkleTree.append(nums[-1])
    else:
        for txn in nums:
            merkleTree.append(txn)

def computeMerkleTree():
    global merkleTree
    for i in range(math.ceil(len(merkleTree)/2)-1, 0, -1): # index of where to begin our concate hash
        # merkleTree[i] = computeHash1(str(merkleTree[2*i]) + str(merkleTree[2*i+1]))
        # print("here",merkleTree[2*i])

        merkleTree[i] = binMerkle(merkleTree[2*i], merkleTree[2*i+1])
        # print(merkleTree)
        
        # displayMerkleTree()


def binMerkle(txn1, txn2):
    # txn1_data = bytes.fromhex(txn1)
    # txn1_hash_bin = sha256(sha256(txn1).digest()).digest()
    # txn1_hash_hex = sha256(sha256(txn1).digest()).hexdigest()

    # # print(txn1_hash_hex)

    # # txn2_data = bytes.fromhex(txn2)
    # txn2_hash_bin = sha256(sha256(txn2).digest()).digest()
    # txn2_hash_hex = sha256(sha256(txn2).digest()).hexdigest()

    # print(txn2_hash_hex)
    # print("txn1: ",txn1, txn2)
    # print(merkleTree)
    print(merkleTree)
    # if txn1 == None:
    #     parent_hash_bin=sha256(sha256(txn2).digest()).digest()
    # if txn2 == None:
    #     parent_hash_bin=sha256(sha256(txn1).digest()).digest()
    # else:
    parent_hash_bin=sha256(sha256(txn1+txn2).digest()).digest()


    # parent_hash_hex=sha256(sha256(txn1_hash_bin+txn2_hash_bin).digest()).hexdigest()
    
    return parent_hash_bin
    # return sha256(sha256(txn_string).digest()).digest()


def binaryHash(val):
    txn1_data = bytes.fromhex(val)
    txn1_hash_bin = sha256(sha256(txn1_data).digest()).digest()
    return txn1_hash_bin


def displayMerkleTree():
    print("merkleTree", merkleTree)

def validateMerkleHash():
    # print(transaction_bytes)
    # print("last",transactions_merkle)
    # print("validating merkle hash")
    hashes = []
    # for i in range(len(block.transactions)):
    #     print(int.from_bytes(block.transactions[i]))
    # print("transactions_merkle: ", transactions_merkle)
    for i in range(len(transactions_merkle)):
        h = binaryHash(transactions_merkle[i])
        # print('\n')
        # print(h)
        hashes.append(h)
    # print("hashes: ", hashes)
    addHashes(hashes)
    computeMerkleTree()
    # print(merkleTree[1])
    return merkleTree[1]

#-------- MERKLE TREE SECTION ---------------#

def finalvalidate(val):
    tmp = bytearray(val)
    tmp.reverse()
    hash = ''.join(format(x, '02x') for x in tmp)
    return hash

def computeHash1(txn_string):
    # print(txn_string)
    # txn_string = bytearray(arr).hex()
    return ''.join(format(x, '02x') for x in reversed(bytearray(sha256(sha256(bytes.fromhex(txn_string)).digest()).digest())))

def computeHash(arr):
    # print(txn_string)
    txn_string = bytearray(arr).hex()
    return ''.join(format(x, '02x') for x in reversed(bytearray(sha256(sha256(bytes.fromhex(txn_string)).digest()).digest())))

file = open(fileName + ".json", mode='w')
bigBlock = Blocks()
height = 0
p_hash = None
while len(bytes_master.hex()) > 0:
    
    p = Preamble()
    p.getMagicNumber()
    p.getSize()
   
    current_header_hash = bytes_master[:80]
    bigBlock.getBlock(height)
    block = bigBlock.blocks[height]

    prev_block = bigBlock.blocks[height - 1]
    if p.magic_number != magicNumber_FINAL: #error 1
        print("error 1 block " + str(height)) 
        exit()
    if str(block.version) != "1": #error 2
        print("error 2 block " + str(height))
        exit()

    c_hash = computeHash(current_header_hash)

    if height >= 1 and str(block.previous_hash) != str(p_hash) : # error 3
        print("error 3 block " + str(height))
        exit()

    d1 = datetime.strptime(block.timestamp_readable, "%Y-%m-%d %H:%M:%S%f") # error 4
    d2 = datetime.strptime(prev_block.timestamp_readable, "%Y-%m-%d %H:%M:%S%f")
    if height > 0 and (d2-d1).total_seconds()/3600.0 > 2:
        print("error 4 block " + str(height))
        exit()

    for i in range(block.txn_count): # error 5
        if block.transactions[i].version != 1:
            print("error 5 block " + str(height))
            exit()

    merkle_hash_compute = validateMerkleHash() #error 6
    if finalvalidate(merkle_hash_compute) != block.merkle_hash.strip():
        print("error 6 block " + str(height))
        exit()

    # transaction_bytes.clear()
    # transactions_merkle.clear()
    # merkleTree.clear()
    # merkleTree.append(None)

    p_hash = c_hash
    height += 1

    transaction_bytes.clear()
    transactions_merkle.clear()
    merkleTree.clear()
    merkleTree.append(None)

    # if height%1000 == 0:
    #     print(height)


bigBlock.finalizeHeight(height)
file.write(bigBlock.toJSON())
file.close()
print("no errors " + str(height) + " blocks")