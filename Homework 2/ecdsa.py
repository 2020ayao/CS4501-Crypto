import sys
import random
# finite field operations
a = 0
b = 7

def add(a, b, size):
    return (a+b) % size
def add_inverse(val, size):
   return(size - abs(val))
def sub(a, b, p): # a - b = a + (-b)
    # find additive inverse for b 
    # let -b = size - b, then size - b is the additive inverse
    # if b = 10, and size = -10 = 17 - 10 = 7, additive inverse of 10 is 7
    return add(a, add_inverse(b, p), p)
def mult(a, b, p):
    return (a*b) % p

def exp(a, b, p):
    return (a ** b) % p

def mult_inverse(val, p):
    return (exp(val, p-2, p))
# print("mult inverse test")
# print(mult(7,mult_inverse(7, 43), 43))


def div(a, b, p): # a / b == a * 1/b, find the mult inverse for b:
    # 1/b = b ^(-1) = b^(p-2) mod p
    return mult(a, mult_inverse(b, p), p)


# arithmetic tests
# print("15+15 = ", add(15, 15))
# print("3 + 15 = ", add(3, 15))

# print("15 - 13 = ", sub(15, 13))
# print("13 - 15 = ", sub(13, 15))

# print("14 * 14 = ", mult(14, 14))
# print("2 * 10 = ", mult(2, 10))

# print("14 / 19 = ", div(14, 19))
# print("13 / 24 = ", div(13, 24))

# print("14 ** 15 = ", exp(14, 15))
# print("2 ** 6", exp(2, 6))

#EC operations

# HELPER METHODS
# adding point to itself 
def slope(x, y, p): # given a point, find the slope of the tangent line derivative
    return div(mult(3, exp(x, 2, p), p), mult(2, y, p), p)

#adding point to a point
def slope1(x1, y1, x2, y2, p):
    return div(sub(y2, y1, p), sub(x2, x1, p), p)

def calc_x3(x1, x2, m, p):
    return sub(sub(exp(m, 2, p), x1, p), x2, p)

def calc_y3(x1, x3, y1, m, p):
    return sub(mult(m, sub(x1, x3, p), p), y1, p)

def addPointItself(x1, y1, p):
    m = slope(x1, y1, p) # size = 43
    x3 = calc_x3(x1, x1, m, p)
    y3 = calc_y3(x1, x3, y1, m, p)
    return(x3, y3)
def addTwoPoints(x1, y1, x2, y2, p):
    if x1 == None and y1 == None: # identity property
        return x2, y2
    if x2 == None and y2 == None:
        return x1, y1
    m = slope1(x1, y1, x2, y2, p)
    x3 = calc_x3(x1, x2, m, p)
    y3 = calc_y3(x1, x3, y1, m, p)
    if x1 == x2 and add_inverse(y2, p) == y1: # o or p?
        return (None, None)
    return(x3, y3)


# testing EC operations
# 1. Point to Point (same)
# print(addPointItself(12, 31))
# print(addPointItself(13, 21))
# print(addPointItself(12, 12))
# print(addPointItself(7, 7))

# # 2. Point to Point (different)
# print(addTwoPoints(2, 31, 7, 36, 43))
# print(addTwoPoints(20, 3, 2, 31, 43))
# print(addTwoPoints(7, 36, 29, 31, 43))

# print(addTwoPoints(2, 31, 2, 12, 43))

def scalar_mult(x1, y1, k, p): # base point G = (x1, y1)
    b = bin(k).replace("0b", "")
    length = len(b) # the largest multiple 2 we need to calculate up to. 
    powers = []
    powers.append((x1, y1)) # base point G (1xG)

    for i in range(1,length): # for 21:  [1xG, 2xG, 4xG]
        px1, py1 = powers[i-1] # previous
        newx, newy = addPointItself(px1, py1, p)
        powers.append((newx, newy))    
    powers = powers[::-1] # reverse because of our binary endianess
    # print("powers", powers)

    # calculate the actual value of k x G with the binary value
    # points to add:
    stack = []
    for i in range(len(b)):
        if b[i] == "1":
            stack.append((powers[i][0], powers[i][1]))
    # copyOfPoints = stack.copy() # to shift if necessary
    while len(stack) != 1:
        # print(stack)
        fx, fy = stack.pop()
        nx, ny = stack.pop()
        if fx != nx: # check if the x points are equivalent (edge case)
            stack.append(addTwoPoints(fx, fy, nx, ny, p))
        else:
            stack.insert(0, (fx,fy))
            stack.append((nx,ny))
    return stack[0]

# 3. Elliptic curve multiplication of a point by a scalar value: P = k ⊗ Q
# print(scalar_mult(25,25,4))
# print(scalar_mult(13,21,4))
# print(scalar_mult(13,22,4))
# print(scalar_mult(2,12,4))

def generate_d(o):
    return random.randint(1, o-1)
def calc_Q(d,x,y, p):
    return scalar_mult(x, y, d, p)

def genkey(p,o,x,y):
    d = generate_d(o)
    Qx, Qy = calc_Q(d, x, y, p)
    print(d)
    print(Qx)
    print(Qy)

def generate_rand_k(o):
    return random.randint(1, o-1)

def calc_secret_k(k, o):
    return mult_inverse(k, o)

def calc_s(secret_k, h, Rx, d, o):
    return secret_k * (h + Rx * d) % o

def signature(p,o,x,y,d,h):
    k = generate_rand_k(o)
    secret_k = calc_secret_k(k, o)
    Rx, _ = scalar_mult(x, y, k, p)
    
    s = calc_s(secret_k, h, Rx, d, o)
    while Rx == 0 or s == 0: # handling special cases of Rx and s but need to shuffle?
        signature(p,o,x,y,d,h)
    return Rx, s

def verify(p,o,x,y,Qx,Qy,r,s,h):
    mult_inverse_s = mult_inverse(s, o) 
    fpoint = scalar_mult(x, y, mult(mult_inverse_s, h, o), p)
    spoint = scalar_mult(Qx, Qy,mult(mult_inverse_s, r, o), p)
    R = addTwoPoints(fpoint[0], fpoint[1], spoint[0], spoint[1], p)
    # print(R)
    return R[0] == r


# size = sys.argv[2] # size = p = size of finite field

match sys.argv[1]:
    case "userid":
        print("aly3ye")
    case "genkey": 
        p = int(sys.argv[2]) # size
        o = int(sys.argv[3])
        x = int(sys.argv[4]) # base point x
        y = int(sys.argv[5]) # base point y
        genkey(p,o,x,y)
    case "sign": #(p, o, Gx, Gy, d, h)
        p = int(sys.argv[2]) # size
        o = int(sys.argv[3])
        x = int(sys.argv[4]) # base point x
        y = int(sys.argv[5]) # base point y
        d = int(sys.argv[6])
        h = int(sys.argv[7])
        r, s = signature(p,o,x,y,d,h)
        print(r)
        print(s)
    case "verify":
        p = int(sys.argv[2]) # size
        o = int(sys.argv[3])
        x = int(sys.argv[4]) # base point x
        y = int(sys.argv[5]) # base point y
        Qx = int(sys.argv[6]) # public key
        Qy = int(sys.argv[7]) # 
        r = int(sys.argv[8]) # signature
        s = int(sys.argv[9]) # r and s
        h = int(sys.argv[10]) # hash

        print(verify(p,o,x,y,Qx,Qy,r,s,h))



# print(scalar_mult(12, 31, 1000, 43))