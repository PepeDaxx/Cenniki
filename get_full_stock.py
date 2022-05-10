from rApi import rApi_request
import os
import json
class Stock_import():
    rApi = rApi_request()
    all_dict = {}
    all_file_path = "codes_all.json"
    #Get highest product ID from existing file
    def get_highest_id(self):
        if os.path.isfile(self.all_file_path):
            with open(self.all_file_path,"r") as file:
                self.all_dict = json.load(file)
        if self.all_dict:
            highest_id = max(self.all_dict.values())
        else : highest_id = 1
        return highest_id 
    #Return dictionary in format {product : id}
    def get_all_dict(self):
        return self.all_dict
    #Import new ID's from api starting with current highest ID, ending with user given ID
    def import_ids(self,end):
        id = self.get_highest_id()+1
        print(f"Zaciągam bazę produktów od id {id} do {end}")
        while id<=end:
            if self.rApi.check_if_free() == False:
                producer = self.rApi.get_producer(id)
                if producer != None:
                    code = self.rApi.get_partnumber(id)
                    code = code.replace(" ","")
                    print(f"{id} - Producer : {producer} - Code: {code}")
                    self.all_dict[code] = id
                id += 1
        with open(self.all_file_path,"w") as file:
            json.dump(self.all_dict,file,indent=2)
        