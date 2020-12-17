import os
import hashlib

class Duplicates:

    def __init__(self, dup, org, hash):
        self.duplicate = dup
        self.original = org
        self.hash = hash

def is_image(img):

    if ( img[-4:] == '.jpg' or 
            img[-5:] == '.jpeg' or 
            img[-4:] == '.3gp' or 
            img[-4:] == '.avi' or 
            img[-4:] == '.png' or 
            img[-4:] == '.mp4' or 
            img[-4:] == '.mov' ):
        return True
    else:
        return False

def get_md5(myfile):
   
    CHUNK_SIZE = 16 * 1024

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
orig_files = dict()
dup_files = []

file_names = os.listdir(base_path)
files = [os.path.join(base_path,i) for i in file_names]
files.sort(key=os.path.getctime, reverse = False)

for img in files:

    if (is_image(img) != True):
        continue

    #print(imgpath, end =" ")

    hash = get_md5(img)

    if hash not in orig_files:
        orig_files[hash] = img
    else:
        dup_files.append(Duplicates(img, orig_files[hash], hash))

    #print(get_md5(imgpath))

    #break

print('\nOriginal Files:')
for k,v in orig_files.items():
    print(v)

print('\nDuplicate Files:')
for dup in dup_files:
    print(dup.duplicate+" ==> "+dup.original)
