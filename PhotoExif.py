from pathlib import Path
import string
import pyexiv2
from PIL import Image
#
class PhotoExif:
    """
    PhotoExif object contains the exif information necessary for the present program and a compressed version of the original date

    Attributes
        dir: str
            directory containing the RAW files
        original_name: str
            original name (stem) from camera memory card
        original_ext: str
            original ext (NEF for Nikon)
        original_suffix: str
            idem original_ext (for backward compatibility)
        date [%Y %m %d]: str
            original date (date of the shooting)
        compressed_date: tuple
            the first element of the tuple represents the decade (format: YYYX), the second one the date itself (format: YMDD, where Y is the last part of the year et M is the month as a letter between A for january and L for december)
            Note: the compressed date is for compatibility with old files (the times of the 8.3 filenames)
        orientation: int  (TODO: 2 next lines are obsolete, to be rewritten)
            unknown if no orientation tag in the exif otherwise :
            portrait (exif orientation == 8), landscape (otherwise)
        height: int
            height of the image
        width: int
            width of the image
        nikon_file_number: int
            Nikon file number
        nikon_color_space: int
            Exif.Nikon3.ColorSpace
    """
    def __init__(self, file) -> None:
        """
        __init__ creates PhotoExif objects

        Args:
            file: str
                path to the RAW file
        """
        self._compressed_date = None
        self._file = file
        self._date_suffix = ''
        path = Path(file)
        self.dir = str(path.cwd()) # maybe useless
        self.original_name = path.stem
        self.original_suffix = path.suffix  # kept for backward compatibility
        self.original_ext = self.original_suffix

        img = Image.open(file)
        w, h = img.size
        self.width = w
        self.height = h

        meta_data = pyexiv2.ImageMetadata(file)
        meta_data.read()
        self.date = None
        for key in list(meta_data):
            if 'DateTimeOriginal' in key:
                self.date = meta_data[key].value.strftime('%Y %m %d')
                self.time = meta_data[key].value.strftime('%H %M %S')
                self.date_time = meta_data[key].value.strftime('%Y %m %d %H %M %S')
                self.raw_date_time = meta_data[key].value
        self.orientation = None
        if 'Exif.Image.Orientation' in list(meta_data):
            orientation = meta_data['Exif.Image.Orientation'].value # type int
            # self.orientation = 'portrait' if orientation == 8 else 'paysage'
            self.orientation = orientation
        if self.original_suffix == '.NEF':
            try:
                self.nikon_file_number = meta_data['Exif.NikonFi.FileNumber'].value # type int
            except:
                msg = f'Pas de clef \'Exif.NikonFi.FileNumber\' dans le fichier : {file}'
                # print(msg)  # TODO: to console
                self.nikon_file_number = -1
            try:
                self.nikon_color_space = meta_data['Exif.Nikon3.ColorSpace'].value  # type int 1: sRGB, 2: Adobe
            except:
                msg = f'Pas de clef \'Exif.Nikon3.ColorSpace\' dans le fichier : {file}'
                # print(msg)   # TODO: to console
                self.nikon_color_space = -1
        else:
            self.nikon_file_number = None
            self.nikon_color_space = None
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
            2. the year/month/day part ([0-9][A-L][0-3][0-9])
            3. an optional suffix
        :return: the tuple
        """
        index = int(self.date[5:7]) - 1
        tmp_date = self.date[3] + string.ascii_uppercase[index] + self.date[-2:]
        self._compressed_date = (str(self.date[0:3])+'0', str(tmp_date), self.date_suffix)
        return self._compressed_date
