# 研究の到達点 — 2026-09-08

Q012f2は全三格子・全246,480 block triple・578,760 columnで`passed / accepted`。
全104実座標、四階filter付き`eta=.02, omega=1.5`、固定保存量葉、paired入力・固定3回refinementを保持した。
11 validity gate、2仮説、全数保存後監査、972組の独立fresh/GMP照合を全て通過した。
最大exact外部残差は65³の`3.07901e-11`、最大full残差は`1.16995e-10`で、それぞれ元の上限以内。
H3共役誤差最大は17³/33³/65³で`1.11479e-12 / 1.36351e-11 / 8.80803e-11`、全て`1e-8`以内。
元float64列の65³の17件は全て前段と同じ判定差であり、別列のexact計算で全件通過した。
31実装テスト・16artifactテストを再実行して通過した。Q012f2の主計算は正常終了した。
元Q012f/Q012f1の棄却とQ012f1aの限定的受理を保持し、丸め済み方程式の検証を厳密symbolへ一般化しない。
Q012gは全三格子・全1,248 caseを完了して`passed / rejected`と確定した。
12 validity gate、全generic/holdoutの解像性、独立144 caseの一致、53保存後監査テストが通過した。
H1（実評価・固定葉構造）、H2（全48立方対称性）、H3（独立物理三次式）は通過したが、H4/H5は棄却した。
一般方向gateは17³/33³/65³で64/64、64/64、61/64。65³のindex 34/51が三次傾き上限、52が最小振幅比に不達だった。
有限振幅gateは64/64、32/64、0/64。65³の`.032`全32方向で三次欠陥が二次より大きく、最大比5.834018だった。
全holdoutはpositiveだが、65³では両モデルのW葉・W(R)葉の質量成分が全64 caseで上限を超えた。
3運動量・Phi(W)−Wの保存差はholdoutで上限以内。質量葉の集計誤差は後続Q012g1で、欠陥比とは分けて診断した。
特殊24方向/格子のfitは未解像でnullを保持した。全準備配列は三格子×worker/mainの全6組で元fiberと一致した。
主計算PID 29360／handle 89608とworker PID 33368／handle 81813はいずれもexit 0で終了済み。再pollしない。
Q012g1は全三格子・192 caseを完了して`passed / accepted`。8 validity gateとH1が全て通過した。
旧recordと1,152 fieldを同一に再現し、31,104 population和・4,608成分のexactな符号付き分解を全数監査した。
独立GMP workerの全48 case・288 field・1,152成分・12対照もprimary整数方式と厳密一致した。
元超過256成分は65³の両degree・W/W(R)葉の質量であり、exactな場の誤差と総和だけの交換後は全件が元上限以内だった。
全成分の最大は元集計`5.46839381544819e-13`、exact場誤差`8.804966277311955e-17`、総和交換後`2.1195324866078255e-16`。
65³の基準側集計項はsite平均`+5.322701185384562e-13`で、葉の差へ負号付きで現れる主要項だった。
場を投影せず、基準・閾値・振幅・方向・map・係数を変更していない。exact場誤差が厳密に0という結果ではない。
実装71、worker監査10、main監査10、親Q012g監査53、計144テストが通過した（204.00秒）。Ruff・整形・compileallも通過した。
worker PID 12416／handle 41088は00:08:34 JST、primary PID 5024／handle 14558は00:39:06 JSTにexit 0で終了済み。再pollしない。
物理計算は現在稼働していない。最終親`artifacts/q012g1_d3q27_conservation.json`と三childのSHAを設計書・監査テストへ封印した。
検証範囲は192 holdout caseであり、元Q012g全1,248 caseの保存量再診断・再判定へ一般化しない。
次は[Q012g2](../docs/D3Q27_CUBIC_DEFECT_ORACLE.md)の代数オラクル。九次合成・有理式の残りを別記述のFraction式で検証する。
6方向・4振幅・両符号・二次／三次の96人工caseを事前登録した。新規helper/runner、実LBMの次数別診断は未実装・未実行。
検証済み保存量集計を後続の実LBM監査へ採用する条件も明記した。旧record・旧判定を保持し、新しい高次chartはまだ構築しない。
H4の3方向とH5の欠陥比不達は別の次数別診断に残す。
Q012eの登録振幅`.008, .032`の二次モデル有限sample受理と元Q012d/Q012d1の棄却を保持する。
3DのSSM存在・連続球の実用半径やTTの優位性は未認証である。

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
| 元D3Q27 damping試行 | Q012c1 failed/inconclusiveを保持。4/108条件後に108×108 SVDが不収束 |
| D3Q27 damping修正検証 | Q012c1a accepted。108条件・332,748 pair。例外時SVD代替1件、四階型9/16 familyが3格子で通過。選択eta=.02, omega=1.5 |
| D3Q27二次W/R | Q012d passed/rejected。全3,081 pair・実座標化・独立Hessian・64方向の次数・48 trajectoryは通過。R2なし対照の4方向が傾き上限2.1を超過 |
| D3Q27対照の次数別診断 | Q012d1 passed/rejected。560 sampleを別プロセスで全再現。元振幅域のP3 vector誤差最大3.38%で2%基準を棄却、P4誤差最大7.09e-6。元傾きはC3で再現、小振幅80本の次数は約2 |
| D3Q27有限振幅 | Q012e accepted。224 case・8,416 iterate。選択値.032を独立holdoutで確認。.128は絶対誤差基準内だが半減基準30/32件不達。振幅1以上は初期正値性不合格 |
| D3Q27三次preflight | Q012f passed/rejected。全246,480 triple・578,760 column、17³は通過。33³/65³のH3共役誤差は7.88e-8／5.39e-6で上限1e-8を超過。65³は272件の残差も不合格 |
| D3Q27入力／精度診断 | Q012f1 passed/rejected。5,832 arm、全二次pair・全三次forcingは検証済み。65³のpaired/refined共役誤差8.80803e-11、外部残差は17件不合格。固定96 tripleを別プロセス照合 |
| D3Q27厳密残差診断 | Q012f1a accepted。65³の全648 caseのexact残差を独立整数演算で全数照合。元37件の不合格は残差積和の丸めで説明され、全3種のexact gateは違反0。元判定は保持 |
| D3Q27修正三次preflight | Q012f2 accepted。全246,480組・578,760列のexact残差・full式・共役が通過。独立972組、全行/全fiberの保存後監査も通過。元float64の17件は保持 |
| D3Q27三次W/R | Q012g passed/rejected。全1,248 case、12 validity、独立144 case、53監査テスト通過。H1–H3成立、H4の65³3方向とH5の有限振幅/質量葉が不達 |
| D3Q27保存量診断 | Q012g1 accepted。全192 case・1,152 field・4,608成分、独立48 caseと12対照を監査。元超過256成分を集計誤差へ切り分け。144テスト通過 |
| 次の主課題 | Q012g2: 次数別欠陥の代数オラクルを事前登録。6方向・96人工caseで九次合成と有理式の残りを検証してから実LBM診断へ接続する |
| さらに必要 | 実用振幅・高次／存在認証、3D sparse／TT費用評価、Taylor–Green、force／wall。有限sampleのrollout／正値／保存はQ012dで検証済み |

Q005の元isotropic候補の棄却、Q006iの元保存量閾値による棄却、TT圧縮の棄却を保持する。
Q012の着手条件は後続の修正候補と個別gateを照合して判定した。詳細な対応は
[Q012a設計](../docs/D3Q27_FOUNDATION.md)にある。高次非共鳴の個別signature監査が
3D基礎代数の唯一の前提である、という直列順序にはしない。
Q012bのcutoffとその限界は[スペクトル検証結果](../docs/D3Q27_SPECTRAL_GATE.md)を参照。
Q012cの共鳴・near-Nyquist・悪条件化の切り分けは
[二次preflight結果](../docs/D3Q27_QUADRATIC_PREFLIGHT.md)を参照。
Q012c1の数値backend障害と保存した行列は[damping結果](../docs/D3Q27_DAMPING_REPAIR.md)を参照。
Q012c1aの独立再計算・選択候補・不採用の残差失敗は
[SVD代替と全条件結果](../docs/D3Q27_SVD_FALLBACK.md)を参照。
Q012dの構築・7仮説通過・負の対照失敗と次の診断は
[実座標quadratic chart結果](../docs/D3Q27_QUADRATIC_CHART.md)に保存した。
Q012d1でのnorm傾きとvector精度の切り分け、独立全数replayは
[負の対照の次数別診断](../docs/D3Q27_NEGATIVE_CONTROL_DIAGNOSIS.md)にある。
Q012eの同一初期状態比較、有限sampleの使用範囲と絶対精度の区別は
[有限振幅結果](../docs/D3Q27_PRACTICAL_AMPLITUDE.md)に保存した。
Q012fの全数coverage、二種類の不合格、例外時SVD代替と再現範囲は
[三次preflight結果](../docs/D3Q27_CUBIC_PREFLIGHT.md)に保存した。
Q012f1の二入力×三solver、残った不合格と残差評価の精度差は
[入力／精度診断](../docs/D3Q27_CUBIC_PRECISION_DIAGNOSIS.md)に保存した。
Q012f1aの元判定・厳密判定の分解、全648件の独立照合と丸め済み方程式への限定は
[厳密残差監査](../docs/D3Q27_EXACT_CUBIC_RESIDUAL.md)に保存した。
Q012f2の全数結果、固定済み実装、保存後監査と限定された主張範囲は
[修正候補の全三次preflight](../docs/D3Q27_REFINED_CUBIC_PREFLIGHT.md)に保存した。
Q012gの実座標評価、人工写像、三格子の次数・有限振幅比較と独立再現範囲は
[三次W/R評価の事前登録](../docs/D3Q27_CUBIC_CHART.md)に保存した。

再現コマンド（repository root）:

```powershell
python -m pytest tests/test_d3q27_foundation.py tests/test_d3q27_spectral.py tests/test_d2q9.py tests/test_manufactured.py -q
python -m research.q012a_d3q27_foundation --output research/replays/q012a_d3q27_foundation.json
python -m research.q012b_d3q27_spectral --output research/replays/q012b_d3q27_spectral.json
python -m pytest tests/test_d3q27_quadratic.py -q
python -m research.q012c_d3q27_preflight --output research/replays/q012c_d3q27_preflight.json
python -m pytest tests/test_d3q27_damping.py tests/test_d3q27_damping_artifact.py tests/test_d3q27_svd_fallback.py tests/test_d3q27_damping_complete.py -q
python -m research.q012c1a_d3q27_damping --output research/replays/q012c1a_d3q27_damping.json
python -m pytest tests/test_d3q27_chart.py tests/test_d3q27_chart_artifact.py -q
python -m research.q012d_d3q27_quadratic_chart --output research/replays/q012d_d3q27_quadratic_chart.json
python -m pytest tests/test_d3q27_negative_control.py tests/test_d3q27_negative_control_artifact.py -q
python -m research.q012d1_d3q27_negative_control --worker-output research/replays/q012d1_worker.json
python -m research.q012d1_d3q27_negative_control --output research/replays/q012d1_diagnosis.json --replay research/replays/q012d1_worker.json
python -m pytest tests/test_d3q27_amplitude.py tests/test_d3q27_amplitude_artifact.py -q
python -m research.q012e_d3q27_amplitude --worker-output research/replays/q012e_worker.json
python -m research.q012e_d3q27_amplitude --output research/replays/q012e_amplitude.json --replay research/replays/q012e_worker.json
python -m pytest tests/test_d3q27_cubic.py tests/test_d3q27_cubic_artifact.py -q
python -m research.q012f_d3q27_cubic_preflight --worker-output research/replays/q012f_worker.json
python -m research.q012f_d3q27_cubic_preflight --output research/replays/q012f_cubic.json --replay research/replays/q012f_worker.json
python -m pytest tests/test_d3q27_cubic_precision.py tests/test_d3q27_cubic_precision_artifact.py -q
python -m research.q012f1_d3q27_cubic_precision --worker-output research/replays/q012f1_worker.json
python -m research.q012f1_d3q27_cubic_precision --output research/replays/q012f1_diagnosis.json --replay research/replays/q012f1_worker.json
python -m pytest tests/test_d3q27_exact_residual.py tests/test_d3q27_exact_residual_artifact.py -q
python -m research.q012f1a_d3q27_exact_residual --prepare-output research/replays/q012f1a_prepared.json
python -m research.q012f1a_d3q27_exact_residual --worker-output research/replays/q012f1a_worker.json --prepared research/replays/q012f1a_prepared.json
python -m research.q012f1a_d3q27_exact_residual --output research/replays/q012f1a_exact.json --prepared research/replays/q012f1a_prepared.json --replay research/replays/q012f1a_worker.json
```

成果物再生成では時刻が変わるためファイル全体hashは変わる。科学的な再現照合では、
helper／runnerのsource hashと数値結果を比較する。Q012e/Q012f/Q012f1のcycleにはworkerのprocess ID・
metadata込みhashが含まれるため、caseごとの数値・係数配列hashを照合する。
Q012fの全tripleはgzip JSONLに保存し、圧縮fileのbyte hashと展開record列のdigestを区別する。
Q012f1も同形式で選択全324組/格子の6 armを保存する。全三次tripleの保存とは区別する。
Q012f1aは65³・二入力の648個の丸め済み行列問題をNPZへ保存し、全entry・archive byte hashを
照合する。時刻・PID・出力名を含むdigestではなく、再現した配列と各caseの有理数proofを比較する。
metadataを含まない旧experimentについては、そのresult digestも使用できる。
封印した既存artifactを上書きしないよう、再実行は別の`research/replays/`へ出力する。
元Q012c1を再実行すると数値障害を記録して終了code 1となる。これは事前登録された
108条件が未達であることを示す意図的な不合格で、例外の隠蔽や部分結果の受理ではない。
