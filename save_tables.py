# Author: Anna Goldstein

import html_parser
import pprint
import csv
import time


# Output from html_parser is a list of dictionaries, one per grant
# Each grant dictionary contains a key called "patent list", which is itself a list of dictionaries, one per patent


def print_grant_table(data, csv_file):

    with open("USPTO_scraping - grant data - " + csv_file[:-4] + " - " +
              time.strftime("%d %b %Y") + ".csv", 'wb') as f:

        writer = csv.writer(f, delimiter=',')

        # Write heading for grant data from dictionary keys, excluding "__paper list"
        example_grant = data[0]
        heading_tuples = sorted(example_grant.items(), key=lambda (k, v): k)[:-1]
        fields = [field[0] for field in heading_tuples]
        writer.writerow(fields)

        # Fill in values for grant data
        for grant in data:

            dictionary_tuples = sorted(grant.items(), key=lambda (k, v): k)[:-1]
            row = [field[1] for field in dictionary_tuples]
            writer.writerow(row)


def print_patent_table(data, csv_file):

    with open("USPTO_scraping - patent data - " + csv_file[:-4] + " - " +
              time.strftime("%d %b %Y") + ".csv", 'wb') as f:

        writer = csv.writer(f, delimiter=',')

        # Write heading for paper data from dictionary keys, excluding "__citing patent list"
        example_grant = []
        for item in data:
            example_grant = item["__patent list"]
            if example_grant:
                break

        example_patent = example_grant[0]
        example_patent["Award Number"] = ""
        heading_tuples = sorted(example_patent.items(), key=lambda (k, v): k)[:-1]
        fields = [field[0] for field in heading_tuples]
        writer.writerow(fields)

        # writer.writerow(["Award Number", "Patent Number", "Patent Title", "Date Granted", "Number of Claims"])

        for grant in data:

            print grant['Award Number']
            # if grant['number of patents'] > 0:
            #
            for patent in grant["__patent list"]:
                patent["Award Number"] = grant["Award Number"]
                dictionary_tuples = sorted(patent.items(), key=lambda (k, v): k)[:-1]
                row = [field[1] for field in dictionary_tuples]
                writer.writerow(row)


csv_file = "DOE grants.csv"

if __name__ == "__main__":
    data = html_parser.process_grants(csv_file)
    print_patent_table(data, csv_file)
    print_grant_table(data, csv_file)
