import csv

def read_dictionary(filename, key_column_index):

    dictionary = {}

    with open(filename, "rt") as csv_file:
        
        reader = csv.reader(csv_file)
        next(reader)

        for row_list in reader:
            if len(row_list) != 0:
                key = row_list[key_column_index]
                dictionary[key] = row_list
    return dictionary


def main():
    
    products_dict = read_dictionary("products.csv", 0)

    items = 0 

    subtotal = 0 

    with open("request.csv", "rt" ) as request:
        pass


