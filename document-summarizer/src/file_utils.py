import os
import glob
import shutil

def get_txt_files(folder_path: str = "input") -> list[str]:
    """Return a list of full paths for all .txt files in the given folder."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return []
    
    pattern = os.path.join(folder_path, "*.txt")
    return glob.glob(pattern)

def read_text(file_path: str) -> str:
    """Read and return string content from a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def save_summary(original_name: str, content: str, output_dir: str = "output"):
    """
    Save the summary string to a .txt file in output_dir.
    The filename will be 'original_name_summary.txt'.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    base_name = os.path.splitext(os.path.basename(original_name))[0]
    output_filename = f"{base_name}_summary.txt"
    output_path = os.path.join(output_dir, output_filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    return output_path

def move_to_processed(file_path: str, processed_dir: str = "processed"):
    """
    Move the file at file_path to processed_dir to prevent reprocessing it later.
    """
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
        
    filename = os.path.basename(file_path)
    destination = os.path.join(processed_dir, filename)
    shutil.move(file_path, destination)
    return destination
