# Author: Anna Goldstein

import html_parser
import pprint
import csv
import time
import datetime
import os
import gc


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
def print_patent_table_from_assignees(csv_file):

    output_file = "USPTO_scraping - patent data - " + csv_file[:-4] + " - " + time.strftime("%d %b %Y") + ".csv"

    # read input CSV file and make a list of rows
    # for individually searching and writing to output CSV

    with open(csv_file, "rb") as f:
        text = csv.reader(f)
        queries = [row[0] for row in text]

    # track whether the header has been created
    header_row = 0

    for query in queries:
        entry = html_parser.process_query(query, "assignee")

        # write header if it hasn't been written and there are patents to record
        if header_row == 0 and entry["__patent list"] != []:
            print "writing header row"
            header_row = 1

            with open(output_file, 'wb') as f:
                writer = csv.writer(f, delimiter=',')

                # Pull the patent list from the first successful search and use its dictionary keys
                # to write the column titles in the first row
                # put [:-1] at the end of the "sorted" function to exclude "__citing patent list"
                example_patent_list = entry["__patent list"]
                example_patent = example_patent_list[0]
                example_patent["Search Name"] = ""
                heading_tuples = sorted(example_patent.items(), key=lambda (k, v): k)
                first_row = [field[0] for field in heading_tuples]
                writer.writerow(first_row)

        # input row into file
        # put [:-1] at the end of the "sorted" function to exclude "__citing patent list"
        with open(output_file, 'ab') as f:
            writer = csv.writer(f, delimiter=',')

            print entry["Query"]

            for patent in entry["__patent list"]:
                patent["Search Name"] = entry["Query"]
                dictionary_tuples = sorted(patent.items(), key=lambda (k, v): k)
                row = [field[1] for field in dictionary_tuples]
                writer.writerow(row)

        entry = []
        gc.collect()

# csv_file = "test assignees.csv"
csv_file = "companies founded 2005-2010 - resume at Uber.csv"

if __name__ == "__main__":
    start_time = datetime.datetime.now()
    print start_time
    # print_patent_table_from_grants(data, csv_file)
    # print_grant_table(data, csv_file)
    print_patent_table_from_assignees(csv_file)
