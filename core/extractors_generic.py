"""
Code, generic for extractors functionality
"""
import logging
import os
from pprint import pprint

from bs4 import BeautifulSoup

from extractors import extractors_list
import exceptions

from extractor import Extractor

def determine_extractor_auto(bank_text:str) -> type:
    """
    Function determines which extractor to use 

    returns:
        reference to a calss of a supported extractor
    """

    global extractors_list # type list[Extractor]

    supported_extractors = [extractor for extractor in extractors_list if extractor(bank_text).check_support()]

    if len(supported_extractors) == 0:
        raise exceptions.InputFileStructureError("Unknown format, none of the extractors works")

    if len(supported_extractors) > 1 :
        raise exceptions.InputFileStructureError(f"Unknown format, more than one extractor works")

    # If only one supported extractor if found - then all OK
    return supported_extractors[0]

def determine_extractor_by_name(extractor_name:str) -> type:
    """
    Checks if the is an Extractor class available, which has a name, equal to the 'extractor_name' string
    If such extractor is available, then this class is returned, otherwise an exception is raised
    """
    extractor_names_set = set()

    global extractors_list # type list[Extractor]

    for extractor_ in extractors_list:
        if extractor_.__name__ == extractor_name:
            return extractor_

        extractor_names_set.add(extractor_.__name__ )

    raise exceptions.UserInputError(f'Specifyed format ({extractor_name}) is unknown .\n The list of supported formats is \n {extractor_names_set}')

def debug_extractor(extractor_type_object:type, test_text_file_name:str):
    """
    This is helper function, which helps to debug a new extractor. It is not used in the operational code
    """

    class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    wrong_text = """
-------------------------------------------
Some wrong text, which cannot be correct
2nd line of the wrong text
-------------------------------------------
        """

    print("This is helper function, which helps to debug a new extractor")
    print("Test will be done for 2 situations")
    print(f"1) Extractor {extractor_type_object.__name__} initilyzed with the text from the file '{test_text_file_name}'\n\n")
    print(f"1) Extractor {extractor_type_object.__name__} initilyzed with the knownly wrong text {wrong_text}")

    all_actually_returned_fields_set=set()

    with open(test_text_file_name, encoding='utf-8') as f:
        txt_file_content = f.read()

    # Initializing an extractor with the type extractor_type_object and passing txt_file_content to it
    extractor_ = extractor_type_object(txt_file_content)


    extractor_which_shall_not_work = extractor_type_object(wrong_text)

    # Getting file name for intermediate file

    

    filename, file_extension = os.path.splitext(test_text_file_name)
    post_processed_text_file_name = filename + "_post_processed." + file_extension

    soup = BeautifulSoup(extractor_.get_processed_text(), "html.parser")

    with open(post_processed_text_file_name, "w", encoding='utf-8') as f:
        f.write(soup.prettify())
    
    print(f"File {post_processed_text_file_name} has been created")

    print('-'*20)
    print("Checking 'check_specific_signatures()'")
    print("Cheking on file, which shall work. If code continues, everything is OK")
    extractor_.check_specific_signatures()

    print("Cheking on file, which shall NOT work. If code continues, everything is OK")
    try:
        extractor_which_shall_not_work.check_specific_signatures()
        raise exceptions.TestingError ("function 'check_specific_signatures()' shall raise exception 'exceptions.InputFileStructureError'")
    except exceptions.InputFileStructureError:
        pass

    print('-' * 20)
    print("Testing 'get_entries()'")
    print("Testing on real file")
    
    entries = extractor_.get_entries()

    assert len(entries) >1

    for entry in extractor_.get_entries():
        print('*'*20)
        pprint(entry)
        assert isinstance(entry,dict)
        all_actually_returned_fields_set = all_actually_returned_fields_set | set(entry.keys())


    print("Cheking on file, which shall NOT work. If code continues, everything is OK")   
    try:
        extractor_which_shall_not_work.get_entries()
        raise exceptions.TestingError ("function 'get_entries()' shall raise exception 'exceptions.InputFileStructureError'")
    except exceptions.InputFileStructureError:
        pass


    print('-' * 20)
    print("Testing 'check_support()'")
    print("Cheking on file, which shall work")
    supported = extractor_.check_support()
    print(f"check_support = {supported}")
    if not supported:
        exceptions.TestingError("Function 'check_support()' shall return True for correct file")

    print("Cheking on file, which shall not work")
    wrong_file_supported = extractor_.check_support()
    print(f"check_support() = {wrong_file_supported}")
    if wrong_file_supported:
        exceptions.TestingError("Function 'check_support()' shall return False for wrong file")

    print('-' * 20)
    print(f"Testing get_columns_info()")
    columns_info_dic = extractor_.get_columns_info()
    pprint(columns_info_dic)



    undefined_fiels_set = all_actually_returned_fields_set - set(columns_info_dic.keys())

    print(f"{undefined_fiels_set=}")

    if len(undefined_fiels_set)>0:
        raise ValueError(f"""
Some of the fields, returned by the function 'get_entries()' are not retured by the function 'get_columns_info()'
Specifically the following fields are missing {undefined_fiels_set}""")



    print('\n'*2)
    print(bcolors.WARNING + "#"*10 + " Warnings! " + "#"*10 + bcolors.ENDC)

    defined_but_not_used_fiels_set = set(columns_info_dic.keys()) - all_actually_returned_fields_set

    # https://stackoverflow.com/a/287944/4432107
    if len(defined_but_not_used_fiels_set)>0:
        print(f"""
Some of the fields, returned by the function 'get_columns_info()'  are not retured by the function 'get_entries()''
Specifically the following fields are missing {defined_but_not_used_fiels_set}
This may be due to an input file, used for testing. Make sure you test this fucntion on another input file""")


    print("All tests have passed, if you have reached this point")

if __name__ == '__main__':
    """
    Some testing code
    """
    pass