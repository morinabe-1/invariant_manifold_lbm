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

## Cycle 007: Q005 の isotropic slow set は二次非共鳴か

### 問い

Q004b の cutoff 内にある2次元 isotropic hydrodynamic set は、固定保存量葉上で
quadratic external nonresonance と finite-grid normal attraction を持つか。

### 仮説

登録した \(N=9,17,33,65\)、\(\omega=1.0,1.2,1.5,1.8\) の少なくとも1条件は、
strict quadratic nonresonance、normal attraction、実用的 condition number を
同時に満たす。

### 実験

- Q004b の方向別最小 cutoff を isotropic radial cutoff として使用
- 全 radial master wave で3次元 hydrodynamic cluster と kinetic complement を分離
- ordered-Schur separation、Riesz projector norm/residual を全 master wave で再監査
- Fourier sum \(k_{\rm out}=k_1+k_2\pmod{2\pi}\) ごとの最大 \(9\times9\) block を使用
- 数値 rank threshold:
  \(100\epsilon_{\rm mach}\max(m,n)\sigma_{\max}\)
- singular block は SVD 左 nullspace への解析的 equilibrium-Hessian forcing 射影で
  compatible/noncompatible を分類
- \(k_{\rm out}=0\) は固定葉の6次元 kinetic block だけを使用
- 全 excluded wave の最大 modulus と master の最小 modulus を比較
- 修正案として cutoff 縮小、mode追加、\(y\)-independent stripe を比較

### 結果

仮説は棄却された。実験の判定自体に必要な全 gate は通過した。

- 最小非空 C4-complete shell の external resonance: 16/16条件
- Q004b radial band 境界の external resonance witness: 14/16条件
- 最大 resonant null-forcing ratio: \(9.97\times10^{-16}\)
- radial band の normal-attraction 必要条件失敗: 14/16条件
- master 内最小 ordered-Schur separation: 0.4846
- 最大 spectral-projector norm: 1.8387
- 最大 Schur/projector residual: \(3.09\times10^{-14}\)

最小 shell の代表的な積は

\[
\lambda_{a+}(q,0)\lambda_{a-}(0,q)
\simeq\lambda_s(q,q)
\]

であり、homological block は登録した数値 rank threshold で singular になった。
共鳴 shear への二次 forcing 射影はゼロと整合したため、分類は
compatible_nonunique である。

radial cutoff の normal gap を壊した最悪 excluded mode は主に odd grid の
near-Nyquist axis sector だった。奇数格子は厳密な \(\lambda=-1\) を避けるが、
格子細分化に一様な normal gap を与えない。

### 分析

forcing compatibility は「二次方程式が不整合ではない」ことを示すが、標準 SSM
非共鳴条件と係数の一意性を回復しない。従って、登録した2次元 isotropic set を
nonresonant・normally-attracting SSM と呼ぶ仮説は棄却する。一方で、これは resonant
invariant chart が存在しないことの証明でもない。

cutoff を最小非空 shell まで縮小しても同じ障害が残る。diagonal shear orbit を
追加すれば最初の witness は internal になるが、二次和による closure cascade と
conditioning を新たに監査する必要がある。

独立な solver oracle として \(y\)-independent stripe
\(K=\{\pm(q,0)\}\) を監査した。この部分空間は full nonlinear collide-stream map で
不変で、二次出力は \(0,\pm2q\) だけである。全16条件は nonsingular かつ
\(\kappa_2<1.14\times10^4\) だった。代表 \(N=17,\omega=1.2\) では

- second-harmonic \(\sigma_{\min}=1.9335\times10^{-2}\)
- worst condition number: 96.02
- zero-wave fixed-leaf \(\sigma_{\min}=1.1550\)
- realification singular-value error: \(2.1\times10^{-15}\) 以下

だった。ただし second-harmonic \(\sigma_{\min}\) は概ね \(N^{-2}\) で閉じるため、
stripe にも grid-uniform claim は置かない。

### 改善

- full 2D Q006 を保留する。
- \(N=17,\omega=1.2\) の stripe を Q006s dense coefficient-solver oracle にする。
- stripe では Fourier selection rule により二次 \(R_2=0\) を予測する。
- diagonal shear を加える full 2D 案は resonant/near-resonant closure audit を
  別 gate にする。
- floating-point で観測した resonance identity は、後に symbolic/high-precision
  証明を試みる。

### 次の問い

Q006s: 固定葉 stripe の dense quadratic chart は、独立方向で invariance residual
order を2から3へ上げるか。

## Cycle 008: Q006s fixed-leaf stripe quadratic solver oracle

### 問い

\(N_x=17,\omega=1.2\) の \(y\)-independent invariant stripe で、first-shell の
shear/acoustic conjugate modes を実6座標へ変換し、固定保存量葉上の二次 chart が
invariance residual order を2から3へ上げるか。

### 仮説

- Fourier selection rule により二次 \(R_2=0\) となる。
- \(k=0\) kinetic block と \(\pm2k\) population blockだけで homological equation が解ける。
- analytic Hessian、graph gauge、fixed-leaf constraint が独立検証を通る。
- pilot と異なる seed の64方向で linear order \(2\pm0.1\)、quadratic order
  \(3\pm0.1\) を得る。
- 振幅0.01、32方向、100 step の quadratic shadowing が登録閾値を通る。

### 実験

- mode順序: shear、acoustic-positive、acoustic-negative
- 実座標順序: 各 mode の real/imag を interleave
- lift scale: \(s=(2N_x)^{-1/2}\)
- output basis: zero-wave kinetic 6次元 + \(\pm2k\) full-population 18次元
- solver: ordered \(6\times6\) tensor-product 36列上の real Sylvester equation
- analytic Hessian: local moment → equilibrium Hessian → output-wave streaming
- finite difference: step 0.006、0.003 の centered difference と Richardson extrapolation
- 非ゲート pilot: seed 20260801
- residual本試験: 未使用 seed 20260802、64方向、振幅
  `0.000625, 0.00125, 0.0025, 0.005, 0.01`
- shadow本試験: seed 20260803、32方向、振幅0.01、100 step
- domain stress: 同じ64方向、最大振幅0.1、判定には不使用
- quotient検証: \(1\times17\) state を \(y\) 方向へ複製した \(17^2\) state と比較

### 結果

全10個の登録 gate は通過し、仮説は登録範囲で支持された。

- solver assembly \(\sigma_{\min}=1.9335068\times10^{-2}\)
- solver assembly condition number: `96.0205`
- homological relative residual: \(4.5736\times10^{-15}\)
- graph gauge relative residual: \(1.4664\times10^{-16}\)
- global fixed-leaf Hessian residual: \(9.0339\times10^{-16}\)
- zero-wave conserved-moment residual: \(6.6589\times10^{-16}\)
- predicted reduced Hessian norm ratio: \(3.7075\times10^{-17}\)
- Richardson Hessian discrepancy: \(4.2948\times10^{-11}\)
- \(\lVert\widehat H_0\rVert_F=0.662983\)
- \(\lVert\widehat H_{+2}\rVert_F=\lVert\widehat H_{-2}\rVert_F=2.093771\)
- linear residual order range: `2.0000001–2.0000204`
- quadratic residual order range: `3.0000003–3.0002188`
- 振幅0.01の最大方向別 quadratic/linear residual ratio: `0.056721`
- local campaign minimum population: `0.027057`
- quadratic 100-step maximum absolute error: `1.8726e-6`
- quadratic maximum perturbation-relative error: `3.9270e-4`
- quadratic/linear maximum shadow error ratio: `0.016912`
- maximum conservation drift: `1.2791e-13`
- quotient-to-square 1-step maximum difference: `0.0`

保存した非ゲート診断には改善しなかった量もある。

- projected-coordinate drift: quadratic `1.2826e-6`、linear `5.0056e-7`
- 振幅0.1 stress の最大方向別 residual ratio: `0.600863`
- 振幅0.1 stress の aggregate maximum residual ratio: `0.101770`

### 分析

sector-restricted solve は、全格子の巨大な Kronecker operator を作らずに、解析的
二次 forcing、zero-wave kinetic correction、second harmonics を一貫して回収した。
残差次数2→3と独立 finite difference の一致により、homological solve が小さいだけでなく、
右辺 Hessian と座標正規化も整合している。

固定保存量葉とは global mass と global momentum を固定することである。
\(k=0\) correction の保存モーメントはゼロだが、非零の kinetic mean correction は許す。
各格子点の density/momentum perturbation がゼロという意味ではない。

厳密に不変なのは ambient な \(y\)-independent stripe 部分空間である。二次 chart は
その内部で defect が三次となる局所近似で、exact invariant manifold の証明ではない。
振幅0.1での劣化は、最大振幅0.01までの登録サンプルで支持された局所スケールを
外挿できないことを示す。半径0.01の ball 全体に対する一様保証は得ていない。
座標 drift が改善しなかったため、shadow error の改善だけから reduced coordinates が
最適だとは結論しない。

### 改善

- Q006s は \(N=17,\omega=1.2\) の finite-grid dense solver oracle としてのみ受理する。
- full 2D、grid-uniform conditioning、存在・一意性、normal attraction を主張しない。
- full 2D chart の前に、diagonal shear orbit を含む resonant/near-resonant mode-added
  closure を独立の Q006r gate にする。
- Q006r では literal な全 wave-index 加法閉包でなく、external Schur resonance と
  forcing を基準に追加 mode を選ぶ。

### 次の問い

Q006r: capped resonant/near-resonant mode addition は、全 quadratic external Schur
block を解像し、finite-grid linear normal-dominance prequalification を通過できるか。

## Cycle 009: Q006r mode-added Schur-block closure audit

### 問い

Q005 の compatible diagonal-shear resonance を selected dynamics に internalize した
16実座標 family は、有限回の mode addition で全 quadratic external block を解像し、
有限格子 linear normal-dominance prequalification も通過できるか。

### 仮説

- diagonal shear orbit の追加により既知の exact external resonance は internal になる。
- 全 unordered input Schur-block pair の external homological operator は、最大4回・
  64実座標 cap 内で singular/forced-near cluster を解消する。
- coefficient-solvability と selected/excluded normal gap の双方が通る。

### 実験

- fixed condition: \(N=17,\omega=1.2\)、固定保存量葉
- initial set: axial first-shell hydrodynamic 12実座標 + diagonal shear 4実座標
- input: 16 complex spectral blocks の unordered pair 136個
- self pair: orthonormal symmetric tensor-product basis
- output: \(k\ne0\) は \(\mathbb C^9\)、\(k=0\) は6次元 kinetic block
- selected projector: ordered-Schur Riesz projector \(P_k\)
- external forcing: \(Q_k^*(I-P_k)B_{ij,k}\)
- operator: full column-major Kronecker Sylvester matrix
- numerical singular threshold:
  \(100\epsilon_{\rm mach}\max(m,n)\sigma_{\max}\)
- near threshold: \(\sigma/\sigma_{\max}<10^{-4}\)、forcing sensitivity
  \(\ge10^{-10}\)
- response cluster: right singular-vector covariance と generalized Schur range の energy
- closure cap: 最大4 nonempty additions、64実座標
- terminal normal screen: global modulus gap、sector Sylvester separation、Riesz norm

### 結果

study validity は通過した。仮説は coefficient axis では支持されたが、normal-dominance
axis で棄却された。

- initial/final real dimension: `16 / 16`
- pair enumeration: `136 / 136`
- nonempty additions: `0`
- numerical singular / near-singular external blocks: `0 / 0`
- maximum condition number: `1894.2921`
- condition median / q90 / q99: `13.8416 / 78.8023 / 1894.2921`
- maximum solve residual: \(1.5915\times10^{-15}\)
- maximum structural residual: \(4.0689\times10^{-15}\)
- maximum fixed-leaf forcing residual: \(5.4584\times10^{-16}\)

既知の acoustic-product witness は unprojected block で
`compatible_nonunique`、\(\sigma_{\min}=5.1020\times10^{-16}\) だった。diagonal shearを
selected に入れた後の external block は \(\sigma_{\min}=0.1305687\)、condition
`13.8414` となった。従って resonance internalization は成功し、closure cascade は
発生しなかった。

normal screen は次の一項だけを落とした。

- minimum selected modulus: `0.9699501` at diagonal shear \((-1,-1)\)
- maximum excluded modulus: `0.9830465` at near-Nyquist \((0,-8)\)
- normal-dominance gap: `-0.0130964`
- minimum local Sylvester separation: `0.1305687` — pass
- maximum selected Riesz projector norm: `1.52896` — pass

### 分析

Q005 の共鳴は mode addition によって外部方程式から除けた。しかも追加後に別の
singular/near-singular cascade は現れなかったため、Q006r の coefficient closureは
16実座標で停止した。この結果により、full 2D candidate の障害を「homological
coefficient が解けないこと」と一括りにはできなくなった。

一方、near-Nyquist excluded mode は selected diagonal shear より遅く減衰する。
projector conditioning と local spectral separation は十分なので、失敗は branch
classification や nonnormal projector の数値崩壊ではなく、global decay orderingにある。
従って `coefficient-solvable finite-grid candidate` と記録するが、slow/attracting
manifold として full Q006 を開始しない。

### 改善

- Q006r 内では登録どおり normal-gap mode を追加しない。
- 同じ16実座標 family を odd-grid refinement と4個の \(\omega\) で再監査する。
- coarse grid だけの positive gap と grid-refinable gap を分ける。
- obstruction が持続する場合は、標準 BGK のまま chart 構築を強行せず、filterまたは
  collision-model modification を独立 gate にする。

### 次の問い

Q006n: near-Nyquist normal-gap failure は、登録した odd-grid refinement ladder と
relaxation sweep で一貫した obstruction か。

## Cycle 010: Q006n near-Nyquist normal-gap refinement audit

### 問い

Q006r の negative normal gap は \(N=17,\omega=1.2\) だけの有限格子現象か。それとも、
同じ16実座標 family と標準 periodic BGK に対し、登録した odd-grid refinement ladder
で一貫した near-Nyquist obstruction か。

### 仮説

- \(N\ge17\) の16条件が coefficient と blockwise projector gate を全て通る。
- 同16条件の normal gap は全て \(-10^{-6}\) 未満となる。
- 最大 excluded modulus は全条件で axial near-Nyquist sectorにある。
- direct \((\pi,0),(0,\pi)\) symbol は \(-1\) modeを持つ。

この4項を全て満たす場合だけ clean registered obstruction を支持する。ある \(\omega\) が
全 refinement gridで coefficient gateと正の gapを通る場合は viable familyとする。

### 実験

- odd grid: \(N=9,17,33,65,129\)
- relaxation: \(\omega=1.0,1.2,1.5,1.8\)
- \(N=9\) は coarse diagnostic、\(N\ge17\) は refinement gate
- fixed selected family: axial hydrodynamic + diagonal shear、16実座標
- 全質量・全運動量を固定した葉
- 全条件で unordered Schur-block pair 136個
- mode additionなし
- structural / solve tolerance: \(10^{-10}\)
- materially forced near condition ceiling: \(10^4\)
- remaining external condition ceiling: \(10^8\)
- normal gap pass: \(g_N\ge10^{-6}\)
- parity anchor: 全 \(\omega\) の \(A(\pi,0),A(0,\pi)\)

### 結果

study validity は通過したが、仮説判定は `inconclusive` だった。

- registered conditions: `20 / 20`
- pair enumeration: 全条件 `136 / 136`
- refinement coefficient + blockwise pass: `13 / 16`
- refinement negative gap: `16 / 16`
- refinement axial near-Nyquist worst mode: `16 / 16`
- coarse-grid pass: `0`
- direct Nyquist anchor: pass
- viable \(\omega\): なし
- numerical singular external block: 全条件 `0`
- maximum condition number: `2.4167863e7`
- maximum structural residual: `2.6541e-14`
- maximum solve relative residual: `1.1353e-13`

normal gap の \(N^2\) scaling は次のとおりだった。列は
\(N=9,17,33,65,129\) の順である。

| \(\omega\) | \(N^2g_N\) |
|---:|---|
| 1.0 | `-5.24648, -5.61314, -5.71894, -5.74738, -5.75476` |
| 1.2 | `-3.65084, -3.78486, -3.82396, -3.83451, -3.83725` |
| 1.5 | `-1.89785, -1.91388, -1.91776, -1.91875, -1.91900` |
| 1.8 | `-0.649628, -0.642876, -0.640570, -0.639924, -0.639754` |

clean classification を止めた coefficient failure は次の3条件だった。

| \(N\) | \(\omega\) | maximum materially forced near condition |
|---:|---:|---:|
| 65 | 1.8 | `11367.27` |
| 129 | 1.5 | `12802.79` |
| 129 | 1.8 | `45747.27` |

主 witness は acoustic-positive / acoustic-negative self-product の second harmonic
\((\pm2,0),(0,\pm2)\) だった。\(N=129,\omega=1.8\) では
\(\sigma_{\min}=5.9018\times10^{-5}\)、forcing sensitivity `0.02083`、condition
`45747.27` である。axial shear × diagonal shear の
\((\pm2,\pm1),(\pm1,\pm2)\) orbit も同条件で condition `37612.95` となった。

### 分析

near-Nyquist normal-gap failure は全登録条件で同じ位置に現れ、\(N^2g_N\) も安定した
負値へ近づいた。しかし事前登録は「16 refinement条件が coefficient gateも全通過」を
clean obstruction の必要条件にしていたため、その仮説を accepted へ変更しない。
有限5点から全 odd grid の漸近定理も主張しない。

coefficient failure は numerical singularity、branch ambiguity、solve residual failure
ではない。small waveの input productと second-harmonic outputの homological separationが
細分化で閉じる別の conditioning obstruction である。ただし condition numberだけでは、
実際の forcingが最弱方向へどの速さで近づくか、local-amplitude と global-\(\ell_2\)
coordinateで response normがどう変わるかを判定できない。

### 改善

- Q006n は `mixed coefficient/normal-gap obstruction; inconclusive` と固定する。
- Q006n の gateや thresholdを結果後に緩めない。
- Q006c では全136 pairの completenessを残しつつ、登録した16 witness pairについて
  singular separation、forcing projection、response normの scalingを分離する。
- symbol-local amplitude と global-\(\ell_2\)-isometric normalizationを併記する。
- Q006c の結果にかかわらず、negative normal gapを解消する model modification 前に
  full Q006へ進まない。

### 次の問い

Q006c: small-wave second-harmonic block の \(\sigma_{\min}\)、forcing projection、
quadratic response は、固定した refinement windowと二つの座標正規化でどの scalingを持つか。

## Cycle 011: Q006c small-wave second-harmonic coefficient scaling

### 問い

Q006nの3個のcoefficient failureは、真のsmall-wave second-harmonic near resonanceと
local-amplitude quadratic curvatureの増大を表すか。それともforcingの消失と座標正規化に
より、condition-only gateがboundedな係数を過剰棄却しただけか。

### 仮説

固定window \(N=33,65,129,257\) で、acoustic-self second harmonicと
axial-shear × diagonal-shearの両orbitが、全4 \(\omega\) について

\[
\sigma_{\min}\sim N^{-2},\quad
\kappa\sim N^2,\quad
\lVert b\rVert\sim N^0,\quad
|u_{\min}^*b|\sim N^{-1},\quad
\lVert x\rVert\sim N,\quad
\frac{\lVert x\rVert}{N}\sim N^0
\]

を同時に示す。\(N=257\) で新しいmaterially forced witness classが現れればclean
classificationを出さない。

### 実験

- odd grid: \(N=17,33,65,129,257\)
- relaxation: \(\omega=1.0,1.2,1.5,1.8\)
- fixed fit window: \(N=33,65,129,257\)
- 全条件でfixed-leaf 16実座標、全136 pairを列挙
- target 1: axial acoustic self-product 8 pair
- target 2: axial shear × diagonal shear 8 pair
- 各targetでfull operator、forcing、full SVD、minimum-norm responseを保存
- global-\(\ell_2\) normalization: symbol response normをside length \(N\) で割る
- orbit relative-spread gate: \(10^{-8}\)
- structural / solve gate: \(10^{-10}\)
- mode addition、threshold tuningなし

### 結果

全validity gateと8本のfitに含まれる全scaling windowが通過し、仮説は登録範囲で
支持された。

- study outcome: `accepted`
- classification: `genuine weakly-forced small-k resonance supported`
- conditions / fits: `20 / 8`
- pair / target count: 全条件 `136 / 16`
- maximum orbit relative spread: `1.6046e-10`
- \(N=257\) materially forced witness / target外 witness: `56 / 0`
- maximum target condition: `182598.06`
- maximum all-pair condition: `3.8074e8`
- maximum structural residual: `6.6025e-14`
- maximum solve relative residual: `1.7609e-13`

| metric | 8 fitのslope range | registered window |
|---|---:|---:|
| \(\sigma_{\min}\) | `-2.04791 … -1.98123` | `[-2.25,-1.75]` |
| detuning | `-2.04823 … -1.99309` | `[-2.25,-1.75]` |
| condition | `1.97607 … 2.04818` | `[1.75,2.25]` |
| forcing norm | `0.00257 … 0.00833` | `[-0.25,0.25]` |
| weakest forcing \(\beta\) | `-0.99574 … -0.98548` | `[-1.25,-0.75]` |
| local response | `0.95557 … 1.05216` | `[0.75,1.25]` |
| global-\(\ell_2\) response | `-0.04443 … 0.05216` | `[-0.25,0.25]` |

代表として \(N=257,\omega=1.2\) のacoustic-self orbit medianは、
\(\sigma_{\min}=8.8532\times10^{-5}\)、condition `20334.25`、
\(\beta=0.0325874\)、local response `368.089`、global-\(\ell_2\) response
`1.43225` だった。\(\omega=1.8\) ではlocal response `2204.23` に対して
global-\(\ell_2\) response `8.57676` である。

### 分析

operator separationとeigenvalue detuningが同じ \(N^{-2}\) exponentを持ち、orbit symmetry、
solve residual、full SVD reconstructionも通るため、near resonanceをbasis selectionや
roundoffへ転嫁できない。forcingの最弱方向成分は \(N^{-1}\) まで小さくなるが、逆operator
が \(N^2\) で増幅するため、固定local amplitudeのquadratic responseは \(N\) で増える。

global-\(\ell_2\) coordinateでboundedになるのは、unit-norm Fourier basisがlocal basisを
\(1/N\) 倍するためである。これはlocal-amplitude chartのgrid-uniform性を回復しない。
また全pair最大conditionは旧 \(10^8\) ceilingを超えた。従ってQ006nを遡及的に成功扱いせず、
Q006cの受理範囲を有限ladder上のscaling classificationに限定する。

### 改善

- unfiltered標準BGKのfull Q006は保留する。
- near-Nyquist normal gapを直接減衰させる保存的5点filterを、別の変更モデルとして監査する。
- filter後も全136 pair、Q006c target class、二つのcoordinate normalizationをbaselineに残す。
- low-wave eigenvector/phase、relative modulus、global conservation、positivityを独立gateにする。
- viable parameterは結果後に選ばず、登録sweepからlexicographic ruleで一意に決める。

### 次の問い

Q006f: 保存的checkerboard filterは、低波数geometryとQ006c scalingを壊さず、登録odd-grid
ladderでnormal dominanceを回復するviable \((\eta,\omega)\) を与えるか。

## Cycle 012: Q006f conservative checkerboard-filter audit

### 問い

global conservation、uniform equilibrium、positivity、low-wave geometryを保つ5点convex
filterをBGK step後へ加え、登録odd-grid ladderでnormal dominanceを回復できるか。

### 仮説

事前登録した \(\eta\in\{0,0.01,0.02,0.03,0.05\}\)、
\(\omega\in\{1.0,1.2,1.5,1.8\}\)、\(N\in\{17,33,65,129,257\}\) の中に、
全spectral・coefficient・scaling gateを通る正の\(\eta\) familyが1個以上ある。

### 実験

- 100条件を重複・欠落なく実行し、各条件で固定16実座標の全136 unordered pairと
  Q006c登録16 targetを再監査した。
- filter単独のconvexity、conservation、constant state、minimum principle、Fourier
  multiplier、Nyquist anchorをseed `20260809` で独立に検証した。
- selected subspace、phase、relative modulus、Riesz projector、local separation、normal
  gapを全5 gridで評価した。
- full external condition ceilingは \(10^9\)、normal-gap thresholdは \(10^{-6}\) のまま
  固定し、mode additionや結果後のparameter追加は行わなかった。

### 結果

study validityは通過したが、viable familyは0で、仮説は有効に棄却された。

- outcome / classification: `rejected / no viable registered filtered family`
- registered / unique conditions: `100 / 100`
- pair / target count: 全条件 `136 / 16`
- filter algebra gate: 全5項通過
- coefficient gate: `20 / 20` family通過
- normal-gap gate: `0 / 20` family通過
- raw gapが正のfamily: `11 / 20`
- maximum five-grid minimum gap: `9.5571481e-9`
- maximum all-pair condition: `7.4420686e8`
- maximum target response ratio to unfiltered: `1.0`
- maximum structural / solve residual: `6.6025e-14 / 1.7609e-13`
- maximum conservation/constant residual: `7.7965e-16`
- maximum Fourier multiplier discrepancy: `1.7356e-16`
- maximum checkerboard-anchor error: `2.0053e-15`

全40 fit（20 family × 2 target orbit）はQ006cと同じ7 slope windowを通過し、filtered
target responseは対応するunfiltered responseを一度も1.10倍以上へ悪化させなかった。
従って棄却理由はnormal gap一項に局在する。

### 分析

filterはnear-Nyquist obstructionを減衰させたが、十分に減衰したfamilyのglobal
bottleneckは同じ対角第一shell \((\pm1,\pm1)\) にあるselected shearとexcluded
acousticのmodulus差へ移った。例えば \((\eta,\omega)=(0.02,1.2)\) ではgapが

\[
5.0817\times10^{-4},\ 3.5322\times10^{-5},\ 2.3383\times10^{-6},\
1.5059\times10^{-7},\ 9.5571\times10^{-9}
\]

と減少した。正のgapを持つ11 familyの5点log-log slopeは
`-4.0284 … -4.0052` だった。これは事後診断であり、Q006fの登録thresholdを緩めたり
結果をacceptedへ変更したりしない。

同一wave sectorではscalar filterが全固有値を同じ正の\(\chi_\eta(k)\) で掛けるため、
shear/acousticの符号付きgap、相対順序、leading exponentを独立には変更できない。
Q006fだけではこのlow-wave tangencyを拡張grid上で確定していないため、次に専用の
symbol-level auditを置く。

### 改善

- Q006fとQ006nの棄却判定を維持し、filtered full Q006へ進まない。
- absolute normal-gap thresholdを事後に緩和しない。
- scalar-filter classの限界と対角hydrodynamic clusterの接触次数をQ006gで分離する。
- Q006gを通過した場合だけ、diagonal acousticを含むcluster-complete familyか、
  grid依存physical bandのどちらを次に監査するかを新しく事前登録する。

### 次の問い

Q006g: Q006fの唯一の失敗gateは、scalar population filterでは変えられない対角第一shellの
shear/acoustic \(N^{-4}\) tangencyで説明できるか。

## Cycle 013: Q006g diagonal low-wave shear/acoustic tangency

### 問い

Q006fで唯一落ちたnormal-gap gateは、同じ対角第一shell sectorのselected shearと
excluded acousticが4次で接し、scalar population filterでは相対順序もseparation exponentも
変えられないことに由来するか。

### 仮説

7 odd grids、全5 \(\eta\)、全4 \(\omega\)、対角C4 orbitの140条件・560 waveで、
符号付きgapが登録sign patternを持ち、absolute/relative gapがともに \(N^{-4}\) となる。

### 実験

- grid: \(N=33,65,129,257,513,1025,2049\)
- fixed fit: \(N=129,257,513,1025,2049\)
- C4 orbit: \((1,1),(-1,1),(-1,-1),(1,-1)\)
- direct filtered eigensystemと、unfiltered moment classificationへscalar multiplierを掛ける
  経路を独立に計算した。
- gap、relative gap、\(N^4g\)、C4 spread、eigensystem residual、scalar identity errorを保存した。
- full-zone sweep、quadratic solve、mode addition、threshold変更は行わなかった。

### 結果

全validity gateと20 familyの全hypothesis gateが通過し、仮説を登録範囲で受理した。

- outcome: `accepted`
- classification: `same-sector hydrodynamic fourth-order tangency confirmed`
- registered / unique conditions: `140 / 140`
- registered / unique wave records: `560 / 560`
- family fit pass: `20 / 20`
- absolute-gap slope: `-4.0008778 … -3.9997961`
- relative-gap slope: `-4.0009176 … -4.0000699`
- maximum scaled-gap relative spread: `0.00180356`
- maximum C4 gap spread: `4.2188e-15`
- maximum eigensystem residual: `1.3344e-15`
- maximum eigenvalue matching residual: `4.3673e-15`
- maximum scalar-gap identity error: `5.0034e-15`

全fit grid・全\(\eta\)で、\(\omega=1.0\) のsigned gapは負、
\(\omega=1.2,1.5,1.8\) は正だった。\((\eta,\omega)=(0.02,1.2)\) では
\(N^4g\) がfit grid上で `41.7026, 41.6928, 41.6903, 41.6898, 41.7005` となった。

### 分析

同じwave vectorにある全population eigenmodeは、filterにより同一の正scalar
\(\chi_\eta(k)\) を受ける。従って

\[
g_{\eta,N}=\chi_\eta(k)g_{0,N}
\]

であり、scalar filterは符号、相対順序、leading exponentを変えられない。Q006fで
Nyquist obstructionを除いた後に現れた \(N^{-4}\) gapは、枝分類やroundoffのartifactでは
なく、16実座標familyが対角acousticを外部へ残したことに対応する構造的bottleneckである。

これはQ006fをacceptedへ変える結果ではない。また有限7点fitは全grid theoremではない。
次は同じnormal thresholdを保ち、対角第一shellのacoustic pairもselectedへ含めた
cluster-complete familyを独立に監査する。

### 改善

- axial/diagonal第一shellの各waveでshearとacoustic pairを全て含める。
- 選択次元を16から24へ増やし、C4・共役閉包を構成時に固定する。
- Q006fと同じfilter sweep、normal threshold、condition ceiling、Q006c target baselineを使う。
- mode additionなしのminimal cluster-complete familyを先に反証する。

### 次の問い

Q006h: diagonal acousticをselectedへ昇格した24実座標familyは、登録filter sweepで
coefficient solvabilityと有限ladder normal dominanceを同時に満たすか。

## Cycle Q006h: first-shell cluster-complete filtered family

### 問い

第一shellの全8 waveでshearとacoustic pairをselectedへ含めた24実座標familyは、
登録checkerboard-filter sweepでcoefficient solvabilityと有限ladder normal dominanceを
同時に満たすか。

### 仮説

登録した正の \(\eta\) familyのうち1個以上が、5 grid全てでspectral、low-wave、
coefficient、response、scaling gateを通る。

### 実験

- odd grid: \(N=17,33,65,129,257\)
- filter: \(\eta=0,0.01,0.02,0.03,0.05\)
- relaxation: \(\omega=1.0,1.2,1.5,1.8\)
- 100条件、各24 one-dimensional block、300 unordered pair
- Q006cの16 targetと7 scaling windowを維持
- mode additionなし
- 全pair table、condition quantile、最悪pair、material witness classを保存

### 結果

全validity gateが通過し、登録仮説を有限ladderの範囲で受理した。

- outcome: `accepted`
- classification: `cluster-complete filtered finite-ladder prequalification passed`
- viable family: `6 / 20`
- deterministic selection: \((\eta,\omega)=(0.01,1.5)\)
- selected minimum normal gap: `6.9386924e-5`
- selected minimum local Sylvester separation: `1.1600649`
- selected maximum Riesz projector norm: `1.5115930`
- selected maximum external condition: `5.9581662e8`
- selected maximum target response ratio: `0.9647730`
- selected maximum structural/fixed-leaf/solve residual: `8.3841e-14`
- numerical singular block: `0`

選択familyのnormal gapはgrid順に
`0.0020611, 0.0041556, 0.0010814, 0.00027523, 0.000069387`、最大conditionは
`1.4514e4, 1.7105e5, 2.4697e6, 3.7920e7, 5.9582e8` だった。従って全登録gridでは
閾値を通るが、grid-uniformな下界は示していない。

materially forced near witnessは選択familyで40件だった。内訳はQ006cの
axial acoustic self second harmonic 16件、axial shear–diagonal shear mixed harmonic
16件、新しいdiagonal acoustic self second harmonic 8件である。新classは \(N=257\) の
\((\pm1,\pm1)+(\pm1,\pm1)\to(\pm2,\pm2)\) に現れ、conditionは約 `2.4298e4`、
weak-direction forcing sensitivityは約 `0.02049` だった。全件を分類・保存し、事前登録どおり
class出現自体ではなくcondition ceilingと残差で判定した。

### 分析

Q006gで特定したsame-sector \(N^{-4}\) bottleneckは、対角acoustic pairをselectedへ含める
ことで外部normal-gap判定から除かれた。その結果、最小の正filterである \(\eta=0.01\) に
viable familyが現れた。一方、高解像度側ではnormal gap低下とhomological condition増大が
続くため、受理範囲は変更写像・有限5-grid・24座標familyのprequalificationに限る。
all-grid theorem、grid-uniform chart、非線形normal attraction、full chartの存在・一意性は
主張しない。

### 改善

- 選択parameterを \((\eta,\omega)=(0.01,1.5)\) に固定し、parameter探索を終了する。
- 最初のfull 2D chartは計算可能な \(N=17\) dense oracleに限定する。
- internal tangential outputには非自明な \(R_2\) を許し、graph gaugeを明示する。
- zero-wave correction、second harmonic、C4/conjugacy、独立Hessian差分、残差次数、
  100-step shadowingを別々に検証する。

### 次の問い

Q006i: \((N,\eta,\omega)=(17,0.01,1.5)\) の固定保存量葉上で、24実座標のfull 2D
dense quadratic candidate chartは不変性残差次数を2から3へ改善できるか。

## Cycle Q006i: filtered full-2D dense quadratic chart

### 問い

Q006hが固定した変更写像と24実座標familyについて、非自明な \(R_2\) を含むdense quadratic
candidate chartは、独立微分検証を通り、残差次数を2から3へ改善し、100-step shadowingと
保存量の全登録gateを満たすか。

### 仮説

構成validity、局所不変性、positivity、global conservation、100-step shadowingの全gateが
通過し、`N17 filtered full-2D quadratic candidate chart verified` と判定される。

### 実験

- \((N,\eta,\omega)=(17,0.01,1.5)\)、固定質量・運動量葉
- 第一Chebyshev shellの8 wave × 3 hydrodynamic mode、24実座標
- 300 unordered pairをzero-wave kinetic、internal selected、external full blockに分解
- internal outputではgraph gaugeを課し、tangential componentを \(R_2\) として同時に解く
- seed `20260808`、32方向、2 stepとRichardson extrapolationによる独立Hessian検証
- seed `20260809`、64方向、5振幅によるlinear／quadratic残差次数
- seed `20260810`、32方向、振幅0.01、100 stepのlinear／quadratic shadowing

### 結果

全validity gateは通過したが、hypothesis gateはglobal conservationだけが失敗した。従って
封印規則どおり`rejected`とした。

- classification: `Q006i local chart hypothesis rejected`
- pair count: `300` = zero `36` + internal `108` + external `156`
- numerical singular block: `0`
- minimum operator singular value: `1.5502436e-4`
- maximum operator condition: `1.4513931e4`
- maximum solve relative residual: `1.0863772e-14`
- homological relative residual: `2.3530055e-15`
- graph-gauge residual: `3.1780609e-16`
- coefficient conservation residual: `3.6863996e-15`
- conjugacy / C4 Hessian residual: `1.0915747e-14 / 5.6073056e-14`
- \(\lVert R_2\rVert_F\): `0.6040702`
- independent Hessian maximum discrepancy: `9.0693268e-10`（上限 `1e-8`）
- linear residual slope: `1.9998167 ... 2.0002631`
- quadratic residual slope: `2.9997300 ... 3.0002761`
- maximum quadratic/linear residual ratio: `0.00658935`
- quadratic shadow maximum absolute / relative error: `1.5115145e-7 / 2.2173082e-5`
- quadratic/linear shadow-error ratio: `0.00512138`
- linear / quadratic conservation drift: `2.7284963e-12 / 2.7284953e-12`
- minimum population: `0.0275263`

### 分析

homological solve、graph gauge、conjugacy、C4、Fourier support、独立Hessianが整合し、登録64方向で
残差次数が2から3へ改善した。100-step state errorも全shadowing閾値を大幅に通過した。従って
二次chart係数の誤りを示す証拠は得られなかった。

一方、global conservation上限 \(10^{-12}\) に対する最大値は約 \(2.73\times10^{-12}\) である。
linear／quadratic trajectoryで値がほぼ一致するため、chart Hessian固有の違反よりも、保存量の
通常和またはfull-map float64反復に共通する丸め誤差が候補になる。ただし、この解釈を理由に
Q006iを遡及的にacceptedへ変更したり、閾値を緩和したりしない。

### 改善

- Q006iの同じ64 trajectoryを、通常和と二つの補償和で再測定する。
- 各full stepをcollision、streaming、filterへ分解し、signed moment incrementを保存する。
- exact-arithmeticでは恒等なfixed-leaf roundoff projectionを対照としてのみ追加する。
- Q006i artifactと判定は不変に保ち、診断は別artifact Q006jへ保存する。

### 次の問い

Q006j: Q006iの単一失敗gateは保存量の通常和だけで生じたのか、それともfloat64 full mapの
どのstageで蓄積した実状態の丸めdriftなのか。

## Cycle Q006j: float64 global-conservation drift source audit

### 問い

Q006iの単一失敗gateはNumPy reductionだけの測定誤差か。それともfloat64 full mapが実状態に
蓄積したdriftか。後者ならcollision、streaming、filterのどこに局在するか。

### 仮説

補償和でQ006i超過が消えるか、補償和でも残る場合はstage増分で全driftを再構成でき、登録した
一様fixed-leaf projectionで \(10^{-12}\) 以下へ制御できる。

### 実験

- Q006iのseed `20260810`、linear／quadratic各32、合計64 trajectory
- 振幅0.01、100 step、8 checkpoint、6,400 stage record
- NumPy reduction、`math.fsum`、独立Neumaier補償和
- collision、periodic streaming、five-point filterのsigned moment increment
- 各step後のuniform equilibrium-tangent fixed-leaf projection control

### 結果

全validity gateは通過したが、projection controlの保存gateだけが失敗したため、登録規則どおり
`structural or unresolved conservation defect`として`rejected`とした。

- Q006i NumPy drift reproduction error: `0`
- maximum NumPy drift: `2.7284963e-12`
- maximum `math.fsum` / Neumaier drift: `2.7285042e-12 / 2.7285042e-12`
- maximum `math.fsum`–Neumaier component difference: `0`
- maximum NumPy–`math.fsum` measurement difference: `1.1368684e-13`
- stage-map identity / streaming drift / reconstruction error: `0 / 0 / 0`
- collision maximum one-step / cumulative norm: `5.6869073e-14 / 2.6716420e-12`
- filter maximum one-step / cumulative norm: `5.6845056e-14 / 5.1159450e-13`
- projection-control maximum drift: `2.1600519e-12`
- maximum single / cumulative projection norm: `1.6729733e-15 / 1.1419158e-13`
- projected / standard maximum state difference: `1.4274532e-13`
- projected minimum population: `0.0275271`

### 分析

NumPyと補償和の測定差は最大 \(1.14\times10^{-13}\) に留まり、補償和でも
\(2.73\times10^{-12}\) のdriftが残る。従ってQ006iの失敗はreduction-onlyではなく、実際の
float64 stateに蓄積している。streamingはpopulation permutationとして補償和driftが厳密に0、
collisionの累積が主寄与、filterが副寄与だった。全stage増分はtotal driftを誤差0で再構成した。

一方、exact arithmeticでは恒等な一様fixed-leaf projectionは、補正normが十分小さいにもかかわらず
100-step driftを \(10^{-12}\) 以下へ戻せなかった。分散した各population補正がlocal ULPに吸収された
可能性があるが、Q006jでは変更されたpopulation数や実現moment correctionを保存していないため、
まだ結論にしない。またこの失敗を数学的なBGK/filterの非保存性の証明とは解釈しない。

### 改善

- Q006jの同じ64 trajectoryと各step errorを固定する。
- 一様補正について、intended correction、実際のstate delta、changed-entry fraction、ULP ratio、
  realized moment correctionを保存する。
- 診断対照として固定siteの \(q_0,q_1,q_2\) だけを使う3×3 moment solveを一回適用する。
- localized controlはtranslation/C4 symmetryを壊すため、成功しても本番写像へ採用しない。

### 次の問い

Q006k: Q006jの一様projection失敗はsub-ULP分散補正の表現不能で説明でき、同じintended global
moment correctionを固定3-populationへ局在化すれば登録100-step保存上限を通るか。

## Cycle Q006k: fixed-leaf projection representability audit

### 問い

Q006jの一様projection失敗は、intended global moment correctionをfloat64 populationへ分散加算した
際の実現誤差で説明できるか。同じcorrectionを固定3 populationへ局在化すれば保存上限を通るか。

### 仮説

一様補正に非零のrealization errorを観測し、固定 \((0,0)\) siteの \((q_0,q_1,q_2)\) 一回補正が
positivityと微小state差を保ったまま、100-step driftを \(10^{-12}\) 以下へ抑える。

### 実験

- Q006jと同じlinear／quadratic各32、合計64 trajectory、100 step
- standard／uniform／localizedの合計19,200 control-step
- 一様補正のchanged-entry count、ULP ratio、intended／realized moment correction
- 固定site \((0,0)\)、population \((q_0,q_1,q_2)\) の解析的3×3 solve、一回補正
- `math.fsum`とNeumaierによる独立保存量集約

### 結果

全validity gateとhypothesis gateを通過し、
`uniform projection representability failure localized`としてacceptedとした。

- Q006j standard / uniform reproduction error: `0 / 0`
- standard / uniform maximum drift: `2.7285042e-12 / 2.1600519e-12`
- nonzero uniform correction-error step: `6400 / 6400`
- maximum uniform global correction error: `5.7125343e-14`
- changed population count: `0 ... 2601`、mean `1563.0384`
- ULP ratio: `4.8020027e-20 ... 1.8158401`、median-of-medians `1.5747789`
- localized maximum drift: `1.5115007e-16`
- localized maximum correction norm: `5.9292511e-14`
- localized / standard maximum state difference: `1.0385189e-13`
- minimum population: `0.0275271`
- moment matrix rank / condition / maximum solve residual: `3 / 3.7320508 / 0`

### 分析

一様補正は全stepでintended global moment correctionを正確に実現しなかった。stepによっては
2,601 entries全てが変化せず、平均changed fractionは約0.601だった。一方でULP ratioの
median-of-mediansは1.57であり、全entryがsub-ULPだったわけではない。従って支持された説明は、
分散加算全体のfloat64 realization errorであり、単純な「全項丸め落ち」ではない。

固定3-population controlはdriftを機械精度近くまで抑え、standardとの差も \(1.04\times10^{-13}\)
だった。これは数学的保存構造が失われた証拠ではなく、補正の算術的実現方法が律速だったことを
支持する。ただし固定site／populationはtranslation／C4を壊すため、production mapとして無効である。
Q006iとQ006jの封印判定は変更しない。

### 改善

- 固定座標でなく、stateのrest population \(q_0\) が最大の一意なsiteをanchorにする。
- population correctionは保存moment matrixのC4共変なminimum-norm right inverseを使う。
- collision／filter各stageで、2つのtranslation generatorとquarter-turnに対するcorrection
  operator equivarianceを全stepで測る。
- anchor uniquenessをvalidity gateにし、tie時のrow-major fallbackを受理範囲から除外する。

### 次の問い

Q006l: collision／filter各stageのstate-covariant anchorとC4共変right inverseによる一回補正は、
登録64 trajectoryで保存上限、positivity、translation／C4 equivarianceを同時に満たすか。

## Cycle Q006l: stagewise state-covariant conservative arithmetic

### 問い

Q006kの固定site依存を除き、collision／filter各stageの \(q_0\) 最大siteとC4共変right inverseを使う
一回補正は、保存上限、positivity、translation／C4 equivarianceを同時に満たすか。

### 仮説

全registered trajectoryでanchorが一意に分離し、stagewise controlがstandardとの差を微小に保ったまま
100-step保存driftを \(10^{-12}\) 以下にし、2 translation generatorとquarter-turnに共変となる。

### 実験

- Q006kと同じlinear／quadratic各32、合計64 trajectory、100 step
- standard／fixed／stagewise-covariantの合計19,200 control-step
- collision後とfilter後に各一回、global residualをminimum-norm right inverseで補正
- 各12,800 stageでunique-anchor gapを保存
- 各stageでtranslation-y、translation-x、quarter-turnの補正operatorを直接比較

### 結果

全validity／hypothesis gateを通過し、
`covariant anchor correction controls registered drift`としてacceptedとした。

- Q006k standard / fixed reproduction error: `0 / 0`
- covariant maximum drift: `1.1368684e-13`
- minimum collision / filter anchor gap: `1.6348855e-9 / 1.2466926e-9`
- anchor covariance failure: `0`
- maximum translation / quarter-turn error: `0 / 0`
- right-inverse condition / residual: `1.2247449 / 2.2204460e-16`
- maximum single-stage correction norm: `1.8963156e-14`
- covariant / standard maximum state difference: `1.1557707e-13`
- minimum population: `0.0275271`
- `math.fsum` / Neumaier maximum component difference: `0`

### 分析

登録した非零振幅trajectory上では、state-derived anchorはtranslation／C4のgeneratorに厳密に共変で、
補正は100-step driftを上限の約0.114倍へ抑えた。固定site controlよりdriftは大きいが、対称性を
失わず、state差とcorrection normは十分小さい。

ただし、これは平衡近傍の滑らかなmapをまだ定義しない。一様平衡では \(q_0\) が全289 siteで等しく、
unique anchor gapは0である。周期translationに不変なstateからtranslation-equivariantに一つのsiteを
選ぶことは、どのsiteもtranslation generatorの固定点でないため不可能である。従ってQ006lの受理は
unique-anchor有限軌道に限定し、production map、Taylor微分、Q006i再判定へ拡張しない。

### 改善

- uniform equilibriumのtie multiplicityとtranslation stabilizerを明示的に監査する。
- equivariant unique-site selectorの固定点条件を有限群作用として検証する。
- Q006i方向を振幅縮小し、collision／filter anchor gapが0へ近づくことを記録する。
- このobstructionを通過するまでQ006l mapでHessian、chart、shadowingを再計算しない。

### 次の問い

Q006m: periodic translation-equivariantなunique-site anchor selectorは、一様平衡へ連続・微分可能に
延長できず、Q006l correctionをlocal parameterization mapに採用できないか。

## Cycle Q006m: equivariant unique-anchor differentiability obstruction

### 問い

Q006lのunique-site anchor selectorは、周期translationに不変なuniform equilibriumへequivariantかつ
連続・微分可能に延長できるか。

### 仮説

uniform stateは全translationで固定される一方、周期site作用の非自明なgeneratorには固定siteがない。
従ってequivariant unique-site selectorは平衡で値を持てず、登録振幅を縮小すると \(q_0\) top-two gapも
0へ向かう。

### 実験

- \(X=\mathbb Z_{17}\times\mathbb Z_{17}\) の全289 siteを2 translation generatorについて列挙
- uniform stateのbitwise invariance、row-major tie break、C4補助診断
- linear／quadratic各32方向、6 amplitude、正負、collision／filterの1,536 stage observation
- chart／stage／signごとの8本のmaximum-gap ladder

### 結果

全validity／hypothesis gateを通過し、
`equivariant unique-anchor obstruction confirmed`としてacceptedとした。

- uniform maximum multiplicity / gap: `289 / 0`
- translation-y / translation-x fixed-site count: `0 / 0`
- common fixed-site count: `0`
- maximum uniform translation error: `0`、bitwise invariant: `true`
- row-major translation covariance failure: `2 / 2`
- direction-amplitude / signed-state / stage record: `384 / 768 / 1536`
- failed gap ladder: `0 / 8`
- maximum smallest/largest-amplitude gap ratio: `1.0052062e-5`
- minimum population: `0.0275189`

### 分析

equivarianceを満たすselector \(s\) がuniform state \(f_*\) で定義できれば、任意のgenerator \(g\) に対し

\[
s(f_*)=s(T_gf_*)=g\cdot s(f_*)
\]

が必要である。しかし2 generatorはいずれも固定siteを持たないため矛盾する。これは連続性の問題より
強く、equivariant unique-site selectorは平衡で定義自体ができない。8本のgap ladderの最大比は全て
登録上限 \(10^{-4}\) を通り、最大でも `1.0052062e-5` だったが、これは有限振幅診断であって固定点矛盾の
証明には用いない。

従ってQ006lの有限unique-anchor trajectory上のacceptedは維持するが、そのcorrectionを平衡近傍の
production map、Taylor derivative、Q006i再判定へ使わない。排除したのはunique-site selector classだけで、
anchor-freeなsmooth correctionや、写像を変更しないroundoff budgetは未判定である。

### 改善

- Q006jのuniform minimum-norm projectionをanchor-free smooth controlとして再利用する。
- 標準写像には観測driftからfitしないcomponentwise ULP budgetを事前登録する。
- uniform correctionを選ぶには、worst driftを2倍以上改善し、全stepでremaining driftを0にすることを
  要求する。
- どちらを選んでもQ006i／Q006jの封印判定は遡及変更せず、必要なら別gateでdual-reportingする。

### 次の問い

Q006o: anchor-free uniform projectionは標準写像を置き換えるだけの改善とexact realizationを示すか。
示さない場合、unmodified mapの登録driftは2 conservation-sensitive stageから定めた明示的ULP budget内に
収まるか。

## Cycle Q006o: anchor-free correction versus forward-error budget

### 問い

Q006lの非滑らかなanchor correctionを採用せず、Q006jのuniform projectionを使うべきか。それとも
標準写像を変更せず、明示的なcomponentwise ULP budgetでroundoffを管理すべきか。

### 仮説

unmodified mapの全登録driftは、collision／filter各stageへglobal component scaleの1 ULPを割り当てた
\(B_c(t)=2t\,\operatorname{spacing}(S_c)\) に収まる。一方、uniform projectionはworst driftを2倍以上
改善せず、remaining local driftもexact zeroにできない。

### 実験

- Q006jと同じlinear／quadratic各32、合計64 trajectory、100 stepを独立再実行
- 6,400 trajectory-step × 3 component = 19,200 budget check
- 初期stateの \(S_c=\sum_{x,q}|C_{cq}f_{0,x,q}|\) だけからbudgetを計算
- Q006j standard／uniform drift、streaming、補償和、positivityを再現
- uniform selectionに改善率2以上とremaining drift 6,400 / 6,400 exact zeroを要求

### 結果

全validity／standard-policy gateを通過し、uniform-policy gateは2個とも失敗した。
`unmodified equivariant map with registered forward-error budget preferred`としてacceptedとした。

- standard budget violation: `0 / 19200`
- maximum utilization: `0.5`
- maximum final component budget: `1.1368684e-11`（上限 `1.2e-11`）
- maximum streaming increment / independent-sum difference: `0 / 0`
- standard / uniform maximum drift: `2.7285042e-12 / 2.1600519e-12`
- uniform improvement factor: `1.2631660`（下限 `2`を失敗）
- uniform exact-zero remaining drift: `0 / 6400`
- maximum uniform remaining local drift: `5.7125343e-14`
- minimum population: `0.0275271`

### 分析

standard mapのworst witnessはlinear direction 0のstep 1 massで、absolute drift
`5.6843419e-14`に対するbudgetは`1.1368684e-13`、utilizationはexactly `0.5`だった。全trajectory・
componentでviolationはなく、100-step最大budgetも登録上限内だった。

uniform projectionはworst driftを約20.8%減らしただけで、必要な2倍改善に届かなかった。また全stepで
remaining local driftが非零であり、anchor-free smooth correctionとして標準写像を置き換える根拠を
満たさない。従ってmapは変更せず、roundoffを明示的に別報告する。

ただし \(2t\,\operatorname{spacing}(S_c)\) は登録trajectory用のoperational envelopeであり、一般の
forward-error theoremではない。Q006i／Q006jの旧 \(10^{-12}\) failureを遡及的に消さない。

### 改善

- Q006iの旧8 gateをoriginal columnとしてそのまま再現する。
- global conservationだけをQ006o policyで別columnに置換し、他7 gateは変更しない。
- Q006iとQ006oの方向・seed・amplitude・horizon alignmentを誤差0で照合する。
- integration後も別seed／amplitude／horizonのholdoutを要求する。

### 次の問い

Q006p: Q006iのoriginal conservation failureを保持したdual reportで、unmodified-map chart continuationを
条件付きで支持できるか。

## Cycle Q006p: Q006i dual-reporting integration audit

### 問い

Q006iの旧 \(10^{-12}\) conservation failureを保持したまま、同じtrajectoryをQ006oのforward-error policyで
別欄評価し、candidate chartの条件付き継続を支持できるか。

### 仮説

original columnではglobal conservationだけが失敗し続ける。一方、global conservationだけをQ006o standard
policyへ置換したpolicy columnでは、他7 gateを一切変えずに全8 gateが通る。

### 実験

- Q006iとQ006oをartifact入力なしでsealed runnerから再実行
- grid、\(\omega\)、\(\eta\)、seed、amplitude、horizon、chart種別を照合
- linear／quadratic各32方向、合計64方向を成分ごとに完全照合
- Q006iの8 gateをoriginal columnへdeep-copy
- policy columnではglobal conservationだけをQ006o standard budgetへ置換

### 結果

全validity／dual decision gateを通過し、
`dual reporting supports unmodified-map chart continuation`としてacceptedとした。

- direction alignment record / maximum error: `64 / 0`
- Q006i original maximum drift: `2.728496323152741e-12`
- Q006o `math.fsum` maximum drift: `2.7285041507210106e-12`
- cross-measurement difference: `7.82756826945652e-18`
- original failed gate count / names: `1 / [global_conservation]`
- policy failed gate count: `0`
- Q006o standard / uniform policy: `passed / failed`
- budget violation / maximum utilization: `0 / 0.5`
- maximum final component budget: `1.1368683772161603e-11`

### 分析

Q006iのoriginal global-conservation threshold `1e-12`、failed判定、study outcome `rejected`はそのまま
保存された。policy columnではその1 gateだけを有限trajectory用ULP budgetへ置き換え、他7 gateは値・
threshold・判定がoriginalと一致する。従って過去の失敗を遡及的に消さず、unmodified mapを用いた次の
検証へ条件付きで進める。

ただしQ006pはQ006oと同じseed `20260810`、amplitude `0.01`、100 step、64 trajectoryを使うintegration
auditであり、独立な一般化証拠ではない。all-state conservationやSSM existenceも主張しない。

### 改善

- Q006oのbudget式、係数2、component scale、測定法を凍結する。
- seed `20260811`・amplitude `0.005`・200 stepで長時間holdoutを行う。
- seed `20260812`・amplitude `0.02`・50 stepで大振幅holdoutを行う。
- 128 trajectory、16,000 step、48,000 component checkを全列挙する。
- holdout失敗後にbudgetをretuneせず、最初のviolation witnessを保存する。

### 次の問い

Q006q: Q006oのforward-error budgetは、別seed・amplitude・horizonの独立holdoutを係数変更なしで通るか。

## Cycle Q006q: independent forward-error holdout

### 問い

Q006oで固定したcomponentwise ULP budgetは、Q006pまでに使っていないseed・amplitude・horizonでも、
unmodified standard mapの保存driftを係数変更なしで覆えるか。

### 仮説

seed `20260811`・amplitude `0.005`・200 stepのlong-horizon scenarioと、seed `20260812`・
amplitude `0.02`・50 stepのlarge-amplitude scenarioは、ともに
\(B_c(t)=2t\operatorname{spacing}(S_c(f_0))\) 内に収まる。

### 実験

- linear／quadratic各32方向を各scenarioで共有し、合計128 trajectory
- 16,000 trajectory-step × 3 component = 48,000 budget check
- Q006o seed `20260810`と2 holdout seedのexact duplicateを監査
- collision → streaming → filterと`full_map`を各stepで照合
- `math.fsum`とNeumaier、positivity、全step record、strict JSONを保存
- budget係数2、final ceiling `2.4e-11`を結果を見る前に固定

### 結果

全validity／scenario／aggregate policy gateを通過し、
`independent holdout supports registered forward-error policy`としてacceptedとした。

- trajectory / step / component check: `128 / 16000 / 48000`
- budget violation: `0`
- aggregate maximum utilization: `0.5`
- maximum final component budget: `2.2737367544323206e-11`
- long-horizon maximum absolute drift: `5.4569682106375694e-12`
- large-amplitude maximum absolute drift: `1.3642420526593924e-12`
- minimum population: `0.027322438516769965`
- stage-map identity / streaming / independent-sum error: `0 / 0 / 0`
- direction duplicate: `0`

### 分析

worst utilizationはlong-horizon・linear direction 0・step 1のmassで、drift
`5.6843418860808015e-14`、budget `1.1368683772161603e-13`、utilization `0.5`だった。200 step側の
最大final budgetも登録上限を通過し、50 stepの大振幅側でも違反はなかった。Q006oと同じ式を別軌道へ
適用して通ったため、登録有限trajectoryに限るoperational policyの独立holdoutは完了した。

ただしこれはall-state／all-horizon roundoff theoremではない。amplitude `0.02`は算術stress testにだけ
使っており、その振幅でのchart invarianceやshadowingを支持しない。

### 改善

- cubic coefficientを作る前に全order-three homological operatorを列挙する。
- 24 complex modeの2,600 unordered tripleをzero/internal/external sectorに分ける。
- Q006iの300 pair assemblyを独立に再現してoperator実装を検証する。
- numerical singularity、condition、共役、C4 output-count closureを先に判定する。

### 次の問い

Q007a: Q006iの24座標clusterは、登録grid上で全2,600 order-three homological blockが一意に解ける
非共鳴familyか。

## Cycle Q007a: cubic homological-family prequalification

### 問い

Q006iの24座標clusterに対する全order-three homological blockは、登録grid上で一意に解ける
非共鳴operator familyか。

### 仮説

24 complex modeの全2,600 unordered tripleでnumerically singular blockは0となり、全conditionは
登録ceiling `1e9` 以下に収まる。

### 実験

- artifactを入力せず8 wave × 3 modeを再構築
- 同じassemblyでorder-2の300 pairを再列挙しQ006iをcontrol再現
- order-3の2,600 tripleをzero-wave kinetic／internal selected／externalへ分類
- 全singular values、rank threshold、condition、near-resonance、multiplicityを保存
- triple共役operatorのmultiplier／singular valuesとC4／共役output-wave count closureを監査

### 結果

全validity／hypothesis gateを通過し、
`order-three homological family prequalified on registered grid`としてacceptedとした。

- order-2 pair / sector count: `300 / 36 / 108 / 156`
- order-2 minimum singular / maximum condition:
  `0.00015502435597333105 / 14513.930547954875`
- order-3 triple / sector count: `2600 / 108 / 1044 / 1448`
- order-3 singular / near-resonant block: `0 / 24`
- order-3 minimum singular / maximum condition:
  `0.00020787972673242753 / 10821.814847751179`
- minimum rank margin: `4.6239929774875706e8`
- conjugate multiplier / singular-value relative error:
  `2.9151992739486325e-16 / 2.8470292165304574e-15`
- output wave count / rotation / conjugacy failure: `49 / 0 / 0`

### 分析

order-2 controlはQ006iのsector count、minimum singular value、maximum conditionを数値誤差0で再現した。
order-3のworst blockは`t00238`、input `m000,m013,m017`、external wave `(1,2)`で、conditionは
`10821.8148`だった。これはceilingより約5桁小さく、numerical rank thresholdに対するminimum marginも
`4.62e8`ある。従って登録grid上で3次係数の一意solveを妨げるspectral obstructionは見つからなかった。

ただしforcingを計算しておらず、係数の正しさや残差4次化は未検証である。near-resonant diagnostic 24件も
存在するため、Q007bでは全forcing・solve residual・係数normを保存し、実際の改善で判定する。

### 改善

- rest equilibriumの解析的3次微分を独立5点有限差分で照合する。
- 2次係数と3次map derivativeから全2,600 forcingを構成する。
- complex Fourier-fiber表現でcubic chartを評価し、dense \(2601\times24^3\) tensorを避ける。
- held-out seedで残差次数`3 → 4`と100-step shadowingを比較する。
- fixed-leaf、共役、C4、Q006o arithmetic budgetを別gateで監査する。

### 次の問い

Q007b: 全cubic forcingと係数は独立微分・homological equationを通り、held-out残差次数と100-step
shadowingをquadratic chartから改善するか。

## Cycle Q007b: cubic coefficient and residual continuation

### 問い

全2,600 cubic forcingとcubic chart／reduced mapを構築し、独立3次微分、係数方程式、held-out残差次数、
100-step shadowingを全て通過できるか。

### 仮説

- quadratic residual slopeは全方向で`3 ± 0.1`
- cubic residual slopeは全方向で`4 ± 0.15`
- amplitude `0.01`のcubic/quadratic residual ratioは全32方向で`0.10`以下
- 3種類の100-step shadow ratioは全32方向で`0.8`以下
- cubic trajectoryの9,600 component checkでQ006o budget違反は0

### 実験

- Q007aと同じ2,600 unordered tripleについて解析的3次forcingを構成
- symmetric complex Fourier-fiberで \(T\) と \(K\) を解き、full physical dense tensorは作らない
- seed `20260814`の16方向で解析的 \(D^3\Phi\) を5点中心差分と独立照合
- 全solve、homological equation、fixed-leaf conservation、graph gauge、係数共役を監査
- seed `20260817`の16方向でchart／reduced mapのC4 equivarianceを監査
- seed `20260815`の32方向・5 amplitudeで残差次数とratioを監査
- seed `20260816`の32方向でquadratic／cubicを自己整合的に100 step rollout

### 結果

全7 validity gateは通過したが、4 hypothesis gateのうちheld-out residual-ratio gateだけが失敗した。
事前登録どおり`cubic continuation does not improve the registered chart`として`rejected`と固定した。

- independent derivative minimum norm / maximum best relative error:
  `0.04310510283888515 / 3.3657127711273197e-6`
- triple / sector / singular count: `2600 / 108 / 1044 / 1448 / 0`
- maximum condition / reproduction relative error: `10821.814847751179 / 0`
- maximum solve / homological residual:
  `7.507193302943194e-13 / 7.507420157100771e-13`
- maximum graph-gauge / zero-wave forcing / zero-wave coefficient residual:
  `9.544008185850808e-15 / 1.1964700984616753e-14 / 5.592366378684957e-16`
- coefficient conjugacy / C4 chart / C4 reduced error:
  `1.9424559059939878e-13 / 2.037693065234071e-14 / 1.1934586964246845e-15`
- quadratic slope range: `2.999458101008406 – 3.00050163830818`
- cubic slope range: `3.999307108046794 – 4.000367209086971`
- amplitude `0.01` residual-ratio maximum / failure count:
  `0.2286914274494018 / 9 of 32`
- shadow maximum-absolute / final-absolute / maximum-relative ratio:
  `0.15091634126760786 / 0.10970020315090677 / 0.13108685317368804`
- cubic budget component checks / violation / maximum utilization / final budget:
  `9600 / 0 / 0.5 / 1.1368683772161603e-11`

### 分析

係数構築の妥当性、残差次数`3 → 4`、100-step shadowing改善は独立に支持された。棄却理由は
「3次化が改善しない」こと一般ではなく、登録振幅`0.01`で全方向の残差を10分の1以下にするという
有限振幅の効果量gateである。最大ratioはamplitude
`0.00125 / 0.0025 / 0.005 / 0.0075 / 0.01`に対して
`0.028587 / 0.057175 / 0.114348 / 0.171520 / 0.228691`となり、4次／3次のtruncation ratioに
整合するほぼ一次の振幅依存を示した。

一方、この半径依存はQ007bの同じ32方向から得たpost-hoc観測なので、そのまま小さい半径でacceptedへ
読み替えない。半径`0.004`は最大ratioの線形calibration cutoff約`0.00437`より保守的に固定し、別seedの
holdoutで検証する。また大きなcubic coefficientがchart foldを作っていないかを解析Jacobianで別に監査する。
Q006iの旧`rejected`判定とQ007bのamplitude `0.01`棄却は変更しない。

### 改善

- calibration方向とradius holdout方向を分離する。
- \(DW_3(a)=V+H[a,\cdot]+T[a,a,\cdot]/2\) を実装し、有限差分で独立検証する。
- 半径`0.01`までのradial lineでminimum singular valueを測り、chart fold候補を監査する。
- Q007aの24 near-resonant tripleがcubic correctionへ占める割合を記録する。
- quartic coefficientはQ007b1の診断前に構築しない。

### 次の問い

Q007b1: 独立方向で半径`0.004`の10倍残差改善を再現でき、元の半径`0.01`でchart immersionは
保たれているか。

## Cycle Q007b1: independent cubic-radius and immersion audit

### 問い

Q007bと独立な方向で、cubic chartは半径`0.004`まで全方向10倍の残差改善を示し、元の失敗半径
`0.01`までradial immersionを保つか。

### 仮説

- seed `20260818`の64方向で半径`0.004`のcubic/quadratic residual ratioは全て`0.10`以下
- quadratic／cubic／ratio slopeはそれぞれ`3 ± 0.1 / 4 ± 0.15 / 1 ± 0.1`
- seed `20260820`のanalytic chart Jacobianは独立中心差分と`1e-7`以下で一致
- 半径`0.01`まで正規化minimum singular valueは`0.8`以上
- seed `20260819`の32方向で3種類の100-step shadow ratioは`0.8`以下、budget違反0

### 実験

- Q007bの5 coefficient hashを固定し、係数を再fit・truncateしない
- Q006i／Q007bの全登録方向とのexact duplicateを監査
- 7 amplitudeで残差比を測り、最初の4点で残差次数、全7点でratio次数をfit
- $DW_3(a)d=Vd+H[a,d]+T[a,a,d]/2$をFourier-fiberから解析評価
- 64 radial direction × 5 nonzero amplitudeとbaseでfull $2601\times24$ JacobianをSVD
- condition `>=1e4`の24 near-resonant tripleを部分評価し、残差比との相関を診断
- 独立32方向を半径`0.004`から100 step rollout

### 結果

全5 validity gateと全6 hypothesis gateを通過し、
`registered cubic improvement radius localized without fold signature`として`accepted`とした。

- quadratic slope range: `2.9997535988860777 – 3.0003725714946294`
- cubic slope range: `3.999374269224645 – 4.00027779049691`
- ratio slope range: `0.9994377578283731 – 1.000310528367947`
- radius `0.004` maximum ratio / failure count:
  `0.07800626791012572 / 0 of 64`
- amplitude ladder maximum ratios:
  `0.024376 / 0.039004 / 0.058505 / 0.078006 / 0.117007 / 0.156005 / 0.195002`
- corresponding `0.10` failure counts: `0 / 0 / 0 / 0 / 2 / 12 / 16`
- analytic Jacobian minimum action norm / maximum best relative error:
  `0.921079697651058 / 1.463877022273861e-10`
- minimum normalized singular value / maximum condition:
  `1.0 / 1.7676346838545076`
- shadow maximum-absolute / final-absolute / maximum-relative ratio:
  `0.044022136608928585 / 0.030088934796968496 / 0.03621745864325118`
- budget component check / violation / maximum utilization / final budget:
  `9600 / 0 / 0.5 / 1.1368683772161603e-11`

### 分析

独立sampleでも残差比はほぼ厳密に振幅一次で増え、半径`0.004`では10倍改善を保ったが、半径`0.01`では
64方向中16方向が同じeffect-size gateを落とした。従ってQ007bの棄却を再現しつつ、より小さい有限sample
radiusを局在化できた。Jacobianの最悪値は非線形点ではなくbaseの`1.0`であり、登録radial lineにfoldへ
近づくsignatureはなかった。

near-resonant chart fractionと残差比のSpearman相関は`-0.5789377`、上位quartile enrichmentは`0.4723544`
だった。24 tripleは全てreduced coefficientが0のsectorにあり、reduced near fractionは全方向0なので相関を
未定義と記録した。一方、全cubic／quadratic chart correction ratioと残差比の相関は`0.9607601`だった。
従ってnear-resonant subsetの集中より、全cubic curvatureと有限次数truncationが主要なindicatorである。

このacceptedは64 residual／immersion方向と32 shadow方向だけに限る。半径`0.004` ball全体、global
injectivity、Q007bの半径`0.01`再判定、真の不変多様体を主張しない。

### 改善

- quartic forcingを作る前に全order-4 operatorを列挙する。
- order-2／order-3結果をcontrolとして同一runner内で再現する。
- order-4の共役operator、C4／共役output count、conditionを先に固定する。
- order-4 operatorが通過した場合だけforcingとquartic residual gateを事前登録する。

### 次の問い

Q007c: Q006iの24座標clusterは、登録grid上で全17,550 order-4 homological blockが一意に解ける
非共鳴familyか。

## Cycle Q007c: quartic homological-family prequalification

### 問い

Q006iの24 complex modeに対する全order-4 homological blockは、登録grid上で一意に解ける
非共鳴operator familyか。

### 仮説

- 全17,550 unordered 4-tupleのnumerically singular blockは0
- zero-wave kinetic／internal selected／externalを含む全blockのcondition numberは`1e9`以下
- order-2／order-3 control、tuple completeness、共役、C4、strict serializationが全て通る

### 実験

- grid \(17^2\)、\(\omega=1.5\)、\(\eta=0.01\)、Q006iと同じ24 complex modeを再構築
- pair 300件、triple 2,600件を同じrunner内で再計算し、Q007aのsector countとspectral extremaを照合
- `i <= j <= k <= l`の全17,550 tupleを列挙し、zero／internal／external operatorをSVD
- permutation multiplicity、conjugate tuple、output wave、output kind、C4／conjugate wave countを監査
- forcingや係数は構築せず、全operator singular valuesとconditionをartifactへ保存

### 結果

全6 validity gateと全2 hypothesis gateを通過し、
`order-four homological family prequalified on registered grid`として`accepted`とした。

- pair control sector count / singular: `36 / 108 / 156 / 0`
- pair minimum singular / maximum condition:
  `0.00015502435597333105 / 14513.930547954875`
- triple control sector count / singular / near-resonant:
  `108 / 1044 / 1448 / 0 / 24`
- triple minimum singular / maximum condition:
  `0.00020787972673242753 / 10821.814847751179`
- quartic record / unique / duplicate count: `17550 / 17550 / 0`
- quartic sector count: `846 / 4536 / 12168`
- quartic singular / near-resonant block count: `0 / 8`
- quartic minimum singular / maximum condition:
  `6.485706497181907e-05 / 34673.915552593266`
- minimum rank margin: `144315965.0768939`
- worst block: `q17061`、`m015,m015,m015,m021`、output `(-2,2)`、external
- multiplicity sum / values: `331776 / 1, 4, 6, 12, 24`
- maximum fixed-leaf invariance residual: `1.227779058661652e-16`
- conjugate missing／wave／kind failure: `0 / 0 / 0`
- maximum conjugate multiplier / singular-value relative error:
  `3.571246854667297e-16 / 3.019068596546352e-15`
- output wave count / rotation／conjugacy failure: `81 / 0 / 0`

### 分析

最悪conditionはQ007aの3次familyより約3.2倍大きいが、登録ceiling `1e9`より4桁以上小さく、rank
thresholdに対する最小marginも`1.44e8`ある。従ってこの有限grid上ではorder-4 operator自体に数値的・
代数的な障害は見つからない。near-resonant blockは8件だけだが、これはforcingの大きさや係数応答を
まだ評価していないため、性能上無害とは結論しない。

このacceptedはoperator-only prequalificationである。quartic forcing／coefficient、残差次数`4 → 5`、
半径`0.01`の回復、shadowing、grid-uniform family、真の不変多様体の存在・一意性・normal attractionを
主張しない。

### 改善

- 写像の解析的4階微分を、線形tangent方向の独立5点差分で照合する。
- Faà di Brunoで組み立てた全quartic forcingを、cubic invariance defectの独立4階差分でも照合する。
- solve residualとforcing validationを分離し、全係数のgraph gauge／fixed leaf／共役／C4を監査する。
- 半径`0.01`ではresidualと100-step shadowingをcubic chartに対して比較する。

### 次の問い

Q007c1: 全quartic forcing／coefficientは独立検証を通り、残差次数を`4 → 5`へ改善して、Q007bで
失敗した半径`0.01`の有限sample性能を回復できるか。

## Cycle Q007c1: quartic coefficient and sampled-radius continuation

### 問い

Q007cを通過したsymmetric Fourier-fiberの4次forcing／coefficientは独立検証を通り、残差次数を
`4 → 5`へ改善して、半径`0.01`の1-step残差と100-step shadowingをともに回復できるか。

### 仮説

- 解析的4階微分と独立5点差分のmaximum best relative errorは`5e-3`以下
- 全quartic forcingとcubic defectの4階差分は`2e-2`以下で一致
- 全17,550係数のsolve／homological／gauge／保存／共役／C4 gateが`1e-10`以下
- cubic／quartic residual slopeは`4 ± 0.15 / 5 ± 0.30`
- 半径`0.01`でquartic/cubic残差比`<=0.8`、quartic/quadratic残差比`<=0.10`
- 100-stepの3 shadow比は全32方向`<=0.8`、forward-error budget違反0

### 実験

- Q007bのcubic係数hashとQ007cの全operator統計をartifact入力なしで再現
- Faà di Brunoの4／3／6 labelled partitionから全17,550 forcingを構築
- seed `20260821 / 20260822`で写像4階微分と全forcingを別々に有限差分検証
- 全quartic coefficientをsolveし、zero／internal／external、fixed leaf、共役、C4を監査
- seed `20260823`の32方向、5 amplitudeでquadratic／cubic／quartic残差を比較
- seed `20260825`の32方向、amplitude `0.01`から100-step shadow rolloutを比較

### 結果

全8 validity gateは通過した。4 hypothesis gateのうち残差次数、残差比、forward-error budgetの3件は
通過したが、shadowing比が失敗したため、`quartic continuation does not restore registered radius`として
有効な`rejected`とした。

- map fourth-derivative maximum best relative error: `3.096316945580041e-05`
- assembled-forcing maximum best relative error: `0.0003957993866089215`
- minimum analytic derivative / forcing norm:
  `0.012125858957928786 / 1.5109132913737002`
- maximum solve / homological residual:
  `1.0006036636030973e-12 / 9.530583825936524e-13`
- maximum graph gauge / conjugacy residual:
  `1.010360766298989e-14 / 1.6766439496313294e-13`
- maximum C4 field error / global conservation residual:
  `4.651395234795445e-12 / 3.778236108733814e-15`
- cubic slope range: `3.9997142511488586 – 4.000288731411633`
- quartic slope range: `4.999739294776105 – 5.000472391642802`
- maximum quartic/cubic residual ratio / failure count:
  `0.4391470445743498 / 0 of 32`
- maximum quartic/quadratic residual ratio / failure count:
  `0.09270518013931812 / 0 of 32`
- maximum absolute / final absolute / maximum relative shadow ratio:
  `0.7464493651463932 / 1.3715310087581642 / 0.8914189366016195`
- corresponding shadow failure counts: `0 / 1 / 1 of 32`
- budget component check / violation / maximum utilization / final budget:
  `9600 / 0 / 0.5 / 1.1368683772161603e-11`

### 分析

係数構築の妥当性と5次残差は強く支持され、半径`0.01`の1-step effect sizeも全方向で通過した。
従って棄却原因はquartic forcingの符号やhomological solveではなく、登録100-step性能に限定される。

失敗は方向14に集中した。この方向でもmaximum absolute errorは
`2.908886069449626e-08 → 2.1713361598238602e-08`へ改善したが、instantaneous absolute／relative比は
step 15から`0.8`を超え、step 100のabsolute errorは
`5.219526416836927e-09 → 7.158742331724237e-09`となった。誤差はmachine floorではなく、遅い時間での
位相・累積誤差のcrossoverとして扱う。これは同じ方向から得たpost-hoc診断なので、次のacceptance dataへ
再利用しない。

Q007c1の棄却、Q007bの半径`0.01`棄却、Q007b1の半径`0.004` acceptanceは変更しない。有限32方向、
有限grid、100 stepを超える主張も行わない。

### 改善

- quartic coefficientを変更せず、全5 hashを固定する。
- Q007c1方向14はrunner reproduction controlとcalibrationだけに使う。
- 別seedの64方向でamplitude `0.004 / 0.007 / 0.01`を100 stepまで同時に評価する。
- 同じrolloutのprefixからhorizon `10 / 25 / 50 / 100`を事前登録し、post-hoc horizon選択を避ける。
- 短時間・大振幅と長時間・小振幅を別gateにして、有効領域を局在化する。

### 次の問い

Q007c2: 独立方向で、quartic chartは半径`0.01`・10 step、および半径`0.004`・100 stepの
shadowing改善をともに再現し、振幅・horizon依存の有効領域を局在化できるか。

## Cycle Q007c2: quartic shadow amplitude-horizon localization

### 問い

Q007c1の係数を変更せず、独立方向で半径`0.01`・10 stepの短時間改善と、半径`0.004`・100 stepの
長時間改善をともに再現し、有限sampleの有効shadow領域を局在化できるか。

### 仮説

- Q007c1の全5 coefficient hashと方向14 controlを再現する。
- seed `20260826`の64方向はunit normで、全既登録方向とのexact duplicateが0である。
- 半径`0.01`・10 stepと半径`0.004`・100 stepの3 shadow比は全方向`<=0.8`である。
- quartic側57,600 component-stepでforward-error budget違反0、maximum utilization `<=1`、
  final budget `<=1.2e-11`である。

### 実験

- amplitude `0.004 / 0.007 / 0.01`ごとにcubic／quartic各64本を100 stepまで一度だけ進めた。
- 同じtrajectoryからhorizon `10 / 25 / 50 / 100`のprefix maximum absolute、final absolute、
  prefix maximum perturbation-relative errorを計算した。
- Q007c1方向14はupstream reproduction controlだけに使い、新campaignのacceptance dataから除外した。
- 全state、coordinate、error、ratio、population、strict JSON serializationをvalidityとして監査した。

### 結果

全4 validity gateと全3 hypothesis gateが通過し、
`quartic shadowing domain localized on independent directions`として`accepted`とした。

- coefficient hash match / Q007c1 control maximum relative error: `true / 0`
- direction maximum norm error / exact duplicate count: `2.220446049250313e-16 / 0`
- trajectory / chart-step count: `384 / 38400`
- budget component check / violation / maximum utilization / maximum final budget:
  `57600 / 0 / 0.5 / 1.1368683772161603e-11`
- minimum population: `0.02751468992141129`

登録した2 operating pointのmaximum directional ratioは次の通りである。

| amplitude | horizon | maximum absolute | final absolute | maximum relative |
|---:|---:|---:|---:|---:|
| 0.01 | 10 | 0.46692017829349514 | 0.48393482249773484 | 0.4610632459952544 |
| 0.004 | 100 | 0.22081209266153715 | 0.339679128695444 | 0.2703146187976154 |

診断用のamplitude `0.007`・100 stepも
`0.38643325358644326 / 0.5949214762401986 / 0.4730500614608752`で全方向通過した。一方、
amplitude `0.01`・100 stepは
`0.5520626734869788 / 0.8505821724417485 / 0.675783734038649`で、final absolute比だけが2方向で
`0.8`を超えた。

### 分析

短時間・大振幅と長時間・小振幅という事前登録した2点では、四次chartの改善を独立64方向で再現した。
同時に、長時間・大振幅では改善が一様でない境界も再現された。従ってQ007c1の半径`0.01`・100 step
棄却は変更せず、Q007c2のacceptedは2 operating pointの有限sample局在化だけを意味する。

ball全体、他horizon、global injectivity、grid-uniform family、真の不変多様体、TT圧縮優位性は
主張しない。

### 改善

- Q007c1のvalidated coefficient hashを以後の表現比較でも固定する。
- 物理空間のfull dense quartic tensorはmaterializeせず、local Fourier coefficient tensorだけを
  dense oracleに使う。
- 自然なunordered sparse-fiberを必須baselineとし、TT core stored scalars、index metadata、
  serialized bytes、rank、rounding時間、評価時間、忠実度を分離する。
- TT gaugeを除いた次元をcore stored scalar countと混同しない。

### 次の問い

Q008a: 固定したdegree `2 / 3 / 4` Fourier chart係数に対し、事前登録した4つのTT出力軸配置のいずれかが、
忠実度を保ったまま四次natural sparse-fiberよりstored real scalarsとserialized bytesの両方で小さくなるか。

## Cycle Q008a: local Fourier coefficient TT storage prequalification

### 問い

固定したdegree `2 / 3 / 4` local complex Fourier chart係数に対し、flat D2Q9出力またはD1Q3出力分解を
先頭／末尾に置く4つのTTのいずれかが、忠実度を保ったまま四次natural sparse-fiberより
stored real scalarsとserialized bytesの両方で小さくなるか。

### 仮説

- 全入力hash、fiber count `300 / 2600 / 17550`を再現する。
- ordered dense actionはunordered sparse actionとmaximum relative error `<=5e-14`で一致する。
- 12 TTのtensor reconstruction errorは`<=2e-13`、action errorは`<=1e-11`である。
- degree 4で少なくとも1候補が`<315900` core stored real scalarsかつnatural sparseより小さい
  uncompressed NPZ bytesを持つ。

### 実験

- complex128 TT-SVD、relative discarded-Frobenius budget `1e-13`、rank capなしを使った。
- `flat-q-first / flat-q-last / d1q3-q-first / d1q3-q-last`をdegree `2 / 3 / 4`で比較した。
- D1Q3候補は、同じbudgetで検証したlexicographic flat TTの出力coreだけをfull-rank SVDで3×3へ分け、
  巨大tensor全体を重複分解する丸め誤差を避けた。
- natural sparseは`uint8` unordered index／multiplicityと`complex128` 9-vectorを保持し、TTとともに
  uncompressed NPZ roundtripをbitwise検証した。
- seed `20260827`の64方向で作用誤差、seed `20260828`の128方向で2 warm-up／7 blockのtimingを測った。

### 結果

全4 validity gateは通過したが、唯一のstorage hypothesis gateは4候補すべて失敗した。従って
`registered TT tensorizations do not beat natural quartic sparse-fiber storage`として有効な`rejected`とした。

- maximum dense-vs-sparse action error: `2.4453226833464242e-14`
- maximum TT reconstruction error: `1.0601074033942119e-13`
- maximum TT action error: `2.0799628811140123e-13`
- degree-4 natural sparse stored real scalars / NPZ bytes:
  `315900 / 2615734`
- degree-4 flat-q-first／last stored real scalars / NPZ bytes:
  `3550626 / 28406852`
- degree-4 D1Q3-first／last stored real scalars / NPZ bytes:
  `3550644 / 28407260`
- minimum TT/sparse real-scalar / byte ratio:
  `11.2397150997151 / 10.859992644512019`
- degree-4 flat-q-last ranks: `[1, 24, 300, 216, 9, 1]`
- median local-action timing sparse / flat-q-last:
  `603107.8125 / 2783184.375 ns per sample`

### 分析

係数再構成と作用は全候補で十分正確なので、棄却はTT実装の忠実度失敗ではない。degree 2でもTTは
sparseの約2.16倍、degree 3で約7.34倍、degree 4で約11.24倍のstored real scalarsを使い、degreeとともに
相対格納量が悪化した。D1Q3出力分解はcoreを2個増やすだけで、rankや格納量を改善しなかった。

timingは診断に限るが、最速TTもsparse-fiberの約4.61倍だった。従ってこの4 tensorizationに対する
Q008b full-chart／rolloutとQ009 TT-crossは開始しない。これはTT一般の否定ではなく、固定したflat入力modeと
flat／D1Q3出力配置の否定である。

### 改善

- Q008aで未検証の入力mode構造`24=8 wave×3 branch`を次の候補へ明示的に使う。
- wave index 8を3 bitへ分け、tuple-majorとscale-interleaved QTTを区別する。
- Q008aで格納量が同一かつ評価が速かったflat-q-lastだけをupstream reproduction controlに残す。
- 同じnatural sparse baselineと二重storage gateを維持し、結果を見て候補を追加しない。

### 次の問い

Q008c: wave／branch factorizationまたは3-bit wave QTTは、固定四次係数の忠実度を保ったまま、
natural sparse-fiberよりstored real scalarsとserialized bytesの両方で小さくなるか。

## Cycle Q008c: wave-branch / wave-QTT storage prequalification

### 問い

Q008aで未検証だった入力modeの`24=8 wave×3 branch`構造とwave indexの3-bit分解を明示すれば、
固定degree `2 / 3 / 4`係数を忠実に保ちながら、四次natural sparse-fiberよりstored real scalarsと
serialized bytesの両方で小さいTTが得られるか。

### 仮説

- Q008aの6入力hash、fiber count、flat-q-last ranks／格納量を完全一致で再現する。
- 4 tensorizationのmapping action errorは`<=5e-14`である。
- 12 TTのtensor reconstruction errorは`<=2e-13`、sparse action errorは`<=1e-11`である。
- degree 4で少なくとも1候補が`<315900` core stored real scalarsかつ`<2615734` NPZ bytesを持つ。

### 実験

- `wave-branch-tuple-major / wave-branch-factor-major / wave-qtt-tuple-major /
  wave-qtt-scale-interleaved`をdegree `2 / 3 / 4`で直接TT-SVDした。
- mode indexは`i=3w+b`、wave bitは`w=4s2+2s1+s0`、C-orderと固定した。
- 分割された入力軸へ任意の24次元方向を正しく作用させるため、同じ元座標に属する物理軸を一つの
  feature tensorで結ぶ一般tensor-network contractionを用いた。
- seed `20260829`の独立64方向でmapping／作用誤差、seed `20260830`の128方向で2 warm-up／7 blockの
  診断timingを測った。

### 結果

全5 validity gateは通過したが、degree-4 storage gateを通る候補は0だった。従って
`registered wave-factorized TTs do not beat natural quartic sparse-fiber storage`として
有効な`rejected`とした。

- maximum canonical dense-vs-sparse action error: `1.8460488990463964e-14`
- maximum candidate mapping action error: `1.3427825001646324e-15`
- maximum TT reconstruction error: `1.4915465734115449e-13`
- maximum TT action error: `6.624328755394939e-13`
- degree-4 natural sparse stored real scalars / NPZ bytes: `315900 / 2615734`
- degree-4 wave-branch-tuple-major stored real scalars / NPZ bytes:
  `4465748 / 35728884`
- minimum TT/sparse scalar / byte ratio:
  `14.136587527698639 / 13.659219171368342`
- degree-4 wave-QTT-tuple-major stored real scalars / NPZ bytes:
  `8121540 / 64977332`
- degree-4 wave-branch-tuple-major ranks:
  `[1,8,24,192,300,648,216,27,9,1]`
- diagnostic sparse / fastest registered-candidate median action time:
  `573325.78125 / 22348794.53125 ns per sample`

### 分析

mapping、再構成、作用、serializationは全候補で通過したため、棄却は実装忠実度の失敗ではない。
最小のwave-branch TTでも自然なsparse-fiberの約14.14倍で、Q008a flat-q-lastの約11.24倍より悪化した。
最小wave-QTTは約25.71倍、scale-interleaved QTTは約43.67倍であり、bit分解もrank低減へつながらなかった。

timingは診断だけだが、最速登録候補もsparse-fiberの約38.98倍だった。従って固定Q007c1係数に対する
TT-SVD圧縮経路を閉じ、Q009 TT-crossを開始しない。これは登録4配置の有限問題に対する結論であり、
TT一般や別の基底・別の物理問題を否定するものではない。

### 改善

- 圧縮候補のpost-hoc追加を止め、自然なFourier sparse-fiberをこの係数族の採用表現とする。
- Q006hの線形spectral gapとQ007c2の有限shadow領域の間に残る、非線形normal-attraction診断へ戻る。
- full-map Jacobian、quartic chart tangent、fixed-leaf projector、normal cocycle adjointを独立に検証する。
- 有限sampleのEuclidean projector結果と、存在・一意性のa posteriori theoremを混同しない。

### 次の問い

Q007d: Q007c2で局在化した半径`0.004 / 0.01`の10-step領域で、quartic candidate chartに沿う
projected normal cocycleは、最弱tangent cocycleより一様に強く減衰するか。

## 2026-08-08: Q007d finite-radius projected tangent／normal cocycle

### 実装

- 任意の正密度stateでfiltered BGK mapの解析的matrix-free `Jv`とEuclidean adjoint `J^T u`を実装した。
- quartic Fourier-fiber chartの解析的physical-by-reduced Jacobianを実装した。
- global mass／momentum固定葉projector、thin-QR tangent basis、Euclidean normal projectorを構成した。
- 33 starting pointそれぞれで10-step tangent block積とprojected normal cocycleを構成し、2つの決定的
  startからmatrix-free SVDを実行した。one-step ratioも診断として保存した。

### validity

全7 validity gateが通過した。

- maximum best full-map derivative relative error: `6.0343862358835346e-11`
- maximum best quartic-chart derivative relative error: `1.2051245689498942e-10`
- maximum adjoint inner-product relative error: `3.67240461070866e-17`
- maximum fixed-leaf conservation derivative residual: `2.0292205916090742e-16`
- maximum projector-family residual: `1.8367094929943913e-15`
- minimum chart-tangent singular value / rank: `0.6963531816444375 / 24`
- maximum normal singular-triplet residual: `2.8463046225927812e-15`
- maximum two-start singular-value disagreement: `8.9606828648914722e-16`
- minimum population / minimum tangent-cocycle singular value:
  `0.02752853237565495 / 0.5733335035182436`
- maximum tangent leakage: `2.3392329166073374e-6`

### 結果

3つのhypothesis gateはすべて失敗した。

- equilibrium `gamma_1 / gamma_10`: `2.4223625220259515 / 2.592215401693412`
- amplitude `0.004`の`gamma_10`範囲: `2.59246193501529–2.5929140877584227`
- amplitude `0.01`の`gamma_10`範囲: `2.59285618762261–2.593947499641212`
- finite-radius failure count: `16 / 16`および`16 / 16`

従って`registered finite-sample projected normal-cocycle dominance not observed`として有効な
`rejected`とした。失敗は平衡点のone-stepから既に存在し、tangent leakageも登録上限の約`1/427`なので、
有限次chartの接空間近似だけでは説明できない。Q006hが扱った固有値modulusのspectral gapを、Euclidean
singular-value normal attractionへ読み替えることはできない。

### 主張境界と次の問い

棄却したのは固定grid・Euclidean orthogonal projectorの登録仮説だけであり、adapted norm、Riesz bundle、
真のinvariant normal bundle、grid-uniform attraction、多様体の存在・一意性は判定していない。Q007eでは
有限半径データを再利用せず、まず平衡点Fourier blockだけから固定するRiesz／Stein metricをprequalification
し、nonnormal Euclidean amplificationとspectral gapを切り分ける。

## 2026-08-08: Q007e equilibrium Riesz／Stein metric prequalification

### 実装

- \(17^2\)固定保存量葉を289個のFourier active blockへ分解し、8 signed low-wave blockの24 complex
  selected modeと2574 excluded modeをordered-Schur／Riesz invariant splitで分離した。
- global spectral gapから一つのrate \(r_*=\sqrt{\rho_N\mu_T}\) を固定し、selected inverse blockと
  excluded forward blockにHermitian正定値Stein metricを構成した。
- Cholesky whiteningを全Fourier blockへ実装し、実fixed-leaf stateの往復、共役wave、blockwise dense値と
  2598次元matrix-free two-start SVDを独立に監査した。
- Q007dのquartic coefficient hashとEuclidean平衡点ratioを同じ実装から再現し、上流結果を固定した。

### validity

全8 validity gateが通過した。

- selected minimum／excluded maximum modulus:
  `0.9837709569927492 / 0.9817098358325433`
- fixed rate／両margin:
  `0.9827398560586499 / 0.0010300202261065428 / 0.001031100934099305`
- maximum invariant-split residual: `4.478049432763522e-14`
- maximum Stein／Hermitian residual:
  `7.717980857245268e-14 / 1.0118933183687303e-14`
- minimum Stein eigenvalue: `1.0914517112309456`
- maximum registered condition number: `1383.4345053355412`
- maximum conjugacy／roundtrip／imaginary leakage residual:
  `2.2615002024861891e-13 / 4.1650348386053546e-16 / 6.534769174688447e-17`
- maximum blockwise SVD error／triplet residual／two-start disagreement:
  `4.0053646874458993e-16 / 1.2331152676133846e-15 / 6.675607812409829e-16`
- Q007d coefficient hash match／equilibrium ratio relative error: `true / 0`

### 結果

2つのhypothesis gateは両方通過した。

- one-step normal maximum／tangent minimum／gamma:
  `0.9820654543743582 / 0.9832397122496608 / 0.9988057257445229`
- 10-step normal maximum／tangent minimum／gamma:
  `0.831552014305928 / 0.8488403856607576 / 0.9796329537956986`

従って`equilibrium Riesz/Stein metric prequalified for finite-radius testing`として`accepted`とした。
Euclidean normの`gamma_1 / gamma_10 = 2.42236 / 2.59222`に対し、同じ平衡Jacobianのspectral splitを
使う固定adapted normでは両方が1未満となった。Q006hのmodulus gapとQ007dのEuclidean棄却は矛盾せず、
nonnormal transient amplificationを計量依存性として切り分けられた。

### 主張境界と次の問い

これは平衡点・単一gridのprequalificationだけである。有限半径normal attraction、真のinvariant normal
bundle、grid-uniform bound、多様体の存在・一意性は示していない。Q007dのEuclidean棄却も変更しない。
Q007fではmetric／whitening hashを固定し、Q007dと同じ33 starting pointへ再調整なしで適用する。

## 2026-08-08: Q007f fixed-metric finite-radius normal cocycle

### 実装

- Q007eの2598次元Fourier-Riesz whitening \(S\)、その逆、両方の複素Euclidean adjointを実装した。
- 任意の有限半径stateで共役Jacobian \(S J S^{-1}\) とそのmatrix-free adjointを構成した。
- \(S D W_4(a)\)のthin complex QRからvarying adapted tangentとmetric-orthogonal normal projectorを
  構成し、Q007dと同じ33 starting pointで10-step cocycleを評価した。
- seed `20260908`のcomplex two-start SVD、seed `20260909`の9点derivative／adjoint validationを
  独立に実装した。Stein metricは有限半径dataから再推定していない。

### validity

全7 validity gateが通過した。

- Q007d coefficient／direction／Euclidean equilibrium reproduction: pass、maximum relative error `0`
- Q007e全8 gate／metric hash／whitening hash reproduction: pass、maximum gamma relative error `0`
- transform roundtrip／imaginary leakage:
  `3.9730855178692216e-16 / 5.782992871388017e-17`
- maximum adapted-map derivative／adjoint relative error:
  `1.9411413072870177e-10 / 1.1552411204406219e-16`
- maximum projector-family residual: `1.864754803590191e-15`
- minimum adapted chart-tangent singular value／rank: `7.215951647785912 / 24`
- maximum equilibrium blockwise error／normal triplet residual／two-start disagreement:
  `2.6702431249639317e-15 / 8.851836222444479e-15 / 1.0678514354388054e-15`
- minimum population／minimum tangent-cocycle singular value:
  `0.02752853237565495 / 0.8485215443610019`
- maximum adapted tangent leakage: `1.5024964047170558e-7`

### 結果

3つのhypothesis gateはすべて通過した。

- equilibrium adapted `gamma_1 / gamma_10`:
  `0.9988057257445231 / 0.979632953795698`
- amplitude `0.004`の`gamma_10`範囲／failure count:
  `0.9798077420025896–0.980286028267377 / 0`
- amplitude `0.01`の`gamma_10`範囲／failure count:
  `0.9802276957977255–0.9815609124608508 / 0`
- 全33点のmaximum one-step `gamma_1`: `0.9991153531281403`

従って`registered finite-sample adapted-metric projected normal-cocycle dominance observed`として
`accepted`とした。Q007dと同じ方向・半径・horizonで、Euclidean ratioは全点失敗した一方、平衡点だけから
固定したadapted metricでは全点が通過した。これは計量比較としての有効な結果である。

### 主張境界と次の問い

方向を再利用した比較campaignなのでindependent holdoutではない。固定grid・2半径・32方向・10 step・
candidate quartic tangentに限り、ball全体、真のinvariant normal bundle、grid-uniform attraction、存在・
一意性は示していない。one-step全点通過も事前登録hypothesisではないため診断に留める。次のQ007gは
a posteriori theoremの対象空間・inverse・tail・roundoff majorantと十分条件を先に固定してから開始する。

## 2026-08-08: Q007g nonresonant-manifold theorem readiness

### 実装

- Cabré--Fontich--de la Llave Theorem 1.2／Remark 5を固定し、固定保存量葉の解析性・局所可逆性を
  collision、streaming、filterの構造から監査した。
- Q007eと同じ289 Fourier blockからselected 24、excluded 2574固有値を再構築した。
- theorem tailを満たす最小float64 spectral quotientを計算し、Q006i／Q007a／Q007cの次数2--4
  homological evidenceをsource hash・artifact hash付きで再照合した。
- direct theoremのfull-spectrum条件と、既存Fourier-selection-rule sector条件を別fieldへ分離した。
- Banach関数norm、inverse、domain、defect、variation、tail、roundoff、十分不等式をproof-object inventoryへ
  明示した。新しい方向sample、defect探索、metric retuningは行っていない。

### validity

全6 validity gateが通過した。

- selected spectral radius／excluded minimum modulus:
  `0.9920954673550985 / 0.49008513450158`
- spectral quotient \(L_*\): `89`
- degree-90 tail ratio／previous ratio:
  `0.9989422022329809 / 1.006901286320898`
- tail／previous boundary margin:
  `0.0010577977670190863 / 0.006901286320897926`
- sector-aware degree record／singular count:
  `300 / 2600 / 17550`, `0 / 0 / 0`
- required／sector-audited／direct-certified order count:
  `88 / 3 / 0`

### 結果

`current evidence is not theorem-ready`として有効な`not_ready`とした。構造的な解析性・局所可逆性と
float64再現は通ったが、次数2--4の既存SVDはmonomialのFourier和で決まるoutput sectorに限り、固定した
Theorem 1.2のfull-spectrum条件を直接認証しない。次数5--89はsector-awareにも未監査であり、全88次数が
interval／代数的には未認証である。定量的proof objectもgraph gauge以外は未構築だった。

これはcandidate manifoldの不存在を意味せず、Q007f、Q007d、Q008cの既存判定も変更しない。最初の
missing layerはoutward-rounded linear eigenvalue／split enclosureである。Q007hでは有理区間、Machin
formula、Taylor remainder、Neumann inverse bound、Bauer--Fike inclusionにより、線形splitとdegree-90
tailだけを認証する。

## 2026-08-08: Q007h rational-interval linear spectrum

### 実装

- D2Q9 collision symbolを有理数で構成し、Machin公式96項とTaylor多項式64項から17個のsin／cos区間を
  `Fraction`端点だけで生成した。
- 全288非零Fourier blockでNumPy固有分解をpreconditionerに限定し、floatをexact dyadic rationalへ変換した。
- \(\epsilon=\|I-WV\|_\infty\)、Neumann inverse bound、区間残差、Bauer--Fike半径を完全有理演算で評価した。
- 8 selected waveでは3／6円板群を分離し、homotopyでselected 24／excluded 2574のcountを固定した。
- zero waveの固定保存量葉は、6重の厳密固有値\(-1/2\)として処理した。

### validityと停止

8 validity gateのうち7個が通過した。

- maximum pi／trigonometric／symbol width:
  `1.0408e-136 / 9.4537e-136 / 6.24574e-136`
- maximum inverse defect \(\epsilon\): `1.10700e-14`
- maximum Bauer--Fike radius: `1.06752e-10`
- minimum selected／excluded disc-group gap: `1.34448`
- Q007g extrema reproduction maximum relative error: `1.56670e-15`
- conjugate endpoint difference: `0`
- maximum C4 endpoint difference: `2.32993e-11`

最後の値だけが事前登録閾値`1e-12`を超えた。最悪pairはexcluded群の
\((-5,4)\rightarrow(-4,-5)\)である。従って結果を見てthreshold、norm、Bauer--Fike半径式、selected clusterを
変更せず、`study_validity=failed`、`hypothesis_outcome=inconclusive`とした。

### 線形仮説の診断値

validity失敗のため認証結論には使わないが、登録した5 hypothesis gate自体はすべて通過した。

- selected spectral-radius upper: `0.9920954673554354`
- excluded minimum-modulus lower: `0.4900851345011790`
- selected minimum lower／excluded maximum upper:
  `0.9837709569923185 / 0.9817098358326815`
- normal-gap lower: `0.002061121159637118`
- degree-90 tail upper: `0.9989422022643313`
- certified disc count: `24 / 2574 / 2598`

これは線形splitの反証ではない。独立に正規化されたC4-related eigenvector matrixの条件数と残差が少し異なり、
真の対称スペクトルを包含する有効な円板半径が同一にならなかったためである。Q007h1ではC4 orbit代表だけで
preconditionerを作り、exact population permutationで全orbitへ輸送する。Q007hの全値と`inconclusive`は保存し、
次数2--89の非共鳴や非線形存在主張へは進まない。

## 2026-08-08: Q007h1 C4-transported rational spectrum

### 実装

- 289 waveをzero orbit 1個とnonzero C4 orbit 72個へexactに分割した。
- 有理0／1 population permutation \(P\) について、全289 edgeで
  \(A_{r(n)}=P A_nP^{-1}\) がrational rectangleとしてentrywise一致することを検証した。
- NumPy preconditionerを72代表でだけ構築し、\(V_j=P^jV\)、\(W_j=WP^{-j}\) を全288 memberへ輸送した。
- 各target blockでもQ007hと同じ区間残差、Neumann bound、Bauer--Fike半径を独立に再評価した。
- Q007h artifactの`failed / inconclusive`、C4 gateだけの失敗、5 hypothesis passをSHA付きで入力照合した。

### validity

全10 validity gateが通過した。

- orbit count／nonzero representative／member: `73 / 72 / 288`
- exact symbol C4 mismatch edge／entry: `0 / 0`
- maximum transported \(\epsilon\)／Bauer--Fike radius:
  `1.1070037300235058e-14 / 1.0675245062923042e-10`
- minimum selected／excluded disc-group gap: `1.3444770890709528`
- maximum Q007g extrema relative error: `1.454789362016216e-15`
- transported \(\epsilon\)／\(\beta\)／radius difference: exact `0`
- conjugate／C4 modulus endpoint difference: exact `0 / 0`

Q007hで最悪だった\((-5,4)\rightarrow(-4,-5)\)を含め、同じorbitの有効な円板包含が完全に一致した。
threshold、norm、radius式、Taylor項数、selected clusterはQ007hから変更していない。

### 結果と主張境界

5 hypothesis gateも全通過した。

- selected spectral-radius upper: `0.9920954673554099`
- excluded minimum-modulus lower: `0.4900851345011790`
- selected minimum lower／excluded maximum upper:
  `0.9837709569923394 / 0.9817098358326815`
- normal-gap lower: `0.002061121159657998`
- degree-90 tail upper: `0.9989422022620159`
- certified count: `24 / 2574 / 2598`

従って`registered symmetry-equivariant linear spectral split and degree-90 tail certified`として`accepted`とした。
Q007hの`inconclusive`は置換せず、独立preconditioner版の失敗として保存する。

これは固定17² filtered mapの線形層だけの認証である。次数2--89のdirect nonresonanceをまだ示していないため、
この時点ではTheorem 1.2から多様体存在を結論しない。Q007iはselected 6中心を4 modulus型へ包含し、96項の
有理atanh-log区間で全2,919,730 aggregateを外部disk unionから分離する。

## 2026-08-08: Q007i rational-log direct external nonresonance

### 実装

- Q007gとQ007h1 artifactをsource／scope／SHA付きで固定し、Q007h1の72 C4代表証明を全て再構築した。
- axis／diagonalのselected 6 diskをacoustic／shearの4 modulus型へ包含し、external spectrumをzero-wave
  kineticを含む643 representative diskへ包含した。
- \(z=(x-1)/(x+1)\) の96項atanh級数を110桁有理gridで逐次外向き丸めし、60桁有理log endpointを作った。
- 次数2--89の4型countを全列挙し、2,919,730 aggregate区間を253個のmerged external log区間へexact integer
  binary searchで照合した。acoustic pair内部まで展開した869,107,778 product countも組合せ恒等式で照合した。

### validityと結果

全7 validity gateと全4 hypothesis gateが通過した。

- representative proof digest mismatch: `0 / 72`
- selected representative／disk／modulus type: `2 / 6 / 4`
- external representative disk／merged interval: `643 / 253`
- minimum acoustic／shear classification margin: `0.20943761223015187`
- maximum rational-log tail bound: `1.5377133803221814e-92`
- aggregate／expanded product count: `2,919,730 / 869,107,778`
- overlap count: `0`
- minimum rational log-gap lower: `6.912230841407495e-10`
- witness: degree `51`、count `(1,19,27,4)`、external wave `(-2,-2)`

従って`registered direct external nonresonance through degree 89 certified`として`accepted`とした。complex phaseや
translation selection ruleへ弱めず、Cabré--Fontich--de la Llave Theorem 1.2が要求する
\(\operatorname{Spec}(A_1)^i\cap\operatorname{Spec}(A_2)=\varnothing\)、\(2\le i\le89\)をdirectに認証した。

### 定理帰結と主張境界

Q007gの解析性・local diffeomorphism・固定保存量葉、Q007h1のstable selected split・excluded invertibility・
degree-90 tailと合わせ、固定17² filtered mapのrest equilibrium近傍に、selected 24実次元spectral subspaceへ
接する局所解析的不変多様体と解析的parameterization \(K\)、reduced map \(R\)が存在する。同じ接空間を持つ
\(C^{90}\) locally invariant manifoldのクラスで局所一意である。

この結論は定性的・局所的で、explicit neighborhood radiusを与えない。またQ006i／Q007b／Q007c1の数値
Taylor係数がこの一意な多様体の厳密jetであること、finite-ball normal attraction、grid-uniform性、continuum
limitも示していない。次は係数へ進む前に、登録数値固有ベクトルと定理の厳密selected subspaceのtangent bridgeを
区間固有対で認証する。

## 2026-08-08: Q007j rational Krawczyk selected-eigencoordinate bridge

### 実装

- Q006i、Q007h1、Q007iのfull-file SHAとpackage sourceを固定したまま、独立proof runnerのSHAを別記録した。
- axis `(1,0)`、diagonal `(1,1)`の3 branchについてright／left各6、計12個のpivot-normalized complex
  eigenpair systemを構成した。
- exact rational Fourier rectangle、exact dyadic center／inverse candidate、component半径`1e-10`から
  Krawczyk imageを`Fraction`だけで評価した。
- right rootをQ007h1 negative representativeのselected Bauer--Fike discへ対応させ、C4 permutation／共役で
  全24 modeへ輸送した。left rootはright rootとのoverlapを区間評価してexact biorthogonal normalizationを作った。

### 結果

全5 validity gateと全4 hypothesis gateが通過した。

- representative／branch／system／transported mode: `2 / 6 / 12 / 24`
- maximum Krawczyk utilization: `3.453560282251993e-5`
- maximum point inverse defect／interval contraction:
  `7.929821403096009e-15 / 7.431317256896775e-9`
- Q007h1 representative proof digest mismatch: `0`
- selected-disc unique assignment／collision: `6 / 0`
- minimum overlap modulus lower: `0.9888476879367266`
- maximum right／biorthogonal-left correction upper:
  `1.153401559605646e-15 / 2.9617269241843315e-15`
- conjugate label mismatch: `0`

従って`registered selected eigencoordinates rigorously bridge to the theorem spectral subspace`として`accepted`とした。
Q006i以降のmode label、right tangent direction、left extractor coordinateは、Q007iの定理で選ばれた厳密spectral
subspaceの一意なsimple eigenpairsを表すと認証された。

これはlinear coordinate同定だけである。Q006iの300 quadratic coefficient、Q007b／Q007c1の高次係数、explicit
radius、finite-ball attractionはまだ認証していない。次はQ007kで二次forcing／homological solveだけを区間化する。

## 2026-08-08: Q007n quartic-centered explicit local radius

### 実装

- Q007h1--Q007mの6 artifact SHAとQ007j--Q007mの4 runner SHAを固定し、全sealed gateとQ007c1の
  5 coefficient hashを再確認した。
- 24 complex modal coordinateへ\(\ell^1\) norm、full Fourier-population stateへWiener \(\ell^1\) norm、
  pairへ\(\max(\|H\|,c_V\|G\|)\)を固定した。
- D2Q9 weightsと\(\omega=3/2\)から、非線形部の全次数majorant
  \((21/2)x^2/(1-x)\)とその微分をexact rationalで導いた。
- Q007i log-gapをabsolute gapへ変換し、external blockにはQ007h1のBauer--Fike／Neumann bound、
  selected outputには12次bordered determinantとadjugate boundを使った。後者はexternal eigenvectorの
  個別一意性や対角化可能性を仮定しない。
- Q007k／Q007l／Q007mのexact root boxから\(h_2,h_3,h_4,g_2,g_3,g_4\)を上から囲み、quartic centerで
  4次まで消える不変性残差のdegree-5 tailを構成した。
- 元の有理upperを80桁10進格子へ外向きに丸め、登録した`1e-2`から`1e-120`までの119候補を
  `Fraction`で評価した。全候補のexact signとbit length、選択境界2点の完全なbase-16有理数を保存した。

### 結果

全5 validity gateと全4 hypothesis gateが通過した。

- raw／working all-degree absolute gap lower: `1.611328085325626e-10 / 1.611328085325626e-10`
- \(S_\infty\) upper／bordered-entry upper: `6.025984057925574 / 1.6509200830138158`
- pair homological inverse upper: `1.5620130640618827e71`
- registered／passing radius count: `119 / 46`
- largest passing modal radius: `1e-75`
- previous larger candidate: `1e-74`（contraction `4.49393612526706`でfail）
- selected contraction／radii margin:
  `0.449393612526706 / 8.2002417161445e-297`
- selected correction radius \(\tau\): `1.620396579477627e-295`
- contained real-coordinate Euclidean radius lower: `3.470110468942836e-75`

従って`registered quartic-centered contraction gives an explicit fixed-leaf local radius`として
`accepted`とした。固定17²・固定保存量葉で、Q007mのexact quartic jetから\(\tau\)以内にあるanalytic
\(W,R\)の存在を\(\|b\|_1<10^{-75}\)で認証し、Q007iの局所一意性により同じ定理多様体と同定した。

### 主張境界

`1e-75`は最適半径ではなく、内部blockへ使った\(12!2^{11}\delta^{-6}\) adjugate boundの粗さに支配される。
従って実用半径を得たとは解釈しない。Q007c1の有限振幅directional-shadowing棄却、forward invariance、
positivity、finite-ball normal attraction、grid-uniform性、continuum limitは変更・認証していない。
次は存在結論を維持したまま、内部bordered resolvent上界だけを独立に鋭くする。

## 2026-08-08: Q007o exact external-complement resolvent refinement

### 実装

- Q007h1／Q007j／Q007n artifact SHAとQ007n runner SHAを固定し、source、scope、全sealed gateを再確認した。
- Q007nのworking all-degree gap、degree-2--4 majorant、D2Q9 nonlinear majorant、external／zero inverse、
  119候補と収縮閾値を変更しなかった。旧pair inverseで119 candidate recordがartifactとexact一致することを
  validity gateにした。
- Q007jのexact selected \(V,L\) boxから\(P=VL^*\)、\(Q=I-P\)を構成した。Q007h1のnegative C4
  representativeで作ったexternal center vectorsをpositive axial／diagonal代表へexact transportし、
  artifact proof digestを再現した。
- 固定selector rows`(0,1,2,3,7,8)`／`(0,1,2,3,4,5)`で\(JU\)を6次元化し、
  midpoint inverseのNeumann defect、projected residual、\(\gamma\)、graph-gauge chart inverseを
  exact `Fraction` intervalで評価した。
- reduced correctionにはbordered全逆行列を使わず、graph-gauge identity \(G=-L^*F\)を用いた。
  external eigenvalueの個別一意性やexternal diagonalizabilityは仮定していない。

### 結果

全6 validity gateと全4 hypothesis gateが通過した。

- axial coordinate defect／\(\gamma\)／pair inverse:
  `2.6657034780660514e-13 / 4.4155560973760785e-15 / 1.3284288681133191e11`
- diagonal coordinate defect／\(\gamma\)／pair inverse:
  `3.724809047388777e-13 / 1.1339793519314153e-14 / 2.1920952274236575e11`
- working internal pair inverse upper: `2.1920952274236575e11`
- unchanged external-output inverse upper: `2.746444556852928e13`
- new total／Q007n old pair inverse upper:
  `2.746444556852928e13 / 1.5620130640618827e71`
- registered inverse-upper reduction factor: `5.687400680142434e57`
- registered／passing candidate count: `119 / 103`
- largest passing modal radius／previous fail: `1e-18 / 1e-17`
- selected／previous contraction: `0.07901564138003579 / 0.7901564138003603`
- correction radius \(\tau\)／radii margin:
  `2.8490986842816327e-68 / 1.199425982247287e-68`
- contained real-coordinate Euclidean radius lower: `3.470110468942836e-18`

従って`exact external-complement resolvent strictly sharpens the registered explicit radius`として
`accepted`とした。Q007nと同じfixed 17² map・固定保存量葉・全次数gap・nonlinear majorantのもとで、
同じanalytic theorem manifoldの登録existence radiusを`1e-18`へ改善した。

### 主張境界

新しいtotal inverse upperはinternal blockではなく、Q007nから据え置いたexternal-output
Bauer--Fike／Neumann upperに支配される。`1e-18`は最適半径ではなく、位相情報を捨てたuniform gapも
維持している。Q007c1の有限振幅directional-shadowing棄却、finite-ball normal attraction、
forward invariance、positivity、grid-uniform性、continuum limitは変更・認証していない。
次はこの半径を固定入力とし、finite-ball normal attractionだけを独立gateで扱う。

## 2026-08-08: Q007p exact-manifold finite-tube normal attraction

### 実装

- Q007h1／Q007n／Q007o artifact SHAとQ007n／Q007o runner SHAを固定し、source、scope、全sealed gateを
  再確認した。Q007oのanalytic radius \(\rho=10^{-18}\)とselected boundary correction \(\tau\)を変更しなかった。
- graph gauge \(W(a)=Va+H(a)\)、\(\mathcal LW=a\)を固定し、base radius \(r=10^{-19}\)、normal radius
  \(\zeta=10^{-20}\)のtubeを結果を見る前に登録した。
- zero waveにはfixed-leaf kinetic population \(\ell^1\)、8 selected waveにはQ007oの6次元external
  coordinate、残る280 waveにはQ007h1のtransported full eigencoordinateを用いた。
- 70 nonselected C4代表でNumPy center／returned column orderをQ007h1と同じに再構成した。
  rational symbol boxに対し、\(I-KE\)、\(AE-ED\)、coordinate inverse、linear contractionを全て
  `Fraction` intervalで評価し、70 proof digestを再現した。
- 2 selected代表ではQ007o coordinate inverse／projected residualをexact replayし、C4で全8 selected
  waveへ輸送した。zero blockを加え、`70*4 + 2*4 + 1 = 289` blockとexternal complex dimension
  `2574`を閉じた。
- Q007nの\(c_V,h_2,h_3,h_4,g_2,g_3,g_4\)、D2Q9 \(21/2\) derivative majorant、Q007oの
  \(\rho,\tau\)をexact reuseし、state radius、base drift、fiber derivative、tangent conormを有理数だけで
  評価した。
- zero-wave collisionを\(C=-I/2+(3/2)VM\)へexact factorizationし、fixed leaf上の\(-I/2\)作用を確認した。
  Q007oの\(AQ=QA\)、\(\mathcal LQ=0\)から\(\mathcal LAQ=0\)を監査し、C4 population permutationが
  \(\ell^1\) normを保つことも確認した。

### 結果

全6 validity gateと全4 hypothesis gateが通過した。

- nonselected／selected representative: `70 / 2`
- represented wave block／external complex dimension: `289 / 2574`
- Q007h1 proof-digest mismatch／Q007o selected replay mismatch: `0 / 0`
- maximum nonselected coordinate defect: `9.306827894107678e-15`
- linear external contraction \(q_0\): `0.981709835832552`
- synthesis／analysis／selected-left upper \(K_s/K_a/K_L\):
  `2.888267212368763 / 29.917136268364473 / 1.5106842091904618`
- tube-state Wiener upper \(x_*\): `3.075728140408179e-19`
- base-image modal upper \(a_*\): `9.920954673554099e-20`
- base forward-invariance margin \(r-a_*\): `7.904532644590156e-22`
- normal fiber contraction \(q_*\)／cap margin:
  `0.9817098358325526 / 0.008290164167447421`
- normal tube margin: `1.8290164167447423e-22`
- tangent conorm lower \(m_T\): `0.9837709569923394`
- domination ratio \(\Gamma_*\)／cap margin:
  `0.9979048769989224 / 0.0010951230010776572`

従って`registered fixed-leaf tube is uniformly normally attracting in the external-coordinate norm`として
`accepted`とした。固定17²・固定保存量葉のexact theorem manifoldについて、
\(\|a\|_1\le10^{-19}\)、\(\|z\|_*\le10^{-20}\)の登録tubeはforward invariantであり、normal fiberは
one-stepで一様に収縮し、tangentよりstrictに速く収縮する。

### 主張境界

これはQ007fの33 starting point／10-step observationではなく、登録tube全体に対する解析的majorantである。
ただし\(\|\cdot\|_*\)は固定Fourier external-coordinate block-sum \(\ell^1\) normで、Euclidean normではない。
Q007dのEuclidean projected-normal棄却、Q007c1の有限振幅directional-shadowing棄却を変更しない。
population positivity、より大きいtube、global basin、grid-uniform attraction、continuum limitも認証していない。
次はこの極小tubeを拡大解釈せず、残る研究課題を独立gateとして一つずつ扱う。

## 2026-08-08: Q007q registered-tube population positivity

### 実装

- Q007p artifact／runner SHA、package source、固定17²・\(\omega=3/2\)・\(\eta=1/100\)・固定保存量葉、
  base radius \(10^{-19}\)、normal radius \(10^{-20}\)、全validity／hypothesis gate、4 theorem flagを
  再確認した。
- D2Q9の9 velocityとweightをexact `Fraction`として監査し、rest／axis／diagonalのmultiplicity
  \(1/4/4\)、weight sum \(1\)、minimum weight \(1/36\)を再構成した。
- Q007pの289 Fourier blockとreal conjugacy constraintを再確認し、
  \[
  \max_{x,i}|\delta f_i(x)|
  \le\max_i\sum_k|\widehat{\delta f}_{k,i}|
  \le\|\delta f\|_{\mathrm W}
  \]
  を明示的なvalidity gateにした。
- Q007pのchart upper \(w(r)\)、synthesis upper \(K_s\)、normal radius \(\zeta\)から
  \(x_*=w(r)+K_s\zeta\)を保存済み有理数だけでexactに再構成した。
- population／density lowerを浮動小数値ではなく
  \(p_*=1/36-x_*\)、\(d_*=1-x_*\)というexact rational差で判定した。

### 結果

全5 validity gateと全3 hypothesis gateが通過した。

- D2Q9 population count／weight multiplicity: `9 / (1, 4, 4)`
- weight sum／minimum: `1 / 1/36`
- Fourier wave count: `289`
- chart radius upper \(w(r)\): `2.7869014191713026e-19`
- synthesis upper \(K_s\): `2.888267212368763`
- tube-state Wiener upper \(x_*\): `3.075728140408179e-19`
- population lower: exact \(1/36-x_*>0\)
- density lower: exact \(1-x_*>0\)
- runner SHA-256:
  `026b4d549e92bf74ac29393244a4400fb7a8d1bb3eb263ee729d81432c8290e5`
- artifact newline-normalized SHA-256:
  `e8c763419f6e803f102f81a3beb957261b736754ab490ca3cb914dc9247269cb`

従って
`registered Q007p tube lies in the strictly positive population cone at every full-map iterate`
として`accepted`とした。Q007pのforward invarianceにより、固定tube内から開始する全real stateの
9 populationとdensityには、full one-step mapの入力／出力時刻 \(n=0,1,2,\ldots\) で同じstrict lowerが
帰納的に適用される。

### 主張境界

これはfull mapのsampling時刻だけの結論である。BGK collision直後、streaming直後、filter内部の
stagewise positivity、entropy、monotonicity、maximum principleは認証していない。より大きいtube、
global basin、grid-uniform性、continuum limitも扱わず、Q007c1の有限振幅性能棄却とQ007dのEuclidean
棄却も変更しない。次の課題は別gateとして事前登録する。

## 2026-08-08: Q007r exact stagewise population positivity

### 実装

- Q007q artifact／runner SHA、package source、scope、全sealed gate、3 theorem flag、transitive Q007p inputを
  固定し、Q007qのexact \(x_*\)、base／normal radius、Q007p forward-invariance flagを再利用した。
- D2Q9 moment matrix \(M\)、rest-equilibrium tangent \(E\)、BGK collision linearization
  \(C=(1-\omega)I+\omega EM\)を`Fraction`だけで構成し、登録rational collision symbolとentrywise
  一致させた。
- \(EM\)と\(C\)の全9 column absolute sumをexactに列挙し、induced \(\ell^1\) norm
  \(13/6\)、\(19/6\)を得た。
- D2Q9 weight sum、weighted absolute velocity quadratic、2 momentum-square componentを監査し、
  equilibrium／collision nonlinear constant \(7\)、\(21/2\)を再構成した。
- 17² periodic site mapを全9 populationで列挙して各streaming mapのbijectivityを確認し、basis replayも
  行った。
- five-point filterを\(99/100\)と4個の\(1/400\)からなるexact convex combinationとして再構成し、
  全9 population basisとwrapped stage compositionを実装に対してreplayした。

### 結果

全6 validity gateと全5 hypothesis gateが通過した。

- equilibrium projector／collision linear norm: `13/6 / 19/6`
- equilibrium／collision nonlinear constant: `7 / 21/2`
- equilibrium／collision nonlinear remainder upper:
  `6.622072515589128e-37 / 9.933108773383692e-37`
- equilibrium deviation upper \(e_*\):
  `6.66407763755105e-19`
- post-collision deviation upper \(c_*\):
  `9.73980577795923e-19`
- streaming periodic permutation replay: `9 / 9`
- filter coefficient sum／minimum: `1 / 1/400`
- filter basis／wrapped composition replay: pass
- runner SHA-256:
  `0f990cb4c046f9c7aedd4f68d6255ed014e1bdb694401505c5e4cc65ead028d6`
- artifact newline-normalized SHA-256:
  `f88710066712720552594e96aad24d8ca216fd8ffa2dc7eb2877a3287647ba67`

従って
`registered Q007p tube is population-positive at every exact BGK, streaming, and filter stage`
として`accepted`とした。equilibrium evaluation、BGK collision output、periodic streaming output、
five-point filter outputのpopulation lowerは全てexactに正である。Q007pのforward invarianceにより、
同じstage boundを全iterateへ再適用できる。

### 主張境界

これはexact mathematical mapの各stage outputに対する結論であり、NumPy／IEEE-754の全中間加算・除算を
roundoff intervalで囲った結果ではない。entropy、monotonicity、maximum principle、より大きいtube、
global basin、grid-uniform性、continuum limitを扱わず、Q007c1の有限振幅性能棄却とQ007dのEuclidean
棄却も変更しない。

## 2026-08-08: Q007s registered-grid finite-tube enlargement

### 実装

- Q007p artifact／runner SHA、package source、固定17²・固定保存量葉・exact manifold・external-coordinate
  norm、全upstream／sealed gate、4 theorem flagを固定した。
- Q007pの\(\rho,\tau,c_V,h_2,h_3,h_4,g_2,g_3,g_4,q_0,K_s,K_a,K_L,\lambda_s,\lambda_{\min}\)と
  nonlinear derivative constant \(21/2\)をexactに再利用した。保存されていた6個のbox-audit係数も別欄で
  完全照合した。
- base grid \(\{m\,10^{-19}:m=1,\ldots,9\}\)とnormal grid
  \(\{m\,10^{-e}:e=10,\ldots,20,\ m=1,\ldots,9\}\)の全891 candidateを`Fraction`で評価し、
  単調性による枝刈りを行わなかった。
- Q007p control \((10^{-19},10^{-20})\)について12 fieldと8 strict marginをexactに再現した。
- passing candidateのbase radius、次にnormal radiusを最大化する事前登録済み辞書式規則を適用し、
  全candidateのexact decision quantityとgateをcanonical digestへ封印した。

### 結果

全6 validity gateと全5 hypothesis gateが通過した。

- registered／passing candidate count: `891 / 676`
- base-slice passing counts:
  `73 / 74 / 74 / 75 / 75 / 76 / 76 / 76 / 77`
- selected base／normal radius:
  `9e-19 / 5e-12`
- Q007p controlからのbase／normal improvement factor:
  `9 / 500000000`
- tube-state Wiener upper \(x_*\): `1.44413385700551e-11`
- base-image modal upper \(a_*\): `8.9950210818665e-19`
- base forward-invariance margin \(r-a_*\): `4.97891813350137e-22`
- normal contraction \(q_*\): `0.9817098620375503`
- tangent conorm lower \(m_T\): `0.9837709569923394`
- domination ratio \(\Gamma_*\): `0.9979049036362179`
- domination-cap margin: `0.001095096363782186`
- selected sliceのfirst larger normal candidate:
  `6e-12`、`base_forward_invariance`だけでfail
- canonical candidate digest:
  `91fcc70355acfc4b7163c951227188960ef275408b06a678d45d5e4ec4c85300`
- runner SHA-256:
  `6c8633f7e99874ac3be7dd14d3caa253b0dc8c499bb2f6edbb392fa695975b1e`
- artifact newline-normalized SHA-256:
  `7b70fd20df8fb7db5e5460a08d3f86fe8b81a55b56864c860a2c24e9cab63292`

従って
`registered exact-manifold tube enlarged on the fixed rational candidate grid`
として`accepted`とした。固定17²・固定保存量葉・同じexact manifold・同じexternal-coordinate normで、
選択tubeはforward invariantかつ一様one-step normal-contractingであり、tangentに対してstrictly normally
dominatingである。

### 主張境界

これは9×99有限登録格子上の辞書式最大点であり、連続最適化、最大可能tube、Euclidean／grid-uniform
attraction、global basin、continuum limitを意味しない。Q007q／Q007rのpopulation／stagewise positivityは
旧Q007p tubeだけに封印されたままで、新tubeへは拡張していない。Q007c1の有限振幅性能棄却とQ007dの
Euclidean棄却も変更しない。次は新tubeのpositivityを独立gateとして扱う。

## 2026-08-08: Q007t larger-tube full-map population positivity

### 実装

- Q007s artifact／runner SHA、source／scope、全6 validity gate、全5 hypothesis gate、4 theorem flag、
  canonical candidate digestを固定した。
- Q007s selected candidateのbase／normal radius、state upper、全6 candidate gate、forward-invariance
  theorem flagをexactに再利用した。
- Q007sが固定したtransitive Q007p artifactを再読込し、SHA、Fourier block count、external-coordinate
  norm definition、real conjugacy constraintを再確認した。
- D2Q9の9 velocityとweightをexact `Fraction`で構成し、rest／axis／diagonal multiplicity、
  weight sum、minimum weightを独立に再構成した。
- Fourier phaseのunit modulusとpopulation-wise triangle inequalityから、各physical population deviationが
  Q007sのWiener state upper \(x_*\)以下になることを監査した。

### 結果

全5 validity gateと全3 hypothesis gateが通過した。

- Q007s input／transitive Q007p norm audit: pass
- D2Q9 population count／weight multiplicity: `9 / (1, 4, 4)`
- weight sum／minimum: `1 / 1/36`
- Fourier wave count: `289`
- selected base／normal radius: `9e-19 / 5e-12`
- selected tube-state Wiener upper \(x_*\): `1.44413385700551e-11`
- population lower: exact \(1/36-x_*>0\)、float `0.02777777776333644`
- density lower: exact \(1-x_*>0\)、float `0.9999999999855587`
- runner SHA-256:
  `1e00281c71b5ea5d06fedcebd9bd483a73e6ec111388df20e8255ae3aefed877`
- artifact newline-normalized SHA-256:
  `2089d97aa19248cc17689f3e7a01e113540e5afc329ffa5cb3a4c511a43a8529`

従って
`registered Q007s larger tube lies in the strictly positive population cone at every full-map iterate`
として`accepted`とした。Q007s selected tube内の全real stateについて、全9 populationとdensityは
full one-step mapの入力／出力時刻でstrict positiveである。Q007sのforward invarianceにより同じboundを
全iterateへ帰納的に適用できる。

### 主張境界

これはfull-map sampling時刻だけの結論であり、equilibrium evaluation、BGK collision、streaming、filterの
stagewise positivityは認証しない。Q007rのstagewise certificateは旧Q007p tubeだけに封印されたままである。
entropy、monotonicity、maximum principle、IEEE-754 roundoff enclosure、連続最適tube、global basin、
grid-uniform性、continuum limitを扱わず、Q007c1の有限振幅性能棄却とQ007dのEuclidean棄却も変更しない。

## 2026-08-08: Q007u larger-tube exact stagewise population positivity

### 実装

- Q007t artifact／runner SHA、source／scope、全5 validity gate、全3 hypothesis gate、3 theorem flag、
  transitive Q007s input／tube reuseを固定した。
- Q007tのexact state upper \(x_*\)、population lower、base／normal radius、Q007s selected candidateの
  全6 gate、forward-invariance flagをexactに再利用した。
- D2Q9 moment map \(M\)、rest-equilibrium tangent \(E\)、equilibrium projector \(EM\)、BGK
  collision linearization \(C=(1-\omega)I+\omega EM\)を`Fraction`で再構成し、全column sumと
  rational collision mapを照合した。
- D2Q9 weight sum、weighted absolute velocity quadratic、cyclic Fourier convolutionから、
  equilibrium／collision nonlinear majorant constant \(7,21/2\)を再導出した。
- 全9 populationの17² periodic streaming bijection、filter係数 \(99/100\)と4個の\(1/400\)、
  wrapped stage compositionを実装basis replayで照合した。

### 結果

全6 validity gateと全5 hypothesis gateが通過した。

- Q007t input／transitive Q007s selected tube reuse: pass
- equilibrium projector／collision induced \(\ell^1\) norm:
  `13/6 / 19/6`
- equilibrium／collision nonlinear constant:
  `7 / 21/2`
- selected base／normal radius:
  `9e-19 / 5e-12`
- input state Wiener upper \(x_*\):
  `1.44413385700551e-11`
- equilibrium deviation upper／population lower:
  `3.12895669032459e-11 / 0.02777777774648821`
- post-collision deviation upper／population lower:
  `4.5730905474030926e-11 / 0.02777777773204687`
- post-streaming／post-filter population lower:
  `0.02777777773204687 / 0.02777777773204687`
- runner SHA-256:
  `56fc99f1f381e97e70710c7da0cee8d1262d0c10190cf617316f822d1eb29014`
- artifact newline-normalized SHA-256:
  `b568fc304fd939121dd52543f316cb571ae6f4be4f4f664c68fe1c749b566c55`

従って
`registered Q007s larger tube is population-positive at every exact BGK, streaming, and filter stage`
として`accepted`とした。Q007s selected tube内の全real stateについて、exact equilibrium
evaluation、BGK collision output、periodic streaming output、five-point filter outputで全9 populationが
strict positiveである。Q007sのforward invarianceにより同じstage boundを全iterateへ帰納的に適用できる。

### 主張境界

これはexact mathematical mapに対する結果であり、NumPy／IEEE-754の全中間加算・除算を外向きroundoff
intervalで囲っていない。entropy、monotonicity、maximum principle、連続最適tube、global basin、
grid-uniform性、continuum limitを扱わず、Q007c1の有限振幅性能棄却とQ007dのEuclidean棄却も変更しない。

## 2026-08-08: Q007v binary64 stage-roundoff enclosure

### 実装

- Q007u／Q007s artifact・runner SHA、全sealed gate／theorem flag、selected tubeと、現行D2Q9／filter
  source SHAを固定した。
- binary64 unit roundoff \(u=2^{-53}\)とsubnormal absolute fallback \(h=2^{-1075}\)を固定し、
  exact target intervalとabsolute forward-error upperのpairを`Fraction`だけで伝播した。
- D2Q9 weight、\(\eta\)、filter center／neighbour係数は実際のbinary64 dyadic valueを
  `Fraction.from_float`で復元し、exact rationalとの差を含めた。
- density／momentum reduction、velocity division、equilibrium polynomial、BGK update、streaming、
  filterについてsource scheduleとoperation countを固定し、arbitrary reduction orderを
  \(\gamma_n\) boundで囲った。
- post-filter component errorをnormalized 17² DFT triangle boundでWiener errorへ変換し、Q007sの
  selected／external analysis normからbase／normal coordinate re-entry errorを評価した。

### 結果

全7 validity gateが通過した。6 hypothesis gateのうちone-step positivityの5件は通過し、
roundoff-robust tube re-entryだけが失敗した。

- input／source／binary64 model／paired arithmetic／operation replay: pass
- registered operation count:
  input rounding `9`、sign/zero product `36`、add/subtract/multiply/divide
  `36 / 18 / 83 / 2`、reduction `22 calls / 61 additions`
- equilibrium lower／maximum component error:
  `0.027777777759726004 / 7.154770604839416e-16`
- post-collision lower／maximum component error:
  `0.02777777771459676 / 1.2459169501537343e-15`
- post-streaming lower:
  `0.02777777771459676`
- post-filter lower／maximum component error:
  `0.027777777714596753 / 1.3501237168549712e-15`
- Wiener roundoff upper:
  `1.1666869562204168e-12`
- base error／margin／utilization:
  `1.7624955618306674e-12 / 4.978918133501365e-22 / 3.539916734062091e9`
- normal error／margin／utilization:
  `3.490393265176959e-11 / 9.145068981224883e-14 / 381.6694299783683`
- one-step／robust-reentry outcome:
  `accepted / not_certified`
- runner SHA-256:
  `a0d3cea0fcae8a627f4a96db56d46727589411b2557e2aa91433569576a0575c`
- artifact newline-normalized SHA-256:
  `c4c1c45941a6f6ac302691efd8e795e431f6acc1fa4f4629cb0c7a0afac3c0a5`

従って
`binary64 one-step stages remain positive, but the registered Q007s tube is not certified roundoff-invariant`
として有効な`not_certified`とした。Q007s exact tube内のreal stateを正しくbinary64へ丸めた
入力では、一段の全内部stage populationがstrict positiveである。しかしroundoff errorをQ007s座標へ
戻したworst-case upperはbase／normal両re-entry marginを超えるため、この結論を全iterateへ帰納しない。

### 主張境界

re-entry失敗は実際のtrajectoryがtubeを脱出する反例ではない。固定component box、DFT triangle bound、
analysis normによる登録enclosureがstrict marginへ収まらないという`not certified`判定である。
nonstandard rounding、FTZ／DAZ、GPU／fast-math、entropy、monotonicity、maximum principle、連続最適tube、
global basin、grid-uniform性、continuum limitを扱わない。

## 2026-08-08: Q007w ideal binary precision threshold

### 実装

- Q007v artifact／runner SHA、source／scope、mixed outcome、transitive Q007s inputを固定した。
- Q007vのpaired arithmeticを、total significand bits \(p\)を引数とするexact ties-to-even
  binary arithmeticへ一般化した。
- \(p=53,\ldots,128\)の全76候補について、population stage enclosure、Wiener error、
  base／normal re-entry errorを同じoperation scheduleで再計算した。
- \(p=53\)でQ007vの全constant、population target/error record、stage summary、
  re-entry quantityがexactに一致することを独立gateにした。
- registered base／normal strict marginを同時に通る最小候補をsufficient thresholdとして選んだ。

### 結果

全7 validity gateと全6 hypothesis gateが通過した。

- ties-to-even halfway check: `4 / 4` pass
- candidate／passing count: `76 / 44`
- passing precision range: `85..128`
- selected precision／previous boundary: `85 / 84`
- 84-bit Wiener error／base error／base utilization:
  `5.360999559126826e-22 / 8.0987773794499245e-22 / 1.6266138872531641`
- 84-bit normal utilization:
  `1.7537949103972442e-7`
- 85-bit Wiener error／base error／base utilization:
  `2.706739822688458e-22 / 4.089029108522444e-22 / 0.8212685966874661`
- 85-bit normal error／utilization:
  `8.097790411837928e-21 / 8.854816107415864e-8`
- 85-bit minimum stage lower:
  `0.02777777771459692`
- candidate digest:
  `440a08dc36990d3e34edf1886fd7e47eacb4766c4a42352022897fd79dbb3ce2`
- runner SHA-256:
  `86dcc0a507e24216775650d5467d0ebf6e90eac0865190d0d5186e08afb7eac8`
- artifact newline-normalized SHA-256:
  `bac362d9dca4a681387b986a5f5802278ef61a1a3bcf1a0f8577c7f3ab0a07af`

従って
`registered ideal binary precision threshold restores roundoff-robust Q007s tube re-entry`
として`accepted`とした。固定Q007v worst-case enclosureでは84 bitsはnormal marginを通るが
base marginを通らず、85 bitsで初めて両marginをstrictに通る。この意味で85 significand bitsが
最小の登録sufficient thresholdである。

### 主張境界

これはideal binary arithmetic familyに対する十分条件であり、84 bits以下の実trajectoryが必ずtubeを
脱出するという必要条件ではない。具体的なNumPy／MPFR／decimal／hardware backend、rounding mode、
trajectory、性能を認証せず、Q007vのbinary64 `not_certified`も変更しない。実装mapの
roundoff-robust claimには、85 bits以上のconcrete correctly-rounded backendを別gateとして事前登録し、
Q007wとbitwise／interval cross-checkする必要がある。

## 2026-08-09: Q007x concrete MPFR-85 backend and fixed-leaf closure

### 実装

- `gmpy2==2.3.1`、`MPFR 4.2.2`、`GMP 6.3.0`を固定し、
  \(p=85\)、nearest-even、`emin=-1105`、`emax=1024`、
  gradual subnormalのcontextを構成した。
- exact rationalを`Fraction -> mpq -> mpfr`でcomponentwiseに丸め、float／decimal stringを
  経由しない専用D2Q9 collision／streaming／filter backendを実装した。
- density、momentum、velocity、equilibrium、BGK、filterを明示left-foldと個別加減乗除で実装し、
  FMA、`np.sum`、parallel reductionを使わなかった。
- constant construction、input encoding、全map operationのoperand／resultをexact dyadicへ戻し、
  Q007wのinteger ties-to-even oracleで全件照合した。
- exact fixed-leafの4 rational probeを17²で構成し、exact `Fraction` mapとの差、
  stage positivity、global \(M,P_x,P_y\)を各stageで測定した。
- backendを`research/`へ隔離し、既存`src/ttim_lbm` package fingerprintと
  upstream artifactを変更しないようにした。

### 結果

全8 validity gateが通過した。hypothesisは6件中2件が通過した。

- MPFR semantic bridge／Q007w one-step bound: pass／pass
- fixed-leaf encoding／collision／streaming／filter: fail／fail／pass／fail
- trace count: `70,824 per probe / 283,296 total`
- trace mismatch: `0`
- maximum component-bound utilization:
  `0.15250294804773457`
- rounded-weight sum defect:
  `6.462348535570529e-27`
- rounded-filter partition-of-unity defect:
  `8.077935669463161e-27`
- rest-grid encoding／filter mass defect:
  `1.8676187267798828e-24 / 8.404284270509473e-24`
- probe digest:
  `a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329`
- aggregate trace digest:
  `49ce9b304b4b6a07fdf7d7baed6c9118a97c5a08e489e3aa5eacde28662c2351`
- result digest:
  `12cb83a87895d50523c909ad314b9ad155ac507af73e05f1b28cfb2a65328c7d`
- backend／runner SHA-256:
  `25ad43629e2487c5c062920cbb5319dac4e8fbded339dc856548bfab7f18a0dc` /
  `de16e86ab365e6e64b15fd62ebdb442a54e05d4e4e529ae1e018299983d7491b`
- artifact newline-normalized SHA-256:
  `20ba483c4c627de015673a2f8873cc020a5c1a43ee48c7715121a00330e13566`

従って
`MPFR-85 realizes the Q007w one-step arithmetic bound but not the fixed conservation leaf`
として有効な`not_certified`とした。concrete backendはQ007wのideal \(p=85\) arithmeticを
operationwiseに実現し、全registered probe／stageでQ007w error upper内に収まる。しかし
componentwise encoding時点でexact fixed leafから外れ、非一様collisionとfilterも追加の保存量driftを
生成する。periodic streamingだけはexact permutationとして保存する。

### 分析と次の改善

85-bitに丸めたD2Q9 weightsは和が1ではなく、filterのrounded center／neighbour係数も
partition of unityをexactには満たさない。さらに非一様probeでは、operation roundoffによりcollisionの
mass／momentumもexactには保存されない。従ってQ007wのselected／external coordinate errorがstrict
margin内でも、固定葉から外れる3 center componentsを無視してall-iterate re-entryを主張できない。

次はQ007wのprecision／operation boundとQ007xのbackend semanticを固定し、conservation-exact
input encodingおよびpost-stage repairを別gateとして事前登録する。repairがexact \(M,P_x,P_y\)を
回復するだけでなく、その追加Wiener／base／normal errorが既存strict marginに収まることを要求する。

### 主張境界

finite probeは障害の反例を与えるが、任意のtube stateに対するdrift最大値やmulti-step trajectory、
repairの存在／安定性／性能を示さない。Q007wのideal sufficient threshold、Q007uのexact stage
positivity、Q007sのexact fixed-leaf invarianceを変更しない。GPU、threaded reduction、他のMPFR build、
continuous optimization、grid-uniform性、D3Q27を扱わない。

## 2026-08-09: Q007y distributed dyadic conservation repair

### 実装

- Q007w／Q007xのartifact、runner、MPFR backendをread-only inputとしてSHA固定した。
- 対角population \(q=5,6,7,8\) の85-bit格子幅 \(h=2^{-90}\) を用い、global
  mass／momentum defectを整数Hadamard系へ変換した。
- 自由整数 \(t\) は、対角4総unitについて

  \[
  \left(\sum_i|a_i|,\max_i|a_i|,|t|,t\right)
  \]

  を辞書式最小化した。各総unitは`divmod(total,289)`でrow-major siteへ均等配分した。
- componentwise encoding直後とpost-filter直後にだけ補正を適用した。collision内部のdriftを
  許し、Q007x backendの演算順序・定数・primitive operationは変更しなかった。
- 全補正加算をexact rationalへ戻し、exact addition、same binade、positivity、MPFR flagを検査した。
- Q007wの85-bit paired evaluatorを再生し、population別post-filter errorからmass／momentum defectと
  repair-aware Wiener boundをexact rationalで構成した。

### 結果

全8 validity gateが通過した。hypothesisは7件中5件が通過し、base budgetとall-iterate inductionが
失敗した。

- finite repaired conservation:
  `input 4/4 exact / post-filter 4/4 exact`
- repair additions:
  `9,248 / 9,248 exact, same-binade, positive`
- maximum finite component-bound utilization:
  `0.15776531320758136`
- raw post-filter Wiener error upper:
  `2.706739822688458e-22`
- repair Wiener addition upper:
  `4.959477689155467e-22`
- repaired Wiener error upper:
  `7.666217511843926e-22`
- base error／margin／utilization:
  `1.158123373936201e-21 / 4.978918133501365e-22 / 2.326054260951996`
- normal error／margin／utilization:
  `2.2935127396475674e-20 / 9.145068981224883e-14 / 2.507922842743146e-7`
- finite campaign digest:
  `f47bb30b0e2280d339a40b196d1ca3dcb84f94b9e8de087bbff215d07a220fe6`
- runner SHA-256:
  `ba757030c852b68d5a4c643ec150422c0a7b4c3ba125211d2715ba1445e89811`
- artifact newline-normalized SHA-256:
  `a3afa87c4ee3f5d45e667eac9a6a89a1726f1d4bad0a9f90a624c562fb598648`

従って
`distributed MPFR-85 repair restores the registered fixed-leaf probes but not the Q007w tube-wide base budget`
として有効な`not_certified`とした。有限実装だけでなく、Q007w登録boxのbinade、共通dyadic lattice、
parity、最悪site補正を用いてrepair自体がtube全体で定義できることも示した。normal marginには十分
収まるが、粗いtriangle boundによるbase errorはmarginの2.326倍であり、Q007s re-entryを全iterateへ
帰納できない。

### 分析と次の改善

今回の上界はraw errorの全Wiener normへrepairのphysical \(\ell^1\) upperを単純加算する。
しかしrepair後にはglobal \(M,P_x,P_y\) errorがexactにゼロであり、raw center errorとrepair centerは
相殺している。また、balanced distributionのnonzero-wave Fourier contentはphysical \(\ell^1\)より
大幅に小さい可能性がある。次は封印済みrepairを変えず、center cancellationと実際のspatial phaseを
selected spectral projectorへ通した上界を独立に事前登録する。

### 主張境界

4 finite probeの成功だけをtube sampling proofとは呼ばない。tube-wideに示したのはrepairの
algebraic well-definednessと粗いworst-case boundであり、projector-aware bound、multi-step trajectory、
性能、parallel reduction、他のMPFR build、center-slow構成、grid-uniform性、D3Q27を示さない。
Q007w／Q007xおよびQ007s／Q007uの既存結論を変更しない。

## 2026-08-09: Q007z selected-wave repair certificate

### 実装

- Q007pの2 selected C4 orbitとper-orbit left-operator norm、Q007yのbackend／repair／artifactを
  SHA固定し、Q007y cycleをfresh replayした。
- 8 selected wavesと全\(r=0,\ldots,288\)について、row-major prefixの17th-root phase
  histogramをexact integerで構成した。
- 各nonzero characterのfull 17² histogramが17 phaseごとに17個であることから、一様quotientの
  DFTがcyclotomic identityでexactにゼロとなることを検証した。
- prefixとcomplementのtriangle boundを同時に使い、

  \[
  |\widehat c_q(k)|\le \frac{144}{289}2^{-90}
  \]

  をtotal correction unitに依存しないtube-wide upperとして構成した。
- 軸／対角orbitのexact left normを別々に掛け、repairのselected-base寄与だけを再評価した。
  raw MPFR base errorとQ007y full-Wiener normal errorは小さくせず、そのまま再利用した。

### 結果

全6 validity gate、全7 hypothesis gateが通過した。

- selected structure:
  `2 C4 orbits / 8 nonzero waves / k=0 excluded`
- phase histogram／distribution cases:
  `2,312 / 4,624`
- axis／diagonal left norm:
  `1.5106842091904618 / 1.4732828143196361`
- four-population per-selected-wave upper:
  `1.6099968669933496e-27`
- repair base-coordinate error upper:
  `1.9216710236250915e-26`
- raw／repaired base error:
  `4.089029108522444e-22 / 4.0892212756248066e-22`
- base margin／headroom／utilization:
  `4.978918133501365e-22 / 8.896968578765586e-23 / 0.8213071928437413`
- normal utilization:
  `2.507922842743146e-7`
- selected／phase／result digest:
  `ea5d303e4333638447d70ef8ec6692599948260657e7cb51c133b8c3c5d20b90` /
  `f0da04edcc58edd6b96b2869ee67c79cc44b020278545bc52d03a142c0fa4a83` /
  `62262fe2cfb0bf361e5b79aaf89c8ba319ad1df046bf59aff56be8b7a54d4054`
- runner SHA-256:
  `0e2b3aebdc30d6a441178e3ac05fe417ab66673885a52ac9da801bd787dd8f79`
- artifact newline-normalized SHA-256:
  `b1ca382a76e874c18b804c7614ff8ad1ded3a5d0b9dda583facf6641b24f0c53`

従って
`selected-wave certificate closes the repaired MPFR-85 fixed-leaf tube induction`
として`accepted`とした。Q007yのcoarse physical-\(\ell^1\) repair normはuniform quotientを
全波数へ課金したためbase gateを落としたが、selected baseは8 nonzero wavesだけである。uniform
quotientをexactに除きprefix remainderだけへ課金すると、repair base寄与は\(1.92\times10^{-26}\)となり、
base marginに\(8.90\times10^{-23}\)のstrict headroomが残った。normal側はQ007yの粗い上界のまま通る。

### 定理的帰結

`already encoded, repaired MPFR-85 state`が登録Q007s tubeとfixed leafに属することを初期条件とする。
この条件下で、Q007w raw stage enclosure、Q007y exact post-stage repair、Q007z base／normal strict
re-entryを反復できる。従ってsampling timeのexact \(M,P_x,P_y\)、Q007s tube membership、
全MPFR equilibrium／collision／streaming／filter／repair stageのstrict positivityを全iterateへ
帰納できる。

### 主張境界と次の改善

任意のexact boundary stateを85-bitへencodingした後もtube内に入るとは示していない。trajectory error、
exact mapとのshadowing時間、性能、parallel reduction、他のgrid／MPFR build、center-slow構成、D3Q27を
扱わない。Q007yは粗いestimatorに対する有効な`not_certified`として保存する。次はinitialization
interiorを定義したうえで、repaired MPFR mapとexact mapのmulti-step shadowingを別gateで評価する。

## 2026-08-09: Q007aa exact-state encoding initialization interior

### 実装

- Q007s／Q007y／Q007zのartifactとrunner SHAを固定し、Q007yとQ007zのcycleをfresh replayした。
- Q007s外側tube \(r=9\times10^{-19}\)、\(\zeta=5\times10^{-12}\)に対し、
  結果を見る前に

  \[
  r_0=8.9998\times10^{-19},\qquad
  \zeta_0=4.999999999\times10^{-12}
  \]

  をinitialization interiorとして固定した。
- Q007y input boundからraw componentwise encoding errorとrepair physical errorをexact rationalで
  再構成した。base repairにはQ007zのselected-wave phase boundを再利用し、

  \[
  \epsilon_a=K_LE_{\rm raw}+B_{\rm rep}^{\rm sel}
  \]

  とした。
- graph gauge \(W(a)=Va+H(a)\) のbase移動を無視せず、

  \[
  d_H(r)=2h_2r+3h_3r^2+4h_4r^3+\frac{\tau}{\rho-r},
  \qquad
  \epsilon_z=K_a(E_W+d_H(r)\epsilon_a)
  \]

  を用いた。direct external perturbationとgraph-shift perturbationをartifactで分離した。
- \(\epsilon_a<r-r_0\)により\(a\)から\(\tilde a\)までの線分が外側base ball内に留まること、
  \(\epsilon_z<\zeta-\zeta_0\)によりnormal座標が外側tubeへ入ることをexactに検査した。

### 結果

全6 validity gate、全6 hypothesis gateが通過した。

- raw／repair／total physical Wiener upper:
  `7.470474908090484e-24 / 1.2452407101265335e-23 / 1.992288200935582e-23`
- raw／repair／total base increment:
  `1.1285528478805861e-23 / 1.9216710236250915e-26 / 1.1304745189042113e-23`
- base margin／headroom／utilization:
  `2e-23 / 8.69525481095789e-24 / 0.5652372594521056`
- chart derivative:
  `1.0403913489904792e-16`
- direct／graph-shift／total normal increment:
  `5.96035575932445e-22 / 3.5186618281273335e-38 / 5.960355759324451e-22`
- normal margin／headroom／utilization:
  `1e-21 / 4.03964424067555e-22 / 0.596035575932445`
- tight base／normal initialization radii:
  `8.99988695254811e-19 / 4.999999999403964e-12`
- input／result digest:
  `71ca5b7b6ec65d0aee8e6486da73c4e532ce9e4721e8ae59edd7c664757fb8c7` /
  `9ccdfa40693489d0161521724c10f452626bb6066712ad6d0ba8c15d53fed5bc`
- runner SHA-256:
  `a7a6334fdb157ec317f65fca2475bf3b03775af88ea6d68eec2c02c5ba74188e`
- artifact newline-normalized SHA-256:
  `cf6a0566b91e9b034d2c93290302182fe8b4a0bf0f7e7bbbbb232f3d4a12ee64`

従って
`registered exact-state interior survives MPFR-85 encoding and repair`
として`accepted`とした。登録inward marginの使用率はbase／normalとも0.6未満であり、
initial encoding／repair後の状態はstrictにQ007s tubeへ入る。

### 定理的帰結

固定保存量葉上で\(\|a\|_1\le r_0\)、\(\|z\|_*\le\zeta_0\)を満たすexact stateを
sealed MPFR-85 backendへcomponentwise encodingし、Q007y balanced repairを適用する。repair後は
exact \(M=289,P_x=P_y=0\)を満たし、base／normal座標はQ007s tube内にある。従ってQ007zの
条件付き帰納を適用でき、sampling-time fixed leaf、tube membership、全MPFR stage positivityが
全iterateで維持される。

### 主張境界と次の改善

本結果は事前登録したcoordinate interiorに限り、任意のQ007s boundary stateを含まない。
またtube membershipはtrajectory accuracyを意味しない。exact mapとの距離、有限時間shadowing、
性能、parallel reduction、他grid／MPFR build、center-slow構成、D3Q27は未評価である。次は同じ
初期化interiorとbackendを固定し、multi-step shadowingの誤差再帰とhorizonを別gateで評価する。

## 2026-08-09: Q007ab fixed-coordinate all-iterate forward shadowing

### 問い

Q007aaの同じexact initial stateから出発するexact軌道とrepaired MPFR-85軌道について、Q007s
tube-wideの固定線形coordinate contractionとQ007z one-step local defectを使い、sampling-time
forward errorを全非負iterateで一様に抑えられるか。

### 仮説

- Q007s／Q007z／Q007aaの封印入力とQ007aa fresh replayが一致する。
- 固定selected／external coordinateにおけるexact-map Lipschitz upperは1未満である。
- initial defectとone-step defectの幾何級数boundが全iterateで不変な誤差区間を作る。
- derived physical Wiener errorは事前登録した\(10^{-6}R_T\)未満である。

### 実装

- 平衡点で固定した線形coordinate

  \[
  \mathcal Cx=(Lx,JQx),\qquad
  \|\mathcal Cx\|_\oplus=\|Lx\|_1+\|JQx\|_*
  \]

  を使った。Q007sのgraph-relative normal coordinateやnormal contraction \(q_*\)は
  full-state Lipschitz定数の代用にしなかった。
- Q007sの封印constantから

  \[
  L_\oplus
  =\max(q_s,q_0)+(K_L+K_a)d_N(R_T)\max(c_V,K_s)
  \]

  をexact rationalで構成した。
- Q007aaのselected incrementとdirect external coordinate incrementから\(d_0\)を構成した。
  graph-shiftはgraph-relative tube membershipには必要だが、\(\mathcal C\)がlinearなので重複課金しない。
- Q007zのrepaired selected errorとexternal local errorから\(\epsilon_{\rm step}\)を構成し、

  \[
  d_{n+1}\le L_\oplus d_n+\epsilon_{\rm step},\qquad
  D_\oplus=\max\left(d_0,\frac{\epsilon_{\rm step}}{1-L_\oplus}\right)
  \]

  のexact fixed-point identityと区間不変性を検査した。
- \(D_W=\max(c_V,K_s)D_\oplus\)をQ007s tube-state Wiener radius \(R_T\)と比較した。

### 結果

全6 validity gate、全6 hypothesis gateが通過した。

- selected／external linear contraction upper:
  `0.9920954673554099 / 0.981709835832552`
- synthesis upper:
  `2.888267212368763`
- nonlinear derivative／coordinate Lipschitz increment:
  `3.0326810997772634e-10 / 2.7528235726518938e-8`
- full Lipschitz upper／contraction gap:
  `0.9920954948836456 / 0.007904505116354432`
- initial／one-step coordinate error upper:
  `6.073403211214871e-22 / 2.3344049524038155e-20`
- uniform coordinate／physical Wiener error upper:
  `2.9532588290365307e-18 / 8.529800645544777e-18`
- tube-state radius／relative error:
  `1.4441338570055092e-11 / 5.90651663221288e-7`
- registered absolute accuracy threshold:
  `1.4441338570055092e-17`
- input／result digest:
  `83c98750b8a18aa98cae710fad0a4d2fa139428d791a085bdd086e39e435225f` /
  `268a5e2098011561c3bc521c845e6eb804692713502fbbd54c3b3106b8f9c014`
- runner SHA-256:
  `4958e1aa5140bdbd1a32ce074c77ce2739636a34f7da2531c792ec165401c01a`
- artifact newline-normalized SHA-256:
  `3770e53e5fd169ea8ba16a568a1a1a3052afdd95d2779ba630c7ba7113bdc7ae`

従って
`fixed-coordinate contraction certifies all-iterate MPFR-85 forward shadowing`
として`accepted`とした。uniform physical boundは登録thresholdの約0.59065倍である。

### 定理的帰結

Q007aa coordinate interiorに属するexact fixed-leaf stateを一つ取る。そのexact軌道と、同じ状態を
componentwise MPFR-85 encodingしてQ007y repairを適用した軌道は、Q007s／Q007zの帰納により同じ
physical Wiener tube内に全iterateで留まる。各sampling timeのfixed-coordinate誤差は
\(D_\oplus\)、physical Wiener誤差は\(D_W\)以下で全\(n\ge0\)に一様である。

### 主張境界と次の改善

これはsame-initial-state forward estimateであり、古典的なbi-infinite shadowing lemma、backward
error、intermediate-stage trajectory distance、componentwise relative errorではない。任意のQ007s
boundary initialization、性能、parallel reduction、他grid／MPFR build、center-slow構成、D3Q27も
扱わない。Q009 TT-crossはQ008c rejectionにより開始せず、次はFourier sparse-fiberを必須baselineに
残したQ010 cost／break-even gateを事前登録する。

## 2026-08-09: Q010 sealed TT-SVD representation cost and break-even

### 問い

Q008a／Q008cでstorage棄却された固定8 TT-SVD候補に対し、独立holdout campaignでoffline
preparation、online local quartic action、raw／serialized storageをnatural sparse-fiberと比較する。
TT側に有利な共通費用除外を置いても有限break-evenを持つ候補はあるか。

### 仮説

- Q008a／Q008cのartifact、package source、fixed coefficient、8候補のfidelity／storageが再現する。
- seed `20260901`の16方向は全Q008a／Q008c方向とexact duplicateを持たない。
- 全8 TTでbest offline／online timeがworst sparse timeを上回り、median online slowdownが2以上である。
- 全8 TTがstored scalars、raw payload、serialized bytesでsparseより大きい。
- 従って登録campaignにfinite sparse-baseline time break-evenもjoint time/storage採択候補もない。

### 実装

- full quartic model／coefficient family構築とordered-dense materializationを全methodの共通入力として
  timingから除外した。これはTT-SVD costを過小評価するTT-favorable protocolである。
- sparseはfresh copyとstorage／NPZ roundtrip、TTはtensorization、full-rank TT-SVD、storage／NPZ
  roundtripをoffline costとした。warmup 1、measured 3 blockをcyclic orderで実行した。
- natural sparse、ordered-dense control、8 TTを16 holdout方向で評価した。warmup 1、measured 5
  blockとし、各blockの16 output norm checksumを保存した。
- candidate \(m\)とsparse \(s\)に対し、

  \[
  T_m^-(N)=B_m^-+Nt_m^-,
  \qquad
  T_s^+(N)=B_s^++Nt_s^+
  \]

  を比較した。\(B_m^->B_s^+\)かつ\(t_m^->t_s^+\)なら全整数\(N\ge0\)でrobust no
  break-evenとした。
- ordered-dense controlとのmedian break-evenも診断したが、必須sparse baselineを判定から外さなかった。

### 結果

全6 validity gate、全5 hypothesis gateが通過した。

- holdout direction hash／prior duplicate／maximum norm error:
  `ed625949a32c1cbf6cb7f00e0a4cca5e05675481159b29c61db59c769890609b / 0 / 2.220446049250313e-16`
- sparse offline min／median／max:
  `20.9392 / 20.9547 / 21.6592 ms`
- fastest TT offline min／median／max（`flat-q-last`）:
  `1.3654306 / 1.3732766 / 1.3768735 s`
- sparse online min／median／max:
  `0.5805375 / 0.58298125 / 0.61728125 ms per sample`
- fastest TT online min／median／max（`flat-q-last`）:
  `2.85776875 / 2.89795 / 3.0604 ms per sample`
- fastest median slowdown／robust envelope ratio:
  `4.9709145877333105 / 4.629605629524629`
- median slowdown range over 8 TT:
  `4.9709145877333105 -- 685.3140752811519`
- sparse stored real scalars／raw／serialized bytes:
  `315900 / 2614950 / 2615734`
- best TT core stored real scalars／raw／serialized bytes:
  `3550626 / 28405096 / 28406852`
- best TT/sparse ratios:
  `11.2397150997151 / 10.8625771047248 / 10.859992644512`
- maximum dense action／TT reconstruction／TT action／checksum error:
  `1.20460032995549e-14 / 1.49154657341154e-13 / 6.63724332998628e-13 / 4.65675471404282e-14`
- flat／D1Q3 ordered-dense median break-even:
  `120--144 actions`
- input／result digest:
  `566d3ce0569736c140dae7c4f19d36223957e5ad2b25abc4b9d6a012558d0841` /
  `79545f0cbf14a53fef52d46bc44cbb8586efb95e1b6645d7c8cc00b45ceed6dc`
- runner SHA-256:
  `c6e99082a3418d604f7d09687685cf5e6ab9efe341ea36153123bb8ad4b26b4e`
- artifact newline-normalized SHA-256:
  `2885a029ecfe2c17aebe3b05b305caebd927d78476971e4ab186455d0ee30b7f`

従って
`sealed TT-SVD path is cost-dominated by natural quartic sparse-fiber`
としてnegative hypothesisを`accepted`とした。

### 分析

最速候補でもTT offline minimumはsparse offline maximumの約63.04倍、TT online minimumはsparse
online maximumの約4.63倍である。全8候補でこのstrict envelopeが閉じたため、初期費用を何回の
actionで償却するかという意味のfinite break-evenは存在しない。さらに最小TT payloadもsparseの
約10.86倍なので、時間と格納量のjoint candidateは0である。

flat／D1Q3 TTがordered-dense coefficient oracleには120--144 actionでmedian break-evenを持つことは、
dense oracleだけをbaselineにすればTTが有用に見える例である。しかしnatural sparse-fiberはdenseより
小さく速いため、この比較を採択根拠にはしない。negative resultは忠実度不良ではなく、既知のFourier
selection ruleを活かす専用表現にgeneral TT-SVDが負けた結果である。

### 主張境界と次の改善

timingは現在のCPU／Python／NumPy環境の有限blockだけに限り、他machineの性能定理ではない。
ordered-dense coefficient oracleはfull dense LBMではなく、full reduced-chart rollout、direct TT-LBM、
MPFR cost、GPU、thread scaling、compressed rounding、TT-cross、別tensorization、別grid、D3Q27を
扱わない。固定Q007c1係数に対するQ009／TT-SVD online pathを閉じる。新しい表現は別candidate familyを
事前登録しない限り再開しない。次は非TTの未解決数学gateまたはQ011 boundary／forcingへ戻る。

## 2026-08-09: Q007ac phase-aware external-output resolvent refinement

### 問いと事前登録

Q007oのtotal inverseを支配するQ007n external-output upperを、complex phaseを保ったdisc separationで
selected-output internal upperより小さくできるかを問うた。target gapを`1e-7`、modulus screenを
log-gap`1e-6`へ固定し、Q007n／Q007oのinternal／zero inverse、majorant、119候補は変更しなかった。
Fourier wave-sumは使わず、全selected productと全630 nonselected-output target discを比較する
保守的なsuperset certificateとした。

### 実装

- Q007h1の72 C4 representative proofを再構成し、2 selected representativeからaxis／diagonalの
  acoustic共役対とreal shear nominal discを作った。
- 残る70 representativeの9 eigenvalueを全てtargetとし、630 complex Bauer--Fike discを構成した。
- Q007iと同じ96項rational log、110／60桁外向き格子で次数2--89の全2,919,730 modulus aggregateを
  列挙した。screen外は\(m_*10^{-6}>10^{-7}\)で直接覆った。
- screen内826 aggregateだけをacoustic positive／negativeへ108,273通り完全展開し、nearby discとの
  287,929比較をexact dyadic integer不等式で実行した。thresholdは256 binary bit格子へ上向きに丸め、
  exact targetより強い比較にした。
- Q007o旧119 candidate recordをexact再現し、診断用にexternal inverseだけを差し替えたscanも保存した。

### 結果

validity 5/6、hypothesis 4/5で、研究判定は`inconclusive`となった。

1. 対称化したnominal discは元のselected discを全て含んだが、axis acoustic discがQ007n working
   \(\sigma\)を`1.6653345369377348e-16`超えた。事前登録したvalidity条件を満たさない。
2. exact phase comparison 287,929件中4件がtarget gap`1e-7`を満たさなかった。
3. 最小witnessはdegree 71、counts`(24,38,2,7)`、acoustic split`(12,12,1,1)`、
   external `wave=(-7,-7);eigenvalue_index=6`で、certified distance lowerは
   `2.4028360293239852e-8`だった。

- safe／dangerous aggregate: `2,918,904 / 826`
- dangerous expanded product／comparison: `108,273 / 287,929`
- failed comparison: `4`
- phase digest:
  `5039563c60ab57b85b683b324506049535372847b1a5adef3362da2b16a954ab`
- input／result digest:
  `15166f90e39b132c0d6956b7a14f821095cc1b31da9d9e83b9b3f5b9cf3314b9` /
  `369809e953652c9e99ade3553e2754a06c1b0add52549e2f53dbcdb0ab15f018`
- runner／artifact SHA-256:
  `8c2757c4c3771007dc15135bc407551bbef74906294ab897b1a4f251d5abe2ae` /
  `b3c9d99088492bf157cbb651d958597573a9c7b5386a189b6b9e4ee5d88dbcf5`

### 分析と停止

gapが通ったというcounterfactualでは、external inverseは`4.425423249246816e10`へ下がり、
new totalはQ007o internal inverse`2.1920952274236575e11`、改善率は`125.28856057411295`、
最大pass候補は`1e-16`となる。しかしvalidityとphase hypothesisが落ちたため、これらを認証結果へ
採用しない。登録thresholdを事後に緩めず、Q007oの`1e-18`と全下流結果を維持する。

次はoriginal asymmetric discsまたは明示的にinflated product-factor upperを使う別gateとする。
external bottleneckを外すcritical gapをQ007o internal inverseから先に導き、その閾値を固定してから
再評価する。Fourier wave-sum restrictionを追加する場合も別の事前登録事項とする。

## 2026-08-09: Q007ad asymmetric-disc critical phase certificate

### 問いと事前登録

Q007acのinvalid結果を変更せず、Q007h1 original asymmetric selected discsでexternal-output
resolvent bottleneckを外せるかを問うた。Q007n \(\beta_*\)とQ007o internal inverseからcritical gap
`2.0188097642308912e-8`をexactに導き、targetを`2.1e-8`へ固定した。これはQ007acの
失敗を観測した後のfollow-up certificateであり、独立な探索仮説ではないことも事前登録した。

### 実装

- Q007ac artifact／runnerとinvalid outcome、input／result／phase digestを封印入力として再現した。
- selected 2 representativeの6 eigenvalue centerをexact dyadicへ戻し、Q007h1 Bauer--Fike radiusを
  inflationなしで使用した。全discはQ007n working \(\sigma\)内にあり、minimum slackは
  `7.672593033162951e-81`だった。
- target 630 discs、2,919,730 aggregate、826 dangerous aggregate、108,273 expanded product、
  287,929 comparisonをQ007acと同じ順序で再構成した。
- original acoustic +/- centerとshear centerを用いてphase productをexact dyadic arithmeticで作り、
  Q007n \(\sigma^{n-1}\) telescoping uncertainty、external radius、256-bit outward thresholdを
  含む平方距離比較を全件実行した。
- Q007oのinternal／zero inverse、全majorant、119候補を変えず、旧recordをexact再現してから
  external inverseだけを差し替えた。

### 結果

validity `6/6`、hypothesis `5/5`で`accepted`となった。

1. 全287,929 comparisonがtarget `2.1e-8`をstrictに通過した。
2. 最小witnessはQ007acと同じdegree `71`、counts `(24,38,2,7)`、
   acoustic split `(12,12,1,1)`、external
   `wave=(-7,-7);eigenvalue_index=6`だった。
3. certified complex distance lowerは`2.4028364427409988e-8`、
   minimum squared marginは`1.364447467611938e-16`だった。
4. working external inverseは`2.107344404403246e11`となり、Q007o internal upper
   `2.1920952274236575e11`を下回った。new totalはinternal-limitedで、改善率は
   `125.28856057411295`となった。
5. radius scanは`1e-16`を最大pass、`1e-15`を直前のfailとして再現した。

- input／result digest:
  `b1b1b2750e871c6ee3b243f7df590ec19dd6d604d9699f183af007b89d0f7935` /
  `f5df89c55a86978c85542eeec82e6419884b69b919c0385ca77e9677b1c1d17f`
- phase comparison digest:
  `086516b273f30d7c94c276399c16f8a6433bd90e3dc03fb740d2ab45754e4a37`
- runner／artifact SHA-256:
  `3ca5e39c3ddb79c886ef7bf4d6e6ad923deb66e53da3663251f183abbab7b0ae` /
  `6a6f642cb681409ca160773180e025c1ffbc1929d6ec84423c384c57007571e4`

### 解釈と境界

固定17²・固定保存量葉・固定modal／Wiener normで、Q007i analytic manifoldのexplicit modal
\(\ell^1\) radiusを`1e-16`へ改善した。Q007acの`1e-7` claimはinvalidのままであり、
Q007ad targetをoptimal gapとは解釈しない。

Q007p--Q007abのfinite tube、positivity、MPFR、forward-shadowingは`1e-18`を前提とする
別certificateなので変更しない。次のanalytic-radius bottleneckはQ007o selected-output internal
inverseである。下流tubeの拡大も、internal phase refinementも別gateで事前登録する。

## 2026-08-09: Q007ae phase-aware selected-output internal resolvent

### 問いと事前登録

Q007o internal inverseを支配したglobal gapのQ007i witnessを再確認すると、degree `51`、
counts `(1,19,27,4)`、external `wave=(-2,-2);eigenvalue_index=(8,7)`で、
selected outputではなかった。そこでQ007o 2 representativeの12 external coordinate point
centersだけを位相付きで比較した。target gapは探索せずQ007adと同じ`2.1e-8`、
Fourier wave-sum restrictionはunusedと事前登録した。

### 実装

- Q007ad artifact／runner、accepted outcome、input／result／phase digestを再現した。
- Q007ad original asymmetric 6 discsとQ007n working \(\sigma\) product uncertaintyを再利用した。
- Q007o axial／diagonal source blockのexternal index
  `(2,3,5,6,7,8)`／`(2,3,4,5,7,8)`から12 exact dyadic point centersを作った。
- target residualはQ007o \(\gamma_k\)で扱うためtarget radiusを0とし、Bauer--Fike radiusとの
  二重計上を避けた。
- 2,919,730 aggregateをscreenし、81 dangerous aggregate、15,773 expanded product、
  19,870 comparisonをexact dyadic arithmeticで完走した。
- phase gap通過後、Q007o numerator／\(\gamma_k\)を固定して
  \(N_k/(\delta_{\rm ae}-\gamma_k)\)を再評価し、Q007ad external、Q007n zero、majorant、
  119候補を変えずに再走査した。

### 結果

validity `6/6`、hypothesis `5/5`で`accepted`となった。

1. 19,870 comparisonのfailは0だった。
2. minimum witnessはdegree `63`、counts `(1,39,17,6)`、
   acoustic split `(0,1,3,14)`、target
   `selected_output_wave=1,0;external_index=6`だった。
3. certified complex distance lowerは`5.228929928706603e-4`で、登録`2.1e-8`を
   大幅に上回った。ただし登録gapは事後変更しない。
4. axial／diagonal working internal upperは
   `1.0192745414727758e9 / 1.6818752065691547e9`となり、zero-wave upper
   `6.2060607588672085e9`をともに下回った。
5. new totalはQ007ad external upper`2.107344404403246e11`に支配され、改善率は
   `1.0402168828423712`だった。
6. 最大pass candidateは`1e-16`、直前の`1e-15`はfailのままで、decimal-grid
   radiusのstrict improvementはなかった。

- input／result digest:
  `23fba479cfa07ec50721d9b05bcaf40a0ac04126497ff64b04785e1d20534e0e` /
  `3e1792c5215952d9126bf5bd61409a2a0d72ebc12970ad1e4aaca481d4fcb687`
- phase／selected-center certificate digest:
  `4aea091076179e7ef8eb14c9c4828b41d6af3ef25665e5b2dbbf562acf692b3b` /
  `3cc524ebb82c3e375bf35d456f96be11fa5d124728873046ed59a7032a2058d7`
- runner／artifact SHA-256:
  `f2e0d90ae6bb5f9694c799d2ea850a014f66f2ab9681d94dc1c850cc753db600` /
  `c6d28bba13fcf831dfccaf03854072256f7e8ff1a241b54aaf84552dd06a2a55`

### 解釈と次のbottleneck

selected-output internal blockはtotalの支配要因から外れた。新しいanalytic bottleneckはQ007ad
nonselected-output external inverseである。Q007aeは`1e-16` radiusを維持するが拡大しない。
Q007p--Q007ab tube／MPFR定数も変更しない。external gap sharp化、連続radius最適化、下流tube
再監査のいずれも別の事前登録を必要とする。

## 2026-08-09: Q007af sealed external phase-disc radius-step obstruction

### 問いと事前登録

Q007ae後のexternal bottleneckを同じQ007ad original-disc family内でsharp化すれば
`1e-15` candidateへ届く余地があるかを、位相比較の再探索前に判定した。Q007n scalar
majorant、Q007ad discs／norm formula、Q007ae inverse orderingを固定し、次を事前登録した。

1. Q007n `_candidate_record`へpair inverse \(C\)だけを入れ、
   \([1,10^{13}]\)のexact integer bisectionで`1e-15` pass／fail境界を挟む。
2. 予備的exact algebraで得たbracket
   `173791195571 / 173791195572`を結果前に封印する。
3. external inverse formulaからfail側端点に対応する必要gap
   \(\delta_{\rm req}=81\beta_*/173791195572\)を使う。
4. Q007ad minimum-margin witnessを固定し、保存centerからdistance squaredを再構成する。
5. witnessの許容gapは保存lowerではなく100桁`isqrt` enclosureのupperから評価する。

### 実装

- Q007n／Q007ad／Q007ae artifact 3件と、Q007ac／Q007ad／Q007ae／Q007n／Q007o
  implementation 5件のSHA、scope、accepted outcome、封印digestを再現した。
- Q007aeの13 working coefficients、inverse ordering、119 candidate records、
  `1e-16 pass / 1e-15 fail`をexactに再現した。
- integer bisectionを44回完走し、隣接する整数端点を得た。
- positive domainではstate majorantとcomposition numeratorが増加し、bufferが減少するため
  derivative majorant \(D(C)\)は非減少、\(Z(C)=CD(C)\)はstrict増加することを符号と
  exact endpoint identityで監査した。domain外はbuffer gateでfailする。
- radii marginがexactに \(CT(1-2Z)\)であることを両端で確認した。
- fixed witnessのcenter distance squared、product uncertainty、external radiusをexact再構成し、
  required gapをthreshold roundingなしで直接比較した。

### 結果

validity `6/6`、hypothesis `5/5`で、
`sealed external phase-disc family cannot certify the 1e-15 radius step`
というnegative obstructionを`accepted`とした。

1. maximum passing／minimum failing integer inverseは
   `173791195571 / 173791195572`だった。
2. 両端の \(Z\) は
   `0.4999999999994811 / 0.5000000000023581`、
   radii marginは
   `9.35528407264837e-68 / -4.2513570828920896e-67`だった。
3. 必要external gap lowerは`2.546402442702229e-8`だった。
4. Q007ad fixed witnessのsqrt-upper allowable gapは
   `2.4028364427409988e-8`で、required ratioは
   `0.9436200666659436`、shortfallは
   `1.4356599996123017e-9`だった。
5. required gapでのexact squared marginは
   `-7.109332998428586e-17`で、outward threshold roundingなしでもfailした。
6. allowable gap upperを楽観的に使うraw external inverse floorは
   `1.841749679890231e11`で、failing端点の
   `1.059748552755201`倍だった。

- integer-bisection digest:
  `24b0e993f676082579158cfeddfe74009161d72412bf228f715baa396246c31b`
- input／result digest:
  `6cfeabe16a18fdb6de08e67c575a0b0db2f3ab1341c35c434faff100fd959255` /
  `3d210cf25513e373ac6a2e7a276163998a602c529878f3c95f085c9e0625bfdd`
- runner／artifact SHA-256:
  `819679b22d7552a3f247d7c3389a83890f56c60522154bdb5ea05d7eb77a48a4` /
  `a686526552c33f5f1f01a9f1d9c49036d1c9491a2092b07ac8c8621a33d4ada1`

### 解釈と次のbottleneck

同じQ007ad disc family内でgapを少しずつ上げても、Q007n scalar majorantの次の10進radiusへは
届かない。従ってこのmicro-sharpening branchは停止する。ただしこれは真のspectral separationや
analytic radiusの上限ではなく、wave-sum、blockwise majorant、別norm、別spectral enclosureを
排除しない。

Q007aeの`1e-16` analytic radiusとQ007p--Q007abの`1e-18` tube／MPFR定数は
ともに維持する。次はexternal certificateを同じ形でsharp化せず、認証済み`1e-16` chart
domainをQ007p-style finite-tube boundへ渡す下流再監査を別gateとして事前登録する。

## 2026-08-09: Q007ag Q007ae analytic radiusのfinite-tube伝播

### 問いと事前登録

Q007aeのaccepted \(10^{-16}\) chart radiusをQ007p／Q007s finite-tube majorantへ伝播したとき、
旧Q007s tubeのbase／normal両半径をstrictに拡大できるかを問うた。変更を\(\rho,\tau\)の2定数に
限定し、base gridだけをexactに100倍、normal gridを不変にした9×99候補と選択境界を事前登録した。

1. Q007p／Q007s／Q007ae／Q007af artifactと6 runner／implementation SHAを封印する。
2. Q007s old 891 candidate、676 pass、digest、selected boundaryをexact再現する。
3. Q007aeの119 radius recordと`1e-16 pass / 1e-15 fail`をexact再現する。
4. \(\rho=10^{-16}\)、\(\tau=2.186110822784426\times10^{-60}\)だけを更新する。
5. 予備exact evaluationで得た757 pass、selected
   \((r,\zeta)=(9\times10^{-17},5\times10^{-11})\)を結果前に固定する。

### 実装

- Q007s `_evaluate_candidate`を変更せず再利用し、全候補を`Fraction` signsで判定した。
- Q007s old cycleをfresh replayし、候補数、pass数、candidate digest、selected点、全gateと
  selection boundaryをartifactへ照合した。
- Q007ae radius searchをfresh replayし、119 records、boundary、\(\rho,\tau\)を照合した。
- Q007p／Q007s定数の差分を監査し、変更名がexactに`rho / tau`だけであることを確認した。
- scaled 9×99 Cartesian gridの一意性、全6 gate、lexicographic selectionを完走した。
- input／candidate／resultをcanonical digest化し、全出力をfinite strict JSONとして保存した。

### 結果

validity `6/6`、hypothesis `5/5`で、
`Q007ae analytic radius enlarges the registered external-coordinate tube`
として`accepted`とした。

1. Q007s old 891 candidate／676 passとQ007ae 119 radius recordをexact再現した。
2. new gridでは891候補中757個がpassした。
3. selected tubeは
   \((r,\zeta)=(9\times10^{-17},5\times10^{-11})\)で、Q007s比`100 / 10`だった。
4. selected state Wiener upperは`1.4441361143956586e-10`、base imageは
   `8.995021185299983e-17`、base forward marginは`4.978814700017615e-20`だった。
5. normal contraction／tangent conorm／domination ratioは
   `0.9817100978829438 / 0.9837709569923392 / 0.9979051433722989`だった。
6. first larger normal `6e-11`はbase forward margin
   `-2.4132428529856413e-19`で、`base_forward_invariance`だけをfailした。

- input／candidate／result digest:
  `262cbeccacf858bd798de06f363635f15c78ff3d361b44bdd5850aeb90679613` /
  `a7a6a8f605339b0e8ffd16a5d3190967cb7329771d322f8edc0a53bc4b45e408` /
  `6f52c6f1cfa618ca881439504f1bd5b46e45eb245670f1a2c6341669aa024f43`
- runner／artifact SHA-256:
  `bafd9a56d2d2ceb94acb709609bd710c9fff0f6c0bf543202fa411b9456fb6e0` /
  `5783df74abb4b6ec7d658fd7e3dd272cf100cd134783c31863d643fcd17d4200`

### 解釈と次のbottleneck

認証済みanalytic chart domainの拡大は、同じexternal-coordinate majorant上で有限tubeの両半径へ
実際に伝播した。ただしbase grid上端を選んだためcontinuous maximumではなく、Euclidean／grid-uniform
attraction、global basin、continuum limitも示さない。

Q007t／Q007u positivityとQ007v--Q007ab finite-precision certificateは旧Q007s tubeに封印されている。
次は新Q007ag tubeのfull-map population positivityを独立gateで監査し、その後にstagewise positivityを
別gateとして扱う。有限精度定数は両positivity gateが通るまで拡張しない。

## 2026-08-09: Q007ah Q007ag tubeのfull-map population positivity

### 問いと事前登録

Q007ag selected tubeをfull one-step mapの入力／出力時刻でstrict positive D2Q9 population coneへ
含められるかを問うた。Q007ag／Q007t／Q007pを封印し、exact Wiener upperから
\(p_{\rm ag}=1/36-x_{\rm ag}\)、\(d_{\rm ag}=1-x_{\rm ag}\)を`Fraction`で判定するよう登録した。
内部stageは対象外とし、Q007aiへ分離した。

### provenance訂正

最初のinput-only実装監査は、Q007t artifactにraw-byte SHA
`de5ee6db33e06459c64e5cea92b206673938d5f8d6fef948e5b4496dcca92283`を登録したためvalidityで停止した。
既存Q007t／Q007u封印と研究ログにあるnewline-normalized SHA
`2089d97aa19248cc17689f3e7a01e113540e5afc329ffa5cb3a4c511a43a8529`へ、結果採用前に訂正した。
artifact内容、runner、数値bound、成功条件は変更していない。

### 実装

- Q007ag stored cycleをfresh replayし、3 digest、selected tube、6 candidate gate、forward invarianceを再現した。
- Q007t old population oracleをfresh replayし、weight table、Wiener triangle、old exact boundを再現した。
- 現行D2Q9 weight tableを独立に`Fraction`化し、multiplicity、sum、minimum／maximumを監査した。
- Q007pの289 wave、block-sum norm definition、real conjugacy constraintを直接照合した。
- exact state upperからpopulation／density boundsを再構成し、input／result digestを保存した。

### 結果

validity `6/6`、hypothesis `3/3`で、
`registered Q007ag propagated tube lies in the strictly positive population cone at every full-map iterate`
として`accepted`とした。

- tube state Wiener upper: `1.4441361143956586e-10`
- population lower／upper:
  `0.027777777633364167 / 0.44444444458885807`
- density lower: `0.9999999998555864`
- D2Q9 weight multiplicities／minimum: `1 / 4 / 4`、`1/36`
- Fourier wave count: `289`
- input／result digest:
  `6d7bd69b5c90ff7dbabd5193a4536809f4b79eef36a41fb288ab7caec44321b4` /
  `caea5280667e909f17922260ef0d78998b6a8b374cd048b4b3e526185f040921`
- runner／artifact SHA-256:
  `f29a974f0219af1767140e977775aa95dcf22b41a36de7a97bb553d540968d27` /
  `cab5ecc090b794a21a21fded8e5c503eca40be2bbc6502767c29844ba8209fa9`

### 解釈と次のbottleneck

Q007ag forward invarianceにより、同じstrict lower boundをexact full-mapの全入力／出力時刻へ帰納できる。
しかしequilibrium evaluation、BGK collision、streaming、filterの各内部stageはこの結論に含まれない。
次はQ007aiで同じnew tubeのexact stagewise positivityだけを監査する。entropy、maximum principle、
IEEE-754 roundoff、Q007v--Q007ab finite-precision inductionもまだ拡張しない。

## 2026-08-09: Q007ai Q007ag tubeのexact stagewise positivity

### 問いと事前登録

Q007ahでfull-map時刻のpositivityを認証したnew tubeについて、exact equilibrium／collision／streaming／
filter各stageでもstrict positivityを維持できるかを問うた。Q007ah／Q007uと現行D2Q9／filter sourceを
封印し、Q007uと同じoperator norm、nonlinear majorant、stage structureを新しい\(x_{\rm ag}\)へ評価した。

### 実装

- Q007ah stored cycle、2 digest、tube state identity、forward invarianceをfresh replayした。
- Q007u old stagewise cycle、全gate、operator／majorant／structure、old boundsをfresh replayした。
- current D2Q9／checkerboard-filter source SHAを照合した。
- exact \(M,E,EM,C\)、nonlinear constants、9 streaming bijection、convex filterを再構成した。
- 全stage boundを`Fraction`で計算し、事前登録float表示とinput／result digestを照合した。

### 結果

validity `6/6`、hypothesis `5/5`で、
`registered Q007ag propagated tube is population-positive at every exact BGK, streaming, and filter stage`
として`accepted`とした。

- state upper／density buffer:
  `1.4441361143956586e-10 / 0.9999999998555864`
- equilibrium nonlinear／deviation／population lower:
  `1.459870382042079e-19 / 3.1289615826504644e-10 / 0.02777777746488162`
- collision nonlinear／deviation／population lower:
  `2.1898055730631184e-19 / 4.5730976977760583e-10 / 0.027777777320468006`
- streaming／filter population lower:
  `0.027777777320468006 / 0.027777777320468006`
- input／result digest:
  `0dff47e8b0ed6e9b87cb73e6dea20192088495b51283c57b9d58630b7344c6a3` /
  `c101313957c738ccee9fd3d7f1ed36b77c6f3dad4e1130651f5be4d8757ef18a`
- runner／artifact SHA-256:
  `3235b2dc31445e5912f2aaf7fc080e8295035801ade9b27d3f683d34da61173d` /
  `3ce5fa6358eaa6f3a64f93fe773e3fbc1990abfb83886aad1a4ade9c82425804`

### 解釈と次のbottleneck

Q007ag forward invarianceにより、4 stageのstrict lowerをexact mapの全iterateへ再適用できる。
Q007ahで残ったexact内部stageの穴は閉じた。次はQ007ajでcurrent binary64 one-step演算を同じnew tube上で
囲う。stage positivityとroundoff-robust tube re-entryは別のhypothesisとして維持し、後者がfailしても
前者を有効な結論として残す。

## 2026-08-09: Q007aj Q007ag tubeのcurrent binary64 one-step enclosure

### 問いと事前登録

Q007aiでexact内部stageまで閉じたnew tubeについて、current NumPy binary64演算の一段stageがstrict
positiveか、さらにpost-filter roundoff error upperがQ007agのbase／normal strict re-entry marginへ
収まるかを問うた。Q007ag／Q007ai／Q007vとcurrent D2Q9／filter sourceを封印し、stage positivity、
base re-entry、normal re-entryを独立hypothesisとした。re-entryがfailしてもone-step positivityを残し、
全iterateへは帰納しない停止規則を先に固定した。

### 実装

- Q007ag stored cycle、3 digest、selected tube、6 candidate gate、strict margin、forward invarianceをfresh replayした。
- Q007ai stored cycle、2 digest、exact new-tube stage bound、全accepted gate／theoremをfresh replayした。
- Q007v stored cycle、old one-step acceptance／re-entry rejection、binary64 model、Fraction primitive、固定operation
  count、source schedule、deterministic NumPy replayをfresh replayした。
- Q007vのpaired interval engineへnew exact state upperを代入し、全target interval／forward errorを再計算した。
- post-filter component errorを289-wave Wiener upperへ持ち上げ、Q007p selected／external analysis upperを掛けて
  Q007agのbase／normal strict marginとexact Fractionで比較した。

### 結果

validity `7/7`が通過した。hypothesisはstage positivity 5件がpassし、base／normal re-entry 2件がfailした。
従って`one_step_outcome=accepted`、`robust_reentry_outcome=not_certified`、overallは
`binary64 one-step stages remain positive, but the registered Q007ag tube is not certified roundoff-invariant`
という有効な`not_certified`とした。

- input state Wiener upper: `1.4441361143956586e-10`
- equilibrium／collision／streaming／filter population lower:
  `0.02777777759726066 / 0.027777777145968068 / 0.027777777145968068 / 0.02777777714596806`
- maximum equilibrium／collision／filter component forward error:
  `7.154770620135027e-16 / 1.2459169528232512e-15 / 1.350123719783517e-15`
- post-filter component-error sum／Wiener error upper:
  `4.036979113491066e-15 / 1.1666869637989181e-12`
- base coordinate error／margin／utilization:
  `1.7624955732793895e-12 / 4.978814700017615e-20 / 35399902.97837664`
- normal coordinate error／margin／utilization:
  `3.490393287849664e-11 / 9.144951058528087e-13 / 38.16743540245316`
- input／result digest:
  `040bf7e2c62094ea66a4cf8a6190ea78e53745e30c70a3b3ce856a7e4d1c5284` /
  `517846a3a99f1e684f40c2ea6d5a8ae7b3db8c0849dae3097fc7f380f4eca923`
- runner／artifact SHA-256:
  `e91cd0740ca9d639f6eaeeea8ed71552a0323897f45eee50070f4c8cdf947ac5` /
  `29b8cd320f40396cc24ae30b46e46eecc7e23564600284aeb916a90af3a1fd8e`

### 解釈と次のbottleneck

new tubeでもcurrent binary64の一段内部stage positivityは大きな余裕で成立した。しかしroundoff upperは
base marginを約3540万倍、normal marginを約38.17倍上回る。旧Q007v比ではmargin拡大によりutilizationが
base約100分の1、normal約10分の1へ改善したが、all-iterate再入にはなお不足する。

これは実際のtrajectory escapeや反例ではなく、component box、Wiener triangle、global analysis norm、
局所roundoff accumulationをまとめた固定worst-case certificateの失敗である。Q007akでは4因子を分離し、
どこを改善すれば再入thresholdへ届くかを定量化する。Q007akまではnew-tube MPFR／repair／shadowingへ進まない。

## 2026-08-09: Q007ak Q007ag re-entry obstructionの4因子分解

### 問いと事前登録

Q007ajのbase／normal failureをstrict margin、analysis upper、289-wave Wiener lifting、post-filter local
component-error sumへexact分解し、単独因子の必要改善率を求めた。加えてQ007wのsealed ideal-binary
evaluatorをnew tubeへ移し、53--128 bitの全整数候補からbase／normal／joint first-passを独立に選ぶよう
登録した。\(p=53\)はQ007ajの全target／error recordとsplit outcomeをexact再現することを必須とした。

### 実装

- Q007aj stored cycle、2 digest、5-pass／2-fail hypothesis、全stage／re-entry quantityをfresh replayした。
- Q007w stored cycle、old 85-bit boundary、76候補digest、ties-to-even／p53 controlをfresh replayした。
- \(U_X=K_XNE_{53}/m_X\)とlocal-error／analysis／wave／marginの4 boundary identityを`Fraction`で再構成した。
- counterfactual \(N=1\)、\(K=1\)を診断として計算したが、実現可能な新normとは扱わなかった。
- 全76 precisionでoperation count、domain、error monotonicity、stage-lower monotonicityを検証し、3 selection
  boundaryをexactに再構成した。

### 結果

validity `7/7`、hypothesis `7/7`で、
`registered factor audit isolates base re-entry as the dominant Q007ag binary64 obstruction`
として`accepted`とした。

- binary64 base／normal utilization: `35399902.97837664 / 38.16743540245316`
- maximum local component error at boundary:
  `1.1403927055836785e-22 / 1.0577024814278182e-16`
- maximum analysis factor at boundary:
  `4.26748121347461e-08 / 0.7838393109965568`
- maximum wave factor at boundary:
  `8.163864182806664e-06 / 7.5718998919540965`
- unit-wave base／normal utilization:
  `122491.01376600914 / 0.13206725052751958`
- unit-analysis base／normal utilization:
  `23433026.41479689 / 1.2757716868379836`
- minimal sufficient ideal precision base／normal／joint: `79 / 59 / 79`
- base boundary `p=78 / 79` utilization: `1.049142142753718 / 0.5226851687280066`
- normal boundary `p=58 / 59` utilization: `1.1922608315359098 / 0.5970734654373829`
- input／candidate／result digest:
  `333ce7e6b4537947808a369f1c218c2d930a11df4b826994df0947fa42489d46` /
  `eacc824a8f0fc891971c210883d05f7178e4fe5848ab3b2432dc94adf289e567` /
  `a4d10df4c1d6edd83488115d501af21ad6727dd6321e159e37b2b0e434858644`
- runner／artifact SHA-256:
  `c8bb3f7a84d19d9ab2794d9a1c27334ecd53e62dabce7862343b51ef30cd29b1` /
  `aae6b560125cd29dad5b87bf20e9806ae26a5b1b6ae2ee9c055580042561cf7c`

### 解釈と次のbottleneck

baseはbinary64で約3540万倍超過し、wave factorを反実仮想的に1へ下げても約12.2万倍超過する。
normalはbinary64で約38.17倍だが、unit-wave counterfactualでは0.132へ下がる。precision boundaryでも
normalは59 bit、base／jointは79 bitなので、固定enclosureの支配障害はbase coordinateである。

joint ideal threshold 79は既存MPFR-85 precision以下だが、これはimplemented backendの証明ではない。
次はQ007alでQ007xのconcrete MPFR-85全演算traceをnew tube上へ一段だけ再適用する。fixed-leaf closure、
repair、all-iterate induction、same-initial shadowingは別gateに残す。

## 2026-08-09: Q007al Q007ag tubeのconcrete MPFR-85 one-step bridge

### 問いと事前登録

Q007akでjoint ideal sufficient thresholdが79 bitsとなったため、既存Q007x MPFR-85 backendを
変更せずnew Q007ag component boxへ再適用した。一段stage discrepancy／positivityと、ideal
85-bit base／normal complement-coordinate error budgetを独立hypothesisとした。Q007xの
fixed-leaf defectは診断としてexact再現するが、acceptance hypothesisには入れないと先に固定した。

### 実装

- Q007ak stored cycle、3 digest、7+7 gate、79／59／79 boundary、$p=85$ candidateをfresh replayした。
- Q007x stored cycle、probe／trace／result digest、8 validity、2-pass／4-fail hypothesis、runtime／source／
  context／conservation結果をfresh replayした。
- sealed Q007w evaluatorでnew-tube $p=85$ candidateをexact再評価し、stored candidateと比較した。
- 同じ4 exact probeで各70,824 operationをties-to-even oracleと照合し、exact Fraction mapとの
  stage discrepancyをnew 85-bit boundと比較した。
- Q007xのconservation recordとobserved stage recordが変更されていないことを独立回帰にした。

### 結果

validity `8/8`、hypothesis `5/5`で、
`registered MPFR-85 backend realizes the Q007ag one-step arithmetic and complement-coordinate error budgets`
として`accepted`とした。

- probes／trace: `4 / 70,824 per probe / 283,296 total`
- trace mismatch／operation-domain failure: `0 / 0`
- post-filter component-error sum／Wiener error upper:
  `9.365881800643092e-25 / 2.7067398403858536e-22`
- base error／margin／utilization:
  `4.08902913525762e-22 / 4.978814700017615e-20 / 0.008212856636827946`
- normal error／margin／utilization:
  `8.097790464783468e-21 / 9.144951058528087e-13 / 8.8549303467643e-09`
- maximum concrete stage-bound utilization: `0.15250294771440714`
- minimum observed concrete stage population: `0.027777777777759027`
- conservation:
  encoding `fail` / collision `fail` / streaming `pass` / filter `fail` / full step `fail`
- input／candidate／probe／trace／campaign-result／result digest:
  `e14b6251a0f5da2ad4c73c1b08c5e21205e99749917f3f78228de6bb12b13738` /
  `7b63d94121aea24e589ed3e7b221e154705f42df37c4c603c3f99a4a3b1799c0` /
  `a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329` /
  `49ce9b304b4b6a07fdf7d7baed6c9118a97c5a08e489e3aa5eacde28662c2351` /
  `edbfbe317f2254f3d6a628608a19b4986f7ea308cae889d19ce470f31234dad5` /
  `a46f4850d57b0e7d503177205c2cb3d1ed91679cc4c13b9ef31382dbd7bdcd06`
- runner／artifact SHA-256:
  `b82e03145e0c7f1c20b1d1345b87acbae5ce526b732969c391b88141118dfd8e` /
  `bf1a2d9959f24cfc83a4efb2926ec76d9ced97755846ee310490585940d8dcf5`

### 解釈と次のbottleneck

fixed MPFR-85 backendはnew tubeの一段算術包囲を実現し、両complement-coordinate marginに十分な
余裕がある。しかしcomponentwise encoding／collision／filterのexact conservation failureも
Q007xどおり再現した。従ってactual rounded stateはfixed leafに属さず、Q007ag tube re-entryや
all-iterate invarianceをここから帰納しない。これは一段算術bridgeの成功とfixed-leaf closureの未解決を
分離した結果である。次はQ007amでnew-tube repairとその追加誤差を別途判定し、
all-iterate induction／same-initial shadowingはさらに後続gateへ残す。

## 2026-08-09: Q007am propagated tubeのdistributed fixed-leaf repair

### 問いと事前登録

Q007alのMPFR-85一段包囲は通過したが、componentwise rounding後stateはfixed leafから外れた。
そこでQ007yと同じ\(h=2^{-90}\) diagonal dyadic repairを変更せずQ007ag component boxへ移し、
fixed-leaf closure、tube-wide well-definedness、修復込みbase／normal一段予算を独立に判定した。
Q007ag exact invarianceとの自己写像合成、all-iterate induction、initialization、shadowingはこのgateに
含めないと事前登録した。

### 実装

- Q007al accepted cycleとQ007y mixed cycleをartifact／runner SHA、全gate、digestごとfresh replayした。
- Q007alのfresh \(p=85\) component boundsへQ007yの`_tube_stage_repair_bound`をそのまま適用した。
- input encodingとpost-filterについてHadamard integer solution、balanced distribution、lattice／parity／
  binade、最大site correctionをexact rationalで再監査した。
- 4 exact probeでinput repair、raw MPFR-85 map、output repairを実行し、保存量、operation exactness、
  positivity、registered component enclosureをQ007y campaignとbitwise／exactに回帰した。
- coarse Wiener triangle boundだけを使い、Q007zのphase-aware selected-wave cancellationは導入しなかった。

### 結果

validity `8/8`、hypothesis `7/7`で、
`distributed MPFR-85 repair restores the Q007ag fixed leaf and fits both registered one-step budgets`
として`accepted`とした。

- input repair \(\ell^1\) upper／maximum site correction:
  `1.2452407121655381e-23 / 4.362085261510107e-26`
- raw／repair／total post-filter Wiener upper:
  `2.7067398403858536e-22 / 4.959477728036884e-22 / 7.666217568422737e-22`
- repaired／raw ratio: `2.8322698229209555`
- repair-aware base error／margin／utilization:
  `1.1581233824834727e-21 / 4.978814700017615e-20 / 0.02326102601246388`
- repair-aware normal error／margin／utilization:
  `2.2935127565743277e-20 / 9.144951058528087e-13 / 2.5079552005207522e-08`
- finite campaign: 4 probeともinput／output fixed-leaf restoration、exact repair operation、
  backend domain、positivity、component enclosureが通過した。
- input／probe／finite-result／result digest:
  `f1a0dfd0b90cf354e9847cb076058fd241ab813a90bdee0bfdbafa9dfee17de5` /
  `a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329` /
  `905b65f13ee01711f3b083a0bd93e44b32d0fc5201007fad77e99de03063ab6d` /
  `2217172b48bf86b987a316c9b8c14db6aaeceb3e50f304fa7fefb021c2fd5bd2`
- runner／artifact newline-normalized SHA-256:
  `a0bdebc150c4c3ad055e1840b98196dee95bf967c417d17097f7a35579f2aa16` /
  `3b1b6f3c839cec572d0279f41c158dfafa09088e5f8ee1c3eab84f5bd279b781`

### 解釈と次のbottleneck

old Q007y tubeでは修復込みbase budgetが2.326倍超過したが、Q007agの縮小boxでは同じcoarse
repairを含めてもbase margin使用率は0.0233、normalは約\(2.51\times10^{-8}\)である。従って
fixed-leaf repair feasibilityと両一段予算は共存する。しかしQ007amは、exact-map invariance、
MPFR error budget、repairを一つのrepaired-map tube self-mapへまだ合成していない。次はQ007anで
already-repaired MPFR-85 statesに対するall-iterate inductionを事前登録し、initializationと
same-initial shadowingは別gateに残す。

## 2026-08-09: Q007an repaired MPFR-85 fixed-leaf tube induction

### 問いと事前登録

Q007ag exact forward invariance、Q007ai exact stagewise positivity、Q007al MPFR-85一段包囲、
Q007am distributed repairと修復込み誤差予算を、一つのrepaired sampling map

\[
\widetilde\Psi_{85}=\mathcal R\circ\widetilde\Phi_{85}
\]

のQ007ag tube自己写像へ合成できるかを判定した。初期条件はすでにMPFR-85へencode・repairされ、
fixed leafと登録tubeに属するstateに限定した。任意exact stateからのinitializationとsame-initial
shadowingはこのgateへ含めないと事前登録した。

### 実装

- Q007ag／Q007ai／Q007al／Q007amのartifact・runner SHA、scope、classification、gate count、digestを
  封印し、Q007ag／Q007ai／Q007am cycleとQ007am内のQ007al／Q007yをfresh replayした。
- Q007ag exact strict marginとQ007am登録marginをexact rationalで同定し、raw-map誤差とrepair correctionを
  含むbase／normal誤差を引いた自己写像headroomを再構成した。
- Q007ai exact stage lower、Q007al MPFR-85 stage lower、Q007am post-repair same-binade positivityを
  同じcomponent box上の連続stageとして照合した。
- fixed leaf上のzero-defect repairが289-site distributionを含めてidentityであることを一般に示し、
  `rest` probeではrepairの冪等性もexactに回帰した。
- finite 4-probeは実装回帰だけに使い、自己写像と帰納はtube-wide exact-rational boundから導いた。

### 結果

validity `7/7`、hypothesis `7/7`で、
`coarse repair certificate closes the Q007ag repaired MPFR-85 fixed-leaf tube induction`
として`accepted`とした。

- exact base／normal strict margin:
  `4.978814700017615e-20 / 9.144951058528087e-13`
- repair-aware base／normal error:
  `1.1581233824834727e-21 / 2.2935127565743277e-20`
- repaired-map base／normal headroom:
  `4.863002361769267e-20 / 9.144950829176811e-13`
- exact／MPFR-85 minimum internal-stage population lower:
  `0.027777777320468006 / 0.027777777145968227`
- repaired diagonal population lower: `0.015625`
- input／composition／result digest:
  `7d93718b4e8375ea3983c37042d0aaedc98f4a16a329687afa69f75511e29657` /
  `7ce1bde2ddc99ace52610c1a814a65dada1711baf048ec5410241ce497f809d7` /
  `80bae2065ec27d22c7e5a392f764e422ef57d521e0848d6c9eae3e0ed07e8bf7`
- runner／artifact newline-normalized SHA-256:
  `bacf2eca47348ebbb5f5fbfe739f3239ebdb49eedc0d615efc144eb113b5f1bf` /
  `dd28dc89f2096252db80e2ad7461ebdf71bb757e879b8657df01da766849ebdb`

### 解釈と次のbottleneck

already encoded and repaired MPFR-85 stateがQ007ag fixed-leaf tube内にあるなら、各sampling timeで
fixed leafとtube membershipを保ち、各stepの内部stage population positivityも全iterateへ帰納できる。
これはQ007amの一段予算をexact-map invariant tubeへ初めて閉じた結果である。

一方、任意exact stateのcomponentwise encoding／input repairがこの初期集合へ入ることは未認証であり、
same-initial exact軌道とのshadowingも主張しない。次はQ007aoでstrict inner exact-state setからの
initialization interiorだけを独立に事前登録する。

## 2026-08-09: Q007ao propagated tubeのexact-state initialization interior

### 問いと事前登録

Q007anの条件付き帰納へexact-state initializationを接続するため、fixed leaf上のstrict inner set

\[
\lVert a\rVert_1\le8.9998\times10^{-17},\qquad
\lVert z\rVert_*\le4.999999999\times10^{-11}
\]

を事前登録した。内側半径はQ007aaの値をQ007ag tubeのbase／normal拡大率100／10で写した。
componentwise MPFR-85 encodingとQ007y row-major input repair後にQ007ag outer tubeへstrictに入るかだけを
判定し、same-initial shadowingは含めないと固定した。

### 実装

- Q007ag／Q007am／Q007an artifact・runner SHA、scope、classification、gate count、digestを封印した。
- Q007an stored cycleをfresh replayし、そのtransitive Q007ag／Q007ai／Q007amと、Q007am内の
  Q007al／Q007y reproductionまで通した。
- Q007am input-encoding boundからraw／repair physical Wiener errorをexactに再構成し、Q007amの
  selected／external analysis upperとQ007ag selected candidateのchart derivativeを再利用した。
- base shiftをK_L E_W、normal shiftをK_a(E_W+d_H(r) epsilon_a)でexact rational評価した。
- center cancellation、spatial Fourier phase、Q007z selected-wave boundは使わなかった。

### 結果

validity 7/7、hypothesis 6/6で、
「registered propagated-tube exact-state interior survives MPFR-85 encoding and repair」
としてacceptedとした。

- raw／repair／total input Wiener upper:
  7.470474916829075e-24 / 1.2452407121655381e-23 / 1.9922882038484456e-23
- base increment／inward margin／headroom／utilization:
  3.009718329710275e-23 / 2e-21 / 1.969902816702897e-21 / 0.015048591648551374
- direct external／graph-shift／total normal increment:
  5.960355768038905e-22 / 9.362725402249564e-36 / 5.960355768038998e-22
- normal inward margin／headroom／utilization:
  1e-20 / 9.4039644231961e-21 / 0.05960355768038998
- tight base／normal initialization radius:
  8.99999699028167e-17 / 4.9999999999403966e-11
- input／bound／result digest:
  4793702239a7bc6252b71b5fff43cc68e78dcad1d1b9446db94544b85270deb3 /
  b747e0a635cf4d747728fd5447e613b62a0b951813634f8a98c9e80a17f3308a /
  6c2a41f2ff2d610d8f542cb132a50a678298098245063d54bcd2a38b6e6a8360
- runner／artifact newline-normalized SHA-256:
  2cd4c852c2855b93efaeb618bc3b1cb488885375c69f11e2c7624f0ea84614f7 /
  c6262043848a479b90634fc8aa82dbd02bfcaea4bcb3467d240b956fd7602b8f

### 解釈と次のbottleneck

登録inner setのexact fixed-leaf stateは、encoding／repair後にQ007ag repaired tubeへ入り、Q007anと
合成してall-iterate tube invarianceと内部stage positivityへ接続できる。base inward margin使用率は
約1.50%、normalは約5.96%である。

この結論は任意Q007ag boundary stateやarbitrary exact physical stateを初期化できるという主張ではない。
またexact軌道とのtrajectory errorもまだ与えない。次はQ007apでQ007abのfixed-coordinate contractionと
local MPFR defectを新tubeへ移し、same-initial forward shadowingを独立に判定する。

## 2026-08-09: Q007ap propagated-tube same-initial forward shadowing

### 問いと事前登録

Q007ao inner exact-state setの同じfixed-leaf stateから出るexact軌道と、componentwise MPFR-85
encoding／input repair後のsealed repaired軌道を、各repair後のsampling timeで比較する問題を固定した。
trajectory distanceにはQ007abと同じ平衡点固定の線形座標

\[
\mathcal Cx=(Lx,JQx),\qquad
\|\mathcal Cx\|_\oplus=\|Lx\|_1+\|JQx\|_*
\]

だけを使う。Q007ag tube上のexact mapがこのnormでstrict contractionか、Q007ao initial defectと
Q007am one-step local defectを幾何級数で全iterateへ足し上げられるかを判定した。graph-relative
normal contractionはtrajectory normへ代入せず、Q007ao graph shiftもinitial errorへ二重加算しないと
事前に固定した。

### 実装

- Q007ab／Q007ag／Q007am／Q007aoのartifact SHA、runner SHA、scope、classification、gate count、
  全登録digestを封印した。
- Q007abとQ007ao stored cycleをfresh replayした。Q007ao内ではQ007anとそのtransitive
  Q007ag／Q007ai／Q007al／Q007am／Q007y reproductionまで通した。
- Q007abで認証済みのlinear analysis／synthesis constantsと、Q007agの新state radius／nonlinear
  derivativeからfixed-coordinate full-map Lipschitz upperをexact rationalで再構成した。
- Q007ao initial encoding／repair errorをselected＋direct external coordinateへ写した。graph shiftは
  tube membership termとして記録し、線形trajectory errorへは加えなかった。
- Q007am repair-aware base／normal一段誤差をfixed-coordinate local defectとして合成した。
- \(d_{n+1}\le L_\oplus d_n+\epsilon_{\rm step}\) のstationary bound、physical synthesis、
  tube-relative accuracyを全てexact rationalで評価した。

### 結果

validity 7/7、hypothesis 6/6で、
`propagated-tube fixed-coordinate contraction certifies all-iterate MPFR-85 forward shadowing`
としてacceptedとした。

- selected／external linear contraction upper:
  `0.9920954673554099 / 0.981709835832552`
- nonlinear coordinate Lipschitz increment:
  `2.7528278762500916e-7`
- full Lipschitz upper／contraction gap:
  `0.9920957426381974 / 0.007904257361802534`
- initial selected／physical／external／total coordinate error:
  `3.009718329710275e-23 / 1.9922882038484456e-23 /`
  `5.960355768038905e-22 / 6.261327601009932e-22`
- step selected／external／total coordinate defect:
  `1.1581233824834727e-21 / 2.2935127565743277e-20 / 2.4093250948226748e-20`
- stationary／uniform coordinate error:
  `3.0481359405954845e-18 / 3.0481359405954845e-18`
- uniform physical Wiener error／tube-radius ratio:
  `8.803831096064757e-18 / 6.096261293035372e-8`
- registered relative／absolute accuracy threshold:
  `1e-6 / 1.4441361143956587e-16`
- input／recurrence／result digest:
  `06692ce9d11691d2a45cd57220ea3e5e201b5c2beb2d0b55776a60f15456830f` /
  `108cb6d50ecaa2d9ad50c02777f6c0bb03a979903849149e30f686c8004fc1ce` /
  `1ee4dc09badbba0264ccc05317ba87de68557d5df148cb7085b158097d17a910`
- runner／artifact newline-normalized SHA-256:
  `095bd3cf728e916d937df22bf9e6773698801064213cd679af52d39719f94d3d` /
  `3b35ad0c3f8979f295214ae16c7be09f6a1047b2779f9eeabe3dabec759e49f0`

### 解釈と次のbottleneck

Q007ag拡大tubeに対し、Q007anのrepaired-map全iterate帰納、Q007aoのexact-state initialization、
Q007apのsame-initial forward-error boundが接続した。従って登録inner exact-state setから始めた
exact軌道とsealed repaired MPFR-85軌道は、全非負sampling timeで一様Wiener誤差
\(8.803831096064757\times10^{-18}\)以内に留まる。

これはbi-infinite shadowing lemma、backward error、内部stage間距離、componentwise relative error、
任意Q007ag boundary initialization、他grid／MPFR build、GPU／parallel reduction、grid-uniformity、
continuum limit、D3Q27を主張しない。Q009 TT-crossはQ008c／Q010の固定経路棄却により保留する。
次はQ011 boundary／forcingまたはQ007af後に残る別norm certificateを独立に事前登録してから進む。

## 2026-08-09: Q011a nonzero-mean periodic forcing fixed-point compatibility

### 問いと事前登録

odd periodic \(17^2\)、\(\omega=3/2\)、\(\eta=1/100\)のfiltered BGK mapに、一様body-force

\[
F=(3\,2^{-40},0),\qquad
S_q(F)=3w_q(c_q\cdot F)
\]

をcollision後に加える問題を固定した。periodic streamingとpopulation-wise filterの後にもglobal
momentum incrementが残るため、boundary／drag／repairのないmapでfixed pointがcompatibleかを
Newton solveより先に判定した。rest-state spectrumはsource微分0の実装診断にだけ使い、fixed-point
stabilityとは呼ばないと事前登録した。

### 実装

- exact D2Q9 rational weight／velocity tableから9 source populationとmass／momentum momentを構成した。
  \(F_x=3\,2^{-40}\)により全source populationはdyadicとなる。
- rest、一様moving equilibrium、seed `20260809`の8 fixed-leaf positive perturbationの全10 probeで、
  forced-minus-unforced stateとcompensated global ledgerを照合した。
- 先頭4 direction、step \(2^{-12},2^{-13},2^{-14}\)でforced／unforced central derivativeを比較した。
- 全17² Fourier blockでstate-independent sourceのreference symbolをunforced filtered symbolと照合し、
  tolerance \(10^{-10}\)のstrict unit-circle countを監査した。
- exact global ledgerとdual moment inequalityから、任意stateのpopulation-l1 fixed-point residual lowerを
  \(867\,2^{-40}\)と構成した。
- Q011a codeは`research/`内へ閉じ、既存Q004--Q010 artifactのpackage source fingerprintを変更しない
  ことを全artifact回帰で確認した。

### 結果

validity 6/6、hypothesis 4/4で、
`nonzero-mean periodic body force is incompatible with a fixed point of the registered conservative map`
としてnegative obstructionをacceptedとした。

- exact source mass／momentum:
  `0 / 3*2^-40 / 0`
- exact per-step global momentum increment／population-l1 residual lower:
  `867*2^-40 / 867*2^-40`（float `7.885319064371288e-10`）
- source float moment residual:
  `0.0`
- maximum finite state-difference error:
  `1.3877787807814457e-17`
- maximum compensated global-ledger error:
  `1.2032042029375134e-14`
- maximum best forced／unforced derivative discrepancy:
  `5.062223386808321e-14`
- rest forced-output minimum population:
  `0.027777777777550403`
- rest reference strict unit-circle count／largest nonunit modulus:
  `3 / 0.9920954673551`
- direction／reference-spectrum digest:
  `6dbe9348ef90a73006319b366923706082faf69eda4dcf0295e5ea1e35720c32` /
  `e402291edccddbcfad43aef9ee8344ab3ac220b2324c66951e4b5ee88013f293`
- source／probe／result digest:
  `75fd3fe1050b39a333f483375969a67c79ab9ec75009a2048359d0f0dabb7492` /
  `43d0b722ba63a45ccf6b5a41cffaef387448fcc2cd9324538887fd3169571001` /
  `9b1f0c1516a365481c72617957b30424a7873136d221bd164b6d0617c4c3d958`
- runner／artifact newline-normalized SHA-256:
  `41e45565066fd4c96c2ae927bc8cc6a1218377f67b711f6cc312ecbf0d1c68de` /
  `31c427660b10771af7756c249408606578a9b7a02d756bc77b918b56e7a5b14a`

### 解釈と次のbottleneck

exact collision、periodic streaming、population-wise filterはいずれもsource以外のglobal momentumを
保存する。従って毎stepのstrict positive incrementはfixed-point等式と矛盾し、非零平均periodic
fixed-point Newton solveやmanifold continuationを開始すべきではない。

この結論はexact real-arithmetic global ledgerに限る。finite-precision bitwise fixed point、
Guo／EDM高次精度、zero-mean forcing、drag、pressure boundary、bounce-back、Poiseuille／Couette、
forced invariant manifold、normal attraction、他gridは未評価である。次はQ011bでzero-mean
single-wave periodic sourceを事前登録し、そこでforced fixed pointとspectrumを判定する。

## 2026-08-09: Q011b zero-mean periodic forced fixed point

### 問いと事前登録

Q011aと同じodd periodic \(17^2\)、\(\omega=3/2\)、\(\eta=1/100\)のfiltered BGK mapで、

\[
F_x(y)=3\,2^{-24}\cos(2\pi y/17),\qquad F_y(y)=0
\]

という零平均single-wave sourceをcollision後へ加えた。全mass／momentumを
\((289,0,0)\)へ固定し、x-independent stripe上では\((17,0,0)\)とした。153次元stripeの
global-moment nullspace \(B\in\mathbb R^{153\times150}\)を使い、zero coordinateとrest linear
responseの二初期値から同じfixed pointへ到達するかを判定した。

結果を見る前に、Newton最大12 step、line-search列、三つのfixed-point residual閾値、解一致閾値、
full x-Fourier 17 block、Schur／conjugacy／block-action閾値、spectral radius `0.9999`、全
\(I-J(k_x)\)のsingular-value／condition gateを固定した。未収束時にもzero-start terminal iterateで
validity診断を完走する一方、科学的解釈はsolver hypothesis通過時だけ行う規則とした。

### 実装

- Q011a artifact／runner／三digest／6+4 gateをread-only fresh replayした。
- unmodified binary64 cosineのmeanとFFT support、各site source moment、Q011a sourceとのbitwise一致、
  collision→source→streaming→filter stage orderを照合した。
- `scipy.linalg.null_space`による固定葉basisを一度だけ構成し、orthogonalityとmoment annihilationを
  Frobenius normで監査した。
- density／momentum座標でD2Q9 equilibriumを微分し、任意rectangular stateへ作用するanalytic
  collide-stream-filter Jacobianを実装した。rest linear-response stateの4方向central differenceで
  検証した。
- analytic reduced Jacobianを使うNewtonを二startから各2回実行し、terminal coordinateのbitwise一致と
  traceのexact JSON一致を確認した。
- fixed pointがx-translation invariantであることを使い、各\(k_x\)で153次元complex blockを構成した。
  \(k_x=0\)だけ150次元固定葉へ制限し、他16 blockは全153次元を用いた。
- 全2598 fixed-leaf eigenvalue、complex Schur reconstruction／unitarity、共役block spectrum、
  \(I-J\) singular valuesを計算した。4登録complex directionではfull \(17^2\) analytic actionと
  block actionを直接比較した。

### 結果

validity 6/6、hypothesis 4/4で、
`zero-mean single-wave periodic forcing yields a numerically resolved stable fixed-leaf fixed point`
としてacceptedとした。

- float force sum／FFT leakage:
  `-2.3822801641527197e-22 / 3.7252978093103943e-16`
- maximum source moment／stage replay discrepancy:
  `2.6469779601696886e-23 / 0.0`
- basis orthogonality／moment-annihilation residual:
  `1.259169632432682e-14 / 1.4118649012697392e-14`
- linear-response equation residual／maximum best Jacobian error:
  `4.779732994797796e-14 / 3.105943967977383e-11`
- Newton accepted steps（zero／linear-response）: `2 / 1`
- maximum terminal projected／full／component residual:
  `3.4838391155252677e-16 / 4.088062755440557e-16 / 1.6653345369377348e-16`
- two-solution absolute／forced-departure-relative distance:
  `7.901660672580398e-16 / 2.444328466505941e-11`
- minimum population／density:
  `0.027775908313351423 / 0.9999999999999997`
- maximum compensated target residual:
  `5.898059818321144e-16`
- first-harmonic \(j_x\) amplitude／force amplitude:
  `2.202356130540601e-05 / 1.7881393432617188e-07`
- departure leakage outside \(k_y=0,\pm1,\pm2\):
  `9.755400055442727e-12`
- unrestricted \(k_x=0\) unit count／fixed-leaf eigenvalue count:
  `3 / 2598`
- maximum fixed-leaf modulus（wave index）:
  `0.9920954673551019 (0)`
- minimum \(\sigma_{\min}(I-J)\)／maximum \(\kappa_2(I-J)\)（両witness index）:
  `0.00649328212134047 / 360.53472657220163 (16)`
- maximum Schur reconstruction／unitarity／conjugate Hausdorff／block-action error:
  `9.580660157280466e-15 / 8.02559073515726e-14 /`
  `1.3286214932264194e-14 / 1.129993555579798e-15`
- input／fixed-point／spectrum／result digest:
  `53dea81353ed4bcd77ab0c06533528f6d867d8b1bfa80d3d2ac3eddd7cf7dfbb` /
  `8db05ad1e7ae7806b70b6330d798f6dad05bc8718027ba13cb315116b021b17c` /
  `3ab8866e141b64a4d1d81bdfae1a70c61d8e7964d8480e2bd7ec7c7e174850fc` /
  `66c4b579dbd7d7c391fd2017f165c2de251ecf850b7c485cb936b9742c8addf6`
- runner／artifact newline-normalized SHA-256:
  `bac9448f280ce2dfb2e1627ce1558b792cb53e05746b94246baa6c329b8c8ef0` /
  `477202184694da1386c6b5bc0f0441e004a7a44f7a7b064f1d060d50adc66c27`

### 解釈と次のbottleneck

Q011aのglobal momentum obstructionは零平均sourceでは消え、登録固定葉上にpositiveなfixed pointを
高精度で数値的に解けた。さらに、そのfixed pointの全x-Fourier fixed-leaf spectrumは登録上限より
strictに内側にあり、全\(I-J(k_x)\)も登録isolation gateを通る。従ってforced問題の次段へ進める。

ただしこれは一つのgrid／amplitudeにおけるbinary64 Newton／Schur prequalificationである。rigorous
existence／uniqueness、basin、individual shear／acoustic labels、forced slow spectral subspace、
external gap／spectral quotient、nonresonance、normal attraction、forced invariant manifold、
finite-precision all-iterate shadowing、他grid／amplitude、boundary、Poiseuille／Couetteは主張しない。
次はQ011cでcandidate slow spectral clusterと外部gapを独立に事前登録する。

## 2026-08-09: Q011c forced slow spectral-cluster continuation

### 問いと方法

Q006hで選んだfirst-shell 24-mode hydrodynamic subspaceを、Q011b零平均forceの
\(t=j/8\), \(j=0,\ldots,8\)に沿ってfixed pointと同時に継続できるかを判定した。
\(k_x=0,1,16\) blockのselected dimensionを`6 / 9 / 9`に固定し、Hungarian set matchingから
ordered complex Schur range、Riesz projector、selected eigenvalue setを構成した。個別の
forced shear／acoustic labelやcluster内部permutationはgateに使っていない。

Q011b stored endpointからのbackward path、unforced targetからのdirect endpoint control、
\(k_x=\pm1\) conjugacy、\(k_x=0\) real closureを監査した。\(t=0,1/2,1\)では全2598 fixed-leaf
eigenvalueを再列挙し、selected/external global modulus gapと全9個の明示的Sylvester operator
minimum singular valueを計算した。

### 結果

validityは`5 / 6`で、Q011b endpoint spectrum reproductionだけが失敗したため、
`registered forced spectral-cluster audit is invalid`として`inconclusive`とした。
事前登録の`1e-12`閾値、witness一致、amplitude pathは観測後に変更していない。

- maximum forward/backward state distance:
  `3.2722439815434854e-15`
- endpoint stored-state absolute／relative distance:
  `3.2437399411382716e-15 / 1.0034303173230714e-10`
- maximum structural residual／adjacent principal angle:
  `7.476245086769142e-14 / 1.0421788015551248e-05`
- minimum reference alignment／external eigenvalue separation:
  `0.9999999965243628 / 0.023905378580598713`
- maximum projector 2-norm:
  `1.5115930042152532`
- maximum reversal／direct endpoint angle:
  `1.3633376718264379e-13 / 1.8516964947723607e-15`
- maximum projector／spectrum conjugacy error:
  `7.01708059108712e-14 / 1.6543129169796175e-14`
- minimum checkpoint Sylvester separation:
  `0.019362054767979874`
- minimum global normal gap／maximum full fixed-leaf radius:
  `0.002061121154971146 / 0.9920954673551043`
- endpoint radius／minimum-singular／maximum-condition absolute difference:
  `1.6653345369377348e-15 / 1.231653667943533e-16 / 7.048583938740194e-12`
- stored／continued worst resolvent witness index:
  `16 / 1`
- input／path／spectrum／result digest:
  `7d8d4a593dc29a715c995e237890da4de17314c4feffabe10111b289120435ee` /
  `06254ea5569d8b0c8c5369477c82ea685284aec9970574c46c24fea749280b92` /
  `5b1e79280b752268248f5150dd12c73a96719cb20d86cbd34fb3ff1e1b8b472c` /
  `4b41c4e7bda3a45f1ece871c183d321bed637d255053e22a82e7000dd83f5751`
- runner／artifact newline-normalized SHA-256:
  `10222da26fe14b97cd9565c517838d3a03e21f19e605d4a60cb2461e011d1d13` /
  `dbb562dd3628dc7589219baa94ae6791e084847f302c69dbcdc328b94ac6d2b3`

### 解釈と次のbottleneck

cluster pathそのもののraw hypothesis checkは全て通った。特にselected/external gap、
projector conditioning、Sylvester separation、global modulus normal dominance、fixed-leaf stabilityには
十分な数値marginがある。しかしvalidity停止規則により、これをforced spectral clusterのaccepted
selectionとは解釈しない。

失敗は、Q011b stored stateから\(3.24\times10^{-15}\)だけ異なるcontinued endpointで、
ほぼ同値な共役\(k_x=1,16\) blockのworst witnessが交換し、maximum condition numberが
\(7.05\times10^{-12}\)だけ変化したことに局在する。次はQ011c artifactをsealed inputとし、
stored exact replay、continued-state perturbation、共役orbit上のset-valued extrema、局所感度を
別々に判定する修復gateを事前登録する。Q011cの`inconclusive`を変更せず、そのgateを通るまで
Q011d external nonresonanceへ進まない。

## 2026-08-09: Q011c1 conjugacy-orbit endpoint localization

### 問いと方法

Q011cの唯一のvalidity failureが、許容されたstate perturbationに対する
\(k_x=1,16\)共役blockの個別witness交換だけで説明できるかを独立に判定した。Q011c artifact／runner／
四digest／exact cycleをsealed inputとし、Q011cの`inconclusive`を変更しない停止規則を置いた。

stored Q011b endpointとcontinued Q011c endpointの各17 fixed-leaf blockで\(A_k=I-J_k\)のfull SVDを
実行した。各block差にはFrobenius normと固定係数64のbinary64 paddingを使うWeyl区間を構成し、
\(\sigma_{\min}\)、\(\sigma_{\max}\)、\(\kappa_2\)のcontinued値を囲んだ。extremal witnessは
個別indexではなく9個のcomplex-conjugacy orbitで比較した。

### 結果

validity `5 / 5`、hypothesis `4 / 4`を通過し、
`the Q011c endpoint failure is localized to perturbation-consistent conjugate-witness tie instability`
として`accepted`とした。

- maximum stored／continued SVD reconstruction residual:
  `2.889692747875842e-15 / 2.94286841789878e-15`
- maximum stored／continued SVD unitarity residual:
  `2.5479952376461563e-14 / 2.480871382499916e-14`
- maximum stored／continued matrix-conjugacy residual:
  `6.570605272701854e-16 / 6.577836273397531e-16`
- maximum resolvent Frobenius difference／registered bound:
  `4.2352782748696136e-14 / 2.9468087840500247e-13`
- maximum minimum／maximum singular-value bound utilization:
  `0.0009382376259671139 / 0.010647618003265125`
- minimum-singular／maximum-condition winning-orbit interval margin:
  `2.694725883406468e-10 / 0.5844815558106689`
- stored／continued extremal orbit:
  radius`{0}`、minimum singular／maximum condition`{1,16}`
- exact individual witness exchange:
  minimum singular、maximum conditionとも`16 -> 1`
- input／metric／enclosure／result digest:
  `e9ea01348fe839dd745c3ccb7cf2e622bec3c0a4f080a1ab1c62a92a02ced064` /
  `fca5a81f3fc47e24a6f17578065adb527d892400d5d88c8eb18cf7089e234a9e` /
  `7a6cd761f88b328c2ffa74de5b9fb7952f454b86a99630d6266973e8fa6fea20` /
  `ad8b47548ebc04595246301864314502158e686520197377b3a33d30db1d4f86`
- runner／artifact newline-normalized SHA-256:
  `1f777dc50c6748cb8d8a64d643822b55733ac247b5de7d08b119d628b63c52a6` /
  `939baa85fa4db1efaf701985d81665f863e5f77f6ec2c95cfc2bacf004c0c45c`

### 解釈と次のbottleneck

continued endpointの全resolvent metric変化は登録上界の約1.1%以下であり、winning orbitと外部orbitの
順序は摂動区間込みで変わらない。従ってQ011cの失敗原因は、ほぼ同値な共役block間でのpointwise
tie-breakingと、state perturbationを無視したabsolute condition-number再現規則に局在した。

ただし同じQ011cデータを使う診断なので、Q011cの`inconclusive`をacceptedへ変更しない。forced
clusterを選択したとも、rigorous singular-value enclosureを得たとも主張しない。次は共役orbit意味論を
最初から採用し、未使用amplitude midpointをheld-out評価するQ011c2を事前登録する。Q011d
external nonresonanceはその後である。

## 2026-08-09: Q011c2 held-out forced spectral-cluster reissue

### 問いと方法

Q011cの9 training amplitudeの中間に、未使用だった8 midpointをholdoutとして固定した。17-node
forward／backward Newton pathを新たに解き、同じordered-Schur 24-mode clusterを追跡した。
training state／cluster、direct endpoint、Q011b stored canonical endpointをcontrolとした。

holdout 8 node全てで3 selected blockの明示的Sylvester operatorと全17 fixed-leaf blockを評価した。
合計24 Sylvester SVD、20,784 eigenvalueでselected/external separation、global modulus normal
dominance、strict stabilityを判定した。endpointはQ011c1と同じ共役orbit意味論とFrobenius--Weyl
intervalを最初から採用し、個別worst indexをgateにしなかった。

### 結果

validity `7 / 7`、hypothesis `5 / 5`を通過し、
`the forced first-shell cluster passes a conjugacy-orbit reissue with eight held-out amplitude nodes`
として`accepted`とした。

- maximum forward/backward／training state distance:
  `5.037082596836928e-15 / 4.318359172954769e-15`
- endpoint absolute／relative distance:
  `9.417935011590327e-16 / 2.913378288239695e-11`
- minimum population／density:
  `0.027775908313351423 / 0.9999999999999997`
- maximum structural residual／adjacent angle:
  `7.560599367895308e-14 / 5.2108940113403335e-06`
- minimum reference alignment／external separation:
  `0.999999996524363 / 0.02390537858060371`
- maximum projector norm／reversal angle:
  `1.5115930042152512 / 2.009181800848714e-13`
- maximum training cluster／canonical endpoint angle:
  `1.8103036342337398e-13 / 8.532131573213541e-14`
- minimum held-out Sylvester separation:
  `0.019362054855570406`
- minimum held-out normal gap／maximum fixed-leaf radius:
  `0.0020611211556098574 / 0.9920954673551043`
- endpoint resolvent difference／registered bound:
  `1.1428197375089487e-14 / 2.639179006344862e-13`
- endpoint minimum-singular／maximum-condition orbit margin:
  `2.6953366361742725e-10 / 0.5844815592084842`
- input／path／holdout-spectrum／endpoint／result digest:
  `de4b0c4d38d0efcff9c7db4bbef66ba6d081a6703c732dbd7116a294020459f2` /
  `36be8801af32ae178e91e049b2640ed4bb058107abdf2df2af8860930c53c27d` /
  `d7319399578d3755ee0679122dec5e6b6d3454e394295bd62886920d104b0d72` /
  `8c78791883b82f4a964d0c102006d9295b7b96733e77dea93249f30dc427b6a8` /
  `8c23b985d69ffaa980e752e5d262184c0a6d466681d9d44fa4f0e9101df02b0c`
- runner／artifact newline-normalized SHA-256:
  `87bdfc1ed20e6e68e4a395d36399adbab19e82809c626ecefa65a342ce42b9d2` /
  `c1794ca72eebd60c4bc097278495218e9e2d2e84bdacd0f478e510a80fcba42a`

### 解釈と次のbottleneck

Q011c2はQ011cの失敗閾値を緩めた再採点ではなく、未使用8 midpointを持つ別のreissueである。
training reproductionとheld-out spectrumが同時に通ったため、単一17² grid・登録force・17 nodeの
finite binary64 prequalificationとしてforced candidate spectral clusterをselectedとする。
Q011c originalの`inconclusive`とQ011c1のfailure-localization classificationは保持する。

continuous-amplitude continuation、individual mode label、rigorous projector／SVD enclosure、
external nonresonance、spectral quotient smoothness、forced invariant manifold、nonlinear normal
attractionは未認証である。次はQ011dでquadratic external nonresonanceとforced homological operatorを
事前登録する。

## 2026-08-09: Q011d forced quadratic external homological-family prequalification

### 問いと方法

Q011c2でselectedとしたforced 24-dimensional clusterについて、quadratic monomial全300個の
external homological blockが数値的に非共鳴かを、forced-map Hessianを観測する前に検査した。
base pointはQ011b stored endpointに固定し、\(k_x=0,1,16\)のordered-Schur selected dynamicsを
block diagonalに並べた。external quotientは同3 sectorのexcluded Schur blockと、
\(k_x=2,15\)のfull complex Schur blockで構成した。

selected coordinateのunordered pairをlexicographicに列挙し、output sectorごとに
`102 / 54 / 54 / 45 / 45` pairへ分解した。対称二次monomial action
\(m(R_1a)=Km(a)\)を直接assemblyし、8登録方向のactionと各sector spectrumを独立に照合した。

各pairの固有値積に対して\(A_{e,k}-\mu_{ij}I\)を構成し、300 block全てでfull SVD、
registered rank threshold、spectral distance、condition number、seed `20260820`のdirect solveを
保存した。非正規性を落とさない診断として、5 sectorで
\(A_{e,k}X-XK_k=B\)を各4 RHS、合計20本解いた。

### 結果

validity `7 / 7`、hypothesis `5 / 5`を通過し、
`the forced quadratic external homological family is numerically nonresonant and solvable`
として`accepted`とした。

- selected／external／full fixed-leaf eigenvalue count:
  `24 / 2574 / 2598`
- maximum structural／conjugate-spectrum residual:
  `7.35746952368904e-14 / 1.3286214932264194e-14`
- selected minimum／external maximum modulus:
  `0.983770956987517 / 0.981709835832543`
- global normal gap／full radius／logarithmic spectral quotient:
  `0.0020611211549740327 / 0.9920954673551019 / 1.128181043680419`
- pair count by output sector \(0,1,16,2,15\):
  `102 / 54 / 54 / 45 / 45`
- pair-enumeration SHA-256:
  `c94c79f6bdf98fd2e85706b5e15f2534dfb4e0132cc19e2bf17cdf02471b9f85`
- sector leakage／maximum action error／maximum product-spectrum error:
  `0.0 / 2.4215004011706513e-16 / 0.0`
- singular block count／minimum operator singular value:
  `0 / 0.0001550243474275936`
- minimum spectral distance／maximum condition number:
  `0.00019318395013023792 / 15018.139810898925`
- maximum direct-solve residual／conjugate-sector discrepancy:
  `3.0754729793416724e-15 / 2.0227681201111162e-11`
- 20 probe maximum equation residual／response amplification:
  `1.620591689280895e-13 / 361.53308227372094`
- input／linear-split／pair-family／sector-probe／result digest:
  `ee2713e8169ea0f475ddee1b1233964ba40739d2276b78db3fff5410158dd2f8` /
  `7208875ff95f3a768e4b822cf9be854228d6664800dfc69218c0e6a030a0c63e` /
  `f9caee5b591e74b40b497ca7eb8244f1bbaeba71d239684c47d8215c46c2fb0b` /
  `feb864e2725e0cf726b43c443bb48b53f34ba0ac54693bb97a2b986f598a1414` /
  `a6941371e54a5e4d4abbea2f835196ddd7cce35c7c266ce399020764ed5b9dd7`
- runner／artifact newline-normalized SHA-256:
  `815fe7e0101cc05cc44fcb224534762f0ef7625f8c9604ff0a822c13171a617d` /
  `c3acb9b7acc6e3121cb6e48a04bb060b5c95d7b128fe15fb11b67ee456337fd0`

### 解釈と次のbottleneck

全300固有値積はexternal spectrumから分離し、full-rank SVDとdirect solve gateを通過した。
5 sectorのfull nonnormal \(K_k\) actionも登録20 RHSを安定に解いた。従って単一17² grid、
登録forced endpoint、binary64 Schur／SVDにおけるquadratic external operator familyを
numerically nonresonant and solvableとしてprequalifiedとする。

ただし20 probeはrigorous inverse-operator norm upperではなく、spectral quotient `1.12818`も
smoothness／uniqueness定理には解釈しない。forced-map Hessian、quadratic forcing support、
\(W_2\)、\(R_2\)、homological residual、independent derivative、invariance residual order、
forced SSM existence／uniqueness、nonlinear normal attractionは未認証である。次はQ011eで
dense forced quadratic chartと独立残差検証を観測前に事前登録する。

## 2026-08-09: Q011e dense forced quadratic fixed-leaf chart

### 問いと方法

Q011b stored endpointとQ011d selected 24-dimensional clusterを封印し、保存量の扱いは案A、すなわち
\(\delta M=\delta P_x=\delta P_y=0\)の不変葉に固定した。zero-wave center coordinateは追加せず、
zero-\(k_x\) quadratic correctionのglobal conserved momentをゼロに制限した。

ordered-Schur selected basisに対してSylvester equationからinvariant external complementとRiesz型
left coordinatesを構成した。forced-map equilibriumの解析Hessianを各siteで評価し、全300 unordered
pairをoutput sector `102 / 54 / 54 / 45 / 45`へ分割した。5 sectorのfull nonnormal
Sylvester equationから\(W_2/R_2\)を解き、deterministic real QR basisへ移した。

解析Hessianはseed `20260823`の16 independent direction pairについて、forced mapそのものの
step `0.004 / 0.002` centered mixed differenceと比較した。一段不変性残差はseed `20260824`の
32方向、振幅`1e-5 / 2e-5 / 4e-5 / 8e-5 / 1.6e-4`で測定し、登録どおり`1e-13`以上の点だけを
log-log fitへ使った。

### 結果

validity `7 / 7`を通過した。hypothesisはhomological construction、graph gauge／保存／support、
realification、independent Hessian、largest-amplitude improvement／positivity／conservationの5 gateが
通り、residual slope gateだけが落ちたため`5 / 6`である。Q011eは事前登録どおり`rejected`とした。

- classification:
  `the forced fixed-leaf quadratic chart is constructed, but the registered residual-order window is underresolved`
- maximum complex structural／real linear invariance residual:
  `7.35746952368904e-14 / 8.341890217669523e-15`
- analytic forcing／\(W_2\)／\(R_2\) Frobenius norm:
  `6.834040875959414 / 14.084081139824606 / 0.5789086833342865`
- maximum sector solve／full／pairwise homological residual:
  `8.463492700134046e-16 / 1.2377387705494087e-14 / 1.3875757356771478e-14`
- graph-gauge／zero-\(k_x\) conservation residual:
  `2.028243962507091e-15 / 8.28412455635593e-15`
- forcing／\(W_2\) support leakage:
  `4.5884705629714995e-15 / 2.903640423048552e-15`
- independent Hessian maximum discrepancy／coarse-to-fine change:
  `1.2602687807695985e-9 / 3.254644954471969e-7`
- minimum independent directional Hessian norm／population:
  `0.19527762984006905 / 0.027594496291526268`
- slope-eligible／degenerate directions: `0 / 32`、`32 / 32`
- linear／quadratic fit-point count per direction: `5 / 1`
- maximum largest-amplitude quadratic／linear residual ratio:
  `8.954201113852774e-5`
- minimum chart-or-mapped population／maximum global conservation drift:
  `0.027772230628583257 / 1.1370760687229683e-13`
- input／derivative／chart／residual／result digest:
  `f0bd65361d0cdc39e6499b8b0065ce6d7705945927ed77af5d2b231d0572bc9c` /
  `d017d3ea204ad337f538b6f1819e215b6ab8a69f89090cc51ca9eb4885b75fce` /
  `6d4ee0102a6df052fac857890468ed911cff994e07c573dde837eb54a4a22e05` /
  `5570cb7acfc465f57850f960c6c9d68770182856b6a9aba62e81256c77e84948` /
  `89b39a6a6a80452142a2c9288780a08c1b24b49614080b5412fff82171a8188e`
- runner／artifact newline-normalized SHA-256:
  `3aa608852be7a1df7dbe37b4d3c7e1bb3fbf125eae115260fc45a223e0757955` /
  `45d563103678d790aa3df4db692bbe781c9c86ed550c7499c61b397688666fca`

### 解釈と次のbottleneck

解析Hessian、全300 homological coefficient、graph gauge、固定葉保存、Fourier support、実座標化は
登録精度で整合した。従って`dense_forced_quadratic_chart_is_constructed=true`は記録する。一方、
quadratic residualはnoise floor以上の点が各方向1点しかなく、三次slopeをfitできなかったため、
`registered_residual_order_is_confirmed=false`である。小さい残差を成功に読み替えず、Q011eは再採点しない。

観測後に唯一の失敗がconstructionではなくmeasurement windowだったことを明示するため、genericな
reject reporting stringのみ上記classificationへ精密化した。登録threshold、seed、amplitude、noise floor、
gateとbinary outcomeは変えていない。次は同じ閾値を固定し、別seed・拡大振幅窓のQ011e1を独立gateとして
事前登録する。forced SSM existence／uniqueness、uniform Taylor remainder、nonlinear normal attraction、
basin、他grid／force／wall boundaryは依然として未認証である。

## 2026-08-09: Q011e1 independent enlarged residual-window reissue

### 問いと方法

Q011eのmeasurement-window underresolutionだけを修復する独立gateとして、Q011e artifactとrunner、
全digest、元の`rejected` outcomeを封印した。Q011e chartは同じ解析手順で一度だけfresh再構築し、
real tangent／extractor／linear dynamics／analytic second derivative／\(W_2\)／\(R_2\)の6 array hashと
全construction thresholdを照合した。係数の再fitやQ011eの再採点は行っていない。

未使用seed `20260825`から32 unit directionを生成し、振幅を
`1.6e-4 / 3.2e-4 / 6.4e-4 / 1.28e-3 / 2.56e-3`に固定した。Q011eと同じnoise floor
`1e-13`、最低eligible `28 / 32`、linear slope `1.85--2.15`、quadratic slope `2.70--3.30`を使った。
5点primary fitに加え、bridge点を除く上位4点secondary fitを保存し、両slope差を`<=0.15`でgateした。
160 sample全てについてchart／reduced／mapped state hash、residual、minimum population、global
conservation driftを保存した。

### 結果

validity `5 / 5`、hypothesis `6 / 6`を通過し、
`the independent enlarged window resolves second- and third-order forced chart residuals`
として`accepted`とした。

- slope-eligible／degenerate directions: `32 / 32`、`0 / 32`
- linear primary slope range:
  `1.9999592141961493 -- 2.0000652994279995`
- linear secondary slope range:
  `1.9999478838445748 -- 2.000083440834926`
- quadratic primary slope range:
  `2.9998586349153378 -- 3.000154889315294`
- quadratic secondary slope range:
  `2.999908289307265 -- 3.000145181102861`
- maximum linear／quadratic primary-secondary slope difference:
  `1.8141406926464043e-5 / 1.7126610593187763e-4`
- maximum largest-amplitude quadratic／linear residual ratio:
  `0.0013091448869808333`
- minimum chart/reduced/mapped population／maximum conservation drift:
  `0.027713756598630398 / 1.1370820561363141e-13`
- direction SHA-256:
  `64b017fb5a3c55378ccee4d457b4d2a8c75a92cd5b421897f9b7de1ad6a77b1d`
- input／chart-reconstruction／residual-window／result digest:
  `8e979deeed0e5f4151addb5f3b06c1a9815a28f4e0c5762726d7c29a03d035c0` /
  `2e739657032352d7d0496568a216b761000a68beb6d00749e1e427e6447598fb` /
  `20267150710538f797f21cc2846ee6be14060ad9ea6bef98ef29e4731121410b` /
  `0370a24ce7a74da71ee978b3892ea23412c3d18adb110e2b2b53aaf02ccdf039`
- runner／artifact newline-normalized SHA-256:
  `bb8a052f387d2748fee823af10f2ab4ea4a9a08ebe62e8b4ff87d68d55c2929f` /
  `989801d1e4e1396ebba279e11c396f7f6d4e9616d2aa170f5687f9ba08a95840`

### 解釈と次のbottleneck

独立拡大窓ではlinear chartの二次、quadratic chartの三次が全32方向でnoise floor上に解像され、
上位4点secondary fitにも安定だった。従って単一17² forced endpointの登録有限方向・振幅範囲では、
Q011e dense quadratic chartの一段残差次数を確認した。

Q011eの元小振幅窓と`rejected` outcomeは変更しない。Q011e1もuniform Taylor remainder、
continuous-amplitude family、forced SSM existence／uniqueness、nonlinear normal attraction、basin、
他grid／force／wall boundaryを示さない。次はQ011fで独立multi-step shadowing windowを観測前に
事前登録し、その後にnatural Fourier-sparse baselineを残したTT／sparse費用評価へ進む。

## 2026-08-09: Q011f independent multi-step forced-chart shadowing window

### 問いと方法

Q011e1 accepted artifactとQ011e rejected artifactを封印し、同じforced quadratic chartを一度だけ
fresh再構築した。未使用seed `20260826`の32方向、5振幅について、linear／quadratic各160 full orbitと
reduced-lift orbitを64 step追跡した。linear／quadraticは同じreduced coordinateから始めるが、それぞれ
自分のchart上のphysical initial stateを使うsame-chart comparisonとした。

全10,240 stepでshadowing error、minimum population、global conservation drift、reduced-coordinate normを
保存し、horizon `1 / 2 / 4 / 8 / 16 / 32 / 64`の1,120 checkpointでは4 state hashを追加した。
各direction・horizonの5振幅errorをfloor `1e-12`以上の点だけでfitし、224 fit全てに4点以上を要求した。

### 結果

validity `6 / 6`を通過した。hypothesisは5 gateを通ったが、slope-eligible fit countが登録`224 / 224`に
対して`222 / 224`だったため、
`the forced quadratic chart fails the registered finite shadowing window`
として`rejected`とした。

- degenerate direction-horizon:
  `(4, 1)`、`(4, 2)`
- linear／quadratic fit-point count: `5 / 3`
- quadratic fit mask: `[false, false, true, true, true]`
- horizon 1 first-two quadratic errors:
  `1.1752258806252989e-13 / 9.402263023336189e-13`
- horizon 2 first-two quadratic errors:
  `1.1463003790416861e-13 / 9.171105405464717e-13`
- eligible linear／quadratic slope range:
  `1.9999216343019504 -- 2.000128344576816` /
  `2.999096737571295 -- 3.000265091846932`
- maximum checkpoint quadratic／linear error ratio:
  `0.002547526388856511`
- maximum horizon-64 quadratic error／initial amplitude:
  `1.1019505895816554e-6`
- minimum full-or-lifted population／maximum conservation drift:
  `0.027704572566416702 / 1.8214860035899544e-12`
- maximum linear／quadratic reduced-coordinate amplification:
  `1.3831860210790254 / 1.38318678185839`
- direction SHA-256:
  `4d0bef57236d4f70a8a8f422b1bdfa39cd5737c88401c2441decdd98d886d2f9`
- input／chart-reconstruction／trajectory／result digest:
  `e9b29c95d41af0062259d3aab19ab2c58175cd98582ed82f3af36863f023bc53` /
  `aa1da452db8ff6b84e88a32f7a7119c63816b12e283147daaa303e9e09c3ae42` /
  `aa62fc11a36bef881bbcdb05919818f6db167f3f95eee396fcdaf79fead5e182` /
  `629a5a7a3d3bfed12a590646c375d4977db1726ddc521ddb86394786b1005f22`
- runner／artifact newline-normalized SHA-256:
  `e9c0a8e38b94dbe693855dc836f8cf02393675b417ff3f43fc43059ab361a741` /
  `9c091dbafd60617850cd3168f3ad9235a353b0990cbd003df9be0b487ead1591`

### 解釈と次のbottleneck

失敗はdirection 4のhorizon 1・2に局在した。両者とも第2振幅のquadratic errorが登録floor `1e-12`を
僅かに下回り、第三振幅以降の3点しかfitに残らなかった。222 eligible fitの次数、全checkpoint改善比、
64-step相対誤差、positivity、conservationは通過しているため、長時間shadowing劣化の観測ではない。

それでも`224 / 224` gateを緩めず、Q011fは再採点しない。次は同じdirection、floor、horizon、slope／
performance thresholdを維持し、未使用midpoint amplitude `4.8e-4`の32 trajectoryだけを追加する
Q011f1を独立再発行として事前登録する。Q011f1が通るまでQ011gのTT／sparse比較へ進まない。

## 2026-08-09: Q011f1 held-out-amplitude multi-step reissue

### 問いと方法

Q011fの`rejected` artifact、runner、4 digest、direction hash、二つのdegenerate witnessを封印した。
Q011e chartを同じ6 array hashで一度だけfresh再構築し、Q011fと同じseed `20260826`から同じ32方向を
再現した。新しいデータは未使用振幅`4.8e-4`のlinear／quadratic full orbitとreduced-lift orbitだけで、
各64 stepを追跡した。元artifactの5振幅errorは置換せず、追加点と振幅順にmergeした。

noise floor `1e-12`、horizon `1 / 2 / 4 / 8 / 16 / 32 / 64`、linear slope `1.75--2.25`、
quadratic slope `2.50--3.50`、quadratic／linear ratio `0.05`、64-step relative-error `1e-3`、
positivity／conservation閾値はQ011fから変更していない。追加campaignは32 trajectory per chart、
2,048 step、224 checkpointで、元データと合わせて224個の6点fitを評価した。

### 結果

validity `6 / 6`、hypothesis `6 / 6`を通過し、
`the forced quadratic chart passes a held-out-amplitude 64-step shadowing reissue`
として`accepted`とした。

- merged slope-eligible／degenerate fit: `224 / 224`、`0 / 224`
- merged linear／quadratic slope range:
  `1.9999204011998797 -- 2.000130424734462` /
  `2.9992217798368643 -- 3.00027147080911`
- maximum merged checkpoint quadratic／linear error ratio:
  `0.002547526388856511`
- maximum merged horizon-64 quadratic error／initial amplitude:
  `1.1019505895816554e-6`
- minimum merged full-or-lifted population／maximum conservation drift:
  `0.027704572566416702 / 1.8214860035899544e-12`
- held-out-only minimum population／maximum conservation drift:
  `0.027762813486844076 / 1.8213621153007498e-12`
- held-out-only maximum checkpoint ratio／horizon-64 relative error:
  `0.00047765951440299786 / 3.8740640529751134e-8`
- direction SHA-256:
  `4d0bef57236d4f70a8a8f422b1bdfa39cd5737c88401c2441decdd98d886d2f9`
- input／chart-reconstruction／heldout-trajectory／merged-fit／result digest:
  `101adcdc6fc2d40dc984e6ba900d234b913f7c78aa34381a08d0a77aa9e23000` /
  `ba50ee295551dae970d33e1bba735ac0502987aef0f4a82987f2998ae884f732` /
  `243c41522a9eb7d7b78b2031bdbe8f55eb23b447e8d84162b1aae2f53b651829` /
  `2e3fcee7bebec5c82f2fbd2b78ddac8c44401fd0681ad5d9feb60c7257a8326e` /
  `484580786b6c535856f0693b14c58815462e1de979759057dc3b402d475bcbc7`
- runner／artifact newline-normalized SHA-256:
  `eab2d63a075f2c43b4c6adfaa7941e9c23bf85a351427057130f68945346ce62` /
  `79ddb64e0965b5b87b7ad68c6dc8698efdd2281540c798ed27f355747d265bc1`

元の失敗二点ではheld-out quadratic errorがhorizon 1で`3.1730810288365184e-12`、horizon 2で
`3.0952409781368448e-12`となり、どちらもfloorを越えた。combined maskは
`[false, false, true, true, true, true]`、fit-point countは4となり、quadratic slopeはそれぞれ
`3.000037106494855`、`3.0000355600774475`だった。

### 解釈と次のbottleneck

Q011fで局在したearly-horizon measurement-floor underresolutionは、閾値を緩めず独立振幅で修復された。
従ってこの6振幅、32方向、64 step、7 horizonのfinite binary64 reissueでは、quadratic chartの有限
multi-step shadowing windowを確認した。一方、Q011f自体は`rejected`のままであり、all-time shadowing、
uniform remainder、basin、normal attraction、forced SSM existence／uniqueness、他grid／force／wall
boundaryは未認証である。

次はQ011gで、forced quadratic coefficientのnatural Fourier-sparse representationを必須baselineとして
残し、TT-SVDと格納scalar数、実メモリ、評価時間、rounding時間、実効自由度、不変性残差を比較する。
結果を見て表現や閾値を変えないよう、実装前に独立gateを事前登録する。

## 2026-08-09: Q011g forced quadratic Fourier-sparse／TT-SVD audit

### 問いと方法

Q011f1 accepted artifactとQ011e coefficientを封印し、native complex (W_2/R_2)、coordinate map、
real chartを一度だけfresh再構築した。300 unordered pairをoutput sector `0 / 1 / 16 / 2 / 15`へ
`102 / 54 / 54 / 45 / 45`と分割した。各(W_2) pairは該当する17×9 Fourier fiberだけ、(R_2)は
selected sector `0 / 1 / 16`の`6 / 9 / 9` output fiberだけを保存するnatural表現を構築した。

同じ構造射影済みordered-dense (W_2^F/R_2^F)を、output-first／last、flat／Fourier-factor／D1Q3-factorの
6 uncapped TT-SVD bundleへ入力した。toleranceは`1e-13`である。独立seed `20260902`の32方向で作用、
seed `20260903`の16方向・振幅`2.56e-3`でone-step invariance defectを比較した。offlineはwarmup 1、
measured 3、onlineはwarmup 1、measured 5とし、各blockでmethod順をcyclic rotationした。TT採択には
同じ候補が忠実度、4 storage metric、robust online envelope、conservative break-evenを全て通ることを
要求した。

### 結果

validity `6 / 6`を通過した。全6 TTの係数・作用・realification・invariance residualは登録閾値を通った。
一方、storage winnerは0、robust timing winnerは3、joint winnerは0だった。hypothesisは`1 / 4`通過で、
`registered TT-SVD bundles do not beat the natural Fourier-sparse forced-quadratic baseline`
として`rejected`とした。

- robust timing winners:
  `flat-output-last / fourier-output-last / d1q3-output-last`
- natural sparse stored real scalars／raw／in-memory／NPZ bytes:
  `94,968 / 760,644 / 761,995 / 762,188`
- best-storage TT (`fourier-output-first`) corresponding values:
  `474,050 / 3,792,544 / 3,795,218 / 3,795,586`
- best TT／sparse scalar／raw／memory／NPZ ratio:
  `4.99168140847443 / 4.98596452479741 / 4.98063373119246 / 4.97985536376852`
- sparse offline min／median／max:
  `2.6452 / 2.7488 / 2.7883 ms`
- best-storage TT offline min／median／max:
  `396.4686 / 401.5353 / 411.2165 ms`
- sparse online min／median／max:
  `0.725621875 / 0.7321 / 0.735528125 ms per joint action`
- fastest TT (`flat-output-last`) online min／median／max:
  `0.46046875 / 0.47460625 / 0.480134375 ms per joint action`
- fastest TT online ratio／stored-scalar ratio:
  `0.6482806310613304 / 15.2224538792014`
- maximum TT reconstruction／joint-action／realification error:
  `2.41559062578165e-14 / 3.84139374578316e-14 / 3.82602037711869e-14`
- natural projection loss (W_2/R_2):
  `3.33475349414364e-15 / 0`
- natural-vs-dense action／defect relative difference:
  `3.23695449081624e-16 / 4.16928788077864e-9`
- maximum TT-vs-sparse defect relative difference:
  `2.12579364573947e-8`
- minimum population／maximum conservation drift:
  `0.027702486940874498 / 1.13691215527115e-13`
- input／coefficient／fidelity／cost／result digest:
  `0632be40fccc212f23a271fa00ed80696f9a146a1b107e513b3a47edb9870a20` /
  `fc9edec10ee22abfaa2b763be9f69c9d72bfc59543aa34faea6ab206c35ab264` /
  `30dabea285da9070e2ebc0b351afde4695deb275d5f96ee66de1b1ca0468fcad` /
  `222a42321f4ae814478cc65102afcbc8926754d8cb7c48ed8ca2952e350767a7` /
  `e0874eabe2c5b924d0b5d7b56533cd695406166d4370b493a0dabdc0b22dbb2a`
- runner／artifact newline-normalized SHA-256:
  `84ed56dabd0b0f870f1c6b27c9907c9566439ff03affe5aacc61ba611f4678fe` /
  `842ddbae2a28ccd2f11a112f23205cb049668b82691fdd180edc5ac20fecaa25`

### 解釈と次のbottleneck

output-last配置はこのCPU campaignのlocal joint actionではnatural sparseより速かった。従って「TTは常に
遅い」とは結論しない。しかし最速候補は格納scalarで約15.2倍、最小格納候補でも約5倍を要し、事前登録した
joint採択条件を満たさない。全忠実度gateが通っているため、棄却は数値精度不足ではなくこのtensorizationの
格納損失である。

このsealed forced coefficientにはnatural Fourier-sparseを採用し、TT-crossを開始しない。Q011e--Q011f1の
既存結果は変更せず、TT一般、別tensorization、GPU、full rollout、他grid／forceの不可能性は主張しない。
次に実装上の表現を進める場合は、natural sparse-backed chartのfinite multi-step equivalenceを独立gateとして
事前登録する。数学側へ戻る場合は、forced SSM存在・一意性またはnormal attractionを別gateにする。

## 2026-08-09: Q011h natural Fourier-sparse 64-step chart equivalence

### 問いと方法

Q011gで必須baselineとして残ったnatural Fourier-sparse (W_2/R_2)作用が、ordered-dense
real Hessianを使うforced quadratic chartと64 reduced stepにわたり同じ計算を行うかを調べた。
Q011g artifact、TT-cross非許可、Q011f1／Q011fのoutcomeを封印し、natural coefficientを一度だけ
fresh再構築した。

sparse runtimeはbase、tangent、reduced linear map、complex-to-real coordinate map、pair、sector、
Fourier fiberだけを所有し、dense Hessian、ordered-dense tensor、native dense coefficientを持たない。
seed `20260906`の24方向と未使用3振幅`4.0e-4 / 9.6e-4 / 2.4e-3`から72初期値を作り、
dense／sparse reduced coordinateとlifted stateを別々に64 step更新した。全65 stateの両coordinateで
common-input actionを比較し、8 checkpointで両chartのone-step invariance defectを比較した。

### 結果

validity `5 / 5`、hypothesis `4 / 4`を通過し、
`the natural Fourier-sparse chart reproduces the dense forced quadratic reduced trajectory through 64 steps`
として`accepted`とした。

- trajectory／state／update count per implementation:
  `72 / 4,680 / 4,608`
- common-input action comparison／checkpoint defect count per implementation:
  `9,360 / 576`
- maximum joint-action relative error／sparse imaginary leakage:
  `2.8548696893009472e-15 / 6.582416358786708e-13`
- maximum coordinate error / initial-coordinate norm:
  `1.0164395367051605e-16`
- maximum lifted-state error / initial-tangent-perturbation norm:
  `1.4456028966473394e-14`
- maximum checkpoint defect-vector／defect-norm scaled difference:
  `6.624584698733856e-15 / 1.492977856773724e-16`
- minimum population／maximum conservation drift:
  `0.027709129004501398 / 1.1371721488215581e-13`
- state／checkpoint metric SHA-256:
  `298efab077e38fe3d31b146460558219675ab88ab9c0182ad3fb14e25a52d854` /
  `7fd9446be00f5822f7aee5a2750b03b36d5b0f4b1916e123878b824cba95757b`
- input／coefficient／campaign／result digest:
  `c9ea06c8961940f54dd3c02e3d68d7ba777e77fc9be2f0a7c3eecab5ab257b83` /
  `2ab44a23811ef9f7e1975fb27561dd92660938778bf73ef149e46ed04f399669` /
  `bbb6a489fc76af150a3a162f585b0b2e1a65d0445d5eb14ab11b280bc492a035` /
  `a78812d93063ed7deeaca09dad5feb2cf018fb1bec315dab94b4f02d27f75864`
- runner／artifact newline-normalized SHA-256:
  `1e6848e572137d019531514235741b18ca10644dd7d14e304dc26d92d81cda9e` /
  `2cfcf5cb76698ae8e451f448a3048e3d29a1b8aed034d3afa5c25f7fd66038f5`

### 解釈と次のbottleneck

64-stepでの表現差の蓄積は、coordinateで初期振幅比`1.02e-16`、lifted stateで初期接線
摂動比`1.45e-14`に留まった。従ってこのfixed coefficientにはnatural Fourier-sparseをforced
quadratic chartの実装baselineとする。Q011gのTT棄却とTT-cross非許可は変更しない。

一方、本campaignが64 step進めたのはreduced trajectoryであり、full LBM orbitは各checkpointの
one-step defectにのみ使った。従ってQ011f／Q011f1のshadowing outcomeを再採点せず、all-time
equivalence、uniform remainder、forced SSM存在・一意性、normal attraction、basinを追加認証しない。
実装表現の問題はここで一度閉じ、次はforced SSMの存在・一意性またはnormal attractionの
数学gateを別途事前登録する。

## 再現 artifact

数値の完全な記録:

[artifacts/q005_nonresonance.json](artifacts/q005_nonresonance.json)

[artifacts/q006s_stripe.json](artifacts/q006s_stripe.json)

[artifacts/q006r_mode_closure.json](artifacts/q006r_mode_closure.json)

[artifacts/q006n_normal_refinement.json](artifacts/q006n_normal_refinement.json)

[artifacts/q006c_coefficient_scaling.json](artifacts/q006c_coefficient_scaling.json)

[artifacts/q006f_checkerboard_filter.json](artifacts/q006f_checkerboard_filter.json)

[artifacts/q006g_low_wave_tangency.json](artifacts/q006g_low_wave_tangency.json)

[artifacts/q006h_cluster_complete.json](artifacts/q006h_cluster_complete.json)

[`artifacts/d2q9_baseline.json`](artifacts/d2q9_baseline.json)

[`artifacts/q004b_and_manufactured.json`](artifacts/q004b_and_manufactured.json)

[`artifacts/q006m_anchor_obstruction.json`](artifacts/q006m_anchor_obstruction.json)

[`artifacts/q006o_forward_error_budget.json`](artifacts/q006o_forward_error_budget.json)

[`artifacts/q006p_dual_reporting.json`](artifacts/q006p_dual_reporting.json)

[`artifacts/q006q_forward_error_holdout.json`](artifacts/q006q_forward_error_holdout.json)

[`artifacts/q007a_cubic_prequalification.json`](artifacts/q007a_cubic_prequalification.json)

[`artifacts/q007b_cubic_continuation.json`](artifacts/q007b_cubic_continuation.json)

[`artifacts/q007b1_cubic_radius.json`](artifacts/q007b1_cubic_radius.json)

[`artifacts/q007c_quartic_prequalification.json`](artifacts/q007c_quartic_prequalification.json)

[`artifacts/q007c1_quartic_continuation.json`](artifacts/q007c1_quartic_continuation.json)

[`artifacts/q007c2_quartic_shadow_radius.json`](artifacts/q007c2_quartic_shadow_radius.json)

[`artifacts/q007d_normal_cocycle.json`](artifacts/q007d_normal_cocycle.json)

[`artifacts/q007e_adapted_metric.json`](artifacts/q007e_adapted_metric.json)

[`artifacts/q007f_adapted_finite_cocycle.json`](artifacts/q007f_adapted_finite_cocycle.json)

[`artifacts/q007g_theorem_readiness.json`](artifacts/q007g_theorem_readiness.json)

[`artifacts/q007h_rational_spectrum.json`](artifacts/q007h_rational_spectrum.json)

[`artifacts/q007h1_equivariant_spectrum.json`](artifacts/q007h1_equivariant_spectrum.json)

[`artifacts/q007i_direct_nonresonance.json`](artifacts/q007i_direct_nonresonance.json)

[`artifacts/q007j_eigencoordinate_bridge.json`](artifacts/q007j_eigencoordinate_bridge.json)

[`artifacts/q007k_quadratic_jet_bridge.json`](artifacts/q007k_quadratic_jet_bridge.json)

[`artifacts/q007l_cubic_jet_bridge.json`](artifacts/q007l_cubic_jet_bridge.json)

[`artifacts/q007m_quartic_jet_bridge.json`](artifacts/q007m_quartic_jet_bridge.json)

[`artifacts/q007n_explicit_local_radius.json`](artifacts/q007n_explicit_local_radius.json)

[`artifacts/q007o_external_complement_radius.json`](artifacts/q007o_external_complement_radius.json)

[`artifacts/q007p_finite_tube_attraction.json`](artifacts/q007p_finite_tube_attraction.json)

[`artifacts/q007q_population_positivity.json`](artifacts/q007q_population_positivity.json)

[`artifacts/q007r_stagewise_positivity.json`](artifacts/q007r_stagewise_positivity.json)

[`artifacts/q007s_finite_tube_enlargement.json`](artifacts/q007s_finite_tube_enlargement.json)

[`artifacts/q007t_larger_tube_population_positivity.json`](artifacts/q007t_larger_tube_population_positivity.json)

[`artifacts/q007u_larger_tube_stagewise_positivity.json`](artifacts/q007u_larger_tube_stagewise_positivity.json)

[`artifacts/q007v_binary64_stage_enclosure.json`](artifacts/q007v_binary64_stage_enclosure.json)

[`artifacts/q007w_ideal_precision_threshold.json`](artifacts/q007w_ideal_precision_threshold.json)

[`artifacts/q007x_mpfr_fixed_leaf.json`](artifacts/q007x_mpfr_fixed_leaf.json)

[`artifacts/q007y_distributed_conservation_repair.json`](artifacts/q007y_distributed_conservation_repair.json)

[`artifacts/q007z_selected_wave_repair.json`](artifacts/q007z_selected_wave_repair.json)

[`artifacts/q007aa_initialization_interior.json`](artifacts/q007aa_initialization_interior.json)

[`artifacts/q007ab_forward_shadowing.json`](artifacts/q007ab_forward_shadowing.json)

[`artifacts/q007ac_phase_aware_resolvent.json`](artifacts/q007ac_phase_aware_resolvent.json)

[`artifacts/q007ad_asymmetric_phase_resolvent.json`](artifacts/q007ad_asymmetric_phase_resolvent.json)

[`artifacts/q007ae_internal_phase_resolvent.json`](artifacts/q007ae_internal_phase_resolvent.json)

[`artifacts/q007af_radius_step_obstruction.json`](artifacts/q007af_radius_step_obstruction.json)

[`artifacts/q007ag_tube_radius_propagation.json`](artifacts/q007ag_tube_radius_propagation.json)

[`artifacts/q007ah_propagated_tube_population_positivity.json`](artifacts/q007ah_propagated_tube_population_positivity.json)

[`artifacts/q007ai_propagated_tube_stagewise_positivity.json`](artifacts/q007ai_propagated_tube_stagewise_positivity.json)

[`artifacts/q007aj_propagated_tube_binary64_enclosure.json`](artifacts/q007aj_propagated_tube_binary64_enclosure.json)

[`artifacts/q007ak_reentry_factor_audit.json`](artifacts/q007ak_reentry_factor_audit.json)

[`artifacts/q007al_propagated_tube_mpfr85_bridge.json`](artifacts/q007al_propagated_tube_mpfr85_bridge.json)

[`artifacts/q007am_propagated_tube_distributed_repair.json`](artifacts/q007am_propagated_tube_distributed_repair.json)

[`artifacts/q007an_repaired_tube_induction.json`](artifacts/q007an_repaired_tube_induction.json)

[`artifacts/q007ao_initialization_interior.json`](artifacts/q007ao_initialization_interior.json)

[`artifacts/q007ap_forward_shadowing.json`](artifacts/q007ap_forward_shadowing.json)

[`artifacts/q011a_periodic_forcing_compatibility.json`](artifacts/q011a_periodic_forcing_compatibility.json)

[`artifacts/q011b_zero_mean_forced_fixed_point.json`](artifacts/q011b_zero_mean_forced_fixed_point.json)

[`artifacts/q011c_forced_spectral_cluster.json`](artifacts/q011c_forced_spectral_cluster.json)

[`artifacts/q011c1_endpoint_localization.json`](artifacts/q011c1_endpoint_localization.json)

[`artifacts/q011c2_heldout_cluster_reissue.json`](artifacts/q011c2_heldout_cluster_reissue.json)

[`artifacts/q011d_forced_quadratic_homological.json`](artifacts/q011d_forced_quadratic_homological.json)

[`artifacts/q011e_forced_quadratic_chart.json`](artifacts/q011e_forced_quadratic_chart.json)

[`artifacts/q011e1_enlarged_residual_window.json`](artifacts/q011e1_enlarged_residual_window.json)

[`artifacts/q011f_multistep_shadowing.json`](artifacts/q011f_multistep_shadowing.json)

[`artifacts/q011f1_heldout_amplitude_reissue.json`](artifacts/q011f1_heldout_amplitude_reissue.json)

[`artifacts/q011g_forced_representation_audit.json`](artifacts/q011g_forced_representation_audit.json)

[`artifacts/q011h_sparse_chart_equivalence.json`](artifacts/q011h_sparse_chart_equivalence.json)

[`artifacts/q008a_tt_storage_prequalification.json`](artifacts/q008a_tt_storage_prequalification.json)

[`artifacts/q008c_wave_qtt_prequalification.json`](artifacts/q008c_wave_qtt_prequalification.json)

[`artifacts/q010_representation_cost.json`](artifacts/q010_representation_cost.json)
