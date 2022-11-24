import pyaes

#encrypt: function to encrypt a plaintext with a given key, following AES 
#         algorithm
def encrypt(key, plaintext):
    #key = key.encode("utf-8")
    
    aes = pyaes.AESModeOfOperationCTR(key)    
    cipher = aes.encrypt(plaintext)
    
    return cipher

#decrypt: function to decrypt a ciphertext using a given triple (ciphertext, 
#         tag and nonce) and a key
def decrypt(key, cipher):
    
    aes = pyaes.AESModeOfOperationCTR(key)
    
    plaintext = aes.decrypt(cipher).decode('utf-8')
    
    return plaintext