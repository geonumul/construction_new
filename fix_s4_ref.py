import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('notebooks/02_데이터분석.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)
cells = nb['cells']
src = ''.join(cells[50]['source'])
src = src.replace(
    "if var in s4.index and var in s_model1_dummy.index:",
    "if var in s_model1.index and var in s_model1_dummy.index:"
)
cells[50]['source'] = [src]
with open('notebooks/02_데이터분석.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print('Fixed s4.index -> s_model1.index in cell 50')
