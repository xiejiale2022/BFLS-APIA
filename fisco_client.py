from web3 import Web3
import json
import os

class FISCOClient:
    def __init__(self, config_file='config.ini'):
        self.config = self.load_config(config_file)
        self.w3 = Web3(Web3.HTTPProvider(self.config['node_url']))
        self.chain_id = self.config['chain_id']
        self.account = self.w3.eth.account.from_key(self.config['private_key'])
        
        # Load contracts
        self.fl_manager = self.load_contract(
            self.config['fl_manager_address'], 
            self.config['fl_manager_abi']
        )
        self.key_manager = self.load_contract(
            self.config['key_manager_address'], 
            self.config['key_manager_abi']
        )
    
    def load_config(self, config_file):
        # Load configuration from file
        config = {
            'node_url': 'http://127.0.0.1:8545',
            'chain_id': 1,
            'private_key': '0x...',
            'fl_manager_address': '0x...',
            'key_manager_address': '0x...'
        }
        # In real implementation, load from config file
        return config
    
    def load_contract(self, address, abi_file):
        with open(abi_file) as f:
            abi = json.load(f)
        return self.w3.eth.contract(address=address, abi=abi)
    
    def send_transaction(self, contract_function, *args):
        tx = contract_function(*args).build_transaction({
            'chainId': self.chain_id,
            'gas': 2000000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
        })
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)
    
    # FLManager methods
    def register_organization(self, server, devices):
        tx_receipt = self.send_transaction(
            self.fl_manager.functions.registerOrganization,
            server,
            devices
        )
        return tx_receipt
    
    def upload_local_model(self, encrypted_model):
        tx_receipt = self.send_transaction(
            self.fl_manager.functions.uploadLocalModel,
            encrypted_model
        )
        return tx_receipt
    
    def update_global_model(self, parameters):
        tx_receipt = self.send_transaction(
            self.fl_manager.functions.updateGlobalModel,
            parameters
        )
        return tx_receipt
    
    def get_global_model(self):
        return self.fl_manager.functions.getGlobalModel().call()
    
    # KeyManager methods
    def register_public_key(self, x, y):
        tx_receipt = self.send_transaction(
            self.key_manager.functions.registerPublicKey,
            x,
            y
        )
        return tx_receipt
    
    def upload_key_share(self, device, encrypted_share):
        tx_receipt = self.send_transaction(
            self.key_manager.functions.uploadKeyShare,
            device,
            encrypted_share
        )
        return tx_receipt
    
    def get_public_key(self, owner):
        return self.key_manager.functions.getPublicKey(owner).call()
    
    def get_key_share(self, owner, device):
        return self.key_manager.functions.getKeyShare(owner, device).call()
