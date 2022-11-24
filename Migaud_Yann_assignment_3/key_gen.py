import random
from math import gcd


#verif_p: function verifying that given values of p and g are compatible for 
#         diffie-hellmann
def verif_p(p, g):
    if (g > 1 and p > 2):                       #g = 1 forbidden because 1**k will always give 1; p = 1 and p = 2 forbidden because the algorithm needs at least one member of the cyclic group other than 1
        for i in range(2, p):                           #value 1 not needed for the test as any number power 0 gives 1
            if (gcd(i, p) == 1):                           #verifying if i is coprime to p
                
                found = False           #^ initialization of the loop
                k = 1                   #v
                
                while (found == False and k <= p): #loop to find the first k respecting "g**k = a%p" with a a coprime of p
                    if ((g**k)%p == i):
                        found = True
                        break
                    k += 1
                    
                if (found == False):            #if there is a coprime of p for which k does not exist, then p and g are not compatible and a new couple must be selected
                    print("p and g not compatible, please select another couple\n")
                    return False
                    
        # print("p and g compatible\n")
        return True
    else:
        if (g <= 1):                                                    #^
            print("Error, g must be strictly greater than 1.\n")        #|
            return False                                                #| if p and g are not respectively strictly greater than 2 and 1 then they must also be chosen again
        if (p <= 2):                                                    #|
            print("Error, p must be strictly greater than 2.\n")        #|
            return False                                                #v
                

#cycle: function to create a list of the elements in the cyclic group for the
#       given parameters p and q
def cycle(limit, gen):
    res = {}
    for i in range(0, limit):
        res[i] = (gen**i)%limit
    return res

#gen_keys: function to generate the couple private key/public key for the user
def gen_keys(limit, gen):
    group = cycle(limit, gen)   #^
    for i in range(0, limit):   #| taking the cyclic group and deleting all the occurrences of 1 in the values of the dictionary (because those values are possible public keys, and for the shared key computation, having a public key equal to 0 means in bbs, all the steps are also equal to 0)
        if (group[i] == 1):     #|
            del(group[i])       #v
    
    prv = random.choice(list(group.keys())) #selecting a (pseudo) random element in the remaining ditcionary to get the private and public keys
    pub = group[prv]
    return (pub, prv)

#compute_shared: function to compute the shared key from the public key of 
#                the other endpoint
def compute_shared(key, prv_key, limit):
    shared = (key**prv_key)%limit
    return shared