# Author: Anna Goldstein
# This script takes in a CSV file of grant numbers and returns a data structure with
# patenting metrics for the grant and basic info for each patent.

import pprint
import manual_search
from bs4 import BeautifulSoup
from datetime import datetime
import re
import gc


# Input a query and get out a dictionary containing the
# patent data, including a list of dictionaries for each patent
def process_query(query, search_unit):

    [query, filename] = manual_search.run_search(query, search_unit)

    print "processing " + query

    entry = {"Query": query,
             "Number of Patents": 0,
             "Avg. Number of Claims": "",
             "__patent list": []}

    # Open file with search results for each grant
    with open(filename) as f:
        soup = BeautifulSoup(f, "lxml")

    patent_list = []

    # If bold text is present, there is more than one patent result in that search
    # Number of search results printed in bold
    if soup.strong:

        num_patents = int(soup.find_all('strong')[2].contents[0])

        entry["Number of Patents"] = num_patents

        up_to_50 = min(50, num_patents)

        patent_list = interpret_search(soup, up_to_50, "primary")

        # Is there a second page of results past the first 50?
        if num_patents > 50:

            # record number of pages (using negative values so that it rounds up to the next integer)
            max_page = -(-num_patents // 50)

            for page in range(2, max_page + 1):
                search_file_past_1 = manual_search.multiple_page_search(query, search_unit, page)

                with open(search_file_past_1) as h:
                    soup = BeautifulSoup(h, "lxml")

                if page == max_page:
                    num_on_page = num_patents % 50
                else:
                    num_on_page = 50

                patent_list += interpret_search(soup, num_on_page, "primary")

    # If there is only one search result, there is a redirect page
    # Search needs to be repeated
    if soup.title.contents[0] == "Single Document":
        num_patents = 1
        entry["Number of Patents"] = num_patents

        # Repeat search to save actual patent instead of redirect page
        print "query with single result: " + query + ", search unit: " + search_unit
        search_file_1 = manual_search.single_result_search(query, search_unit)

        with open(search_file_1) as g:
            soup = BeautifulSoup(g, "lxml")

        title = soup.find("font", size="+1").string.replace("\n", "").replace("    ", "")
        number = soup.title.contents[0][22:]

        # Search on the patent number to save a patent page with the expected formatting
        single_pat_file = manual_search.pn_search(str(number), "primary")

        with open(single_pat_file) as g:
            soup = BeautifulSoup(g, "lxml")

        # Create dictionary of patent attributes
        single_pat = get_patent_details(soup)

        # Add title and patent number to dictionary
        single_pat["Patent Number"] = number
        single_pat["Patent Title"] = title

        patent_list.append(single_pat)

    # For each search, set the value of the "patent list" key
    # as a list of patent dictionaries
    entry["__patent list"] = patent_list

    if patent_list:

        for patent in patent_list:

            pat_num = patent["Patent Number"]

            patent["Citing Patents through April 1, 2017"] = 0
            citing_patent_list = []

            print "search for patents citing " + pat_num
            # search for patents that cite the original patent
            ref_file = manual_search.ref_search(pat_num)

            with open(ref_file) as d:
                ref_soup = BeautifulSoup(d, "lxml")

            # Read search results page for citing patents
            # Number of search results printed in bold
            if ref_soup.strong:

                num_citing_patents = int(ref_soup.find_all('strong')[2].contents[0])

                up_to_50 = min(50, num_citing_patents)

                citing_patent_list = interpret_search(ref_soup, up_to_50, "citing")
                citing_patents_in_search_period = [x for x in citing_patent_list if x["Issued Date"] < datetime(2017, 4, 1)]
                patent["Citing Patents through April 1, 2017"] += len(citing_patents_in_search_period)

                # clearing memory after each page of citing patents
                citing_patent_list = []
                citing_patents_in_search_period = []
                gc.collect()

                # Is there a second page of results past the first 50?
                if num_citing_patents > 50:

                    # number of pages (using negative values so that it rounds up to the next integer)
                    max_page = -(-num_citing_patents // 50)

                    for page in range(2, max_page + 1):
                        ref_file_past_1 = manual_search.ref_search_next(pat_num, page)

                        with open(ref_file_past_1) as h:
                            ref_soup = BeautifulSoup(h, "lxml")

                        if page == max_page:
                            num_on_page = num_citing_patents - (50 * (page - 1))
                            print str(num_on_page) + " on page " + str(page)
                        else:
                            num_on_page = 50

                        citing_patent_list = interpret_search(ref_soup, num_on_page, "citing")
                        citing_patents_in_search_period = [x for x in citing_patent_list if x["Issued Date"] < datetime(2017, 4, 1)]
                        patent["Citing Patents through April 1, 2017"] += len(citing_patents_in_search_period)

                        # clearing memory after each page of citing patents
                        citing_patent_list = []
                        citing_patents_in_search_period = []
                        gc.collect()

            # Is there only one search result, so the page redirects?
            if ref_soup.title.contents[0] == "Single Document":
                ref_file_1 = manual_search.ref_search_1(pat_num)

                with open(ref_file_1) as e:
                    ref_soup = BeautifulSoup(e, "lxml")

                # citing_pat_num = ref_soup.find("font", size="+1").string.replace("\n", "").replace("    ", "")
                # citing_pat_title = ref_soup.title.contents[0][22:]

                # Create dictionary of patent attributes
                citing_pat = get_patent_details(ref_soup)

                # # Add title and patent number to dictionary
                # citing_pat["Patent Number"] = citing_pat_num
                # citing_pat["Patent Title"] = citing_pat_title

                if citing_pat["Issued Date"] < datetime(2017, 4, 1):
                    patent["Citing Patents through April 1, 2017"] = 1

            citing_patent_list = []
            gc.collect()

            # Commented out until I can resolve possible issues with finding the date value

            # if citing_patent_list:
            #
            #     # calculate annual citations for each patent
            #     for year in range(4):
            #
            #         date_format = "%B %d, %Y"
            #         key = "Citing patents in month %s to %s" % (str((year-1)*12), str(year*12))
            #
            #         patent[key] = 0
            #         citations = []
            #
            #         for item in patent["__citing patent list"]:
            #
            #             print "checking time difference for citing patent " + item["Patent Number"]
            #
            #             delta = datetime.strptime(item["Date"], date_format) - datetime.strptime(patent["Date"], date_format)
            #             item["Cite Time"] = delta.days / float(365)
            #             if year-1 < item["Cite Time"] <= year:
            #                 citations.append(item["Date"])
            #
            #         if citations:
            #             patent[key] = len(citations)

        # # calculate average number of claims for patents in each grant
        # total_claims = sum(x["Number of Claims"] for x in entry["__patent list"])
        # avg_claims = total_claims / float(num_patents)
        # entry["Avg. Number of Claims"] = avg_claims
    return entry


def interpret_search(soup, num_patents, type):

    # Output a list of patent dictionaries from a soup document of USPTO search results
    # Results containing patent number and title are in the second table on the page
    results = soup.find_all('table')[1]
    patent_list = []
    table = [str(a.contents[0]) for a in results.find_all('a')]

    for i in range(num_patents):

        # Store patent number from even numbered <a> tags
        pat_num = table[2*i]
        pat_num = pat_num.replace(",", "")

        # Store patent title from odd numbered <a> tags
        pat_title = table[(2*i)+1].replace("\n", "").replace("    ", "")

        # Search for the patent number
        pat_file = manual_search.pn_search(pat_num, type)

        print "opening " + str(pat_num) + ": " + type + " patent " + str(i+1) + " of " + str(num_patents)
        time = datetime.now()
        print time

        # Open file with patent data for each patent
        with open(pat_file) as c:
            pat_soup = BeautifulSoup(c, "lxml")

        # Create dictionary of patent attributes
        patent = get_patent_details(pat_soup)

        # Add title and patent number to dictionary
        patent["Patent Number"] = pat_num
        patent["Patent Title"] = pat_title

        patent_list.append(patent)

    return patent_list


def get_patent_details(soup):

    # Get first patent assignee
    assignee_label = soup.find(string="Assignee:")
    try:
        assignee = assignee_label.parent.next_sibling.next_sibling.contents[1].contents[0]
    except:
        assignee = []
    print "Assignee: " + str(assignee)

    # Get additional patent assignee (if there is one)
    try:
        assignee_2 = assignee_label.parent.parent.contents[3].find("br").next_element.next_element.contents[0]
    except:
        assignee_2 = []

    # Get patent application filing date
    filed_label = soup.find(string=re.compile("Filed:"))
    try:
        filed = filed_label.parent.next_sibling.contents[1].contents[0]
    except:
        filed = []
    print "Filed: " + str(filed)

    # Get patent issue date from a header table
    table = soup.find_all('table')[2]
    row = list(table.children)[3]
    cell = list(row.children)[2]
    date = list(cell.children)[1].string
    date = str(date).replace("\n", "").replace("*", "").strip()
    print date

    # Get number of claims
    description = soup.find("center", string="Description")
    step = 0
    num_claims = 0
    final_claim = description.previous_sibling
    while step < 3:
        final_claim = final_claim.previous_sibling
        try:
            list_num = final_claim[0:4].replace(".", "").replace(" ", "")
            num_claims = int(list_num)
        except ValueError:
            step += 1
        except TypeError:
            step += 1
        else:
            step = 3
    if num_claims == 0:
        num_claims = 1
    # print str(num_claims) + " claims"

    # Get lists of patent classes
    intl_class_label = soup.find(string="Current International Class: ")
    try:
        intl_classes = intl_class_label.parent.parent.next_sibling.next_sibling.contents[0]
    except:
        intl_classes = []

    cpc_class_label = soup.find(string="Current CPC Class: ")
    try:
        cpc_classes = cpc_class_label.parent.parent.next_sibling.next_sibling.contents[0]
    except:
        cpc_classes = []

    pat = {"Assignee 1": assignee,
           "Assignee 2": assignee_2,
           "Issued Date": datetime.strptime(date, '%B %d, %Y'),
           "Issued Year": datetime.strptime(date, '%B %d, %Y').year,
           "Filed Date": datetime.strptime(filed, '%B %d, %Y'),
           "Filed Year": datetime.strptime(filed, '%B %d, %Y').year,
           "Number of Claims": num_claims,
           "Intl Classes": intl_classes,
           "CPC Classes": cpc_classes}

    return pat


csv_file = "test assignees.csv"

if __name__ == '__main__':
    entry = process_query("ASPEN AEROGELS", "assignee")
    print entry