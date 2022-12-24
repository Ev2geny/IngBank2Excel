import argparse
import os

import pandas as pd

import utils
import extractors
import exceptions

from extractors_generic import determine_extractor_auto



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


def IngBank2Excel(input_file_name: str,
                    output_file_name: str = None,
                    format = 'auto',
                    output_file_type='xlsx') -> str:
    """
    Function converts ING bank WEB statement to excel or CSV formats.
    If output_file_name is not provided, then it will be generated from input_file_name by removing of extention

    return: file name of the created file
    """

    # creating output file name for Excel/csv file, if not provided
    if not output_file_name:
        pre, ext = os.path.splitext(input_file_name)
        output_file_name = pre

    with open(input_file_name, encoding="utf8") as file:
        file_text = file.read()

    extractor_type = None

    if format == 'auto':
        extractor_type = determine_extractor_auto(file_text)
        print(r"File format is detected as " + extractor_type.__name__)

    else:
        for extractor in extractors.extractors_list:
            if extractor.__name__ == format:
                extractor_type = extractor
                break
        else:
            raise exceptions.UserInputError(f"Unknown format is provided: {format}")

        print(f"Converting file as format {format}")

    # in this case extractor_type is not a function, but a class
    # if you call it like this extractor_type() it returns an object with the type of extractor_type
    extractor = extractor_type(file_text)

    # extracting entries (operations) from big text to list of dictionaries
    individual_entries = extractor.get_entries()

    # converting list of dictionaries to pandas dataframe
    df = pd.DataFrame(individual_entries,
                      columns=extractor.get_columns_info().keys())

    # getting balance, written in the bank statement
    # extracted_balance = extractor.get_period_balance()

    # checking, if balance, extracted from text file is equal to the balance, found by summing column in Pandas dataframe

    error = ""

    # try:
    #     utils.check_transactions_balance(input_pd=df,
    #                                      balance=extracted_balance,
    #                                      column_name_for_balance_calculation=extractor.get_column_name_for_balance_calculation())

    # except exceptions.BalanceVerificationError as e:
    #     if perform_balance_check:
    #         raise
    #     else:
    #         print(bcolors.FAIL + str(e) + bcolors.ENDC)
    #         error = str(e)


    df = utils.rename_sort_df(df = df,
                              columns_info=extractor.get_columns_info())

    utils.write_df_to_file(df, output_file_name,
                            extractor_name = extractor_type.__name__,
                            errors=error,
                            output_file_format=output_file_type)


    return output_file_name

def main():

    parser = argparse.ArgumentParser(description='Converting ING bank extracts to Excel')
    parser.add_argument('input_file_name', type=str, help='Input file name for conversion')
    parser.add_argument('-o','--output', type=str, default=None, dest='output_Excel_file_name', help='Output file name (without extension), which will be created in excel or CSV format')
    parser.add_argument('-f', '--format', type=str,default='auto', dest='format', choices = extractors.get_list_extractors_in_text(),help = 'Format of input file. If not provided, determined automatically' )
    parser.add_argument('-t', '--type', type=str,default='xlsx', dest='output_file_type', choices = ["xlsx","csv"],help = 'Format of the output file to be created' )

    args = parser.parse_args()


    IngBank2Excel(input_file_name = args.input_file_name,
                      output_file_name = args.output_Excel_file_name,
                      format = args.format,
                      output_file_type=args.output_file_type)

if __name__ == '__main__':
    main()