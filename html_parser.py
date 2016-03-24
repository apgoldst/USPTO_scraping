# Author: Anna Goldstein
# This script takes in a CSV file of grant numbers and returns a data structure with
# patenting metrics for the grant and basic info for each patent.

import pprint
import manual_search
from bs4 import BeautifulSoup
from datetime import datetime


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

        print "interpreting search results for " + str(pat_num) + ": " + type + " patent"

        # Store patent title from odd numbered <a> tags
        pat_title = table[(2*i)+1].replace("\n", "").replace("    ", "")

        # Search for the patent number
        pat_file = manual_search.pn_search(pat_num, type)

        # Open file with patent data for each patent
        with open(pat_file) as c:
            pat_soup = BeautifulSoup(c, "lxml")

        [date, num_claims] = get_date_claims(pat_soup)

        # Create patent dictionary
        patent = {"Patent Number": pat_num,
                  "Patent Title": pat_title,
                  "Date": date,
                  "Year": datetime.strptime(date, '%B %d, %Y').year,
                  "Number of Claims": num_claims}

        # print "date " + patent["Date"]
        # print "year " + str(patent["Year"])

        patent_list.append(patent)

    return patent_list


def get_date_claims(soup):

    # Add patent date to dictionary from a header table
    table = soup.find_all('table')[2]
    row = list(table.children)[3]
    cell = list(row.children)[2]
    date = list(cell.children)[1].string
    date = str(date).replace("\n", "").replace("     ", "")

    # Add number of claims to dictionary
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

    return [date, num_claims]


# Input a list of grant numbers and get out a list of dictionaries containing the
# patenting metrics
def process_grants(grant_list):

    [grants, files] = manual_search.run_search(grant_list)

    data = []

    for counter, grant_num in enumerate(grants):

        print "processing grant " + grant_num

        grant = {"Award Number": grant_num,
                 "Number of Patents": 0,
                 "Avg. Number of Claims": "",
                 "__patent list": []}

        # Open file with search results for each grant
        filename = files[counter]
        with open(filename) as f:
            soup = BeautifulSoup(f, "lxml")

        patent_list = []

        # If bold text is present, there is more than one patent citing that grant
        # Number of search results printed in bold
        if soup.strong:

            num_patents = int(soup.find_all('strong')[2].contents[0])
            if num_patents > 50:
                raise Exception
            grant["Number of Patents"] = num_patents

            patent_list = interpret_search(soup, num_patents, "DOE")

        # If there is only one search result, there is a redirect page
        # Search needs to be repeated
        if soup.title.contents[0] == "Single Document":

            num_patents = 1
            grant["Number of Patents"] = num_patents

            search_file_1 = manual_search.govt_search_1(grant_num)

            with open(search_file_1) as g:
                soup = BeautifulSoup(g, "lxml")

            title = soup.find("font", size="+1").string.replace("\n", "").replace("    ", "")
            number = soup.title.contents[0][22:]

            [date, num_claims] = get_date_claims(soup)

            single_pat = {"Patent Title": title,
                          "Patent Number": number,
                          "Date": date,
                          "Year": datetime.strptime(date, '%B %d, %Y').year,
                          "Number of Claims": num_claims}

            # print "date " + single_pat["Date"]
            # print "year " + str(single_pat["Year"])

            patent_list.append(single_pat)

        # For each grant, set the value of the "patent list" key
        # as a list of patent dictionaries
        grant["__patent list"] = patent_list

        if patent_list:

            for patent in patent_list:

                pat_num = patent["Patent Number"]

                print "opening files for patent " + pat_num

                patent["Citing Patents through 12-31-2015"] = 0
                citing_patent_list = []

                # search for patents that reference this DOE patent
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

                        ref_file_2 = manual_search.ref_search_2(pat_num)

                        with open(ref_file_2) as h:
                            ref_soup = BeautifulSoup(h, "lxml")

                        past_50 = num_citing_patents - 50
                        citing_patent_list += interpret_search(ref_soup, past_50, "citing")

                # Is there only one search result, so the page redirects?
                if ref_soup.title.contents[0] == "Single Document":

                    ref_file_1 = manual_search.ref_search_1(pat_num)

                    with open(ref_file_1) as e:
                        ref_soup = BeautifulSoup(e, "lxml")

                    title = ref_soup.find("font", size="+1").string.replace("\n", "").replace("    ", "")
                    number = ref_soup.title.contents[0][22:]

                    [date, num_claims] = get_date_claims(ref_soup)

                    citing_pat = {"Patent Title": title,
                                  "Patent Number": number,
                                  "Date": date,
                                  "Year": datetime.strptime(date, '%B %d, %Y').year,
                                  "Number of Claims": num_claims}

                    # print "date " + citing_pat["Date"]
                    # print "year " + str(citing_pat["Year"])

                    citing_patent_list.append(citing_pat)

                patent["__citing patent list"] = citing_patent_list

                citing_patents_through_2015 = [x for x in citing_patent_list if x["Year"] < 2016]

                patent["Citing Patents through 12-31-2015"] = len(citing_patents_through_2015)

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
            total_claims = sum(x["Number of Claims"] for x in grant["__patent list"])
            avg_claims = total_claims / float(num_patents)
            grant["Avg. Number of Claims"] = avg_claims

        data.append(grant)

    return data


csv_file = "DOE grant short list.csv"

if __name__ == '__main__':
    process_grants(csv_file)
