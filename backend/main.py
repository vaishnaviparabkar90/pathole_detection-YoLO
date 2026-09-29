from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
from io import BytesIO
import base64

from backend.predictor import predict


app = FastAPI(
    title="Pothole Detection API",
    description="YOLOv8-based pothole detection API",
    version="1.0.0"
)


# -----------------------------
# Home
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "Pothole Detection API is running"
    }


# -----------------------------
# Prediction
# -----------------------------

@app.post("/predict")
async def prediction(file: UploadFile = File(...)):

    # Check file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid image file."
        )

    try:

        # Read uploaded image
        contents = await file.read()

        # Convert bytes to PIL image
        image = Image.open(
            BytesIO(contents)
        ).convert("RGB")

        # YOLO prediction
        results = predict(image)

        detections = []

        # Get first result
        result = results[0]

        # -----------------------------
        # Extract detections
        # -----------------------------

        for box in result.boxes:

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            confidence = float(box.conf[0])

            class_id = int(box.cls[0])

            class_name = result.names[class_id]

            detections.append({
                "class": class_name,
                "confidence": round(confidence, 4),
                "bbox": [
                    round(x1, 2),
                    round(y1, 2),
                    round(x2, 2),
                    round(y2, 2)
                ]
            })

        # -----------------------------
        # Create image with boxes
        # -----------------------------

        annotated_image = result.plot()

        # YOLO plot() returns BGR NumPy image
        annotated_image = Image.fromarray(
            annotated_image[:, :, ::-1]
        )

        # -----------------------------
        # Convert image → Base64
        # -----------------------------

        buffer = BytesIO()

        annotated_image.save(
            buffer,
            format="JPEG"
        )

        encoded_image = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

        # -----------------------------
        # Return response
        # -----------------------------

        return {
            "filename": file.filename,
            "total_potholes": len(detections),
            "detections": detections,
            "annotated_image": encoded_image
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )