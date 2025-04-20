from pathlib import Path
import string
import pyexiv2

class PhotoExif:
    """
    PhotoExif object contains the exif informations necessary for the present program and a compressed version of the original date

    Attributes
        dir: str
            directory containing the RAW files
        original_name: str
            original name (stem) from camera memory card
        original_suffix: str
            original ext (NEF for Nikon)
        date [%Y %m %d]: str
            original date (date of the shooting)
        compressed_date: tuple
            the first element of the tuple represents the decade (format: YYYX), the second one the date itself (format: YMDD, where Y is the last part of the year et M is the month as a letter between A for january and L for december)
            Note: the compressed date is for compatibility with old files (the time of the 8.3 filenames)
        oriention: str
            portrait (exif orientation == 8), landscape (otherwise)
        nikon_file_number: int
            Nikon file number
    """
    def __init__(self, file) -> None:
        """
        __init__ creates PhotoExif objects

        Args:
            file: str
                path to the RAW file
        """
        self._file = file
        self._date_suffix = ''
        path = Path(file)
        self.dir = str(path.cwd()) # maybe useless
        self.original_name = path.stem
        self.original_suffix = path.suffix
        meta_data = pyexiv2.ImageMetadata(file)
        meta_data.read()
        self.date = meta_data['Exif.Image.DateTimeOriginal'].value.strftime('%Y %m %d')
        orientation = meta_data['Exif.Image.Orientation'].value
        self.orientation = 'portrait' if orientation == 8 else 'landscape'
        if self.original_suffix == '.NEF':
            self.nikon_file_number = meta_data['Exif.NikonFi.FileNumber'].value
        else:
            self.nikon_file_number = -1
#--------------------------------------------------------------------------------
    @property
    def file(self):
        return self._file
    @property
    def full_path(self):
        return '/'.join([self.dir, self.file])
    @property
    def date_suffix(self):
        # print('Récupération du suffixe de la date')
        return str(self._date_suffix)
    @date_suffix.setter
    def date_suffix(self, suffix: str):
        # print('Attribution suffixe')
        self._date_suffix = suffix
    @property
    def compressed_date(self):
        """
        structure of the compressed date, a tuple which comprised:
            1. the decade
            2. the year/month/day part (DADD)
            3. an optional suffix
        :return: the tuple
        """
        index = int(self.date[5:7]) - 1
        tmp_date = self.date[3] + string.ascii_uppercase[index] + self.date[-2:]
        self._compressed_date = (str(self.date[0:3])+'0', str(tmp_date), self.date_suffix)
        return self._compressed_date
