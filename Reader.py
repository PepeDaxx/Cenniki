import openpyxl as opxl

class xlsx_reader:
    product_list = []
    product_ids = {}
    #Read from xlsx file and put data into list
    def read_from_file(self,path):
        self.product_list.clear()
        wb = opxl.load_workbook(filename = path)
        self.read_details(wb.active)
        return self.product_list
    # Receive ID's from reader and put it into dict
    def set_ids(self,ids_dict):
        self.product_ids = ids_dict
    # Read details from xlsx file
    def read_details(self,sheet):
        i = 1
        while True:
            if sheet[f"A{i}"].value == None:
                break
            elif len(sheet[f"A{i}"].value) == 12:
                pn = sheet[f"A{i}"].value
                name = sheet[f"B{i}"].value
                rrp = sheet[f"C{i}"].value
                if pn in self.product_ids:
                    id = f"{self.product_ids[pn]}"
                else:
                    id = "-"
                self.product_list.append([pn,name,rrp,0,id])
            else:
                #Not product - Skip
                pass
            i+=1


