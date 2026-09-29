from ultralytics import YOLO


# Load the trained YOLOv8 model
model = YOLO("model/best.pt")


def predict(image):
    """
    Run YOLO prediction on the input image.
    """
    results = model(image)

    return results