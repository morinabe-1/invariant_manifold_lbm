# Q012c: D3Q27 first-shell quadratic preflight — 事前登録 2026-09-07

Q012bの局所Fourier cluster分離から非零波数W/Rへ進む前に、固定保存量葉上の
二次homological operatorと全格子の減衰率順序を別々に検査する。
対象は周期・無外力・**無変更のD3Q27 BGK**であり、このgateではfilterを加えない。

## 前提・対象

- Q012b artifact改行正規化SHA-256:
  `53753f2d2344d5ec308a7498875703f0c89ae8d184ade1d8f19377ffbc10b870`。
  result digest:
  `b26abf59676f6689216f9143068d7a06dfad432faf7c723e9ab4b3fec3fa632d`。
  runner／helper sealと`accepted`、Q012b入力checkerも照合する。
  これは封印済み前提の照合であって過去の全trajectoryの再実行ではない。
- odd grid `N=(17,33,65)`、omega `(1.0,1.2,1.5,1.8)`。
- nested selected-wave setsは整数波数`n in {-1,0,1}^3`、
  `0 < |n|^2 <= s`、`s=(1,2,3)`。各波数のhydrodynamic 4次元clusterを全部含める。
  波数数`6/18/26`、共役制約後の実座標数`24/72/104`、合計36条件。
- `delta M=delta Px=delta Py=delta Pz=0`。`k=0`の4保存座標は含めない。
  zero-wave outputのambientを`ker M`（23次元）へ制限し、kinetic補正だけを許す。
- axis／face／bodyの代表では`0`からstep `<=0.0125`の連続pathを使いQ012bと同じ
  閾値を通す。残る波数へはsigned axis permutationで輸送し、symbol covarianceを照合する。

## ブロックと二次演算子

各波数の入力座標はshear **2次元Schur平面**と、分離したacoustic 1次元×2から作る。
shear内部の固有vectorの選択や対角化は行わない。各blockはorthonormalにし、
結合した4列frameのcondition number `<=100`、invariance／左右duality／共役と立方対称性の
部分空間誤差 `<=5e-12`を要求する。scalar acousticはimaginary partの符号で対応させる。

全unordered **block** pairを列挙する。異なるblockには通常のtensor product、同一blockには
orthonormal symmetric squareを使う。block数`18/54/78`、pair数`171/1485/3081`、
product次元の総和が`m(m+1)/2 = 300/2628/5460`となることを検査する。
Fourier outputは`n_i+n_j mod N`。非selected outputを縮約座標へ無条件追加しない。

selected outputではspectral projector `P` のkernelをexternal invariant subspaceにする。
そのorthonormal basisを`Qe`、external blockを`Ae=Qe* A Qe`、入力のproduct dynamicsを`Dij`とする。
入力Hessian forcingは解析平衡Hessianへ保存momentを適用し、output波数のstreaming phaseを掛ける。

\[
 A_e H-H D_{ij}=-B_e,\qquad
 B_e=Q_e^*(I-P)D^2\Phi[V_i,V_j],
\]

\[
 L_{ij}=I\otimes A_e-D_{ij}^{T}\otimes I.
\]

zero-waveでは`Qe`が23次元のkinetic basis、`P=0`。他の非selected outputでは27次元全体を使う。
最大operatorは108×108で、全格子のdense Kronecker行列は作らない。
nested候補で入力pairとoutputのselected／external状態が同一なら同じ計算を再利用してよい。
全pairの個別recordとcoverageは保持し、未評価のpairをpassと扱わない。

各operatorのfull SVDでrank、condition、最小特異値、product spectrumとのdetuningを保存する。
rank thresholdは`100 eps max(shape) sigma_max`、実用condition上限は`1e8`。
singular時には左nullspaceへのforcing投影を記録し、
`||U_null* B|| <= 1e-10 max(1,||B||)`ならnumerically compatible、他はincompatibleとする。
compatibleでも一意な二次非共鳴gateは通さない。
非singular solveはforcing-relative residual `<=1e-10`、graph gaugeとzero-wave保存momentは
`<=5e-12 max(1,||H||)`を要求する。弱くforcedされたnear resonanceのresponseも保存し、
symbol-local座標とglobal-l2-isometric座標（3Dでは`N^(-3/2)`倍）を区別する。

独立対照は、Sym²の多項式作用、列優先vectorizationによるSylvester作用、既知の複素block map、
exact singularのcompatible／incompatible両例、shear平面のunitary basis変更、
実空間mixed finite difference（seed `2026090706`、step `1e-3,5e-4,2.5e-4`、
Hessian relative誤差 `<=1e-5`）である。解析Hessianの保存momentは`<=5e-12`。

## 全格子のnormal orderingと非正規性

全離散波数を48立方対称orbitの代表へ集約し、multiplicityで全個数を復元する。
zero-waveの保存4個を除くambient次元は`27 N^3 - 4`、external数はさらに`m`を引く。
代表で27次eigを評価し、selected waveでは4次元clusterを除外側から明示的に取り除く。
small 5³ gridでは別のbrute-force全波数計算と比較する。

\[
 g_N=\min_{selected}|\lambda|-\max_{external}|\lambda|.
\]

`g_N>1e-10`、全selectedが`0<|lambda|<1`、external最大`<1-1e-12`を
linear normal-ordering必要条件とする。最悪のselected／external波数と固有値、`N^2 g_N`を保存する。
selected projector norm／local Schur sepはQ012bの上限100／下限0.02を保持する。
external restrictionの最大Euclidean one-step normも測定するが、norm>1だけで不存在とはしない。
減衰率順序の通過だけで非線形normal attractionを認証しない。

## 判定・停止・次の問い

入力seal、全36条件、pair次元・grid multiplicity、構造・対照検証、finite JSONがvalidity gate。
失敗時は`inconclusive`として実装または数値検証の原因を直す。
有効な各条件を`coefficient_prequalified`と`normal_ordering_prequalified`の二軸で分類する。
同じshell・omegaが全3格子で両方を満たす場合だけjointly viable familyとする。
その場合は最少実座標数、次いで最小omegaの登録順で一つ選び、Q012dのdense quadratic W/Rへ進む。
全familyが通らなければjoint prequalificationを`rejected`とし、障害を記録して別gateで修正案を検証する。
単に係数が解ける候補は保持するが、それをnormal-attracting SSMへ読み替えない。

二次sector条件は高次のfull-spectrum非共鳴でも存在定理でもない。
一般定理のspectral条件とjet計算を区別する根拠として
[Cabré–Fontich–de la Llave, Part I, Theorem 1.1](https://web.mat.upc.edu/xavier.cabre/docs/indi1jour.pdf)
を再確認した。Q012cはこの定理の全仮定を検証するgateではない。

実装は`research/d3q27_quadratic.py`、runnerは`research/q012c_d3q27_preflight.py`、
成果物は`research/artifacts/q012c_d3q27_preflight.json`。

## Q012c結果（2026-09-07）

事前登録`36e978d`の全8 validity gateを通過したが、jointly viable familyは`0/12`だった。
結果は **`passed / rejected`**。計算の失敗・研究全体の棄却・多様体不存在の証明ではなく、
登録した無変更BGKの3種類のfirst-shell候補が二つの必要なscreenを同時に通らなかった結果である。
候補や閾値は変更しない。

### Coverageと独立検証

- 36条件、延べ56,844 unordered block pair、100,656 product-coordinate列を評価した。
  shearを2次元のまま保持し、最大operatorは108×108だった。
- 12組の全26 wave frameで、最大condition `1.79852`、最大構造残差`6.13651e-14`。
  最大projector norm `2.11200`、最小local Schur sep `0.747594`。
- coefficient側の最大構造残差は`1.66718e-14`。zero-wave outputは全て23次元kinetic blockで、
  保存momentとgraph gaugeを通過した。
- known complex-block solution誤差`5.85096e-16`、shear unitary basis変更の誤差`9.97034e-16`。
  physical mixed FD誤差はstep `1e-3,5e-4,2.5e-4`で
  `2.76941e-7,6.92880e-8,1.86062e-8`となった。
- full 5³ fixed-leaf brute-forceとの最大modulus差`9.99201e-16`。
  追加の17³全波数回帰でも、各selected shellの除外処理・normal gapがorbit計算と一致した。
- Q012cの18テスト（全36条件の数値再計算・保存artifact照合を含む）は123.22 sで通過。
  追加17³全波数テスト1件も通過。D3Q27基礎・D2Q9・manufactured oracleの86回帰テスト、
  3 Pythonファイルのruff検査も通過した。

### 二つのscreenは異なる理由で失敗した

各cellは3格子中の**二次計算通過数**である。これはnormal orderingの通過数ではない。

| omega | 軸のみ・24実座標 | 面対角まで・72実座標 | first shell全体・104実座標 |
|---|---:|---:|---:|
| 1.0 | 0/3 | 0/3 | 2/3 |
| 1.2 | 0/3 | 2/3 | 3/3 |
| 1.5 | 0/3 | 2/3 | 2/3 |
| 1.8 | 0/3 | 0/3 | 1/3 |

軸のみの24実座標はnormal orderingを全12条件で通過したが、各条件に少なくとも24件の
numerically singular-compatible pairが残った。例えば`N=17, omega=1.2`の
`(-1,0,0) acoustic_plus + (0,-1,0) acoustic_minus -> (-1,-1,0)`では、
`sigma_min=1.38985e-15`、rank threshold `1.32385e-12`、forcing norm `0.814042`、
左null forcing norm `7.84092e-16`となった。数値的にcompatibleでも非共鳴・一意なsolveには
数えない。`omega=1`ではさらにincompatible pairが軸候補に12件、72実座標候補に24件あった。
これらはfloat64のrank判定であり、exact resonanceを厳密に認証した結果ではない。

72／104実座標ではnormal orderingが**全24条件で失敗**し、全ての最大external modeは
軸near-Nyquist orbit `sort(|n|)=(0,0,(N-1)/2)`だった。
二次計算を全3格子で通した唯一のfamily `104実座標, omega=1.2`でも次の負のgapが残る。

| N | selected最小modulus | external最大modulus | normal gap | N² × gap | 最大二次condition |
|---|---:|---:|---:|---:|---:|
| 17 | 0.953854241 | 0.983046508 | -0.0291922673 | -8.43657 | 14,356.9 |
| 33 | 0.987874715 | 0.995477066 | -0.0076023506 | -8.27896 | 204,008 |
| 65 | 0.996882625 | 0.998832568 | -0.0019499435 | -8.23851 | 3,068,758 |

odd gridへの限定は厳密なNyquist centerを除いたが、その近傍の遅いexternal modeを除かない。
最大external Euclidean one-step normは`3.04400`だった。これは非正規性の診断値であり、
その値だけから存在・不存在や適応計量での吸引性を結論しない。

### 悪条件化とsolve残差を混同しない

`N=65, omega=1.8, 104実座標`では48 pairがcondition上限`1e8`を超えた。
最悪例は`(-1,-1,-1) shear × (1,0,-1) shear -> (0,-1,-2)`で、
108次operatorの`condition=2.58670e8`、`sigma_min=1.27832e-8`、
forcing norm `20.9445`、局所response norm `1.87685e7`だった。
global-l2正規化後も`35,814.5`であり、単なる座標正規化の違いとして無視しない。
これは初期chartの有効振幅やgrid依存性を別に調べる必要がある証拠である。

さらに、condition上限内でもforcing-relative solve残差`1e-10`を落としたpairがある。
例えば`N=65, omega=1.5, 104実座標`は全3,081 pairがnumerically nonsingularで
最大condition `1.43319e7`だが、30件が残差gateを落とし、最大残差は`1.38319e-10`だった。
artifactの`nonsingular_practical`はrank／condition分類だけであり、`passed`はsolve残差も要求する。
この棄却を「全て解けた」と集約しない。また、solve精度の棄却をexact resonanceや多様体不存在としない。

### 改善の方向と未完事項

Q012dのjointly-prequalified dense chartへは進まない。次はQ012c1で、同じ104実座標候補を
保持してhigh-wave damping修正を比較し、normal gap、全二次sector、解の残差を再検証する。
修正mapと無変更BGKは別対象として保存する。単純なLaplacian filterはsmall-k粘性も変えるため、
保存量だけでなくleading-order hydrodynamicsへの影響も事前に定義する。
high-wave減衰だけで上記shear interactionの悪条件化が直るとは仮定しない。
必要なら未変更operatorでの精度改善を独立に比較し、旧残差判定を保持する。

104実座標・omega=1.2はcoefficient-only候補として残すが、normal-attracting SSMの
代替受理はしない。非零波数W/Rの非線形残差・rollout、存在・半径、3D sparse／TT費用、
Taylor–Green、force／wallは未完である。

成果物は全pairをcolumn名と数値rowのJSON tableとして保存した（20,304,961 bytes）。
[artifact](../research/artifacts/q012c_d3q27_preflight.json)の改行正規化SHA-256:
`3dc9da853cbea183546d5646916e50828faaa89156ca217d16e1b6dc68cf886d`。
result digest:
`79a17890a273ca26ab297a8c98a0fe550b8eae1fedc74f3a2452c836f39b3863`。
runner／quadratic helper SHA-256:
`5d135f03939c3d4d9b519750a3f18c0c5a3b8e8800284cbe1e566dc129ab2df2` /
`e096e42739a59735752375b09ee362281d887b50733c721e41729802cafb54bc`。

```powershell
python -m pytest tests/test_d3q27_quadratic.py -q
python -m research.q012c_d3q27_preflight --output research/artifacts/q012c_d3q27_preflight.json
```
