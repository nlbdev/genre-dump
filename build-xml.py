#!/usr/bin/env python3

import os
import sys
import csv
from lxml import etree as ET

if sys.version_info[0] != 3:
    print("# This script requires Python version 3.x")
    sys.exit(1)

def xml_escape(value):
    value = "" if value == None else str(value)
    value = value.replace("&", "&amp;").replace("<", "&lt;").replace(">","&gt;").replace("\"", "&quot;")
    return value

def main(argv):
    if len(argv) < 3:
        print("usage: ./run.py </path/to/genre.csv> <output_dir>")
        sys.exit(1)
    
    genre_csv = argv[1]
    out_dir = argv[2]
    filter_dir = argv[3]
    
    if not os.path.isfile(genre_csv):
        print("Not a file: " + str(genre_csv))
        sys.exit(1)
    
    if not os.path.isdir(out_dir):
        print("Not a directory: " + str(out_dir))
        sys.exit(1)
    
    filter_books = os.listdir(filter_dir)

    genres = {}
    
    genre_id = 1
    with open(genre_csv, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in csvreader:
            genre = row[0]
            identifier = row[1]
            title = row[2]
            available = row[3]
            
            if genre is None or genre == "":
                continue

            if identifier not in filter_books:
                continue
            
            if genre not in genres:
                genres[genre] = {
                    "id": str(genre_id),
                    "books": {}
                }
                genre_id += 1
            genres[genre]["books"][identifier] = {"title": title, "available": available}
    
    sorted_genres = sorted([genre for genre in genres], key=lambda genre: len(genres[genre]["books"]), reverse=True)
    
    genre_list_csv = os.path.join(out_dir, "genres.csv")
    with open(genre_list_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for genre in sorted_genres:
            csvwriter.writerow([genre, genres[genre]["id"] + ".xml", str(len(genres[genre]["books"]))])
    
    for genre in sorted_genres:
        genre_xml = os.path.join(out_dir, genres[genre]["id"] + ".xml")
        
        # <active_loans>...</active_loans>
        active_loans = ET.Element("active_loans")
        
        # <result><success>true</success><message/></result>
        result = ET.SubElement(active_loans, "result")
        success = ET.SubElement(result, "success")
        success.text = "true"
        message = ET.SubElement(result, "message")
        
        # <data><books>...</books></data>
        data = ET.SubElement(active_loans, "data")
        data.append(ET.Comment(" " + genre + " "))
        books = ET.SubElement(data, "books")
        
        for identifier in genres[genre]["books"]:
            # <book><id>...</id><title>...</title></book>
            book = ET.SubElement(books, "book")
            id_element = ET.SubElement(book, "id")
            id_element.text = identifier
            title = ET.SubElement(book, "title")
            title.text = genres[genre]["books"][identifier]["title"]
            book.append(ET.Comment(" " + genres[genre]["books"][identifier]["available"] + " "))

        tree = ET.ElementTree(active_loans)
        tree.write(genre_xml, xml_declaration=True, encoding='UTF-8', pretty_print=True)


if __name__ == "__main__":
    main(sys.argv)
