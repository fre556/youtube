import os

def check_missing_files(end_number):
    folder_path = os.getcwd()
    missing_files = []
    
    for i in range(1, end_number + 1):
        file_name = f"{i}.mp4"
        file_path = os.path.join(folder_path, file_name)
        
        if not os.path.isfile(file_path):
            missing_files.append(file_name)
    
    log_file_path = os.path.join(folder_path, "missing_files.log")
    with open(log_file_path, 'w') as log_file:
        for file in missing_files:
            log_file.write(f"{file}\n")
    
    print(f"Missing files log created at: {log_file_path}")

if __name__ == "__main__":
    end_number = int(input("Enter the end number: "))
    
    check_missing_files(end_number)
