import re
from datetime import datetime
import sys

import bs4
from bs4 import BeautifulSoup, Comment


import exceptions
from extractor import Extractor
import extractors_generic

from utils import get_text_from_tag


def deconstruct_entry(entry:bs4.element.Tag)->dict:

    res = {}
    
    #  <time datetime=3D"2022-08-27">
    res['date']=entry.find("time").get("datetime")
    # '3D"2022-07-20"' => '2022-07-20'
    res['date'] = re.search(r'"(.*)"', res['date']).group(1)
    res['date'] = datetime.strptime(res['date'], '%Y-%m-%d').date()

    # <h5 class=3D"expandable-title">
    res['title']=get_text_from_tag(entry.find(class_='3D"expandable-title"'))

    # <strong class=3D"expandable-value">
    res['value']=get_text_from_tag(entry.find(class_='3D"expandable-value"'))
    res['value']=float(res['value'].replace(',',''))

    return res


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

        periods = soup.find_all( re.compile(r"ing-feat-transaction-period-\d*"))

        if len(periods) == 0:
            raise exceptions.InputFileStructureError("No accounting period is found")

        for period in periods:

            period_name = get_text_from_tag(period.find('h2'))

            # <li class=3D"date-item">
            date_items = period.find_all("li", class_='3D"date-item"')
            for date_item in date_items:

                # Finding date
                #  <time datetime=3D"2022-08-27">
                date = date_item.find("time").get("datetime")
                # '3D"2022-07-20"' => '2022-07-20'
                date = re.search(r'"(.*)"', date).group(1)
                date = datetime.strptime(date, '%Y-%m-%d').date()

                rows = date_item.find_all("div", class_= '3D"expandable-row"')

                for row in rows:
                    # <h5 class=3D"expandable-title">
                    title =get_text_from_tag(row.find(class_='3D"expandable-title"'))

                    # <strong class=3D"expandable-value">
                    value = get_text_from_tag(row.find(class_='3D"expandable-value"'))
                    value = float(value.replace(',',''))

                    result.append({"period_name":period_name, 
                                    "date":date,
                                    "title":title,
                                    "value":value})

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