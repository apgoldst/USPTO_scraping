# Author: Anna Goldstein
# This is a script that takes a CSV list of grant numbers and searches
# the USPTO database for patents that cite each one. The search results
# page is saved as an HTML file.


import requests
import csv
import time
import os
import pprint

csv_file = "DOE grant short list.csv"


def govt_search(query):
    filename = "grant search results - full html/" + query + ".html"
    if not os.path.exists(filename):
        data = {"Sect1": "PTO2",
                "Sect2": "HITOFF",
                "u": "/netahtml/PTO/search-adv.htm",
                "r": "0",
                "p": "1",
                "f": "S",
                "l": "50",
                "Query": "GOVT/" + str(query),
                "d": "PTXT"}
        r = requests.get("http://patft.uspto.gov/netacgi/nph-Parser", data)
        with open(filename, 'w') as f:
            f.write(r.text)
        print "Saved" + filename
        time.sleep(0.5)


def pn_search(query):
    filename = "patent pages - full html/" + query + ".html"
    if not os.path.exists(filename):
        data = {"Sect1": "PTO2",
                "Sect2": "HITOFF",
                "u": "/netahtml/PTO/search-adv.htm",
                "r": "1",
                "p": "1",
                "f": "G",
                "l": "50",
                "d": "PTXT",
                "S1": str(query) + ".PN.",
                "OS": "PN/" + str(query),
                "RS": "PN/" + str(query)}
        r = requests.get("http://patft.uspto.gov/netacgi/nph-Parser", data)
        with open(filename, 'w') as f:
            f.write(r.text)
        print "Saved file: " + filename
        time.sleep(0.5)


def run_search(data_file):
    with open(data_file, "rb") as f:
        text = csv.reader(f)
        data = [row[0] for row in text]
        # data = map(lambda x: x[:2] + "-" + x[2:], data)
        for x in data:
            govt_search(x)
    return data


if __name__ == '__main__':
    pprint.pprint(run_search(csv_file)[:10])



