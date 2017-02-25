import glob

def get_file_by_prefix(dataFolder, filePrefix):
    client_files = glob.glob(dataFolder + filePrefix + "*")

    if client_files:
        return client_files[0]
    else:
        return ""