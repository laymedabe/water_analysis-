"""
patch_nb_grid.py
This script automatically modifies our Jupyter Notebook (`wqi_analysis_demo.ipynb`).
It finds the part of the notebook that trains a Neural Network (a brain-like AI) 
and replaces it with a smarter version that tests hundreds of different 
settings to automatically find the best "brain structure" for our AI.
"""

import json

def patch_nb():
    """
    Opens the notebook file, finds the AI code block, 
    and replaces it with the new code that tests different settings.
    """
    # 1. Open the notebook so we can read it
    with open('wqi_analysis_demo.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    # 2. Look through all the blocks (cells) in the notebook
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            
            # 3. Find the exact code block we want to replace
            if 'mlp = MLPClassifier(random_state=42' in source:
                
                # 4. Swap the old code for the smarter "Grid Search" code
                cell['source'] = [
                    "print('Grid Search with 5-Fold Stratified CV on Training Set...')\n",
                    "mlp = MLPClassifier(random_state=42, max_iter=1000, early_stopping=True, validation_fraction=0.15)\n",
                    "param_grid = {\n",
                    "    'hidden_layer_sizes': [(64, 32), (128, 64), (100, 50, 25)],\n",
                    "    'activation': ['relu', 'tanh'],\n",
                    "    'alpha': [0.0001, 0.001, 0.01],\n",
                    "    'learning_rate': ['constant', 'adaptive']\n",
                    "}\n",
                    "grid = GridSearchCV(mlp, param_grid, cv=5, scoring='f1_weighted', n_jobs=1, verbose=1)\n",
                    "grid.fit(X_train_resampled, y_train_resampled)\n",
                    "print(f'Best Params: {grid.best_params_}')\n",
                    "best_mlp = grid.best_estimator_\n",
                    "y_pred = best_mlp.predict(X_test)\n",
                    "\n",
                    "print(f\"MLP Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%\")\n",
                    "print(f\"MLP F1-Score: {f1_score(y_test, y_pred, average='weighted')*100:.2f}%\\n\")\n",
                    "print(classification_report(y_test, y_pred, target_names=le.classes_))\n",
                    "\n",
                    "ConfusionMatrixDisplay.from_predictions(y_test, y_pred, display_labels=le.classes_, cmap='Blues')\n",
                    "plt.title('MLP Confusion Matrix (GridSearchCV)')\n",
                    "plt.show()\n"
                ]
    
    # 5. Save the updated notebook back to the computer
    with open('wqi_analysis_demo.ipynb', 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)

# Run the function
patch_nb()
print("Notebook patched successfully.")
