import os
import time
import shutil
import hashlib
from PIL import Image
from PIL.ExifTags import TAGS

VIDEO = ('.m1v', '.mpeg', '.mov', '.qt', '.mpa', '.mpg', '.mpe', '.avi', '.movie', '.mp4', '.3gp')
IMAGE = ('.ras', '.xwd', '.bmp', '.jpe', '.jpg', '.jpeg', '.xpm', '.ief', '.pbm', '.tif', '.gif', '.ppm', '.xbm', '.tiff', '.rgb', '.pgm', '.png', '.pnm')

class ImageInfo:

    def __init__(self, orig):
        self.origf= orig

    def GetImageTags(self):

        try:
            # read the image data using PIL
            image = Image.open(self.origf)

            # extract EXIF data
            exifdata = image.getexif()

            """
            The problem with exifdata variable now is that the field names are just IDs, not a 
            human readable field name, thats why we gonna need the TAGS dictionary from PIL.ExifTags 
            module which maps each tag ID into a human readable text 
            """

            print('\n'+self.origf+'\n')

            # iterating over all EXIF data fields
            for tag_id in exifdata:
                # get the tag name, instead of human unreadable tag id
                tag = TAGS.get(tag_id, tag_id)
                data = exifdata.get(tag_id)
                # decode bytes 
                if isinstance(data, bytes):
                    data = data.decode(encoding='UTF-8',errors='strict')

                print(f"{tag_id}:{tag:25}: {data}")
        except:
            pass

        return

    def CreateNewName(self):
        token = ':'
        c = ''
        fstr = self.GetImageDate()
        fstr = fstr.replace(':', '')
        fstr = fstr.replace(' ', '_')
        fname = os.path.basename(self.origf)
        split = os.path.splitext(fname)
        if(fname.lower().endswith(IMAGE)):
            new = 'IMG_' + fstr + split[1]
        elif(fname.lower().endswith(VIDEO)):
            new = 'MOV_' + fstr + split[1]
        else:
            new = fname

        return new

    def GetFileDate(self):
        t = os.path.getmtime(self.origf)
        return time.strftime("%Y:%m:%d %H:%M:%S", time.localtime(t))

    def GetImageDate(self):
       
        try:
            # read the image data using PIL
            image = Image.open(self.origf)
            
            # extract EXIF data
            exifdata = image.getexif()
            cdate = exifdata.get(36867)
            if(str(cdate) == 'None'):
                cdate = self.GetFileDate()
        except:
            cdate = self.GetFileDate()

        return cdate

def replace_chars_in_str(old, new, mystr): 
  
    # iterating to check vowels in string 
    for ele in old: 
  
        # replacing vowel with the specified character 
        mystr = mystr.replace(ele, new) 
  
    return mystr 

def get_md5(myfile):
   
    CHUNK_SIZE = 64 * 1024

    with open(myfile, "rb") as f:
        file_hash = hashlib.md5()
        #file_hash = hashlib.sha1()
        #file_hash = hashlib.sha256()
        #file_hash = hashlib.sha512()
        chunk = f.read(CHUNK_SIZE)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(CHUNK_SIZE)
    
    return file_hash.hexdigest()

print ('Give directory location of image: ', end ="")
base_path = input()

if os.path.isdir(base_path) == False:
    print("Directory not valid")
    exit()

"""
print ('Give destination path for duplicates: ', end ="")
dest_path = input()

if os.path.isdir(dest_path) == False:
    print("Destination path not valid")
    exit()
"""

"""
file_names = os.listdir(base_path)
files = [os.path.join(base_path,i) for i in file_names]
files.sort(key=os.path.getctime, reverse = False)
"""

image_db = dict()

# Using os.walk() 
for dirpath, dirs, files in os.walk(base_path): 
  for filename in files: 
    print("Processing "+filename+20*' ', end="\r")
    if filename.lower().endswith(IMAGE) or filename.lower().endswith(VIDEO): 
        fname = os.path.join(dirpath,filename)
        hash = get_md5(fname)
        image_db.setdefault(hash,[]).append(fname)

#clear screen
print(30*' ')

file_list = []

for k,v in image_db.items():
    #print("%s repeates %d times" %(v[0], len(v)))
    #print(os.path.basename(v[0]), len(v))
    v.sort(key=os.path.getctime, reverse = False)
    im = ImageInfo(v[0])
    file_list.append(im)
    #print(im.origf+'  '+im.GetImageDate())
    print(im.origf+'  '+im.CreateNewName())
    #im.GetImageTags()

print("Original Files Count: %d" %(len(file_list)))

"""
print('\nDuplicate Files:')
for dup in dup_files:
    print(dup.duplicate+" ==> "+dup.original)
    #shutil.move(dup.duplicate, dest_path)
"""
