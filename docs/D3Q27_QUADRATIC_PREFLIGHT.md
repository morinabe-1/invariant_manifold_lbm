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
