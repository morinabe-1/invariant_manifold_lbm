# 研究の到達点 — 2026-09-07

Q012f2は全三格子・全246,480 block triple・578,760 columnで`passed / accepted`。
全104実座標、四階filter付き`eta=.02, omega=1.5`、固定保存量葉、paired入力・固定3回refinementを保持した。
11 validity gate、2仮説、全数保存後監査、972組の独立fresh/GMP照合を全て通過した。
最大exact外部残差は65³の`3.07901e-11`、最大full残差は`1.16995e-10`で、それぞれ元の上限以内。
H3共役誤差最大は17³/33³/65³で`1.11479e-12 / 1.36351e-11 / 8.80803e-11`、全て`1e-8`以内。
元float64列の65³の17件は全て前段と同じ判定差であり、別列のexact計算で全件通過した。
31実装テスト・16artifactテストを再実行して通過した。Q012f2の主計算は正常終了した。
元Q012f/Q012f1の棄却とQ012f1aの限定的受理を保持し、丸め済み方程式の検証を厳密symbolへ一般化しない。
Q012gの三次W/R評価器と逐次実行器を実装した。新規90＋既存31、計121テストを通過した。
人工graphの最大不変性欠陥2.86624e-17、R3省略／H3倍掛け対照の欠陥1.56678e-5／4.87333e-6を確認した。
独立144 caseは正常終了し、10保存後監査テストを通過した。各格子の最初の8方向は全て次数3→4を満たした。
有限振幅gateは17³/33³/65³で16/16、8/16、0/16。65³は欠陥比15件と保存量数値gate16件が不合格である。
局所次数の改善から有限振幅やgrid-uniformな改善を主張しない。Q012gの総合判定は主計算の全検証後に行う。
2026-09-07 22:00 JSTに全三格子の主計算を開始した（PID 29360、実行handle 89608）。
独立workerのPID 33368／handle 81813はexit 0で終了済み。主計算は同じ二つのsource sealを保って追跡する。
主計算17³・33³は全phaseを完了し、全832 caseを監査した。別processの96 caseも全数値・field hashが一致した。
新規23＋worker監査10の33テストを通過した。一般方向は両格子64/64で次数3→4、holdoutは64/64と32/64。
33³の`.032`全32方向が欠陥半減基準不達、うち5方向は二次より悪化した。両格子のholdout正値・保存量は全件通過。
特殊24方向/格子のfitは未解像でnullを保持し、次数の証拠にしない。65³は同じ主計算で実行中である。
追加7テストで元NPZの全578,760単項式から準備配列を独立再構成し、worker三格子とmain二格子の全fingerprint一致を確認した。
元係数・全indexの同一性を確認したのであり、未保存の65³ main結果や有限振幅の合格を意味しない。
次段のQ012g1は保存量誤差のexactな分解を条件付き設計しただけで、親の終了・監査・追加封印まで実装/実験は開始しない。
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
| 次の主課題 | Q012g: main17³・33³の全832 case監査・独立96 case一致、保存後33テスト通過。一般次数は全件通過、33³有限振幅H5に反例。main65³の全件検証を継続 |
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
