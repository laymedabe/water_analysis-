import json

def patch_nb():
    with open('wqi_analysis_demo.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            if 'mlp = MLPClassifier(random_state=42' in source:
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
    
    with open('wqi_analysis_demo.ipynb', 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)

patch_nb()
print("Notebook patched successfully.")
