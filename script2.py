from bs4 import BeautifulSoup as bs
import requests
import os
from pathlib import Path
from requests.structures import CaseInsensitiveDict
import time
import zipfile

stations = {
    "8" : "Gurguripal PS",
    "17": "Keshiary PS",
    "4": "Keshpur PS",
    "16": "Kharagpur(Local) PS",
    "15": "Kharagpur(Town) PS",
    "5": "Kotwali PS",
    "18": "Mohanpur PS",
    "19": "Narayangarh PS",
    "20": "Pingla PS",
    "21": "Sabang PS",
    "6": "Salboni PS"                
}

url = "https://paschimmedinipurpolice.co.in/online-fir"
session = requests.Session()
cookie_response = session.get(url)
cookies = session.cookies.get_dict()


for station in stations.keys():

    query_string = f"fir_ps_id={station}"
    resp = requests.post(url, query_string, cookies=cookies)
    
    if resp.status_code == 403:
        cookie_response = session.get(url)
        cookies = session.cookies.get_dict()
        resp = requests.post(url, query_string, cookies=cookies)

    page = bs(resp.content, features="html.parser")
    print("\033[37m\n\n"+stations[station] +" main page fetched\n")

    a = page.find_all("a")
    for link in a:

        if "fir-download/" in link.get("href"):
            pdf_url = "https://paschimmedinipurpolice.co.in/" + link.get("href")


            path = Path.cwd().joinpath("data", stations[station])
            zip_path = path.joinpath("zips")
            path.mkdir(parents=True, exist_ok=True)
            zip_path.mkdir(parents=True, exist_ok=True)

            try:
                filename =  zip_path.joinpath(pdf_url[pdf_url.rfind('/')+1:]+".zip")
            except:
                continue

            if os.path.exists(filename):
                print("\033[93m" + pdf_url + "\tfile already present")
                continue

            try:
                start = time.perf_counter()
                pdfx = requests.get(pdf_url, timeout=10)
                request_time = time.perf_counter() - start
            except:
                print("\033[91m" + pdf_url + "\tget request exception")
                continue

            filename.write_bytes(pdfx.content)
            print("\033[32m"+ pdf_url + "\tdownloaded\t" + str(request_time) +" secs")

            try:
                with zipfile.ZipFile(filename, "r") as file:
                    file.extractall(path)
            except:
                pass 



