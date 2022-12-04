"""
Module contain different utils, called from other modules
"""
import re
from typing import *

import pandas as pd
import bs4
from bs4 import Comment

import exceptions
import version_info

def get_text_from_tag(tag:bs4.element.Tag)->str:
    """
    Function extracts text from bs4 tag in the situation, where .string returns None, because there are comments
    More problem description is here https://stackoverflow.com/a/20754362/4432107
    """
    text = " ".join(tag.find_all(text=lambda t: not isinstance(t, Comment)))
    return text

def rename_sort_df(df:pd.DataFrame, columns_info:dict)->pd.DataFrame:

    # Reordering columns to follow the order of the keys in the columns_info
    df=df[list(columns_info.keys())]

    # renaming columns
    df = df.rename(columns = columns_info)
    return df


def write_df_to_file(df:pd.DataFrame, 
                        filename:str, 
                        extractor_name:str, 
                        errors:str="",
                        output_file_format:str="xlsx")->None:
    """
        output_file_format - supported values xlsx, csv
    """

    global version_info

    def print_message_about_file_creation(file_name:str)->None:
        print(f"File  '{file_name}' has been created")

    filename = filename + "." + output_file_format

    if output_file_format == "xlsx":
        writer = pd.ExcelWriter(filename, engine='xlsxwriter', datetime_format='dd.mm.yyyy HH:MM')

        df.to_excel(writer, sheet_name='data', index=False)

        workbook = writer.book
        info_worksheet = workbook.add_worksheet('Info')

        info_worksheet.write('A3', f'The file is created by the tool"{version_info.NAME}", which is available for download from here {version_info.PERMANENT_LOCATION}')
        info_worksheet.write('A4', f'Version: "{version_info.VERSION}"')
        info_worksheet.write('A5', f'For extracting of the information the following extractor was used: "{extractor_name}"')
        info_worksheet.write('A6', f'Errors during conversion: "{errors}"')

        writer.save()

        print_message_about_file_creation(filename)

    elif output_file_format == "csv":
        df.to_csv(filename,
                    sep=";",
                    index=False,
                    # date_format='dd.mm.yyyy HH:MM'
                    )

        print_message_about_file_creation(filename)
    else:
        raise exceptions.UserInputError(f"not supported output file format '{output_file_format}' is gven to the function 'write_df_to_file'")