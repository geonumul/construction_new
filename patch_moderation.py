import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('notebooks/02_데이터분석.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']

def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": [src] if isinstance(src, str) else src}

def code(src):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": src if isinstance(src, list) else [src]}

# ─── 1. Update cell 14 — Phase 2 header ───
assert '계층적 회귀' in ''.join(cells[14]['source']), "Cell 14 not Phase 2 header"
cells[14]['source'] = [
    "---\n",
    "## Phase 2. 조절효과 분석 (Moderation Analysis)\n",
    "\n",
    "RQ의 핵심인 '외부 기관의 조절효과'를 직접 검증하기 위해,\n",
    "**Baseline 주효과 모형**에 각 상호작용항을 개별적으로 추가하는\n",
    "**개별 조절효과 검증(Individual Moderation Test)** 구조를 사용한다.\n",
    "\n",
    "| 단계 | 내용 |\n",
    "|:---|:---|\n",
    "| Baseline | 통제 + 독립A + 독립B + 조절 주효과 (=Model 4) |\n",
    "| 개별 조절 24쌍 | Baseline + 상호작용 1개씩 → 각 OR, 95% CI, p-value |\n",
    "| 그룹 LR test | A군(9쌍) / B군(15쌍) 전체 우도비 검정 |\n",
    "| 부록 A | 계층적 회귀 보조 분석 (M1~M5 ΔR² 참고용) |\n"
]

# ─── 2. Build new moderation analysis cells to insert after cell 15 ───
new_cells = []

# 2-a. Baseline model
new_cells.append(code([
    "# Phase 2-1. Baseline 주효과 모형\n",
    "# BASELINE = CTRL + IND_A + IND_B + MOD = ALL_FEATURES\n",
    "# (Model 4와 동일 — 조절효과 검증의 참조 기준)\n",
    "BASELINE_FEATURES = ALL_FEATURES  # CTRL+IND_A+IND_B+MOD 전체 주효과\n",
    "m_baseline, s_baseline = fit_logit(y, df[BASELINE_FEATURES], 'Baseline: 주효과 모형 (조절효과 참조)')\n",
    "\n",
    "print(f'\\n[Baseline 핵심 변수 (주효과)]')\n",
    "for var in ['정리정돈상태', '인증보유', '고용노동부감독', '공사규모', '기성공정률']:\n",
    "    if var in s_baseline.index:\n",
    "        r = s_baseline.loc[var]\n",
    "        print(f'  {var:12s}: OR={r[\"OR\"]:.3f}, p={r[\"P>|z|\"]:.4f} {r[\"Sig\"]}')\n",
]))

# 2-b. 24 individual moderation models
new_cells.append(code([
    "# Phase 2-2. 개별 조절효과 검증 — 24쌍 (8독립 × 3조절)\n",
    "# 각 상호작용항을 Baseline에 하나씩 추가해 개별적으로 검증\n",
    "# → 상호작용항 간 다중공선성 없이 각 조절효과의 순수 추정량 확보\n",
    "\n",
    "import warnings; warnings.filterwarnings('ignore')\n",
    "from scipy.stats import chi2 as chi2_dist_mod\n",
    "\n",
    "moderation_results = []\n",
    "\n",
    "for indep in IND_ALL:\n",
    "    for mod_var in MOD:\n",
    "        interaction_name = f'{indep}_x_{mod_var}'\n",
    "        X_mod = df[BASELINE_FEATURES].copy()\n",
    "        X_mod[interaction_name] = df[indep] * df[mod_var]\n",
    "        X_c = sm.add_constant(X_mod)\n",
    "        m_mod = sm.Logit(y, X_c).fit(disp=0)\n",
    "\n",
    "        coef  = m_mod.params[interaction_name]\n",
    "        pval  = m_mod.pvalues[interaction_name]\n",
    "        ci_lo = m_mod.conf_int().loc[interaction_name, 0]\n",
    "        ci_hi = m_mod.conf_int().loc[interaction_name, 1]\n",
    "\n",
    "        # LR test vs Baseline (1 df)\n",
    "        lr_stat  = 2 * (m_mod.llf - m_baseline.llf)\n",
    "        lr_p     = chi2_dist_mod.sf(lr_stat, 1)\n",
    "\n",
    "        sig = '***' if pval < 0.001 else ('**' if pval < 0.01 else ('*' if pval < 0.05 else ('.' if pval < 0.1 else '')))\n",
    "        moderation_results.append({\n",
    "            '독립변수': indep,\n",
    "            '조절변수': mod_var,\n",
    "            '그룹': 'A' if indep in IND_A else 'B',\n",
    "            'β': round(coef, 4),\n",
    "            'OR': round(float(np.exp(coef)), 3),\n",
    "            '95% CI': f'[{np.exp(ci_lo):.3f}, {np.exp(ci_hi):.3f}]',\n",
    "            'p (Wald)': round(pval, 4),\n",
    "            '유의성': sig,\n",
    "            'LR_p': round(lr_p, 4),\n",
    "        })\n",
    "\n",
    "moderation_df = pd.DataFrame(moderation_results)\n",
    "\n",
    "print('[개별 조절효과 24쌍 결과 (Baseline + 1 상호작용항)]')\n",
    "print(moderation_df.to_string(index=False))\n",
    "\n",
    "sig_mod = moderation_df[moderation_df['p (Wald)'] < 0.05]\n",
    "print(f'\\n[p<0.05 유의 조절효과: {len(sig_mod)}쌍]')\n",
    "if len(sig_mod) > 0:\n",
    "    print(sig_mod[['독립변수','조절변수','OR','95% CI','p (Wald)','유의성']].to_string(index=False))\n",
]))

# 2-c. Group A and B LR tests
new_cells.append(code([
    "# Phase 2-3. 그룹별 조절효과 통합 우도비 검정\n",
    "# Group A Moderation: Baseline + (IND_A × MOD = 9쌍)\n",
    "# Group B Moderation: Baseline + (IND_B × MOD = 15쌍)\n",
    "\n",
    "from scipy.stats import chi2 as chi2_grp\n",
    "\n",
    "# Group A\n",
    "X_groupA = df[BASELINE_FEATURES].copy()\n",
    "for indep in IND_A:\n",
    "    for mod_var in MOD:\n",
    "        X_groupA[f'{indep}_x_{mod_var}'] = df[indep] * df[mod_var]\n",
    "m_groupA = sm.Logit(y, sm.add_constant(X_groupA)).fit(disp=0)\n",
    "lr_A  = 2 * (m_groupA.llf - m_baseline.llf)\n",
    "df_A  = len(IND_A) * len(MOD)\n",
    "p_A   = chi2_grp.sf(lr_A, df_A)\n",
    "\n",
    "# Group B\n",
    "X_groupB = df[BASELINE_FEATURES].copy()\n",
    "for indep in IND_B:\n",
    "    for mod_var in MOD:\n",
    "        X_groupB[f'{indep}_x_{mod_var}'] = df[indep] * df[mod_var]\n",
    "m_groupB = sm.Logit(y, sm.add_constant(X_groupB)).fit(disp=0)\n",
    "lr_B  = 2 * (m_groupB.llf - m_baseline.llf)\n",
    "df_B  = len(IND_B) * len(MOD)\n",
    "p_B   = chi2_grp.sf(lr_B, df_B)\n",
    "\n",
    "print('[그룹별 조절효과 통합 LR test]')\n",
    "print(f'  A군(IND_A×MOD = {df_A}쌍): χ²={lr_A:.3f}, df={df_A}, p={p_A:.4f}  '\n",
    "      f'{\"*\" if p_A<0.05 else \"(비유의)\"}')\n",
    "print(f'  B군(IND_B×MOD = {df_B}쌍): χ²={lr_B:.3f}, df={df_B}, p={p_B:.4f}  '\n",
    "      f'{\"*\" if p_B<0.05 else \"(비유의)\"}')\n",
    "print()\n",
    "print('[해석]')\n",
    "print('  - A군 LR test: 절차 이행 응답 변수(인증·조직·위원회)와 외부 기관 조절변수의')\n",
    "print('    집합적 상호작용 유의성')\n",
    "print('  - B군 LR test: 현장 안전 행동 응답 변수와 외부 기관 조절변수의')\n",
    "print('    집합적 상호작용 유의성')\n",
    "print('  - 전체 집합 비유의 시에도 개별 쌍(인증×감독 등) 유의성은 별도로 해석')\n",
]))

# 2-d. P-value heatmap (8×3)
new_cells.append(code([
    "# Phase 2-4. 조절효과 p-value 히트맵 (8독립 × 3조절)\n",
    "import seaborn as sns\n",
    "\n",
    "pivot_p = moderation_df.pivot(index='독립변수', columns='조절변수', values='p (Wald)')\n",
    "# 행 순서: IND_A 먼저, IND_B 다음\n",
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
    "\n",
    "# p<0.05 셀에 테두리 강조\n",
    "for i, row in enumerate(pivot_p.index):\n",
    "    for j, col in enumerate(pivot_p.columns):\n",
    "        val = pivot_p.loc[row, col]\n",
    "        if val < 0.05:\n",
    "            ax.add_patch(plt.Rectangle((j, i), 1, 1, fill=False,\n",
    "                         edgecolor='blue', lw=2.5, clip_on=False))\n",
    "\n",
    "# A/B 그룹 구분선\n",
    "ax.axhline(len(IND_A), color='black', lw=2)\n",
    "ax.text(-0.05, len(IND_A)/2, 'IND_A', ha='right', va='center',\n",
    "        fontsize=10, rotation=90, transform=ax.get_yaxis_transform())\n",
    "ax.text(-0.05, len(IND_A) + len(IND_B)/2, 'IND_B', ha='right', va='center',\n",
    "        fontsize=10, rotation=90, transform=ax.get_yaxis_transform())\n",
    "\n",
    "ax.set_title('조절효과 p-value 히트맵\\n(파란 테두리: p<0.05 유의 쌍, 색상: 낮을수록 유의)')\n",
    "ax.set_xlabel('조절변수')\n",
    "ax.set_ylabel('독립변수')\n",
    "plt.tight_layout()\n",
    "plt.savefig('../results/20_moderation_pvalue_heatmap.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
    "print('저장: 20_moderation_pvalue_heatmap.png')\n",
]))

# 2-e. Hosmer-Lemeshow for Baseline
new_cells.append(code([
    "# Phase 2-5. Baseline 모형 적합도 (Hosmer-Lemeshow)\n",
    "hl_b_stat, hl_b_df, hl_b_p = hosmer_lemeshow_test(m_baseline, y, df[BASELINE_FEATURES])\n",
    "print('[Hosmer-Lemeshow 검정 — Baseline(주효과) 모형]')\n",
    "print(f'  H-L 통계량: {hl_b_stat:.4f}')\n",
    "print(f'  자유도(df): {hl_b_df}')\n",
    "print(f'  p-value:    {hl_b_p:.4f}')\n",
    "if hl_b_p > 0.05:\n",
    "    print('  → p > 0.05: 모형이 데이터에 적합')\n",
    "else:\n",
    "    print('  → p < 0.05: 모형 적합도 주의')\n",
]))

# Appendix A markdown
new_cells.append(md([
    "---\n",
    "### 부록 A. 계층적 회귀 보조 분석 (Model 1~5 참고용)\n",
    "\n",
    "아래 Model 1~5는 메인 분석(조절효과 분석)의 보조 참고용이다.\n",
    "변수 그룹별 설명력 기여(ΔR²)를 확인하여 통제변수의 지배적 역할을 부각하는 용도로 활용한다.\n",
    "Model 5는 24개 상호작용항을 동시 투입한 버전으로, 개별 조절효과 분석(Phase 2-2)과 보완 관계다.\n"
]))

# ─── 3. Insert new cells after cell 15 ───
insert_pos = 16  # After cell 15 (fit_logit definition)
for i, c in enumerate(new_cells):
    cells.insert(insert_pos + i, c)

print(f"Inserted {len(new_cells)} new cells at position {insert_pos}.")
print(f"Total cells now: {len(cells)}")

# ─── 4. Clear outputs of modified/inserted cells ───
for c in cells:
    if c['cell_type'] == 'code':
        c['outputs'] = []
        c['execution_count'] = None

with open('notebooks/02_데이터분석.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Notebook saved.")
