import tkinter as tk
import os
from tkinter import ttk, filedialog
from tkinter import *
from tkinter import messagebox
from datetime import date
from datetime import datetime
from rApi import rApi_request
from rApi import exhange_NBP
from Reader import xlsx_reader
from get_full_stock import Stock_import
##########################################
###     Needed Variables
file_path = ""
files = [("Arkusz kalkulacyjny","*.xlsx")]

exhange_rate = None
reader = xlsx_reader()
nbp = exhange_NBP()
importer = Stock_import()
rApi = rApi_request()
product_list = []
products = 0
ready_to_update = False
##########################################
###     Program Functions
##########################################
###     Choose file with prices and load it's path
def choose_file():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=files)
    file_name = file_path[file_path.rfind("/")+1:]
    file_path_label.config(text=file_name)
###     Load file and get products details from it
def read_from_file():
    global product_list
    if file_path != "":
        reader.set_ids(importer.get_all_dict())
        product_list = reader.read_from_file(file_path)
        fill_table()
    else: 
        messagebox.showerror("Błąd","Musisz wskazać plik z cennikiem!")
##########################################
###     Receive current Euro exhange rate from NBP Api
def get_exhange_rate():
    global exhange_rate 
    try:
        exhange_rate_string.set(str(nbp.get_exh_rate()))
    except: 
        messagebox.showwarning("Błąd!","Nie mogę poprawnie zaciągnąć aktualnego kursu ze strony NBP!")
###     Price calculation based on given exh ratio
def calculate_prices():
    global ready_to_update
    temp_nbp = nbp.get_exh_rate()
    try:
        exhange_rate = float(exhange_rate_field.get())
        if len(product_list) == 0:
            messagebox.showerror("Błąd","Nie wczytany cennik!")
        else:
            if abs(temp_nbp-exhange_rate) > 0.5:
                rate_decide = messagebox.showerror("Uwaga!",f"Wpisany przez Ciebie kurs Euro różni się od kursu NBP o ponad 50gr.\nKurs wpisany - {exhange_rate}\nKurs NBP - {temp_nbp}")
            else:
                for product in product_list:
                    product[3] = round_price(product[2],exhange_rate)
                ready_to_update = True
                fill_table()
    except:
        ready_to_update = False
        messagebox.showerror("Błąd","Błędny kurs Euro!")
###     Round change from € to PLN and round price
def round_price(price,rate):
    final_price = int(price*rate)
    round = final_price % 10
    final_price += 9-round
    return final_price
##########################################
###     Fill specific columns in table
def fill_table():
    global products
    table.delete(*table.get_children())
    i = 0
    for product in product_list:
        if product[2] == 0:
            table.insert(parent='',index=i,text='',values=(i+1,product[0],product[1],f"{product[2]}€",f"BŁĄD!","BŁĄD!"))
        else:
            table.insert(parent='',index=i,text='',values=(i+1,product[0],product[1],f"{product[2]}€",f"{product[3]} zł",product[4]))
        i+=1
    products = i
##########################################
###     Send new prices to shop api
def update_price():
    if ready_to_update == True:
        count = 0
        log_date = date.today()
        log_file_path = f"{log_date}-log.txt"
        if os.path.isfile(log_file_path):
            os.remove(log_file_path)
        log_file = open(log_file_path,"w",encoding="utf-8")
        decision = messagebox.askyesno("Czy na pewno?",f"Czy na pewno chcesz zatwierdzić zmiany cen?\nUpewnij sie ,że wprowadziłeś poprawny kurs i ceny zostały przeliczone prawidłowo.\nCała operacja może zająć trochę czasu, program nie będzie odpowiadał.\nPo wszystkim znajdziesz podsumowanie operacji w pliku tekstowym {log_date}-log.txt")  
        if decision:
            for product in product_list:
                time = datetime.now()
                time2 =time.strftime("%d/%m/%Y %H:%M:%S")
                count +=1
                process_label.configure(text=f"Przetworzono {count} z {products} produktów.")
                process_label.update()
                if product[4] != "-":
                    log_file.writelines(f"{time2}: Zmieniam produkt z ID - {product[4]}, PN - {product[0]} na cenę {product[3]}\n")
                    print(f"Zmieniam produkt z ID - {product[4]}, PN - {product[0]} na cenę {product[3]}")
                    log_file.writelines(rApi.set_data(product[4],product[3],product[0]))
            results = rApi.get_results()
            errors = rApi.get_errors()
            log_file.writelines(f"Zakończono pracę.\nIlość produktów o aktualnej cenie {results[1]}\nIlość produktów zmienionych poprawnie : {results[1]}\nIlość produktów ze zbyt dużą różnicą cenową : {results[2]}\nIlość produktów o niezgodnym PN : {results[3]}\n")
            log_file.close()
            write_errors(errors)
            rApi.clear_results()
            messagebox.showinfo("Koniec!","Operacja zakończona, wszelkie informacje o zmianach dokonanych oraz błędach znajdziesz w pliku z logiem.")
        else:
            messagebox.showwarning("Anulowano","Operacja została anulowana.")

    else:
        messagebox.showerror("Błąd","Co najmniej jeden etap został pominięty. Nie mogę zaktualizować cen!")
##      Write file with specific errors and product codes
def write_errors(errors):
    error_path = "error_details.txt"
    if os.path.isfile(error_path): os.remove(error_path)
    with open(error_path,"w",encoding="utf-8") as file:
        file.writelines("Poniższe produkty zwróciły błąd cenowy:\n")
        for x in errors[0]:
            file.writelines(f"{x}\n")
        file.writelines("Poniższe produkty zwróciły błędny PN :\n")
        for x in errors[1]:
            file.writelines(f"{x}\n")
###     Import product ID's from Shop Api
def import_ids():
    temp_end = end_entry.get()
    try:
        end = int(temp_end)
        choice = messagebox.askokcancel("Jesteś pewien?","Zaciąganie bazy ID może potrwać od kilku do kilkudziesięciu minut w zależności od ilości produktów.\nŚredni czas to ok 1 min/40-50 produktów.\nW tym czasie program nie będzie odpowiadał. Czy na pewno chcesz rozpocząć?")
        if choice:
            if end <= importer.get_highest_id():
                messagebox.showerror("Błąd","ID które podałeś jest niższe niż najwyższa wartość w bazie!")
            else:
                importer.import_ids(end=end)
                id_label.config(text=f"Aktualnie najwyższe ID w bazie to {importer.get_highest_id()}")
        else:
            messagebox.showwarning("Anulowano","Operacja została anulowana.")
    except:
        messagebox.showerror("Błąd","Brak wprowadzonego ID lub jest ono błędne!")
##########################################    
###     GUI         
###     First Frame - contains file path, current exchange rate and buttons for operating with program
root = tk.Tk()
root.title("Aktualizowanie cen z cenników")
root.resizable(False,False)
top_frame = ttk.LabelFrame(root,text="Wybór pliku")
top_frame.pack(fill=BOTH)
file_path_label = ttk.Label(top_frame,text="...",width=50)
file_path_label.grid(column=0,row=0)
file_button = ttk.Button(top_frame,text="Wybierz cennik",command=choose_file,width=20)
file_button.grid(column=1,row=0,sticky=E)
read_button = ttk.Button(top_frame,text="Wczytaj ceny",command=read_from_file,width=20)
read_button.grid(column=2,row=0,sticky=E)
exhange_rate_label = ttk.Label(top_frame,text="Aktualny kurs Euro : ")
exhange_rate_label.grid(column=0,row=1,sticky=E)
exhange_rate_string = tk.StringVar()
exhange_rate_field = ttk.Entry(top_frame,textvariable=exhange_rate_string)
exhange_rate_field.grid(column=1,row=1)
exhange_button = ttk.Button(top_frame,text="Pobierz kurs z NBP",command=get_exhange_rate,width=20)
exhange_button.grid(column=2,row=1)
calculate_button = ttk.Button(top_frame,text="Przelicz",command=calculate_prices,width=20)
calculate_button.grid(column=2,row=2)


###     Middle Frame - Contains table with details about part number, product name, RRP Price, Price after calculations
mid_frame = ttk.LabelFrame(root,text="Szczegóły produktów")
mid_frame.pack(fill=BOTH)
mid_1_frame = ttk.Frame(mid_frame)
mid_1_frame.pack(fill=BOTH)
table = ttk.Treeview(mid_1_frame)
scroll = ttk.Scrollbar(mid_1_frame,orient="vertical",command=table.yview)
table.configure(yscrollcommand=scroll.set)
mid_2_frame = ttk.Frame(mid_frame)
mid_2_frame.pack(fill=BOTH)
mid_3_frame = ttk.Frame(mid_frame)
mid_3_frame.pack(fill=BOTH)
process_label = ttk.Label(mid_2_frame,text="")
process_label.pack()
send_button = ttk.Button(mid_3_frame,text="Zatwierdź",command=update_price,width=20)
send_button.pack()

###     Bottom Frame - Contains ID's importer
bot_frame = ttk.LabelFrame(root,text="Importer kodów ID")
bot_frame.pack(fill=BOTH)
bot_frame1 = ttk.Frame(bot_frame)
bot_frame1.pack(fill=BOTH)
bot_frame2 = ttk.Frame(bot_frame)
bot_frame2.pack(fill=BOTH)
id_label = ttk.Label(bot_frame1)
id_label.config(text=f"Aktualnie najwyższe ID w bazie to {importer.get_highest_id()}")
id_label.pack(side=LEFT)
end_id = tk.StringVar()
end_entry = ttk.Entry(bot_frame1,textvariable=end_id)
end_entry.pack(side=RIGHT)
end_id_label = ttk.Label(bot_frame1)
end_id_label.config(text="Podaj najwyższe ID produktu w sklepie")
end_id_label.pack(side=RIGHT)
id_import_button = ttk.Button(bot_frame2,text="Importuj nowe kody",command=import_ids)
id_import_button.pack(side=BOTTOM)

###     Table Details
scroll.pack(side="right",fill=Y)
table['columns'] = ['LP','PN','Name','RRP','Price','ID']
table.column('#0',width=0,stretch=NO)
table.heading('#0',text='')
table.column('LP',width=40,stretch=NO)
table.heading('LP',text='LP')
table.column('PN',width=100,stretch=NO)
table.heading('PN',text='PN')
table.column('Name',width=255,stretch=NO)
table.heading('Name',text='Nazwa Produktu')
table.column('RRP',width=100,stretch=NO)
table.heading('RRP',text='RRP')
table.column('Price',width=100,stretch=NO)
table.heading('Price',text='Cena')
table.column('ID',width=100,stretch=NO)
table.heading('ID',text='ID')
table.pack(fill=BOTH)
###     RUN
root.mainloop()
