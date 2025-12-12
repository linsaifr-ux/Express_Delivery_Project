# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Created on Wed Dec 10 21:26:22 2025

@author: laisz
"""
from PaymentRecord import PaymentRecord
from PaymentArrangement import PaymentMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Customer import Customer
    from Order import Order
    

def verify_transaction(transaction_ID, amount) -> bool:
    "A mock up for verifying a transaction."
    return True

class Bill:
    """
    Represents a bill for a Customer, tracking the payment amount,
    status, and associated orders (manifest).

    Attributes:
        outer (Customer): Reference to the Customer object this bill belongs to.
        ID (str): The unique identifier for the bill.
        amount (float): The total monetary amount of the bill.
        payment_status (bool): True if the bill has been paid, False otherwise.
        payment_record (PaymentRecord or None): Details of the payment if completed.
        manifest (list[str]): A list of Order IDs included in this bill.

    Methods:
        pay(transaction_ID, method): Attempts to process payment for the bill.
        verify_payment(): Returns the current payment status.
        add_item(order): Adds an Order to the bill, updating the manifest and amount.
    """
    
    def __init__(self, outer_ref: Customer, payment_amount: float, order_ID: str):
        """
        Initialize Bill

        Parameters
        ----------
        outer_ref : Customer
            The customer who will be paying the bill.
        payment_amount : float
            The amount of money to pay.
        order_ID : str
            The delivery that is billed.

        """
        self.outer = outer_ref
        self.__ID = "B" + str(self.outer.ID)[1:] + f"{self.outer.bill_cnt:04d}"
        self.__amount = payment_amount
        self.__payment_status = False
        self.__payment_record = None
        self.__manifest = [order_ID]
    
    @property
    def ID(self) -> str:
        return self.__ID
    
    @property
    def amount(self) -> float:
        return self.__amount
        
    @property
    def payment_status(self) -> bool:
        return self.__payment_status
    
    @property
    def payment_record(self) -> PaymentRecord:
        return self.__payment_record
    
    @property
    def manifest(self) -> list[str]:
        return self.__manifest.copy()

    
    ## Methods
    def pay(self, transaction_ID: str, method: PaymentMethod) -> None:
        """
        Mark the bill instance as payed by providing transaction_ID and the
        payment method chosen.
        
        Parameters
        ----------
        transaction_ID : str
            The transaction ID.
        method : PaymentMethod
            The method of payment.
            
            
        Return
        ----------
        None
        
        """
        if verify_transaction(transaction_ID, self.amount):
            self.__payment_status = True
            self.__payment_record = PaymentRecord(transaction_ID, method)
        else:
            print("Error, The transaction ID provided is invalid!")
            
    def verify_payment(self) -> bool:
        """
        Verify if the bill has been paid.
        
        Parameters
        ----------
        None
            
            
        Return
        ----------
        None
        
        """
        return self.__payment_status
    
    def add_item(self, order: Order) -> None:
        """
        Add another order's payment to the bill

        Parameters
        ----------
        order : Order
            The purchase of a delivery service

        Returns
        -------
        None

        """
        self.__manifest.append(order.ID)
        self.__amount += order.fee
        
    def snapshot(self) -> dict:
        snapshot = {'ID': self.ID[len(self.outer.ID):],
                    'amount': self.amount,
                    'payment_status': self.payment_status,
                    'manifest': self.__manifest}
        if self.payment_status:
            snapshot['payment_record'] = self.payment_record.snapshot()
            
        return snapshot
    
    def __restore(self, payment_status:bool, payment_record: PaymentRecord | None,
                  manifest: list[str]) -> None:
        self.__payment_status = payment_status
        self.__payment_record = payment_record
        self.__manifest = manifest
    
    @classmethod
    def from_dict(cls, data: dict, outer_ref: Customer) -> Bill:
        """
        Reconstruct the instance from a previous snapshot
        
        """
        instance = cls(outer_ref, data['amount'], '')
        instance.__restore(data['payment_status'],
                           PaymentRecord.from_dict(data.get('payment_record', None)),
                           data['manifest'])
        
        return instance
    
if __name__ == "__main__":
    class ABC:
        def __init__(self):
            self.ID = 'C00005'
            self.bill_cnt = 40
    bill = Bill(ABC(), 100.0, 'O124577')
    bill.pay('55555', PaymentMethod.card)
    print(bill.ID)
    snap = bill.snapshot()
    print(snap)
    copy = Bill.from_dict(snap, ABC())
    print(copy.payment_record)