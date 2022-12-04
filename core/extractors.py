"""
This module lists all extractor calsses available
It shall be edited with every new extractor class created
"""

extractors_list = []

from extractor_ING_CREDIT import ING_CREDIT
extractors_list.append(ING_CREDIT)



def get_list_extractors_in_text():
    return [extractor.__name__ for extractor in extractors_list]

