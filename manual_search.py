# Author: Anna Goldstein
# This is a script that takes a CSV list of grant numbers and searches
# the USPTO database for patents that cite each one. The search results
# page is saved as an HTML file.


import requests
import csv
import time
import os
import pprint


def govt_search(query):
    directory = "grant search results html"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = "grant search results html/" + query.replace("/", "") + ".html"
    if query[0:2] == "DE":
        number = query[5:] # e.g. 000032
        office_code = query[3:5] # e.g. AR
        query = "GOVT/" + office_code + number + ' OR GOVT/"' + \
                office_code + " " + number + '"'
        print query
    else:
        query = "GOVT/" + query

    if not os.path.exists(filename):
        data = {"Sect1": "PTO2",
                "Sect2": "HITOFF",
                "u": "/netahtml/PTO/search-adv.htm",
                "r": "0",
                "p": "1",
                "f": "S",
                "l": "50",
                "Query": query,
                "d": "PTXT"}
        r = requests.get("http://patft.uspto.gov/netacgi/nph-Parser", data)
        with open(filename, 'w') as f:
            f.write(r.text)
        print "Saved file: " + filename

        time.sleep(0.5)
    return filename


# Used when there is only one citing patent and the search page redirects
def govt_search_1(query):
    directory = "grant search results html"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = "grant search results html/" + query.replace("/", "") + "_1.html"
    if query[0:2] == "DE":
        number = query[5:] # e.g. 000032
        office_code = query[3:5] # e.g. AR
        query = "(" + office_code + number + '.GOTX. OR ("' + \
                office_code + " " + number + '".GOTX.))'
        print query
    else:
        query = "GOVT/" + query

    if not os.path.exists(filename):
        data = {"Sect1": "PTO2",
                "Sect2": "HITOFF",
                "u": "/netahtml/PTO/search-adv.htm",
                "r": "1",
                "p": "1",
                "f": "G",
                "l": "50",
                "S1": query,
                "d": "PTXT"}
        r = requests.get("http://patft.uspto.gov/netacgi/nph-Parser", data)
        with open(filename, 'w') as f:
            f.write(r.text)
        print "Saved file: " + filename

        time.sleep(0.5)
    return filename

def pn_search(query, type):
    # Type is "citing" or "DOE"-- determines which folder the patent is stored in
    if type == "DOE":
        filename = "patent pages html/" + query + ".html"
        directory = "patent pages html"
    else:
        filename = "citing patents html/" + query + ".html"
        directory = "citing patents html"

    if not os.path.exists(directory):
        os.makedirs(directory)

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
    return filename


def ref_search(query):
    directory = "reference search results html"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = "reference search results html/" + query + ".html"
    if not os.path.exists(filename):
        data = {"Sect1": "PTO2",
                "Sect2": "HITOFF",
                "u": "/netahtml/PTO/search-adv.htm",
                "r": "0",
                "p": "1",
                "f": "S",
                "l": "50",
                "Query": "REF/" + str(query),
                "d": "PTXT"}
        r = requests.get("http://patft.uspto.gov/netacgi/nph-Parser", data)
        with open(filename, 'w') as f:
            f.write(r.text)
        print "Saved file: " + filename

        time.sleep(0.5)
    return filename


# Used when there is only one citing patent and the search page redirects
def ref_search_1(query):
    directory = "reference search results html"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = "reference search results html/" + query + "_1.html"
    if not os.path.exists(filename):
        data = {"Sect1": "PTO2",
                "Sect2": "HITOFF",
                "u": "/netahtml/PTO/search-adv.htm",
                "r": "1",
                "p": "1",
                "f": "G",
                "l": "50",
                "d": "PALL",
                "S1": str(query) + ".UREF.",
                "OS": "REF/" + str(query),
                "RS": "REF/" + str(query)}
        r = requests.get("http://patft.uspto.gov/netacgi/nph-Parser", data)
        with open(filename, 'w') as f:
            f.write(r.text)
        print "Saved file: " + filename

        time.sleep(0.5)
    return filename


# Used when there is more than one page of citing patents
def ref_search_2(query):
    directory = "reference search results html"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = "reference search results html/" + query + "_2.html"
    if not os.path.exists(filename):
        data = {"Sect1": "PTO2",
                "Sect2": "HITOFF",
                "u": "/netahtml/PTO/search-adv.htm",
                "r": "0",
                "f": "S",
                "l": "50",
                "d": "PTXT",
                "OS": "REF/" + str(query),
                "RS": "REF/" + str(query),
                "Query": "REF/" + str(query),
                "TD": "1",
                "Srch1": str(query) + ".UREF.",
                "NextList2": "Final"}
        r = requests.get("http://patft.uspto.gov/netacgi/nph-Parser", data)
        with open(filename, 'w') as f:
            f.write(r.text)
        print "Saved file: " + filename

        time.sleep(0.5)
    return filename


def run_search(csv_file):
    with open(csv_file, "rb") as f:
        text = csv.reader(f)
        grants = [row[0] for row in text]
        files = []
        for x in grants:
            filename = govt_search(x)
            files.append(filename)
    return [grants, files]


csv_file = "DOE grant short list.csv"

if __name__ == '__main__':
    # pprint.pprint(run_search(csv_file))
    # patent cited 56 times
    # ref_search_2("7922809")
    # patent cited 1 time
    # ref_search("8047593")
    # patent cited 31 times
    # ref_search("8307899")
    govt_search_1("DE-SC0003254")




