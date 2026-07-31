# 詳細設計: TT パラメータ化不変多様体による LBM 縮約

Status: design baseline v1

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

### 2.3 Hydrodynamic field manifold

全格子の \(\rho,\boldsymbol j\) を座標とすれば

\[
m=(d+1)N_xN_y
\]

となる。これは population 数を \(Q\) から \(d+1\) へ減らすが、空間次元は
減らさない。TT はこの高次元 field chart を圧縮し得る。

### 2.4 Reduced spatial-mode manifold

低波数 Fourier modes、POD modes などを選び

\[
m\ll (d+1)N_xN_y
\]

とする。本設計はまず周期格子の低波数 Fourier hydrodynamic branches でこれを
実装する。境界付き問題では Arnoldi/POD へ一般化する。

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

branch label は modulus ではなく、前 wave vector の固有ベクトルとの biorthogonal
overlap と moment participation の組合せで決める。

\(k=0\) は conserved eigenspace が縮退しているため、個別 shear/acoustic vector を
overlap だけで初期化できない。各 path direction \(\hat k\) について

1. conserved subspace 内の一次 perturbation operator を対角化する、または
2. 十分小さい \(k=\varepsilon\hat k\) で longitudinal/transverse moment
   polarization により acoustic/shear を初期化する

必要がある。その後にだけ隣接 \(k\) 間の overlap tracking を使う。縮退点では個別
vector でなく spectral projector/cluster を比較する。

```text
cost(branch_i(k-dk), candidate_j(k))
  = 1 - normalized biorthogonal overlap
    + alpha * moment_signature_distance
```

assignment は Hungarian matching または小規模全探索で行う。固有値衝突点では
個別ベクトルでなく invariant cluster を追跡する。

### 4.3 Physical admissibility

master mode selector は次を全て満たすこと。

1. \(k=0\) の conserved branch から連続に追跡できる。
2. \(\lVert k\rVert\le k_c\)。
3. kinetic cluster との separation が下限以上。
4. 複素共役を必ず対で含む。
5. 実状態用には共役対を実 \(2\times2\) block に変換する。
6. Nyquist checkerboard を low-\(k\) rule で除外する。

候補 \(k_c\) ごとに

\[
\mathrm{sep}_p =
\min_{\substack{
  k_{\mathrm{out}}=\sum_j\alpha_j k_j\ \mathrm{mod}\ 2\pi\\
  \mu\in\sigma(A_{\mathrm{excluded}}(k_{\mathrm{out}}))\\
  \alpha,\ 2\le|\alpha|\le p}}
\left|\mu-\lambda^\alpha\right|
\]

と homological operator の最小特異値・条件数を記録する。非線形 Fourier interaction
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

とする。偶数格子も実用上必要なので別途監査し、Nyquist modes を明示する。

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

### 5.1 Conditioning

\(V,L\) は列・行 scaling を固定し、artifact に次を保存する。

- \(\lVert LV-I\rVert\)
- \(\kappa(V)\)
- \(\lVert P^2-P\rVert\)
- selected/excluded cluster separation
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

非自明な slow manifold では \(R\) も online state であり、\(W\) の付属物として
省略しない。同じ基底 \(\psi_\alpha\) を使い、

\[
R_\ell(a)=\sum_\alpha D_{\ell,\alpha}
\prod_j\psi_{\alpha_j}(a_j),\qquad \ell=1,\ldots,m
\]

と表す。output \(m\) を block mode にした coefficient TT、symmetric sparse
polynomial、dense coefficient の3表現を同じ interface で比較する。

初期段階では \(m\) が小さいので \(R\) は sparse polynomial を正本とする。TT化は

- parameter count
- standalone \(R(a)\) evaluation cost
- composition \(W(R(a))\) cost
- conserved \(k=0\) coordinates の exact update
- resonant coefficients

を sparse baseline より悪化させない場合だけ採用する。\(R\) の rounding 後も
graph identity \(R=L(\Phi(W)-f_\*)\) を独立点で再検証する。

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

chart tangent projectorを \(P_a\) とし、多様体外 perturbation \(\delta_\perp\) に対して

\[
\frac{
\|(I-P_{R(a)})D\Phi(W(a))\delta_\perp\|
}{
\|\delta_\perp\|
}
\]

を測る。1未満の一様 bound が失われた地点は slow manifold の validity limit
候補である。

### 9.6 Cost gates

比較対象:

1. dense full LBM
2. direct TT/MPS LBM
3. dense reduced \(R\)
4. TT \(W,R\)

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

### Phase 1: Hydrodynamic branch tracking

実装:

- moment signatures
- left/right eigensystems
- branch continuation
- real block basis
- \(k_c\) candidates
- separation/condition report

exit gate:

- known small-\(k\) shear/acoustic asymptoticsと一致
- grid rotationで branch identity が保たれる
- even-grid Nyquist ghosts を除外

### Phase 2: Nonzero-mode dense quadratic manifold

最初の master set:

- \(k=0\) conserved modes
- 最小非零 wave shell の shear/acoustic conjugate pairs

実装:

- general real \(\Lambda\)
- Kronecker/Sylvester homological solve
- generated mean and second harmonics
- graph gauge

exit gate:

- linear chart \(O(\varepsilon^2)\)
- quadratic chart \(O(\varepsilon^3)\)
- independent directionsで同じ order
- rollout dispersion/decay が full LBM と一致

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

現行の小さいモジュールは Phase 0 oracle であり、Phase 1 で上記へ機械的に分割する。
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

Phase 0 の `d2q9_baseline.json` は cycle ごとの問い・仮説・結果を優先した schema v1
であり、`source_fingerprint` と runtime version は持つが、上記 campaign field を
完全には平坦化していない。schema v2 へ移行するときは変換器と schema test を
同時に追加し、v1 artifact の意味を後から変更しない。

## 13. 失敗モードと対応

| 失敗 | 観測 | 最初の対応 |
|---|---|---|
| center/slow 混同 | \(m=3\) で空間流れを再現不能 | branch-tracked slow setへ変更 |
| Nyquist ghost | 偶数格子で \(\lambda=-1\) | low-\(k\)+moment selector |
| spectral gap collapse | homological condition急増 | mode追加、\(k_c\)低下、MRT |
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
