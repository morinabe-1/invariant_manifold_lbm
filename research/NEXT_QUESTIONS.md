# 次に検証する問い

上から順に gate を通す。前段が失敗した場合は、失敗分析と設計修正を記録してから
同じ gate を再実行する。Q004b と Q005m は実装済みだが、定義と再現条件を残す。

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

### 判断

near resonance が選択境界に現れたら、mode追加と \(k_c\)縮小の両案を比較する。
\(\omega\to2\) で gap が閉じる場合は MRT の kinetic relaxation を対照実験にする。

## Q005m: manufactured nonidentity oracle

Q006より前に、既知の安定実共役 block、非零 \(R_2\)、mean-like complement、
second-harmonic pair、可制御な二次共鳴を持つ5状態写像で、一般
Kronecker homological solverを検証する。係数回収、real/complex変換、gauge、
非直交 similarity transform 下の左右基底 \(LV=I\) と左右不変性、条件数増大、
厳密共鳴の明示的拒否を全て gate にする。

## Q006: fixed-leaf nonzero-mode quadratic parameterization

### 問い

全質量・全運動量を固定した不変葉上で、最小 hydrodynamic shell を含む dense
candidate chart が residual order 2 → 3 を再現できるか。

### 必須観測

- \(k+(-k)=0\) が作る zero-wave-number kinetic/complement correction
- 上記 correction の保存密度・保存運動量成分が厳密にゼロ
- second harmonic generation
- internal \(R_2\)
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
