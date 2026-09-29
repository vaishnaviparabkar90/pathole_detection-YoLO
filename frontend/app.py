import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64


# =========================================================
# CONFIG
# =========================================================

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(
    page_title="Pothole Detection",
    page_icon="🚧",
    layout="wide"
)


# =========================================================
# MAIN TITLE
# =========================================================

st.title("🚧 Pothole Detection")

st.write(
    "AI-powered road inspection using YOLOv8"
)

st.write("")


# =========================================================
# HOW IT WORKS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Upload")
    st.caption("Choose a road image")

with col2:
    st.subheader("2. Detect")
    st.caption("YOLOv8 analyzes the image")

with col3:
    st.subheader("3. Report")
    st.caption("Review detected potholes")


st.divider()


# =========================================================
# UPLOAD SECTION
# =========================================================

st.subheader("Upload a road image")

uploaded_file = st.file_uploader(
    "Choose an image",
    type=["jpg", "jpeg", "png"]
)


# =========================================================
# PREVIEW + DETECT
# =========================================================

if uploaded_file is not None:

    image = Image.open(
        uploaded_file
    ).convert("RGB")


    st.image(
        image,
        caption="Image preview",
        width=500
    )


    st.write("")


    detect_button = st.button(
        "🔍 Detect Potholes",
        type="primary",
        use_container_width=True
    )


    if detect_button:

        with st.spinner(
            "Analyzing image with YOLOv8..."
        ):

            try:

                uploaded_file.seek(0)

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }


                response = requests.post(
                    API_URL,
                    files=files,
                    timeout=60
                )


                # =========================================
                # SUCCESS
                # =========================================

                if response.status_code == 200:

                    result = response.json()

                    st.session_state["result"] = result

                    st.session_state["original"] = image


                    # Force page refresh so result appears
                    st.rerun()


                # =========================================
                # API ERROR
                # =========================================

                else:

                    try:

                        error = response.json().get(
                            "detail",
                            "Prediction failed."
                        )

                    except Exception:

                        error = response.text


                    st.error(error)


            # =============================================
            # CONNECTION ERROR
            # =============================================

            except requests.exceptions.ConnectionError:

                st.error(
                    "FastAPI is not running. "
                    "Start the backend first."
                )


            # =============================================
            # TIMEOUT
            # =============================================

            except requests.exceptions.Timeout:

                st.error(
                    "Prediction took too long. "
                    "Please try again."
                )


            # =============================================
            # OTHER ERROR
            # =============================================

            except Exception as e:

                st.error(
                    f"Something went wrong: {str(e)}"
                )


# =========================================================
# RESULTS
# =========================================================

if "result" in st.session_state:

    result = st.session_state["result"]

    original_image = st.session_state["original"]


    total = result.get(
        "total_potholes",
        0
    )


    detections = result.get(
        "detections",
        []
    )


    st.divider()


    # =====================================================
    # RESULTS TITLE
    # =====================================================

    st.title("Detection Results")


    # =====================================================
    # SUMMARY
    # =====================================================

    if total > 0:

        confidences = [
            detection.get(
                "confidence",
                0
            )
            for detection in detections
        ]


        average_confidence = (
            sum(confidences) /
            len(confidences)
        )


        summary_col1, summary_col2 = st.columns(2)


        with summary_col1:

            st.metric(
                "Potholes Detected",
                total
            )


        with summary_col2:

            st.metric(
                "Average Confidence",
                f"{average_confidence:.0%}"
            )


        st.write("")


        # =================================================
        # IMAGE + REPORT
        # =================================================

        image_col, report_col = st.columns(
            [2, 1],
            gap="large"
        )


        # =================================================
        # DETECTED IMAGE
        # =================================================

        with image_col:

            st.subheader("Detected Image")


            if "annotated_image" in result:

                encoded_image = result[
                    "annotated_image"
                ]


                image_bytes = base64.b64decode(
                    encoded_image
                )


                detected_image = Image.open(
                    BytesIO(image_bytes)
                )


                st.image(
                    detected_image,
                    width=600
                )


                # -----------------------------------------
                # DOWNLOAD
                # -----------------------------------------

                st.download_button(
                    label="⬇️ Download Detected Image",
                    data=image_bytes,
                    file_name="pothole_detection.jpg",
                    mime="image/jpeg",
                    use_container_width=True
                )


        # =================================================
        # REPORT
        # =================================================

        with report_col:

            st.subheader("Detection Report")


            st.caption(
                f"{total} pothole"
                f"{'s' if total != 1 else ''} detected"
            )


            # ---------------------------------------------
            # SCROLLABLE REPORT
            # ---------------------------------------------

            with st.container(
                height=380,
                border=True
            ):

                for i, detection in enumerate(
                    detections,
                    start=1
                ):

                    class_name = detection.get(
                        "class",
                        "Pothole"
                    )


                    confidence = detection.get(
                        "confidence",
                        0
                    )


                    bbox = detection.get(
                        "bbox",
                        []
                    )


                    st.write(
                        f"**#{i} · {class_name}**"
                    )


                    st.progress(
                        confidence
                    )


                    st.caption(
                        f"Confidence: "
                        f"{confidence:.1%}"
                    )


                    st.caption(
                        f"Coordinates: {bbox}"
                    )


                    if i < len(detections):

                        st.divider()


    # =====================================================
    # NO DETECTIONS
    # =====================================================

    else:

        st.info(
            "✓ No potholes detected in this image."
        )


        st.subheader("Uploaded Image")


        st.image(
            original_image,
            width=600
        )


    # =====================================================
    # NEW IMAGE
    # =====================================================

    st.write("")

    if st.button(
        "↻ Analyze Another Image",
        use_container_width=True
    ):

        st.session_state.pop(
            "result",
            None
        )

        st.session_state.pop(
            "original",
            None
        )

        st.rerun()