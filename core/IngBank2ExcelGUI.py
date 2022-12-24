"""
GUI interface to IngBank2Excel
"""

# sources used:
# https://likegeeks.com/python-gui-examples-tkinter-tutorial/



from tkinter import *
import tkinter.filedialog
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import messagebox, ttk
import traceback
import sys
import logging

from IngBank2Excel import IngBank2Excel
import version_info


# defining global variable, which will hold files tuple
files = ()
leave_intermediate_txt_file = 0
no_balance_check = 0

def btn_selectFiles_clicked():
    global files

    files = tkinter.filedialog.askopenfilenames(parent=window,
                                                title='SElect file(s)',
                                                filetypes =(("Web archive file", "*.mhtml"),("All Files","*.*")) )

    SelectedFiles_ScrolledText.configure(state=NORMAL)
    # empty scrollText widget
    SelectedFiles_ScrolledText.delete('1.0', END)
    created_excel_files_scrollText.delete('1.0', END)

    # Populating SelectedFiles_ScrolledText widget
    for file in files:
        SelectedFiles_ScrolledText.insert(INSERT, file+'\n')

    SelectedFiles_ScrolledText.configure(state=DISABLED)
    

def btn_convertFiles_clicked():
    """
    main function, which performs functionality by calling calls ProjectExpenditure2Excel.ProjectExpenditure2Excel(file)
     and converts file to Excel
    """
    # empty scrollText widget
    print("Version "+version_info.VERSION)
    created_excel_files_scrollText.delete('1.0',END)

    qntFiles=len(files)
    qntFilesConverted=0
    for file in files:
        try:
            created_excel_files_scrollText.insert(INSERT,
                                                  IngBank2Excel(file ) + '\n')
            qntFilesConverted=qntFilesConverted + 1
        except:
            print('An error occured during conversion of the file "'+'file'+'" '+ str(sys.exc_info()[0]))
            print(traceback.format_exc())
            print('Skipping conversion of this file')

    
    if qntFiles==qntFilesConverted:
        print('All files have been successfully converted')
    else:
        print(f'!!!!!!! {qntFiles-qntFilesConverted} files of {qntFiles} have not been converted')

window = Tk()
menu = Menu(window)
help_about=Menu(menu)

def help_about_clicked():

    info_string = f'{version_info.NAME}\nVersion={version_info.VERSION}\nDeveloper={version_info.AUTHOR}\nWhere to download={version_info.PERMANENT_LOCATION}'
    print(info_string)
    messagebox.showinfo('', info_string)

help_about.add_command(label='About',command=help_about_clicked)

menu.add_cascade(label='Help', menu=help_about)
window.config(menu=menu)
 
window.title(f'{version_info.NAME} Version={version_info.VERSION}')
 
window.geometry('720x350')
 
Label(window, text="""
Step1: Select one or several files in format *.mhtml
""",justify=LEFT).grid(column=0, row=0,sticky="W")
 
Button(window, text="Select files", command=btn_selectFiles_clicked).grid(column=0, row=2)
 

Label(window, text='Selected files:').grid(column=0,row=3,sticky="W")
SelectedFiles_ScrolledText = scrolledtext.ScrolledText(window,width=80,height=4,state=DISABLED)
SelectedFiles_ScrolledText.grid(column=0,row=4)

Label(window, text="Step 2: Convert files to Excel").grid(column=0,row=5,sticky="W")

Button(window,text="Convert \n selected files", command=btn_convertFiles_clicked).grid(column=0,row=6)

Label(window, text='Created files in Excel format').grid(column=0,row=7,sticky="W")
created_excel_files_scrollText = scrolledtext.ScrolledText(window,width=80,height=4)
created_excel_files_scrollText.grid(column=0,row=8)

window.mainloop()

