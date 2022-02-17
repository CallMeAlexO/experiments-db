import zipfile
from typing import List
import pandas


def read_t(zipfile_ob, names: List[str], t: str):
    lower_t = t.lower()
    t_file = [x for x in names if lower_t+".xls" in x.lower()]
    if len(t_file) == 0: return None

    # T1/T2 was found, so let's read it
    return zipfile_ob.read(t_file[0])
    # try:
    #     # convert the excel sheet into a pandas object - dtype is string to not lose accuracy
    #     sheet = pandas.read_excel(xls_file, dtype=str, header=None)
    #     # convert pandas to list of lists
    #     return sheet.transpose().values.tolist()
    # except:
    #     return None


def read_2d(zipfile_ob, names: List[str]):
    d_file = [x for x in names if "2d.txt" in x.lower()]
    if len(d_file) == 0:
        for filename in names:
            if "2d" not in filename.lower(): continue
            with zipfile_ob.open(filename, "r") as f:
                # Some files don't end with 2d.txt, so this is another way to find files.
                first_bytes = f.read(6)
                if first_bytes == b'0 5000' or \
                        first_bytes == b'0 1000' or \
                        first_bytes == b'0 500 ' or \
                        first_bytes == b'0 3000':
                    d_file.append(filename)
                    break

    # 2D wasn't found
    if len(d_file) == 0: return None

    # 2D was found, so let's read it
    return zipfile_ob.read(d_file.pop())
    # try:
    #     # convert the txt sheet into a pandas object - dtype is string to not lose accuracy
    #     sheet = txt_file.decode("ascii").split("\n")
    #     sheet = pandas.DataFrame.from_records([x.strip().split(" ") for x in sheet])
    #     # convert pandas to list of lists
    #     return sheet.transpose().values.tolist()[1:]
    # except:
    #     return None
    # pass


def handle_zip(file):
    file_like_object = file.stream._file
    zipfile_ob = zipfile.ZipFile(file_like_object)
    file_names = zipfile_ob.namelist()
    folders = [x for x in file_names if x.endswith('/')]
    raw_data = {}
    if any(["T1" in x for x in folders]):
        raw_data.update({"T1_excel": read_t(zipfile_ob, file_names, "T1")})
    if any(["T2" in x for x in folders]):
        raw_data.update({"T2_excel": read_t(zipfile_ob, file_names, "T2")})
    if any(["2D" in x for x in folders]):
        raw_data.update({"2D_txt": read_2d(zipfile_ob, file_names)})
    return raw_data
