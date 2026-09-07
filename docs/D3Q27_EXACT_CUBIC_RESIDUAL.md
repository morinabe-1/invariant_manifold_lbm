# Q012f1a: 丸め済み三次方程式の厳密残差監査

## 2026-09-07 事前登録

Q012f1は65³のrefined解でraw20・paired17 armの外部float64残差を落とした。
同じ解の128-bit残差は全件`1e-10`以内だったが、元判定は棄却のまま固定した。
今回は係数を修正せず、残差評価の丸めと保存された解の方程式誤差を厳密に分離する。

### 対象と不変な入力

- Q012f1の選択全324 block triple、65³、raw/pairedのrefined解、計648 case。
- 元20/17 armの失敗と、その32個の異なるtripleを全て含む。成功対も省略しない。
- 全104実座標・26波数、四階filter付きmap `omega=1.5, eta=.02, power=2`、固定保存量葉。
- 元の二次入力・A/D/F・refined解Xをfreshに再構築する。元のproblem配列・X・応答・
  固定3回補正historyのhash/数値と全648 caseで一致を要求し、新しいsolveへ変更しない。
- 元Q012f/Q012f1のartifact・source・判定を上書きしない。今回扱うのは丸め済み外部方程式
  `R = A X - X D + F` であり、厳密LBM symbolや固有空間そのものではない。

### 厳密評価と判定の分解

複素float64の実部・虚部を、二進有理数へexactに変換する。実部と虚部を分けた有理数行列積で
Rを計算する。全成分の二乗和を有理数として保存し、平方根を取らずに基準と比較する。

元のfloat64定数`1e-10`と`1e-14`は、その二進有理数値として明示する。
意味上の十進定数`1/10^10`・`1/10^14`による比較も併記する。どちらか都合のよい方だけを採らない。
次の判定を分離する。

1. `legacy`: 元のfloat64残差・norm・除算で計算した元判定を再現する。
2. `rounded_vector_exact_norm`: float64で作ったR64だけをexactに写し、そのnorm二乗を評価する。
   分母には元の`max(1e-14, norm64(F))`を固定する。norm計算の丸めだけを除く対照。
3. `exact_residual_stored_denominator`: exact Rと同じ元分母を比較する。
   残差の積和の丸めと、右辺のnorm正規化の変更を分離する。
4. `exact_residual_exact_denominator`: 分母二乗も`max(floor^2, sum(abs(F)^2))`としてexactにする。
5. `exact_decimal_constants`: 意味上の十進定数でも同じ二乗判定を行う。

R64とRの差、R128とRの差のnorm二乗、R/R64/Fのexact norm二乗、残差成分のcanonical digestを
保存する。相対normのfloat表示は診断表示だけに使い、厳密gateをfloatへ戻して比較しない。
R128はQ012f1の128-bit評価をfloat64へ格納したものとし、そのexact Rとの差を
`norm(R128-R)/max(floor,norm(F)) <= 1e-24`で検査する。128-bit全桁の正しさとは呼ばない。

### 独立性と保存

主計算はGMP有理数の行列積とする。別プロセスでは、保存した全float64行列をIEEE754の
sign/exponent/mantissaから独立にdecodeし、共通の2冪分母を払った整数行列積で全648 caseを
再計算する。主計算の有理数変換・残差生成関数を独立計算へ流用しない。
exact R・R64・R128との差とnorm二乗・gate・digestが全件一致することを要求する。
数値配列をpickle不要のNPZへ保存し、各entryのshape/dtype/hashとarchive byte hashを固定する。
別プロセスの全数照合は保存した行列のexact演算の独立検証であり、全LBM solveの別プロセス再実行ではない。

既知の複素有理数行列、float64積で消える`2^-104`残差、zero forcing、subnormal入力を対照にする。
さらに閾値の内側・境界・外側と、float64残差だけなら誤って通る負の対照を置く。
非有限・shape不一致・既存artifact上書きは拒否する。全caseを省略せず保存・再集計する。

### 仮説・判定・次の行動

source/input seal、全648配列の一致、制御例、全coverage、有限性、legacy再現、NPZ roundtrip、
独立整数計算の全数一致、R128照合をvalidityとする。仮説は次の二つ。

- H1: 両入力・全324組のexact residualが元の保存分母・exact分母・十進定数の全てで基準内。
- H2: 元20/17 armは、R64のexact normでも不合格だが、同じ分母のexact Rでは通る。
  すなわち元37件の判定差はnorm・閾値緩和ではなく、残差積和の丸めで説明される。
  それ以外のcaseに新しいexact residual不合格はない。

validity通過かつ両仮説通過なら、この丸め済み方程式の診断範囲でaccepted。
validity通過で仮説不合格ならrejected、validity不通過ならinconclusiveとする。
元float64 gateは残したまま、厳密評価を別の判定列として保存する。
acceptedならQ012f2でpaired入力・refined solve・検証済み残差評価を用い、三格子の
全三次preflightを再検証する。rejectedなら全失敗familyをまとめて分析する。
三次chart評価器・有限振幅改善・SSM存在・厳密symbolの非共鳴・TT優位性は認証しない。

## 2026-09-07 結果

事前登録commitは`890c432`。全9 validity gateとH1/H2が通り、`passed / accepted`となった。
元Q012f1の全648 caseについて、二次入力、problem配列、refined解、population応答、
固定3回補正history、元残差値が一致した。全104実座標・map・固定保存量葉は変更していない。

判定列ごとの不合格数は次の通りである。各入力324 caseを省略せず評価した。

| 判定列 | raw | paired |
|---|---:|---:|
| 元float64残差・norm・分母 | 20 | 17 |
| R64のnormだけexact、元分母 | 20 | 17 |
| exact R、元分母 | 0 | 0 |
| exact R、exact分母、二進定数 | 0 | 0 |
| exact R、exact分母、十進定数 | 0 | 0 |

元37 armは32個の異なるtripleに属する。同じ元分母のまま、残差ベクトルの積和をexactに
することだけで判定が変わり、norm計算の丸めだけを除いても変わらなかった。
したがって、この37件は残差評価の丸めに起因する判定差と切り分けられた。
全648件に新たなexact不合格はなく、元Q012f/Q012f1の棄却はそのまま保持する。

以下の数値はexact二乗normからの**表示用近似値**である。厳密gateは有理数同士で比較した。

| 診断値 | raw | paired |
|---|---:|---:|
| 最大exact相対残差 | 3.245167548326693e-11 | 3.079011002599421e-11 |
| そのtriple ordinal | 71731 | 55031 |
| 最大元float64相対残差 | 1.3357811405332092e-10 | 1.1699491177173276e-10 |
| 最大R64評価誤差／exact分母 | 1.2746108989539855e-10 | 1.1283509297402725e-10 |
| 最大R128格納値の誤差／exact分母 | 2.1292335370403238e-27 | 1.6177888236133328e-27 |

R128照合は全件で登録上限`1e-24`を通った。これはR128をcomplex128へ格納した値の
exact Rへの近さであり、128-bit演算の全桁や厳密LBM symbolの正しさの認証ではない。
単純な残差norm同士の一致だけでなく、複素成分ごとの差を評価した。

元不合格ordinalを全て保存する。

```text
raw (20):
18794, 19208, 26247, 32776, 33367, 45000, 45396, 50764, 54758, 55169,
55382, 58920, 62968, 62992, 63628, 66233, 69264, 69711, 71743, 71914
paired (17):
903, 2205, 17786, 18794, 19190, 19208, 32608, 33385, 33511, 33718,
45627, 50764, 54758, 55169, 63622, 69288, 71731
```

### 独立性・保存・再現範囲

prepared NPZは8,487,838 bytes、648 case × 6配列 = 3,888 entry。
全entryは有限complex128で、pickleを使わず読み戻し、shape/dtype/bytes/hashを照合した。
GMP有理数積に対して、別processのIEEE754 decodeと整数行列積が全648件のproofと一致した。
proofは残差成分のcanonical digest、R/F/R64/R128と両評価誤差の6種のexact norm二乗、
全5判定列とMP128照合を含む。主計算の変換・残差積関数を独立側へ再利用していない。
共通部分はshape/有限性の検査、norm二乗からの判定・serialization・digestである。
既知解、消える積、subnormal、zero forcing、閾値の内外・二種類の境界、float64だけなら
誤って通る／落ちる対照の全10例も通った。

新規27・既存関連301テストは通過した。新規artifactテストは全648件を整数演算で再計算し、
保存されたnorm二乗から全判定を独立に有理数比較した。両入力のexact最悪例をfreshなLBM
係数から再構築し、source／entry metadataの改変、case欠落、同一process replayの拒否も検証した。

独立全数replayは**保存した丸め済み行列問題**に対するものであり、別プロセスでの
LBM chart・全三次solveの全数再構築ではない。元648件へのfresh再構築とhash照合は主processで行った。
丸め済み外部方程式の残差を認証しても、射影前の厳密symbol、固有部分空間、全三次係数、
SSM存在や有限振幅の改善を認証したことにはならない。

### 成果物とseals

- [最終判定](../research/artifacts/q012f1a_d3q27_exact_residual.json)
- [全648 caseの再構築・有理数proof](../research/artifacts/q012f1a_d3q27_exact_residual_prepared.json)
- [全3,888配列](../research/artifacts/q012f1a_d3q27_exact_residual_prepared.npz)
- [別プロセス全数整数replay](../research/artifacts/q012f1a_d3q27_exact_residual_replay.json)

```text
final JSON normalized SHA256:
869831275160a5457e554fff6ed8750410ee734cff99d6c9349f90f38ccd42a4
cycle digest:
5888cfa9b32aae39f05f9cb4db401cb02eff81b6c09f05753c1846014748fc31
prepared JSON normalized SHA256:
eda749214a3f2fc147e5688d235b251e3543fcd4dc232477f10185d394a8ac64
prepared result digest:
b1ffcd9c77db2d1a981624efa0c03605f51646e60d19c97137e19b9321056a66
NPZ raw-byte SHA256:
32ab8e4661fe7b3eb87efeb62758137e0dc6d78010469749289a8a56be428765
integer replay normalized SHA256:
67b4afba836c7204abc4b4c7c6bb24239a20827dfbe27a405791d95cf544fb87
integer evidence digest:
acd1e74accb69d5280d742a0fc7971bdc9d4f4b8950dd1d7f6e5ee8817976283
helper normalized SHA256:
8dfa7f053a1e8d7aa924ba761a69c7f97d7c98a65bc31aeef68a6c58e01f5925
runner normalized SHA256:
5263976de1b43ab85db3620faac6c60f950b873a724073e249c34225ba05e2c3
```

再生成は既存fileを上書きしない別pathで、3つの独立commandとして実行する。

```powershell
python -m research.q012f1a_d3q27_exact_residual --prepare-output research/replays/q012f1a_prepared.json
python -m research.q012f1a_d3q27_exact_residual --worker-output research/replays/q012f1a_worker.json --prepared research/replays/q012f1a_prepared.json
python -m research.q012f1a_d3q27_exact_residual --output research/replays/q012f1a_exact.json --prepared research/replays/q012f1a_prepared.json --replay research/replays/q012f1a_worker.json
python -m pytest tests/test_d3q27_exact_residual.py tests/test_d3q27_exact_residual_artifact.py -q
```

時刻・PID・出力名を含むfile/cycle digestは再実行で変わる。科学的再現ではsource sealと
全648配列・各caseのproofを照合する。NPZはテキスト改行正規化をせずraw byteで検証する。

次はQ012f2でpaired二次入力・固定3回refined solve・検証済み残差評価を、17³/33³/65³の
全三次preflightへ戻す。この選択組の通過だけでQ012g三次chart評価器へ進めない。
