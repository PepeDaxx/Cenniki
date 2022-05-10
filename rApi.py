import time
import requests as req
import json
from Authorization import Authorize

class rApi_request():
    def __init__(self):
        # Variables disabled to allow app to work without rest api
        # self.basic_auth = Authorize()
        # self.token = self.basic_auth.get_token()
        # self.token_auth = {"Authorization" : self.token}
        self.results = [0,0,0,0]
        self.errors = [[],[]]
    # Method requests amount of calls in rest api queue to prevent 'too many requests' error
    def check_if_free(self):
        response = req.request(method="GET",url=f"",headers=self.token_auth)
        count = int(response.headers["X-Shop-Api-Calls"])
        print(f"Api calls : {count}")
        if count < 5 : return False
        else:
            time.sleep(1)
            return True
    #Get part number of product with given ID - That method prevents changing wrong products if mistake happens in input file
    def get_partnumber(self,id):
        try:
            self.product_request = req.request(method="GET",url=f"https://<site>/webapi/rest/products/{id}/",headers=self.token_auth).json()
            return self.product_request["code"]
        except Exception as e:
            print(f"{e} // Connection Error: Nie mogę połączyć z serwerem!")
            return None
    # Method for changing data in shop api. ID - ID in shop api, Quantity - available quantity, Availability - delivery time
    #   Availability codes:
    # 1 - 24h
    # 2 - 48h
    # 9 - None
    def set_data(self,id,price,code):
        while True:
            if self.check_if_free() == False:
                break
        site_pn = self.get_partnumber(id)
        if site_pn == None:
            return (f" // {id} ze strony sklepu zwraca wartość None!\n")
        elif site_pn.strip() == code.strip():
            print(f"ID podane {id} / Kod żądany {code} / Kod zwrócony {site_pn.strip()}-OK",end=" ")
            current_price = self.get_price(id)
            if current_price > 1000:
                max_diff = current_price * 0.05
            else: 
                max_diff = 50
            diff = abs(current_price - price)
            if diff > max_diff:
                self.results[2] += 1
                self.errors[0].append(f"{code} - Obecna cena {current_price}, Cena błędna {price}")
                return (f"Zbyt duża rozbieżność! Maksymalna różnica cenowa - {max_diff}, Aktualna różnica cenowa - {diff}\n")
            if current_price != price:
                data = {"stock" : {"price" : price},}
                response2 = req.request(method="PUT",url=f"https://<site>/webapi/rest/products/{id}/",headers=self.token_auth,data=json.dumps(data))
                self.results[1] += 1
                return (f"Próba zmiany produktu {code} o ID: {id},cena - {price} // {response2.status_code} : Produkt zmieniony!\n")
            else:
                self.results[0] += 1
                return f"Produkt {code} o ID: {id} posiada aktualną cenę - {price}\n"
        else:
            print(f" // ID podane {id} / Kod żądany {code} / Kod zwrócony {site_pn.strip()}- Błąd")
            self.results[3] += 1
            self.errors[1].append(f"{code} - PN na stronie {site_pn}")
            return (f"Podane ID - {id}, nie jest zgodny pod względem kodu produktu. Kod produktu pod podanym id : {site_pn}, Kod oczekiwany : {code}\n")
    
    def get_results(self):
        return self.results
    
    def get_errors(self):
        return self.errors
    
    def clear_results(self):
        self.results = [0,0,0]
        self.errors=[[],[]]
    #Get part number of given product (by ID)
    def get_partnumber(self,id):
        try:
            self.product_request = req.request(method="GET",url=f"https://<site>/webapi/rest/products/{id}/",headers=self.token_auth).json()
            return self.product_request["code"]
        except Exception as e:
            print(f"{e} // Connection Error: Nie mogę połączyć z serwerem sklepu!")
            return None
    #Get price of given product (by ID)
    def get_price(self,id):
        try:
            self.product_request = req.request(method="GET",url=f"https://<site>/webapi/rest/products/{id}/",headers=self.token_auth).json()
            return float(self.product_request["stock"]["price"])
        except Exception as e:
            print(f"{e} // Connection Error: Nie mogę połączyć z serwerem sklepu!")
            return None
    #Get producer of given product (by ID)
    def get_producer(self,id):
        try:
            self.product_request = req.request(method="GET",url=f"https://<site>/webapi/rest/products/{id}/",headers=self.token_auth).json()
            return self.product_request["producer_id"]
        except Exception as e:
            print(f"Product Error // Brak produktu o ID : {id}!")
            return None
# Class to work with NBP api - For future extensions
class exhange_NBP():
    # Get current Euro exchange rate
    def get_exh_rate(self):
        response = req.request("GET","https://api.nbp.pl/api/exchangerates/rates/A/EUR?format=json").json()
        rate = float("%.2f" % response["rates"][0]["mid"])
        return rate