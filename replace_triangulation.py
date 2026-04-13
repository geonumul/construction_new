import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')

def replace_file(path, transforms, delete_lines=None, delete_blocks=None):
    content = open(path, encoding='utf-8').read()
    original = content

    # Delete entire blocks (by start/end marker strings)
    if delete_blocks:
        for (start, end) in delete_blocks:
            # Find start to end and remove the whole segment including trailing newline
            pattern = re.escape(start) + r'.*?' + re.escape(end)
            content = re.sub(pattern, '', content, flags=re.DOTALL)

    # Delete specific lines (exact line match after strip)
    if delete_lines:
        lines = content.splitlines(keepends=True)
        out = []
        for line in lines:
            stripped = line.strip()
            if any(stripped == dl.strip() or dl.strip() in stripped for dl in delete_lines):
                pass  # drop line
            else:
                out.append(line)
        content = ''.join(out)

    # Apply ordered replacements (specific → general)
    for old, new in transforms:
        content = content.replace(old, new)

    if content != original:
        open(path, 'w', encoding='utf-8').write(content)
        print(f'  Updated: {path}')
    else:
        print(f'  No change: {path}')
    return content != original


print('=== 1. docs/데이터분析_과정_및_근거.md ===')

main_doc = None
main_fname = None
for f in os.listdir('docs'):
    try:
        c = open(f'docs/{f}', encoding='utf-8').read()
        if 'Triangulation' in c and '6.4' in c:
            main_doc = c
            main_fname = f'docs/{f}'
    except:
        pass

if main_fname:
    transforms_main = [
        # §6.4 title
        ('Phase 5: Triangulation 기반 강건성 검증',
         'Phase 5: 다층 교차 검증 기반 강건성'),

        # Subsection titles with full English form
        ('### 방법론 삼각검증 (Methodological Triangulation)',
         '### 방법론 간 결론 수렴 검증'),
        ('### 데이터 삼각검증 (Data Triangulation)',
         '### 하위표본 간 결과 일관성 검증'),
        ('### 지표 삼각검증 (Measurement Triangulation)',
         '### 중요도 지표 간 일관성 검증'),

        # §1.2 차별점
        ('다층 Triangulation 강건성 구조',
         '다층 교차 검증으로 확인한 강건성'),

        # Sentence with Triangulation structure marker (§5 para)
        ('Triangulation 구조에서 LR 추론 발견이 ML 비선형 관점에서도 수렴하는지 확인하기 위함이다',
         '다층 교차 검증 구조에서 LR 추론 발견이 ML 비선형 관점에서도 수렴하는지 확인하기 위함이다'),

        # §5.4 B-group convergence sentence
        ("'절차·인식 응답 변수'보다 '객관 관찰 가능한 현장 상태 변수'가 사고와 직접 연관됨을 시사한다. 정리정돈에 대한 심층 분석(방향성·임계값)은 LR 유일 유의 주효과라는 핵심 발견을 비선형 모형에서 재검증하려는 Triangulation 구조에서 정당화된다.",
         "'절차·인식 응답 변수'보다 '객관 관찰 가능한 현장 상태 변수'가 사고와 직접 연관됨을 시사한다. 정리정돈에 대한 심층 분석(방향성·임계값)은 LR 유일 유의 주효과라는 핵심 발견을 비선형 모형에서 재검증하려는 다층 교차 검증 구조에서 정당화된다."),

        # §1.2 table cell
        ('LR + RF/XGBoost/LightGBM + SHAP + Triangulation',
         'LR + RF/XGBoost/LightGBM + SHAP + 다층 교차 검증'),

        # §1.2 table — 방법론·지표 삼각검증
        ('공사규모·공사종류 분할 + 방법론·지표 삼각검증',
         '공사규모·공사종류 분할 + 방법론·지표 교차 검증'),

        # Parenthetical in LR-ML paragraph: (방법론 삼각검증, Methodological Triangulation)
        ('(방법론 삼각검증, Methodological Triangulation)',
         '(방법론 간 결론 수렴 검증)'),

        # §5 RQ alignment paragraph
        ('이는 Triangulation 구조에서',
         '이는 다층 교차 검증 구조에서'),

        # Generic: remaining 삼각검증 variants (order matters: specific first)
        ('방법론 삼각검증', '방법론 간 결론 수렴 검증'),
        ('데이터 삼각검증', '하위표본 간 결과 일관성 검증'),
        ('지표 삼각검증', '중요도 지표 간 일관성 검증'),
        ('삼각검증 체계(Triangulation)', '다층 교차 검증 체계'),
        ('삼각검증', '다층 교차 검증'),

        # Generic Triangulation
        ('Triangulation 기반 강건성', '다층 교차 검증 기반 강건성'),
        ('Triangulation 핵심 축', '교차 검증의 핵심'),
        ('Triangulation 다중 검증', '다층 교차 검증'),
        ('Triangulation', '다층 교차 검증'),
    ]

    # Lines to delete: Denzin/Jick intro sentence and Jick reference in bibliography
    delete_lines_main = [
        '본 연구의 강건성은 단일 기법이 아닌 세 가지 독립적 삼각검증 체계(Triangulation)로 확보된다. Denzin(1970)이 정의하고 Jick(1979, *Administrative Science Quarterly*)이 조직 연구에 적용한 Triangulation 개념에 따르면, 서로 다른 방법·자료·지표에서 도출된 결과가 수렴할 때 단일 연구의 내적 타당도는 현저히 강화된다.',
        '- Jick, T. D. (1979). Mixing qualitative and quantitative methods: Triangulation in action. *Administrative Science Quarterly*, 24(4), 602-611. DOI: 10.2307/2392366',
    ]

    replace_file(main_fname, transforms_main, delete_lines=delete_lines_main)
else:
    print('  ERROR: 데이터분析 doc not found')


print('\n=== 2. README.md ===')

transforms_readme = [
    # Table row title
    ('**Triangulation 기반 강건성 검증**',
     '**다층 교차 검증 기반 강건성 검증**'),

    # Subsample note in bullet
    ('(데이터 삼각검증)', '(하위표본 간 일관성 검증)'),

    # Section heading
    ('## Triangulation 강건성 체계',
     '## 다층 교차 검증 강건성 체계'),

    # Table header
    ('| 삼각검증 유형 | 장치 | 수렴하는 결론 |',
     '| 교차 검증 유형 | 장치 | 수렴하는 결론 |'),

    # Table rows
    ('| 방법론 삼각검증 |', '| 방법론 간 결론 수렴 검증 |'),
    ('| 데이터 삼각검증 |', '| 하위표본 간 결과 일관성 검증 |'),
    ('| 지표 삼각검증 |', '| 중요도 지표 간 일관성 검증 |'),

    # Generic
    ('방법론 삼각검증', '방법론 간 결론 수렴 검증'),
    ('데이터 삼각검증', '하위표본 간 결과 일관성 검증'),
    ('지표 삼각검증', '중요도 지표 간 일관성 검증'),
    ('삼각검증', '교차 검증'),
    ('Triangulation', '다층 교차 검증'),
]

replace_file('README.md', transforms_readme)


print('\n=== 3. docs/참고논문_정리.md ===')

refs_fname = None
for f in os.listdir('docs'):
    try:
        c = open(f'docs/{f}', encoding='utf-8').read()
        if 'Jick' in c and 'Denzin' in c:
            refs_fname = f'docs/{f}'
    except:
        pass

if refs_fname:
    # Delete entire ## 16. Triangulation 방법론 block
    content = open(refs_fname, encoding='utf-8').read()

    # Remove the entire section from ## 16. through the blank line before next ##
    content = re.sub(
        r'\n## 16\. Triangulation 방법론\n.*?(?=\n## |\Z)',
        '',
        content,
        flags=re.DOTALL
    )

    # Replace remaining mentions
    transforms_refs = [
        ('방법론 삼각검증', '방법론 간 결론 수렴 검증'),
        ('데이터 삼각검증', '하위표본 간 결과 일관성 검증'),
        ('지표 삼각검증', '중요도 지표 간 일관성 검증'),
        ('삼각검증', '다층 교차 검증'),
        ('Triangulation', '다층 교차 검증'),
    ]
    for old, new in transforms_refs:
        content = content.replace(old, new)

    open(refs_fname, 'w', encoding='utf-8').write(content)
    print(f'  Updated: {refs_fname}')
else:
    print('  ERROR: 참고논문_정리.md not found')


print('\n=== 4. docs/ML_성능_방어_전략.md ===')
ml_fname = None
for f in os.listdir('docs'):
    try:
        c = open(f'docs/{f}', encoding='utf-8').read()
        if 'Triangulation 다중 검증' in c:
            ml_fname = f'docs/{f}'
    except:
        pass

if ml_fname:
    transforms_ml = [
        ('Triangulation 다중 검증', '다층 교차 검증'),
        ('Triangulation', '다층 교차 검증'),
    ]
    replace_file(ml_fname, transforms_ml)

print('\n완료')
