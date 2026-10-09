"""
patch_nb_desc.py
This script automatically adds a new text block to the very bottom of 
our Jupyter Notebook (`wqi_analysis_demo.ipynb`).
It includes simple, easy-to-understand explanations of how we score 
the AI (using things like Accuracy and F1-Score)
"""

import json

def append_descriptions():
    """
    Opens the notebook, creates a new text block explaining the AI scores,
    and sticks it at the very end of the file.
    """
    # 1. Open the notebook so we can read it
    with open('wqi_analysis_demo.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    # 2. Write down what we want the new text block to say
    explanations = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "### Evaluation Metric Explanations\n",
                "\n",
                "**1. Accuracy**\n",
                "* **What it means:** The percentage of water samples that the model predicted correctly out of all samples.\n",
                "* **Context:** For instance, if MLP Accuracy is 96.69%, it means the model correctly classified approximately 97 out of every 100 samples into the exact DENR Suitability Class.\n",
                "\n",
                "**2. Precision**\n",
                "* **What it means:** When the model predicted a specific class (e.g., 'Good'), how many of those predictions were actually correct?\n",
                "* **Context:** A precision of 1.00 for 'High Risk' means that every single time the model threw a 'High Risk' warning, it was guaranteed to be accurate with zero false alarms.\n",
                "\n",
                "**3. Recall (Sensitivity)**\n",
                "* **What it means:** Out of all the actual samples of a specific class (e.g., all actual 'Excellent' rivers), how many did the model successfully find?\n",
                "* **Context:** If the recall for 'Good' is 1.00, it means the model successfully identified 100% of the truly Good water samples without missing a single one.\n",
                "\n",
                "**4. F1-Score**\n",
                "* **What it means:** The harmonic mean of Precision and Recall. It is the absolute most important metric for imbalanced datasets.\n",
                "* **Context:** Because our original dataset was 97% High Risk, plain Accuracy is misleading. A model could just guess 'High Risk' every time and get 97% Accuracy while being completely useless for clean water. The F1-Score penalizes the model for missing minority classes. An F1-Score of 97.56% proves the model has legitimately learned the complex chemical signatures of every class natively.\n",
                "\n",
                "**5. Confusion Matrix**\n",
                "* **What it means:** A heatmap showing exactly where the model got confused. The diagonal line (top-left to bottom-right) represents correct predictions. Any numbers outside the diagonal are errors.\n",
                "* **Context:** If the model predicted 'Fair' when the actual water was 'Good', you will see a number in the corresponding box off the main diagonal. This allows us to visually verify that the model rarely makes critical errors (e.g., confusing 'Excellent' with 'High Risk')."
            ]
        }
    ]
    
    # 3. Stick this new block at the end of the notebook
    nb['cells'].extend(explanations)
    
    # 4. Save the updated notebook back to the computer
    with open('wqi_analysis_demo.ipynb', 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)

# Run the function
append_descriptions()
print("Descriptions appended to Notebook successfully.")

