# Author: Anna Goldstein
# This script takes in a CSV file of grant numbers and returns a data structure with
# patenting metrics for the grant and basic info for each patent.

import pprint
import manual_search
from bs4 import BeautifulSoup


# Input a list of grant numbers and get out a list of dictionaries containing the
# patenting metrics
def process_grants(grant_list):
    grants = manual_search.run_search(grant_list)
    # data = [{"grant number": grants[i][0:2] + grants[i][3:],
    #          "number of patents": 0} for i in range(len(grants))]
    data = [{"grant number": grants[i], "number of patents": 0} for i in range(len(grants))]

    counter = 0
    for grant in grants:

        # Open file with search results for each grant
        grant_file = "grant search results - full html/" + grant + ".html"
        with open(grant_file) as f:
            soup = BeautifulSoup(f, "lxml")

            # Number of search results printed in bold
            # If no bold text, that means no patents citing that grant
            if soup.strong:
                num_patents = int(soup.find_all('strong')[2].contents[0])
                data[counter]["number of patents"] = num_patents

                # Results containing patent number and title are in the second table on the page
                results = soup.find_all('table')[1]
                grant_pats = []
                pat_nums = []
                pat_titles = []

                for i in range(num_patents):

                    # Create patent dictionary
                    grant_pats.append({})
                    grant_pats[i] = {"patent number": "",
                                     "patent title": "",
                                     "date": "",
                                     "number of claims": "",
                                     "cites": [],
                                     "cited by": []}

                    # Store patent number from even numbered <a> tags
                    a = results.find_all('a')[2*i]
                    pat_nums += a
                    pat_num = str(pat_nums[i])
                    grant_pats[i]["patent number"] = pat_num

                    # Store patent title from odd numbered <a> tags
                    a = results.find_all('a')[(2*i)+1]
                    pat_titles += a
                    pat_title = str(pat_titles[i]).replace("\n", "").replace("    ", "")
                    grant_pats[i]["patent title"] = pat_title

                    pat_num_clean = pat_num.replace(",", "")
                    manual_search.pn_search(pat_num_clean)

                    # Open file with patent data for each patent
                    pat_file = "patent pages - full html/" + pat_num_clean + ".html"
                    with open(pat_file) as c:
                        extra_soup = BeautifulSoup(c, "lxml")

                        # Add patent date to dictionary from fifth bold tag
                        date = extra_soup.find_all('b')[4].contents[0]
                        date = str(date).replace("\n", "").replace("     ", "")
                        grant_pats[i]["date"] = date

                        # Add number of claims to dictionary
                        description = extra_soup.find("center", string="Description")
                        final_claim = description.previous_sibling.previous_sibling.previous_sibling
                        num_claims = int(final_claim[1:4].replace(".", "").replace(" ", ""))
                        grant_pats[i]["number of claims"] = num_claims

                # For each grant, set the value of the "patent list" key
                # as a list of patent dictionaries
                data[counter]["patent list"] = grant_pats

                total_claims = sum(x["number of claims"] for x in data[counter]["patent list"])
                avg_claims = total_claims / float(num_patents)
                data[counter]["avg number of claims"] = avg_claims
        counter += 1
    return data


csv_file = "DOE grant short list.csv"

if __name__ == '__main__':
    pprint.pprint(process_grants(csv_file)[:10])
