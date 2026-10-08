import  csv 

def read_dictionary(filename, key_column_index):
    
    dictionary = {}

    with open (filename, "rt") as csv_file:

        reader = csv.reader(csv_file)

        next(reader)

        for row_list in reader:

            key = row_list[key_column_index]

            dictionary[key] = row_list

    return dictionary 


def main():

    students_dict = read_dictionary("/home/estudiante/Documentos/CSE111/week5/students.csv", 0)

    id_number = input("Please, enter an student's ID number: (XX-XXX-XXXX)")

    id_number = id_number.replace("-", "")
    
    if id_number not in students_dict:
        print("No such student")
    else:
        value = students_dict[id_number]
        name = value[1]
        print(name)




if __name__ == "__main__":
    main()