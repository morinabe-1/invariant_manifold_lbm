# 一次文献調査: 中心・不変・遅い多様体と LBM

調査日: 2026-07-31

## 1. 調査の問い

この研究で最初に明らかにすべき点は次の4つである。

1. \(\Phi(W)=W\circ R\) はどの意味で不変多様体を定めるか。
2. LBM の欲しい流体自由度は、厳密な中心部分空間に入るか。
3. \(W\) と \(R\) を係数ごとに求める際、gauge と共鳴をどう扱うか。
4. TT/TT-cross は何を圧縮でき、何を保証しないか。

検索では査読論文、著者公開稿、出版社ページ、arXiv の原論文を優先した。
解説ページは探索にだけ用い、以下の設計根拠には一次資料を用いた。

## 2. 不変多様体とパラメータ化法

固定点 \(f_\*\) の周りで

\[
F(x)=\Phi(f_\*+x)-f_\*,\qquad F(0)=0,\qquad A=DF(0)
\]

とする。集合 \(M\) が \(F(M)\subseteq M\) を満たせば forward invariant である。
摂動 chart \(K:U\subset\mathbb{R}^{m}\to\mathbb{R}^{N}\) と写像
\(R:U\to\mathbb{R}^{m}\) が

\[
F(K(a))=K(R(a))
\]

を満たせば、\(f_\*+\operatorname{im}K\) は局所的に不変であり、\(R\) はその上の
内部力学を表す。ここでは \(R(a)\in U\) となる評価点、または
\(R(U)\subseteq U\) となる局所領域を考える。以下の LBM 設計では full-state chart
\(W(a)=f_\*+K(a)\) を使うため、同じ式を

\[
\Phi(W(a))=W(R(a))
\]

と書く。この2つの記法を混在させない。これは Cabré–Fontich–de la Llave が
発展させたパラメータ化法の基本方程式である。

主要資料:

- X. Cabré, E. Fontich, R. de la Llave,
  *The Parameterization Method for Invariant Manifolds I: Manifolds Associated
  to Non-Resonant Subspaces*,
  [DOI 10.1512/iumj.2003.52.2245](https://doi.org/10.1512/iumj.2003.52.2245).
- X. Cabré, E. Fontich, R. de la Llave,
  *The Parameterization Method for Invariant Manifolds III: Overview and
  Applications*,
  [DOI 10.1016/j.jde.2004.12.003](https://doi.org/10.1016/j.jde.2004.12.003),
  [著者公開 PDF](https://web.mat.upc.edu/xavier.cabre/docs/inonres3.pdf).

この方法の利点は、多様体の形 \(W\) だけでなく、単純化された内部写像 \(R\) も
同時に求める点にある。

## 3. 離散写像の中心多様体

離散写像における中心部分空間は、線形化 \(A\) の
\(|\lambda|=1\) に属する一般化固有空間である。中心多様体はこの空間に接する
局所不変多様体である。安定方向は \(|\lambda|<1\)、不安定方向は
\(|\lambda|>1\) である。

van den Berg–Hetebrij–Rink は Banach 空間上の離散写像について、中心多様体の
パラメータ化 \(W\) と中心力学 \(R\) を同時に構成し、近似不変性残差から真の解との
誤差を評価する結果も与えている。ただしその a posteriori 評価には、global
\(C^m\) defect、\(C^{m+1}\) bound、smallness、invertibility、spectral hypotheses
が必要である。有限個の sample 上の \(L^2/L^\infty\) residual は経験的 validation
であって、この定理による certificate ではない。

- J. B. van den Berg, W. Hetebrij, B. Rink,
  *The parameterization method for center manifolds*,
  Journal of Differential Equations 269 (2020), 2132–2184,
  [DOI 10.1016/j.jde.2020.01.033](https://doi.org/10.1016/j.jde.2020.01.033),
  [arXiv:1905.00264](https://arxiv.org/abs/1905.00264).
- 同著者,
  *More on the parameterization method for center manifolds*,
  parameter、ODE、reaction–diffusion への拡張,
  [arXiv:2003.00701](https://arxiv.org/abs/2003.00701).

古典的な局所中心多様体は一般に一意ではない。パラメータ化法では中心座標成分、
cutoff、関数空間、gauge を固定することで解を選ぶ。異なる chart は同じ像を
再パラメータ化する場合もあれば、原点で同じ有限 Taylor jet を持ちながら flat な
差を持つ別の局所中心多様体を選ぶ場合もある。したがって「数値解が一意」とだけ
記述せず、何を固定した上での一意性かを明示する必要がある。graph gauge が除くのは
chart の再パラメータ化自由度であり、一般の局所 center-manifold image の非一意性
そのものではない。2020年の定理の一意性は、cutoff/extension 後の固定された global
bounded function class の中で解釈する。

## 4. Gauge と \(R\) の扱い

局所微分同相 \(h\) に対して

\[
\widetilde W=W\circ h,\qquad
\widetilde R=h^{-1}\circ R\circ h
\]

も同じ多様体像を表す。この自由度を残したまま \(W,R\) を同時最適化すると
Jacobian が特異になる。

本設計では、選択モードの左基底を行にもつ \(L\) と右基底 \(V\) を

\[
LV=I_m
\]

となるように構成し、graph gauge

\[
L\bigl(W(a)-f_\*\bigr)=a
\]

を採用する。従って摂動 chart \(K=W-f_\*\) の高次係数 \(K_\alpha\) は

\[
LK_\alpha=0,\qquad |\alpha|\ge 2
\]

を満たす。この gauge では

\[
R(a)=L\bigl(\Phi(W(a))-f_\*\bigr)
\]

であり、固定された chart/cutoff の中で、中心・master 成分を \(R\) に、補空間
成分を \(K\) に振り分ける。これは一般の center-manifold image の一意性主張ではない。

normal-form gauge は内部力学の解釈に有用だが、最初の実装では graph gauge と
混在させない。normal form は dense graph-gauge 解との同値性を確認した後の
別変換とする。

## 5. Homological equation と共鳴

\[
F(x)=Ax+\frac12 B(x,x)+O(\lVert x\rVert^3)
\]

\[
K(a)=W(a)-f_\*=Va+\frac12 H(a,a)+O(\lVert a\rVert^3)
\]

\[
R(a)=\Lambda a+\frac12 G(a,a)+O(\lVert a\rVert^3)
\]

を不変性方程式へ代入すると、二次では

\[
AH+B(V,V)=VG+H(\Lambda\cdot,\Lambda\cdot)
\]

を得る。一般次数 \(p\) では、既知の低次係数から作られる forcing
\(\Gamma_p\) に対して

\[
AK_p+\Gamma_p=K_p\Lambda^{\otimes p}+VR_p
\]

という homological equation を解く。

対角化可能な場合、補空間固有値を \(\mu\)、master 固有値を
\(\lambda_1,\ldots,\lambda_m\)、多重指数を \(\alpha\) とすると、分母は

\[
\mu-\lambda^\alpha,\qquad
\lambda^\alpha=\prod_j\lambda_j^{\alpha_j}
\]

となる。

- 内部共鳴は \(R_\alpha\) に残す。
- 補空間との共鳴は多様体係数を解けなくする。
- 近共鳴は homological operator を悪条件にする。
- 悪条件化した物理モードは reduced coordinates に追加する候補である。

中心固有値が全て \(1\) なら \(1=1^{|\alpha|}\) なので内部項は全次数で共鳴し得る。
従って中心問題で \(R\) を最初から線形に固定してはならない。

## 6. LBM の slow invariant manifold

Packwood–Levesley–Gorban は、連続 Boltzmann 方程式からではなく完全離散の
advection–collision 写像から出発し、slow invariant manifold の不変性方程式を
時間刻みについて展開した。

- D. J. Packwood, J. Levesley, A. N. Gorban,
  *Time Step Expansions and the Invariant Manifold Approach to Lattice
  Boltzmann Models*,
  [DOI 10.1007/978-3-642-14941-2_9](https://doi.org/10.1007/978-3-642-14941-2_9),
  [arXiv:1006.3270](https://arxiv.org/abs/1006.3270).
- A. N. Gorban, I. V. Karlin, A. Y. Zinovyev,
  *Constructive methods of invariant manifolds for kinetic problems*,
  [DOI 10.1016/j.physrep.2004.03.006](https://doi.org/10.1016/j.physrep.2004.03.006).

これは今回の構想に直接つながる。ただし同論文は slow manifold を仮定した
時間刻み漸近展開であり、有限振幅・任意境界・任意外力についての存在証明ではない。
本研究では完全な 1-step map の不変性残差を直接測る。

## 7. なぜ「中心」だけでは流体縮約にならないか

周期境界、一様平衡、正粘性の athermal BGK-LBM を Fourier 変換すると、波数ごとに

\[
A(k)=S(k)C
\]

という \(Q\times Q\) のブロックを得る。\(k=0\) では保存量が
\(\lambda=1\) を持つ。

- D2Q9: 密度と二成分運動量、通常3モード。
- D3Q27: 密度と三成分運動量、通常4モード。

非零波数の shear/acoustic hydrodynamic branches は、粘性により単位円の内側へ
入る。従って空間変動する流れを残すには、低波数の遅い安定部分空間を選ぶか、
全格子の \((\rho,\boldsymbol j)\) を座標とする高次元 hydrodynamic manifold を
扱う必要がある。

分散・散逸・モード同定の主要資料:

- P. Lallemand, L.-S. Luo,
  *Theory of the lattice Boltzmann method: Dispersion, dissipation, isotropy,
  Galilean invariance, and stability*,
  [DOI 10.1103/PhysRevE.61.6546](https://doi.org/10.1103/PhysRevE.61.6546).
- G. Wissocq et al.,
  *An extended spectral analysis of the lattice Boltzmann method: modal
  interactions and stability issues*,
  [DOI 10.1016/j.jcp.2018.12.015](https://doi.org/10.1016/j.jcp.2018.12.015).
- C. Coreixas et al.,
  *Impact of collision models on the physical properties and the stability of
  lattice Boltzmann methods*,
  [DOI 10.1098/rsta.2019.0397](https://doi.org/10.1098/rsta.2019.0397).

固有値の絶対値順だけでは、固有値衝突で流体枝と kinetic 枝を取り違える。
密度、運動量、応力への固有ベクトル射影を使って \(k=0\) から枝を追跡する必要が
ある。

さらに本研究の最初の実験では、偶数幅の D2Q9 周期格子に
\((k_x,k_y)=(0,\pi),(\pi,0)\) の \(\lambda=-1\) checkerboard modes が見つかった。
これらは unit circle selector には入るが、本研究が残したい低波数流体枝ではない。

## 8. D2Q9 と D3Q27 の格子構造

D2Q9 の標準 BGK モデルは次の原論文に遡る。

- Y. H. Qian, D. d'Humières, P. Lallemand,
  *Lattice BGK Models for Navier–Stokes Equation*,
  [DOI 10.1209/0295-5075/17/6/001](https://doi.org/10.1209/0295-5075/17/6/001).

D2Q9 と D3Q27 は、それぞれ D1Q3 の二重・三重 tensor product として扱える。
速度軸を flat な9/27モードとして潰さず、3値の軸因子として保持する設計根拠になる。

- I. V. Karlin, P. Asinari, S. Succi,
  *Matrix lattice Boltzmann reloaded*,
  [DOI 10.1098/rsta.2011.0061](https://doi.org/10.1098/rsta.2011.0061).
- C. Coreixas, B. Chopard, J. Latt,
  *Comprehensive comparison of collision models in the lattice Boltzmann
  framework: Theoretical investigations*,
  [DOI 10.1103/PhysRevE.100.033305](https://doi.org/10.1103/PhysRevE.100.033305).

## 9. TT と TT-cross

TT は多次元配列の unfolding rank を使う安定な分解であり、TT-SVD は dense tensor
が利用できる小規模基準で使える。

- I. V. Oseledets,
  *Tensor-Train Decomposition*,
  [DOI 10.1137/090752286](https://doi.org/10.1137/090752286).

TT-cross は全要素を作らず、選択した entry oracle から tensor を補間する。

- I. V. Oseledets, E. E. Tyrtyshnikov,
  *TT-cross approximation for multidimensional arrays*,
  [DOI 10.1016/j.laa.2009.07.024](https://doi.org/10.1016/j.laa.2009.07.024).
- D. V. Savostyanov,
  max-volume cross の準最適性,
  [DOI 10.1016/j.laa.2014.06.006](https://doi.org/10.1016/j.laa.2014.06.006).
- Z. Qin et al.,
  TT-cross の誤差解析と rank 過指定時の問題,
  [DOI 10.52202/068431-1035](https://doi.org/10.52202/068431-1035),
  [arXiv:2207.04327](https://arxiv.org/abs/2207.04327).

重要なのは、TT-cross が不変性、保存則、positivity、最大誤差を自動的に保証しない
ことである。cross nodes 上の誤差を validation に再利用してはならない。

2026年の direct tensor-network LBM 研究は、streaming の low-rank operator 化が
可能である一方、collision の Hadamard product、小スケール生成、geometry mask が
rank と計算量を増やすことを実測している。elementwise \(1/\rho\) には閉形式がない
ため、同論文は二次 Taylor 近似へ置換している。この点は「inverse の rank 増加を
実測した」という意味ではない。また3D実験は D3Q15 で各 population の空間 MPS を
別々に持つため、D3Q27 の velocity tensorization や本設計の \(W,R\) 係数 TT を
直接検証するものではない。

- L. Gross et al.,
  *Tensor Network Lattice Boltzmann Method for Data-Compressed Fluid
  Simulations*,
  CMAME 460 (2026) 119088, 2026-10-01 issue-dated / 2026-07-31 時点 forthcoming,
  [DOI 10.1016/j.cma.2026.119088](https://doi.org/10.1016/j.cma.2026.119088),
  [arXiv:2512.07615](https://arxiv.org/abs/2512.07615).

従って本研究では TT を「低次元力学を作る根拠」にはせず、まず dense で正しい
\(W,R\) を得てから、その係数または collocation tensor を圧縮する。

## 10. 調査から確定した設計判断

1. 名称を `invariant-manifold` とし、中心は最初の特殊ケースとする。
2. D2Q9 の厳密中心は coefficient solver の解析解付き oracle に使う。
3. 空間流体モデルは moment-based branch tracking で選んだ slow subspace に作る。
4. graph gauge \(L(W-f_\*)=a\) を hard constraint にする。
5. \(R\) の共鳴項を許し、最初から線形に固定しない。
6. dense coefficient solve → TT-SVD → 独立検証 → TT-cross の順に進む。
7. 1-step 平均残差だけでなく、最大残差、保存、positivity、multi-step shadowing、
   normal contraction、条件数を gate にする。
8. D3Q27 は D1Q3 tensor product を保持し、D2Q9 の rank cap を流用しない。
