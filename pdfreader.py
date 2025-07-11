# import PyPDF2

# def read_pdf(file_path):
#     try:
#         with open(file_path, 'rb') as file:
#             reader = PyPDF2.PdfReader(file)
#             print(f"Number of pages: {len(reader.pages)}\n")
            
#             for page_num, page in enumerate(reader.pages, start=1):
#                 text = page.extract_text()
#                 print(f"--- Page {page_num} ---")
#                 print(text if text else "[No extractable text]")
#                 print()
#     except FileNotFoundError:
#         print("File not found. Please check the path.")
#     except Exception as e:
#         print(f"An error occurred: {e}")

# # Example usage
# if __name__ == "__main__":
#     path_to_pdf = "Jimny.pdf" 
#     read_pdf(path_to_pdf)

