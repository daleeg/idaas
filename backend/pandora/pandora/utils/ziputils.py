import zipfile


class ZipHelper(object):
    @staticmethod
    def extract(zip_file, extract_path):
        z = zipfile.ZipFile(zip_file, 'r')
        files = z.namelist()
        z.extractall(path=extract_path)
        z.close()
        return files
