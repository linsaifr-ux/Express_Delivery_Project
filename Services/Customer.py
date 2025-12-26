from __future__ import annotations
"""
Created on Wed Dec 10 21:26:22 2025

@author: laisz
"""
from platformdirs import user_data_dir
import json, pickle
from PaymentArrangement import BillingTiming
from Bill import Bill
from Location import Destination
from OrderHandler import OrdersHandler
from Order import Order
from os.path import isfile, join


def get_dir() -> str:
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        
    return user_data_dir(config['app_name'], config['project_name']) + config['customer_suffix']

class Customer:
    """
    """
    ## Class attribute
    __DATA_PATH = get_dir()
    _OH = OrdersHandler()
    
    
    def __init__(self, ID: int, first_name: str, last_name: str, address: Destination,
                 phone_number: str, password: str, billing_pref: BillingTiming,
                 bill_cnt: int = 0):
        if isfile(join(self.__DATA_PATH, f"{ID}.pkl")):
            raise ValueError("The ID specified is taken. Maybe use 'from_ID' to unpickle it?")
        
        self._ID = f"C{ID:05d}"
        self._first_name = first_name
        self._last_name = last_name
        
        # This line invokes the logic defined in @address.setter
        self.address = address
        
        # This line invokes the logic defined in @number.setter
        self.number = phone_number
        
        self._password = password
        self._billing_pref = billing_pref
        self._bill_cnt = bill_cnt
        self._bill: dict[Bill] = {}
        
        
    @property
    def first_name(self) -> str:
        return self._first_name
    
    @property
    def last_name(self) -> str:
        return self._last_name
    
    @property
    def address(self) -> str:
        return self._address
    
    @address.setter
    def address(self, new_address):
        self._address = new_address
        
    @property
    def ID(self) -> str:
        return self._ID
    
    @property
    def number(self):
        return self._number
    
    @number.setter
    def number(self, phone_number: str) -> None:
        for char in phone_number:
            if not (char.isdigit() or char == " "):
                raise ValueError(f"phone_number contains invalid character '{char}'.")
        self._number = phone_number
    
    @property
    def billing_pref(self) -> BillingTiming:
        return self._billing_pref
        
    @property
    def bill_cnt(self) -> int:
        return self._bill_cnt
    
    
    ## Methods
    def __str__(self) -> str:
        return (f"Name\t: {self.first_name} {self.last_name}\n"
                + f"ID\t\t: {self.ID}\n"
                + f"Address\t: {self.address}\n"
                + f"Phone Number\t: {self.number}\n"
                + f"Billing Preferrence\t: {self.billing_pref.name}")
    
    def verify(self, password: str) -> bool:
        return self._password == password
    
    def set_billing_pref(self, new_pref: BillingTiming) -> None:
        if not isinstance(new_pref, BillingTiming):
            raise TypeError("Invalid choice of billing preferrece!")
        self.__billing_pref = new_pref
        
    def my_orders(self) -> list[Order]:
        return self._OH.filter_by_customer(self.ID, self.bill_cnt)
    
    def get(self, order_ID: str) -> Order:
        if self.ID[1:] == order_ID[1:6]:
            return self._OH.get(order_ID)
        else:
            raise RuntimeError(f"Access to order ({order_ID}) denied!")
            
    def filter_by_date(self, start_date, end_date) -> list[Order]:
        targets = []
        for order in self.my_orders():
            if order.due_date >= start_date and order.due_date <= end_date:
                targets.append(order)
                
        return targets
    
    def bill(self, order: Order) -> None:
        if order.bill_ref is not None:
            return
        
        if (order.bill_timing is not BillingTiming.monthly
            or self._bill.values()[-1].issue_status): # The last bill is issued
            my_bill = Bill(self, order)
            self._bill[my_bill.ID] = my_bill
        else:
            self._bill.values()[-1].add_item(order)
        
    def pay(self, bill_ID: str, *pay_args) -> None:
        self._bill[bill_ID].pay(*pay_args)
    
    def new_order(self, *order_args):
        self._OH.add(*order_args)
        
    def save(self) -> None:
        """
        Calling this method would save the Customer object's field as
        a pkl file in local directory.
        """        
        with open(join(self.__DATA_PATH, f"{self.ID}.pkl"), 'wb') as file:
            pickle.dump(self, file, protocol=4)
        return
    
    def __del__(self):
        self.save()
        return
    
    
    @classmethod
    def from_ID(cls, ID: str) -> Customer:
        """
        This is a factory method that would reconstruct the customer instance 
        base on <ID>.json in local directory.
        
        Parameters
        ----------
        ID : str
            The ID of the customer instance to reconstruct

        Returns
        -------
        Customer
        """
        file_path = join(cls.__DATA_PATH , f"{ID}.pkl")
        if not isfile(file_path):
            raise FileNotFoundError("The Customer with the provided ID does not exist!")
            
        with open(file_path, 'rb') as file:
            instance = pickle.load(file)
        
        return instance
        
if __name__ == "__main__":
    def check_pickleability(obj):
        try:
            pickle.dumps(obj)
            print("✅ Everything in the composition is pickleable!")
        except Exception as e:
            print(f"❌ Pickle Error found: {e}")

    # Run it on your customer
    c = Customer(5, "Samuel", "Lai", "address", "12345", "0000", BillingTiming.in_advance)
    check_pickleability(c)
    c.save()
    a = Customer.from_ID('C00005')
    print(a)