import math 

merkleTree = [None]
num_txn = 0

def computeLength(num_txn):
    return pow(2, math.ceil(math.log(num_txn)/math.log(2)));

def addHashes(nums): # hash later
    global num_txn, merkleTree
    num_txn = len(nums) # if odd we duplicate last, if even we add normally
    length = computeLength(num_txn) # this will determine length of our necessary merkle tree array
    # print("length: ", length)
    if length > len(merkleTree): # extend the tree
        extraNone = [None] * (length - len(merkleTree))
        merkleTree += extraNone
        for txn in nums:
            merkleTree.append(str(txn))
        if num_txn % 2 != 0:
            merkleTree.append(str(nums[-1]))
    else:
        for txn in nums:
            merkleTree.append(str(txn))

def computeMerkleTree():
    global merkleTree
    print(merkleTree)
    for i in range(math.ceil(len(merkleTree)/2)-1, 0, -1): # index of where to begin our concate hash
        # if merkleTree[2*i] == None:
        #     merkleTree[i] = str(merkleTree[2*i+1])
        # else:
        merkleTree[i] = str(merkleTree[2*i]) + str(merkleTree[2*i+1])
        displayMerkleTree()


def displayMerkleTree():
    print(merkleTree)
    

nums = ["1", "2", "3", "4", "5", "6", "7", "8"]
odd_nums = ["1", "2", "3", "4", "5", "6", "7"]
one = ["1", "2"]

# addHashes(nums)
addHashes(odd_nums)
computeMerkleTree()
computeMerkleTree()