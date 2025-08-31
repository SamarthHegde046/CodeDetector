import cv2
import os

# Define the image path
path = r"D:\Projects\Python\Items\ns_image.jpg"

try:
    # Read the image
    src = cv2.imread(path)
    if src is None:
        raise Exception("Failed to load image. Check if the file path is correct.")

    # Define scaling percentage
    scale_percent = 50

    # Calculate new dimensions
    new_width = int(src.shape[1] * scale_percent / 100)
    new_height = int(src.shape[0] * scale_percent / 100)

    # Resize the image
    resized_image = cv2.resize(src, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Define output path
    output_path = "Resized_Image.jpg"

    # Save the resized image
    cv2.imwrite(output_path, resized_image)
    print(f"Resized image saved as {output_path}")

    # Display the resized image
    cv2.imshow("Resized Image", resized_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

except FileNotFoundError:
    print(f"Error: The file at {path} was not found.")
except Exception as e:
    print(f"An error occurred: {e}")