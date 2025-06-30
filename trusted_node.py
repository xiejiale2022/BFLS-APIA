import numpy as np
from .fisco_client import FISCOClient
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import os
import json

class KeyAuthorityNode:
    def __init__(self):
        self.fisco = FISCOClient()
        
        # Generate ECDSA key pair
        self.ecdsa_private_key = ec.generate_private_key(ec.SECP256K1())
        self.ecdsa_public_key = self.ecdsa_private_key.public_key()
        
        # Register public key on blockchain
        pub_bytes = self.ecdsa_public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        self.fisco.register_public_key(pub_bytes[:32], pub_bytes[32:])
    
    def generate_global_secret(self, servers):
        # Collect random values from servers
        random_values = []
        for server in servers:
            # In real implementation, get encrypted random value from blockchain
            random_value = os.urandom(32)  # Simulated
            random_values.append(random_value)
        
        # Combine to create global secret
        global_secret = b''.join(random_values)[:32]
        return global_secret
    
    def shamir_secret_share(self, secret, n, k):
        # Simplified Shamir's Secret Sharing
        # In real implementation, use proper SSS
        shares = []
        for i in range(1, n+1):
            # For demo, just split into n parts
            share = secret[:len(secret)//n]  # Not secure, just for demo
            shares.append(share)
        return shares
    
    def encrypt_share(self, share, device_public_key):
        # Generate shared secret using ECDH
        shared_secret = self.ecdsa_private_key.exchange(
            ec.ECDH(), 
            device_public_key
        )
        
        # Derive symmetric key
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'key_share_encryption',
        ).derive(shared_secret)
        
        # Encrypt share using AES
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(derived_key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        encrypted_share = encryptor.update(share) + encryptor.finalize()
        tag = encryptor.tag
        
        return iv + encrypted_share + tag
    
    def distribute_key_shares(self, shares, devices):
        for i, device in enumerate(devices):
            # Get device's public key from blockchain
            x, y = self.fisco.get_public_key(device)
            pub_bytes = x + y
            device_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256K1(), pub_bytes
            )
            
            encrypted_share = self.encrypt_share(shares[i], device_public_key)
            self.fisco.upload_key_share(device, encrypted_share)

class ModelDecryptionNode:
    def __init__(self):
        self.fisco = FISCOClient()
        
        # Generate ECDSA key pair
        self.ecdsa_private_key = ec.generate_private_key(ec.SECP256K1())
        self.ecdsa_public_key = self.ecdsa_private_key.public_key()
        
        # Register public key on blockchain
        pub_bytes = self.ecdsa_public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        self.fisco.register_public_key(pub_bytes[:32], pub_bytes[32:])
    
    def reconstruct_secret(self, shares):
        # Simplified secret reconstruction
        # In real implementation, use proper Shamir reconstruction
        return b''.join(shares)[:32]  # Not secure, just for demo
    
    def decrypt_model(self, encrypted_model, secret):
        # Derive symmetric key from secret
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'model_decryption',
        ).derive(secret)
        
        # Split encrypted data
        iv = encrypted_model[:16]
        ciphertext = encrypted_model[16:-16]
        tag = encrypted_model[-16:]
        
        # Decrypt model
        cipher = Cipher(algorithms.AES(derived_key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        decrypted_model = decryptor.update(ciphertext) + decryptor.finalize()
        
        return decrypted_model
    
    def aggregate_models(self, models):
        # Simple average aggregation
        model_arrays = [np.frombuffer(m, dtype=np.float32) for m in models]
        aggregated = np.mean(model_arrays, axis=0)
        return aggregated.tobytes()
