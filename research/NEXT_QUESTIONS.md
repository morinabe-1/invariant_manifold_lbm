# 次に検証する問い

上から順に gate を通す。前段が失敗した場合は、失敗分析と設計修正を記録してから
同じ gate を再実行する。Q004b、Q005m、Q005 は実装済みだが、定義と再現条件を残す。

## Q004b: validated hydrodynamic-cluster cutoff

### 問い

\(k=0\) から連続化した3次元 hydrodynamic cluster が kinetic complement から分離し、
物理的 character を保つ最大の低波数領域 \(|k|\le k_c\) はどこか。

全 Brillouin zone で個別の shear/acoustic/kinetic label が一意になることは要求しない。
全域追跡は、分類が破綻する位置を探す棄却診断として残す。

### 事前登録

- candidate-manifold construction: 奇数周期格子 \(17^2,33^2\) のみ
- parity/obstruction regression: 偶数周期格子 \(16^2,32^2\)
- direct symbols: \(A(\pi,0)\), \(A(0,\pi)\)
- \(\omega=1.0,1.2,1.5,1.8\)
- axis、diagonal、一般角度の連続 \(k\)-path
- simple eigenvalue域では左右固有ベクトルの symmetric biorthogonal overlap
- 衝突・縮退域では3次元 ordered-Schur subspace、principal angle、cluster moment content
- selected/excluded 間の eigenvalue gap、Schur Sylvester sep、spectral-projector norm
- \(k\to0\) の dispersion/dissipation を既知の粘性と比較
- analytic/spectral branch identity と moment-based physical character を別に保存

### 成功条件

- cluster 次元が3で、selected/excluded spectral split が \(k_c\) まで維持される
- path reversal と90度回転で cluster の張る部分空間が一致する
- cluster内部の permutation は失敗に数えない
- simple branch は代数的に単純で conditioning gate を通る点だけ label を付ける
- \(16^2,32^2\) と直接 symbol に \(\lambda=-1\) Nyquist mode が現れ、構築対象から除外される
- small-\(k\) shear decay が
  \[
  \log|\lambda_{\mathrm{shear}}(k)|=-\nu |k|^2+O(|k|^4)
  \]
  と整合

初期 dense gate は、equilibrium-subspace alignment 0.75、external eigenvalue gap
0.05、Schur sep 0.02、隣接 principal angle 0.20 rad、spectral-projector norm
100、Schur invariance と projector idempotency/commutator residual \(10^{-12}\) とする。
報告する \(k_c\) は最後の合格 sample と最初の不合格 sample の bracket であり、
一点の厳密な最大値ではない。これは存在定理ではなく、
Q005へ渡す経験的 cutoff である。

## Q005: candidate slow set に spectral gap はあるか

### 問い

Q004bで得たどの \(k_c,\omega,P\) なら、次数 \(P\) までの homological operator が
実用的な condition number を持つか。

### 測定

- selected/excluded eigenvalue distance
- ordered-Schur block間の Sylvester sep
- spectral projector の norm、commutator residual
- simple branch の eigenvalue condition と reduced resolvent norm
- Fourier selection rule
  \(k_{\mathrm{out}}=\sum_j\alpha_jk_j\pmod{2\pi}\) を満たす sector 内だけの
  \(\min|\mu(k_{\mathrm{out}})-\lambda^\alpha|\)
- 実 block Kronecker homological operator の smallest singular value
- nonnormality / eigenvector condition
- grid refinement dependence

### 二次 gate の事前登録

- まず \(P=2\) を判定し、これを通過した候補だけ高次へ進める。
- upstream cutoff は Q004b の方向別最小合格値

  \[
  \{1.0:0.7630763889,\ 1.2:0.9254861111,
    1.5:1.1628541667,\ 1.8:1.3752361111\}
  \]

  とする。
- 奇数格子 \(N=9,17,33,65\) を用いる。\(17,33\) は Q004b の構築格子、
  \(9,65\) は波数集合の疎密に対する refinement 診断であり、固定物理領域の
  continuum convergence とは呼ばない。
- isotropic master set は、離散波数 \(0<|k|\le k_c\) ごとの3次元
  hydrodynamic cluster とする。二次入力ごとに
  \(k_{\mathrm{out}}=k_1+k_2\pmod{2\pi}\) を厳密に加算する。
- \(k_{\mathrm{out}}=0\) では固定保存量葉を採り、3保存方向を外部空間から除いて
  6次元 kinetic sector だけを監査する。master内出力では hydrodynamic block を
  internal \(R_2\) 側へ分け、外部6次元だけを監査する。それ以外は9次元全体を
  外部出力とする。
- sector homological operator は global dense 行列を作らず、Fourier block ごとの

  \[
  I\otimes A_\perp(k_{\mathrm{out}})
  -K_{12}^{\mathsf T}\otimes I
  \]

  として組む。simple mode の積では \(K_{12}=\lambda_1\lambda_2\) とする。
- 数値的 singular の閾値は

  \[
  \sigma_{\min}\le
  100\,\epsilon_{\mathrm{mach}}\max(m,n)\sigma_{\max}
  \]

  とする。singular sector は解析的二次 forcing \(B\) の左 nullspace 射影を測り、
  \(\|U_0^*B\|/\max(\|B\|,\epsilon)\le10^{-10}\) なら
  compatible_nonunique、それを超えれば incompatible と分類する。
- nonsingular sector の初期 practical ceiling は
  \(\kappa_2\le10^8\) とする。これは有限格子で係数を解けるための上限であり、
  grid-uniform bound ではない。
- complex operator と標準 realification の特異値一致は相対 \(10^{-10}\)、
  共役 sector の整合性は \(10^{-12}\) を gate とする。
- normal-attraction 診断では、master multiplier の最小 modulus と、固定葉上の
  全 excluded 離散波数・mode の最大 modulus を比較する。
  \(\rho_\perp/\rho_\parallel<1\) を有限格子の必要条件とし、最悪波数と
  nonnormality 指標も保存する。
- 全 pair の実体を artifact に列挙せず、件数、最悪 sector、分位値、
  resonance witness と gate 値を保存する。

### 判断

near resonance が選択境界に現れたら、mode追加と \(k_c\)縮小の両案を比較する。
\(\omega\to2\) で gap が閉じる場合は MRT の kinetic relaxation を対照実験にする。
strict nonresonance が失敗した場合は、forcing compatibility があっても
標準 SSM の存在・一意性 gate を合格扱いしない。mode追加、cutoff縮小に加えて、
非線形に不変な一方向 stripe 部分空間を solver oracle として切り分ける案を比較する。

### 判定（実装済み）

登録した16条件の最小非空 isotropic shell は全て、直交 acoustic 対から対角 shear
への数値的 rank-deficient external resonance を持った。forcing の左 nullspace
射影は最大 \(9.97\times10^{-16}\) で compatible だが、解の一意性は失われる。
登録 radial band の境界でも14条件に外部 resonance witness があり、14条件で
near-Nyquist excluded mode が finite-grid normal-attraction 必要条件を破った。
従って標準的な nonresonant・normally-attracting 2D isotropic SSM 候補は棄却した。

cutoff を最小 shell まで縮小しても共鳴は残る。diagonal shear orbit の追加は最初の
witness を internalize するが、additive closure を再監査するまで採用しない。
一方、\(y\)-independent stripe は非線形写像で不変であり、有限格子 solver oracle
として次へ進める。これは full 2D candidate の代替受理ではない。

## Q005m: manufactured nonidentity oracle

Q006より前に、既知の安定実共役 block、非零 \(R_2\)、mean-like complement、
second-harmonic pair、可制御な二次共鳴を持つ5状態写像で、一般
Kronecker homological solverを検証する。係数回収、real/complex変換、gauge、
非直交 similarity transform 下の左右基底 \(LV=I\) と左右不変性、条件数増大、
厳密共鳴の明示的拒否を全て gate にする。

## Q006s: fixed-leaf stripe quadratic solver oracle

### 問い

\(N_x=17,\omega=1.2\) の \(y\)-independent 不変部分空間で、
master set \(K=\{\pm(2\pi/17,0)\}\) の3 hydrodynamic modes を実6座標へ変換し、
固定保存量葉上の dense quadratic chart が residual order 2 → 3 を再現できるか。

### 事前登録

- 実装対象は1方向 stripe oracle だけで、full 2D SSM の存在を主張しない。
- \(a_{-k}=\overline{a_k}\) を課し、正波数側の複素3 mode を実6座標へ realify する。
  mode 順序は shear、acoustic-positive、acoustic-negative、各 mode 内は
  real/imag の interleaved 順とする。
- 複素 Fourier mode の線形 lift には

  \[
  s=(2N_x)^{-1/2},\qquad
  \delta f_x=s e^{ikx}V_cz+\overline{s e^{ikx}V_cz}
  \]

  を使う。座標振幅はこの正規化後の実6座標の Euclidean norm とする。
- Fourier selection rule により二次出力は \(k=0,\pm2k\) だけである。
- \(k=0\) correction は \(\ker(\rho,j_x,j_y)\) の6次元 kinetic block に制限する。
- \(K+K\) は \(K\) に戻らないため、二次 \(R_2\) はゼロを予測する。
- Q005 の代表値
  \(\sigma_{\min}=1.9335\times10^{-2}\)、\(\kappa_2=96.1\) 以下を
  solver assembly の回帰値とする。
- analytic equilibrium Hessian と独立 finite difference を比較し、
  homological residual、graph gauge、fixed-leaf residual を各 \(10^{-10}\) 以下にする。
- analytic Hessian の独立検証には full nonlinear map の step \(0.006,0.003\) を用いた
  centered difference と Richardson extrapolation を使い、相対差 \(10^{-8}\) 以下を
  要求する。
- 非ゲート pilot は seed 20260801 で domain calibration だけに使用した。本試験は
  未使用 seed 20260802 の64方向と、振幅

  \[
  0.000625,\ 0.00125,\ 0.0025,\ 0.005,\ 0.01
  \]

  を固定する。linear chart は
  \(2\pm0.1\)、quadratic chart は \(3\pm0.1\) の residual order を要求する。
- 最大試験振幅で quadratic residual が linear residual の1/10未満になることを要求する。
- seed 20260803 の32方向、振幅0.01で100-step full/reduced shadowing を行う。
  quadratic chart の最大 absolute error は \(10^{-5}\) 以下、perturbation-relative
  error は \(10^{-2}\) 以下、linear chart の最大 error の1/10未満を要求する。
  projected-coordinate drift、保存量 drift、最小 population も別に保存する。
- 振幅0.1は domain-stress 診断として保存するが、local chart gate には含めない。
- \(1\times17\) quotient の1 step と、\(y\) 方向へ複製した \(17\times17\) state の
  1 step が \(10^{-12}\) 以内で一致することを要求する。

## Q006: full 2D fixed-leaf nonzero-mode quadratic parameterization — 保留

### 問い

全質量・全運動量を固定した不変葉上で、mode-added 2D hydrodynamic set を含む dense
candidate chart が residual order 2 → 3 を再現できるか。Q006s と、diagonal shear
orbit を加えた additive-closure/conditioning 再監査が通るまで着手しない。

### 必須観測

- \(k+(-k)=0\) が作る zero-wave-number kinetic/complement correction
- 上記 correction の保存密度・保存運動量成分が厳密にゼロ
- second harmonic generation
- Fourier selection rule が許す internal \(R_2\)（最小 shell だけならゼロ）
- gauge residual
- homological condition
- 20以上の独立方向
- amplitude continuation
- 100-step shadowing

### 失敗時の切分け

1. branch misclassification
2. missing resonant mode
3. real/complex basis conversion
4. derivative error
5. coordinate normalization
6. local candidate-chart domain超過
7. fixed-conservation-leaf constraint 違反

## Q007: degree continuation は有効か

### 問い

quadratic → cubic → quartic で held-out maximum residual と rollout horizon が
単調に改善するか。

改善しなければ、多項式次数不足ではなく near resonance、有限半径、chart fold を
先に疑う。

## Q008: TT rank は bounded か

### 問い

同じ dense chart に対して、どの tensorization/order が最小 rank と最小 operator
cost を与えるか。

比較:

- flat velocity vs D1Q3 factors
- axis-major vs scale-interleaved QTT
- coefficient output core first vs last
- monomial vs Chebyshev
- shell countとdegreeの sweep
- Fourier-selection-rule sparse coefficients

格納比較は、box-dense、full Hessian、symmetric packed、fiber-sparse、scalar-sparse、
TT core stored scalars を分ける。値数、index metadata、serialized bytes、評価時間、
rounding時間、不変性残差を別指標とし、TT gaugeを除いた intrinsic DoF と混同しない。

## Q009: TT-cross は residual peak を見つけられるか

### 問い

TT-cross chart は、dense/TT-SVD oracle と比較して independent \(L^\infty\) gate を
通るか。

cross points は validation に使わず、random、domain boundary、high-shear、
adversarial residual search を分けて保存する。

## Q010: online benefit はあるか

### 問い

offline construction を含め、どの rollout 数で full dense LBM または direct
TT-LBM より総時間・総メモリが小さくなるか。

break-even が現れない regime は失敗として正直に記録する。Fourier-selection-rule
sparse representationを必須baselineに残し、TTが負ければ不適切と判定する。

## Q011: boundary/forcing で candidate manifold は維持されるか

periodic forcing → Poiseuille → Couette の順に fixed point と spectrum を作り直す。
boundary mask rank、保存収支、normal attraction を測る。

## Q012: D3Q27 へ移してよいか

D2Q9 で次を全て満たして初めて進む。

- branch/cluster tracking
- Q005 sector-aware nonresonance
- fixed-leaf nonzero-mode quadratic residual order
- multi-step shadowing
- TT-SVD preservation
- TT-cross independent validation
- positivity/conservation
- sparse baselineを含むcost report

D3Q27 の最初の問いは、D1Q3 tensor-product construction が quadrature、moment、
\(z\)-independent limit、回転等方性を同時に満たすかである。
