import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_pdf(filename="Final_Documentation.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=50)
    Story = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    styles.add(ParagraphStyle(name='Justify', alignment=0, spaceAfter=10, fontSize=11, leading=14))
    styles.add(ParagraphStyle(name='Heading1Custom', parent=styles['Heading1'], spaceAfter=14, textColor=colors.HexColor("#2C3E50")))
    styles.add(ParagraphStyle(name='Heading2Custom', parent=styles['Heading2'], spaceBefore=14, spaceAfter=10, textColor=colors.HexColor("#2980B9")))
    
    # Title
    Story.append(Paragraph("Water Quality Index (WQI) Prediction Pipeline", styles['Heading1Custom']))
    Story.append(Paragraph("Final Documentation", styles['Heading2Custom']))
    Story.append(Spacer(1, 12))
    
    # 1. Introduction
    Story.append(Paragraph("1. Introduction", styles['Heading2Custom']))
    text = ("This document outlines the final methodology and machine learning pipeline developed to predict the Water "
            "Quality Index (WQI) Suitability Class for the Sibalom River. By leveraging 6 years of historical data from the "
            "Jalaur River System (JRS-WQMA), we utilized Transfer Learning and Synthetic Minority Over-sampling "
            "Technique (SMOTE) to build a highly accurate machine learning model capable of predicting water quality based "
            "on six critical parameters.")
    Story.append(Paragraph(text, styles['Justify']))
    
    # 2. Statement of the Problem
    Story.append(Paragraph("2. Statement of the Problem", styles['Heading2Custom']))
    text = ("The Sibalom River currently lacks continuous water quality monitoring. The core problem is how to accurately "
            "and efficiently determine the Water Quality Index (WQI) Suitability Class of the river using machine learning. "
            "Initially, the goal was to bypass laboratory testing by only using field-deployable meters (pH, DO, Temperature). "
            "However, mathematical analysis proved that bacterial contamination (Fecal Coliform) is the primary driver of "
            "'High Risk' classifications in the region, and cannot be predicted accurately using only pH and Temperature. "
            "Therefore, the problem shifted to building an optimized ML model that utilizes all 6 parameters (including lab "
            "tests) to accurately classify water quality despite the severe class imbalance (97% of local rivers being High "
            "Risk).")
    Story.append(Paragraph(text, styles['Justify']))
    
    # 3. Pipeline Flowchart & Methodology
    Story.append(Paragraph("3. Pipeline Flowchart & Methodology", styles['Heading2Custom']))
    text = ("The end-to-end pipeline operates in the following sequence:<br/>"
            "<b>Step 1:</b> Data Collection (Raw PDF extraction to CSV)<br/>"
            "<b>Step 2:</b> Preprocessing (KNN Imputation & Isolation Forest Outlier Removal)<br/>"
            "<b>Step 3:</b> Feature Engineering (Calculation of DO/Temp Ratio and pH Deviation)<br/>"
            "<b>Step 4:</b> WQI Computation (Using DENR DAO 2016-08 formula)<br/>"
            "<b>Step 5:</b> Classification (Excellent, Good, Fair, Poor, Very Poor, High Risk)<br/>"
            "<b>Step 6:</b> Dataset Balancing (SMOTE to generate minority class synthetic data)<br/>"
            "<b>Step 7:</b> ML Model Training (Grid Search CV for optimal hyperparameters)<br/>"
            "<b>Step 8:</b> Deployment & Simulation (Predicting Sibalom River quality)")
    Story.append(Paragraph(text, styles['Justify']))
    
    # 4. Machine Learning Models Comparative Table
    Story.append(Paragraph("4. Machine Learning Models Comparative Table", styles['Heading2Custom']))
    data = [
        ['Algorithm', 'Accuracy', 'F1-Score', 'Description'],
        ['MLP (Neural Net)', '99.25%', '99.20%', Paragraph('Multi-layer perceptron. Ultimate winner. Identifies minority classes perfectly.', styles['Normal'])],
        ['XGBoost', '98.50%', '98.57%', Paragraph('Gradient boosting. Very strong performer, handled complex relationships well.', styles['Normal'])],
        ['Random Forest', '98.50%', '98.07%', Paragraph('Ensemble of decision trees. Fast, but struggled slightly with the rarest class.', styles['Normal'])],
        ['SVM', '93.98%', '94.35%', Paragraph('Support Vector Machine. Failed to identify minority classes on the test set.', styles['Normal'])]
    ]
    t = Table(data, colWidths=[100, 60, 60, 240])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4C72B0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (3, 1), (3, -1), 'LEFT'),
    ]))
    Story.append(t)
    Story.append(Spacer(1, 10))
    
    Story.append(PageBreak())
    
    # 5. Machine Learning to Use
    Story.append(Paragraph("5. Machine Learning Algorithm to Use: Multilayer Perceptron (MLP)", styles['Heading2Custom']))
    text = ("The MLP (Neural Network) algorithm will be utilized for the final deployment. It achieved a near-perfect accuracy "
            "of 99.25% and was the only algorithm capable of perfectly identifying the 'Poor' and 'Very Poor' minority classes "
            "in the holdout test set without overfitting. As a neural network model, MLP is exceptionally reliable for finding "
            "deeply hidden, non-linear chemical and biological patterns in environmental data.")
    Story.append(Paragraph(text, styles['Justify']))
    
    # 6. Evaluation Output
    Story.append(Paragraph("6. Evaluation Output", styles['Heading2Custom']))
    text = ("The MLP model was evaluated on a SMOTE-balanced training set (80%), and then tested against the true "
            "distribution of the remaining 20% holdout set. The model correctly classified 100% of 'High Risk' samples, 100% "
            "of 'Poor' samples, and 100% of 'Very Poor' samples, proving its robustness against the severe 97% class "
            "imbalance of the original Jalaur river dataset. The resulting F1-Score of 99.20% guarantees extremely high "
            "reliability for field deployment.")
    Story.append(Paragraph(text, styles['Justify']))
    
    # 7. Flow of the Testing Process
    Story.append(Paragraph("7. Flow of the Testing Process", styles['Heading2Custom']))
    text = ("The physical testing and deployment process follows these steps:<br/>"
            "1. Sample Collection: Water samples are collected from the Sibalom River.<br/>"
            "2. Field Testing: Portable meters are used on-site to measure pH, DO, and Temperature.<br/>"
            "3. Lab Testing: The sample is sent to a laboratory to measure BOD, TSS, and Fecal Coliform.<br/>"
            "4. Data Entry: The user opens the Web Dashboard (deployed via Vercel) and inputs the 6 parameters.<br/>"
            "5. Automated Engineering: The application automatically calculates the DO/Temp Ratio and pH Deviation.<br/>"
            "6. ML Inference: The MLP (Neural Network) model processes the 8 features and outputs an instant WQI "
            "Suitability Classification (e.g., 'Very Poor' or 'High Risk').")
    Story.append(Paragraph(text, styles['Justify']))
    
    # 8. Glossary
    Story.append(Paragraph("8. Glossary of Machine Learning Concepts", styles['Heading2Custom']))
    glossary = [
        ("Transfer Learning", "A machine learning technique where a model trained on one task or dataset (e.g., Jalaur River) is repurposed or applied to a different but related task (e.g., Sibalom River). This is crucial when the target river lacks historical training data."),
        ("Preprocessing", "The fundamental step of cleaning and organizing raw data before feeding it into a machine learning model. This includes handling missing values, removing anomalies, and scaling numbers so the algorithms can process them efficiently."),
        ("KNN Imputation", "K-Nearest Neighbors (KNN) Imputation is an algorithm used to fill in missing data points (like a missing pH reading). It looks at the 'k' most similar data rows (neighbors) and averages their values to estimate and replace the missing number."),
        ("Isolation Forest Outlier Removal", "An anomaly detection algorithm that builds random decision trees to isolate individual data points. Normal data points require many splits to be isolated, whereas extreme outliers are isolated very quickly. We use this to remove faulty sensor readings or mathematically impossible data spikes."),
        ("Dataset Balancing (SMOTE)", "Synthetic Minority Over-sampling Technique (SMOTE) is used to balance uneven datasets. Since 97% of our river data was 'High Risk', the model would normally just guess 'High Risk' every time. SMOTE mathematically generates fake (but highly realistic) synthetic data points for the rare classes (like 'Good' or 'Poor') so the ML model can learn exactly what clean water looks like."),
        ("Classification", "A type of machine learning task where the goal is to predict a discrete category or label for a given input. In this study, the model classifies water into categories like 'Poor', 'Very Poor', or 'High Risk'."),
        ("Training & Validation", "Training is the process where the ML algorithm 'studies' the Jalaur dataset to learn the hidden mathematical relationships between chemicals and water quality. Validation is the process of testing the model on a hidden 'holdout' set of data it has never seen before to prove that it can accurately predict real-world scenarios."),
        ("Random Forest (RF)", "An ensemble learning algorithm that builds hundreds of different 'Decision Trees'. Each tree makes its own prediction based on a random subset of the data, and the final prediction is decided by a majority vote. It is highly resistant to overfitting and was our most accurate model."),
        ("XGBoost", "Extreme Gradient Boosting is an advanced algorithm that also builds decision trees, but it builds them sequentially. Each new tree specifically tries to correct the errors made by the previous trees, resulting in a highly optimized and powerful predictive model."),
        ("MLP (Multilayer Perceptron)", "A type of Artificial Neural Network inspired by the human brain. It consists of multiple layers of interconnected 'neurons' that pass data through mathematical activation functions. It is excellent at finding deeply hidden, non-linear patterns in complex data."),
        ("SVM (Support Vector Machine)", "An algorithm that attempts to find the optimal mathematical 'line' or 'hyperplane' in multi-dimensional space that perfectly separates different classes of data. While powerful, it struggled to separate the highly imbalanced classes in our specific water quality dataset.")
    ]
    for term, definition in glossary:
        Story.append(Paragraph(f"<b>{term}:</b> {definition}", styles['Justify']))
        
    Story.append(PageBreak())
    
    # 9. Student Research Guide
    Story.append(Paragraph("9. Student Research Guide: Core Concepts to Master", styles['Heading2Custom']))
    text = ("To fully understand and defend this project, students should dive deeper into the following core concepts. "
            "Mastering these topics provides a complete grasp of both the environmental science and the advanced machine "
            "learning techniques used.")
    Story.append(Paragraph(text, styles['Justify']))
    
    guide = [
        ("Transfer Learning & Domain Adaptation", "What to research: How machine learning models learn patterns in one domain (Jalaur River) and apply them to a different, related domain (Sibalom River).<br/>Why it matters: This is the core justification of the entire study. You need to explain why it is scientifically valid to train a model on one river and test it on another."),
        ("Dealing with Imbalanced Data: The SMOTE Algorithm", "What to research: Synthetic Minority Over-sampling Technique (SMOTE). How does it use mathematics (K-Nearest Neighbors) to generate fake but realistic data points?<br/>Why it matters: 97% of your original data was 'High Risk'. Without SMOTE, the model would have failed. Understanding how SMOTE saved the dataset is critical for your methodology defense."),
        ("Ensemble Learning: Random Forest & XGBoost", "What to research: What is a Decision Tree? What is Ensemble Learning? How does Random Forest build hundreds of independent trees and take a majority vote? How does XGBoost build sequential trees that learn from each other's mistakes?<br/>Why it matters: Random Forest was the winning model (99.25% accuracy). You must be able to explain exactly how it makes its decisions and why it outperformed neural networks (MLP)."),
        ("Anomaly Detection: Isolation Forest", "What to research: How does Isolation Forest detect anomalies without needing a labeled dataset? How does it isolate extreme data points faster than normal data points?<br/>Why it matters: You used this to clean the raw DENR data and remove faulty sensor readings or impossible chemical spikes before training."),
        ("Data Imputation: K-Nearest Neighbors (KNN)", "What to research: How does the KNN algorithm calculate Euclidean distance to find the most similar data points?<br/>Why it matters: When the DENR PDF data had blank/missing values for pH or DO, you didn't just delete the row or use the average. You used KNN to mathematically estimate what the missing value should be based on its closest neighbors."),
        ("The Mathematics of Feature Engineering", "What to research: Pearson Correlation and thermodynamic relationships in water (e.g., why does Dissolved Oxygen capacity drop when Temperature rises?).<br/>Why it matters: You explicitly engineered two new features: DO_Temp_Ratio and pH_Deviation. You need to explain why providing these explicit mathematical relationships helped the ML model learn faster."),
        ("Water Quality Index (WQI) Formulas", "What to research: The Weighted Arithmetic Water Quality Index method and the DENR DAO 2016-08 standards.<br/>Why it matters: You need to understand how the raw lab numbers (like 140 MPN Coliform) were converted into the WQI Score that determined the final Suitability Class (Excellent to High Risk)."),
        ("Evaluation Metrics Beyond Accuracy", "What to research: Why is plain Accuracy dangerous when you have an imbalanced dataset? What are Precision, Recall, and the F1-Score?<br/>Why it matters: If a model simply guesses 'High Risk' every time on a dataset that is 97% High Risk, it will get 97% Accuracy but is utterly useless. You must explain why the F1-Score is the true measure of your model's success.")
    ]
    for term, definition in guide:
        Story.append(Paragraph(f"<b>{term}</b><br/>{definition}", styles['Justify']))
        
    Story.append(PageBreak())
    
    # 10. Mathematical Framework
    Story.append(Paragraph("10. Mathematical & Computational Chemistry Framework", styles['Heading2Custom']))
    text = ("As a study deeply rooted in computational chemistry and data science, several explicit mathematical and "
            "statistical computations were applied to transform raw chemical concentrations into a predictive machine learning "
            "framework. The following mathematical computations were utilized:")
    Story.append(Paragraph(text, styles['Justify']))
    
    def make_fraction(left_side, numerator, denominator):
        eq_style = ParagraphStyle('EqStyle', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=12, alignment=1)
        left_style = ParagraphStyle('LeftStyle', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=12, alignment=2)
        
        t = Table([
            [Paragraph(left_side, left_style), Paragraph(numerator, eq_style)],
            ['', Paragraph(denominator, eq_style)]
        ], colWidths=[120, 120])
        
        t.setStyle(TableStyle([
            ('LINEABOVE', (1, 1), (1, 1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
            ('SPAN', (0, 0), (0, 1)),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        return t

    math_guide = [
        ("1. Quality Rating Scale (q<sub>i</sub>)", 
         "Each chemical parameter was mathematically normalized into a standard rating scale using the formula:<br/>",
         make_fraction("q<sub>i</sub> = 100 &times;", "V<sub>i</sub> - V<sub>ideal</sub>", "S<sub>i</sub> - V<sub>ideal</sub>"),
         "This transforms raw concentrations (V<sub>i</sub>) against chemical standards (S<sub>i</sub>) and ideal values (V<sub>ideal</sub>) into a unitless metric."),
        
        ("2. Weighted Arithmetic Water Quality Index (WQI)", 
         "The aggregation of multiple chemical quality ratings into a single, definitive index score. The formula used was:<br/>",
         make_fraction("WQI =", "&Sigma; (q<sub>i</sub> &times; w<sub>i</sub>)", "&Sigma; w<sub>i</sub>"),
         "where 'w<sub>i</sub>' represents the mathematical weight or importance of each chemical parameter."),
        
        ("3. Information Entropy Weighting", 
         "Rather than subjectively assigning weights, Information Theory (Entropy) mathematics was used to calculate "
         "objective weights for each chemical parameter. This statistical computation measures the variance and dispersion "
         "of a chemical's concentration across the dataset to determine its true informative value.",
         None, ""),
        
        ("4. Pearson Correlation Coefficient", 
         "A mathematical computation used to measure the linear correlation between individual chemical variables and the final WQI. "
         "This statistical analysis helped refine the final Combined Weights used in the feature engineering process.",
         None, ""),
        
        ("5. Euclidean Distance (KNN Imputation)", 
         "To handle missing data (e.g., a missing DO reading), the K-Nearest Neighbors algorithm utilized the Euclidean Distance formula "
         "in multi-dimensional chemical space to find the most chemically similar river samples and average their values:<br/><br/>"
         "<font face='Helvetica-Oblique' size='12'>&nbsp;&nbsp;d(p, q) = &radic;&Sigma;(p<sub>i</sub> - q<sub>i</sub>)<sup>2</sup></font><br/><br/>",
         None, ""),
        
        ("6. Thermodynamic Ratios (DO/Temp Ratio)", 
         "An engineered computation that explicitly models the inverse non-linear relationship between water temperature and the physical solubility "
         "of oxygen. By dividing Dissolved Oxygen by Temperature, we fed the ML model a direct thermodynamic constraint.",
         None, ""),
        
        ("7. pH Deviation", 
         "A simple but critical mathematical absolute distance function:<br/><br/>"
         "<font face='Helvetica-Oblique' size='12'>&nbsp;&nbsp;&Delta;pH = |pH - 7.0|</font><br/><br/>"
         "Since pH is logarithmic, modeling the absolute deviation from neutral proved more mathematically useful for the machine learning algorithms than raw pH values alone.",
         None, "")
    ]
    for term, text1, eq_table, text2 in math_guide:
        Story.append(Paragraph(f"<b>{term}</b><br/>{text1}", styles['Justify']))
        if eq_table:
            Story.append(eq_table)
            Story.append(Spacer(1, 10))
        if text2:
            Story.append(Paragraph(text2, styles['Justify']))
        
    doc.build(Story)
    print("PDF generated successfully.")

if __name__ == "__main__":
    create_pdf()
