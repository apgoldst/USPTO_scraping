# Author: Anna Goldstein

import html_parser
import pprint
import csv
import time


# Output from html_parser is a list of dictionaries, one per grant
# Each grant dictionary contains a key called "patent list", which is itself a list of dictionaries, one per patent


def print_grant_table(data):

    with open("USPTO_scraping - data on DOE grants - " + time.strftime("%d %b %Y") + ".csv", 'wb') as f:

        writer = csv.writer(f, delimiter=',')
        writer.writerow(["Award Number", "Number of Patents", "Average Number of Claims"])
        for row in range(len(data)):
            if 'avg number of claims' in data[row].keys():
                writer.writerow([data[row]['grant number'], data[row]['number of patents'], data[row]['avg number of claims']])
            else:
                writer.writerow([data[row]['grant number'], data[row]['number of patents']])


def print_patent_table(data):

    with open("USPTO_scraping - patents citing DOE grants.csv - " + time.strftime("%d %b %Y") + "", 'wb') as f:

        writer = csv.writer(f, delimiter=',')
        writer.writerow(["Award Number", "Patent Number", "Patent Title", "Date Granted", "Number of Claims"])
        for grant in range(len(data)):
            if data[grant]['number of patents'] > 0:
                for patent in range(len(data[grant]['patent list'])):
                    patent_entry = data[grant]['patent list'][patent]
                    writer.writerow([data[grant]['grant number'], patent_entry['patent number'],
                                     patent_entry['patent title'], patent_entry['date'], patent_entry['number of claims']])


csv_file = "DOE grant long list.csv"

if __name__ == "__main__":
    data = html_parser.process_grants(csv_file)
    print_patent_table(data)
    print_grant_table(data)