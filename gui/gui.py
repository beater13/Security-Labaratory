import glob
import json
import subprocess
import tarfile
from tkinter import *
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter.font import Font
import requests
import view_audit_structure
import re

global antecedent
main = Tk()
myFont = Font(family="Times New Roman", size=15)
s = ttk.Style()
s.configure('TFrame', background='#00ffff')
main.title("SC Lab")
main.geometry("1920x1080")
frame = ttk.Frame(main, width=1920, height=1080, style='TFrame', padding=(40, 40, 500, 500))
frame.grid(column=0, row=0)
antecedent = []
index = 0
arr = []
matching = []
SystemDict = {}
querry = StringVar()
valori = StringVar()
tofile = []
structure = []

success = []
fail = []
unknown = []

toChange=[]
valori2=StringVar()
arr2=[]
arr2copy=[]

failedselected=[]

def make_request(struct):
    query = 'reg query ' + struct ['reg_key'] + ' /v ' + struct ['reg_item']
    out = subprocess.Popen(query,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    output = out.communicate() [0].decode('ascii', 'ignore')
    str = ''
    for char in output:
        if char.isprintable() and char != '\n' and char != '\r':
            str += char
    output = str
    output = output.split(' ')
    output = [x for x in output if len(x) > 0]
    value = ''
    if 'ERROR' in output [0]:
        unknown.append(struct ['reg_key'] + struct ['reg_item'])
    for i in range(len(output)):
        if 'REG_' in output [i]:
            for element in output [i + 1:]:
                value = value + element + ' '
            value = value [:len(value) - 1]
            if struct ['value_data'] [:2] == '0x':
                struct ['value_data'] = struct ['value_data'] [2:]
            struct ['value_data'] = hex(int(struct ['value_data']))
            p = re.compile('.*' + struct ['value_data'] + '.*')
            if p.match(value):
                print('Patern:', struct ['value_data'])
                print('Value:', value)
                success.append(struct ['reg_key'] + struct ['reg_item'] + '\n' + 'Value:' + value)
            else:
                print('Did not pass: ', struct ['value_data'])
                print('Value that didnt pass: ', value)
                fail.append([struct, value])

def verify():

    for struct in structure:
        if 'reg_key' in struct and 'reg_item' in struct and 'value_data' in struct:
            make_request(struct)

    for i in range(len(fail)):
        item=fail[i]
        arr2.append(' Item:' + item[0]['reg_item'] + ' Value:' + item[1] + ' Desired:' + item[0]['value_data'])
        global arr2copy
        arr2copy=arr2
    valori2.set(arr2)

    frame2 = Frame(main, bd=10, bg='#ffff00', highlightthickness=3)
    frame2.config(highlightbackground="black")
    frame2.place(relx=0.5, rely=0.1, width=1000, relwidth=0.4, relheight=0.8, anchor='n')

    text2 = Text(frame2, bg="#ff0000", width=230, height=50, highlightthickness=3)
    text2.place(relx=0.07, rely=0.03, relwidth=0.4, relheight=0.9)
    text2.insert(END, '\n\n'.join(success))



    shwbox_fail = Listbox(frame2, bg="#0000ff", font=myFont, fg="white", listvariable=valori2, selectmode=MULTIPLE,
                           width=230, height=50, highlightthickness=3)
    shwbox_fail.place(relx=0.5, rely=0.03, relwidth=0.4, relheight=0.9)
    shwbox_fail.config(highlightbackground="green")
    shwbox_fail.bind('<<ListboxSelect>>', on_select_failed)

    def exit():
        frame2.destroy()

    exit_btn = Button(frame2, text='Close', command=exit, bg="#03161d", fg="white", font=myFont, padx='10px',
                      pady='3px')
    exit_btn.place(relx=0.46, rely=0.95)

    def changeFailures():
        global arr2copy
        global arr2
        backup()
        for i in range(len(failedselected)):
            struct=failedselected[i][0]
            query = 'reg add "' + struct ['reg_key'] + '" /v ' + struct ['reg_item'] +' /d "'+ struct['value_data']+ '" /f'
            print(query)
            out = subprocess.Popen(query,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
            output = out.communicate() [0].decode('ascii', 'ignore')
            str = ''
            for char in output:
                if char.isprintable() and char != '\n' and char != '\r':
                    str += char
            output = str
            print(output)
            valori2.set(arr2)
            arr2copy=arr2

    def reestablish():
        f=open('backup.txt')
        fail=json.loads(f.read())
        print(fail)
        f.close()

        for i in range(len(fail)):
            struct=fail[i][0]
            query = 'reg add ' + struct ['reg_key'] + ' /v ' + struct ['reg_item'] +' /d '+ fail[i][1]+ ' /f'
            print('Query:',query)
            out = subprocess.Popen(query,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
            output = out.communicate() [0].decode('ascii', 'ignore')
            str = ''
            for char in output:
                if char.isprintable() and char != '\n' and char != '\r':
                    str += char
            output = str
            print(output)


    def backup():
        f=open('backup.txt','w')
        backupString=json.dumps(fail)
        f.write(backupString)
        f.close()
    changeBtn= Button(frame2, text='Change', command=changeFailures, bg="#03161d", fg="white", font=myFont, padx='10px',
                      pady='3px')
    changeBtn.place(relx=0.66, rely=0.95)

    backupBtn = Button(frame2, text='reestablish', command=reestablish, bg="#03161d", fg="white", font=myFont,
                       padx='10px',
                       pady='3px')
    backupBtn.place(relx=0.86, rely=0.95)

def on_select_failed(evt):
    w = evt.widget
    actual = w.curselection()


    global failedselected
    global arr2
    failedselected=[]
    for i in actual:
        failedselected.append(fail[i])
    localarr2=[]
    for i in actual:
        localarr2.append(arr2copy[i])
    arr2=localarr2
    arr2=[x for x in arr2copy if x not in arr2]
    print(failedselected)

def entersearch(evt):
    search()

def search():
    global structure
    q = querry.get()
    arr = [struct['description'] for struct in structure if q.lower() in struct['description'].lower()]
    global matching
    matching = [struct for struct in structure if q in struct['description']]
    valori.set(arr)


def on_select_configuration(evt):
    global antecedent
    global index
    w = evt.widget
    actual = w.curselection()

    difference = [item for item in actual if item not in antecedent]
    if len(difference) > 0:
        index = [item for item in actual if item not in antecedent][0]
    antecedent = w.curselection()

    text.delete(1.0, END)
    str = '\n'
    for key in matching[index]:
        str += key + ':' + matching[index][key] + '\n'
    text.insert(END, str)

def import_audit():
    global arr
    file_name = fd.askopenfilename(initialdir="../portal_audits")
    if file_name:
        arr = []
    global structure
    structure = view_audit_structure.main(file_name)
    for element in structure:
        for key in element:
            str = ''
            for char in element[key]:
                if char != '"' and char != "'":
                    str += char
            isspacefirst = True
            str2 = ''
            for char in str:
                if char == ' ' and isspacefirst:
                    continue
                else:
                    str2 += char
                    isspacefirst = False
            element[key] = str2

    global matching
    matching = structure
    if len(structure) == 0:
        f = open(file_name, 'r')
        structure = json.loads(f.read())
        f.close()
    for struct in structure:
        if 'description' in struct:
            arr.append(struct['description'])
        else:
            arr.append('Selecting Error')
    valori.set(arr)


shwbox = Listbox(frame, bg="#800000", font=myFont, fg="white", listvariable=valori, selectmode=MULTIPLE, width=175,
                 height=25, highlightthickness=3)
shwbox.config(highlightbackground="white")
shwbox.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
shwbox.bind('<<ListboxSelect>>', on_select_configuration)

def save_config():
    file_name = fd.asksaveasfilename(filetypes=(("Audit FILES", ".audit"),
                                                ("All files", ".")))
    file_name += '.audit'
    file = open(file_name, 'w')
    selection = shwbox.curselection()
    for i in selection:
        tofile.append(matching[i])
    json.dump(tofile, file)
    file.close()


def select_all():
    shwbox.select_set(0, END)
    for struct in structure:
        shwbox.insert(END, struct)


def deselect_all():
    for struct in structure:
        shwbox.selection_clear(0, END)


def download_url(url, save_path, chunk_size=1024):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)

def extract_download():
    url = "https://www.tenable.com/downloads/api/v1/public/pages/download-all-compliance-audit-files/downloads/7472/download?i_agree_to_tenable_license_agreement=true"
    path = "audits.tar.gz"
    download_url(url, path)
    tf = tarfile.open("audits.tar.gz")
    tf.extractall()
    print(glob.glob("portal_audits/*"))


text = Text(frame, bg="#800080", fg="white", font=myFont, width=175, height=15, highlightthickness=3)
text.config(highlightbackground="white")
text.grid(row=3, column=1, columnspan=1, padx=30)
import_button = Button(frame, bg="#bc4f07", fg="white", font=myFont, text="Import", width=7, height=1,
                       command=import_audit).place(relx=0.01, rely=0.999)
openButton = Button(frame, bg="#bc4f07", fg="white", font=myFont, text="Save", width=7, height=1,
                    command=save_config).place(relx=0.06, rely=0.999)
selectAllButton = Button(frame, bg="#bc4f07", fg="white", font=myFont, text="Select All", width=7, height=1,
                         command=select_all).place(relx=0.11, rely=0.999)
deselectAllButton = Button(frame, bg="#bc4f07", fg="white", font=myFont, text="Deselect All", width=10, height=1,
                           command=deselect_all).place(relx=0.16, rely=0.999)
downloadButton = Button(frame, bg="#bc4f07", fg="white", font=myFont, text="Download audits", width=15, height=1,
                        command=extract_download).place(relx=0.227, rely=0.999)
global e
e = Entry(frame, bg="#ffe4d1", font=myFont, width=30, textvariable=querry).place(relx=0.325, rely=0.999)
search_button = Button(frame, bg="#4996b3", fg="white", font=myFont, text="Search", width=7, height=1,
                       command=search).place(relx=0.49, rely=0.999)
verify_button = Button(frame, bg="#bc4f07", fg="white", font=myFont, text="verify", width=7, height=1,
                      command=verify).place(relx=0.54, rely=0.999)
main.bind('<Return>', entersearch)
main.mainloop()
