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
