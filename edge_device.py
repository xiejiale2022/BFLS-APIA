import numpy as np
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import json
from .fisco_client import FISCOClient

class EdgeDevice:
    def __init__(self, name, org, private_key, device_address):
        self.name = name
        self.org = org
        self.private_key = private_key
        self.device_address = device_address
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
    
    def train_local_model(self, global_model, data, epochs):
        # Simplified training process
        # In real implementation, use PyTorch/TensorFlow
        model = np.frombuffer(global_model, dtype=np.float32)
        
        # Simulate training
        for _ in range(epochs):
            # Update model based on local data
            model += np.random.normal(0, 0.1, model.shape)
        
        return model.tobytes()
    
    def encrypt_model(self, model, public_key):
        # Generate shared secret using ECDH
        shared_secret = self.ecdsa_private_key.exchange(ec.ECDH(), public_key)
        
        # Derive symmetric key
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'model_encryption',
        ).derive(shared_secret)
        
        # Encrypt model using AES
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(derived_key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        encrypted_model = encryptor.update(model) + encryptor.finalize()
        tag = encryptor.tag
        
        return iv + encrypted_model + tag
    
    def upload_model(self, encrypted_model, round):
        # Upload to blockchain
        self.fisco.upload_local_model(encrypted_model)
    
    def download_global_model(self):
        return self.fisco.get_global_model()
    
    def receive_key_share(self, owner):
        encrypted_share = self.fisco.get_key_share(owner, self.device_address)
        # In real implementation, decrypt using device's private key
        return encrypted_share
