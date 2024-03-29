import cv2
import argparse


def on_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_points.append((x, y))
        print(f"Clicked at x: {x}, y: {y}")

def main(image_path):
    image = cv2.imread(image_path)
    cv2.namedWindow("Image Clicker")
    cv2.setMouseCallback("Image Clicker", on_click)

    while True:
        cv2.imshow("Image Clicker", image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()

    # Save the coordinates to a file
    with open("clicked_points.txt", "w") as file:
        for point in clicked_points:
            file.write(f"{point[0]},{point[1]}\n")

if __name__ == "__main__":
    clicked_points = []
    parser = argparse.ArgumentParser(description="Image Clicker")
    parser.add_argument("image_path", help="Path to the image file")
    args = parser.parse_args()
    main(args.image_path)
