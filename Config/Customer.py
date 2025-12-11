from __future__ import annotations

from platformdirs import user_data_dir
from BillingPref import BillingPref
from os.path import isfile
import json

def get_dir() -> str:
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        
    return user_data_dir(config['app_name'], config['project_name']) + config['customer_suffix']

class Customer:
    __data_path = get_dir()
    def __init__(self, ID: int, first_name: str, last_name: str, address: str,
                 phone_number: str, password: str, billing_pref: BillingPref,
                 bill_cnt: int = 0):
        self.__ID = f"C{ID:05d}"
        self.__first_name = first_name
        self.__last_name = last_name
        
        # This line invokes the logic defined in @address.setter
        self.address = address
        
        # This line invokes the logic defined in @number.setter
        self.number = phone_number
        
        self.__password = password
        
        # This line invokes the logic defined in @billing_pref.setter
        self.__billing_pref = billing_pref
        self.__bill_cnt = bill_cnt;
        
    @property
    def first_name(self) -> str:
        return self.__first_name
    
    @property
    def last_name(self) -> str:
        return self.__last_name
    
    @property
    def address(self) -> str:
        return self.__address
    
    @address.setter
    def address(self, new_address):
        self.__address = new_address
        
    @property
    def ID(self) -> str:
        return self.__ID
    
    @property
    def number(self):
        return self.__number
    
    @number.setter
    def number(self, phone_number: str) -> None:
        for char in phone_number:
            if not (char.isdigit() or char == " "):
                raise ValueError(f"phone_number contains invalid character '{char}'.")
        self.__number = phone_number
    
    @property
    def billing_pref(self) -> BillingPref:
        return self.__billing_pref    
        
    def __str__(self) -> str:
        return (f"Name\t: {self.first_name} {self.last_name}\n"
                + f"ID\t\t: {self.ID}\n"
                + f"Address\t: {self.address}\n"
                + f"Phone Number\t: {self.number}\n"
                + f"Billing Preferrence\t: {self.billing_pref.name}")
    
    def verify(self, password: str) -> bool:
        pass
    
    def set_billing_pref(self, new_pref: BillingPref) -> None:
        if not isinstance(new_pref, BillingPref):
            raise ValueError("Invalid choice of billing preferrece!")
        self.__billing_pref = new_pref
        
    def my_orders(self) -> list:
        pass
    
    def get(self, order_id):
        pass
    
    def pay(bill):
        pass
    
    def new_order():
        pass
    
    def save(self) -> None:
        """
        Calling this method would save the Customer object's field as
        a json file in local directory.
        """        
        snapshot = {'ID': int(self.ID[1:]),
                    'first_name': self.first_name,
                    'last_name': self.last_name,
                    'address': self.address,
                     'phone_number': self.number,
                     'password': self.__password,
                     'billing_pref': self.billing_pref.value,
                     'bill_cnt': self.__bill_cnt}
        
        with open(self.__data_path + self.ID + ".json", 'w', encoding='utf-8') as file:
            json.dump(snapshot, file, indent=4)
            
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
        file_path = cls.__data_path + ID + ".json"
        if not isfile(file_path):
            raise ValueError("The Customer with the provided ID does not exist!")
            
        with open(file_path, 'r', encoding='utf-8') as file:
            snapshot: dict = json.load(file)
            
        instance = cls(snapshot['ID'],
                       snapshot['first_name'], 
                       snapshot['last_name'],
                       snapshot['address'], 
                       snapshot['phone_number'], 
                       snapshot['password'],
                       BillingPref(snapshot['billing_pref']),
                       snapshot['bill_cnt'])
        
        return instance
        
if __name__ == "__main__":
    print(Customer._Customer__data_path)
    c = Customer(5, "Samuel", "Lai", "address","12345", "0000", BillingPref.in_advance)
    c.save()
    a = Customer.from_ID('C00005')
    print(a)