from PIL import Image
import os


def main():
    img_list = scan(ext='.png')
    for img in img_list:
        crop(img, left=12, upper=92, right=(1024-12), lower=(600-92))


def crop(filename, left, upper, right, lower):
    im = Image.open(filename)
    im_crop = im.crop((left, upper, right, lower))
    im_crop.save(filename, quality=100)


def scan(ext = 'png'):
    img_list = []
    dir_content = os.listdir()    
    for member in dir_content:
        if os.path.isfile(member) == True:
            print("object", member, "is file")
            e = os.path.splitext(member)[1]
            if e == ext:
                img_list.append(member)
        elif os.path.isdir(member) == True:
            print("object", member, "is directory")

    return img_list


if __name__ == '__main__':
    main()
