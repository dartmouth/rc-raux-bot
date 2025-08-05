import csv, os
from langchain_core.documents import Document

def read_ticket_csv_from_folder(folder_path):
    """
    reads all csvs from a folder, (ID, Requestor, Responsible, Ticket Content) and returns a list of dicts and truncates the ticket content. 

    Returns:
        list[dict]: A list of dictionaries, each representing a row from a CSV file.
                    Returns an empty list if no CSV files are found or errors occur.
    """
    all_tickets_data = []
    csv_folder_full_path = os.path.join(folder_path, "csv")

    if not os.path.exists(csv_folder_full_path):
        print(f"Error: The folder '{csv_folder_full_path}' does not exist.")
        return []

    if not os.path.isdir(csv_folder_full_path):
        print(f"Error: '{csv_folder_full_path}' is not a directory.")
        return []

    for filename in os.listdir(csv_folder_full_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(csv_folder_full_path, filename)
            print(f"Processing file: {file_path}")
            try:
                with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)

                    for row in reader:
                        # Limit 'Ticket Content' to 4000 characters
                        if 'Ticket Content' in row and len(row['Ticket Content']) > 4000:
                            row['Ticket Content'] = row['Ticket Content'][:4000]
                            print(f"Note: In '{filename}', Ticket ID {row.get('ID', 'N/A')}'s content truncated to 4000 characters.")
                        all_tickets_data.append(row)
            except FileNotFoundError:
                print(f"Error: The file '{file_path}' was not found (should not happen here).")
            except Exception as e:
                print(f"An unexpected error occurred while reading '{file_path}': {e}")
    return all_tickets_data


def format_ticket_data_for_processing(raw_tickets_data):
    """    
    Returns:
        list[dict]: A list of dictionaries, each formatted as:
                    {
                        "page_content": "...",
                        "metadata": {
                            "ticket_id": "...",
                            "requestor": "...",
                            "responsible": "..."
                        }
                    }
    """
    formatted_data = []
    for ticket in raw_tickets_data:
        # will returrn empty string if a key is missing.
        formatted_entry = {
            "page_content": ticket.get('Ticket Content', ''),
            "metadata": {
                "ticket_id": ticket.get('ID', ''),
                "requestor": ticket.get('Requestor', ''),
                "responsible": ticket.get('Responsible', '')
            }
        }
        formatted_data.append(formatted_entry)
    return formatted_data

# def processing_function(page_content, metadata):
#     print(f"--- Processing Ticket ---")
#     print(f"  Ticket ID: {metadata.get('ticket_id')}")
#     print(f"  Requestor: {metadata.get('requestor')}")
#     print(f"  Responsible: {metadata.get('responsible')}")
#     print(f"  Content: {page_content}")
#     print(f"-------------------------")


def main():
    current_directory = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()

    print(f"Reading CSV files from folder: '{os.path.join(current_directory, 'csv')}'")
    raw_data = read_ticket_csv_from_folder(current_directory)

    processed_data = format_ticket_data_for_processing(raw_data)
    for item in processed_data:
        print(f"Formatted Item: {item}")


    print(f"\nFormatting data for processing:")
    processed_data = format_ticket_data_for_processing(raw_data)
    print(processed_data)
    # print("\nSending to Vector Store")
    # document = Document(processed_data)


if __name__ == "__main__":
    main()