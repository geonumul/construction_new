import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('notebooks/02_데이터분석.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)
cells = nb['cells']
print(f'Initial cell count: {len(cells)}')

def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": [src] if isinstance(src, str) else src}

def code(src):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": src if isinstance(src, list) else [src]}

# ─── 0. Save robustness cells 32-35 before deletion (fix s4 → s_model1) ───
ordinal_md = md(["---\n",
    "## 부록 A. 순서형 변수 등간 가정 강건성 검증\n",
    "\n",
    "안전조직수준·위원회수준·위험성평가수준(0/1/2)을 더미 변수(기준=0)로 처리한 대안 모형과 연속형 처리 결과 비교.",
])

# Fix cell 33: s4 → s_model1, m4_dummy variable OK (local)
ordinal_src = ''.join(cells[33]['source'])
ordinal_src = ordinal_src.replace(
    "orig_or  = round(float(np.exp(s4.loc[var,'Coef.'])), 3)",
    "orig_or  = round(float(np.exp(s_model1.loc[var,'Coef.'])), 3)"
)
ordinal_src = ordinal_src.replace(
    "orig_p   = round(float(s4.loc[var,'P>|z|']), 3)",
    "orig_p   = round(float(s_model1.loc[var,'P>|z|']), 3)"
)
# m4_dummy → m_model1_dummy to avoid name confusion
ordinal_src = ordinal_src.replace('m4_dummy', 'm_model1_dummy')
ordinal_src = ordinal_src.replace('s4_dummy', 's_model1_dummy')
ordinal_code = code(ordinal_src)

likert_md = md(["---\n",
    "## 부록 B. 리커트 상향편향 강건성 검증 (정리정돈상태)\n",
    "\n",
    "정리정돈상태 응답의 상향편향(4-5점 쏠림) 확인 후 저(1-3점)/중(4점)/고(5점) 3범주 더미 처리 강건성 검증.",
])

# Fix cell 35: s4 → s_model1
likert_src = ''.join(cells[35]['source'])
likert_src = likert_src.replace(
    "orig_or = round(float(np.exp(s4.loc['정리정돈상태','Coef.'])), 3)",
    "orig_or = round(float(np.exp(s_model1.loc['정리정돈상태','Coef.'])), 3)"
)
likert_src = likert_src.replace(
    "orig_p  = round(float(s4.loc['정리정돈상태','P>|z|']), 3)",
    "orig_p  = round(float(s_model1.loc['정리정돈상태','P>|z|']), 3)"
)
likert_src = likert_src.replace('m4_lik', 'm_model1_lik')
likert_src = likert_src.replace('s4_lik', 's_model1_lik')
likert_code = code(likert_src)

# ─── 1. Update cell 14: Phase 2 header ───
assert '조절효과 분석' in ''.join(cells[14]['source']), "Cell 14 unexpected"
cells[14]['source'] = [
    "---\n",
    "## Phase 2. 조절효과 분석 (Moderation Analysis)\n",
    "\n",
    "외부 기관의 조절효과 검증을 위해 2단계 로지스틱 회귀를 수행한다.\n",
    "\n",
    "| 모형 | 내용 |\n",
    "|:---|:---|\n",
    "| **Model 1 (주효과)** | 통제(5) + 독립A(3) + 독립B(5) + 조절(3) = 16개 변수 |\n",
    "| **Model 2 (조절효과)** | Model 1 + 24개 상호작용항(IND_ALL × MOD) 동시 투입 |\n",
    "\n",
    "Model 2의 24개 상호작용항 p-value를 개별 출력하고, p-value 히트맵으로 시각화한다.\n",
    "Hosmer-Lemeshow 검정을 통해 Model 2의 적합도를 확인한다.\n",
]

# ─── 2. Update cell 16: Baseline → Model 1 ───
assert 'Baseline' in ''.join(cells[16]['source']), "Cell 16 unexpected"
cells[16]['source'] = [
    "# Phase 2-1. Model 1 — 주효과 모형\n",
    "# 통제(5) + 독립A(3) + 독립B(5) + 조절(3) = 16개 변수\n",
    "m_model1, s_model1 = fit_logit(y, df[ALL_FEATURES], 'Model 1: 주효과 모형')\n",
    "\n",
    "print(f'\\n[Model 1 핵심 변수 (주효과, p<0.05)]')\n",
    "for var in ['정리정돈상태', '고용노동부감독', '공사규모', '기성공정률', '공사종류', '외국인비율']:\n",
    "    if var in s_model1.index:\n",
    "        r = s_model1.loc[var]\n",
    "        print(f'  {var:14s}: OR={r[\"OR\"]:.3f}, p={r[\"P>|z|\"]:.4f} {r[\"Sig\"]}')\n",
]

# ─── 3. Build new Phase 2-2: Model 2 + p-value table + heatmap ───
new_model2_cell = code([
    "# Phase 2-2. Model 2 — 조절효과 모형 (주효과 + 24개 상호작용항 동시 투입)\n",
    "import warnings; warnings.filterwarnings('ignore')\n",
    "import seaborn as sns\n",
    "\n",
    "# 상호작용항 생성: IND_ALL × MOD = 8 × 3 = 24쌍\n",
    "X_inter = df[ALL_FEATURES].copy()\n",
    "inter_terms = []\n",
    "for indep in IND_ALL:\n",
    "    for mod_var in MOD:\n",
    "        term = f'{indep}_x_{mod_var}'\n",
    "        X_inter[term] = df[indep] * df[mod_var]\n",
    "        inter_terms.append(term)\n",
    "\n",
    "m_model2 = sm.Logit(y, sm.add_constant(X_inter)).fit(disp=0)\n",
    "print(f'[Model 2] Pseudo R²={m_model2.prsquared:.4f}, ')\n",
    "print(f'          ΔPseudo R² (M1→M2) = {m_model2.prsquared - m_model1.prsquared:.4f}')\n",
    "\n",
    "# 24쌍 결과 추출\n",
    "moderation_results = []\n",
    "for indep in IND_ALL:\n",
    "    for mod_var in MOD:\n",
    "        term = f'{indep}_x_{mod_var}'\n",
    "        coef  = m_model2.params[term]\n",
    "        pval  = m_model2.pvalues[term]\n",
    "        ci_lo = m_model2.conf_int().loc[term, 0]\n",
    "        ci_hi = m_model2.conf_int().loc[term, 1]\n",
    "        sig = '***' if pval < 0.001 else ('**' if pval < 0.01 else ('*' if pval < 0.05 else ('.' if pval < 0.1 else '')))\n",
    "        moderation_results.append({\n",
    "            '독립변수': indep,\n",
    "            '조절변수': mod_var,\n",
    "            '그룹': 'A' if indep in IND_A else 'B',\n",
    "            'OR': round(float(np.exp(coef)), 3),\n",
    "            '95% CI': f'[{np.exp(ci_lo):.3f}, {np.exp(ci_hi):.3f}]',\n",
    "            'p (Wald)': round(pval, 4),\n",
    "            '유의성': sig,\n",
    "        })\n",
    "\n",
    "moderation_df = pd.DataFrame(moderation_results)\n",
    "print('\\n[조절효과 24쌍 결과 (Model 2 상호작용항)]')\n",
    "print(moderation_df.to_string(index=False))\n",
    "\n",
    "sig_mod = moderation_df[moderation_df['p (Wald)'] < 0.05]\n",
    "print(f'\\n[p<0.05 유의 조절효과: {len(sig_mod)}쌍]')\n",
    "if len(sig_mod) > 0:\n",
    "    print(sig_mod[['독립변수','조절변수','OR','95% CI','p (Wald)','유의성']].to_string(index=False))\n",
    "\n",
    "# ── p-value 히트맵 (8독립 × 3조절) ──\n",
    "pivot_p = moderation_df.pivot(index='독립변수', columns='조절변수', values='p (Wald)')\n",
    "row_order = IND_A + IND_B\n",
    "pivot_p = pivot_p.reindex(row_order)\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(8, 7))\n",
    "sns.heatmap(\n",
    "    pivot_p, annot=True, fmt='.3f', cmap='RdYlGn_r',\n",
    "    vmin=0, vmax=0.2, ax=ax,\n",
    "    linewidths=0.5, linecolor='gray',\n",
    "    cbar_kws={'label': 'p-value'}\n",
    ")\n",
    "for i, row in enumerate(pivot_p.index):\n",
    "    for j, col in enumerate(pivot_p.columns):\n",
    "        val = pivot_p.loc[row, col]\n",
    "        if val < 0.05:\n",
    "            ax.add_patch(plt.Rectangle((j, i), 1, 1, fill=False,\n",
    "                         edgecolor='blue', lw=2.5, clip_on=False))\n",
    "ax.axhline(len(IND_A), color='black', lw=2)\n",
    "ax.text(-0.05, len(IND_A)/2, 'IND_A', ha='right', va='center',\n",
    "        fontsize=10, rotation=90, transform=ax.get_yaxis_transform())\n",
    "ax.text(-0.05, len(IND_A) + len(IND_B)/2, 'IND_B', ha='right', va='center',\n",
    "        fontsize=10, rotation=90, transform=ax.get_yaxis_transform())\n",
    "ax.set_title('조절효과 p-value 히트맵 (Model 2)\\n(파란 테두리: p<0.05, 색상: 낮을수록 유의)')\n",
    "ax.set_xlabel('조절변수')\n",
    "ax.set_ylabel('독립변수')\n",
    "plt.tight_layout()\n",
    "plt.savefig('../results/20_moderation_pvalue_heatmap.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
    "print('저장: 20_moderation_pvalue_heatmap.png')\n",
])

# ─── 4. Build new H-L cell for Model 2 ───
new_hl_cell = code([
    "# Phase 2-3. Model 2 적합도 — Hosmer-Lemeshow 검정\n",
    "from scipy.stats import chi2 as chi2_dist\n",
    "\n",
    "def hosmer_lemeshow_test(pred_vals, y_vals, g=10):\n",
    "    df_hl = pd.DataFrame({'y': np.asarray(y_vals), 'pred': np.asarray(pred_vals)})\n",
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
    "hl_stat, hl_df, hl_p = hosmer_lemeshow_test(m_model2.fittedvalues, y.values)\n",
    "print('[Hosmer-Lemeshow 검정 — Model 2 (조절효과 모형)]')\n",
    "print(f'  H-L 통계량: {hl_stat:.4f}')\n",
    "print(f'  자유도(df): {hl_df}')\n",
    "print(f'  p-value:    {hl_p:.4f}')\n",
    "if hl_p > 0.05:\n",
    "    print('  → p > 0.05: 모형이 데이터에 적합')\n",
    "else:\n",
    "    print('  → p < 0.05: 모형 적합도 주의')\n",
])

# ─── 5. Delete cells 17-36, insert new cells at 17 ───
del cells[17:37]   # removes 20 cells (17, 18, 19, 20, 21, 22..36)
cells.insert(17, new_hl_cell)
cells.insert(17, new_model2_cell)
print(f'After Phase 2 restructure: {len(cells)} cells')

# ─── 6. Update calibration cell (remove Brier/ECE) ───
calib_idx = None
for i, c in enumerate(cells):
    if c['cell_type'] == 'code' and 'brier_score_loss' in ''.join(c['source']):
        calib_idx = i
        break
print(f'Calibration cell at index: {calib_idx}')

if calib_idx is not None:
    cells[calib_idx]['source'] = [
        "# M4. Calibration Curve — 예측확률 신뢰도 검증\n",
        "from sklearn.calibration import calibration_curve\n",
        "\n",
        "y_proba = best_pipe.predict_proba(X_test)[:, 1]\n",
        "prob_true, prob_pred = calibration_curve(y_test, y_proba, n_bins=10)\n",
        "\n",
        "fig, ax = plt.subplots(figsize=(6, 5))\n",
        "ax.plot([0, 1], [0, 1], 'k--', label='완벽한 보정')\n",
        "ax.plot(prob_pred, prob_true, 's-', color='#4C72B0', label='Random Forest')\n",
        "ax.set_xlabel('예측 확률 (평균)')\n",
        "ax.set_ylabel('실제 양성 비율')\n",
        "ax.set_title('Calibration Curve (Random Forest)')\n",
        "ax.legend()\n",
        "plt.tight_layout()\n",
        "plt.savefig('../results/16_calibration_curve.png', dpi=150, bbox_inches='tight')\n",
        "plt.show()\n",
        "print('저장: 16_calibration_curve.png')\n",
        "print('[해석] Calibration Curve가 대각선에 근접할수록 예측확률이 실제 사고발생률과 일치함.')\n",
        "print('       Random Forest는 예측확률의 절대값보다 위험 순위 변별력(AUC=0.717)을 활용하는 것이 적절하다.')\n",
    ]

# ─── 7. Update results summary cell ───
summary_idx = None
for i, c in enumerate(cells):
    if c['cell_type'] == 'code' and '계층적 로지스틱 회귀' in ''.join(c['source']):
        summary_idx = i
        break
print(f'Results summary cell at index: {summary_idx}')

if summary_idx is not None:
    cells[summary_idx]['source'] = [
        "print('=' * 60)\n",
        "print('1. 조절효과 분석 (Moderation Analysis)')\n",
        "print('=' * 60)\n",
        "print(f'   Model 1 Pseudo R²: {m_model1.prsquared:.4f}')\n",
        "print(f'   Model 2 Pseudo R²: {m_model2.prsquared:.4f}')\n",
        "print(f'   ΔPseudo R² (M1→M2): {m_model2.prsquared - m_model1.prsquared:.4f}')\n",
        "print()\n",
        "\n",
        "sig_m1 = s_model1[(s_model1['P>|z|'] < 0.05) & (s_model1.index != 'const')]\n",
        "print('   Model 1 유의미한 변수 (p<0.05):')\n",
        "for v in sig_m1.index:\n",
        "    r = sig_m1.loc[v]\n",
        "    d = '+' if r['OR'] > 1 else '-'\n",
        "    print(f'     {v}: OR={r[\"OR\"]:.3f}({d}), p={r[\"P>|z|\"]:.4f} {r[\"Sig\"]}')\n",
        "\n",
        "print()\n",
        "sig_m2 = moderation_df[moderation_df['p (Wald)'] < 0.05]\n",
        "print(f'   Model 2 유의 조절효과 ({len(sig_m2)}쌍):')\n",
        "for _, r in sig_m2.iterrows():\n",
        "    print(f'     {r[\"독립변수\"]}×{r[\"조절변수\"]}: OR={r[\"OR\"]}, p={r[\"p (Wald)\"]:.4f} {r[\"유의성\"]}')\n",
        "\n",
        "print()\n",
        "print('=' * 60)\n",
        "print('2. ML 모델 비교 (SMOTENC)')\n",
        "print('=' * 60)\n",
        "for _, r in results_df.iterrows():\n",
        "    print(f'   {r[\"Model\"]}: F1={r[\"F1\"]}, AUC={r[\"ROC_AUC\"]}')\n",
        "print(f'   -> 최적 모델: {best_name}')\n",
        "print()\n",
        "print('   [SMOTENC 효과]')\n",
        "print('   적용 전: Recall=0.13~0.14, F1=0.20, LightGBM=0.000')\n",
        "print(f'   적용 후: Recall={results_df[\"Recall\"].min():.2f}~{results_df[\"Recall\"].max():.2f}, '\n",
        "          f'F1={results_df[\"F1\"].min():.2f}~{results_df[\"F1\"].max():.2f}')\n",
        "\n",
        "print()\n",
        "print('=' * 60)\n",
        "print('3. SHAP Top-5')\n",
        "print('=' * 60)\n",
        "for i, (_, r) in enumerate(shap_imp.head(5).iterrows(), 1):\n",
        "    print(f'   {i}. {r[\"변수명\"]} ({r[\"mean_abs_SHAP\"]:.4f})')\n",
        "print()\n",
        "print('   [LR-SHAP 교차 검증]')\n",
        "print('   - 통제변수: LR 유의미 → SHAP 상위권 (크기+방향 일치)')\n",
        "print('   - 정리정돈상태: LR 유의미(OR=0.792) → SHAP 음수 방향 일치')\n",
        "print('   - 선형(LR) + 비선형(ML) 모두에서 동일 결론 → 결과 견고')\n",
    ]

# ─── 8. Update Phase 5 markdown cell (Model 4 → Model 1) ───
for i, c in enumerate(cells):
    if c['cell_type'] == 'markdown' and 'Model 4' in ''.join(c['source']) and 'Phase 5' in ''.join(c['source']):
        src = ''.join(c['source'])
        src = src.replace('Model 4', 'Model 1')
        c['source'] = [src]
        print(f'Phase 5 markdown cell {i} updated')

# Update Phase 5 code cell comments (Model 4 → Model 1)
for i, c in enumerate(cells):
    if c['cell_type'] == 'code' and 'Phase 5' in ''.join(c['source']) and 'Model 4' in ''.join(c['source']):
        src = ''.join(c['source'])
        src = src.replace('Model 4', 'Model 1')
        c['source'] = [src]
        print(f'Phase 5 code cell {i} updated (Model 4 → Model 1)')

# ─── 9. Append appendix cells at end ───
cells.append(ordinal_md)
cells.append(ordinal_code)
cells.append(likert_md)
cells.append(likert_code)
print(f'Final cell count: {len(cells)}')

# ─── 10. Clear all outputs ───
for c in cells:
    if c['cell_type'] == 'code':
        c['outputs'] = []
        c['execution_count'] = None

with open('notebooks/02_데이터분석.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print('Notebook saved.')
