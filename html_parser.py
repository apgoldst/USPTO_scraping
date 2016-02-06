# Author: Anna Goldstein
# This script takes in a CSV file of grant numbers and returns a data structure with
# patenting metrics for the grant and basic info for each patent.

import pprint
import manual_search
from bs4 import BeautifulSoup


def interpret_search(soup, num_patents, type):

    # Output a list of patent dictionaries from a soup document of USPTO search results
    # Results containing patent number and title are in the second table on the page
    results = soup.find_all('table')[1]
    patent_list = []
    table = [str(a.contents[0]) for a in results.find_all('a')]

    for i in range(num_patents):

        # Create patent dictionary
        patent = {"Patent Number": "",
                  "Patent Title": "",
                  "Date": ""}

        # Store patent number from even numbered <a> tags
        pat_num = table[2*i]
        pat_num = pat_num.replace(",", "")
        patent["Patent Number"] = pat_num
        print str(pat_num) + " " + type + " patent"

        # Store patent title from odd numbered <a> tags
        pat_title = table[(2*i)+1].replace("\n", "").replace("    ", "")
        patent["Patent Title"] = pat_title

        pat_file = manual_search.pn_search(pat_num, type)

        # Open file with patent data for each patent
        with open(pat_file) as c:
            pat_soup = BeautifulSoup(c, "lxml")

        [date, num_claims] = get_date_claims(pat_soup)

        patent["Date"] = date
        patent["Number of Claims"] = num_claims

        patent_list.append(patent)

    return patent_list


def get_date_claims(soup):

    # Add patent date to dictionary from fifth bold tag
    date = soup.find_all('b')[4].contents[0]
    date = str(date).replace("\n", "").replace("     ", "")

    # Add number of claims to dictionary
    description = soup.find("center", string="Description")
    final_claim = description.previous_sibling.previous_sibling.previous_sibling
    final_claim = final_claim[1:4].replace(".", "").replace(" ", "")

    if final_claim != "":
        num_claims = int(final_claim)
    else:
        num_claims = 1

    return [date, num_claims]


# Input a list of grant numbers and get out a list of dictionaries containing the
# patenting metrics
def process_grants(grant_list):

    [grants, files] = manual_search.run_search(grant_list)
    data = [{"Award Number": grants[y],
             "Number of Patents": 0,
             "Avg. Number of Claims": "",
             "__patent list": []} for y in range(len(grants))]

    for counter, grant in enumerate(grants):

        # Open file with search results for each grant
        filename = files[counter]
        with open(filename) as f:
            soup = BeautifulSoup(f, "lxml")

        patent_list = []

        # Number of search results printed in bold
        # If no bold text, that means no patents citing that grant
        if soup.strong:
            num_patents = int(soup.find_all('strong')[2].contents[0])
            if num_patents > 50:
                raise Exception
            data[counter]["Number of Patents"] = num_patents

            patent_list = interpret_search(soup, num_patents, "DOE")

            # For each grant, set the value of the "patent list" key
            # as a list of patent dictionaries
            data[counter]["__patent list"] = patent_list

            for patent in patent_list:
                pat_num = patent["Patent Number"]
                patent["Citing Patents"] = 0
                patent["__citing patent list"] = []
                ref_file = manual_search.ref_search(pat_num)

                with open(ref_file) as d:
                    ref_soup = BeautifulSoup(d, "lxml")

                # Are there any results for "referenced by"?
                if ref_soup.strong:

                    # Is there only one search result, so the page redirects?
                    if ref_soup.find('title').contents == "Single Document":
                        patent["Citing Patents"] = 1

                        ref_file_2 = manual_search.ref_search_1(pat_num)

                        with open(ref_file_2) as e:
                            ref_soup = BeautifulSoup(e, "lxml")

                        title = ref_soup.find("font", size="+1")
                        number = ref_soup.title.contents[0][22:]

                        [date, num_claims] = get_date_claims(ref_soup)

                        citing_pat = {"Patent Title": title,
                                      "Patent Number": number,
                                      "Date": date,
                                      "Number of Claims": num_claims}

                        patent["__citing patent list"].append(citing_pat)

                    else:
                        num_citing_patents = int(ref_soup.find_all('strong')[2].contents[0])
                        patent["Citing Patents"] = num_citing_patents

                        up_to_50 = min(50, num_citing_patents)

                        patent["__citing patent list"] = interpret_search(ref_soup, up_to_50, "citing")

                        if num_citing_patents > 50:
                            past_50 = num_citing_patents - 50
                            patent["__citing patent list"] += interpret_search(ref_soup, past_50, "citing")

            total_claims = sum(x["Number of Claims"] for x in data[counter]["__patent list"])
            avg_claims = total_claims / float(num_patents)
            data[counter]["Avg. Number of Claims"] = avg_claims

    return data


csv_file = "DOE grant short list.csv"

if __name__ == '__main__':
    process_grants(csv_file)
