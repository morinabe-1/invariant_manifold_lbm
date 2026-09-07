# 研究の到達点 — 2026-09-07

現在はD3Q27への段階的拡張に入った。Q012a/bは通過したが、Q012cの無変更BGK
first-shell候補は二次計算とnormal orderingを同時に通らなかった。研究全体は継続中で、
3D非零波数の縮約モデルやTTの優位性はまだ示していない。

| 課題 | 到達点と次の行動 |
|---|---|
| 別系統での研究基盤 | `tt_invariant_manifold_lbm`。既存tciから独立。理論整理と詳細設計を保存 |
| D2Q9の縮約 | 固定保存量葉のdense quadraticからquarticまで構築。残差・限定領域でのshadowingを検証 |
| 存在・半径 | Q007系の固定17²・指定map／norm／tubeについて認証。実用半径・grid-uniform性へ一般化しない |
| TT表現 | Q008/Q010、forced系Q011gの登録TT候補は自然Fourier sparse baselineに敗れた。疎表現を採用 |
| repaired mapの高次滑らかさ | Q011no ordinal 149は個別区間分割で改善なし。Q011np位相監査、degrees 34--90は未解決 |
| D3Q27基礎 | Q012a accepted。216有理moment、48立方対称操作、z独立D2Q9 lift、center二次残差次数3 |
| D3Q27スペクトル | Q012b accepted。16 pathのprefix、二重shear平面、odd unit count 4／even 7。全方位・normal attractionの証明ではない |
| D3Q27非零波数preflight | Q012c passed/rejected。36条件・56,844 block pair、jointly viable 0/12 family。104座標・omega=1.2は二次計算のみ3格子通過 |
| 次の主課題 | Q012c1: 104座標を保つhigh-wave damping修正とleading hydrodynamics、全二次sectorの精度を検証。元BGKの棄却は保持 |
| さらに必要 | 3D rollout／positivity／conservation、3D sparse／TT費用評価、Taylor–Green、force／wall |

Q005の元isotropic候補の棄却、Q006iの元保存量閾値による棄却、TT圧縮の棄却を保持する。
Q012の着手条件は後続の修正候補と個別gateを照合して判定した。詳細な対応は
[Q012a設計](../docs/D3Q27_FOUNDATION.md)にある。高次非共鳴の個別signature監査が
3D基礎代数の唯一の前提である、という直列順序にはしない。
Q012bのcutoffとその限界は[スペクトル検証結果](../docs/D3Q27_SPECTRAL_GATE.md)を参照。
Q012cの共鳴・near-Nyquist・悪条件化の切り分けは
[二次preflight結果](../docs/D3Q27_QUADRATIC_PREFLIGHT.md)を参照。

再現コマンド（repository root）:

```powershell
python -m pytest tests/test_d3q27_foundation.py tests/test_d3q27_spectral.py tests/test_d2q9.py tests/test_manufactured.py -q
python -m research.q012a_d3q27_foundation --output research/artifacts/q012a_d3q27_foundation.json
python -m research.q012b_d3q27_spectral --output research/artifacts/q012b_d3q27_spectral.json
python -m pytest tests/test_d3q27_quadratic.py -q
python -m research.q012c_d3q27_preflight --output research/artifacts/q012c_d3q27_preflight.json
```

成果物再生成では時刻が変わるためファイル全体hashは変わる。科学的な再現照合は、
`cycle.result_digest_sha256`とhelper／runnerのsource hashを比較する。
既存artifactを変更する場合は新たな実験記録として扱う。
