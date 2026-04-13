import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

nb_f = [f for f in os.listdir('notebooks') if f.endswith('.ipynb') and '02' in f and 'executed' not in f][0]
path = f'notebooks/{nb_f}'
nb = json.load(open(path, encoding='utf-8'))
cells = nb['cells']

def add_savefig(cell_i, save_line, before='plt.show()'):
    src = ''.join(cells[cell_i]['source'])
    if save_line.split('/')[-1].split("'")[0] in src:
        print(f'  Cell {cell_i}: 이미 저장 코드 있음 — 스킵')
        return
    if before in src:
        src = src.replace(before, save_line + '\n' + before)
    else:
        src = src.rstrip() + '\n' + save_line + '\nplt.show()'
    cells[cell_i]['source'] = [src]
    cells[cell_i]['outputs'] = []
    cells[cell_i]['execution_count'] = None
    print(f'  Cell {cell_i}: savefig 추가 ✓')

def replace_in_cell(cell_i, old, new):
    src = ''.join(cells[cell_i]['source'])
    if old in src:
        cells[cell_i]['source'] = [src.replace(old, new)]
        cells[cell_i]['outputs'] = []
        cells[cell_i]['execution_count'] = None
        print(f'  Cell {cell_i}: 경로 수정 ✓')
    else:
        print(f'  Cell {cell_i}: 패턴 없음 — {old[:50]}')

def make_code(src):
    return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":[src]}

print('=== 1. Phase 1 그림 저장 추가 ===')
# Cell 9: 종속변수 분포
add_savefig(9,  "plt.savefig('../results/1_target_distribution.png', dpi=150, bbox_inches='tight')")
# Cell 11: 상관관계 히트맵 (plt.show → savefig + show)
src11 = ''.join(cells[11]['source'])
if 'plt.show' in src11 and '1_target' not in src11:
    src11 = src11.replace('plt.show', "plt.savefig('../results/2_correlation_heatmap.png', dpi=150, bbox_inches='tight')\nplt.show")
    cells[11]['source'] = [src11]
    cells[11]['outputs'] = []
    cells[11]['execution_count'] = None
    print('  Cell 11: 상관관계 히트맵 savefig 추가 ✓')

print('\n=== 2. Phase 3 ML 그림 저장 추가 ===')
# Cell 31: Confusion Matrix
add_savefig(31, "plt.savefig('../results/10_confusion_matrices.png', dpi=150, bbox_inches='tight')")
# Cell 32: ROC Curve
add_savefig(32, "plt.savefig('../results/11_roc_curves.png', dpi=150, bbox_inches='tight')")

print('\n=== 3. Phase 4 SHAP 그림 저장 추가 ===')
# Cell 42: SHAP Summary Dot
add_savefig(42, "plt.savefig('../results/12_shap_summary_dot.png', dpi=150, bbox_inches='tight')")
# Cell 43: SHAP Bar
add_savefig(43, "plt.savefig('../results/13_shap_bar.png', dpi=150, bbox_inches='tight')")
# Cell 46: SHAP Dependence 6쌍
add_savefig(46, "plt.savefig('../results/12_shap_dependence_moderation.png', dpi=150, bbox_inches='tight')")

print('\n=== 4. Permutation Importance 시각화 + 저장 (Cell 49) ===')
src49 = ''.join(cells[49]['source'])
pi_viz = '''

# Permutation Importance 시각화
fig, ax = plt.subplots(figsize=(8, 6))
top15 = perm_df.head(15)
ax.barh(top15['변수명'][::-1], top15['PI_mean'][::-1],
        xerr=top15['PI_std'][::-1], color='#4C72B0', alpha=0.8, capsize=3)
ax.axvline(0, color='black', lw=0.8, linestyle='--')
ax.set_xlabel('Permutation Importance (F1 기준)')
ax.set_title('Permutation Importance Top-15')
plt.tight_layout()
plt.savefig('../results/16_permutation_importance.png', dpi=150, bbox_inches='tight')
plt.show()
print('저장: 16_permutation_importance.png')
'''
cells[49]['source'] = [src49 + pi_viz]
cells[49]['outputs'] = []
cells[49]['execution_count'] = None
print('  Cell 49: Permutation Importance 시각화 + savefig 추가 ✓')

print('\n=== 5. 임계값 분석 경로 수정 (Cell 51) ===')
replace_in_cell(51,
    "plt.savefig('17_shap_threshold_정리정돈.png', dpi=150, bbox_inches='tight')",
    "plt.savefig('../results/17_shap_threshold_정리정돈.png', dpi=150, bbox_inches='tight')")
replace_in_cell(51,
    "print('저장: 17_shap_threshold_정리정돈.png')",
    "print('저장: results/17_shap_threshold_정리정돈.png')")

print('\n=== 6. §3.6 Interaction Plot 셀 추가 (cell 27 위치) ===')
interaction_plot_src = '''\
# §3.6 조절효과 시각화 (Interaction Plot) — 인증보유 × 고용노동부감독
# Model 2(주효과 모형) 예측확률 기반

# 4개 그룹: 인증보유(0/1) × 감독(0/1) 조합별 평균 예측확률
pred_proba_m2 = m2.predict()   # Model 2 fitted probabilities (학습 데이터 전체)
df_pred = df.copy()
df_pred['pred'] = pred_proba_m2

groups = df_pred.groupby(['인증보유', '고용노동부감독'])['pred'].mean().reset_index()
groups.columns = ['인증보유', '감독', '예측사고확률']

fig, ax = plt.subplots(figsize=(6, 4.5))
colors = {'감독 없음': '#4C72B0', '감독 있음': '#DD8452'}
for 감독_val, label in [(0, '감독 없음'), (1, '감독 있음')]:
    sub = groups[groups['감독'] == 감독_val].sort_values('인증보유')
    ax.plot(sub['인증보유'], sub['예측사고확률'],
            marker='o', linewidth=2, markersize=8,
            label=label, color=colors[label])

ax.set_xticks([0, 1])
ax.set_xticklabels(['인증 미보유', '인증 보유'])
ax.set_ylabel('사고발생 예측확률 (Model 2)')
ax.set_title('조절효과 Interaction Plot\\n인증보유 × 고용노동부감독')
ax.legend()
ax.set_ylim(0, 0.5)
plt.tight_layout()
plt.savefig('../results/8_interaction_plot.png', dpi=150, bbox_inches='tight')
plt.show()
print('저장: results/8_interaction_plot.png')
'''
# 기존 셀 27 앞에 삽입 (Phase 2 결과 직후 = 셀 26 alias 이후)
cells.insert(27, make_code(interaction_plot_src))
print('  Cell 27 삽입: Interaction Plot ✓')

json.dump(nb, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n노트북 패치 완료')
