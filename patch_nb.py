import json

def patch_notebook():
    with open('wqi_analysis_demo.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    seed_code = """# Inject synthetic Class A and AA (Excellent/Good) samples 
# to allow the Neural Network and SMOTE to map the entire decision space.
print("\\n[2d] Seeding dataset with synthetic Excellent, Good, and Fair baseline samples...")
np.random.seed(42)

# Generate 30 Excellent Samples (Class AA/A)
excellent_samples = pd.DataFrame({
    "DO": np.random.uniform(7.0, 10.0, 30),
    "BOD": np.random.uniform(0.1, 1.5, 30),
    "TSS": np.random.uniform(1.0, 15.0, 30),
    "pH": np.random.uniform(6.8, 7.5, 30),
    "Temperature": np.random.uniform(22.0, 26.0, 30),
    "Fecal_Coliform": np.random.uniform(0.0, 1.1, 30)
})

# Generate 30 Good Samples (Class A/B)
good_samples = pd.DataFrame({
    "DO": np.random.uniform(5.0, 7.0, 30),
    "BOD": np.random.uniform(1.5, 3.5, 30),
    "TSS": np.random.uniform(15.0, 40.0, 30),
    "pH": np.random.uniform(6.5, 8.0, 30),
    "Temperature": np.random.uniform(25.0, 29.0, 30),
    "Fecal_Coliform": np.random.uniform(1.1, 50.0, 30)
})

# Generate 30 Fair/Poor Samples to bridge the gap to the Jalaur data
fair_samples = pd.DataFrame({
    "DO": np.random.uniform(3.0, 5.0, 30),
    "BOD": np.random.uniform(3.5, 6.0, 30),
    "TSS": np.random.uniform(40.0, 70.0, 30),
    "pH": np.random.uniform(6.0, 8.5, 30),
    "Temperature": np.random.uniform(28.0, 31.0, 30),
    "Fecal_Coliform": np.random.uniform(50.0, 200.0, 30)
})

synthetic_df = pd.concat([excellent_samples, good_samples, fair_samples], ignore_index=True)
df = pd.concat([df, synthetic_df], ignore_index=True)
print(f"Added {len(synthetic_df)} synthetic baseline records.")
print(f"New shape: {df.shape}")
"""

    new_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in seed_code.split("\n")][:-1]
    }
    
    # Find the cell index that calculates WQI
    target_idx = -1
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code' and "df['DO_Temp_Ratio'] =" in ''.join(cell['source']):
            target_idx = i
            break
            
    if target_idx != -1:
        nb['cells'].insert(target_idx, new_cell)
        
    with open('wqi_analysis_demo.ipynb', 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)

patch_notebook()
print("Notebook successfully patched.")
