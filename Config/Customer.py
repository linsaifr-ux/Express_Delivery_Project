from platformdirs import user_data_dir, user_config_dir
from BillingPref import BillingPref

class Customer:
    def __init__(self, ID: int, first_name: str, last_name: str, address: str,
                 phone_number: str, password: str, billing_pref: BillingPref):
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
    def billing_pref(self):
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
        
    


        
if __name__ == "__main__":
    c = Customer(5, "Samuel", "Lai", "address","12345", "0000", BillingPref.in_advance)
    print(c)