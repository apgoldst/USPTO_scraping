# Author: Anna Goldstein

import html_parser
import pprint
import csv
import time
import datetime


# For award number search:
# Output from html_parser is a list of dictionaries, one per grant
# Each grant dictionary contains a key called "patent list", which is itself a list of dictionaries, one per patent


# Output table of all awards with patenting results
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


# Output table of all patents from award number search
def print_patent_table_from_grants(data, csv_file):

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

            print grant["Query"]
            # if grant['number of patents'] > 0:
            #
            for patent in grant["__patent list"]:
                patent["Award Number"] = grant["Query"]
                dictionary_tuples = sorted(patent.items(), key=lambda (k, v): k)[:-1]
                row = [field[1] for field in dictionary_tuples]
                writer.writerow(row)


# Output table of all patents from assignee search
def print_patent_table_from_assignees(data, csv_file):

    with open("USPTO_scraping - patent data - " + csv_file[:-4] + " - " +
              time.strftime("%d %b %Y") + ".csv", 'wb') as f:

        writer = csv.writer(f, delimiter=',')

        # Write heading for paper data from dictionary keys, excluding "__citing patent list"
        example_company = []
        for item in data:
            example_company = item["__patent list"]
            if example_company:
                break

        example_patent = example_company[0]
        example_patent["Search Name"] = ""
        heading_tuples = sorted(example_patent.items(), key=lambda (k, v): k)[:-1]
        fields = [field[0] for field in heading_tuples]
        writer.writerow(fields)

        for assignee in data:

            print assignee["Query"]

            for patent in assignee["__patent list"]:
                patent["Search Name"] = assignee["Query"]
                dictionary_tuples = sorted(patent.items(), key=lambda (k, v): k)[:-1]
                row = [field[1] for field in dictionary_tuples]
                writer.writerow(row)

# csv_file = "test assignees.csv"
csv_file = "companies founded 2005-2010.csv"

if __name__ == "__main__":
    start_time = datetime.datetime.now()
    print start_time
    data = html_parser.process_queries(csv_file, "assignee")
    # print_patent_table_from_grants(data, csv_file)
    # print_grant_table(data, csv_file)
    print_patent_table_from_assignees(data, csv_file)