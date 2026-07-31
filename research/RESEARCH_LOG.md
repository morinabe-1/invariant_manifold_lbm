# 研究ログ

研究の各項目を

```text
問い → 仮説 → 実験 → 結果 → 分析 → 改善 → 次の問い
```

の順で残す。成功だけでなく、棄却された仮説を保存する。

## Cycle 001: unit-circle selector は物理中心だけを選ぶか

### 問い

D2Q9 の有限周期格子で \(|\lambda|=1\) を選べば、保存量3モードだけを
抽出できるか。

### 仮説

格子幅の偶奇に関係なく3モードになる。

### 実験

- D2Q9 BGK
- \(\omega=1.2\)
- 一様 \(\rho=1,\boldsymbol u=0\)
- \(A(k)=S(k)C\) の \(9\times9\) 固有値を全離散波数で計算
- \(8\times8\) と \(9\times9\) を比較
- unit tolerance \(10^{-10}\)

### 結果

仮説は棄却された。

| grid | strict unit count | nonzero-\(k\) unit count |
|---|---:|---:|
| \(8\times8\) | 5 | 2 |
| \(9\times9\) | 3 | 0 |

偶数格子では

\[
(k_x,k_y)=(0,\pi),(\pi,0)
\]

に \(\lambda=-1\) の checkerboard modes が1個ずつ現れた。

### 分析

modulus は物理的 mode identity を表さない。厳密な dynamical-systems center
selector は数学的には checkerboard modes も含むが、低波数流体縮約としては
不適切である。また、非零低波数 hydrodynamic modes は
\(|\lambda|<1\) なので strict selector から外れる。

### 改善

- strict-center coefficient oracle は奇数格子で行う。
- 本命の slow set は \(k=0\) から moment signature で枝追跡する。
- \(\lVert k\rVert\le k_c\) を hard admissibility にする。
- 偶数格子では Nyquist ghost count を regression test にする。

### 次の問い

moment participation と biorthogonal overlap で shear/acoustic branches を固有値衝突
の前後まで正しく追跡できるか。

## Cycle 002: 二次 homological equation は残差次数を上げるか

### 問い

解析解付き strict center family で、係数方程式を解くと invariance defect が
二次から三次へ改善するか。

### 仮説

- linear chart: \(O(\lVert a\rVert^2)\)
- quadratic chart: \(O(\lVert a\rVert^3)\)

### 実験

- \(3\times3\) の奇数周期格子
- coordinates \(a=(\delta\rho,j_x,j_y)\)
- exact family:
  \[
  W_{\mathrm{eq}}(a)=f^{\mathrm{eq}}(1+\delta\rho,\boldsymbol j)
  \]
- reduced map \(R(a)=a\)
- finite difference で \(D^2\Phi[V,V]\)
- graph gauge \(LH=0\)
- augmented homological systemを dense least squares
- amplitudes \(0.0025,0.005,0.01,0.02\)

### 結果

仮説は支持された。

- linear residual order: `1.9969022040`
- quadratic residual order: `2.9969021991`
- homological equation relative residual: `5.57e-15`
- analytic equilibrium Hessian との relative error: `7.10e-14`
- reduced quadratic dynamics norm: `3.36e-12`

最大振幅 `0.02` で

- linear residual: `9.44e-4`
- quadratic residual: `7.08e-6`

となった。

### 分析

一様 equilibrium family の curvature は kinetic complement にあり、
graph gauge で一意に回収された。exact reduced dynamics は identity なので
quadratic \(G\) は数値誤差内でゼロである。二次 chart に残る三次誤差は
\(1/\rho\) 展開の次項と整合する。

この成功は空間的 slow manifold の成功ではない。既知の厳密中心 family を再現した
coefficient-solver validation である。

finite-difference step を
`1e-1, 1e-2, 2e-4, 1e-6, 1e-8` で監査した。homological equation 自体の相対残差は
全 step で `3.86e-15`–`5.89e-15` だったが、`1e-8` では Hessian error が `2.97e-1`
まで悪化した。
従って「係数方程式を精密に解けた」ことは derivative の正確さを証明しない。
この特殊な一様 oracle では `1e-1` と `1e-2` の両方が丸め誤差水準であり、
baseline にはより局所的な `1e-2` を採用した。これは一般座標での最適 step を
意味しない。非零モードでは列スケーリング、座標別 step、Richardson 監査が必要である。

さらに seed `20260731` の64方向で residual order を確認し、

- linear: `1.9918`–`2.0079`
- quadratic: `2.9918`–`3.0079`

を得た。pure density のように defect が丸め誤差になる方向や、真の三次係数が消える
退化方向では log-log slope を次数 gate に使わず、絶対誤差と別に評価する。

### 改善

- general real \(\Lambda\) の Kronecker/Sylvester solver を作る。
- nonzero Fourier modes が生成する mean/second harmonic を含める。
- derivative step-size sweep を artifact 化する。

### 次の問い

最小非零波数の hydrodynamic conjugate pair を含む master set で、二次補正は
独立方向すべてについて三次 residual order を示すか。

## Cycle 003: dense 二次 chart を TT にしても同じか

### 問い

検証済み二次 chart の係数 tensor

\[
C_{i,\alpha_1,\alpha_2,\alpha_3}
\]

を output-block TT にしても chart 評価が変わらないか。

### 仮説

TT-SVD tolerance \(10^{-13}\) で dense chart と \(10^{-11}\) 以内に一致する。

### 実験

- coefficient shape: \(81\times3\times3\times3\)
- box-dense stored scalar slots: 2187
- monomial features \([1,a_j,a_j^2]\)
- TT-SVD relative tolerance \(10^{-13}\)
- independent coordinate \((0.01,-0.015,0.007)\)

### 結果

仮説は支持された。

- TT ranks: `[1, 6, 6, 3, 1]`
- TT core stored scalars: 657
- box-dense/TT-core storage ratio: `3.33`
- natural sparse-fiber/TT-core storage ratio: `0.863`
- relative reconstruction error: `3.01e-15`
- relative evaluation error: `7.31e-16`
- maximum post-TT invariance-residual change: `9.55e-16`

### 分析

係数表現の同値性は確認できた。ただし \(m=3\) の一様 chart は簡単すぎる。
TT は 2187-entry の box-dense tensor より小さいが、構造的に非零な7 fiber をそのまま
持つ567 stored values + 7 multi-indices の表現より大きい。657は core に格納する
scalar slot 数であり、TT gauge を除いた独立自由度数ではない。従って、自然な疎表現に
対する圧縮優位性は棄却された。serialized bytes、index/rank metadata、評価時間、
rounding時間は今後別々に測る。
また、入力 tolerance \(10^{-13}\) は discarded singular values の予算であって、
丸め誤差込みの再構成誤差保証ではない。上の再構成、評価、不変性の実測 gate を
独立に通した。
この結果だけでは次を示していない。

- spatially varying chart の rank が低い。
- TT-cross が chart を発見できる。
- TT rounding 後の長時間 rollout が正しい。
- offline cost が償却できる。

### 改善

dense nonzero-mode chart を次の oracle とし、

1. dense
2. TT-SVD
3. TT-cross

の順で同じ held-out set を比較する。cross nodes は validation から除く。

### 次の問い

low-\(k\) shell を増やしたとき、polynomial degree、spatial ordering、velocity
factorization に対して TT rank はどう増えるか。

## Cycle 004: moment content は低波数の物理枝を同定できるか

### 問い

equilibrium-tangent participation と conserved-moment polarization による局所分類で、
D2Q9 の shear viscosity と acoustic speed を回収できるか。

### 仮説

低波数で equilibrium-tangent participation が最大の3モードは、transverse shear
1個と acoustic conjugate pair である。

### 実験

- \(\omega=1.2\)
- wave magnitudes: \(0.02,0.04,0.08,0.12\)
- angles: \(0,\pi/8,\pi/4\)
- shear:
  \[
  \nu_{\mathrm{eff}}(k)=-\frac{\log|\lambda_s(k)|}{|k|^2}
  \]
- acoustic:
  \[
  c_{\mathrm{eff}}(k)=\frac{|\arg\lambda_a(k)|}{|k|}
  \]
- 全角度の観測を \(|k|^2\to0\) へ外挿

### 結果

仮説は低波数範囲で支持された。

- expected viscosity: `0.111111111111`
- extrapolated viscosity: `0.111111105670`
- relative error: `4.90e-8`
- expected sound speed: `0.577350269190`
- extrapolated sound speed: `0.577350280591`
- relative error: `1.97e-8`

acoustic pair の conjugacy error は gate `1e-12` を満たし、全選択モードの
hydrodynamic score は `0.99` より大きかった。

### 分析

固有値 modulus ではなく moment content を使う方針は、少なくとも \(k=0\) 近傍で
物理的な dispersion/dissipation と一致した。しかし各 \(k\) を独立分類しており、
大波数の mode mixing、eigenvalue collision、degenerate cluster を越えた同一性は
まだ示していない。

### 改善

- left/right eigensystem を biorthogonalize する。
- 隣接 \(k\) 間の symmetric overlap で assignment する。
- collision 近傍は個別 mode から invariant cluster tracking へ切り替える。
- path reversal と回転 path で branch identity を検証する。

### 次の問い

どの最大低波数域まで、simple branch または invariant cluster を kinetic complement
との交換なしに継続できるか。

## Cycle 005: Q004b の全域個別ラベル仮説と cluster cutoff

### 問い

\(k=0\) から継続した3次元 hydrodynamic cluster が、kinetic complement から分離し
物理的 character を保つ最大の \(|k|\le k_c\) はどこか。

### 仮説

旧仮説は「全 Brillouin zone で個別 shear/acoustic label が path-independent に
一意になる」であった。修正後の仮説は「全域一意性が破れても、ordered-Schur
cluster として path/rotation-consistent な非自明 low-\(k\) prefix が得られる」である。

### 実験

- continuous path: \(|k|=10^{-3}\) から 1.8 まで145点
- angle: \(0,\pi/8,\pi/4\)
- \(\omega=1.0,1.2,1.5,1.8\)
- simple eigenvalue 域: symmetric biorthogonal overlap
- 衝突・縮退域: 3次元 ordered-Schur subspace
- gate: equilibrium alignment 0.75、external gap 0.05、Schur sep 0.02、
  step principal angle 0.20 rad、projector norm 100、Schur/projector residual \(10^{-12}\)
- path reversal と90度回転
- construction parity: \(17^2,33^2\)
- diagnostic parity: \(16^2,32^2\)
- parity/direct-symbol audit: \(\omega=1.2\)
- direct symbols: \(A(\pi,0),A(0,\pi)\)

### 結果

旧仮説は棄却され、修正後の cluster-prefix 仮説は支持された。
表の値は最後に gate を通った sampled \(k\) であり、真の最大値ではなく \(k_c\) の
下限である。最初の不合格点との幅は各 path で約 0.01249 だった。

| \(\omega\) | axis \(k_c\) | \(\pi/8\) \(k_c\) | diagonal \(k_c\) |
|---:|---:|---:|---:|
| 1.0 | 0.763076 | 0.813049 | 0.987951 |
| 1.2 | 0.925486 | 1.000444 | 1.187840 |
| 1.5 | 1.162854 | 1.250306 | 1.387729 |
| 1.8 | 1.375236 | 1.437701 | 1.450194 |

- maximum path-reversal principal angle: \(4.5\times10^{-8}\) 未満
- maximum quarter-turn principal angle: \(4.3\times10^{-8}\) 未満
- \(17^2,33^2\): strict unit count 3
- \(16^2,32^2\): strict unit count 5
- \(A(\pi,0),A(0,\pi)\): \(\lambda=-1\) が各1個
- 全域 axis path は3次元 ordered-Schur cluster を一意に分離できない点に達した

全12 path で最初に失敗した gate は equilibrium-subspace alignment であった。
accepted prefix 内の最小 Schur separation は事前登録値 0.02 より十分大きかった。

### 分析

物理的に有効な問いは全波数域のラベル付けではなく、\(k=0\) から継続できる最大
low-\(k\) domain の同定である。cluster 内 permutation は追跡失敗ではない。
一方、上の \(k_c\) は離散 sampling と事前登録 threshold に依存する経験的境界であり、
candidate manifold の存在・一意性・normal attraction を証明しない。

Nyquist mode は分類上の nuisance だけでなく、偶数格子の excluded unit-circle
direction である。checkerboard-free 部分空間の非線形不変性を示すまでは、主構築を
奇数格子に限定する。

### 改善

- Q005 では \(k_{\rm out}=\sum_j\alpha_jk_j\pmod{2\pi}\) ごとの外部共鳴を測る。
- eigenvalue gap だけでなく ordered-Schur sep、projector norm、reduced resolvent、
  full homological operator の最小特異値を保存する。
- \(k_c\) の grid/path refinement と threshold sensitivity を監査する。

### 次の問い

accepted \(k_c\) 内の次数2 sector は、実用的な非共鳴 gap と condition number を持つか。

## Cycle 006: manufactured nonidentity quadratic oracle

### 問い

LBM の branch classification から独立な5状態写像で、一般 real-block homological
solver は既知の二次 chart、非零 \(R_2\)、複素共役実基底、near resonance を正しく
扱えるか。

### 仮説

- 既知の \(H\) と非零 \(R_2\) を丸め誤差近くで回収する。
- stable complex pair を実 \(2\times2\) block に変換できる。
- complement multiplier \(\mu\to0.82^2\) で condition number が増大する。
- \(\mu=0.82^2\) の厳密な二次共鳴を rank deficiency として拒否する。

### 実験

- full dimension 5、reduced dimension 2
- master: radius 0.82 の stable rotation pair
- complement: mean-like scalar + second-harmonic real pair
- condition 1.74 の非直交 similarity transform で左右基底を非自明化
- exact map: \(\Phi(x)=W(R(a))+A_\perp(x-W(a))\)
- mean multiplier: `0.25, 0.60, 0.66, 0.671, 0.6723`
- exact resonance: \(0.82^2=0.6724\)

### 結果

仮説は支持された。

- chart Hessian relative error: `1.40e-15`
- reduced Hessian relative error: `1.81e-15`
- homological equation relative residual: `1.78e-15`
- exact-chart invariance residual: `1.55e-17`
- condition number: `5.10 → 23.95 → 139.93 → 1239.80 → 17357.93`
- 最接近点の smallest singular value: `9.12e-5`
- real-pair right/left invariance residual: `1.12e-15` / `1.29e-15`
- real-pair duality residual: `3.20e-16`
- exact resonance: 明示的に拒否

### 分析

strict-center oracle の \(\Lambda=I,R_2\simeq0\) という特殊性を外し、一般
Kronecker operator、非零 reduced dynamics、real/complex conversion、共鳴診断を
独立に検証できた。これは algebraic solver oracle であり、非零波数 D2Q9 candidate
manifold の存在証拠ではない。

### 改善

非零波数 chart は案A、すなわち

\[
\delta M=\delta P_x=\delta P_y=0
\]

の固定保存量葉上で構築する。\(k+(-k)=0\) が生成する correction は保存モーメントを
持たない zero-wave-number kinetic 成分だけを許す。一様 strict-center oracle は保存量葉を
横切る別問題として維持し、center-slow 案Bと混ぜない。

### 次の問い

Q005: Q004b の accepted sector に quadratic external resonance、強い nonnormality、
grid refinement に伴う gap collapse がないか。

## 再現 artifact

数値の完全な記録:

[`artifacts/d2q9_baseline.json`](artifacts/d2q9_baseline.json)

[`artifacts/q004b_and_manufactured.json`](artifacts/q004b_and_manufactured.json)
