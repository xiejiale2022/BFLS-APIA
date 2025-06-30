import time
import numpy as np
from sdk.edge_device import EdgeDevice
from sdk.edge_server import EdgeServer
from sdk.trusted_node import KeyAuthorityNode, ModelDecryptionNode
from sdk.fisco_client import FISCOClient

def simulate_fl_training(total_rounds=10, local_epochs=5, num_devices=5):
    # Initialize blockchain client
    fisco = FISCOClient()
    
    # Create organizations and devices
    org_address = "org1"
    devices = [f"device{i}" for i in range(num_devices)]
    
    # Register organization on blockchain
    fisco.register_organization(org_address, devices)
    
    # Create edge devices
    edge_devices = []
    for i in range(num_devices):
        dev = EdgeDevice(f"Device{i}", org_address, f"priv_key_{i}", devices[i])
        edge_devices.append(dev)
    
    # Create edge server
    edge_server = EdgeServer(org_address, devices)
    
    # Create trusted nodes
    key_authority = KeyAuthorityNode()
    model_decryptor = ModelDecryptionNode()
    
    # Generate and distribute global secret
    global_secret = key_authority.generate_global_secret([org_address])
    shares = key_authority.shamir_secret_share(global_secret, num_devices, num_devices//2+1)
    key_authority.distribute_key_shares(shares, devices)
    
    # Initialize global model
    global_model = np.random.randn(100).astype(np.float32).tobytes()
    fisco.update_global_model(global_model)
    
    # Training loop
    for round in range(1, total_rounds+1):
        print(f"\n=== Starting Round {round}/{total_rounds} ===")
        
        # Devices download global model
        current_global_model = fisco.get_global_model()
        
        # Local training
        local_models = []
        for device in edge_devices:
            # Simulate local data
            local_data = np.random.randn(100).astype(np.float32)
            
            # Train local model
            local_model = device.train_local_model(
                current_global_model, 
                local_data, 
                local_epochs
            )
            
            # Encrypt model
            # In real implementation, get server's public key from blockchain
            encrypted_model = device.encrypt_model(
                local_model, 
                edge_server.ecdsa_public_key
            )
            
            # Upload encrypted model
            device.upload_model(encrypted_model, round)
            local_models.append(encrypted_model)
        
        # Edge server processes local models
        # Step 1: Calculate weighted geometric center
        last_gwc = edge_server.weighted_geometric_center([], None, round, total_rounds)
        gwc = edge_server.weighted_geometric_center(local_models, last_gwc, round, total_rounds)
        
        # Step 2: Detect outliers
        valid_models, valid_indices = edge_server.detect_outliers(local_models, gwc)
        print(f"Filtered {len(local_models) - len(valid_models)} outliers")
        
        # Step 3: Aggregate valid models
        aggregated_model = edge_server.aggregate_local_models(valid_models)
        
        # Upload aggregated model to blockchain
        edge_server.upload_aggregated_model(aggregated_model)
        
        # Model decryption node processes global model
        # In real implementation, this would be triggered by smart contract
        if round % 2 == 0:  # Periodically decrypt
            # Collect key shares from devices
            key_shares = []
            for device in edge_devices:
                share = device.receive_key_share(key_authority.ecdsa_public_key)
                key_shares.append(share)
            
            # Reconstruct secret
            secret = model_decryptor.reconstruct_secret(key_shares)
            
            # Decrypt and re-aggregate
            decrypted_models = []
            for model in valid_models:
                decrypted = model_decryptor.decrypt_model(model, secret)
                decrypted_models.append(decrypted)
            
            # Aggregate decrypted models
            true_aggregated = model_decryptor.aggregate_models(decrypted_models)
            
            # Update global model
            fisco.update_global_model(true_aggregated)
        
        print(f"Completed Round {round}")
        time.sleep(1)

if __name__ == "__main__":
    simulate_fl_training(total_rounds=5, local_epochs=3, num_devices=5)
