# -*- coding: utf-8 -*-

from __future__ import annotations
"""
Created on Wed Dec 12 15:21:22 2025

@author: Frank
"""
from PaymentArrangement import PaymentMethod


class PaymentRecord:
    """
    Payment Record class.
    Stores transaction ID and payment method.
    """
    def __init__(self, transaction_ID: str, method: PaymentMethod):
        """
        Initialize Payment Record.
        
        Parameters
        ----------
        transaction_ID : str
            The transaction ID.
        method : PaymentMethod
            The method of payment.
        """
        self.__transaction_ID = transaction_ID
        
        if not isinstance(method, PaymentMethod):
            raise TypeError("The method provided is invalid!")
        self.__method = method
        
    @property
    def transaction_ID(self) -> str:
        return self.__transaction_ID
        
    @property
    def method(self) -> PaymentMethod:
        return self.__method
    
    def snapshot(self) -> dict:
        """
        Create a dictionary containing the data of the object
        """
        snapshot = {'transaction_ID': self.transaction_ID,
                    'method': self.method.value}
        return snapshot
    
    @classmethod
    def from_dict(cls, data: dict|None) -> PaymentRecord:
        """
        Reconstruct the instance from a previous snapshot
        
        """
        if data is None:
            return None
        else:
            return cls(data['transaction_ID'], PaymentMethod(data['method']))
    
if __name__ == "__main__":
    record = PaymentRecord('104060', PaymentMethod.cash)
    sp = record.snapshot()
    replica = PaymentRecord.from_dict(sp)
    print(replica.transaction_ID, replica.method)
    
    