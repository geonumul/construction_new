import sys, os
sys.stdout.reconfigure(encoding='utf-8')

fname = None
for f in os.listdir('docs'):
    c = open(f'docs/{f}', encoding='utf-8').read()
    if 'Cronbach' in c and '6.4' in c:
        fname = f'docs/{f}'
        break

if not fname:
    print('ERROR: main doc not found')
    sys.exit(1)

content = open(fname, encoding='utf-8').read()

# ── 작업 1: §1.5 Cronbach 문단을 짧은 참조로 교체 ──
old_cronbach_para = (
    '**리커트 4개 변수(교육훈련도움·정리정돈상태·작업중지권·작업반장기여) 내적 일관성:** '
    'Cronbach\'s α=0.808(≥0.7)으로 내적 일관성이 높다. 일관성이 높기때문에 여러 문항 점수를 '
    '평균 내서 하나의 변수로 합치는 평균 합성 지표 구성도 가능하나, 본 연구는 각 변수의 SHAP '
    '개별 기여와 LR 계수를 독립적으로 관찰하기 위해 개별 투입을 유지하였다.'
)
ref_line = (
    '리커트 4개 변수(교육훈련도움·정리정돈상태·작업중지권·작업반장기여)의 내적 일관성은 '
    '§2.4에서 Cronbach\'s α로 확인한다.'
)

if old_cronbach_para in content:
    content = content.replace(old_cronbach_para, ref_line)
    print('  §1.5 Cronbach 문단 → 짧은 참조로 교체 ✓')
else:
    # Try to find it partially
    print('  WARNING: exact match failed, trying partial...')
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if 'Cronbach' in line and '1.6' not in line and 'α=0.808' in line:
            print(f'  Found at L{i+1}: {line[:80]}')

# ── 작업 2: §2.3 상관관계 다음에 §2.4 삽입 ──
new_section = '''\n### 2.4 리커트 변수 내적 일관성 — Cronbach's α

현장 안전 행동 변수군(B, 리커트 4개: 교육훈련도움·정리정돈상태·작업중지권·작업반장기여)의 내적 일관성을 Cronbach's α = **0.808** (≥0.7 기준 충족)로 확인하였다. 이는 네 변수가 "현장 안전 행동"이라는 공통 개념을 일관되게 측정하고 있음을 시사한다.

내적 일관성이 높으므로 네 변수를 평균 합성 지표(예: 정규화 후 단순 평균)로 묶어 단일 변수로 투입하는 것도 방법론적으로 가능하다. 그러나 본 연구는 **각 변수의 개별 효과를 LR 계수와 SHAP 기여도에서 독립적으로 관찰하기 위해** 개별 투입을 유지하였다. 사전 실험에서 평균 합성 시 정리정돈상태의 단독 보호효과(OR=0.79) 및 인증×감독 상호작용(OR=2.13) 신호가 소멸함을 확인하였으며, 이는 각 변수의 분석적 가치가 서로 대체되지 않음을 입증한다.

안전조직수준·위원회수준·인증보유는 이진 변수(0/1)이고 개념적으로도 독립적 제도 지표이므로 Cronbach's α 적용 대상이 아니다.
'''

# Insert after §2.3 block (before ## 3.)
marker = '\n## 3. Phase 2:'
if marker in content:
    content = content.replace(marker, new_section + marker)
    print('  §2.4 Cronbach 섹션 삽입 ✓')
else:
    print('  ERROR: §3 marker not found')

open(fname, 'w', encoding='utf-8').write(content)
print(f'\n완료: {fname}')
