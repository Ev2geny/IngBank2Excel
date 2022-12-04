"""
Abstract Extractor class
All real extractors need to inherit from it and overwrite overwrite all @abstractmethod
"""

from abc import ABC, abstractmethod

import exceptions

class Extractor(ABC):
    def __init__(self, bank_text: str):
        self.bank_text = bank_text

    @abstractmethod
    def check_specific_signatures(self):
        pass


    @abstractmethod
    def get_entries(self)->list[dict]:
        pass

    @abstractmethod
    def get_columns_info(self)->dict:
        """
        Returns full column names in the order and in the form they shall appear in Excel
        The keys in dictionary shall correspond to keys of the result of the function self.decompose_entry_to_dict()
        """

    def get_processed_text(self)->str:
        """
        If your extractor changes original input file before processing, then overwrite this function
        and return post-processed text
        It will be used during debugging only
        """
        return ""

    def check_support(self)->bool:
        """
        Function checks whether this extractor support the  text format from self.bank_text 
        """
        try:
            self.check_specific_signatures()
            return True

        except exceptions.InputFileStructureError:
            return False