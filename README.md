
# Explainable Multimodal AI-Based Healthcare Screening and Clinical Decision Support System

## 1. Project Overview

This project is a final-year B.Tech Computer Science and Engineering academic research prototype that combines deep learning, medical image analysis, structured clinical information, and explainable AI.

The system supports two screening tasks:

1. Skin lesion classification into six categories.
2. Diabetic retinopathy classification into five grades.

Each screening model uses both medical image information and relevant clinical metadata.

The application also provides:
- Image-type validation.
- Experimental image-quality assessment.
- Visual explanations using Grad-CAM.
- Clinical feature contributions using Integrated Gradients.
- Multilingual interface support.
- General doctor consultation guidance.

**Important:** This is an experimental academic prototype. It is not clinically validated and must not be used for medical diagnosis, treatment decisions, or determining medical urgency.

---

## 2. Problem Statement

Medical image classification systems commonly rely on image information alone. However, relevant clinical characteristics may also contribute to predictions.

This project investigates a multimodal approach that combines medical images with structured patient information while providing explanations of model behavior.

The objective is to demonstrate the technical feasibility of such a system, not to establish clinical diagnostic effectiveness.

---

## 3. Project Objectives

- Develop multimodal classification models for skin lesions and diabetic retinopathy.
- Combine image features with structured clinical metadata.
- Provide a web interface for submitting images and clinical inputs.
- Explain model predictions through Grad-CAM and clinical feature attribution.
- Validate uploaded medical images before inference.
- Display experimental image-quality warnings.
- Support English, Telugu, and Hindi.
- Provide general doctor consultation guidance.
- Evaluate the models on held-out test datasets.

---

## 4. Supported Screening Tasks

### 4.1 Skin Lesion Screening

The skin model predicts one of six categories:

| Code | Category |
|------|----------|
| ACK | Actinic Keratosis |
| BCC | Basal Cell Carcinoma |
| MEL | Melanoma |
| NEV | Melanocytic Nevus |
| SCC | Squamous Cell Carcinoma |
| SEK | Seborrheic Keratosis |

The clinical inputs include:

- Age
- Gender
- Lesion location
- Two lesion diameter measurements
- Itching
- Growth
- Pain
- Changes
- Bleeding
- Elevation
- Previous skin cancer history

The system displays the predicted category and model-assigned probabilities.

### 4.2 Diabetic Retinopathy Screening

The retinal model predicts five grades:

| Code | Grade |
|------|-------|
| DR0 | Grade 0 |
| DR1 | Grade 1 |
| DR2 | Grade 2 |
| DR3 | Grade 3 |
| DR4 | Grade 4 |

Clinical inputs include:

- Age
- Sex
- Diabetes type

The retinal screening workflow requires a fundus image obtained using appropriate retinal imaging equipment.

The system does not replace a professional retinal examination.

---

## 5. System Architecture

The application consists of a Streamlit frontend and FastAPI backend.

### Processing Workflow

1. The user selects a screening type.
2. The user provides a medical image.
3. The user enters clinical information.
4. The frontend submits the image and metadata to FastAPI.
5. The backend validates the uploaded image.
6. The backend preprocesses image and clinical features.
7. The corresponding multimodal model performs inference.
8. The predicted category and probability distribution are returned.
9. The frontend displays experimental image-quality information.
10. General doctor consultation guidance is displayed.
11. On request, the explanation API generates Grad-CAM and clinical feature contributions.

### Main Components

**Frontend**
- Streamlit
- Clinical information forms
- Multilingual interface
- Prediction visualization
- Explanation visualization
- Consultation guidance

**Backend**
- FastAPI
- Input validation
- Model loading
- Clinical preprocessing
- Multimodal inference
- Explanation generation

**Models**
- Skin multimodal classification model
- Retinal multimodal classification model
- Image-type validation model

---

## 6. Technologies Used

| Component | Technology |
|-----------|------------|
| Programming language | Python |
| Deep learning | PyTorch |
| Image processing | Pillow, OpenCV |
| Machine learning utilities | Scikit-learn |
| Data processing | NumPy, Pandas |
| Backend | FastAPI |
| Frontend | Streamlit |
| API communication | HTTP requests |
| Visual explanations | Grad-CAM |
| Clinical feature attribution | Integrated Gradients |
| Model storage | PyTorch checkpoints |
| Clinical preprocessing | Saved Scikit-learn preprocessor |

The exact dependency versions are maintained in `requirements.txt`.

---

## 7. Project Structure

```text
MultimodalHealthAI/
├── backend/
│   ├── main.py
│   ├── prediction_api.py
│   ├── explanation_api.py
│   ├── skin_explanation_api.py
│   ├── image_validator.py
│   ├── image_quality_validator.py
│   └── model_loader.py
│
├── frontend/
│   ├── app.py
│   └── translations.py
│
├── checkpoints/
│   ├── skin_multimodal_best.pth
│   ├── retinal_multimodal_best.pth
│   ├── image_type_best.pth
│   └── calibration files
│
├── data/
│   ├── processed/
│   ├── retinal/
│   ├── skin/
│   └── splits/
│
├── src/
│   ├── datasets/
│   ├── preprocessing/
│   ├── models/
│   ├── training/
│   ├── evaluation/
│   └── explainability/
│
├── notebooks/
│   ├── eda_outputs/
│   ├── retinal_outputs/
│   ├── image_type_outputs/
│   └── training_outputs/
│
├── results/
│   └── final_test/
│       ├── skin_predictions.csv
│       ├── skin_confusion_matrix.png
│       ├── retinal_predictions.csv
│       └── retinal_confusion_matrix.png
│
├── tests/
├── docs/
│   └── model_evaluation.md
│
├── requirements.txt
└── README.md
```

Some local directories contain additional experimental files and checkpoints.

---

## 8. Installation and Setup

### Requirements

- Python and pip
- A compatible operating system
- Project dependencies from `requirements.txt`
- Saved model checkpoints
- Saved clinical preprocessors

### Step 1: Open the Project Directory

```bash
cd ~/Documents/MultimodalHealthAI
```

### Step 2: Activate the Virtual Environment

```bash
source .venv/bin/activate
```

If the environment does not already exist:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Start FastAPI

Open a terminal and run:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Backend API:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

### Step 4: Start Streamlit

Open another terminal:

```bash
cd ~/Documents/MultimodalHealthAI
source .venv/bin/activate

python -m streamlit run frontend/app.py --server.port 8501
```

Open:

http://localhost:8501

Both the FastAPI and Streamlit processes must be running.

---

## 9. Model Evaluation

Both models were evaluated using held-out test datasets.

### Overall Test Performance

| Metric | Skin Model | Retinal Model |
|--------|------------|---------------|
| Test samples | 346 | 460 |
| Accuracy | 74.28% | 50.65% |
| Balanced accuracy | 68.65% | 50.58% |
| Macro F1-score | 69.24% | 49.71% |
| Quadratic Weighted Kappa | Not reported | 0.7273 |

These metrics were checked against the final test prediction CSV files and confusion matrices.

### Skin Model Findings

The skin model achieved 74.28% test accuracy.

However, performance differed substantially across categories.

SCC was particularly difficult to identify:
- 42 actual SCC samples.
- 14 correctly classified.
- Recall of approximately 33.33%.

The melanoma test set contained only five samples, limiting conclusions about melanoma detection reliability.

### Retinal Model Findings

The retinal model achieved 50.65% exact-grade test accuracy.

Performance was limited particularly for intermediate disease grades.

DR3 results:
- 97 actual DR3 samples.
- 30 correctly classified.
- Recall of approximately 30.93%.

The Quadratic Weighted Kappa was 0.7273, but this does not overcome the limitations of the model's exact-grade predictions.

### Final Test Artifacts

Skin confusion matrix:

`results/final_test/skin_confusion_matrix.png`

Retinal confusion matrix:

`results/final_test/retinal_confusion_matrix.png`

Detailed evaluation and limitations are available in:

`docs/model_evaluation.md`

---

## 10. Explainable AI

The application includes two explanation mechanisms.

### Grad-CAM

Grad-CAM generates heatmaps indicating image regions that influenced the model's predicted class.

The highlighted regions do not necessarily correspond to clinically confirmed disease findings.

### Integrated Gradients

Integrated Gradients estimates the contribution of encoded clinical features to a model class score relative to a reference input.

Attribution values:
- May be positive or negative.
- Describe model behavior.
- Are not disease-risk percentages.
- Do not establish causal medical relationships.

The frontend displays these explanations alongside the model prediction.

---

## 11. Image Validation

The backend implements several input checks:

- Supported image format verification.
- Empty-image rejection.
- Maximum uploaded image size of 12 MB.
- Image decoding checks.
- Skin-versus-retinal image-type validation.
- Experimental image-quality assessment.

Image-quality checks may generate warnings for blur, darkness, or excessive brightness.

These thresholds have not been clinically validated.

Image-quality warnings do not automatically reject an image.

---

## 12. Multilingual Interface

The Streamlit interface supports:

- English
- Telugu
- Hindi

Translations are maintained in:

`frontend/translations.py`

Translated content includes:
- Screening selection
- Clinical input labels and options
- Prediction results
- Image-quality information
- Explanation sections
- Doctor consultation guidance

The translation system changes displayed text without intentionally changing the internal metadata values required by the models.

---

## 13. Doctor Consultation Guidance

After a successful prediction, the interface provides general educational guidance.

For skin screening, it recommends professional assessment by a dermatologist.

For retinal screening, it recommends professional eye examinations by an ophthalmologist.

The guidance is not based on a clinically validated AI referral or urgency assessment.

It must not be interpreted as an automated medical referral decision.

---

## 14. Testing

The following verification activities were completed during development:

### Automated Testing

Six automated tests passed.

The verified cases included:
- Unsupported image format.
- Empty image.
- Corrupted image.
- Invalid clinical metadata.
- Skin prediction and explanation consistency.
- Retinal prediction and explanation consistency.

### Manual Functional Testing

Manual testing covered:
- Skin prediction workflow.
- Retinal prediction workflow.
- Prediction distributions.
- Grad-CAM visualization.
- Clinical feature contributions.
- Doctor consultation guidance.
- Multilingual interface behavior.
- Invalid input handling.

Automated and manual tests establish behavior for the tested cases, not comprehensive clinical or deployment safety.

### Running Automated Tests

```bash
python -m pytest -q
```

### Checking Python Syntax

```bash
python -m compileall -q backend frontend
```

---

## 15. Privacy Considerations

The application processes uploaded medical images and clinical information.

The reviewed frontend retains image data and metadata using Streamlit session state to support prediction and explanation workflows.

The inspected backend code did not show explicit permanent storage of uploaded images.

However, temporary-file handling, server logs, session retention, and deployment configuration have not undergone a comprehensive privacy audit.

Use non-identifiable test images during academic demonstrations.

The system should not be described as clinically compliant or privacy-certified.

---

## 16. Limitations

The system has several significant limitations:

1. Weak SCC classification performance.
2. Very limited melanoma test examples.
3. Low retinal exact-grade accuracy.
4. Difficulty distinguishing intermediate retinal grades.
5. Experimental image-quality thresholds.
6. No demonstrated external clinical validation.
7. No prospective clinical evaluation.
8. Explainability outputs are not clinically validated.
9. Limited testing of real-world deployment conditions.
10. Dataset split independence has not been independently audited.

These limitations prevent the prototype from being considered a clinically validated diagnostic system.

---

## 17. Conclusion

This project demonstrates the technical feasibility of combining multimodal medical image classification, structured clinical metadata, explainable AI, image validation, multilingual interaction, and general consultation guidance in a single application.

Both screening workflows were implemented and tested.

However, the measured classification errors and lack of clinical validation mean that the system must remain an experimental academic research prototype.

It is not intended for clinical diagnosis or treatment decisions.
