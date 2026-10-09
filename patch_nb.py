"""
patch_nb.py
This script acts like a search-and-replace tool for our Jupyter Notebook (`wqi_analysis_demo.ipynb`).
It automatically looks for old water quality names (like "Very_Poor" or "Very Poor") 
and changes them to the new names ("Fair" and "Poor") so our project matches the latest standards.
"""

import json
import re

def fix_notebook():
    """
    Opens the notebook file, reads through every text block and code block,
    and swaps out the old words for the new ones.
    """
    # 1. Open the notebook so we can read it
    with open('wqi_analysis_demo.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    changes_made = 0
    
    # 2. Go through every single block (cell) in the notebook
    for cell in nb['cells']:
        if cell['cell_type'] == 'code' or cell['cell_type'] == 'markdown':
            new_source = []
            
            # 3. Read the block line by line and replace the old words
            for line in cell['source']:
                original = line
                
                # Replace logic in code
                line = line.replace('elif wqi <= 75: return "Poor"', 'elif wqi <= 75: return "Fair"')
                line = line.replace('elif wqi <= 100: return "Very_Poor"', 'elif wqi <= 100: return "Poor"')
                line = line.replace('elif wqi <= 100: return "Very Poor"', 'elif wqi <= 100: return "Poor"')
                
                # Replace lists of classes
                line = line.replace('"Very_Poor"', '')
                line = line.replace('"Excellent", "Good", "Poor", "High Risk"', '"Excellent", "Good", "Fair", "Poor", "High Risk"')
                line = line.replace('["Excellent", "Good", "Poor", "Very_Poor", "High Risk"]', '["Excellent", "Good", "Fair", "Poor", "High Risk"]')
                line = line.replace('"Very Poor"', '')
                
                # Replace in markdown (text blocks)
                line = line.replace('Very_Poor', 'Poor')
                line = line.replace('Very Poor', 'Poor')
                
                new_source.append(line)
                
                if original != line:
                    changes_made += 1
            
            # 4. Save the updated text back into the block
            cell['source'] = new_source
            
    # 5. Save the updated notebook back to the computer
    with open('wqi_analysis_demo.ipynb', 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
        
    print(f"Notebook successfully patched. Made {changes_made} changes.")

if __name__ == '__main__':
    fix_notebook()

