# 건설현장 산업재해 발생 영향 요인 분석

제13회 안전보건 논문공모전 출품작

## 연구 질문 (RQ)

> 건설현장의 내부 안전 관리와 실질적 안전 행동이 산업재해 발생에 미치는 영향 — 외부 기관의 조절효과를 중심으로

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
| 2+ | LR 타당성 검증 | Hosmer-Lemeshow 검정, FDR 보정, 표준화 OR |
| 3 | 머신러닝 모델 비교 | RF / XGBoost / LightGBM + SMOTENC + 5-Fold CV |
| 3+ | ML 타당성 검증 | Bootstrap 95% CI, McNemar 검정, Sensitivity Analysis (5 seeds), Ablation Study |
| 4 | SHAP 분석 | TreeExplainer, Summary/Bar/Dependence Plot, LR-SHAP 교차검증 |
| 4+ | 변수중요도 삼중검증 | SHAP × Permutation Importance × LR p-value |

## 주요 결과

- **독립변수**: 정리정돈상태(OR=0.792, p=0.031) — FDR 보정 후 p=0.098(10% 수준), SHAP·PI 삼중 교차검증으로 보호 효과 경향 지지
- **통제변수**: 공사규모, 기성공정률, 공사종류, 외국인비율이 사고발생에 가장 강한 영향 (FDR 보정 후에도 유의미)
- **조절효과**: 인증보유 × 고용노동부감독 상호작용항 유의미(OR=2.081, p=0.022) — 선택편향으로 해석
- **최적 ML 모델**: Random Forest — F1=0.543 (95% CI: 0.455–0.621), ROC-AUC=0.714, McNemar p=0.0303으로 XGBoost 대비 유의미한 우위
- **모델 안정성**: Sensitivity Analysis (5 seeds) F1=0.551±0.019 — seed 의존성 없음
- **SMOTENC 검증**: Ablation Study에서 SMOTENC가 class_weight 대비 Recall 5.7%p 추가 향상 확인
- **LR 모형 적합**: Hosmer-Lemeshow p=0.2017 — Model 4 적합도 검증 통과
- **SHAP Top-3**: 기성공정률 > 외국인비율 > 공사종류

## 파일 구조

```
Safety-13th-Thesis-Competition/
├── README.md
├── .gitignore
├── data/
│   └── 전처리_최종.csv              # 전처리 완료 데이터 (1,375 × 17)
├── notebooks/
│   ├── 01_전처리.ipynb              # 원자료 → 전처리_최종.csv
│   └── 02_데이터분석.ipynb          # Phase 1~4 전체 분석
├── docs/
│   ├── 데이터분석_과정_및_근거.md   # 분석 설계 및 결과 해석 (SCI 검증 포함)
│   ├── 전처리_근거_및_과정.md       # 전처리 단계별 근거
│   ├── 통계_용어집.md               # 주요 통계 지표 해석 가이드
│   └── 참고논문_정리.md             # 참고문헌 정리
└── results/
    └── (분석 실행 후 생성되는 이미지/CSV 파일)
```
