# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Created on Wed Dec 12 15:21:22 2025

@author: Frank
"""
class Package:
    """
    Package class.
    Attributes: size, weight, value, content_description, is_dangerous, is_fragile.
    """
    def __init__(self, size: tuple, weight: float, value: float, content_description: str,
                 is_dangerous: bool, is_fragile: bool):
        self.__size = size
        self.__weight = weight
        self.__value = value
        self.__content_description = content_description
        self.__is_dangerous = is_dangerous
        self.__is_fragile = is_fragile
        
    def add_description(self, description: str):
        self.__content_description += " " + description
    
    @property
    def size(self):
        return self.__size
        
    @property
    def weight(self):
        return self.__weight
        
    @property
    def value(self):
        return self.__value
        
    @property
    def content_description(self):
        return self.__content_description
        
    @property
    def is_dangerous(self):
        return self.__is_dangerous
        
    @property
    def is_fragile(self):
        return self.__is_fragile

    def __str__(self):
        return (f"Package Details:\n"
                f"  Size: {self.size}\n"
                f"  Weight: {self.weight} kg\n"
                f"  Value: ${self.value}\n"
                f"  Description: {self.content_description}\n"
                f"  Dangerous: {'Yes' if self.is_dangerous else 'No'}\n"
                f"  Fragile: {'Yes' if self.is_fragile else 'No'}")

    def snapshot(self) -> dict:
        """
        Create a dictionary containing states of the Package.
        """
        return {
            'size': self.size,
            'weight': self.weight,
            'value': self.value,
            'content_description': self.content_description,
            'is_dangerous': self.is_dangerous,
            'is_fragile': self.is_fragile
        }

    @classmethod
    def from_dict(cls, data: dict) -> Package:
        """
        Reconstruct the instance from a previous snapshot.
        """
        return cls(
            size=tuple(data['size']) if isinstance(data['size'], list) else data['size'],
            weight=data['weight'],
            value=data['value'],
            content_description=data['content_description'],
            is_dangerous=data['is_dangerous'],
            is_fragile=data['is_fragile']
        )

    def save(self, file_path: str) -> None:
        """
        Save the Package object to a file using pickle.
        """
        with open(file_path, 'wb') as file:
            pickle.dump(self, file)

    @classmethod
    def from_file(cls, file_path: str) -> Package:
        """
        Reconstruct the instance from a pickle file.
        """
        if not isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'rb') as file:
            instance = pickle.load(file)
            
        if not isinstance(instance, cls):
            raise TypeError("The loaded file is not a Package object.")

        return instance

if __name__ == "__main__":
    p = Package((10, 10, 10), 1.5, 100.0, "Books", False, False)
    print("Original Package:")
    print(p)
    p.add_description("Second Edition")
    
    # Test pickling
    test_file = "package_test.pkl"
    p.save(test_file)
    print(f"\nSaved to {test_file}")
    
    p2 = Package.from_file(test_file)
    print("\nLoaded Package from pickle:")
    print(p2)
    
    # Clean up
    import os
    if os.path.exists(test_file):
        os.remove(test_file)
        print("\nCleaned up test file.")
