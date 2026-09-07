# Q012g2: 次数別欠陥診断器の代数オラクル — 事前登録 2026-09-08

## 問いと開始条件

Q012g1の全192 caseの保存量診断はcommit `97c109c`で `passed / accepted` と確定した。
元Q012gのH4と有限振幅の欠陥比不達は残っている。次に必要なのは、既存W2/W3の欠陥を
次数ごとに分け、係数の大きさ・異なる次数間の干渉・有理式の残りを区別することである。
ただし、次数抽出器自体の誤りをLBMの原因と取り違えないよう、本問ではその代数を先に検証する。

**問い:** 既知の二次／三次chartと非自明な内部力学を持つ小さな離散写像で、
九次までの合成・有理式の係数・残りを、別記述の厳密有理数オラクルと照合できるか。
本書をcommitしてから新規helper/runnerを実装する。実LBMの診断計算は本問に含めない。
本問が通った後、元の一般方向・holdoutと反例を保持した実LBMの次数別診断を別に事前登録する。

## 変更しないもの

Q012gとQ012g1、全先行scientific source、係数NPZ、固定保存量葉、格子、filter、座標・FFT規約は凍結したままとする。
元Q012gの傾き上限`4.1`、最小振幅比`.1`、holdout欠陥比`.5`を緩めず、元棄却を変更しない。
自然Fourier sparse表現を必須baselineに残す。新しいW4/W9のsolveやTT圧縮を本問で行わない。
「次数9までの欠陥」は、既存三次chartの合成次数が最大9になることに由来し、九次不変多様体ではない。

入力確定の根拠は以下であり、実行前後に変更がないことを照合する。

- Q012g main: `research/artifacts/q012g_d3q27_cubic_chart.json`
  normalized SHA256 `6a201f212b321d8d7b3d4d143306633608c9df4c50c763e05dcd044695002944`
- Q012g1 main: `research/artifacts/q012g1_d3q27_conservation.json`
  normalized SHA256 `ca6b15627880cbe390f6a53bc87eb9a6ba0833f1f370c5b9ea2c494625e75000`
- Q012g1 scientific evidence digest:
  `769f0a6dbed6f4763ca145225caf5c1f9825b7a9e0ab13d679637a9378e134de`

後続の実LBM監査では、Q012g1で検証済みの整数exact集計、丸め済みf*のexact保存量基準、
元float `5e-13`の二進有理数としての上限を採用する。場への投影や基準の交換は行わない。
旧recordとそのlegacy判定も保持する。この後続採用は元Q012gの遡及的な再判定を意味しない。
本問の人工写像には質量保存の意味を持たせず、この物理許容値を人工オラクルの誤差上限へ流用しない。

## 一般の次数演算

経路の係数はascending powerで格納し、Taylorの階乗を既に含む係数として扱う。
既存H2 fiberにさらに`1/2`、H3 fiberにさらに`1/6`を掛けない。

1. 係数列の評価はHorner法、積は畳み込みで求める。
2. sparse monomialの各入力へ多項式経路を代入し、次数ごとの積を畳み込んで出力groupへ足す。
   非零の定数経路も扱い、重複monomial、同一入力の反復、空のsupport、複素係数を検証する。
3. 局所有理式`Q(t)/rho(t)`の係数は、`rho(0) != 0`を確認し、
   `c_n = (Q_n - sum_{j=1}^{min(n,deg rho)} rho_j c_{n-j}) / rho_0`で求める。
   `rho_0=1`をハードコードしない。
4. 九次多項式P9の残りは`[Q-rho*P9]/rho`として保持する。
   分子の低次数の浮動小数点残りも消さず、全係数を保存する。fitや数値差分から係数を推定しない。

実LBMでは局所moment積・densityの除算の後にstream/filterを作用させる必要がある。
本問はその実LBM適用やIEEE実装の解析性を証明するものではない。
実数／有理数式の次数展開と、丸められた物理場の評価との差は後続問で別に照合する。

## 固定する人工離散写像

二座標`a=(x,y)`に対して次のdyadic係数を固定する。

```text
L(a)  = (x/2-y/4, x/4+y/2)
G2(a) = (x*x/8, -x*y/8)
G3(a) = (x*y*y/16, y*y*y/32)
R3(a) = L(a)+G2(a)+G3(a),  R2(a)=L(a)+G2(a)
h2(a) = x*x+x*y/2-y*y/4
h3(a) = x*x*x/4-x*y*y/8+y*y*y/16
h(a)  = h2(a)+h3(a)
rho(a)= 1+x/4-y/8+x*x/16+y*y*y/32
Q(a)  = x*x*x*x+x*x*x*y/2-x*y*y*y/4+y*y*y*y*y*y/8
F(a)  = Q(a)/rho(a)
W3(a) = (x,y,h(a)),  W2(a)=(x,y,h2(a))
Phi(x,y,z) = (R3_1(a), R3_2(a), h(R3(a))+(z-h(a))/8+F(a))
```

線形内部固有値は`1/2 +/- i/4`、graph外方向は`1/8`である。
定義から`Phi(W3(a))-W3(R3(a))=(0,0,F(a))`が厳密に成り立ち、Fは次数4から始まる。
これは既知の三次不変jetであって、W3が厳密に不変という設計ではない。
W2/R2では同じPhiを使い、G3をPhiから落とさない。
したがって、二次chartの欠陥には内部成分のG3と、合成からの三次以上の項が残る。

方向は`(1,0),(0,1),(1,1),(1,-1),(2,1),(-1,2)`の6本とし、正規化しない。
振幅は`1/128,1/64,1/32,1/16`、符号は`-1,+1`、chart次数は`2,3`。
全96 caseを対象とする。方向を結果に合わせて除外・追加しない。
全caseでdensityを確認し、零・非有限値なら失敗を保存する。

## 独立オラクルと判定

primaryは新規のNumPy係数列／grouped monomial演算を用いる。
referenceはPython Fractionのscalar多項式を別記述し、NumPyの畳み込み・合成器を呼ばない。
有理式の逆数はprimaryの漸化式ではなく、有限幾何級数
`rho_0^-1 sum_{k=0}^9 (-(rho-rho_0)/rho_0)^k`を次数9へ切って作る。
direction・係数・振幅は全て二進有理数としてexactに扱う。
全reference係数とcase値は正規化された分子／分母文字列で保存し、表示用floatと分離する。

validityは入力封印、実行前後の新規source一致、6方向×2次数の全係数、96 caseのcoverage、
有限な記録、全saved値の読戻し、人工対照・別記述referenceの独立性とする。
H1は全係数・全caseの比較で成立することとし、比較を二つに分ける。

- 係数: `max(abs(actual-reference)) <= 5e-13 * max(1,max(abs(reference)))`。
- case値・残りidentity: `max(abs(actual-reference)) <= 256*eps*scale`。
  `eps`はbinary64 machine epsilon。`scale`は1と、そのcaseのPhi、W(R)、P9、
  有理式の残り各ベクトルの最大絶対成分との最大値とする。値とscaleを必ず保存する。

これらは小さい人工写像の演算誤差基準であり、実LBMのvector予測精度の基準ではない。
P9単独が有限振幅のexact欠陥に一致することは要求しない。P9と有理式の残りを分けて照合する。
normだけを比較せず、符号付き全成分を照合する。exactに消える低次数も保持する。

人工対照は以下を含む。

- `(1,0)`の三次欠陥の次数4–9は`1,-1/4,0,1/64,-1/256,0`。
- 混合方向で`h(R3)`の次数9が非零となること。
- 三次monomialのfactorを誤って`1/6`にする対照、G3を落とす対照が検出されること。
- 非零定数density、非零定数経路、空support、複素係数、反復・重複monomial。
- 零denominator、不正shape/dtype/index、NaN/Inf、overflowを拒否すること。
- 人工的な低次数残りをremainder分子から消さないこと。
- 最後の方向・次数・成分の改変やcase欠測で保存後監査が失敗すること。

validityが通りH1成立ならaccepted、validity通過かつH1不成立ならrejected、validity不足ならinconclusive。
不合格を許容値の変更や丸めによる0への置換で消さない。
本問を受理しても、65³の傾き超過や比5.834018の原因を説明できたとはしない。

実装予定は`research/polynomial_path.py`、`research/q012g2_cubic_defect_oracle.py`と専用テスト。
本書作成時点では未実装・未実験。受理後に、LBMへの接続・全元方向でのvector誤差・
Gramによる次数間干渉・元判定の再現を対象とする次問を登録する。
