# Author: Anna Goldstein
# This script searches the USPTO database for
# patents that cite particular grant numbers or company names.
# The search results page is saved as an HTML file.


import requests
import csv
import time
import os
import pprint
import string


def run_search(query, search_unit):

    if search_unit == "grant":
        filename = govt_search(query)
    elif search_unit == "assignee":
        filename = assignee_search(query)

    return [query, filename]


def assignee_search(query):
    directory = "assignee search results"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = "assignee search results/" + query.replace(" ", "_").replace("/", "_") + ".html"
    print query

    if not os.path.exists(filename):
        data = {"Sect1": "PTO2",
                "Sect2": "HITOFF",
                "u": "/netahtml/PTO/search-adv.htm",
                "r": "0",
                "p": "1",
                "f": "S",
                "l": "50",
                "Query": 'AN/"' + query + '"',
                "d": "PTXT"}
        r = requests.get("http://patft.uspto.gov/netacgi/nph-Parser", data)
        with open(filename, 'w') as f:
            f.write(r.text)
        print "Saved file: " + filename

        time.sleep(0.5)
    return filename


# Used when there are multiple pages of results to be named _2, _3, etc.
def assignee_search_next(query, page):
    directory = "assignee search results"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = "assignee search results/" + query.replace(" ", "_").replace("/", "_") + "_" + str(page) + ".html"
    print query

    if not os.path.exists(filename):
        data = {"Sect1": "PTO2",
                "Sect2": "HITOFF",
                "u": "/netahtml/PTO/search-adv.htm",
                "r": "0",
                "p": page,
                "f": "S",
                "l": "50",
                "OS": 'AN/"' + query + '"',
                "RS": 'AN/"' + query + '"',
                "Page": "Next",
                "S1": '("' + query + '".ASNM.)',
                "d": "PTXT"}
        r = requests.get("http://patft.uspto.gov/netacgi/nph-Parser", data)
        with open(filename, 'w') as f:
            f.write(r.text)
        print "Saved file: " + filename

        time.sleep(0.5)
    return filename


# Used when there is only one patent and the search page redirects
def assignee_search_1(query):
    directory = "assignee search results"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = "assignee search results/" + query.replace(" ", "_").replace("/", "_") + "_1.html"
    query = '("' + query + '".ASNM.)'
    print query

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
        print r.url
        with open(filename, 'w') as f:
            f.write(r.text)
        print "Saved file: " + filename

        time.sleep(0.5)
    return filename


def govt_search(query):
    directory = "grant search results"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = "grant search results/" + query.replace("/", "") + ".html"
    if query[0:2] == "DE":
        number = query[5:]  # e.g. 000032
        office_code = query[3:5]  # e.g. AR
        query = "GOVT/" + office_code + number + \
                '$ OR GOVT/"' + office_code + " " + number + '"$' + \
                " OR GOVT/" + office_code + number + \
                ' OR GOVT/"' + office_code + " " + number + '"'
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


# Used when there are multiple pages of results to be named _2, _3, etc.
# THIS NEEDS TO BE CHECKED USING AN ACTUAL EXAMPLE OF A MULTIPAGE GRANT SEARCH RESULT
def govt_search_next(query, page):
    directory = "grant search results"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = "grant search results/" + query.replace("/", "") + "_" + str(page) + ".html"
    if query[0:2] == "DE":
        number = query[5:]  # e.g. 000032
        office_code = query[3:5]  # e.g. AR
        query = "GOVT/" + office_code + number + \
                '$ OR GOVT/"' + office_code + " " + number + '"$' + \
                " OR GOVT/" + office_code + number + \
                ' OR GOVT/"' + office_code + " " + number + '"'
        print query
    else:
        query = "GOVT/" + query

    if not os.path.exists(filename):
        data = {"Sect1": "PTO2",
                "Sect2": "HITOFF",
                "u": "/netahtml/PTO/search-adv.htm",
                "r": "0",
                "p": page,
                "f": "S",
                "l": "50",
                "OS": query,
                "RS": query,
                "Query": query,
                "Page": "Next",
                "S1": query + ".GOVT.",
                "d": "PTXT"}
        r = requests.get("http://patft.uspto.gov/netacgi/nph-Parser", data)
        with open(filename, 'w') as f:
            f.write(r.text)
        print "Saved file: " + filename

        time.sleep(0.5)
    return filename


# Used when there is only one patent and the search page redirects
def govt_search_1(query):
    directory = "grant search results"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = "grant search results/" + query.replace("/", "") + "_1.html"
    if query[0:2] == "DE":
        number = query[5:] # e.g. 000032
        office_code = query[3:5] # e.g. AR
        query = "(" + office_code + number + '$.GOTX. OR "' + \
                office_code + " " + number + '"$.GOTX. OR ' + \
                office_code + number + '.GOTX. OR "' + \
                office_code + " " + number + '".GOTX.)'
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


# Used when there are multiple pages of results to be named _2, _3, etc.
def ref_search_next(query, page):
    directory = "reference search results html"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = "reference search results html/" + query + "_" + str(page) + ".html"
    if not os.path.exists(filename):
        data = {"Sect1": "PTO2",
                "Sect2": "HITOFF",
                "u": "/netahtml/PTO/search-adv.htm",
                "r": "0",
                "p": page,
                "f": "S",
                "l": "50",
                "OS": "REF/" + str(query),
                "RS": "REF/" + str(query),
                "Page": "Next",
                "S1": str(query) + ".UREF.",
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


def pn_search(query, type):
    # Type is "citing" or "primary"-- determines which folder the patent gets saved in
    if type == "primary":
        filename = "patent pages html/" + query + ".html"
        directory = "patent pages html"
    else:
        filename = "citing patents html/" + query + ".html"
        directory = "citing patents html"

    if not os.path.exists(directory):
        os.makedirs(directory)

    # resolve error in special case of early patent missing a zero it its number
    if string.find(query, "PP") != -1 & len(query) == 6:
        query = string.replace(query, "PP", "PP0")

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


def single_result_search(query, search_unit):
    if search_unit == "grant":
        filename = govt_search_1(query)
    elif search_unit == "assignee":
        filename = assignee_search_1(query)

    return filename


def multiple_page_search(query, search_unit, page):
    if search_unit == "grant":
        filename = govt_search_next(query, page)
    elif search_unit == "assignee":
        filename = assignee_search_next(query, page)

    return filename


# csv_file = "DOE grant short list.csv"

if __name__ == '__main__':
    # pprint.pprint(run_search(csv_file))
    # patent cited 56 times
    # ref_search_2("7922809")
    # patent cited 1 time
    # ref_search("8047593")
    # patent cited 31 times
    # ref_search("8307899")
    # assignee_search("1366 TECHNOLOGIES")
    # run_search("test assignees.csv", "assignee")
    single_result_search("ABEAM TECHNOLOGIES", "assignee")




