# -*- coding: utf-8 -*-
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
from os import listdir
from os.path import isfile, join


def get_dir() -> str:
    """
    Get the data directory path for storing customer data.
    
    Returns
    -------
    str
        The full path to the customer data directory.
    """
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        
    return user_data_dir(config['app_name'], config['project_name']) + config['customer_suffix']

class Customer:
    """
    Represents a customer in the package delivery system, managing their
    personal information, orders, and billing.

    Attributes:
        ID (str): The unique identifier for the customer.
        first_name (str): The customer's first name.
        last_name (str): The customer's last name.
        address (Destination): The customer's address.
        number (str): The customer's phone number.
        billing_pref (BillingTiming): The customer's billing preference.
        bill_cnt (int): The count of bills associated with this customer.

    Methods:
        verify(password): Verify if the provided password matches.
        set_billing_pref(new_pref): Update the customer's billing preference.
        my_orders(): Get all orders belonging to this customer.
        get(order_ID): Get a specific order by ID.
        filter_by_date(start_date, end_date): Filter orders by date range.
        bill(order): Create or add to a bill for an order.
        pay(bill_ID, *pay_args): Process payment for a bill.
        new_order(*order_args): Create a new order.
        save(): Save the customer data to local storage.
        from_ID(ID): Class method to load a customer from stored data.
    """
    ## Class attribute
    __DATA_PATH = get_dir()
    _cnt = len(listdir(__DATA_PATH))
    
    
    def __init__(self, first_name: str, last_name: str, address: Destination,
                 phone_number: str, email: str,password: str, 
                 billing_pref: BillingTiming,):
        """
        Initialize a new Customer and create customer's data file in local storage.

        Parameters
        ----------
        first_name : str
            The customer's first name.
        last_name : str
            The customer's last name.
        address : Destination
            The customer's address.
        phone_number : str
            The customer's phone number (digits and spaces only).
        email: str
            The customer' email
        password : str
            The customer's password for authentication.
        billing_pref : BillingTiming
            The customer's billing preference.
        bill_cnt : int, optional
            Initial bill count (default is 0).
        """
        if isfile(join(self.__DATA_PATH, f"C{self._cnt:05d}.pkl")):
            raise ValueError("The ID specified is taken. Maybe use 'from_ID' to unpickle it?")
        
        self._ID = f"C{self._cnt:05d}"
        self._first_name = first_name
        self._last_name = last_name
        
        # This line invokes the logic defined in @address.setter
        self.address = address
        
        # This line invokes the logic defined in @number.setter
        self.number = phone_number
        
        self._email = email
        self._password = password
        self._billing_pref = billing_pref
        self._bill_cnt = 0
        self._bill: dict[Bill] = {}
        self._cnt += 1
        
        # Register email in the email index for login lookup
        index_path = join(self.__DATA_PATH, 'email_index.json')
        if isfile(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                email_index = json.load(f)
        else:
            email_index = {}
        
        # Check for duplicate email
        if email in email_index:
            raise ValueError(f"Email '{email}' is already registered!")
        
        email_index[email] = self._ID
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(email_index, f, indent=2)

        # Save customer data to local storage
        self.save()
        
        
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
        self.save()
        
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
        self.save()
    
    @property
    def email(self) -> str:
        return self._email
    
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
                + f"Email\t: {self.email}\n"
                + f"Billing Preferrence\t: {self.billing_pref.name}")
    
    def verify(self, password: str) -> bool:
        """
        Verify if the provided password matches the customer's password.

        Parameters
        ----------
        password : str
            The password to verify.

        Returns
        -------
        bool
            True if the password matches, False otherwise.
        """
        return self._password == password
    
    def set_billing_pref(self, new_pref: BillingTiming) -> None:
        """
        Update the customer's billing preference.

        Parameters
        ----------
        new_pref : BillingTiming
            The new billing preference.

        Returns
        -------
        None
        """
        if not isinstance(new_pref, BillingTiming):
            raise TypeError("Invalid choice of billing preferrece!")
        self._billing_pref = new_pref
        self.save()
        
    def my_orders(self) -> list[Order]:
        """
        Get all orders belonging to this customer.

        Parameters
        ----------
        None

        Returns
        -------
        list[Order]
            A list of Order objects associated with this customer.
        """
        return OrdersHandler().filter_by_customer(self.ID)
    
    def get(self, order_ID: str) -> Order:
        """
        Get a specific order by its ID.

        Parameters
        ----------
        order_ID : str
            The ID of the order to retrieve.

        Returns
        -------
        Order
            The requested Order object.

        Raises
        ------
        RuntimeError
            If the customer does not have access to the requested order.
        """
        order = OrdersHandler().get(order_ID)
        if order.payer != self.ID:
            raise RuntimeError(f"Access to order ({order_ID}) denied!")
        return order
            
    def filter_by_date(self, start_date, end_date) -> list[Order]:
        """
        Filter orders by the due date.

        Parameters
        ----------
        start_date : date
            The start date of the range (inclusive).
        end_date : date
            The end date of the range (inclusive).

        Returns
        -------
        list[Order]
            A list of orders within the specified date range.
        """
        targets = []
        for order in self.my_orders():
            if order.due_date >= start_date and order.due_date <= end_date:
                targets.append(order)
                
        return targets
    
    def bill(self, order: Order) -> None:
        """
        Create or add to a bill for an order.

        Parameters
        ----------
        order : Order
            The order to be billed.

        Returns
        -------
        None
        """
        if order.bill_ref is not None:
            return
        
        if (order.bill_timing is not BillingTiming.monthly
            or self._bill.values()[-1].issue_status): # The last bill is issued
            my_bill = Bill(self, order)
            self._bill[my_bill.ID] = my_bill
        else:
            self._bill.values()[-1].add_item(order)

        self.save()
        
    def pay(self, bill_ID: str, *pay_args) -> None:
        """
        Process payment for a bill.

        Parameters
        ----------
        bill_ID : str
            The ID of the bill to pay.
        *pay_args
            Additional arguments passed to the bill's pay method.

        Returns
        -------
        None
        """
        self._bill[bill_ID].pay(*pay_args)
        self.save()
    
    def new_order(self, *order_args):
        """
        Create a new order.

        Parameters
        ----------
        *order_args
            Arguments passed to the OrdersHandler add method.

        Returns
        -------
        None
        """
        OrdersHandler().add(*order_args)
        
    def save(self) -> None:
        """
        Calling this method would save the Customer object's field as
        a pkl file in local directory.
        """        
        with open(join(self.__DATA_PATH, f"{self.ID}.pkl"), 'wb') as file:
            pickle.dump(self, file, protocol=4)
        return    
    
    @classmethod
    def from_ID(cls, ID: str) -> Customer:
        """
        This is a factory method that would reconstruct the customer instance 
        base on <ID>.pkl in local directory.
        
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
    c = Customer("Samuel", "Lai", 
                 "address", 
                 "0912 345 678", 
                 "xxxx@gmail.com",
                 "0000", 
                 BillingTiming.in_advance)
    check_pickleability(c)
    c.save()
    a = Customer.from_ID(c.ID)
    print(a)