# 次に検証する問い

上から順に gate を通す。前段が失敗した場合は、失敗分析と設計修正を記録してから
同じ gate を再実行する。

## Q004b: full hydrodynamic branch tracking

### 問い

低波数で検証した moment signature と biorthogonal overlap を組み合わせれば、
D2Q9 の shear、acoustic、kinetic branches を wave vector 全域で再現可能に
分類できるか。

### 事前登録

- grid: \(17^2,33^2\)
- \(\omega=1.0,1.2,1.5,1.8\)
- axis、diagonal、一般角度の \(k\)-path
- acoustic conjugate pair、shear、kinetic clusterを追跡
- \(k\to0\) の dispersion/dissipation を既知の粘性と比較
- even grid の Nyquist modes は hydrodynamic low-\(k\) set に入らないこと

### 成功条件

- branch permutation が path reversal で一致
- complex conjugate closure
- moment signature の不連続が cluster event 以外で起きない
- small-\(k\) shear decay が
  \[
  \log|\lambda_{\mathrm{shear}}(k)|=-\nu |k|^2+O(|k|^4)
  \]
  と整合

## Q005: slow set に spectral gap はあるか

### 問い

どの \(k_c,\omega,P\) なら、次数 \(P\) までの homological operator が実用的な
condition number を持つか。

### 測定

- selected/excluded eigenvalue distance
- Fourier selection rule
  \(k_{\mathrm{out}}=\sum_j\alpha_jk_j\pmod{2\pi}\) を満たす sector 内だけの
  \(\min|\mu(k_{\mathrm{out}})-\lambda^\alpha|\)
- 実 block Kronecker homological operator の smallest singular value
- nonnormality / eigenvector condition
- grid refinement dependence

### 判断

near resonance が選択境界に現れたら、mode追加と \(k_c\)縮小の両案を比較する。
\(\omega\to2\) で gap が閉じる場合は MRT の kinetic relaxation を対照実験にする。

## Q006: nonzero-mode quadratic parameterization

### 問い

最小 hydrodynamic shell を含む dense chart で residual order 2 → 3 を再現できるか。

### 必須観測

- mean mode generation
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
6. local manifold domain超過

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

break-even が現れない regime は失敗として正直に記録する。

## Q011: boundary/forcing で manifold は維持されるか

periodic forcing → Poiseuille → Couette の順に fixed point と spectrum を作り直す。
boundary mask rank、保存収支、normal attraction を測る。

## Q012: D3Q27 へ移してよいか

D2Q9 で次を全て満たして初めて進む。

- branch tracking
- nonzero-mode quadratic residual order
- multi-step shadowing
- TT-SVD preservation
- TT-cross independent validation
- positivity/conservation
- cost report

D3Q27 の最初の問いは、D1Q3 tensor-product construction が quadrature、moment、
\(z\)-independent limit、回転等方性を同時に満たすかである。
