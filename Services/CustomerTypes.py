# -*- coding: utf-8 -*-
"""
Created on Sat Dec 27 17:12:20 2025

@author: green
"""
from Location import Destination
from PaymentArrangement import BillingTiming, PaymentMethod
from Customer import Customer
from OrderHandler import OrdersHandler
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Order import Order
'''
Normal (paying in cash or card)
Contracted (with monthly billing accounts)
Sponsored (shipping costs paid by the merchant or a third party)
'''

class Normal(Customer):
    """
    Represents a regular customer paying via cash or card.
    
    Extends Customer with card storage for payment processing.
    Only allows in_advance or on_delivery billing timing.

    Attributes
    ----------
    card : list[str]
        List of stored card numbers for the customer.

    Methods
    -------
    add_card(new_card)
        Add a new card to the customer's stored cards.
    new_order(*order_args)
        Create a new order (enforces non-monthly billing).
    pay(bill_ID, transaction_ID, payment_method)
        Process payment (enforces card or cash only).
    """
    def __init__(self, first_name: str, last_name: str, address:Destination,
                 phone_number: str, email: str,password: str, 
                 billing_pref: BillingTiming, card: str = None):
        super().__init__(first_name, last_name, address,phone_number,email,password,billing_pref)
        self._card = [card] if card else []
    
    @property
    def card(self) -> list[str]:
        return self._card.copy()
    

    def add_card(self, new_card: str) -> None:
        """
        Add a new card to the customer's stored cards.

        Parameters
        ----------
        new_card : str
            The card number to add.

        Returns
        -------
        None
        """
        self._card.append(new_card)
        self.save()
    
    #Override
    def new_order(self, *order_args) -> str:
        """
        Create a new order for Normal customer.
        
        Enforces that billing timing must be in_advance or on_delivery
        (monthly billing is not allowed for Normal customers).

        Parameters
        ----------
        *order_args
            Arguments passed to the Order constructor:
            
            bill_timing : BillingTiming
                When the bill should be issued (must be in_advance or on_delivery).
            service : Service
                The delivery service type.
            origin : Location
                The origin location of the package.
            destination : Location
                The destination location of the package.
            collector_ID : str
                The ID of the staff collecting the package.
            is_international : bool
                Whether this is an international shipment.
            *package_args : tuple
                Arguments passed to create the Package.

        Raises
        ------
        ValueError
            If billing timing is not in_advance or on_delivery.

        Returns
        -------
        str
            The ID of the newly created order.
        """
        if not (BillingTiming.in_advance in order_args
                or BillingTiming.on_delivery in order_args):
            raise ValueError("Billing timing must be in_advance or on_delivery")
        
        return super().new_order(*order_args)
        
        
    #Override 
    def pay(self, bill_ID: str, transaction_ID: str, payment_method: PaymentMethod) -> None:
        """
        Process payment for a bill.
        
        Enforces that payment method must be card or cash
        (wire transfer is not allowed for Normal customers).

        Parameters
        ----------
        bill_ID : str
            The ID of the bill to pay.
        transaction_ID : str
            The transaction ID.
        payment_method : PaymentMethod
            The method of payment (must be card or cash).

        Raises
        ------
        ValueError
            If payment method is not card or cash.

        Returns
        -------
        None
        """
        if not (payment_method is PaymentMethod.card
                or payment_method is PaymentMethod.cash):
            raise ValueError(f"Payment method must be card or cash, not '{payment_method}'.")
        
        super().pay(bill_ID, transaction_ID, payment_method)
        
class Contracted(Customer):
    """
    Represents a business customer with a monthly billing account.
    
    Contracted customers always use monthly billing and wire transfer payments.
    They can also act as sponsors for Sponsored customers.

    Sponsorship Workflow
    --------------------
    1. A Sponsored customer creates an order (with in_advance timing)
    2. The Sponsored sends a sponsorship request notification to this Contracted
    3. Contracted reviews and either:
       - approve_sponsor(): Bills this account, notifies Sponsored of approval
       - reject_sponsor(): Bills the Sponsored's account, notifies of rejection

    Attributes
    ----------
    account : str
        The billing/wire transfer account identifier.

    Methods
    -------
    new_order(*order_args)
        Create a new order (enforces monthly billing, auto-generates bill).
    pay(bill_ID, transaction_ID)
        Process payment via wire transfer.
    approve_sponsor(order_obj)
        Approve a sponsored order and bill it to this account.
    reject_sponsor(order_obj)
        Reject a sponsored order; the Sponsored customer is billed instead.
    """
    def __init__(self, first_name: str, last_name: str, address: Destination,
                 phone_number: str, email: str, password: str, account: str):
        """
        Initialize a Contracted customer.

        Parameters
        ----------
        first_name : str
            The customer's first name.
        last_name : str
            The customer's last name.
        address : Destination
            The customer's address.
        phone_number : str
            The customer's phone number.
        email : str
            The customer's email.
        password : str
            The customer's password.
        account : str
            The billing/wire transfer account identifier.
        """
        super().__init__(first_name, last_name, address, phone_number, email, password, BillingTiming.monthly)
        self._account = account

    @property
    def account(self) -> str:
        return self._account
    
    @account.setter
    def account(self, new_account: str):
        self._account = new_account  # No format check currently
        self.save() 
    
    #Override 
    def new_order(self, *order_args) -> str:
        """
        Create a new order for Contracted customer.
        
        Enforces that billing timing must be monthly
        (in_advance or on_delivery is not allowed for Contracted customers).

        Parameters
        ----------
        *order_args
            Arguments passed to the Order constructor:
            
            bill_timing : BillingTiming
                When the bill should be issued (must be monthly).
            service : Service
                The delivery service type.
            origin : Location
                The origin location of the package.
            destination : Location
                The destination location of the package.
            collector_ID : str
                The ID of the staff collecting the package.
            is_international : bool
                Whether this is an international shipment.
            *package_args : tuple
                Arguments passed to create the Package.

        Raises
        ------
        ValueError
            If billing timing is not monthly.

        Returns
        -------
        str
            The ID of the newly created order.
        """        
        if order_args[0] is not BillingTiming.monthly:
            raise ValueError("Billing timing must be monthly")
        
        order_ID = super().new_order(*order_args)
        
        order_obj = OrdersHandler().get(order_ID)
        self.bill(order_obj) 
        return order_ID    
        
    #Override 
    def pay(self, bill_ID: str, transaction_ID: str) -> None:
        """
        Process payment for a bill via wire transfer.
        
        Contracted customers always pay via wire transfer.

        Parameters
        ----------
        bill_ID : str
            The ID of the bill to pay.
        transaction_ID : str
            The transaction ID.

        Returns
        -------
        None
        """
        super().pay(bill_ID, transaction_ID, PaymentMethod.wire)
        
    def approve_sponsor(self, order_obj: Order) -> None:
        """
        Approve a sponsored customer's order and bill it to this account.
        
        The order fee is charged to this Contracted customer's monthly account.
        The Sponsored customer is notified of the approval.

        Parameters
        ----------
        order_obj : Order
            The order to be billed to this account.

        Returns
        -------
        None
        """
        self.bill(order_obj)
        sponsored = Customer.from_ID(order_obj.payer)
        sponsored.notify(f"{self.first_name} {self.last_name} approved sponsorship for {order_obj.ID}")

    def reject_sponsor(self, order_obj: Order) -> None:
        """
        Reject a sponsored customer's order request.
        
        The order is billed to the Sponsored customer's own account with
        in_advance timing (they have no choice of payment timing).
        The Sponsored customer is notified of the rejection.

        Parameters
        ----------
        order_obj : Order
            The order being rejected.

        Returns
        -------
        None
        """
        sponsored = Customer.from_ID(order_obj.payer)
        sponsored.bill(order_obj)
        sponsored.notify(f"{self.first_name} {self.last_name} rejected sponsorship for {order_obj.ID}")
        
        
class Sponsored(Customer):
    """
    Represents a customer whose orders can be sponsored by a Contracted customer.
    
    Sponsored customers create orders with in_advance billing timing and request
    their linked sponsor (a Contracted customer) to cover the cost. If the sponsor
    approves, the order is billed to the sponsor's account. If rejected, the
    Sponsored customer is billed directly with no choice of payment timing.

    Sponsorship Workflow
    --------------------
    1. Sponsored.new_order() creates order with in_advance timing
    2. request_sponsor() sends notification to the linked Contracted customer
    3. Contracted either approves (bills themselves) or rejects (bills Sponsored)
    4. Sponsored receives notification of the decision

    Attributes
    ----------
    sponsor : str
        The customer ID of the linked Contracted sponsor.

    Methods
    -------
    new_order(*order_args)
        Create a new order and request sponsorship.
    request_sponsor(order, sponsor_ID)
        Send sponsorship request notification to the sponsor.
    """
    def __init__(self, sponsor_ID: str, *args):
        """
        Initialize a Sponsored customer.

        Parameters
        ----------
        sponsor_ID : str
            The customer ID of the Contracted sponsor.
        *args
            Arguments passed to the Customer constructor.
        """
        super().__init__(*args)
        self._sponsor = sponsor_ID
    
    @property
    def sponsor(self) -> str:
        """The customer ID of the linked Contracted sponsor."""
        return self._sponsor
    
    @sponsor.setter
    def sponsor(self, sponsor_ID: str):
        """
        Update the linked sponsor.
        
        Validates that the provided ID belongs to a Contracted customer.

        Parameters
        ----------
        sponsor_ID : str
            The customer ID of the new Contracted sponsor.

        Raises
        ------
        ValueError
            If the provided ID does not belong to a Contracted customer.
        """
        sponsor = Customer.from_ID(sponsor_ID)
        if not isinstance(sponsor, Contracted):
            raise ValueError("Sponsor must be a Contracted customer")
        self._sponsor = sponsor_ID
        self.save()
      
        
    #Override
    def new_order(self, *order_args) -> str:
        """
        Create a new order and request sponsorship.
        
        The order is created with in_advance billing timing (enforced).
        A sponsorship request is sent to the linked Contracted customer.
        If approved, the sponsor pays. If rejected, this customer pays.

        Parameters
        ----------
        *order_args
            Arguments passed to the Order constructor.
            First argument must be BillingTiming.in_advance.

        Returns
        -------
        str
            The ID of the newly created order.

        Raises
        ------
        ValueError
            If billing timing is not in_advance.
        """
        if order_args[0] is not BillingTiming.in_advance:
            raise ValueError("Billing timing must be in_advance")
        
        order_ID = super().new_order(*order_args)
        
        order_obj = OrdersHandler().get(order_ID)
        self.request_sponsor(order_obj, self.sponsor)
        return order_ID
        
    
    def request_sponsor(self, order: Order, sponsor_ID: str) -> None:
        """
        Send a sponsorship request notification to the sponsor.

        Parameters
        ----------
        order : Order
            The order requesting sponsorship.
        sponsor_ID : str
            The customer ID of the Contracted sponsor.

        Returns
        -------
        None
        """
        Customer.from_ID(sponsor_ID).notify(f"You are requested to sponsor order {order.ID}")
