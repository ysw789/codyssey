from file_manager import FileManager
from inventory_manager import InventoryManager

INVENTORY_LIST_FILE_NAME = 'Mars_Base_Inventory_List.csv'
FILTERED_CSV_FILE_NAME = 'Mars_Base_Inventory_danger.csv'
BINARY_OUTPUT_FILE_NAME = 'Mars_Base_Inventory_List.bin'

def print_list(headers, list):
    print(', '.join(headers))
    for row in list:
        print(', '.join(row))
    print()

if __name__ == "__main__":
    fm = FileManager(INVENTORY_LIST_FILE_NAME, BINARY_OUTPUT_FILE_NAME, FILTERED_CSV_FILE_NAME)
    headers, data_list = fm.parse_csv_to_list()

    print('>> Inventory List')
    print_list(headers, data_list)

    im = InventoryManager(headers, data_list)
    im.sort_by_flammability_desc()

    threshold = 0.7 # 인화성 임계값
    filtered_rows = im.filter_by_flammability(threshold)

    print('>> Flammability over', threshold)
    print_list(headers, filtered_rows)

    fm.write_into_csv_file(headers, filtered_rows)
    fm.write_into_binary_file(im.data_list)
    fm.read_and_print_binary_file(BINARY_OUTPUT_FILE_NAME)
