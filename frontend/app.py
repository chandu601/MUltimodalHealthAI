
# frontend/app.py

import base64
import binascii
import hashlib
import json
import math
from pathlib import Path

import joblib
import pandas as pd
import requests
import streamlit as st

from frontend.translations import translate


# ==================================================
# CONFIGURATION
# ==================================================

ROOT = Path(__file__).resolve().parents[1]
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Explainable Multimodal Healthcare AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

language = st.selectbox(
    "🌐 Language / భాష / भाषा",
    options=["English", "తెలుగు", "हिन्दी"],
    key="selected_language",
)


def t(key):
    return translate(key, language)


# ==================================================
# HELPER FUNCTIONS
# ==================================================

@st.cache_resource
def load_skin_preprocessor():
    path = (
        ROOT
        / "data"
        / "processed"
        / "skin"
        / "clinical_preprocessor.joblib"
    )
    return joblib.load(path)


def get_skin_categories():
    preprocessor = load_skin_preprocessor()

    encoder = (
        preprocessor
        .named_transformers_["categorical"]
        .named_steps["encoder"]
    )

    columns = [
        "gender",
        "region",
        "itch",
        "grew",
        "hurt",
        "changed",
        "bleed",
        "elevation",
        "skin_cancer_history",
    ]

    if len(columns) != len(encoder.categories_):
        raise RuntimeError(
            "Skin categorical fields do not match "
            "the saved clinical encoder."
        )

    return {
        name: [str(v) for v in values]
        for name, values in zip(
            columns, encoder.categories_
        )
    }


REGION_CODES = {
    "ABDOMEN", "ARM", "BACK", "CHEST",
    "EAR", "FACE", "FOOT", "FOREARM",
    "HAND", "LIP", "NECK", "NOSE",
    "SCALP", "THIGH",
}


def friendly_choice(value):
    """Translate display labels without changing API values."""
    value = str(value)
    lower = value.lower()

    if lower == "true":
        return t("yes")
    if lower == "false":
        return t("no")
    if lower in {
        "missing", "nan", "none", "unk", "unknown"
    }:
        return t("unknown_not_sure")
    if lower in {"male", "m"}:
        return t("male")
    if lower in {"female", "f"}:
        return t("female")
    if value.upper() in REGION_CODES:
        return t(value.upper())

    return value.replace("_", " ").title()


def category_input(label, values, key):
    return st.selectbox(
        label,
        options=values,
        format_func=friendly_choice,
        key=key,
    )


def validate_diameter(value, label):
    if value is None or str(value).strip() == "":
        return None

    try:
        number = float(str(value).strip())
    except (ValueError, TypeError):
        raise ValueError(
            f"{label}: please enter a valid number."
        )

    if not math.isfinite(number) or number < 0:
        raise ValueError(
            f"{label}: enter a non-negative finite number."
        )

    return number


def clear_saved_results():
    for key in [
        "last_prediction",
        "last_explanation",
        "last_image",
        "last_metadata",
        "last_screening",
        "last_fingerprint",
        "last_endpoint",
    ]:
        st.session_state.pop(key, None)


def make_fingerprint(screening_type, image_bytes, metadata_json):
    digest = hashlib.sha256()
    digest.update(screening_type.encode("utf-8"))
    digest.update(image_bytes)
    digest.update(metadata_json.encode("utf-8"))
    return digest.hexdigest()


def get_class_labels(screening_type):
    if screening_type == "retinal":
        return {
            f"DR{i}": t(f"grade_{i}")
            for i in range(5)
        }

    return {
        code: t(f"class_{code}")
        for code in [
            "ACK", "BCC", "MEL",
            "NEV", "SCC", "SEK"
        ]
    }


KNOWN_API_ERRORS = {
    "The uploaded image appears to belong to a different screening category. Please check the image and selected screening type.":
        "type_mismatch_error",
    "The image type could not be verified with sufficient certainty. Please upload a suitable medical image.":
        "type_uncertain_error",
    "Please upload a JPG or PNG image.":
        "unsupported_image_error",
    "The uploaded image is empty.":
        "empty_image_error",
    "The uploaded image could not be read.":
        "unreadable_image_error",
    "Clinical metadata must be valid JSON.":
        "invalid_json_error",
}


def show_api_error(response):
    st.error(
        f"{t('backend_http')} {response.status_code}"
    )

    try:
        body = response.json()
    except ValueError:
        st.warning(t("backend_non_json"))
        with st.expander(t("view_backend")):
            st.code(
                response.text[:5000]
                or t("empty_server")
            )
        return

    detail = body.get("detail", t("unknown_backend"))

    if isinstance(detail, dict):
        message = detail.get(
            "message", t("request_failed")
        )
        translated = KNOWN_API_ERRORS.get(message)
        st.error(t(translated) if translated else message)

        with st.expander(t("view_details")):
            st.json(detail)

    elif isinstance(detail, str):
        translated = KNOWN_API_ERRORS.get(detail)
        st.error(t(translated) if translated else detail)

    else:
        st.error(t("unexpected_backend"))
        st.write(detail)


# ==================================================
# APPLICATION HEADER
# ==================================================

st.title("🩺 " + t("app_title"))
st.write(t("app_description"))
st.warning(t("research_warning"))

st.divider()


# ==================================================
# 1. SCREENING SELECTION
# ==================================================

st.subheader("1. " + t("screening_type"))

current_type = st.radio(
    t("screening_type"),
    options=["retinal", "skin"],
    format_func=lambda value: (
        t("retinal_screening")
        if value == "retinal"
        else t("skin_screening")
    ),
    horizontal=True,
    label_visibility="collapsed",
)

if current_type == "retinal":
    st.info(t("retinal_instructions"))
else:
    st.info(t("skin_instructions"))



# ==================================================
# 2. MEDICAL IMAGE INPUT
# ==================================================

st.divider()
st.subheader("2. " + t("provide_image"))

# Retinal screening instructions
if current_type == "retinal":
    st.caption(t("retinal_image_caption"))

# Upload an image from the device
# Camera functionality has been removed
uploaded_file = st.file_uploader(
    t("upload_jpg_png"),
    type=["jpg", "jpeg", "png"],
    key=f"upload_{current_type}",
)

# Display the uploaded image
if uploaded_file is not None:
    st.success(t("image_selected"))

    st.image(
        uploaded_file,
        caption=t("selected_image"),
        width=320,
    )


# ==================================================
# 3. CLINICAL INFORMATION
# ==================================================


st.divider()
st.subheader("3. " + t("patient_information"))

with st.form(key=f"healthcare_form_{current_type}"):

    if current_type == "retinal":
        col1, col2 = st.columns(2)

        with col1:
            age = st.number_input(
                t("age"),
                min_value=0,
                max_value=120,
                value=58,
                step=1,
                key="retinal_age",
            )

            sex = st.selectbox(
                t("sex"),
                options=["Male", "Female"],
                format_func=lambda value: (
                    t("male")
                    if value == "Male"
                    else t("female")
                ),
                key="retinal_sex",
            )

        with col2:
            diabetes = st.selectbox(
                t("diabetes_type"),
                options=["Type 1", "Type 2"],
                format_func=lambda value: (
                    t("diabetes_type_1")
                    if value == "Type 1"
                    else t("diabetes_type_2")
                ),
                key="retinal_diabetes",
            )

        # Keep the original retinal API values.
        metadata = {
            "age": int(age),
            "sexe": "M" if sex == "Male" else "F",
            "type_diabete": (
                "1" if diabetes == "Type 1" else "2"
            ),
        }
        prediction_endpoint = "/predict/retinal"

    else:
        categories = get_skin_categories()

        age = st.number_input(
            t("age"),
            min_value=0,
            max_value=120,
            value=50,
            step=1,
            key="skin_age",
        )
        st.info(t("lesion_help"))
        st.caption(t("measurement_guidance"))

        col1, col2 = st.columns(2)

        with col1:
            diameter_1 = st.text_input(
                t("diameter_1"),
                placeholder=t("optional"),
                key="skin_diameter_1",
            )

            gender = category_input(
                t("gender_dataset"),
                categories["gender"],
                "skin_gender",
            )

            itch = category_input(
                t("itch_question"),
                categories["itch"],
                "skin_itch",
            )

            grew = category_input(
                t("grew_question"),
                categories["grew"],
                "skin_grew",
            )

            hurt = category_input(
                t("hurt_question"),
                categories["hurt"],
                "skin_hurt",
            )

            changed = category_input(
                t("changed_question"),
                categories["changed"],
                "skin_changed",
            )

        with col2:
            diameter_2 = st.text_input(
                t("diameter_2"),
                placeholder=t("optional"),
                key="skin_diameter_2",
            )

            region = category_input(
                t("region_question"),
                categories["region"],
                "skin_region",
            )

            bleed = category_input(
                t("bleed_question"),
                categories["bleed"],
                "skin_bleed",
            )

            elevation = category_input(
                t("elevation_question"),
                categories["elevation"],
                "skin_elevation",
            )

            skin_cancer_history = category_input(
                t("skin_cancer_history"),
                categories["skin_cancer_history"],
                "skin_history",
            )

        # Keep the original skin API field names
        # and categorical values.
        metadata = {
            "age": int(age),
            "diameter_1": diameter_1,
            "diameter_2": diameter_2,
            "gender": gender,
            "region": region,
            "itch": itch,
            "grew": grew,
            "hurt": hurt,
            "changed": changed,
            "bleed": bleed,
            "elevation": elevation,
            "skin_cancer_history": skin_cancer_history,
        }
        prediction_endpoint = "/predict/skin"

    st.divider()

    confirmed = st.checkbox(
        t("confirm_information"),
        key=f"confirmed_{current_type}",
    )

    submitted = st.form_submit_button(
        "🔍 " + t("analyze"),
        use_container_width=True,
        type="primary",
    )


# ==================================================
# DISPLAY PREDICTION
# ==================================================

def display_prediction(result):
    st.divider()
    st.header("📋 " + t("result_heading"))

    screening_type = result.get(
        "screening_type", current_type
    )
    labels = get_class_labels(screening_type)

    predicted_class = result.get(
        "predicted_class", "Unknown"
    )
    predicted_name = labels.get(
        predicted_class, predicted_class
    )

    probability = float(
        result.get("model_probability", 0.0)
    )

    st.write(f"**{t('predicted_category')}**")
    st.subheader(
        f"{predicted_class} — {predicted_name}"
    )

    # ===============================================
    # SIMPLE SKIN CONDITION EXPLANATION
    # ===============================================

    if screening_type == "skin":
        supported_skin_classes = {
            "ACK", "BCC", "MEL",
            "NEV", "SCC", "SEK",
        }

        if predicted_class in supported_skin_classes:
            st.write(
                "**" + t("skin_info_category") + ":** "
                + t(f"skin_info_{predicted_class}_type")
            )

            st.write(
                t(f"skin_info_{predicted_class}_description")
            )

            with st.expander(t("skin_info_heading")):
                st.warning(t("skin_info_note"))
    
    # ===============================================
    # SIMPLE RETINAL GRADE EXPLANATION
    # ===============================================

    if screening_type == "retinal":
        supported_retinal_grades = {
            "DR0", "DR1", "DR2", "DR3", "DR4"
        }

        if predicted_class in supported_retinal_grades:
            st.write(
                "**" +
                t(f"retinal_info_{predicted_class}_type")
                + "**"
            )

            st.write(
                t(f"retinal_info_{predicted_class}_description")
            )

            with st.expander(t("retinal_info_heading")):
                st.warning(t("retinal_info_note"))



    st.metric(
        t("model_probability"),
        f"{probability * 100:.2f}%",
    )
    st.progress(max(0.0, min(probability, 1.0)))
    st.caption(t("probability_warning"))

    st.divider()
    st.subheader(t("prediction_distribution"))

    probabilities = result.get(
        "class_probabilities", {}
    )

    for name, value in probabilities.items():
        number = float(value)
        label = labels.get(name, name)

        st.write(
            f"**{name} — {label}: "
            f"{number * 100:.2f}%**"
        )
        st.progress(max(0.0, min(number, 1.0)))

    st.divider()

    if result.get("image_type_validated", False):
        st.success(t("image_type_accepted"))
        st.caption(t("image_type_warning"))

    quality = result.get("image_quality")

    if quality is not None:
        st.subheader(t("image_quality"))

        blur_score = quality.get("blur_score")
        brightness = quality.get("brightness")

        if blur_score is not None:
            st.write(
                f"**{t('blur_score')}:** {blur_score}"
            )

        if brightness is not None:
            st.write(
                f"**{t('brightness')}:** {brightness}"
            )

        issue_keys = {
            "Image may be blurry": "quality_blurry",
            "Image is too dark": "quality_dark",
            "Image is too bright": "quality_bright",
        }

        issues = quality.get("issues", [])

        if issues:
            for issue in issues:
                key = issue_keys.get(issue)
                st.warning(t(key) if key else issue)
        else:
            st.success(t("quality_passed"))

        st.caption(t("quality_disclaimer"))
        st.divider()

    if result.get("calibration_applied", False):
        st.info(t("calibrated"))
    else:
        st.info(t("uncalibrated"))

    st.warning(t("disclaimer"))


# ==================================================
# PROCESS IMAGE ANALYSIS
# ==================================================

if submitted:
    clear_saved_results()

    if uploaded_file is None:
        st.error(t("image_required"))

    elif not confirmed:
        st.warning(t("confirm_required"))

    else:
        try:
            if current_type == "skin":
                metadata["diameter_1"] = validate_diameter(
                    metadata["diameter_1"],
                    t("diameter_1"),
                )
                metadata["diameter_2"] = validate_diameter(
                    metadata["diameter_2"],
                    t("diameter_2"),
                )

            image_bytes = uploaded_file.getvalue()
            image_name = uploaded_file.name
            image_mime = (
                uploaded_file.type or "image/jpeg"
            )

            metadata_json = json.dumps(
                metadata,
                sort_keys=True,
            )

            with st.spinner(t("analyzing")):
                response = requests.post(
                    API_URL + prediction_endpoint,
                    files={
                        "file": (
                            image_name,
                            image_bytes,
                            image_mime,
                        )
                    },
                    data={
                        "metadata": metadata_json
                    },
                    timeout=120,
                )

            if response.status_code == 200:
                result = response.json()

                st.session_state[
                    "last_prediction"
                ] = result

                st.session_state[
                    "last_image"
                ] = (
                    image_name,
                    image_bytes,
                    image_mime,
                )

                st.session_state[
                    "last_metadata"
                ] = metadata_json

                st.session_state[
                    "last_screening"
                ] = current_type

                st.session_state[
                    "last_endpoint"
                ] = prediction_endpoint

                st.session_state[
                    "last_fingerprint"
                ] = make_fingerprint(
                    current_type,
                    image_bytes,
                    metadata_json,
                )

            else:
                show_api_error(response)

        except ValueError as exc:
            st.error(str(exc))

        except requests.exceptions.Timeout:
            st.error(t("analysis_timeout"))

        except requests.exceptions.RequestException as exc:
            st.error(t("connection_error"))
            st.caption(str(exc))


# ==================================================
# CHECK WHETHER SAVED RESULT IS CURRENT
# ==================================================

saved_result = st.session_state.get(
    "last_prediction"
)
saved_screening = st.session_state.get(
    "last_screening"
)
saved_fingerprint = st.session_state.get(
    "last_fingerprint"
)

current_fingerprint = None

if uploaded_file is not None:
    try:
        current_metadata = dict(metadata)

        if current_type == "skin":
            current_metadata["diameter_1"] = (
                validate_diameter(
                    current_metadata["diameter_1"],
                    t("diameter_1"),
                )
            )
            current_metadata["diameter_2"] = (
                validate_diameter(
                    current_metadata["diameter_2"],
                    t("diameter_2"),
                )
            )

        current_metadata_json = json.dumps(
            current_metadata,
            sort_keys=True,
        )

        current_fingerprint = make_fingerprint(
            current_type,
            uploaded_file.getvalue(),
            current_metadata_json,
        )

    except ValueError:
        current_fingerprint = None


result_is_current = (
    saved_result is not None
    and saved_screening == current_type
    and saved_fingerprint is not None
    and saved_fingerprint == current_fingerprint
)

if (
    saved_result is not None
    and saved_screening == current_type
    and not result_is_current
):
    st.info(t("result_stale"))


# ==================================================
# DISPLAY PREDICTION AND EXPLANATION
# ==================================================


if result_is_current:
    display_prediction(saved_result)

    # ==============================================
    # DOCTOR CONSULTATION GUIDANCE
    # ==============================================

    st.divider()

    st.subheader(
        "🩺 " + t("doctor_guidance")
    )

    if current_type == "skin":
        st.write(
            "**" + t("recommended_specialist") + ":** "
            + t("dermatologist")
        )

        st.info(
            t("skin_consultation")
        )

    elif current_type == "retinal":
        st.write(
            "**" + t("recommended_specialist") + ":** "
            + t("ophthalmologist")
        )

        st.info(
            t("retinal_consultation")
        )

        st.warning(
            t("retinal_urgent_warning")
        )

    st.caption(
        t("consultation_disclaimer")
    )

    # ==============================================
    # EXISTING AI EXPLANATION SECTION
    # ==============================================

    st.divider()

    st.subheader(
        "🧠 " + t("explanation_heading")
    )
    st.write(t("explanation_description"))

    explain_clicked = st.button(
        "🧠 " + t("explain"),
        key=f"explain_{current_type}",
        use_container_width=True,
    )

    if explain_clicked:
        image_data = st.session_state.get(
            "last_image"
        )
        metadata_json = st.session_state.get(
            "last_metadata"
        )

        if image_data is None or metadata_json is None:
            st.error(t("analyze_first"))

        else:
            try:
                endpoint = f"/explain/{current_type}"

                with st.spinner(t("explaining")):
                    explanation_response = requests.post(
                        API_URL + endpoint,
                        files={
                            "file": image_data
                        },
                        data={
                            "metadata": metadata_json
                        },
                        timeout=180,
                    )

                if explanation_response.status_code == 200:
                    st.session_state[
                        "last_explanation"
                    ] = explanation_response.json()

                else:
                    st.session_state.pop(
                        "last_explanation",
                        None,
                    )
                    show_api_error(explanation_response)

            except requests.exceptions.Timeout:
                st.error(t("explanation_timeout"))

            except requests.exceptions.RequestException as exc:
                st.error(
                    t("explanation_connection_error")
                )
                st.caption(str(exc))

    explanation = st.session_state.get(
        "last_explanation"
    )

    if explanation is not None:
        explanation_class = explanation.get(
            "predicted_class"
        )
        prediction_class = saved_result.get(
            "predicted_class"
        )
        explanation_type = explanation.get(
            "screening_type"
        )

        if (
            explanation_class != prediction_class
            or explanation_type != current_type
        ):
            st.warning(t("explanation_mismatch"))

        else:
            st.divider()
            st.header(
                "🔬 " + t("explanation_results")
            )

            # ------------------------------------------
            # GRAD-CAM VISUALIZATION
            # ------------------------------------------

            st.subheader(
                "1. " + t("visual_explanation")
            )

            encoded = explanation.get(
                "visual_explanation"
            )

            if encoded:
                try:
                    heatmap_bytes = base64.b64decode(
                        encoded,
                        validate=True,
                    )

                    screening_label = (
                        t("skin_screening")
                        if current_type == "skin"
                        else t("retinal_screening")
                    )

                    st.image(
                        heatmap_bytes,
                        caption=(
                            screening_label
                            + " — "
                            + t("heatmap")
                        ),
                        use_container_width=True,
                    )

                except (
                    ValueError,
                    TypeError,
                    binascii.Error,
                ):
                    st.error(t("heatmap_error"))

            else:
                st.warning(t("heatmap_missing"))

            st.info(t("gradcam_warning"))

            # ------------------------------------------
            # CLINICAL FEATURE CONTRIBUTIONS
            # ------------------------------------------

            st.subheader(
                "2. " + t("clinical_contributions")
            )

            contributions = explanation.get(
                "clinical_contributions", {}
            )

            feature_keys = {
                "sexe": "sex",
                "type_diabete": "diabetes_type",
                "diabetes_type": "diabetes_type",
                "sex": "sex",
            }

            def feature_label(name):
                translation_key = feature_keys.get(
                    name, name
                )
                translated = t(translation_key)

                if translated == translation_key:
                    return name.replace(
                        "_", " "
                    ).title()

                return translated

            if contributions:
                chart_rows = [
                    {
                        "Feature": feature_label(name),
                        "Contribution": float(value),
                    }
                    for name, value in contributions.items()
                ]

                chart_data = pd.DataFrame(
                    chart_rows
                )

                st.bar_chart(
                    chart_data,
                    x="Feature",
                    y="Contribution",
                )

                with st.expander(
                    t("exact_contributions")
                ):
                    for name, value in contributions.items():
                        st.write(
                            f"**{feature_label(name)}:** "
                            f"{float(value):+.6f}"
                        )

                st.caption(
                    t("attribution_warning")
                )

            else:
                st.info(t("contributions_missing"))

            # ------------------------------------------
            # PLAIN-LANGUAGE EXPLANATION
            # ------------------------------------------

            st.subheader(
                "3. " + t("understanding_explanation")
            )

            if current_type == "skin":
                st.write(
                    t("skin_model_description")
                )
                st.write(
                    t("skin_explanation_description")
                )

            else:
                st.write(
                    t("retinal_model_description")
                )
                st.write(
                    t("retinal_explanation_description")
                )

            st.warning(
                t("explanation_disclaimer")
            )


# ==================================================
# FOOTER
# ==================================================

st.divider()
st.caption(t("footer"))
