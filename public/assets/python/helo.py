file_content = "Hello, world! This is a string written to a file."

# Open a file in write mode ('w') and write the string
file_content = "Hello, world! This is a string written to a file."

try:
    with open("output_file.txt", "w", encoding="utf-8") as file:
        file.write(file_content)

except PermissionError:
    print("Permission denied. Try saving to Desktop or Documents.")

except FileNotFoundError:
    print("Invalid path. The directory does not exist.")

except OSError as e:
    print(f"Windows OS error: {e}")

else:
    print("File written successfully!")

print("String has been written to output_file.txt")
