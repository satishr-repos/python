import os
from PIL import Image
from PIL.ExifTags import TAGS

def is_image(img):

    if ( img[-4:] == '.jpg' or 
			img[-4:] == '.jpeg' or 
			img[-4:] == '.3gp' or 
			img[-4:] == '.avi' or 
			img[-4:] == '.png' or 
			img[-4:] == '.mp4' or 
			img[-4:] == '.mov' ):
        return True
    else:
        return False

def get_image_attr(img):
    
    # read the image data using PIL
    image = Image.open(img)

    # extract EXIF data
    exifdata = image.getexif()

    """
    The problem with exifdata variable now is that the field names are just IDs, not a 
    human readable field name, thats why we gonna need the TAGS dictionary from PIL.ExifTags 
    module which maps each tag ID into a human readable text 
    """

    # iterating over all EXIF data fields
    for tag_id in exifdata:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        # decode bytes 
        if isinstance(data, bytes):
            data = data.decode()
    
        print(f"{tag:25}: {data}")

    return

print ('Give directory location of image: ', end ="")
loc = input()

for img in os.listdir(loc):

    if (is_image(img) != True):
        continue

    imgpath = loc+'\\'+img

    print (imgpath)

    get_image_attr(imgpath)

    #break

