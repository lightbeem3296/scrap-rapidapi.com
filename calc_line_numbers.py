import os

def count_lines_in_jsonl_files(directory):
    total_lines = 0

    # Walk through directory and all subdirectories
    for root, dirs, files in os.walk(directory):
        # Iterate over files in the directory
        for file in files:
            # Only process .jsonl files
            if file.endswith(".jsonl"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # Count the number of lines in the file
                        total_lines += sum(1 for _ in f)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    return total_lines

# Example usage:
directory_path = "index_category_slug"  # Replace with your directory path
total_line_count = count_lines_in_jsonl_files(directory_path)
print(f"Total number of lines in all .jsonl files: {total_line_count}")
