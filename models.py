from datetime import datetime

class Transaction:
    def __init__(self, transaction_type, amount, balance_after, timestamp=None):
        self.transaction_type = transaction_type
        self.amount = amount
        self.balance_after = balance_after
        self.timestamp = timestamp or datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'balance_after': self.balance_after,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            transaction_type=data['transaction_type'],
            amount=data['amount'],
            balance_after=data['balance_after'],
            timestamp=data['timestamp']
        )

class Account:
    def __init__(self, account_number, pin, balance=0.0, transactions=None):
        self.account_number = account_number
        self.pin = pin
        self.balance = balance
        self.transactions = transactions or []
    
    def add_transaction(self, transaction_type, amount):
        if transaction_type == "withdrawal":
            self.balance -= amount
        elif transaction_type == "deposit":
            self.balance += amount
        elif transaction_type == "transfer_out":
            self.balance -= amount
        elif transaction_type == "transfer_in":
            self.balance += amount
        
        transaction = Transaction(transaction_type, amount, self.balance)
        self.transactions.append(transaction)
        return transaction
    
    def to_dict(self):
        return {
            'account_number': self.account_number,
            'pin': self.pin,
            'balance': self.balance,
            'transactions': [t.to_dict() for t in self.transactions]
        }
    
    @classmethod
    def from_dict(cls, data):
        account = cls(
            account_number=data['account_number'],
            pin=data['pin'],
            balance=data['balance']
        )
        
        account.transactions = [
            Transaction.from_dict(t) for t in data.get('transactions', [])
        ]
        
        return account
