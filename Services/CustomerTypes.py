# -*- coding: utf-8 -*-
"""
Created on Sat Dec 27 17:12:20 2025

@author: green
"""
from Location import Destination
from PaymentArrangement import BillingTiming, PaymentMethod
from Customer import Customer
from OrderHandler import OrdersHandler
'''
Normal (paying in cash or card)
Contracted (with monthly billing accounts)
Sponsored (shipping costs paid by the merchant or a third party)
'''

class Normal(Customer):
    def __init__(self, first_name: str, last_name: str, address:Destination,
                 phone_number: str, email: str,password: str, 
                 billing_pref: BillingTiming,card:str):
        super().__init__(first_name, last_name, address,phone_number,email,password,billing_pref)
        self._card=card
    '''
    Add card information 
    for in_advance.
    Readable and modifiable
    '''
    @property
    def card(self) ->str:
        return self._card
    
    @card.setter
    def card(self, new_card: str):
        '''No format check currently'''
        self._card = new_card
        self.save() 
    
    #Override
    def new_order(self, *order_args):
        args_list = list(order_args)
        '''
        The second default input value is billing_timing, 
        along with the preference settings.
        
        Force binding to the customer's current billing_pref 
        (in_advance or on_delivery).
        '''
        if len(args_list) >= 2:
            args_list[1] = self.billing_pref
        
        
        order_ID = OrdersHandler().add(*args_list)
        order_obj = OrdersHandler().get(order_ID)
        self.bill(order_obj) 
        
    #Override 
    def pay(self, bill_ID: str,transaction_ID: str):
        '''
        The payment method is determined by checking the billing_timeing type.
        '''
        if self.billing_pref == BillingTiming.in_advance:
            payment_method = PaymentMethod.card  
        else: 
            payment_method = PaymentMethod.cash
        '''
        The parent category pay is called, 
        which in turn triggers Bill.pay.
        '''
        super().pay(bill_ID, transaction_ID, payment_method)
        
class Contracted(Customer):
    def __init__(self,first_name: str, last_name: str, address:Destination,
                 phone_number: str, email: str,password: str,account:str):
        super().__init__(first_name, last_name, address,phone_number,email,password,BillingTiming.monthly)
        self._account=account
    '''
    Add account information 
    for monthly.
    Readable and modifiable
    '''
    @property
    def account(self) ->str:
        return self._account
    
    @account.setter
    def account(self, new_account: str):
        '''No format check currently'''
        self._account =new_account
        self.save() 
    
    #Override 
    def new_order(self, *order_args):
        
        args_list = list(order_args)
        
        if len(args_list) >= 2:
            args_list[1] = BillingTiming.monthly
        
        order_ID = OrdersHandler().add(*args_list)
        
        order_obj = OrdersHandler().get(order_ID)
        self.bill(order_obj)     
        
    #Override 
    def pay(self, bill_ID: str,transaction_ID: str):
        '''
        The parent category pay is called, 
        which in turn triggers Bill.pay.
        '''
        payment_method = PaymentMethod.wire        
        super().pay(bill_ID, transaction_ID, payment_method)  
        
    def receive_sponsored_bill(self, order_obj):
        """
        Receive orders from sponsored users 
        and credit them to this account's monthly statement.
        """
        self.bill(order_obj)
        
        
class Sponsored(Customer):
    def __init__(self, *args, sponsor: Contracted= None, **kwargs):
 
        super().__init__(*args, **kwargs)
        self._sponsor = sponsor
    
    @property
    def sponsor(self) ->Contracted:
        return self._sponsor
    
    @sponsor.setter
    def sponsor(self, new_sponsor: str):
        '''No format check currently'''
        self._sponsor =new_sponsor
      
        
    #Override
    def new_order(self, *order_args):
        
        if not self.sponsor:
            raise ValueError(f"Customer {self.ID} has no sponsor assigned. Cannot place order.")
        args_list = list(order_args)
        
        '''Set it to monthly 
        because it will be attached to the Contracted
        '''
        if len(args_list) >= 2:
            args_list[1] = BillingTiming.monthly
        
        order_ID = OrdersHandler().add(*args_list)
        order_obj = OrdersHandler().get(order_ID)
        
        self.sponsor.receive_sponsored_bill(order_obj)
        


