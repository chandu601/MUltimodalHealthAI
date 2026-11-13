
# frontend/translations.py
# Translations affect display text only.
# API field names and model input values remain unchanged.

LANGUAGES = ("English", "తెలుగు", "हिन्दी")

# Each entry contains English, Telugu, and Hindi in that order.
TEXT = {
    "app_title": (
        "Explainable Multimodal Healthcare AI",
        "వివరణాత్మక మల్టీమోడల్ ఆరోగ్య AI",
        "व्याख्यात्मक मल्टीमॉडल स्वास्थ्य एआई",
    ),
    "app_description": (
        "An experimental AI-based screening platform for skin lesions and diabetic retinopathy.",
        "చర్మ గాయాలు మరియు డయాబెటిక్ రెటినోపతి కోసం ప్రయోగాత్మక AI ఆధారిత పరీక్షా వేదిక.",
        "त्वचा के घावों और डायबिटिक रेटिनोपैथी के लिए एक प्रयोगात्मक एआई-आधारित जाँच मंच।",
    ),
    "research_warning": (
        "Academic research prototype only. Predictions and explanations are not clinically validated and must not be used as medical diagnoses.",
        "ఇది విద్యా పరిశోధన కోసం రూపొందించిన నమూనా మాత్రమే. AI అంచనాలు మరియు వివరణలు వైద్యపరంగా ధృవీకరించబడలేదు. వీటిని వైద్య నిర్ధారణగా ఉపయోగించరాదు.",
        "यह केवल शैक्षणिक अनुसंधान के लिए बनाया गया प्रोटोटाइप है। एआई के अनुमान और व्याख्याएँ चिकित्सकीय रूप से सत्यापित नहीं हैं। इन्हें चिकित्सीय निदान के रूप में उपयोग नहीं करना चाहिए।",
    ),
    "language": ("Language", "భాష", "भाषा"),
    "screening_type": (
        "Choose Screening Type",
        "పరీక్ష రకాన్ని ఎంచుకోండి",
        "जाँच का प्रकार चुनें",
    ),
    "skin_screening": (
        "Skin Disease Screening",
        "చర్మ వ్యాధుల పరీక్ష",
        "त्वचा रोग की जाँच",
    ),
    "retinal_screening": (
        "Retinal Disease Screening",
        "రెటీనా వ్యాధుల పరీక్ష",
        "रेटिना रोग की जाँच",
    ),
    "skin_instructions": (
        "Upload a clear photograph of a skin lesion. Use good lighting and keep the lesion in focus.",
        "చర్మ గాయం యొక్క స్పష్టమైన ఫోటోను అప్‌లోడ్ చేయండి. మంచి వెలుతురులో ఫోటో తీయండి.",
        "त्वचा के घाव की स्पष्ट तस्वीर अपलोड करें। अच्छी रोशनी में तस्वीर लें।",
    ),
    "retinal_instructions": (
        "Upload a retinal fundus photograph obtained using suitable retinal imaging equipment. An ordinary phone photograph cannot replace a fundus image.",
        "తగిన రెటీనా చిత్రీకరణ పరికరంతో తీసిన రెటీనా ఫండస్ చిత్రాన్ని అప్‌లోడ్ చేయండి. సాధారణ ఫోన్ ఫోటో ఫండస్ చిత్రానికి ప్రత్యామ్నాయం కాదు.",
        "उपयुक्त रेटिना इमेजिंग उपकरण से ली गई रेटिनल फंडस छवि अपलोड करें। सामान्य फोन की तस्वीर फंडस छवि का विकल्प नहीं है।",
    ),
    "provide_image": (
        "Provide Medical Image",
        "వైద్య చిత్రాన్ని అందించండి",
        "चिकित्सीय छवि दें",
    ),
    "image_source": (
        "Image Source",
        "చిత్రం తీసుకునే విధానం",
        "छवि का स्रोत",
    ),
    "upload_from_device": (
        "Upload from Device",
        "పరికరం నుండి అప్‌లోడ్ చేయండి",
        "डिवाइस से अपलोड करें",
    ),
    "capture_using_camera": (
        "Capture using Camera",
        "కెమెరాతో తీయండి",
        "कैमरे से लें",
    ),
    "retinal_image_caption": (
        "Retinal screening accepts existing fundus images.",
        "రెటీనా పరీక్ష కోసం ఇప్పటికే తీసిన ఫండస్ చిత్రాన్ని ఉపయోగించండి.",
        "रेटिना जाँच के लिए पहले से ली गई फंडस छवि का उपयोग करें।",
    ),
    "upload_jpg_png": (
        "Upload JPG or PNG image",
        "JPG లేదా PNG చిత్రాన్ని అప్‌లోడ్ చేయండి",
        "JPG या PNG छवि अपलोड करें",
    ),
    "capture_skin_image": (
        "Capture a skin lesion image",
        "చర్మ గాయం చిత్రాన్ని తీయండి",
        "त्वचा के घाव की तस्वीर लें",
    ),
    "image_selected": (
        "Image selected successfully.",
        "చిత్రం విజయవంతంగా ఎంపిక చేయబడింది.",
        "छवि सफलतापूर्वक चुनी गई।",
    ),
    "selected_image": (
        "Selected medical image",
        "ఎంపిక చేసిన వైద్య చిత్రం",
        "चुनी गई चिकित्सीय छवि",
    ),
    "patient_information": (
        "Patient Information",
        "రోగి వివరాలు",
        "रोगी की जानकारी",
    ),
    "age": ("Age", "వయస్సు", "आयु"),
    "sex": ("Sex", "లింగం", "लिंग"),
    "gender": ("Gender", "లింగం", "लिंग"),
    "gender_dataset": (
        "Gender (dataset category)",
        "లింగం (డేటాసెట్ వర్గం)",
        "लिंग (डेटासेट श्रेणी)",
    ),
    "male": ("Male", "పురుషుడు", "पुरुष"),
    "female": ("Female", "స్త్రీ", "महिला"),
    "diabetes_type": (
        "Diabetes Type",
        "మధుమేహం రకం",
        "मधुमेह का प्रकार",
    ),
    "diabetes_type_1": (
        "Type 1 Diabetes",
        "టైప్ 1 మధుమేహం",
        "टाइप 1 मधुमेह",
    ),
    "diabetes_type_2": (
        "Type 2 Diabetes",
        "టైప్ 2 మధుమేహం",
        "टाइप 2 मधुमेह",
    ),
    "diameter_1": (
        "Lesion Diameter 1",
        "చర్మ గాయం వ్యాసం 1",
        "त्वचा के घाव का व्यास 1",
    ),
    "diameter_2": (
        "Lesion Diameter 2",
        "చర్మ గాయం వ్యాసం 2",
        "त्वचा के घाव का व्यास 2",
    ),
    "measurement_guidance": (
        "Enter lesion measurements if known. Units must match the original PAD-UFES-20 dataset.",
        "చర్మ గాయం కొలతలు తెలిస్తే నమోదు చేయండి. కొలతల ప్రమాణాలు PAD-UFES-20 డేటాసెట్‌తో సరిపోవాలి.",
        "यदि घाव का माप ज्ञात हो तो दर्ज करें। इकाइयाँ PAD-UFES-20 डेटासेट के अनुसार होनी चाहिए।",
    ),
    "optional": ("Optional", "ఐచ్ఛికం", "वैकल्पिक"),
    "region": ("Body Region", "శరీర భాగం", "शरीर का भाग"),
    "region_question": (
        "Lesion Location",
        "చర్మ గాయం ఉన్న ప్రదేశం",
        "घाव का स्थान",
    ),
    "itch": ("Itching", "దురద", "खुजली"),
    "grew": ("Lesion Growth", "చర్మ గాయం పెరుగుదల", "घाव का बढ़ना"),
    "hurt": ("Pain", "నొప్పి", "दर्द"),
    "changed": ("Lesion Changes", "చర్మ గాయంలో మార్పులు", "घाव में बदलाव"),
    "bleed": ("Bleeding", "రక్తస్రావం", "रक्तस्राव"),
    "elevation": ("Elevation", "చర్మ గాయం ఉబ్బడం", "घाव का उभरा होना"),
    "skin_cancer_history": (
        "Previous Skin Cancer History",
        "గతంలో చర్మ క్యాన్సర్ ఉన్న చరిత్ర",
        "पहले त्वचा कैंसर होने का इतिहास",
    ),
    "itch_question": (
        "Does the lesion itch?",
        "చర్మ గాయం దగ్గర దురద ఉందా?",
        "क्या घाव में खुजली होती है?",
    ),
    "grew_question": (
        "Has the lesion grown?",
        "చర్మ గాయం పెరిగిందా?",
        "क्या घाव बढ़ा है?",
    ),
    "hurt_question": (
        "Does the lesion hurt?",
        "చర్మ గాయం వద్ద నొప్పి ఉందా?",
        "क्या घाव में दर्द होता है?",
    ),
    "changed_question": (
        "Has the lesion changed?",
        "చర్మ గాయంలో మార్పు వచ్చిందా?",
        "क्या घाव में बदलाव आया है?",
    ),
    "bleed_question": (
        "Does the lesion bleed?",
        "చర్మ గాయం నుండి రక్తం వస్తుందా?",
        "क्या घाव से खून निकलता है?",
    ),
    "elevation_question": (
        "Is the lesion elevated?",
        "చర్మ గాయం ఉబ్బుగా ఉందా?",
        "क्या घाव उभरा हुआ है?",
    ),
    "yes": ("Yes", "అవును", "हाँ"),
    "no": ("No", "కాదు", "नहीं"),
    "unknown": ("Unknown", "తెలియదు", "पता नहीं"),
    "unknown_not_sure": (
        "Unknown / Not Sure",
        "తెలియదు / ఖచ్చితంగా తెలియదు",
        "अज्ञात / निश्चित नहीं",
    ),
    "confirm_information": (
        "I confirm that the supplied information is accurate to the best of my knowledge.",
        "నేను అందించిన సమాచారం నాకు తెలిసినంతవరకు సరైనదని నిర్ధారిస్తున్నాను.",
        "मैं पुष्टि करता/करती हूँ कि दी गई जानकारी मेरी जानकारी के अनुसार सही है।",
    ),
    "confirm_required": (
        "Please confirm the supplied information before continuing.",
        "కొనసాగడానికి ఇచ్చిన వివరాలను నిర్ధారించండి.",
        "जारी रखने से पहले दी गई जानकारी की पुष्टि करें।",
    ),
    "analyze": (
        "Analyze Image",
        "చిత్రాన్ని విశ్లేషించండి",
        "छवि का विश्लेषण करें",
    ),
    "explain": (
        "Explain Prediction",
        "అంచనాను వివరించండి",
        "अनुमान की व्याख्या करें",
    ),
    "analyzing": (
        "Analyzing the medical image...",
        "వైద్య చిత్రాన్ని విశ్లేషిస్తోంది...",
        "चिकित्सीय छवि का विश्लेषण किया जा रहा है...",
    ),
    "image_required": (
        "Please upload or capture an image before analyzing.",
        "విశ్లేషణకు ముందు చిత్రాన్ని అప్‌లోడ్ చేయండి లేదా కెమెరాతో తీయండి.",
        "विश्लेषण से पहले छवि अपलोड करें या कैमरे से तस्वीर लें।",
    ),
    "result_heading": (
        "AI Screening Result",
        "AI పరీక్ష ఫలితం",
        "एआई जाँच परिणाम",
    ),
    "predicted_category": (
        "Model-Predicted Category",
        "AI అంచనా వేసిన వర్గం",
        "एआई द्वारा अनुमानित श्रेणी",
    ),
    "model_probability": (
        "Highest Model-Assigned Probability",
        "మోడల్ కేటాయించిన అత్యధిక సంభావ్యత",
        "मॉडल द्वारा निर्धारित उच्चतम संभाव्यता",
    ),
    "probability_warning": (
        "This is a model probability, not a confirmed probability of disease.",
        "ఇది మోడల్ లెక్కించిన సంభావ్యత మాత్రమే. వ్యాధి ఉన్నట్లు నిర్ధారించే సంభావ్యత కాదు.",
        "यह मॉडल द्वारा गणना की गई संभाव्यता है, बीमारी की पुष्टि की गई संभाव्यता नहीं।",
    ),
    "prediction_distribution": (
        "Prediction Distribution",
        "అంచనాల పంపిణీ",
        "अनुमानों का वितरण",
    ),
    "image_type_accepted": (
        "The image-type detector accepted the image for this screening.",
        "ఈ పరీక్షకు చిత్ర రకాన్ని గుర్తించే వ్యవస్థ చిత్రాన్ని అంగీకరించింది.",
        "छवि प्रकार पहचान प्रणाली ने इस जाँच के लिए छवि स्वीकार कर ली है।",
    ),
    "image_type_warning": (
        "Image-type acceptance does not guarantee image quality or medical suitability.",
        "చిత్ర రకం అంగీకరించబడినంత మాత్రాన చిత్రం నాణ్యమైనదని లేదా వైద్యపరంగా అనుకూలమైనదని కాదు.",
        "छवि का प्रकार स्वीकार होने का अर्थ यह नहीं कि उसकी गुणवत्ता या चिकित्सीय उपयुक्तता सुनिश्चित हो गई है।",
    ),
    "image_quality": (
        "Image Quality Assessment",
        "చిత్ర నాణ్యత అంచనా",
        "छवि गुणवत्ता का आकलन",
    ),
    "blur_score": (
        "Blur Score",
        "చిత్ర స్పష్టత స్కోరు",
        "छवि स्पष्टता स्कोर",
    ),
    "brightness": ("Brightness", "ప్రకాశం", "चमक"),
    "quality_passed": (
        "Basic image-quality checks passed.",
        "ప్రాథమిక చిత్ర నాణ్యత తనిఖీలు పూర్తయ్యాయి.",
        "प्रारंभिक छवि गुणवत्ता जाँच पूरी हुई।",
    ),
    "quality_blurry": (
        "Image may be blurry",
        "చిత్రం అస్పష్టంగా ఉండవచ్చు",
        "छवि धुंधली हो सकती है",
    ),
    "quality_dark": (
        "Image is too dark",
        "చిత్రం చాలా చీకటిగా ఉంది",
        "छवि बहुत अँधेरी है",
    ),
    "quality_bright": (
        "Image is too bright",
        "చిత్రం చాలా ప్రకాశవంతంగా ఉంది",
        "छवि बहुत अधिक चमकीली है",
    ),
    "quality_disclaimer": (
        "Experimental image-quality assessment. These checks are not clinically validated. A warning does not necessarily mean that the image is unsuitable for screening.",
        "ఇది ప్రయోగాత్మక చిత్ర నాణ్యత అంచనా మాత్రమే. ఈ తనిఖీలు వైద్యపరంగా ధృవీకరించబడలేదు. హెచ్చరిక వచ్చినంత మాత్రాన చిత్రం పరీక్షకు అనుకూలం కాదని నిర్ధారించలేము.",
        "यह प्रयोगात्मक छवि गुणवत्ता आकलन है। ये जाँच चिकित्सकीय रूप से सत्यापित नहीं हैं। चेतावनी आने का अर्थ यह नहीं कि छवि जाँच के लिए निश्चित रूप से अनुपयुक्त है।",
    ),
    "calibrated": (
        "Temperature scaling was applied to the model probabilities. Independent calibration validation is still required.",
        "మోడల్ సంభావ్యతలకు టెంపరేచర్ స్కేలింగ్ వర్తింపజేశారు. స్వతంత్ర కాలిబ్రేషన్ ధృవీకరణ ఇంకా అవసరం.",
        "मॉडल की संभाव्यताओं पर टेम्परेचर स्केलिंग लागू की गई है। स्वतंत्र कैलिब्रेशन सत्यापन अभी आवश्यक है।",
    ),
    "uncalibrated": (
        "The displayed probabilities are not temperature calibrated.",
        "చూపించిన సంభావ్యతలకు టెంపరేచర్ కాలిబ్రేషన్ చేయలేదు.",
        "दिखाई गई संभाव्यताओं का टेम्परेचर कैलिब्रेशन नहीं किया गया है।",
    ),
    "disclaimer": (
        "Experimental AI screening system. Not intended for medical diagnosis.",
        "ఇది ప్రయోగాత్మక AI పరీక్షా వ్యవస్థ మాత్రమే. వైద్య నిర్ధారణ కోసం ఉపయోగించరాదు.",
        "यह एक प्रयोगात्मक एआई जाँच प्रणाली है। चिकित्सीय निदान के लिए नहीं है।",
    ),
    "explanation_heading": (
        "Explain AI Prediction",
        "AI అంచనాను వివరించండి",
        "एआई अनुमान की व्याख्या",
    ),
    "explanation_description": (
        "Explore which image regions influenced the model's prediction and how the clinical information contributed.",
        "మోడల్ అంచనాపై ప్రభావం చూపిన చిత్ర భాగాలు మరియు రోగి వివరాల ప్రభావాన్ని తెలుసుకోండి.",
        "जानें कि छवि के किन भागों ने मॉडल के अनुमान को प्रभावित किया और रोगी की जानकारी का क्या योगदान रहा।",
    ),
    "explanation_results": (
        "AI Explanation Results",
        "AI వివరణ ఫలితాలు",
        "एआई व्याख्या के परिणाम",
    ),
    "visual_explanation": (
        "Visual Explanation — Grad-CAM",
        "దృశ్య వివరణ — గ్రాడ్-క్యామ్",
        "दृश्य व्याख्या — ग्रैड-कैम",
    ),
    "heatmap": (
        "Grad-CAM heatmap",
        "గ్రాడ్-క్యామ్ హీట్‌మ్యాప్",
        "ग्रैड-कैम हीटमैप",
    ),
    "gradcam_warning": (
        "Highlighted regions show where image features influenced the model's prediction. They are not confirmed medical abnormalities.",
        "హైలైట్ చేసిన భాగాలు మోడల్ అంచనాపై ప్రభావం చూపిన చిత్ర లక్షణాలను సూచిస్తాయి. అవి వైద్యపరంగా నిర్ధారించిన అసాధారణతలు కావు.",
        "हाइलाइट किए गए क्षेत्र वे छवि विशेषताएँ दिखाते हैं जिन्होंने मॉडल के अनुमान को प्रभावित किया। ये चिकित्सकीय रूप से पुष्टि की गई असामान्यताएँ नहीं हैं।",
    ),
    "clinical_contributions": (
        "Clinical Feature Contributions",
        "రోగి వివరాల ప్రభావం",
        "रोगी की जानकारी का योगदान",
    ),
    "exact_contributions": (
        "View Exact Clinical Contributions",
        "రోగి వివరాల ఖచ్చితమైన ప్రభావ విలువలను చూడండి",
        "योगदान के सटीक मान देखें",
    ),
    "attribution_warning": (
        "Attributions indicate contributions to a model class score relative to a reference input. They are not medical risk percentages.",
        "ఈ విలువలు ఒక సూచన ఇన్‌పుట్‌తో పోలిస్తే మోడల్ వర్గ స్కోరుపై లక్షణాల ప్రభావాన్ని సూచిస్తాయి. ఇవి వైద్యపరమైన ప్రమాద శాతాలు కావు.",
        "ये मान संदर्भ इनपुट की तुलना में मॉडल के वर्ग स्कोर पर विशेषताओं के योगदान को दर्शाते हैं। ये चिकित्सीय जोखिम के प्रतिशत नहीं हैं।",
    ),
    "understanding_explanation": (
        "Understanding the Explanation",
        "AI వివరణను అర్థం చేసుకోవడం",
        "एआई व्याख्या को समझना",
    ),
    "skin_model_description": (
        "The skin AI model combines a lesion photograph with patient information such as age, lesion measurements, symptoms and medical history.",
        "చర్మ AI మోడల్ చర్మ గాయం ఫోటోతో పాటు వయస్సు, కొలతలు, లక్షణాలు, వైద్య చరిత్రను ఉపయోగిస్తుంది.",
        "त्वचा एआई मॉडल घाव की तस्वीर, उम्र, माप, लक्षण और चिकित्सा इतिहास को मिलाकर उपयोग करता है।",
    ),
    "skin_explanation_description": (
        "Grad-CAM highlights image regions influencing the prediction. Integrated Gradients estimates how encoded patient information contributed to the predicted class score.",
        "గ్రాడ్-క్యామ్ అంచనాను ప్రభావితం చేసిన చిత్ర భాగాలను చూపిస్తుంది. ఇంటిగ్రేటెడ్ గ్రేడియెంట్స్ రోగి వివరాల ప్రభావాన్ని అంచనా వేస్తుంది.",
        "ग्रैड-कैम अनुमान में प्रभाव डालने वाले छवि क्षेत्रों को दिखाता है। इंटीग्रेटेड ग्रेडिएंट्स रोगी के विवरण के योगदान का अनुमान लगाता है।",
    ),
    "retinal_model_description": (
        "The retinal AI model combines a fundus photograph with age, sex and diabetes type to estimate a diabetic retinopathy grade.",
        "రెటీనా AI మోడల్ ఫండస్ చిత్రం, వయస్సు, లింగం మరియు మధుమేహం రకంతో రెటినోపతి గ్రేడ్‌ను అంచనా వేస్తుంది.",
        "रेटिना एआई मॉडल फंडस छवि, उम्र, लिंग और मधुमेह के प्रकार से रेटिनोपैथी ग्रेड का अनुमान लगाता है।",
    ),
    "retinal_explanation_description": (
        "Grad-CAM visualizes influential image regions, while clinical attribution shows how patient information contributed to the selected model class score.",
        "గ్రాడ్-క్యామ్ ప్రభావిత చిత్ర భాగాలను చూపుతుంది; క్లినికల్ అట్రిబ్యూషన్ రోగి వివరాల ప్రభావాన్ని సూచిస్తుంది.",
        "ग्रैड-कैम प्रभावशाली छवि क्षेत्र दिखाता है, जबकि क्लिनिकल एट्रिब्यूशन रोगी की जानकारी का योगदान बताता है।",
    ),
    "explanation_disclaimer": (
        "These visualizations explain model behavior only. They do not establish a diagnosis or medically verified findings.",
        "ఈ చిత్రాలు మోడల్ ప్రవర్తనను మాత్రమే వివరిస్తాయి. ఇవి వైద్య నిర్ధారణను లేదా ధృవీకరించిన వైద్య ఫలితాలను సూచించవు.",
        "ये दृश्य केवल मॉडल के व्यवहार की व्याख्या करते हैं। ये चिकित्सीय निदान या प्रमाणित निष्कर्ष नहीं हैं।",
    ),
    "analysis_timeout": (
        "The analysis request timed out.",
        "విశ్లేషణ అభ్యర్థనకు సమయం ముగిసింది.",
        "विश्लेषण अनुरोध का समय समाप्त हो गया।",
    ),
    "connection_error": (
        "Unable to connect to the FastAPI backend. Make sure it is running on port 8000.",
        "FastAPI బ్యాకెండ్‌కు కనెక్ట్ కాలేకపోయాం. పోర్ట్ 8000లో నడుస్తోందో చూడండి.",
        "FastAPI बैकएंड से कनेक्ट नहीं हो सका। पोर्ट 8000 पर चलने की जाँच करें।",
    ),
    "result_stale": (
        "The image or patient information has changed. Click Analyze Image again to generate an updated result.",
        "చిత్రం లేదా రోగి వివరాలు మారాయి. కొత్త ఫలితానికి మళ్లీ విశ్లేషించండి.",
        "छवि या रोगी जानकारी बदल गई है। नया परिणाम पाने के लिए फिर से विश्लेषण करें।",
    ),
    "analyze_first": (
        "Please analyze an image first.",
        "ముందుగా చిత్రాన్ని విశ్లేషించండి.",
        "पहले छवि का विश्लेषण करें।",
    ),
    "explaining": (
        "Generating Grad-CAM and clinical feature explanations...",
        "గ్రాడ్-క్యామ్ మరియు రోగి వివరాల ప్రభావాన్ని రూపొందిస్తోంది...",
        "ग्रैड-कैम और चिकित्सीय योगदान की व्याख्या तैयार की जा रही है...",
    ),
    "explanation_timeout": (
        "Explanation generation timed out.",
        "వివరణ రూపొందించడానికి సమయం ముగిసింది.",
        "व्याख्या तैयार करने का समय समाप्त हो गया।",
    ),
    "explanation_connection_error": (
        "Unable to connect to the explanation API.",
        "వివరణ APIకి కనెక్ట్ కాలేకపోయాం.",
        "व्याख्या API से कनेक्ट नहीं हो सका।",
    ),
    "explanation_mismatch": (
        "The explanation does not match the current screening result. Please analyze the image again.",
        "వివరణ ప్రస్తుత పరీక్ష ఫలితంతో సరిపోలడం లేదు. మళ్లీ విశ్లేషించండి.",
        "व्याख्या वर्तमान जाँच परिणाम से मेल नहीं खाती। फिर से विश्लेषण करें।",
    ),
    "heatmap_error": (
        "Unable to display the Grad-CAM image.",
        "గ్రాడ్-క్యామ్ చిత్రాన్ని చూపలేకపోయాం.",
        "ग्रैड-कैम छवि नहीं दिखाई जा सकी।",
    ),
    "heatmap_missing": (
        "The explanation API did not return a Grad-CAM image.",
        "వివరణ API గ్రాడ్-క్యామ్ చిత్రాన్ని ఇవ్వలేదు.",
        "व्याख्या API ने ग्रैड-कैम छवि नहीं लौटाई।",
    ),
    "contributions_missing": (
        "No clinical feature contributions were returned.",
        "రోగి వివరాల ప్రభావ విలువలు అందలేదు.",
        "चिकित्सीय विशेषताओं के योगदान नहीं मिले।",
    ),
    "backend_http": (
        "Backend returned HTTP",
        "బ్యాకెండ్ HTTP లోపం",
        "बैकएंड HTTP त्रुटि",
    ),
    "backend_non_json": (
        "The backend returned a non-JSON response.",
        "బ్యాకెండ్ సరైన JSON సమాధానాన్ని ఇవ్వలేదు.",
        "बैकएंड ने मान्य JSON प्रतिक्रिया नहीं दी।",
    ),
    "view_backend": (
        "View backend response",
        "బ్యాకెండ్ సమాధానం చూడండి",
        "बैकएंड प्रतिक्रिया देखें",
    ),
    "empty_server": (
        "Empty server response",
        "సర్వర్ సమాధానం ఖాళీగా ఉంది",
        "सर्वर की प्रतिक्रिया खाली है",
    ),
    "unknown_backend": (
        "Unknown backend error",
        "తెలియని బ్యాకెండ్ లోపం",
        "अज्ञात बैकएंड त्रुटि",
    ),
    "request_failed": (
        "The request could not be processed.",
        "అభ్యర్థనను ప్రాసెస్ చేయలేకపోయాం.",
        "अनुरोध संसाधित नहीं किया जा सका।",
    ),
    "view_details": (
        "View error details",
        "లోపం వివరాలు చూడండి",
        "त्रुटि विवरण देखें",
    ),
    "unexpected_backend": (
        "Unexpected backend error format.",
        "బ్యాకెండ్ లోపం ఆకృతి ఊహించనిది.",
        "बैकएंड त्रुटि का प्रारूप अप्रत्याशित है।",
    ),
    "unknown": ("Unknown", "తెలియదు", "अज्ञात"),
    "grade_0": ("Grade 0", "గ్రేడ్ 0", "ग्रेड 0"),
    "grade_1": ("Grade 1", "గ్రేడ్ 1", "ग्रेड 1"),
    "grade_2": ("Grade 2", "గ్రేడ్ 2", "ग्रेड 2"),
    "grade_3": ("Grade 3", "గ్రేడ్ 3", "ग्रेड 3"),
    "grade_4": ("Grade 4", "గ్రేడ్ 4", "ग्रेड 4"),
    "class_ACK": (
        "Actinic Keratosis",
        "ఆక్టినిక్ కెరటోసిస్",
        "एक्टिनिक केराटोसिस",
    ),
    "class_BCC": (
        "Basal Cell Carcinoma",
        "బేసల్ సెల్ కార్సినోమా",
        "बेसल सेल कार्सिनोमा",
    ),
    "class_MEL": ("Melanoma", "మెలనోమా", "मेलानोमा"),
    "class_NEV": (
        "Melanocytic Nevus",
        "మెలనోసైటిక్ నీవస్",
        "मेलानोसाइटिक नेवस",
    ),
    "class_SCC": (
        "Squamous Cell Carcinoma",
        "స్క్వామస్ సెల్ కార్సినోమా",
        "स्क्वैमस सेल कार्सिनोमा",
    ),
    "class_SEK": (
        "Seborrheic Keratosis",
        "సెబోరియిక్ కెరటోసిస్",
        "सेबोरिक केराटोसिस",
    ),
}

REGIONS = {
    "ABDOMEN": ("Abdomen", "పొట్ట", "पेट"),
    "ARM": ("Arm", "చేయి", "बाँह"),
    "BACK": ("Back", "వీపు", "पीठ"),
    "CHEST": ("Chest", "ఛాతీ", "छाती"),
    "EAR": ("Ear", "చెవి", "कान"),
    "FACE": ("Face", "ముఖం", "चेहरा"),
    "FOOT": ("Foot", "పాదం", "पैर"),
    "FOREARM": ("Forearm", "ముంజేయి", "अग्रबाहु"),
    "HAND": ("Hand", "అరచేయి", "हाथ"),
    "LIP": ("Lip", "పెదవి", "होंठ"),
    "NECK": ("Neck", "మెడ", "गर्दन"),
    "NOSE": ("Nose", "ముక్కు", "नाक"),
    "SCALP": ("Scalp", "తల చర్మం", "सिर की त्वचा"),
    "THIGH": ("Thigh", "తొడ", "जाँघ"),
}

# ==================================================
# DOCTOR CONSULTATION GUIDANCE
# ==================================================

TEXT.update({
    "doctor_guidance": (
        "Doctor Consultation Guidance",
        "వైద్యుడిని సంప్రదించడానికి సూచనలు",
        "डॉक्टर से परामर्श संबंधी मार्गदर्शन",
    ),

    "recommended_specialist": (
        "Recommended Specialist",
        "సంప్రదించాల్సిన వైద్య నిపుణుడు",
        "संबंधित विशेषज्ञ",
    ),

    "dermatologist": (
        "Dermatologist (Skin Specialist)",
        "చర్మ వైద్య నిపుణుడు",
        "त्वचा रोग विशेषज्ञ",
    ),

    "ophthalmologist": (
        "Ophthalmologist (Eye Specialist)",
        "నేత్ర వైద్య నిపుణుడు",
        "नेत्र रोग विशेषज्ञ",
    ),

    "skin_consultation": (
        "Consult a dermatologist for professional "
        "assessment of a skin lesion, especially if "
        "it is growing, changing, bleeding, or not healing. "
        "An AI prediction cannot confirm or rule out "
        "skin cancer.",

        "చర్మ గాయం పెరుగుతున్నా, మారుతున్నా, రక్తస్రావం "
        "అవుతున్నా లేదా మానకపోయినా చర్మ వైద్య నిపుణుడిని "
        "సంప్రదించండి. AI అంచనా ద్వారా చర్మ క్యాన్సర్‌ను "
        "నిర్ధారించడం లేదా పూర్తిగా తోసిపుచ్చడం సాధ్యం కాదు.",

        "यदि त्वचा का घाव बढ़ रहा है, बदल रहा है, "
        "उससे खून निकल रहा है या वह ठीक नहीं हो रहा, "
        "तो त्वचा रोग विशेषज्ञ से परामर्श करें। "
        "एआई का अनुमान त्वचा कैंसर की पुष्टि या "
        "उसे पूरी तरह खारिज नहीं कर सकता।",
    ),

    "retinal_consultation": (
        "People with diabetes should receive professional "
        "retinal examinations as advised by their eye-care "
        "professional. Even an AI prediction of Grade 0 "
        "cannot rule out retinal disease.",

        "మధుమేహం ఉన్నవారు నేత్ర వైద్య నిపుణుల సూచనల ప్రకారం "
        "క్రమం తప్పకుండా రెటీనా పరీక్షలు చేయించుకోవాలి. "
        "AI గ్రేడ్ 0 అని అంచనా వేసినా రెటీనా వ్యాధి లేదని "
        "నిర్ధారించలేము.",

        "मधुमेह वाले लोगों को नेत्र विशेषज्ञ की सलाह "
        "के अनुसार रेटिना की नियमित जाँच करानी चाहिए। "
        "एआई द्वारा ग्रेड 0 का अनुमान भी रेटिना की "
        "बीमारी को पूरी तरह खारिज नहीं करता।",
    ),

    "retinal_urgent_warning": (
        "Sudden loss of vision or a sudden major change "
        "in vision requires urgent medical assessment. "
        "Do not wait for an AI screening result.",

        "అకస్మాత్తుగా చూపు తగ్గినా లేదా చూపులో పెద్ద మార్పు "
        "వచ్చినా వెంటనే అత్యవసర వైద్య సహాయం పొందండి. "
        "AI పరీక్ష ఫలితం కోసం వేచి ఉండవద్దు.",

        "अचानक दृष्टि कम होने या दृष्टि में बड़ा बदलाव "
        "आने पर तुरंत चिकित्सा सहायता लें। "
        "एआई जाँच के परिणाम की प्रतीक्षा न करें।",
    ),

    "consultation_disclaimer": (
        "This is general educational guidance, not "
        "personalized medical advice. Consultation "
        "recommendations are not based on a clinically "
        "validated AI referral or urgency assessment.",

        "ఇవి సాధారణ విద్యాపరమైన సూచనలు మాత్రమే. "
        "వ్యక్తిగత వైద్య సలహా కాదు. ఈ సూచనలు వైద్యపరంగా "
        "ధృవీకరించిన AI రిఫరల్ లేదా అత్యవసరత అంచనాపై "
        "ఆధారపడి లేవు.",

        "यह सामान्य शैक्षणिक मार्गदर्शन है, "
        "व्यक्तिगत चिकित्सीय सलाह नहीं। ये सुझाव "
        "चिकित्सकीय रूप से सत्यापित एआई रेफरल या "
        "आपात स्थिति के आकलन पर आधारित नहीं हैं।",
    ),
})


TEXT.update(REGIONS)

# ==================================================
# USER-FRIENDLY SKIN LESION MEASUREMENTS
# ==================================================

TEXT.update({
    "diameter_1": (
        "Skin Spot Width (Horizontal Diameter)",
        "చర్మ మచ్చ వెడల్పు (అడ్డ కొలత)",
        "त्वचा के धब्बे की चौड़ाई (क्षैतिज माप)",
    ),

    "diameter_2": (
        "Skin Spot Height (Vertical Diameter)",
        "చర్మ మచ్చ ఎత్తు (నిలువు కొలత)",
        "त्वचा के धब्बे की ऊँचाई (ऊर्ध्वाधर माप)",
    ),

    "lesion_help": (
        "What is a skin lesion? A lesion is a spot, "
        "mole, patch, bump, or other area of skin "
        "that looks or feels different from normal skin. "
        "A lesion does not necessarily mean cancer.",

        "చర్మ గాయం లేదా మచ్చ అంటే ఏమిటి? "
        "సాధారణ చర్మంతో పోలిస్తే భిన్నంగా కనిపించే "
        "మచ్చ, పుట్టుమచ్చ, గడ్డ లేదా చర్మ భాగాన్ని "
        "చర్మ గాయం అంటారు. అది తప్పనిసరిగా "
        "క్యాన్సర్ అని అర్థం కాదు.",

        "त्वचा का घाव या धब्बा क्या है? "
        "त्वचा पर सामान्य से अलग दिखने वाला "
        "धब्बा, तिल, उभार या अन्य बदलाव "
        "त्वचा का घाव कहलाता है। "
        "इसका मतलब हमेशा कैंसर नहीं होता।",
    ),

    "measurement_guidance": (
        "If measured by a healthcare professional, "
        "enter the spot's horizontal and vertical "
        "diameters using the same units as the "
        "PAD-UFES-20 training data. "
        "If you do not know the measurements, "
        "leave both fields blank. Do not guess "
        "measurements from the photograph.",

        "వైద్య నిపుణుడు కొలిచినట్లయితే, "
        "PAD-UFES-20 శిక్షణ డేటాలో ఉపయోగించిన "
        "అదే కొలత ప్రమాణాలతో మచ్చ అడ్డ మరియు "
        "నిలువు కొలతలను నమోదు చేయండి. "
        "కొలతలు తెలియకపోతే రెండు ఖాళీలను "
        "వదిలేయండి. ఫోటో చూసి ఊహించవద్దు.",

        "यदि किसी स्वास्थ्य विशेषज्ञ ने मापा है, "
        "तो PAD-UFES-20 प्रशिक्षण डेटा की "
        "समान इकाइयों में धब्बे की क्षैतिज और "
        "ऊर्ध्वाधर माप दर्ज करें। "
        "माप ज्ञात न होने पर दोनों स्थान "
        "खाली छोड़ दें। तस्वीर देखकर "
        "अनुमान न लगाएँ।",
    ),
})

# ==================================================
# RETINAL GRADE EXPLANATIONS
# ==================================================

TEXT.update({
    "retinal_info_heading": (
        "What does this retinal grade mean?",
        "ఈ రెటీనా గ్రేడ్ అంటే ఏమిటి?",
        "इस रेटिना ग्रेड का क्या अर्थ है?",
    ),

    "retinal_info_note": (
        "This describes the grade predicted by the AI, "
        "not a confirmed diagnosis. The model may "
        "misclassify disease severity. An eye specialist "
        "must assess retinal health. Even Grade 0 "
        "does not rule out eye disease.",

        "ఇది AI అంచనా వేసిన గ్రేడ్ గురించిన సమాచారం "
        "మాత్రమే; నిర్ధారిత వైద్య ఫలితం కాదు. "
        "వ్యాధి తీవ్రతను మోడల్ తప్పుగా అంచనా వేయవచ్చు. "
        "నేత్ర వైద్య నిపుణుడి పరీక్ష అవసరం. "
        "గ్రేడ్ 0 వచ్చినా కంటి వ్యాధి లేదని నిర్ధారించలేము.",

        "यह एआई द्वारा अनुमानित ग्रेड की जानकारी है, "
        "पुष्टि किया गया निदान नहीं। मॉडल बीमारी की "
        "गंभीरता का गलत अनुमान लगा सकता है। "
        "नेत्र विशेषज्ञ से जाँच कराना आवश्यक है। "
        "ग्रेड 0 भी आँख की बीमारी को पूरी तरह "
        "खारिज नहीं करता।",
    ),

    "retinal_info_DR0_type": (
        "No apparent diabetic retinopathy",
        "డయాబెటిక్ రెటినోపతి స్పష్టమైన లక్షణాలు లేవు",
        "डायबिटिक रेटिनोपैथी के स्पष्ट संकेत नहीं",
    ),

    "retinal_info_DR0_description": (
        "This grade means no visible signs of diabetic "
        "retinopathy are identified under the standard "
        "clinical grading system. People with diabetes "
        "still need regular professional eye examinations.",

        "ప్రామాణిక వైద్య గ్రేడింగ్ ప్రకారం ఈ స్థాయిలో "
        "డయాబెటిక్ రెటినోపతి లక్షణాలు కనిపించవు. "
        "అయినా మధుమేహం ఉన్నవారు క్రమం తప్పకుండా "
        "కంటి పరీక్షలు చేయించుకోవాలి.",

        "मानक चिकित्सीय वर्गीकरण में इस ग्रेड पर "
        "डायबिटिक रेटिनोपैथी के स्पष्ट लक्षण नहीं "
        "दिखते। फिर भी मधुमेह वाले लोगों को "
        "नियमित नेत्र जाँच करानी चाहिए।",
    ),

    "retinal_info_DR1_type": (
        "Mild diabetic retinopathy",
        "స్వల్ప స్థాయి డయాబెటిక్ రెటినోపతి",
        "हल्की डायबिटिक रेटिनोपैथी",
    ),

    "retinal_info_DR1_description": (
        "This is an early stage in which tiny blood "
        "vessels in the retina show small changes. "
        "Vision may still appear normal.",

        "ఇది ప్రారంభ దశ. రెటీనాలోని చిన్న "
        "రక్తనాళాల్లో స్వల్ప మార్పులు కనిపించవచ్చు. "
        "ఈ దశలో చూపు సాధారణంగానే ఉండవచ్చు.",

        "यह शुरुआती अवस्था है जिसमें रेटिना की "
        "छोटी रक्त वाहिकाओं में बदलाव होते हैं। "
        "इस समय दृष्टि सामान्य भी रह सकती है।",
    ),

    "retinal_info_DR2_type": (
        "Moderate diabetic retinopathy",
        "మధ్యస్థ స్థాయి డయాబెటిక్ రెటినోపతి",
        "मध्यम डायबिटिक रेटिनोपैथी",
    ),

    "retinal_info_DR2_description": (
        "There are more changes in the retinal "
        "blood vessels than in the mild stage. "
        "An eye specialist should evaluate the "
        "condition and recommend appropriate follow-up.",

        "స్వల్ప దశతో పోలిస్తే రెటీనా రక్తనాళాల్లో "
        "ఎక్కువ మార్పులు ఉంటాయి. నేత్ర వైద్య నిపుణుడు "
        "పరీక్షించి తదుపరి సూచనలు ఇవ్వాలి.",

        "हल्की अवस्था की तुलना में रेटिना की "
        "रक्त वाहिकाओं में अधिक बदलाव होते हैं। "
        "आगे की जाँच और देखभाल के लिए नेत्र "
        "विशेषज्ञ से परामर्श लेना चाहिए।",
    ),

    "retinal_info_DR3_type": (
        "Severe diabetic retinopathy",
        "తీవ్ర స్థాయి డయాబెటిక్ రెటినోపతి",
        "गंभीर डायबिटिक रेटिनोपैथी",
    ),

    "retinal_info_DR3_description": (
        "This stage involves extensive changes "
        "in retinal blood vessels and a greater "
        "risk of progression. Professional "
        "eye assessment is important.",

        "ఈ దశలో రెటీనా రక్తనాళాల్లో తీవ్రమైన "
        "మార్పులు ఉంటాయి. వ్యాధి మరింత పెరిగే "
        "ప్రమాదం ఉంటుంది. నేత్ర వైద్య నిపుణుడి "
        "పరీక్ష ముఖ్యమైనది.",

        "इस अवस्था में रेटिना की रक्त वाहिकाओं "
        "में गंभीर बदलाव होते हैं और बीमारी "
        "बढ़ने का खतरा अधिक होता है। "
        "विशेषज्ञ द्वारा जाँच आवश्यक है।",
    ),

    "retinal_info_DR4_type": (
        "Proliferative diabetic retinopathy",
        "అధునాతన డయాబెటిక్ రెటినోపతి",
        "प्रोलिफेरेटिव डायबिटिक रेटिनोपैथी",
    ),

    "retinal_info_DR4_description": (
        "This advanced stage involves abnormal "
        "new blood-vessel growth in the retina. "
        "These vessels may bleed and threaten vision. "
        "Prompt specialist assessment is important.",

        "ఇది అధునాతన దశ. రెటీనాలో అసాధారణంగా "
        "కొత్త రక్తనాళాలు ఏర్పడతాయి. వాటి వల్ల "
        "రక్తస్రావం జరిగి చూపు దెబ్బతినవచ్చు. "
        "వీలైనంత త్వరగా నిపుణుడి పరీక్ష అవసరం.",

        "यह एक उन्नत अवस्था है जिसमें रेटिना "
        "में असामान्य नई रक्त वाहिकाएँ बनती हैं। "
        "इनसे रक्तस्राव हो सकता है और दृष्टि "
        "प्रभावित हो सकती है। शीघ्र विशेषज्ञ "
        "जाँच महत्वपूर्ण है।",
    ),
})

TRANSLATIONS = {
    language: {
        key: values[index]
        for key, values in TEXT.items()
    }
    for index, language in enumerate(LANGUAGES)
}

# =========================================================
# PLAIN-LANGUAGE SKIN CONDITION EXPLANATIONS
# =========================================================

SKIN_INFORMATION = {
    "English": {
        "skin_info_heading": "What does this condition mean?",
        "skin_info_category": "General medical classification",
        "skin_info_note": (
            "This describes the condition predicted by the AI, "
            "not a confirmed diagnosis. Even a predicted benign "
            "condition does not rule out skin cancer. "
            "A dermatologist must assess suspicious lesions."
        ),

        "skin_info_ACK_type": "Precancerous condition",
        "skin_info_ACK_description": (
            "A rough or scaly skin patch often caused by "
            "long-term sun exposure. Some cases can develop "
            "into squamous cell carcinoma."
        ),

        "skin_info_BCC_type": "Skin cancer",
        "skin_info_BCC_description": (
            "A type of skin cancer that often grows slowly. "
            "It may appear as a shiny bump or a sore "
            "that does not heal."
        ),

        "skin_info_MEL_type": "Skin cancer",
        "skin_info_MEL_description": (
            "Melanoma is a potentially serious skin cancer "
            "that develops from pigment-producing cells. "
            "It may appear as a new or changing mole."
        ),

        "skin_info_NEV_type": "Usually benign (non-cancerous)",
        "skin_info_NEV_description": (
            "A common mole made of pigment-producing cells. "
            "Most are harmless, but changing or unusual "
            "moles should be examined."
        ),

        "skin_info_SCC_type": "Skin cancer",
        "skin_info_SCC_description": (
            "A type of skin cancer that may appear as "
            "a rough growth, crusted bump, or "
            "a sore that does not heal."
        ),

        "skin_info_SEK_type": "Benign (non-cancerous)",
        "skin_info_SEK_description": (
            "A common non-cancerous skin growth that may "
            "look waxy, raised, or wart-like."
        ),
    },

    "తెలుగు": {
        "skin_info_heading": "ఈ చర్మ సమస్య అంటే ఏమిటి?",
        "skin_info_category": "సాధారణ వైద్య వర్గీకరణ",
        "skin_info_note": (
            "ఇది AI అంచనా వేసిన చర్మ సమస్య గురించిన "
            "సమాచారం మాత్రమే; నిర్ధారిత వైద్య ఫలితం కాదు. "
            "AI హానికరం కాని సమస్యగా అంచనా వేసినా "
            "చర్మ క్యాన్సర్ లేదని నిర్ధారించలేము. "
            "అనుమానాస్పద చర్మ గాయాలను చర్మ వైద్య నిపుణుడు "
            "పరీక్షించాలి."
        ),

        "skin_info_ACK_type": "క్యాన్సర్‌గా మారే అవకాశం ఉన్న సమస్య",
        "skin_info_ACK_description": (
            "ఎక్కువ కాలం సూర్యరశ్మి ప్రభావం వల్ల "
            "చర్మంపై ఏర్పడే గరుకైన లేదా పొలుసులాంటి మచ్చ. "
            "కొన్ని సందర్భాల్లో ఇది స్క్వామస్ సెల్ "
            "కార్సినోమాగా మారవచ్చు."
        ),

        "skin_info_BCC_type": "చర్మ క్యాన్సర్",
        "skin_info_BCC_description": (
            "సాధారణంగా నెమ్మదిగా పెరిగే ఒక రకమైన "
            "చర్మ క్యాన్సర్. మెరుస్తున్న చిన్న గడ్డగా "
            "లేదా మానని పుండుగా కనిపించవచ్చు."
        ),

        "skin_info_MEL_type": "చర్మ క్యాన్సర్",
        "skin_info_MEL_description": (
            "చర్మానికి రంగును ఇచ్చే కణాల నుండి "
            "ఏర్పడే తీవ్రమైన చర్మ క్యాన్సర్ రకం. "
            "కొత్తగా వచ్చిన లేదా మారుతున్న పుట్టుమచ్చలా "
            "కనిపించవచ్చు."
        ),

        "skin_info_NEV_type": "సాధారణంగా క్యాన్సర్ కాని పుట్టుమచ్చ",
        "skin_info_NEV_description": (
            "చర్మానికి రంగును ఇచ్చే కణాల వల్ల ఏర్పడే "
            "సాధారణ పుట్టుమచ్చ. చాలా వరకు హానికరం కావు. "
            "అయితే మారుతున్న లేదా అసాధారణ పుట్టుమచ్చలను "
            "వైద్యుడు పరీక్షించాలి."
        ),

        "skin_info_SCC_type": "చర్మ క్యాన్సర్",
        "skin_info_SCC_description": (
            "ఒక రకమైన చర్మ క్యాన్సర్. గరుకైన పెరుగుదలగా, "
            "పొర ఏర్పడిన గడ్డగా లేదా మానని పుండుగా "
            "కనిపించవచ్చు."
        ),

        "skin_info_SEK_type": "క్యాన్సర్ కాని చర్మ పెరుగుదల",
        "skin_info_SEK_description": (
            "సాధారణంగా హానికరం కాని చర్మ పెరుగుదల. "
            "మైనంలా, పైకి ఉబ్బినట్లు లేదా పులిపిరిలా "
            "కనిపించవచ్చు."
        ),
    },

    "हिन्दी": {
        "skin_info_heading": "इस त्वचा की स्थिति का क्या अर्थ है?",
        "skin_info_category": "सामान्य चिकित्सीय वर्गीकरण",
        "skin_info_note": (
            "यह एआई द्वारा अनुमानित स्थिति की जानकारी है, "
            "पुष्टि किया गया चिकित्सीय निदान नहीं। "
            "एआई द्वारा सामान्य या गैर-कैंसर स्थिति "
            "बताए जाने पर भी त्वचा कैंसर को पूरी तरह "
            "खारिज नहीं किया जा सकता। संदिग्ध घाव की "
            "जाँच त्वचा रोग विशेषज्ञ से कराएँ।"
        ),

        "skin_info_ACK_type": "कैंसर बनने की संभावना वाली स्थिति",
        "skin_info_ACK_description": (
            "लंबे समय तक धूप में रहने से त्वचा पर "
            "बनने वाला खुरदरा या पपड़ीदार धब्बा। "
            "कुछ मामलों में यह स्क्वैमस सेल "
            "कार्सिनोमा में बदल सकता है।"
        ),

        "skin_info_BCC_type": "त्वचा कैंसर",
        "skin_info_BCC_description": (
            "एक प्रकार का त्वचा कैंसर जो अक्सर "
            "धीरे-धीरे बढ़ता है। यह चमकदार उभार "
            "या न भरने वाले घाव जैसा दिख सकता है।"
        ),

        "skin_info_MEL_type": "त्वचा कैंसर",
        "skin_info_MEL_description": (
            "मेलानोमा त्वचा को रंग देने वाली कोशिकाओं "
            "से बनने वाला संभावित रूप से गंभीर कैंसर है। "
            "यह नए या बदलते तिल जैसा दिख सकता है।"
        ),

        "skin_info_NEV_type": "आमतौर पर गैर-कैंसर वाला तिल",
        "skin_info_NEV_description": (
            "रंग बनाने वाली त्वचा कोशिकाओं से "
            "बनने वाला सामान्य तिल। अधिकांश तिल "
            "हानिरहित होते हैं, लेकिन बदलते या "
            "असामान्य तिल की जाँच करानी चाहिए।"
        ),

        "skin_info_SCC_type": "त्वचा कैंसर",
        "skin_info_SCC_description": (
            "एक प्रकार का त्वचा कैंसर जो खुरदरी "
            "गाँठ, पपड़ीदार उभार या न भरने वाले "
            "घाव के रूप में दिखाई दे सकता है।"
        ),

        "skin_info_SEK_type": "गैर-कैंसर वाली त्वचा की वृद्धि",
        "skin_info_SEK_description": (
            "त्वचा पर होने वाली एक सामान्य, "
            "गैर-कैंसर वाली वृद्धि जो मोम जैसी, "
            "उभरी हुई या मस्से जैसी दिख सकती है।"
        ),
    },
}

for language_name, messages in SKIN_INFORMATION.items():
    TRANSLATIONS[language_name].update(messages)


def translate(key, language="English"):
    english = TRANSLATIONS["English"]
    selected = TRANSLATIONS.get(language, english)
    return selected.get(key, english.get(key, key))
