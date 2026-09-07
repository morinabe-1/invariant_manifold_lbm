# Q012g1: 三次chartの保存量数値gateの診断 — 条件付き事前登録 2026-09-07

## 問いと実行開始条件

Q012gの独立workerでは、65³の有限振幅全16 caseがsite平均保存量誤差の上限`5e-13`を超えた。
同時に欠陥半減にも15 caseが失敗したが、これらを同じ原因と仮定しない。
本問は保存量の不達だけを、保存されたfloat64場の保存量と、その総和・差・平均の丸めへ切り分ける。
次数別の不変性欠陥と有限振幅の使用領域は次の別問とする。

この文書はQ012g主計算中の設計であり、新しい診断計算の開始を意味しない。
Q012gの全三格子が正常に閉じ、全件保存後監査・144 caseの再現が完了し、親結果をcommitしてから実行する。
親の12 validity gateとgeneric/holdoutの解像性が通過し、保存量不達を含む登録反例が残ることを要求する。
親のvalidityが不十分なら本問を開始せず、その障害を先に診断する。
主計算の準備配列・物理場・費用測定と本問のphysical campaignを同時実行しない。

現在固定できる入力はQ012g helper/runnerの封印、独立worker、17³/33³ mainである。
それらのSHA256は[Q012g](D3Q27_CUBIC_CHART.md)と同一とする。
全mainと65³ childのSHA256、scientific result digest、親の確定判定は、親終了・監査後に追記してcommitする。
その入力封印が完了するまで、本問のhelper/runnerの実装や実LBM診断を開始しない。
この二段階の封印で、未保存の親結果やその合格を仮定しない。

## 固定する物理系と全診断範囲

- `17³, 33³, 65³`、全104実座標、26第一shell、二重shear平面、固定保存量葉を保持する。
- `omega=1.5, eta=.02, power=2`の同じ修正map、同じpaired H2/G2、同じ未投影H3/G3を使う。
- 元NPZ、評価器、map、spectral frame、実座標化、FFT規約を変更しない。
- Q012g seed `2026090725`の全32 holdout方向、振幅`.008, .032`、三格子で192 caseを対象にする。
  各caseで二次/三次モデルのW、Phi(W)、W(R)、計1,152 fieldを診断する。
  保存量差は各モデルのW葉、W(R)葉、Phi(W)−Wについて4成分、計4,608成分比較となる。
- 元の不合格方向だけを選ばず、元の合格例も全て保持する。新しい振幅や方向を探索しない。
- 丸め済み一様平衡場f*も各格子で一度診断する。Q012gと同じpopulation配列を使う。

全192 caseを封印したQ012gのphysical_caseでfreshに再計算し、元mainの全recordと厳密一致させる。
次に監査対象fieldを逐次再生成し、元のshape/dtype/bytes/hashと照合してから総和を診断する。
旧caseを再現できない場合は、そのcaseの保存量差を別の場へ差し替えて説明せずinconclusiveとする。
field全体を全case分保持しない。この再生成は意図的な追加費用であり、Q012gのtimingへ混ぜない。

## 二つの基準保存量とexactな集計

`S(f)=(M,Px,Py,Pz)`を全格子点・populationについての保存量ベクトルとする。
以下のexactとは、生成済みの各float64値を二進有理数として厳密に足すことである。
実数上のLBM、厳密なequilibrium係数、厳密な不変多様体を計算したという意味ではない。

主たる固定葉の基準は、実際に使った丸め済みf*のexactなS(f*)とする。
別に解析的基準`(N³,0,0,0)`との差も保存し、丸め済み基準と解析的基準を混同しない。
元Q012gは丸めた総和S_legacy(f*)を基準にしていたので、その元の値と元判定も残す。

primary集計はIEEE-754 binary64を整数mantissa・指数・符号へ分解する。
有限値は共通単位`2^-1074`の整数へ写せる。指数別にsigned mantissaを集め、各chunkを最大1,024項とする。
各mantissaの絶対値は`2^53-1`以下なので、chunk内のint64和の絶対値は`2^63-1024`以下でoverflowしない。
chunk間と指数間は任意精度整数で加算し、最後までfloatの総和を使わない。
subnormal、正負zero、正負値を扱い、NaN/Infを拒否する。
各populationのexactな和27個を保存し、整数係数`1,cx,cy,cz`から4保存量を作る。
shape、配列の全件coverage、chunk境界、非有限値、overflow防止は人工対照で独立に検証する。

exact値は正規化した有理数の分子/分母文字列で保存し、表示用のfloat近似とは別に扱う。
許容値は**元のPython float `5e-13`をexactな二進有理数へ変換した値**とする。
新しい十進定数や許容誤差へ変更しない。

## 総和・減算・平均の丸めを分解する

比較対象をA,B、格子点数をn=N³とする。W葉とW(R)葉ではB=f*、保存則ではA=Phi(W), B=W。
各成分について次を保存する。

- `SA, SB`: 生成された場のexactな保存量。
- `LA, LB`: Q012gの元の浮動小数点集計結果を、丸め済み値のままexactな数として解釈したもの。
- `dL`: 元の浮動小数点減算の結果。
- `eL`: 元のsite平均誤差の結果。

有理数上で

```text
exact_field_error = (SA - SB) / n
sum_rounding      = ((LA - SA) - (LB - SB)) / n
sub_rounding      = (dL - (LA - LB)) / n
mean_rounding     = eL - dL / n

eL = exact_field_error + sum_rounding + sub_rounding + mean_rounding
```

を全4,608成分で厳密一致させる。各項の符号を残し、絶対値の和だけで原因を説明しない。
sum_roundingはA側とB側も分ける。固定葉ではf*の定数的な集計誤差と場側の誤差を区別できる。

二つの反実仮想も保存する。どちらも物理場やmapは変更せず、集計値だけを交換する。

1. A,B両方の総和をexact sumの最近接float64へ交換し、元と同じfloat減算・平均を行う。
2. 固定葉比較だけで、B=f*の総和のみを交換し、A側の元の総和を保持する。

1は集計方法だけで元の不合格が解消するかを検証する。2は基準平衡の集計誤差の寄与を記述的に調べる。
2の成否を事後的に新しい受理条件にはしない。Phi(W)−Wへf*の補正を適用しない。

## 人工対照と独立process

primary整数集計は、少数要素のPython Fractionによる逐項和と照合する。
正負の相殺、指数の大きな隔たり、subnormal、最大有限値、1,024境界を跨ぐ配列、空配列を含める。
丸め1単位の差を閾値で消さず、不正dtype・非有限値は拒否する。

各格子で一様平衡から次の4種の場を作り、4保存量の既知の変化をexactに検出する。
`delta=2^-36`とし、populationの追加/減算は実際のfloat64場で行う。

- rest population全点にdeltaを追加: site平均質量変化delta、運動量0。
- 各軸iについて、速度+e_iのpopulationへdelta、-e_iへ−delta:
  site平均質量変化0、i方向運動量変化2delta、他の運動量0。

これらの一様平衡populationで加減算がexactに表現できることも確認する。
全12対照は元の`5e-13`を超える違反として検出されなければならない。
この対照を物理モデルの失敗例と混ぜない。

独立workerは三格子の最初の8 holdout方向×2振幅、全48 caseをfreshに再計算する。
同じ封印fiberを使い、旧record・field hashを全て照合する。
集計はprimaryのbit分解/chunkを使わず、各float値の`as_integer_ratio`からGMP有理数を作る逐項和とする。
全288 field・27 populationのexactな和と4保存量、全分解項をprimaryと厳密一致させる。
対照12場も独立に照合する。これは全192 caseや全三次solveの独立再実行ではない。
workerを完了してからprimary全192 caseを実行し、物理計算を同時実行しない。

## 判定・保存・次の行動

validityは、親と全source/係数の封印、全192元record/fieldの再現、全対照、全exact分解identity、
全case coverage、finiteな表示値、全48 caseの独立exact再現、保存後の全数読戻し監査である。
未実行のfieldや失敗行をゼロで埋めない。正規化有理数文字列も全件監査する。

仮説H1は、全192 holdout caseの両モデルでexact_field_errorが元と同じ上限以内となり、
反実仮想1によって集計方法だけを交換した場合も全保存量gateが通ること、とする。
これが通れば、登録範囲の保存量数値不達を集計の丸めへ切り分けられる。
validityが通りH1不合格ならrejected、validityが不足すればinconclusiveとし、原因が残った成分を列挙する。
H1を通すために場へ保存量投影を加えたり、閾値、方向、振幅、基準の定義を途中で変更しない。

元Q012gの判定は変更しない。欠陥比の不合格もこの問では解消していない。
受理した場合は検証済み集計を後続の監査に採用する設計を別途明記し、次は三次不変性欠陥の次数別診断へ進む。
棄却した場合は、残ったexactな場の保存量誤差をcollision/stream/filter/embeddingの段階へ切り分ける問いを登録する。
中心多様体、SSM存在、連続球、長時間trajectory、grid-uniformな実用半径、TT優位性について新しい主張はしない。

実装予定: `research/d3q27_conservation_audit.py`、`research/q012g1_d3q27_conservation.py`。
本書作成時点では未実装・未実験であり、上記の親結果の追加封印とcommitを実行開始の必須条件とする。
