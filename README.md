# 건설현장 산업재해 발생 영향 요인 분석

제13회 안전보건 논문공모전 출품작

## 연구 질문 (RQ)

> 건설현장의 내부 안전 관리와 실질적 안전 행동이 산업재해 발생에 미치는 영향 — 외부 기관의 조절효과를 중심으로

## 이론적 배경

| 이론 | 역할 |
|:---|:---|
| **HRO (High Reliability Organizations)** | 내부 안전관리 변수군(정리정돈·위험성평가·작업중지권·위원회·안전조직)의 이론적 정당성 — Weick, Sutcliffe & Obstfeld (1999) |
| **Swiss Cheese Model** | 외부감독 변수의 이론적 위치 및 인증×감독 상호작용항(OR=2.081) 양(+)부호의 선택편향 방어 — Reason (1990, 2000) |
| **사고인과연쇄이론** | 건설안전 도메인 이론적 배경 — Heinrich (1931), Bird (1974) |

## 데이터

**제10차 산업안전보건 실태조사 (건설업, 2021)**

- 원자료: 1,502개 사업장
- 전처리 후: 1,375개 사업장 × 17개 변수
- 출처: 안전보건공단

## 분석 구조

| Phase | 내용 | 방법 |
|:---:|:---|:---|
| 1 | 탐색적 데이터 분석 (EDA) | 기술통계, 단변량 분석(변수별 사고발생률), VIF, 상관관계 히트맵 |
| 2 | 계층적 로지스틱 회귀 | statsmodels Logit, ΔR² 우도비 검정, 조절효과 시각화 |
| 2+ | LR 타당성 검증 | Hosmer-Lemeshow 검정 |
| 3 | 머신러닝 모델 비교 | RF / XGBoost / LightGBM + SMOTENC + 5-Fold CV |
| 3+ | ML 타당성 검증 | Bootstrap 95% CI, Calibration Curve, Ablation Study |
| 4 | SHAP 분석 | TreeExplainer, Summary/Bar/Dependence Plot, LR-SHAP 교차검증 |
| 4+ | 변수중요도 삼중검증 | SHAP × Permutation Importance × LR p-value |
| **5** | **Triangulation 기반 강건성 검증** | **공사규모별·공사종류별 Subsample Robustness (데이터 삼각검증)** |

## 주요 결과

- **독립변수**: 정리정돈상태(OR=0.792, p=0.031) — SHAP·PI 삼중 교차검증으로 보호 효과 경향 지지
- **통제변수**: 공사규모, 기성공정률, 공사종류, 외국인비율이 사고발생에 가장 강한 영향
- **조절효과**: 인증보유 × 고용노동부감독 상호작용항 유의미(OR=2.081, p=0.022) — Swiss Cheese Model 기반 선택편향으로 해석
- **최적 ML 모델**: Random Forest — F1=0.543 (95% CI: 0.455–0.621), ROC-AUC=0.714
- **SMOTENC 방법론적 기여**: Ablation Study에서 class_weight 대비 Recall 5.7%p 추가 향상 확인
- **LR 모형 적합**: Hosmer-Lemeshow p=0.2017 — Model 4 적합도 검증 통과
- **SHAP Top-3**: 기성공정률 > 외국인비율 > 공사종류
- **강건성**: 공사규모별(소·중·대) 및 공사종류별(토목·건축·플랜트) 하위표본에서 핵심 계수 방향 일관성 확인 (데이터 삼각검증)

## Triangulation 강건성 체계

| 삼각검증 유형 | 장치 | 수렴하는 결론 |
|:---|:---|:---|
| 방법론 삼각검증 | LR(추론) + ML(예측) + SHAP(해석) | 통제변수 지배, 정리정돈 보호 방향 |
| 데이터 삼각검증 | 공사규모별·공사종류별 분할분석 | 전 하위표본에서 핵심 계수 방향 일관 |
| 지표 삼각검증 | SHAP × PI × LR p-value | 정리정돈 보호 효과 삼중 확인 |

## 파일 구조

```
Safety-13th-Thesis-Competition/
├── README.md
├── .gitignore
├── data/
│   ├── 전처리_최종.csv                  # 전처리 완료 데이터 (1,375 × 17)
│   ├── 제10차 산업안전보건 실태조사_raw data_건설업_230824.CSV
│   └── external/
│       ├── (참고문헌 PDF 파일들)
│       └── prior_winners/              # 선행 대회 수상작 검토용 (참고문헌 아님)
│           ├── 11회 수상작 논문.pdf
│           └── 12회 수상작 논문.pdf
├── notebooks/
│   ├── 01_전처리.ipynb                  # 원자료 → 전처리_최종.csv
│   └── 02_데이터분석.ipynb              # Phase 1~5 전체 분석
├── docs/
│   ├── 데이터분석_과정_및_근거.md       # 분석 설계 및 결과 해석 (이론적 배경 포함)
│   ├── 전처리_근거_및_과정.md           # 전처리 단계별 근거
│   └── 참고논문_정리.md                 # 참고문헌 정리 (§1~§19)
└── results/
    └── (분석 실행 후 생성되는 이미지/CSV 파일)
```
