# Author: Anna Goldstein
# This script takes in a CSV file of grant numbers and returns a data structure with
# patenting metrics for the grant and basic info for each patent.

import pprint
import manual_search
from bs4 import BeautifulSoup
from datetime import datetime


# Input a list of queries and get out a list of dictionaries containing the
# patent data
def process_queries(query_list, search_unit):
    [queries, files] = manual_search.run_search(query_list, search_unit)

    data = []

    for counter, query in enumerate(queries):

        print "processing " + query

        entry = {"Query": query,
                 "Number of Patents": 0,
                 "Avg. Number of Claims": "",
                 "__patent list": []}

        # Open file with search results for each grant
        filename = files[counter]
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

                    num_on_page = num_patents - (50 * (page - 1))

                    patent_list += interpret_search(soup, num_on_page, "primary")

        # If there is only one search result, there is a redirect page
        # Search needs to be repeated
        if soup.title.contents[0] == "Single Document":
            num_patents = 1
            entry["Number of Patents"] = num_patents

            print "query: " + query + ", search unit: " + search_unit
            search_file_1 = manual_search.single_result_search(query, search_unit)

            with open(search_file_1) as g:
                soup = BeautifulSoup(g, "lxml")

            title = soup.find("font", size="+1").string.replace("\n", "").replace("    ", "")
            number = soup.title.contents[0][22:]

            [assignee, date, num_claims, intl_classes, cpc_classes] = get_patent_details(soup)

            single_pat = {"Patent Title": title,
                          "Patent Number": number,
                          "Date": datetime.strptime(date, '%B %d, %Y'),
                          "Year": datetime.strptime(date, '%B %d, %Y').year,
                          "Number of Claims": num_claims,
                          "Intl Classes": intl_classes,
                          "CPC Classes": cpc_classes}

            # print "date " + single_pat["Date"]
            # print "year " + str(single_pat["Year"])

            patent_list.append(single_pat)

        # For each search, set the value of the "patent list" key
        # as a list of patent dictionaries
        entry["__patent list"] = patent_list

        if patent_list:

            for patent in patent_list:

                pat_num = patent["Patent Number"]

                patent["Citing Patents through Oct. 1, 2016"] = 0
                citing_patent_list = []

                print "search for patents citing " + pat_num
                # search for patents that cite the original patent
                ref_file = manual_search.ref_search(pat_num)

                with open(ref_file) as d:
                    ref_soup = BeautifulSoup(d, "lxml")

                # Are there multiple results for "referenced by"?
                if ref_soup.strong:

                    num_citing_patents = int(ref_soup.find_all('strong')[2].contents[0])

                    up_to_50 = min(50, num_citing_patents)

                    citing_patent_list = interpret_search(ref_soup, up_to_50, "citing")

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

                            citing_patent_list += interpret_search(ref_soup, num_on_page, "citing")

                # Is there only one search result, so the page redirects?
                if ref_soup.title.contents[0] == "Single Document":
                    ref_file_1 = manual_search.ref_search_1(pat_num)

                    with open(ref_file_1) as e:
                        ref_soup = BeautifulSoup(e, "lxml")

                    title = ref_soup.find("font", size="+1").string.replace("\n", "").replace("    ", "")
                    number = ref_soup.title.contents[0][22:]

                    [assignee, date, num_claims, intl_classes, cpc_classes] = get_patent_details(ref_soup)

                    citing_pat = {"Patent Title": title,
                                  "Patent Number": number,
                                  "Date": datetime.strptime(date, '%B %d, %Y'),
                                  "Year": datetime.strptime(date, '%B %d, %Y').year,
                                  "Number of Claims": num_claims,
                                  "Intl Classes": intl_classes,
                                  "CPC Classes": cpc_classes}

                    # print "date " + citing_pat["Date"]
                    # print "year " + str(citing_pat["Year"])

                    citing_patent_list.append(citing_pat)

                patent["__citing patent list"] = citing_patent_list

                citing_patents_in_search = [x for x in citing_patent_list if x["Date"] < datetime(2017, 4, 1)]

                patent["Citing Patents through April 1, 2017"] = len(citing_patents_in_search)

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

            # calculate average number of claims for patents in each grant
            total_claims = sum(x["Number of Claims"] for x in entry["__patent list"])
            avg_claims = total_claims / float(num_patents)
            entry["Avg. Number of Claims"] = avg_claims

        data.append(entry)

    return data


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

        [assignee, date, num_claims, intl_classes, cpc_classes] = get_patent_details(pat_soup)

        # Create patent dictionary
        patent = {"Patent Number": pat_num,
                  "Patent Title": pat_title,
                  "Assignee": assignee,
                  "Date": datetime.strptime(date, '%B %d, %Y'),
                  "Year": datetime.strptime(date, '%B %d, %Y').year,
                  "Number of Claims": num_claims,
                  "Intl Classes": intl_classes,
                  "CPC Classes": cpc_classes}

        # print "date " + patent["Date"]
        # print "year " + str(patent["Year"])

        patent_list.append(patent)

    return patent_list


def get_patent_details(soup):

    # Get patent assignee (if there is one)
    assignee_label = soup.find(string="Assignee:")
    try:
        assignee = assignee_label.parent.next_sibling.next_sibling.contents[1].contents[0]
    except:
        assignee = []

    # Get patent date from a header table
    table = soup.find_all('table')[2]
    row = list(table.children)[3]
    cell = list(row.children)[2]
    date = list(cell.children)[1].string
    date = str(date).replace("\n", "").replace("*", "").strip()

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

    # Get list of CPC classes
    intl_class_label = soup.find(string="Current International Class: ")
    intl_classes = intl_class_label.parent.parent.next_sibling.next_sibling.contents[0]
    cpc_class_label = soup.find(string="Current CPC Class: ")
    try:
        cpc_classes = cpc_class_label.parent.parent.next_sibling.next_sibling.contents[0]
    except:
        cpc_classes = []

    return [assignee, date, num_claims, intl_classes, cpc_classes]


csv_file = "test assignees.csv"

if __name__ == '__main__':
    process_queries(csv_file, "assignee")
