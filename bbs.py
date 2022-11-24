from math import gcd

#main: function that computes the pseudo random number according to the bbs 
#      algortihm
def main(skey):
    rng = []
    
    s = skey        #^
    p = 0           #| initalizing variables of the loop (nb starts to 7 because it must be congru to 3 modulo 4 and because we want to have a long enough cycle)
    q = 0           #|
    nb = 11         #v
    while (p == 0 or q == 0):       #^ continue to loop until both p and q have been assigned. Choice has been made to take the 2 first numbers being coprime to g as p and q
        if (gcd(s, nb) == 1):       #|
            if (p == 0):            #|
                p = nb              #|
            else:                   #|
                q = nb              #|
        nb += 4                     #v nb increases by 4 every time to keep it congru 3 modulo 4
    
    m = p*q
    print("p: "+str(p)+"\tq: "+str(q)+"\nm: "+str(m)+"\ns: "+str(s))
    for i in range(0, 256):             #decided to create a 256 bits key for AES used later on
        xn = (s**2)%m                   #computing the value of the nth step of the algorithm
        s = xn                          #s takes the value of the current step to be used as the previous value in the next iteration of the loop
        rng.append(bin(xn)[-1])         #taking each time the least significant bit to append to the tab
    
    rng_k = ''
    for i in rng:               #^ concatenating the different values of the list rng to obtain a binary number
        rng_k += i              #v
    
    rng_k = int(rng_k, 2)
    rng_k = rng_k.to_bytes(32, 'big')
    #rng_k = str(rng_k)
    #print("rng_k: "+rng_k)
    return rng_k