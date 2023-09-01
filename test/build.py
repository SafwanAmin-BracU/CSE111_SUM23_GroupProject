import os
import zipfile

def zip_directory(source_dir, output_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, rel_path)


def main():
    source_dir = "./src"  # Change this to your source directory path
    release_dir = "./release"  # Change this to your releases directory path
    project_name = "8"  # Change this to your project name
    output_zip = os.path.join(release_dir, f"{project_name}.zip")

    # Create releases directory if it doesn't exist
    if not os.path.exists(release_dir):
        print("Releases directory not found, creating...")
        os.makedirs(release_dir)
        print("Created releases directory")
    # Delete zip file if it already exists
    if os.path.exists(output_zip):
        print("Previous release zip file found, deleting...")
        os.remove(output_zip)
        print("Deleted previous zip file")
    # Create zip file
    zip_directory(source_dir, output_zip)
    print("Created project zip file")

if __name__ == "__main__":
    main()
