import csv
from datetime import datetime


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
    

    items = 0 

    subtotal = 0 
    try:
        products_dict = read_dictionary("products.csv", 0)
        print("RECEIPT Maxikioscos Dulcemora")

        with open("request.csv", "rt" ) as request:

            reader = csv.reader(request)
            next(reader)

            for row_list in reader:
                if len(row_list) != 0:
                    product_id = row_list[0]
                    quantity = int(row_list[1])
                    items += quantity
                    subtotal += quantity * float(products_dict[product_id][2])
                    print(f"{products_dict[product_id][1]}: {quantity} @ ${float(products_dict[product_id][2]):.2f}")

        taxes = subtotal * 0.06

        print(f"Number of items: {items}")
        print(f"Subtotal: ${subtotal:.2f}")
        print(f"Sales Tax: ${taxes:.2f}")
        print(f"Total: ${subtotal + taxes:.2f}")
        print("Thank you for shopping at Maxikioscos Dulcemora!")
        now = datetime.now()
        print(now.strftime("%a %b %d %H:%M:%S %Y"))
    except KeyError as key_error:
        print(f"Error: Product ID {key_error} not found in products.csv")
    except FileNotFoundError as file_error:
        print(f"Error: {file_error.filename} missing file")
    except PermissionError as permission_error:
        print(f"Error: Permission denied for file {permission_error.filename}.")
    

if __name__ == "__main__":
    main()


