import cv2
path=r"D:\Projects\Python\Items\ns_image.jpg"
try:
    
    src=cv2.imread(path)
    if src is None:
        raise Exception("Error loading Image")
    
    else:
        scale_percent=50
        new_width = int(src.shape[1] * scale_percent / 100)
        new_hieght=int(src.shape[0]* scale_percent / 100)

    Resized_image=cv2.resize(src, (new_width, new_hieght))
    cv2.imwrite("Resized_Image.jpg", Resized_image)
    cv2.imshow("title",Resized_image)
    cv2.waitKey(0)
except Exception as e:
    print(f"Error : {e}")