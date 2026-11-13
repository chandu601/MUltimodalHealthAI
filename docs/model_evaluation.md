# Model Evaluation, Results, and Limitations

## 1. Evaluation Methodology

The proposed system consists of two multimodal classification models: one for skin disease classification and another for diabetic retinopathy grading. Both models combine medical image features with clinical metadata.

Model performance was assessed using held-out test datasets. The evaluation included accuracy, balanced accuracy, macro F1-score, class-wise precision and recall, and confusion matrix analysis. Quadratic Weighted Kappa (QWK) was additionally reported for the ordinal retinal grading task.

## 2. Overall Test Performance

| Metric | Skin Model | Retinal Model |
|---|---:|---:|
| Test samples | 346 | 460 |
| Accuracy | 74.28% | 50.65% |
| Balanced accuracy | 68.65% | 50.58% |
| Macro F1-score | 69.24% | 49.71% |
| Quadratic Weighted Kappa | Not reported | 0.7273 |

The skin model achieved higher overall classification performance than the retinal model. However, both models exhibited class-specific weaknesses that must be considered when interpreting their predictions.

## 3. Skin Disease Classification Results

The skin model classified six categories: Actinic Keratosis (ACK), Basal Cell Carcinoma (BCC), Melanoma (MEL), Melanocytic Nevus (NEV), Squamous Cell Carcinoma (SCC), and Seborrheic Keratosis (SEK).

The highest F1-score was obtained for NEV (0.89), followed by ACK (0.82). The weakest category was SCC, with an F1-score of 0.34 and recall of 0.33.

The confusion matrix revealed substantial confusion between BCC and SCC. Of the 42 actual SCC samples, only 14 were classified correctly, while 19 were classified as BCC. Similarly, 24 actual BCC samples were classified as SCC.

Melanoma evaluation was limited to five test examples, of which three were correctly classified. This small sample size prevents reliable conclusions about melanoma detection performance.

## 4. Retinal Disease Classification Results

The retinal model classified five diabetic retinopathy grades, DR0 through DR4.

The model achieved 50.65% exact-grade accuracy and a Quadratic Weighted Kappa of 0.7273.

DR4 achieved the highest recall (0.77), whereas DR3 had the lowest recall (0.31). DR2 also performed poorly, with an F1-score of 0.32.

The confusion matrix showed that 33 actual DR3 images were classified as DR4 and 22 were classified as DR2. These results demonstrate difficulty distinguishing intermediate and advanced grades.

Although QWK indicates meaningful ordinal agreement with the reference labels, the modest exact-grade accuracy limits the reliability of individual predictions.

## 5. Explainability

Grad-CAM was implemented to visualize image regions influencing model predictions. Integrated Gradients was used to estimate the contributions of encoded clinical features.

Both explanation APIs were successfully integrated with the Streamlit frontend.

Automated consistency tests confirmed matching predicted classes between the prediction and explanation endpoints for one held-out skin image and one held-out retinal image.

These methods describe model behavior. They do not establish clinically verified disease regions, causal clinical relationships, or diagnostic correctness.

## 6. System Reliability Testing

Six automated tests passed:

1. Unsupported image format rejection.
2. Empty image rejection.
3. Corrupted image rejection.
4. Invalid clinical metadata validation.
5. Skin prediction–explanation consistency.
6. Retinal prediction–explanation consistency.

Additional manual tests confirmed rejection of skin–retinal image-type mismatches and successful display of experimental image-quality warnings.

These tests establish basic functional behavior for the tested cases, not comprehensive robustness or clinical safety.

## 7. Limitations

The system has several important limitations:

- Weak detection performance for SCC in the skin model.
- Limited melanoma evaluation due to the small number of test samples.
- Low exact-grade accuracy for retinal classification.
- Difficulty distinguishing DR2 and DR3 retinal grades.
- Image-quality thresholds that have not been clinically validated.
- No demonstrated external clinical validation or prospective evaluation.
- No established medical correctness of the explanation heatmaps or attribution values.
- Limited automated coverage of edge cases and real-world deployment conditions.

## 8. Conclusion

The project demonstrates the technical feasibility of integrating multimodal medical image classification, clinical metadata processing, explainable AI, image validation, and an interactive screening interface.

The implemented prototype successfully performs prediction and generates explanations for both skin and retinal screening workflows.

However, the observed classification errors and absence of clinical validation mean that the system must be treated strictly as an experimental academic research prototype, not a medical diagnostic system or a clinically validated decision-support tool.