import json

# 1. OUR DATA (A list of dictionaries)
# Imagine this is your internal Python data
# books_list = [
#     {"title": "The Hobbit", "author": "J.R.R. Tolkien", "read": True, "rating": 5},
#     {"title": "1984", "author": "George Orwell", "read": False, "rating": None},
#     {
#         "title": "The Great Gatsby",
#         "author": "F. Scott Fitzgerald",
#         "read": True,
#         "rating": 4,
#     },
# ]


# books_dict = {
#     "title": "The Hobbit",
#     "author": "J.R.R. Tolkien",
#     "read": True,
#     "rating": 5,
# }

# books_standard_list = ["The Hobbit", "1984", "Sunset Song"]

# print("--- STEP 1: ORIGINAL PYTHON LIST ---")
# print(f"Type: {type(books_list)}")
# print(books_list)
# print("\n")


# print("Also the standard list")
# print(books_standard_list)
# print("/n")

# # 2. JSON DUMPS (Python -> String)
# # We use 'indent' to make it look pretty/readable
# json_string = json.dumps(books_list, indent=4)
# json_string_no_indentation = json.dumps(books_list)
# json_standard_string = json.dumps(books_standard_list)

# print("--- STEP 2: THE JSON STRING (Ready to send to a website) ---")
# print(f"Type: {type(json_string)}")
# print(json_string)
# # Notice how True became true and None became null!
# print("\n")
# print(json_string_no_indentation)
# # Notice how True became true and None became null!
# print("\n")
# print(json_standard_string)
# # Notice how True became true and None became null!
# print("\n")

# # 3. JSON LOADS (String -> Python)
# # Now we pretend we just received that string from the internet
# decoded_data = json.loads(json_string)

# print("--- STEP 3: BACK TO PYTHON LIST ---")
# print(f"Type: {type(decoded_data)}")
# # Now we can access it like a normal list again
# print(f"First book's title: {decoded_data[0]['title']}")


books_dict = {
    "title": "The Hobbit",
    "author": "J.R.R. Tolkien",
    "read": True,
    "rating": 5,
}


print(f"Type is {type(books_dict)}")
print(books_dict)
print("/n")

dict_json_string = json.dumps(books_dict)
print(f"new type is {type(dict_json_string)}")
print(dict_json_string)
print("/n")

print("back to python dict")
decoded_dataa = json.loads(dict_json_string)
print(decoded_dataa["title"])
