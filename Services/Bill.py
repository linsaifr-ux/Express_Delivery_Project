# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Created on Wed Dec 10 21:26:22 2025

@author: laisz
"""
from PaymentRecord import PaymentRecord
from PaymentArrangement import PaymentMethod
from typing import TYPE_CHECKING
from datetime import date, timedelta, datetime

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
        issue_status (bool): whether the customer is notified to pay this bill
        payment_status (bool): True if the bill has been paid, False otherwise.
        due_date (date): the date this bill is due, which is 15 days after
                        the bill is issued
        payment_record (PaymentRecord or None): Details of the payment if completed.
        manifest (list[str]): A list of Order IDs included in this bill.

    Methods:
        pay(transaction_ID, method): Attempts to process payment for the bill.
        verify_payment(): Returns the current payment status.
    """
    
    def __init__(self, outer_ref: Customer, order: Order = None):
        """
        Initialize Bill

        Parameters
        ----------
        outer_ref : Customer
            The customer who will be paying the bill.
        payment_amount : float
            The amount of money to pay.
        order : Order
            The delivery that is billed.

        """
        self.outer = outer_ref
        self._ID = "B" + str(self.outer.ID)[1:] + f"{self.outer.bill_cnt:04d}"
        self._amount = 0
        self._issue_status = False
        self._payment_status = False
        self._due_date = None
        self._payment_record = None
        self._manifest = []
        
        if order is not None:
            self._amount += order.fee
            self._manifest.append(order.ID)
            
    
    @property
    def ID(self) -> str:
        return self._ID
    
    @property
    def amount(self) -> float:
        return self._amount
    
    @property
    def issue_status(self) -> bool:
        return self._issue_status
        
    @property
    def payment_status(self) -> bool:
        return self._payment_status
    
    @property
    def due_date(self) -> date:
        return self._due_date
    
    @property
    def payment_record(self) -> PaymentRecord:
        return self._payment_record
    
    @property
    def manifest(self) -> list[str]:
        return self._manifest.copy()

    
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
            self._payment_status = True
            self._payment_record = PaymentRecord(transaction_ID, method)
        else:
            raise ValueError(f"Invalid transaction ID: {transaction_ID}")
            
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
        return self._payment_status
    
    def issue(self) -> None:
        """
        changed the bill status to issued and set the due_date

        Returns
        -------
        None
        """
        
        self._due_date = date.today() + timedelta(days=15)
        self._issue_status = True
    
    def snapshot(self) -> dict:
        """
        Create a dictionary containing states of the Bill.
        Use this method when the object are being saved as file.

        Returns
        -------
        dict
            A dictionary containing all neccesary state to reconstruct the Bill object

        """
        snapshot = {'ID': self.ID[len(self.outer.ID):],
                    'amount': self.amount,
                    'issue_status': self.issue_status,
                    'payment_status': self.payment_status,
                    'manifest': self.manifest}
        
        if self.issue_status:
            snapshot['due_date'] = self.due_date.__str__()
            
        if self.payment_status:
            snapshot['payment_record'] = self.payment_record.snapshot()
        
        return snapshot
    
    @classmethod
    def from_dict(cls, data: dict, outer_ref: Customer) -> Bill:
        """
        Reconstruct the instance from a previous snapshot

        Parameters
        ----------
        data : dict
            a snapshot taken previously
        outer_ref : Customer
            The customer who will be paying the bill.

        Returns
        -------
        Bill
        """
        instance = cls(outer_ref)
        instance._ID = "B" + str(instance.outer.ID)[1:] + data.get('ID')
        instance._amount = data.get('amount')
        instance._issue_status = data.get('issue_status')
        instance._payment_status = data.get('payment_status')
        instance._due_date = None
        instance._payment_record = PaymentRecord.from_dict(data.get('payment_record'), None)
        instance._manifest = data.get('manifest')
        
        if data.get('due_date', None) is not None:
            instance._due_date = datetime.strptime(data['due_date'], "%Y-%m-%d").date()
        
        return instance
    
    
class MonthlyBill(Bill):
    """    
    Attributes:
        month: The duration of collecting payments
        
    Methods:
        add_item(order): Adds an Order to the bill, updating the manifest and amount.
    """
    def __init__(self, outer_ref, order: Order):
        """
        Initialize MonthlyBill

        Parameters
        ----------
        outer_ref : Customer
            The customer who will be paying the bill.
        order : Order
            The source of the fee

        """
        super().__init__(outer_ref, order) 
        
        # set self._due_date to 15th of next month
        self._due_date = (date.today().replace(day=1) + timedelta(days=32)).replace(day=15)
        
    @property
    def month(self) -> int:
        return (self.due_date.month - 2) % 12 + 1
    
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
        if self.issue_status:
            raise RuntimeError("Adding to an issued bill!")
            
        self._manifest.append(order.ID)
        self._amount += order.fee
        
    def issue(self) -> None:
        """
        changed the bill status to issued

        Returns
        -------
        None
        """
        self._issue_status = True
    
if __name__ == "__main__":
    
    class ABC:
        def __init__(self):
            self.ID = 'C00005'
            self.bill_cnt = 40
            
    class order:
        def __init__(self):
            self.ID = 'O124577'
            self.fee = 100.0
    bill = MonthlyBill(ABC(), order())
    print(bill.due_date)
    print(bill.month)
    bill.pay('55555', PaymentMethod.card)
    print(bill.ID)
    snap = bill.snapshot()
    print(snap)
    copy = Bill.from_dict(snap, ABC())
    print(copy.payment_record)
    
