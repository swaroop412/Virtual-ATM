import os
import json
from datetime import datetime
import logging
from models import Account, Transaction

class ATM:
    def __init__(self, data_file='data/accounts.json'):
        self.data_file = data_file
        self.accounts = {}
        self.load_accounts()
        
        # Create demo account if no accounts exist
        if not self.accounts:
            self._create_demo_accounts()
    
    def load_accounts(self):
        """Load accounts from JSON file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # Create file if it doesn't exist
            if not os.path.exists(self.data_file):
                with open(self.data_file, 'w') as f:
                    json.dump({}, f)
            
            # Load accounts from file
            with open(self.data_file, 'r') as f:
                accounts_data = json.load(f)
                
            for acc_num, acc_data in accounts_data.items():
                self.accounts[acc_num] = Account.from_dict(acc_data)
                
            logging.debug(f"Loaded {len(self.accounts)} accounts from {self.data_file}")
        except Exception as e:
            logging.error(f"Error loading accounts: {e}")
            self.accounts = {}
    
    def save_accounts(self):
        """Save accounts to JSON file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            accounts_data = {
                acc_num: account.to_dict() 
                for acc_num, account in self.accounts.items()
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(accounts_data, f, indent=2)
                
            logging.debug(f"Saved {len(self.accounts)} accounts to {self.data_file}")
        except Exception as e:
            logging.error(f"Error saving accounts: {e}")
    
    def _create_demo_accounts(self):
        """Create demo accounts for testing."""
        demo_accounts = [
            Account("123456", "1234", 1000.0),
            Account("654321", "4321", 500.0)
        ]
        
        # Add some transactions
        demo_accounts[0].add_transaction("deposit", 1000.0)
        demo_accounts[1].add_transaction("deposit", 500.0)
        
        for account in demo_accounts:
            self.accounts[account.account_number] = account
        
        self.save_accounts()
        logging.info("Created demo accounts")
    
    def authenticate(self, account_number, pin):
        """Authenticate a user by account number and PIN."""
        if account_number in self.accounts and self.accounts[account_number].pin == pin:
            logging.info(f"User {account_number} authenticated successfully")
            return True
        logging.warning(f"Failed authentication attempt for account {account_number}")
        return False
    
    def check_balance(self, account_number):
        """Check the balance of an account."""
        if account_number in self.accounts:
            return self.accounts[account_number].balance
        return 0.0
    
    def withdraw(self, account_number, amount):
        """Withdraw money from an account."""
        if account_number not in self.accounts:
            return {"success": False, "message": "Account not found"}
        
        account = self.accounts[account_number]
        
        if amount <= 0:
            return {"success": False, "message": "Amount must be positive"}
        
        if amount > account.balance:
            return {"success": False, "message": "Insufficient funds"}
        
        account.add_transaction("withdrawal", amount)
        self.save_accounts()
        
        logging.info(f"Withdrawal of ${amount:.2f} from account {account_number}")
        return {"success": True, "message": f"Successfully withdrew ${amount:.2f}"}
    
    def deposit(self, account_number, amount):
        """Deposit money into an account."""
        if account_number not in self.accounts:
            return {"success": False, "message": "Account not found"}
        
        account = self.accounts[account_number]
        
        if amount <= 0:
            return {"success": False, "message": "Amount must be positive"}
        
        account.add_transaction("deposit", amount)
        self.save_accounts()
        
        logging.info(f"Deposit of ${amount:.2f} to account {account_number}")
        return {"success": True, "message": f"Successfully deposited ${amount:.2f}"}
    
    def get_transactions(self, account_number):
        """Get transaction history for an account."""
        if account_number not in self.accounts:
            return []
        
        # Return transactions in reverse chronological order (newest first)
        return list(reversed(self.accounts[account_number].transactions))
        
    def change_pin(self, account_number, old_pin, new_pin):
        """Change the PIN for an account."""
        if account_number not in self.accounts:
            return {"success": False, "message": "Account not found"}
            
        account = self.accounts[account_number]
        
        # Verify old PIN
        if account.pin != old_pin:
            return {"success": False, "message": "Current PIN is incorrect"}
            
        # Validate new PIN
        if not new_pin or len(new_pin) < 4:
            return {"success": False, "message": "PIN must be at least 4 characters"}
            
        # Update PIN
        account.pin = new_pin
        self.save_accounts()
        
        logging.info(f"PIN changed for account {account_number}")
        return {"success": True, "message": "PIN successfully changed"}
    
    def transfer(self, from_account_number, to_account_number, amount):
        """Transfer money from one account to another."""
        # Validate accounts
        if from_account_number not in self.accounts:
            return {"success": False, "message": "Source account not found"}
            
        if to_account_number not in self.accounts:
            return {"success": False, "message": "Destination account not found"}
            
        if from_account_number == to_account_number:
            return {"success": False, "message": "Cannot transfer to the same account"}
            
        # Validate amount
        if amount <= 0:
            return {"success": False, "message": "Amount must be positive"}
            
        from_account = self.accounts[from_account_number]
        to_account = self.accounts[to_account_number]
        
        # Check sufficient funds
        if amount > from_account.balance:
            return {"success": False, "message": "Insufficient funds for transfer"}
            
        # Perform transfer
        from_account.add_transaction("transfer_out", amount)
        to_account.add_transaction("transfer_in", amount)
        
        self.save_accounts()
        
        logging.info(f"Transfer of ${amount:.2f} from {from_account_number} to {to_account_number}")
        return {"success": True, "message": f"Successfully transferred ${amount:.2f} to account {to_account_number}"}
