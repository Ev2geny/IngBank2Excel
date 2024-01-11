import re
from datetime import datetime
import sys
from decimal import Decimal

from typing import Iterator

import bs4
from bs4 import BeautifulSoup, Comment


import exceptions
from extractor import Extractor
import extractors_generic

from utils import get_text_from_tag, get_number_from_text

class ING_CREDIT(Extractor):

    def __init__(self, bank_text: str):
        super().__init__(bank_text)

        self.bank_text = self.bank_text.replace("=\n","")
        self.bank_text = self.bank_text.replace("=E2=88=92","-")

        # with open("intermittent.html","w") as f:
        #     f.write(self.bank_text)

    def check_specific_signatures(self):
        
        SIGNITURE_STRING = "ing-feat-agreement-details-credit-card"

        if SIGNITURE_STRING in self.bank_text:
            return True

        raise exceptions.InputFileStructureError(f"File does not contain signature string {SIGNITURE_STRING}")

    def get_processed_text(self):
        return self.bank_text

    def get_entries(self)->list[dict]:
        result = []
        soup = BeautifulSoup(self.bank_text, "html.parser")

        periods:Iterator[bs4.element.Tag] = soup.find_all( re.compile(r"ing-feat-transaction-period-\d*"))
        

        if len(periods) == 0:
            raise exceptions.InputFileStructureError("No accounting period is found")

        # period:bs4.element.Tag
        for period in periods:
            
            # print(period)

            period_name = get_text_from_tag(period.find('h2'))
            
            print(f"Period name: {period_name}")


            period_total_claculated = Decimal('0')
            
            period_totals_header=period.find(class_="statement-totals-description-list")
            
            if period_totals_header:
                print(period_totals_header)
            else:
                print("No totals header")

            # <li class=3D"date-item">
            date_items:Iterator[bs4.element.Tag] = period.find_all("li", class_='3D"date-item"')
                        
            # data_item: bs4.element.Tag
            for date_item in date_items:

                # Finding date
                #  <time datetime=3D"2022-08-27">
                date = date_item.find("time").get("datetime")
                # '3D"2022-07-20"' => '2022-07-20'
                date = re.search(r'"(.*)"', date).group(1)
                date = datetime.strptime(date, '%Y-%m-%d').date()

                transactions:Iterator[bs4.element.Tag] = date_item.find_all("div", class_= '3D"expandable-row"')

                for transaction in transactions:
                    # <h5 class=3D"expandable-title">
                    title = get_text_from_tag(transaction.find(class_='3D"expandable-title"'))

                    # <strong class=3D"expandable-value">
                    value_txt = get_text_from_tag(transaction.find(class_='3D"expandable-value"'))
                    value_dec = get_number_from_text(value_txt)
                    value_float = float(value_dec)
                    
                    period_total_claculated += value_dec

                    result.append({"period_name":period_name, 
                                    "date":date,
                                    "title":title,
                                    "value":value_float})

        if len(result) == 0:
            raise exceptions.InputFileStructureError("No single entry is found in any of the periods")

        return result

    def get_columns_info(self)->dict:
        return {'period_name':'period_name',
                'date':'date',
                'title':'title',
                'value':'value'}

                

if __name__ == '__main__':


    if len(sys.argv) < 2:
        print('Input file is not specifyed')
        print(__doc__)

    else:
        extractors_generic.debug_extractor(ING_CREDIT,
                                           test_text_file_name=sys.argv[1])