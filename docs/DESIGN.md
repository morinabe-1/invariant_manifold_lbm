# 詳細設計: TT パラメータ化不変多様体による LBM 縮約

Status: design baseline v2

対象順序: D2Q9 → D3Q27

最初の実装条件: periodic / no forcing / isothermal BGK / uniform rest state

## 1. 目的と成功条件

完全状態を

\[
f_n\in\mathbb{R}^{N},\qquad N=N_xN_yQ
\]

とし、collision、forcing、streaming、boundary を含む自律的な 1-step map を

\[
f_{n+1}=\Phi(f_n)
\]

とする。求めるものは

\[
W:\mathcal A\subset\mathbb{R}^{m}\to\mathbb{R}^{N},
\qquad
R:\mathcal A\to\mathbb{R}^{m}
\]

であり、

\[
\boxed{\Phi(W(a))=W(R(a))}
\]

を指定領域 \(\mathcal A\) で満たす。

研究の成功は「TT rank が小さい」だけでは判定しない。少なくとも次を同時に満たす
必要がある。

1. \(W\) が選択した中心・slow subspace に接する。
2. gauge が固定され、\(W,R\) の座標非一意性が除かれている。
3. 独立点上の invariance defect が所定誤差以下である。
4. 保存量、密度、population positivity、Mach 制限を破らない。
5. full/reduced rollout が所定時間まで shadowing する。
6. 多様体外の kinetic perturbation が予測した率で減衰する。
7. dense coefficient oracle と TT 表現が誤差予算内で一致する。
8. offline 構築費を含めた break-even が報告される。
9. D3Q27 への移行時に格子等方性と rank を再測定する。

## 2. 用語を先に固定する

### 2.1 Strict center manifold

離散写像の \(|\lambda|=1\) 一般化固有空間に接する多様体を指す。
D2Q9 の奇数幅周期格子では、一様平衡まわりの物理的 strict center は通常
\(k=0\) の \((\rho,j_x,j_y)\) である。

この3次元族は任意の周期格子で不変だが、偶数 extent では Nyquist の
\(\lambda=-1\) 方向も full center に含まれる。従って「3次元 full strict center」
という呼称は本監査では奇数×奇数の周期正方格子に限定し、偶数格子では
3次元 invariant submanifold と呼ぶ。

これは次に有用である。

- 解析的な一様 equilibrium family がある。
- \(R(a)=a\) が既知である。
- 二次 \(W\) の解析 Hessian がある。
- homological equation と TT 表現の unit test にできる。

一方、空間変動する流体場を表すには小さすぎる。

### 2.2 Slow/spectral invariant manifold

単位円内にあるが kinetic modes より遅く減衰する hydrodynamic modes に接する
候補多様体を指す。本研究の空間的縮約の本命仮説である。Packwood らが扱う
hydrodynamic-field slow manifold と、有限個の低波数 mode を選ぶ spectral
submanifold は同一の対象ではない。後者がこの full LBM map に存在することは
現時点で未証明であり、存在・滑らかさ・一意性に必要な spectral gap、非共鳴、
normal attraction を数値・理論の両面で確認する。

用語上、Q005 の非共鳴・spectral split と、有限領域での invariance、normal
attraction、domain gate を通るまでは candidate slow spectral subspace または
candidate chart と呼ぶ。これらを通過する前に slow manifold の存在を既成事実として
記述しない。

Q005 の結果、Q004b cutoff を radial に埋めた2次元 isotropic set は、二次 external
resonance と near-Nyquist excluded mode により、標準的な nonresonant・normally
attracting SSM 候補として棄却された。二次 forcing は共鳴左 nullspace と直交するため
compatible だが、このことは一意性を回復しない。従って次の stripe 構築も
candidate chart / solver oracle と呼び、full 2D manifold claim と分ける。

### 2.3 Hydrodynamic field manifold

全格子の \(\rho,\boldsymbol j\) を座標とすれば

\[
m=(d+1)N_xN_y
\]

となる。これは population 数を \(Q\) から \(d+1\) へ減らすが、空間次元は
減らさない。TT はこの高次元 field chart を圧縮し得る。

### 2.4 Reduced spatial-mode candidate manifold

低波数 Fourier modes、POD modes などを選び

\[
m\ll (d+1)N_xN_y
\]

とする。本設計はまず周期格子の低波数 Fourier hydrodynamic cluster で candidate
chart を実装する。境界付き問題では Arnoldi/POD へ一般化する。

## 3. Full map \(\Phi\) の契約

操作順序を曖昧にしない。初期 D2Q9 oracle は

\[
\Phi=S\circ C_{\mathrm{BGK}}
\]

すなわち collide-then-stream、periodic boundary、no forcing とする。

一般形は

\[
\Phi=B\circ S\circ F\circ C
\]

を既定とするが、forcing scheme や wall rule が別順序を要求する場合は map descriptor
に明記する。同じ名前の \(\Phi\) で操作順序を変更しない。

full-map interface は概念的に次を提供する。

```text
apply(f) -> f_next
jvp(f, v) -> D Phi(f) v
vjp(f, w) -> D Phi(f)^T w       # Newton/Krylov が必要になった時点
fixed_point(parameters) -> f*
conserved_moments(f) -> c
```

最初は dense Jacobian を小格子で materialize する。大格子では `jvp` を使う。

### 3.1 Reference fixed point

periodic/no-force では

\[
f_{\*,i}=w_i\rho_\*,\qquad \rho_\*=1,\quad \boldsymbol u_\*=0
\]

を使う。

steady forcing または壁がある場合は、まず

\[
\Phi(f_\*)-f_\*=0
\]

を full solver で解き、残差と保存収支を検証する。reference が固定点でないまま
固定点用のパラメータ化法を使わない。

### 3.2 Nonautonomous forcing

時変入力 \(u_n\) がある場合、単一の自律写像 \(\Phi(f)\) ではない。

- 周期 forcing: phase \(\theta\) を状態へ追加した skew product。
- 既知の control: \(W(a,u)\), \(R(a,u)\) または controlled map。
- 任意時系列: autonomous invariant manifold ではなく reduced input-output model。

この区別をせず forcing を hidden state として学習しない。

## 4. 線形スペクトル監査

### 4.1 Periodic D2Q9

一様平衡まわりでは並進不変なので、各 wave vector \(k\) について

\[
A(k)=S(k)C
\]

という \(9\times 9\) block を作る。

BGK collision の \(k=0\) kinetic multiplier は \(1-\omega\) である。
\(\omega\to2\) では \(-1\) に近づき、kinetic direction の normal attraction が弱く
振動的になる。従って \(\omega=1\) 近傍から continuation し、\(\omega\) を上げる
ごとに gap を再監査する。

### 4.2 Mode identity

各右固有ベクトル \(v\) に対して、次の participation を計算する。

\[
p_\rho=\lVert M_\rho v\rVert,\quad
p_j=\lVert M_jv\rVert,\quad
p_\Pi=\lVert M_\Pi v\rVert
\]

analytic/spectral branch identity と、moment participation が表す physical
hydrodynamic character は別に保存する。単純固有値域の spectral identity は前 wave
vector との symmetric biorthogonal overlap で継続し、moment participation は
physical label の診断に使う。両者を一つの重み付き cost に混ぜて同一概念にしない。
curve veering では physical character が analytic eigencurve 間で交換し得る。

\(k=0\) は conserved eigenspace が縮退しているため、個別 shear/acoustic vector を
overlap だけで初期化できない。各 path direction \(\hat k\) について

1. conserved subspace 内の一次 perturbation operator を対角化する、または
2. 十分小さい \(k=\varepsilon\hat k\) で longitudinal/transverse moment
   polarization により acoustic/shear を初期化する

必要がある。その後にだけ隣接 \(k\) 間の overlap tracking を使う。個別 branch と
呼ぶのは、固定した1次元 path 上で対象固有値が代数的に単純で、補スペクトルから
分離し、左右固有ベクトルの条件数が gate 内にある区間だけとする。

固有値衝突・縮退点では個別 vector を強制せず、次を正本にする。

- complex ordered-Schur subspace
- subspace間の principal angles
- basis rotation に不変な cluster moment singular values
- cluster内固有値の多重集合
- selected/excluded Schur blocks の Sylvester separation

path reversal は cluster の張る部分空間と complement との非交換を判定し、cluster
内部の permutation は失敗に数えない。単一 \(k\) の symbol は複素行列なので complex
Schur を使い、実 \(2\times2\) block 化は \(k,-k\) を組にした full real coordinates
で行う。

現 Q004b 実装は対角化可能な D2Q9 path に対し、個別固有ベクトルから候補 cluster を
seed してから ordered Schur へ移る。非半単純・defective collision ではこの seed 自体が
不十分なので、Q005 でその兆候が出た場合は Schur-native reordering/projector
continuation へ置き換える。simple-label の condition も将来は全固有基底の条件数でなく、
選択固有対ごとの \(\|l_i\|\|r_i\|/|l_i^*r_i|\) を使う。

### 4.3 Physical admissibility

master mode selector は次を全て満たすこと。

1. \(k=0\) の conserved branch から連続に追跡できる。
2. \(\lVert k\rVert\le k_c\)。
3. kinetic cluster との eigenvalue gap と Schur separation が下限以上。
4. 複素共役を必ず対で含む。
5. 実状態用には共役対を実 \(2\times2\) block に変換する。
6. Nyquist checkerboard を low-\(k\) rule で除外する。
7. path reversal と格子90度回転で cluster principal angle が閾値以下。
8. spectral projector の norm、idempotency residual、\(AP-PA\) residual が gate 内。

主目的は全 Brillouin zone の一意分類ではなく、上の条件を同時に満たす最大の
\(|k|\le k_c\) を求めることである。全域追跡の破綻位置も棄却結果として保存する。
有限 path sampling では最後の合格点と最初の不合格点を bracket として報告し、前者を
\(k_c\) の経験的下限とする。単一 sample を厳密な最大値とは呼ばない。

候補 \(k_c\) ごとに

\[
\mathrm{sep}_p =
\min_{\substack{
  k_{\mathrm{out}}=\sum_j\alpha_j k_j\ \mathrm{mod}\ 2\pi\\
  \mu\in\sigma(A_{\mathrm{excluded}}(k_{\mathrm{out}}))\\
  \alpha,\ 2\le|\alpha|\le p}}
\left|\mu-\lambda^\alpha\right|
\]

と homological operator の最小特異値・条件数を記録する。さらに ordered Schur
blocks \(T_{11},T_{22}\) について

\[
\operatorname{sep}(T_{11},T_{22})
=\min_{\|X\|_F=1}\|T_{11}X-XT_{22}\|_F
\]

を測る。非線形 Fourier interaction
は wave vector を格子上の modulo 和で保存するため、出力波数と無関係な excluded
eigenvalue を全 spectrum から比較してはならない。

上の scalar \(\lambda^\alpha\) は複素対角基底での診断式である。実装で複素共役対を
実 \(2\times2\) block にした場合は scalar 差を使わず、

\[
\mathcal H_{p,k_{\mathrm{out}}}
=
A_{\mathrm{excluded}}(k_{\mathrm{out}})\otimes I
-I\otimes \Lambda_{\mathrm{in}}^{(p)}
\]

という実 block homological operator の最小特異値を直接測る。
閾値を満たさない場合は次のいずれかを行う。

1. 共鳴・近共鳴モードを master set に追加。
2. \(k_c\) を下げる。
3. polynomial degree/domain を下げる。
4. MRT で kinetic relaxation を調整。
5. その regime では smooth manifold 仮説を棄却。

### 4.4 Grid refinement

格子を細かくすると最小非零波数の hydrodynamic eigenvalue は単位円へ近づく。
固定 \(m\)、固定 gap、固定誤差定数が解像度に一様とは仮定しない。

監査対象は少なくとも

```text
N = 9, 17, 33, 65   # 奇数 periodic grid、strict-center alias を避ける
omega = 1.0, 1.2, 1.5, 1.8
```

とする。candidate manifold の構築は当面奇数格子に限定する。偶数格子
\(N=16,32\) は parity regression と障害解析に使い、\(A(\pi,0)\),
\(A(0,\pi)\) も直接評価する。checkerboard-free 部分空間の非線形不変性を証明するか、
Nyquist modeを減衰させるまでは偶数格子上の low-k candidate manifold を主張しない。

## 5. 座標と gauge

選択した右基底 \(V\in\mathbb{R}^{N\times m}\) と左基底
\(L\in\mathbb{R}^{m\times N}\) を

\[
LV=I_m
\]

に biorthogonalize する。

chart は

\[
W(0)=f_\*,\qquad DW(0)=V
\]

を満たし、graph gauge を

\[
L(W(a)-f_\*)=a
\]

として hard constraint にする。

従って

\[
R(a)=L(\Phi(W(a))-f_\*)
\]

であり、非線形 solve の独立未知量を減らせる。ただし研究 artifact には \(R\) の
係数を明示保存し、内部共鳴を観察できるようにする。

projector は

\[
P=VL,\qquad Q=I-P
\]

である。不変性方程式の独立な補空間部分は

\[
Q\left[
\Phi(W(a))
-W\left(L(\Phi(W(a))-f_\*)\right)
\right]=0
\]

となる。

### 5.1 非零波数 chart の固定保存量葉

最初の非零波数 candidate chart は、全質量と全運動量を固定する案Aを採用する。
保存量写像を

\[
\mathcal C(f)=\left(\sum_x \rho(x),\sum_x j_x(x),\sum_x j_y(x)\right)
\]

とし、基準値 \(c=\mathcal C(f_\*)\) に対する不変葉を

\[
\mathcal X_c=\{f:\mathcal C(f)=c\}
\]

とする。構成する写像は \(W_c:\mathcal A\to\mathcal X_c\) と
\(R_c:\mathcal A\to\mathcal A\) である。一次・二次係数および多様体外摂動には

\[
\mathcal C V=0,\qquad \mathcal C H=0,\qquad
\mathcal C\delta_\perp=0
\]

を hard constraint として課す。\(k+(-k)=0\) の相互作用で生成される zero-wave-number
補正は、保存モーメントを持たない kinetic/complement 成分だけを許す。shadowing と
normal-attraction の比較も同じ \(\mathcal X_c\) 内で行う。

Phase 0 の一様 equilibrium oracle は \((\delta\rho,j_x,j_y)\) を座標とするため、保存量葉を
横切る別問題である。将来、保存量3座標も含む center-slow 構成へ移る場合は
\(a=(\delta\rho_0,j_{x,0},j_{y,0},a_{\rm slow})\) とし、保存量方向の恒等力学を明示する。
この案Bを固定葉構成へ暗黙に混ぜない。

### 5.2 Conditioning

\(V,L\) は列・行 scaling を固定し、artifact に次を保存する。

- \(\lVert LV-I\rVert\)
- \(\kappa(V)\)
- \(\lVert P^2-P\rVert\)
- \(\lVert AP-PA\rVert\) と \(\lVert P\rVert\)
- selected/excluded cluster の eigenvalue gap と ordered-Schur separation
- real-block conversion error

\(DW(a)\) の最小特異値が領域内で下限を割れば chart fold または座標劣化と判定し、
domain を縮小するか multiple charts に分ける。

## 6. 係数ごとの構成

固定点を原点へ移した map を

\[
F(x)=\Phi(f_\*+x)-f_\*
\]

とする。

\[
K(a):=W(a)-f_\*=\sum_{p=1}^{P}K_p(a),\qquad
R(a)=\sum_{p=1}^{P}R_p(a)
\]

と homogeneous polynomial ごとに展開する。

一次は

\[
AK_1=K_1R_1,\qquad K_1=V,\quad R_1=\Lambda.
\]

次数 \(p\ge2\) は

\[
AK_p-K_p\circ\Lambda^{\otimes p}-VR_p=-\Gamma_p
\]

\[
LK_p=0
\]

を解く。\(\Gamma_p\) は \(F\)、既知の \(K_1,\ldots,K_{p-1}\)、
\(R_1,\ldots,R_{p-1}\) の合成から得る。

### 6.1 二次式

\[
F(x)=Ax+\frac12B(x,x)+O(3)
\]

\[
K(a)=Va+\frac12H(a,a)+O(3)
\]

\[
R(a)=\Lambda a+\frac12G(a,a)+O(3)
\]

なら

\[
AH+B(V,V)=VG+H(\Lambda\cdot,\Lambda\cdot),\qquad LH=0.
\]

現在の strict-center oracle では \(\Lambda=I\) なので、各 \((j,k)\) について

\[
\begin{bmatrix}
A-I & -V\\
L   & 0
\end{bmatrix}
\begin{bmatrix}
H_{jk}\\G_{jk}
\end{bmatrix}
=
\begin{bmatrix}
-B(V_j,V_k)\\0
\end{bmatrix}
\]

を dense least squares で解いている。

一般の slow basis では \(\Lambda\otimes\Lambda\) が係数間を結合する。実装順は

1. dense Kronecker/Sylvester solve
2. sparse/matrix-free Krylov
3. TT operator solve

とし、各段階で前段を oracle にする。

### 6.2 Derivative acquisition

小規模順序:

1. 解析 derivative
2. complex-step または automatic differentiation
3. centered finite difference

complex-step は map 全体が complex dtype を保存する場合に限る。現行 D2Q9 dense
oracle は入力を `float64` に正規化するため complex-step 非対応であり、虚部を
捨てる実装のまま使用しない。

有限差分を使う場合は step-size sweep を行い、係数と residual order が plateau に
入る範囲を artifact に残す。座標 scaling が異なる場合は scalar step を流用せず、
各列 \(\|V_j\|\) と admissible state perturbation に応じた coordinate-wise step
\(h_j\) を使う。対角二階微分には標準3点 stencil、混合微分には4点 stencilを使う。
homological equation residual が小さくても derivative が正しいとは限らない。
現在の strict-center baseline は step sweep と解析 Hessian 比較を併用し、選択 step
で相対誤差 \(10^{-13}\) 以下を得ている。この値は canonical coordinates 固有の
oracle 結果であり、回転・再 scaling 後へ外挿しない。

### 6.3 Higher order

次数3以降は多項式合成を multi-index で行う。各次数で必ず

- coefficient equation residual
- gauge residual
- symmetry residual
- \(\mathrm{sep}_p\)
- condition estimate
- held-out invariance residual order

を測る。高次数が低次数より悪化した場合は、rank を上げる前に near resonance、
finite-difference error、domain 過大、normalization を診断する。

## 7. TT パラメータ化

### 7.1 Dense coefficient tensor

次数上限 \(P\)、reduced dimension \(m\) の chart を

\[
W_i(a)=
\sum_{\alpha_1=0}^{P}\cdots\sum_{\alpha_m=0}^{P}
C_{i,\alpha_1,\ldots,\alpha_m}
\prod_{j=1}^{m}\psi_{\alpha_j}(a_j)
\]

と書く。total-degree \(P\) を超える係数は zero mask とする。
\(\psi\) は最初 monomial、有限領域 refinement では scaled Chebyshev を候補とする。

output mode \(i\) を block core とし、

```text
(output, degree_1, ..., degree_m)
```

の coefficient tensor を TT にする。

初期 oracle では

```text
dense coefficients -> TT-SVD -> exact dense reconstruction check
```

を行う。TT rounding 後は必ず invariance defect を再計算する。

### 7.1.1 Reduced map \(R\)

非自明な candidate chart では \(R\) も online state であり、\(W\) の付属物として
省略しない。同じ基底 \(\psi_\alpha\) を使い、

\[
R_\ell(a)=\sum_\alpha D_{\ell,\alpha}
\prod_j\psi_{\alpha_j}(a_j),\qquad \ell=1,\ldots,m
\]

と表す。output \(m\) を block mode にした coefficient TT、symmetric sparse
polynomial、dense coefficient の3表現を同じ interface で比較する。

初期段階では \(m\) が小さいので \(R\) は sparse polynomial を正本とする。TT化は

- core stored scalar count、index metadata、serialized bytes
- standalone \(R(a)\) evaluation cost
- composition \(W(R(a))\) cost
- conserved \(k=0\) coordinates の exact update
- resonant coefficients

を sparse baseline より悪化させない場合だけ採用する。\(R\) の rounding 後も
graph identity \(R=L(\Phi(W)-f_\*)\) を独立点で再検証する。

### 7.1.2 格納量の比較規約

Phase 0 の \(81\times3\times3\times3\) coefficient tensor では、現在の閾値に基づく
格納値数は次の通りである。

| 表現 | stored scalar/value count | 別に必要な metadata |
|---|---:|---|
| box-dense | 2187 | shape |
| full Hessian | 1053 | degree/axis convention |
| symmetric quadratic | 810 | packed-index convention |
| fiber-sparse | 567 | 7 multi-indices |
| scalar-sparse | 468 | 468 multi-indices |
| TT cores | 657 | ranks、shapes、ordering |

657 は **TT core stored scalars** であり、TT gauge 自由度を除いた数学的自由度数では
ない。sparse の値数も structural-zero threshold に依存する。従って圧縮評価では、
値の格納数、index/rank metadata、serialized bytes、評価時間、rounding時間、実効自由度、
不変性残差を別々に報告する。この oracle では TT は box-dense より小さいが、自然な
fiber-sparse baseline より大きいため、TT 優位性は認めない。

### 7.2 Spatial/velocity tensorization

LBM state output は単一の flat mode に固定しない。

- D2Q9 velocity: \(3\times3\)
- D3Q27 velocity: \(3\times3\times3\)
- \(N_x=2^{b_x}\), \(N_y=2^{b_y}\), \(N_z=2^{b_z}\): QTT bits

比較する ordering:

1. axis-major spatial bits, then velocity axes
2. scale-interleaved spatial bits
3. space/velocity interleaved
4. output-block coefficient modeを先頭または末尾

ordering は理論だけで決めず、同じ dense chart の rank profile と operator cost で
選ぶ。

### 7.3 TT-cross の役割

TT-cross は次の場合だけ導入する。

1. dense coefficient/collocation tensor が作れない。
2. 1 entry の oracle が全 tensor より十分安い。
3. 独立 validation set が用意できる。
4. cross sampling cost を記録できる。

用途は offline assembly であり、毎 time step の full \(\Phi\) を TT-cross で
作り直さない。

cross validation policy:

- cross nodes は validation に使わない。
- independent random points。
- domain boundary points。
- 最大 Mach、最大渦度、最大 shear の targeted points。
- adversarial local search で見つけた residual peak。
- relative \(L^2\) と absolute/relative \(L^\infty\) の両方。

rank 過指定は不安定化し得るため、rank/tolerance sweep を行う。
exact pseudoinverse の rank 過指定で不安定化した場合は、Qin らが解析した
truncated pseudoinverse も対照にする。

#### Entry oracle の非局所性

一般の homological equation は出力成分と係数が結合しているため、
\((i,\alpha)\) という scalar coefficient 1個を安価に問い合わせられるとは仮定しない。
実際の query unit と費用を次のいずれかとして事前登録する。

1. **Coefficient fiber oracle:** 一つの \(\alpha\) に対する全出力
   \(W_\alpha\) を wave-number sector の linear solve で得る。scalar query はこの
   fiber の cache lookup にすぎず、solve 数を減らさない。
2. **Collocation corrector oracle:** 一つの \(a\) に対して低次 chart を初期値に
   invariance corrector を解き、全出力 \(W(a)\) を返す。1 query が nonlinear solve
   なので、wall time を必ず cross cost に含める。
3. **All-TT equation solve:** entry oracle を使わず、homological operator と forcing
   を TT 化して ALS/AMEn/Riemannian solver で係数全体を直接解く。

Phase 5 へ進む前に、小規模 dense 問題でこの3案の oracle call 数、1 call cost、
cache hit、最終 residual を比較する。安い独立 query を示せない限り
「TT-cross により dense solve を回避できる」と主張しない。

### 7.4 Structure not guaranteed by TT

通常の TT-SVD/TT-cross は次を保証しない。

- conserved moments
- population positivity
- density positivity
- local maximum norm
- chart injectivity

保存量は graph gauge と exact low-rank correction で hard constraint にする。
positivity は sampling だけでなく、domain certificate または barrier/limited chart を
検討する。負 population を単純 clipping すると invariance と保存を壊すため禁止する。

## 8. 非線形 refinement

低次 Taylor chart は局所初期値として使う。有限領域では次の loss を解く。

\[
\mathcal L =
\mathcal L_{\mathrm{inv}}
+\eta_g\mathcal L_{\mathrm{gauge}}
+\eta_c\mathcal L_{\mathrm{conservation}}
+\eta_r\mathcal L_{\mathrm{regularity}}
\]

ただし gauge と保存は可能な限り parameterization に組み込み、penalty だけに
依存しない。

候補 solver:

1. dense collocation Newton
2. Gauss–Newton / Levenberg–Marquardt
3. matrix-free Newton–Krylov
4. alternating TT core optimization
5. Riemannian/ALS refinement

Newton step は chart reparameterization nullspace を graph gauge で除く。
training point の平均残差だけを目的にせず、max-residual enrichment を行う。

### 8.1 Domain continuation

小振幅 ball から開始し、次の全 gate を満たす間だけ半径を増やす。

```text
invariance max residual
multi-step shadowing
min density
min population
max Mach
min singular value of DW
normal contraction
TT rank and wall time
```

いずれかが失敗した半径を validity boundary とし、単に rank を上げて隠さない。

## 9. 検証設計

### 9.1 Algebraic gates

| Gate | 初期基準 |
|---|---:|
| D2Q9 quadrature identities | absolute \(2\times10^{-15}\) |
| \(LV-I\) | Frobenius \(10^{-11}\) |
| \(P^2-P\) | relative \(10^{-11}\) |
| linear tangent equation \(AV-V\Lambda\) | relative \(10^{-11}\) |
| coefficient homological residual | relative \(10^{-9}\) |
| gauge coefficient residual | absolute \(10^{-11}\) |
| TT dense reconstruction | measured relative error \(<10^{-11}\) |

閾値は float64 dense oracle 用であり、large matrix-free/TT では conditioning に基づき
事前登録し直す。TT-SVD の入力 tolerance は discarded singular values の切り捨て予算
であって、丸め誤差を含む再構成誤差の保証ではない。したがって、再構成、held-out
chart 評価、不変性残差の各 end-to-end gate は内部 tolerance と独立に測定する。

### 9.2 Invariance metrics

defect:

\[
E(a)=\Phi(W(a))-W(R(a)).
\]

報告値:

\[
\|E\|_2,\quad \|E\|_\infty,\quad
\frac{\|E\|_2}{\max(\|\Phi(W)\|_2,\|W(R)\|_2,\epsilon)}.
\]

さらに amplitude \(\varepsilon\) に対する log-log slope を測る。次数 \(P\) の
Taylor chart は非退化方向で概ね

\[
\|E(\varepsilon a)\|=O(\varepsilon^{P+1})
\]

を示すべきである。単一点で小さいだけでは合格にしない。

### 9.3 Multi-step shadowing

\[
e_n(a)=
\frac{
\left\|\Phi^n(W(a))-W(R^n(a))\right\|_2
}{
\max(\|\Phi^n(W(a))\|_2,\epsilon)
}.
\]

center/slow direction では 1-step error が収縮で消えない。次を報告する。

- \(n=1,10,100,1000\)
- median / 95 percentile / maximum
- phase error and amplitude error for acoustic modes
- shear decay-rate error

### 9.4 Physical gates

- global mass/momentum balance
- local density lower bound
- population minimum
- maximum Mach number
- viscosity
  \[
  \nu=c_s^2\left(\frac1\omega-\frac12\right)
  \]
  に対する shear decay
- acoustic dispersion/dissipation
- isotropy under rotated wave vector
- full LBM baselineとの field error

### 9.5 Normal attraction

chart tangent projectorを \(P_a\) とする。固定保存量葉の接空間内、すなわち
\(\mathcal C\delta_\perp=0\) を満たす多様体外 perturbation \(\delta_\perp\) に対して

\[
\frac{
\|(I-P_{R(a)})D\Phi(W(a))\delta_\perp\|
}{
\|\delta_\perp\|
}
\]

を測る。full/reduced の両軌道も同じ保存量 \(c\) を持たせる。1未満の一様 bound が
失われた地点は candidate manifold の validity limit 候補である。偶数格子では
Nyquist の厳密な単位円方向がこの bound を壊し得るため、主構築は奇数格子に限定する。

### 9.6 Cost gates

比較対象:

1. dense full LBM
2. direct TT/MPS LBM
3. dense reduced \(R\)
4. Fourier-selection-rule sparse \(W,R\)
5. TT \(W,R\)

記録:

- offline derivative/oracle calls
- homological solve time
- cross sample count
- rounding time
- peak memory
- online step time
- lift/project time
- break-even number of time steps
- TT ranks per core and over continuation

Fourier-sparse を Q008–Q010 の必須 baseline とし、TT が値数・実メモリ・online cost
のいずれでも勝たない regime は「この tensorization では TT 不適切」と記録する。
圧縮率だけで速度向上を主張しない。

## 10. 研究フェーズ

### Phase 0: 文献・定義・dense oracle — 完了

- center と slow の区別
- D2Q9 dense map
- exact linearization
- Fourier unit-circle audit
- strict-center quadratic solve
- polynomial TT representation

exit evidence:

- tests passing
- reproducible JSON artifact
- observed residual order 2 → 3

### Phase 1: Hydrodynamic spectrum と Q005 falsification — 完了

実装:

- moment signatures
- left/right eigensystems
- simple-branch continuation と ordered-Schur cluster continuation
- real block basis
- threshold-dependent \(k_c\) candidates
- separation/condition report

exit gate:

- known small-\(k\) shear/acoustic asymptoticsと一致
- path reversal と格子90度回転で cluster subspace が保たれる
- odd \(17^2,33^2\) と even \(16^2,32^2\) の parity を分離
- Q005 で sector-aware nonresonance、nonnormality、grid refinement を評価
- 最小 isotropic shell の compatible external resonance を16/16条件で検出
- registered radial band の normal-attraction 必要条件を14/16条件で棄却
- fixed-leaf stripe の有限格子 conditioning を solver oracle として分離

全 Brillouin zone での個別ラベル一意性は棄却済みであり、失敗ではない。Q004b の
\(k_c\) は経験的 cutoff で、candidate manifold の存在を意味しない。

### Phase 1.5: Manufactured general-homological oracle — 完了

- 安定な複素共役対の実 \(2\times2\) block 化
- 非零 \(R_2\) と既知の二次 chart の回収
- 一般 Kronecker homological operator
- near-resonance condition number の増大
- 厳密な二次共鳴の明示的拒否

これは solver と branch classification の誤差を分離する algebraic oracle であり、
LBM の非零波数 candidate manifold の存在証拠ではない。

### Phase 2: Nonzero-mode dense quadratic solver oracle

最初の master set:

- \(N=17,\omega=1.2\) の \(y\)-independent stripe
- \(K=\{\pm(2\pi/17,0)\}\) の shear/acoustic conjugate modes
- 正波数側の複素3座標を共役制約により実6座標へ変換

構成は \(\delta M=\delta P_x=\delta P_y=0\) の固定保存量葉上で行い、\(k=0\) の
保存方向を reduced coordinates に含めない。

この stripe は full nonlinear map で不変だが、full 2D candidate の代替受理ではない。
二次 Fourier sum は \(0,\pm2k\) にだけ出るため、二次 \(R_2=0\) を予測する。
Q005 では second-harmonic block の
\(\sigma_{\min}=1.9335\times10^{-2}\)、\(\kappa_2=96.02\) を得ている。

実装:

- general real \(\Lambda\)
- Kronecker/Sylvester homological solve
- 保存モーメントを持たない generated zero-wave-number kinetic correction
- generated second harmonics
- graph gauge
- \(\mathcal C H=0\) の fixed-leaf constraint

exit gate:

- linear chart \(O(\varepsilon^2)\)
- quadratic chart \(O(\varepsilon^3)\)
- independent directionsで同じ order
- rollout dispersion/decay が full LBM と一致

full 2D 構築は、diagonal shear orbit を加えた mode set の additive closure と
Schur-block conditioning を再監査するまで保留する。

### Phase 3: Degree/domain continuation

- cubic/quartic coefficients
- resonance and condition ledger
- amplitude continuation
- multiple chart criterion

exit gate:

- degreeを上げるごとに指定領域の held-out residual が改善
- positivity/Mach/injectivity gateを満たす

### Phase 4: TT coefficient compression

- velocity tensorization
- spatial QTT ordering sweep
- TT-SVD oracle
- exact moment correction

exit gate:

- dense chartとの差が invariance budgetの10%以下
- TT rounding後も residual orderを維持
- storageとonline costが報告される

### Phase 5: TT-cross / all-TT construction

- black-box coefficient/collocation oracle
- independent targeted validation
- alternating core refinement

exit gate:

- dense-available小格子で TT-SVD oracle と一致
- cross nodes 以外の \(L^\infty\) gate
- sample count/offline break-even を満たす

### Phase 6: Boundaries and forcing

順序:

1. steady periodic forcing
2. planar wall / Poiseuille
3. Couette
4. cavity
5. time-periodic forcing with augmented phase

各ケースで fixed point、保存収支、boundary-induced rank を再監査する。

### Phase 7: D3Q27

詳細は次節。D2Q9の exit gate を満たすまで着手しない。

## 11. D3Q27 拡張

### 11.1 Algebraic construction

D1Q3 の tensor product として

\[
\mathcal C_{27}=\{-1,0,1\}^3
\]

を作る。重みも一軸重み

\[
(w_{-1},w_0,w_{1})=(1/6,2/3,1/6)
\]

の積とする。これにより

- 速度 index の手書き誤りを避ける。
- D2Q9/D3Q27で同じ tensorized moment code を使える。
- TT velocity cores の物理 index を3値因子として保持できる。

これは速度集合、重み、index の tensor-product 構造を意味するだけで、任意の
collision、boundary、\(W\)、TT rank が軸分離することは意味しない。
### 11.2 Center/slow dimensions

\(k=0\) conserved center は通常

\[
(\rho,j_x,j_y,j_z)
\]

の4次元である。各非零 \(k\) の hydrodynamic cluster は acoustic 2枝と transverse
shear 2枝を含む。degeneracy があるため、個別固有ベクトルでなく shear subspace
全体を追跡する場合がある。

### 11.3 Staged validation

1. quadrature and isotropy tensor identities
2. \(z\)-independent D2Q9 lift
3. axis-aligned low-\(k\) modes
4. face/body diagonal low-\(k\) modes
5. rotated shear/acoustic dispersion
6. periodic 3D Taylor–Green
7. wall/forcing

`z`-independent lift の exact baseline は D1Q3 の \(z\) 重みを使い、

\[
f^{3D}_{q_xq_yq_z}(x,y,z)
=w_{q_z}^{1D}f^{2D}_{q_xq_y}(x,y)
\]

とする。D3Q27 state を単純に一つの \(q_z\) 面へ埋め込まず、同じ
\(\rho,(u_x,u_y,0)\)、\(z\)-independence、3D equilibrium/momentsとの整合を検証する。

### 11.4 Scaling

同じ一辺 \(L\) なら raw state は

\[
9L^2\to27L^3
\]

で比は \(3L\)。hydrodynamic fields は

\[
3L^2\to4L^3
\]

で比は \(4L/3\)。

\(L=2^b\) で各 spatial/velocity factor を1 core とする本設計の ordering では、
QTT core 数は概ね

\[
2b+2\to3b+3
\]

だが、rank 一定は仮定しない。collision、\(1/\rho\)、vorticity、geometry が
rank を増やす。2D rank cap を3Dへコピーしない。

## 12. ソフトウェア構造

目標構造:

```text
src/ttim_lbm/
  lattices/        D1Q3, D2Q9, D3Q27 descriptors and moments
  maps/            collision, forcing, streaming, boundary, full map
  spectra/         Fourier symbols, Arnoldi, branch tracking
  charts/          polynomial and sampled W, R, gauge
  homological/     coefficient assembly and solvers
  tensor_train/    TT-SVD, TT-cross adapter, operators, rounding
  validation/      invariance, rollout, physics, cost
  experiments/     preregistered reproducible campaigns
tests/
research/
  preregistrations/
  artifacts/
  reports/
```

現行の小さいモジュールは Phase 0 oracle、Q004b の branch/cluster tracker、
manufactured general-homological oracle、Q005 の Fourier-sector SVD/normal-gap
campaign を含む。Q006s の coefficient solver が安定してから上記へ機械的に分割し、
過早に抽象階層を増やさない。

Phase 1 以降の campaign artifact 共通 schema:

```text
schema_version
source_fingerprint
code_commit                 # external sealed campaign で追加
generated_at_utc
full_map_descriptor
reference_state
coordinate_definition
gauge_definition
spectrum_selection
solver_parameters
training_samples
validation_samples
algebraic_metrics
invariance_metrics
physical_metrics
cost_metrics
decision
next_question
```

random seed、platform、NumPy/solver version も保存する。

Phase 0 の `d2q9_baseline.json` は cycle ごとの問い・仮説・結果を優先した schema v2
であり、`source_fingerprint` と runtime version を持つ。Q004b/人工オラクルは独立の
artifact に保存し、上記 campaign field を完全には平坦化していない。将来 schema を
変更するときは変換器と schema test を同時に追加し、既存 artifact の意味を後から
変更しない。

## 13. 失敗モードと対応

| 失敗 | 観測 | 最初の対応 |
|---|---|---|
| center/slow 混同 | \(m=3\) で空間流れを再現不能 | branch-tracked slow setへ変更 |
| Nyquist ghost | 偶数格子で \(\lambda=-1\) | 主構築を奇数格子に限定し、偶数格子は障害解析 |
| spectral gap collapse | homological condition急増 | mode追加、\(k_c\)低下、MRT |
| compatible external resonance | null forcing だが homological block が singular | 一意性を主張せず、mode追加または不変 stripe oracleへ分離 |
| internal resonance | \(R\)を線形にすると不整合 | resonant termを \(R\) に残す |
| chart fold | \(\sigma_{\min}(DW)\to0\) | domain縮小、multiple charts |
| TT rank explosion | collision後 rank急増 | ordering/rank適応、domain縮小 |
| TT-cross miss | held-out \(L^\infty\) が大きい | targeted enrichment/multi-start |
| conservation drift | rolloutでmass/momentum drift | graph gauge/exact correction |
| positivity failure | \(\min f_i<0\) | domain制限/barrier、clip禁止 |
| nonautonomous mismatch | forcing phaseで残差系統差 | phase/control augment |
| no speedup | offline cost償却不能 | break-evenを失敗として記録 |

## 14. 現時点で確定していない選択

次は実験で決めるため、設計上まだ固定しない。

- reduced coordinates を low-\(k\) modal にするか全 hydrodynamic field にするか。
- BGK のまま進む最大 \(\omega\) と MRT への切替点。
- monomial と Chebyshev の切替振幅。
- TT output mode ordering。
- TT-cross library/backend。
- boundary case での spectral basis と data-assisted basis の比率。
- single chart と atlas の切替条件。

各選択は [`research/NEXT_QUESTIONS.md`](../research/NEXT_QUESTIONS.md) の
反証可能な問いとして扱う。
