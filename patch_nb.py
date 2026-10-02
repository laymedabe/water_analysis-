import json
import re

def fix_notebook():
    with open('wqi_analysis_demo.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    changes_made = 0
    for cell in nb['cells']:
        if cell['cell_type'] == 'code' or cell['cell_type'] == 'markdown':
            new_source = []
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
                
                # Replace in markdown
                line = line.replace('Very_Poor', 'Poor')
                line = line.replace('Very Poor', 'Poor')
                
                new_source.append(line)
                if original != line:
                    changes_made += 1
            cell['source'] = new_source
            
    with open('wqi_analysis_demo.ipynb', 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
        
    print(f"Notebook successfully patched. Made {changes_made} changes.")

if __name__ == '__main__':
    fix_notebook()
