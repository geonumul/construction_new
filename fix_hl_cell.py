import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('notebooks/02_데이터분석.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']

# Find cell 20 (Phase 2-5 H-L)
idx = 20
assert 'Baseline 모형 적합도' in ''.join(cells[idx]['source']), f"Cell {idx} unexpected"

cells[idx]['source'] = [
    "# Phase 2-5. Baseline 모형 적합도 (Hosmer-Lemeshow)\n",
    "from scipy.stats import chi2 as chi2_dist\n",
    "\n",
    "def hosmer_lemeshow_test(model, y, X_df, g=10):\n",
    "    pred = model.predict(sm.add_constant(X_df))\n",
    "    df_hl = pd.DataFrame({'y': y.values, 'pred': pred})\n",
    "    df_hl['decile'] = pd.qcut(df_hl['pred'], g, duplicates='drop')\n",
    "    obs = df_hl.groupby('decile', observed=True)['y'].sum()\n",
    "    exp = df_hl.groupby('decile', observed=True)['pred'].sum()\n",
    "    n_g = df_hl.groupby('decile', observed=True)['y'].count()\n",
    "    pi_k = exp / n_g\n",
    "    denom = n_g * pi_k * (1 - pi_k)\n",
    "    valid = (exp >= 5) & ((n_g - exp) >= 5)\n",
    "    hl_stat = (((obs[valid] - exp[valid]) ** 2) / denom[valid]).sum()\n",
    "    df_deg = valid.sum() - 2\n",
    "    p_val = chi2_dist.sf(hl_stat, df_deg) if df_deg > 0 else float('nan')\n",
    "    return hl_stat, df_deg, p_val\n",
    "\n",
    "hl_b_stat, hl_b_df, hl_b_p = hosmer_lemeshow_test(m_baseline, y, df[BASELINE_FEATURES])\n",
    "print('[Hosmer-Lemeshow 검정 — Baseline(주효과) 모형]')\n",
    "print(f'  H-L 통계량: {hl_b_stat:.4f}')\n",
    "print(f'  자유도(df): {hl_b_df}')\n",
    "print(f'  p-value:    {hl_b_p:.4f}')\n",
    "if hl_b_p > 0.05:\n",
    "    print('  → p > 0.05: 모형이 데이터에 적합')\n",
    "else:\n",
    "    print('  → p < 0.05: 모형 적합도 주의')\n",
]
cells[idx]['outputs'] = []

with open('notebooks/02_데이터분석.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Cell {idx} (Phase 2-5 H-L) updated with inline function definition.")
