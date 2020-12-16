import os
from PIL import Image
from PIL.ExifTags import TAGS

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

    if (img[-4:] != '.jpg') and (img[-4:] != '.png'):
        continue

    imgpath = loc+'\\'+img

    print (imgpath)

    get_image_attr(imgpath)

    #break

