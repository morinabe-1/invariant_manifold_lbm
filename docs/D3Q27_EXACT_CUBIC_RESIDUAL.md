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
