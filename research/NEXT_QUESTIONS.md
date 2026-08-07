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
witness を internalize するが、resonant/near-resonant closure を再監査するまで
採用しない。
一方、\(y\)-independent stripe は非線形写像で不変であり、有限格子 solver oracle
として次へ進める。これは full 2D candidate の代替受理ではない。

## Q005m: manufactured nonidentity oracle

Q006より前に、既知の安定実共役 block、非零 \(R_2\)、mean-like complement、
second-harmonic pair、可制御な二次共鳴を持つ5状態写像で、一般
Kronecker homological solverを検証する。係数回収、real/complex変換、gauge、
非直交 similarity transform 下の左右基底 \(LV=I\) と左右不変性、条件数増大、
厳密共鳴の明示的拒否を全て gate にする。

## Q006s: fixed-leaf stripe quadratic solver oracle — 完了

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

### 結果と判定

全10個の登録 gate は通過し、有限格子 stripe solver oracle として受理した。

- solver assembly: \(\sigma_{\min}=1.9335068\times10^{-2}\)、
  \(\kappa_2=96.0205\)
- 最大 algebraic consistency residual: \(1.2680\times10^{-14}\)
- Richardson Hessian discrepancy: \(4.2948\times10^{-11}\)
- linear residual order: `2.0000001–2.0000204`
- quadratic residual order: `3.0000003–3.0002188`
- 振幅0.01の最大方向別 quadratic/linear residual ratio: `0.056721`
- 100-step quadratic 最大 absolute / perturbation-relative error:
  `1.8726e-6` / `3.9270e-4`
- quadratic/linear 最大 shadow error ratio: `0.016912`
- \(1\times17\to17^2\) lift の1-step差: `0.0`

zero-wave kinetic と second-harmonic Hessian sector はともに非零で、保存モーメント
残差は \(6.66\times10^{-16}\) だった。保存量を固定するとは global mass/momentumを
固定する意味であり、局所 density/momentum perturbation を全てゼロにする意味ではない。

非ゲート診断では、振幅0.1の最大方向別残差比が `0.600863` へ悪化した。また
projected-coordinate drift は quadratic `1.2826e-6`、linear `5.0056e-7` で改善しなかった。
従って証拠範囲は \(N=17,\omega=1.2\)、固定保存量葉、\(y\)-independent、
最大振幅0.01までの登録サンプルに限定する。半径0.01の ball 全体、full 2D、
grid-uniform、存在・一意性、normal attraction は示していない。

## Q006r: resonant/near-resonant mode-added closure audit — 完了

### 問い

Q005 の最初の compatible external resonance を diagonal shear orbit として
internalize したとき、有限回の resonant/near-resonant mode addition で、full 2D
candidate の全 quadratic external Schur block を解像できるか。さらに、その候補は
excluded modes に対する finite-grid linear normal-dominance prequalification を
通過するか。

### 固定条件

- \(N=17,\omega=1.2\)、全質量・全運動量を固定した葉だけを扱う。
- 初期 reduced set は axial first shell
  \((\pm1,0),(0,\pm1)\) の3 hydrodynamic modes と、diagonal
  \((\pm1,\pm1)\) の shear mode の C4・複素共役 orbit とする。
- 初期実座標次元は16とし、mode 順序、C4写像、共役 pairing を artifact に保存する。
- 全 unordered input Schur-block pair と
  \(k_{\rm out}=k_i+k_j\pmod {17}\) を漏れなく列挙する。異なる block の組は
  Kronecker basis、同一 block の組は
  \(e_p\odot e_q=(e_p\otimes e_q+e_q\otimes e_p)/\sqrt{2(1+\delta_{pq})}\)
  の orthonormal symmetric basis を使い、forcing にも同じ正規化を使う。
- \(k_{\rm out}=0\) は \(\ker(\rho,j_x,j_y)\) の6次元 fixed-leaf block に制限する。

### block operator と cluster rule

active output space は \(k\ne0\) で \(\mathbb C^9\)、\(k=0\) で
\(\ker(\rho,j_x,j_y)\) の6次元 kinetic space とする。その埋込み直交基底を \(E_k\)、
active linear block と forcing を

\[
A_{\rm act}(k)=E_k^*A(k)E_k,\qquad
B_{\rm act}=E_k^*B_{ij,k}
\]

とする。現在 selected な active ordered-Schur invariant block への Riesz projector を
\(P_k\)、external projector を \(\Pi_k=I-P_k\) とする。\(Q_k\) は
\(\operatorname{ran}\Pi_k\) の直交基底とし、

\[
A_{\rm ext}(k)=Q_k^*A_{\rm act}(k)Q_k
\]

を external block とする。固定した \(k=0\) の3保存方向は常に active space の外に置く。
\(P_k\) は一般に斜交なので、forcing は \(Q_k^*B_{\rm act}\) ではなく、必ず
\(Q_k^*\Pi_kB_{\rm act}\) で external 成分へ射影する。

unordered input block pair \((T_i,T_j)\) の正規化済み product block を \(K_{ij}\)、
その次元を \(d_{ij}\)、external output 次元を \(d_{\rm ext}\) とする。column-major
vectorization で homological operator と forcing を

\[
\mathcal L_{ij,k}
=I_{d_{ij}}\otimes A_{\rm ext}(k)
-K_{ij}^{\mathsf T}\otimes I_{d_{\rm ext}},
\qquad
b_{ij,k}=\operatorname{vec}(Q_k^*\Pi_kB_{\rm act})
\]

と固定する。全 condition number、rank、forcing sensitivity はこの full block operator
の SVD から計算する。

external eigenvalues は

\[
|\lambda_p-\lambda_q|\le
10^{-8}\max(1,\lVert A_{\rm ext}(k)\rVert_2)
\]

を辺とする graph の connected components に分け、各 component を generalized
ordered-Schur invariant cluster とする。各 cluster の Riesz range の直交基底を
\(Z_c\) とする。

\(\mathcal L=U\Sigma V^*\) の flagged right singular vector \(v_s\) を
\(d_{\rm ext}\times d_{ij}\) 行列 \(X_s\) へ戻し、

\[
G_R=\sum_s X_sX_s^*,\qquad
e_c=\frac{\operatorname{tr}(Z_c^*G_RZ_c)}
{\max(\operatorname{tr}G_R,\epsilon_{\rm mach})}
\]

を response energy とする。\(e_c\ge10^{-8}\) の全 cluster を追加対象にする。
丸めにより該当 cluster がない場合は最大 \(e_c\) の cluster を選び、最大値との差が
\(10^{-12}\) 以下の tie は全て含める。これにより singular vector から追加する output
cluster への写像を固定する。選択した external cluster は \(E_kQ_kZ_c\) で population
space へ埋め戻してから、C4・複素共役 orbit を追加する。

### closure rule

literal な wave-index 加法閉包は要求しない。非共鳴 external output は \(H\) の
coefficient sector として残せるためである。

1. 数値 rank threshold は Q005 と同じ
   \(100\epsilon_{\rm mach}\max(m,n)\sigma_{\max}\) とする。
2. \(\sigma_s\) が rank threshold 以下の left/right singular subspace を numerically
   singular とする。対応する right-response cluster は forcing compatibility に
   かかわらず C4・共役 orbit ごと reduced set に追加する。left singular subspaceへの
   null-forcing ratio は保存するが、追加により internal \(R_2\) sector へ移せるため
   単独では棄却しない。
3. rank threshold より大きく、\(\sigma_s/\sigma_{\max}<10^{-4}\) の singular subspaceを
   near-resonant とする。その left singular basisを \(U_{\rm near}\) とし、
   \(\lVert U_{\rm near}^*b\rVert_2/
   \max(\lVert b\rVert_2,\epsilon_{\rm mach})\ge10^{-10}\) の場合だけ、対応する
   right-response cluster を C4・共役 orbit ごと追加する。
4. round 0 は初期 set の audit とする。最大4回の nonempty addition を許し、その後に
   mandatory terminal re-audit を行う。terminal audit がさらに追加を要求した場合、または
   次の追加で64実 reduced coordinates を超える場合は cap failure とする。
5. 各 nonempty addition 後に、input block、pair table、output cluster、projectorを
   最初から再構築する。
6. normal-gap violation は terminal coefficient closure 後に別判定し、Q006r 内では
   その違反 mode を追加しない。

### 成功条件

結果は二軸で判定する。

**coefficient-solvability gate**

- cap 内で追加が停止する。
- numerically singular external block がゼロ。
- 停止後、登録した near forcing sensitivity が \(\ge10^{-10}\) の全 external block の condition
  number が \(10^4\) 以下で、残る全 external block も \(10^8\) 以下。
- Schur/projector invariance residual、C4/conjugacy error、fixed-leaf conservation
  residual が各 \(10^{-10}\) 以下。
- pair table の列挙件数、各 round の追加 orbit、全 singular values、response energy、
  forcing sensitivity、最悪 block、condition 分位値を保存する。

**finite-grid linear normal-dominance prequalification gate**

- coefficient-solvability gate を通る。
- 停止後に numerically singular external resonance が残らない。
- fixed-leaf spectrum 上で、全 selected eigenvalue の最小 modulus と全 excluded
  eigenvalue の最大 modulus の差
  \(\min|\lambda_{\rm selected}|-\max|\lambda_{\rm excluded}|\ge10^{-6}\) を満たす。
  固定した \(k=0\) の3保存方向はこの比較の selected/excluded の双方から除く。
- selected と external の双方がある各 Fourier sector で local Sylvester separation を
  計算し、その全 sector 最小値が \(10^{-6}\) 以上である。selected local Riesz
  projector norm の全 sector 最大値は100以下とする。異なる Fourier sector は線形写像で
  block diagonal なので、cross-sector projector は作らない。

coefficient-solvability だけを通り finite-grid linear normal-dominance
prequalification を落とした場合は、
「coefficient-solvable finite-grid candidate」と記録するが、full Q006 着手可とは
扱わない。両 gate を通っても「quadratic finite-grid SSM screening passed」とだけ記録し、
存在・一意性や非線形 normal attraction の証明とは呼ばない。

### 結果と判定

study validity gate と coefficient-solvability gate は全て通過したが、finite-grid
linear normal-dominance prequalification は棄却された。

- initial/final real dimension: `16 / 16`
- enumerated unordered block pair: `136 / 136`
- nonempty mode addition: `0`
- terminal numerical singular / near-singular external block: `0 / 0`
- maximum external condition number: `1894.2921`
- maximum homological solve residual: \(1.59\times10^{-15}\)
- maximum Schur/projector/C4/conjugacy/fixed-leaf residual:
  \(4.07\times10^{-15}\)

Q005 の unprojected diagonal witness は
\(\sigma_{\min}=5.10\times10^{-16}\) の `compatible_nonunique` だったが、diagonal
shear を selected に含めた後の8次元 external block は
\(\sigma_{\min}=0.1305687\)、condition number `13.8414` の nonsingular block になった。
従って resonance の internalization は意図どおり機能し、追加 cascade は生じなかった。

一方、selected の最小 modulus は diagonal shear の `0.9699501`、excluded の最大
modulus は \((0,-8)\) near-Nyquist mode の `0.9830465` で、gap は
`-0.0130964` だった。local Sylvester separation `0.1305687` と selected Riesz
projector norm `1.52896` は通過している。従って失敗を branch/projector ambiguity や
coefficient singularityへ転嫁せず、**coefficient-solvable finite-grid candidate** とだけ
記録する。full Q006 は保留する。

## Q006n: near-Nyquist normal-gap refinement audit — 完了

### 問い

Q006r の negative normal gap は \(N=17,\omega=1.2\) だけの有限格子現象か。それとも
同じ16実座標 mode family と標準 periodic BGK に対し、登録した odd-grid refinement
ladder で一貫して現れる near-Nyquist obstruction か。

### 固定条件

- odd grid: \(N\in\{9,17,33,65,129\}\)
- relaxation: \(\omega\in\{1.0,1.2,1.5,1.8\}\)
- 全20条件で全質量・全運動量を固定した葉を使う。
- selected family は各条件の axial first shell
  \((\pm1,0),(0,\pm1)\) の3 hydrodynamic modesと、diagonal
  \((\pm1,\pm1)\) shear の C4・複素共役 orbit、合計16実座標に固定する。
- Q006r と同じ136 unordered input block pair、symmetric-product normalization、
  Riesz external projection、SVD rank/near thresholdを使う。
- Q006n では mode addition を行わない。numerically singular または登録閾値を超える
  materially forced near-singular block は coefficient failure として記録し、
  normal-gap mode も selected に追加しない。
- \(N=9\) は coarse-grid diagnostic、\(N\ge17\) の16条件を refinement gate とする。
- 各 \(\omega\) で \(N^2g_N\)、
  \(g_N=\min|\lambda_{\rm selected}|-\max|\lambda_{\rm excluded}|\) を保存するが、
  有限5点から漸近定理を主張しない。
- parity anchor として全4 \(\omega\) で \(A(\pi,0)\)、\(A(0,\pi)\) を直接評価する。

### 各条件の gate

1. pair count が136で、Schur/projector/C4/conjugacy/fixed-leaf と solve residual が
   各 \(10^{-10}\) 以下。
2. numerically singular external block がゼロ。
3. forcing sensitivity \(\ge10^{-10}\) の near block condition が \(10^4\) 以下、
   その他の全 external condition が \(10^8\) 以下。
4. local selected/external Sylvester separation が \(10^{-6}\) 以上、selected Riesz
   projector norm が100以下。
5. normal gap は符号と最悪 wave/modeを保存する。gap \(\ge10^{-6}\) だけを
   normally-dominant finite-grid pass とする。

### refinement 判定

次を全て満たす場合、「registered near-Nyquist refinement obstruction supported」とする。

- \(N\ge17\) の16条件が coefficient と blockwise projector gate を全て通る。
- 同16条件の normal gap が全て \(-10^{-6}\) 未満。
- 各条件の最大 excluded modulus が axial near-Nyquist index
  \((\pm(N-1)/2,0)\) または \((0,\pm(N-1)/2)\) にある。
- direct Nyquist anchor に \(|\lambda+1|\le10^{-12}\) の mode がある。

\(N=9\) だけが通っても `coarse-grid exception` とし、grid-refinable repair とは扱わない。
逆に、ある \(\omega\) が \(N\ge17\) の全 grid で coefficient gate と
\(g_N\ge10^{-6}\) を通る場合だけ viable family とする。複数なら
\(\min_{N\ge17}g_N\) が最大の \(\omega\)、同値なら小さい \(\omega\) を選ぶ。

obstruction が支持された場合、標準 periodic BGK の full Q006 へは進まず、
checkerboard-damping filter または collision-model modification を新しい事前登録課題にする。
この判定は登録した有限 ladder の反証であり、全 odd \(N\) に対する解析的不可能性証明ではない。

### 結果と判定

study validity は通過したが、封印した clean-obstruction 仮説の判定は
`inconclusive` だった。

- 全20条件で pair count `136`、numerically singular external block `0`
- \(N\ge17\) の negative normal gap: `16 / 16`
- 同16条件で最大 excluded modulus が axial near-Nyquist: `16 / 16`
- coefficient + blockwise projector gate: `13 / 16`
- coefficient failure:
  \((65,1.8),(129,1.5),(129,1.8)\)
- direct Nyquist anchor: 全4 \(\omega\) の \((\pi,0),(0,\pi)\) で通過
- viable \(\omega\): なし
- maximum condition number: `2.4167863e7`（remaining-block ceiling \(10^8\) 未満）
- maximum structural / solve residual:
  `2.6541e-14 / 1.1353e-13`

全 \(\omega\) で \(N^2g_N\) は負の値へ近づいた。\(N=129\) の値は \(\omega\) 順に
`-5.75476, -3.83725, -1.91900, -0.639754` である。この有限 ladder では
near-Nyquist gap failure は一貫しているが、clean obstruction の第一条件である
「16条件が coefficient gate を全通過」を満たさなかったため、事後的に accepted へ
変更しない。

3個の coefficient failure は数値 singularity や solve failure ではない。
materially forced near condition \(10^4\) を超えた主 orbit は、axial acoustic
self-product が second harmonic \((\pm2,0),(0,\pm2)\) を作る8 pair と、axial shear ×
diagonal shear が \((\pm2,\pm1),(\pm1,\pm2)\) を作る8 pair だった。従って次は、
condition number だけでなく forcing と座標正規化を固定してこの scaling を監査する。

## Q006c: small-wave second-harmonic coefficient scaling — 事前登録

### 問い

Q006n の3個の coefficient failure は、small-wave homological operator の真の
second-harmonic near resonance と local-amplitude quadratic curvature の増大を表すか。
それとも、forcing が十分速く消えるため、物理的に固定した座標では bounded な係数を
condition-only gate が過剰に棄却しただけか。

### 固定条件

- odd grid: \(N\in\{17,33,65,129,257\}\)
- relaxation: \(\omega\in\{1.0,1.2,1.5,1.8\}\)
- Q006n と同じ固定保存量葉、16実座標 selected family、Riesz external projection、
  symmetric-product normalization、SVD rank thresholdを使う。
- 各20条件で全136 unordered pairを再列挙する。ただし詳細 scaling の対象は次の
  登録16 pairに固定する。
  1. axial first-shell の acoustic-positive / acoustic-negative の self-product:
     C4・共役 orbit 8 pair、output は \((\pm2,0),(0,\pm2)\)。
  2. axial first-shell shear と diagonal shear の積のうち、output の絶対 index が
     \(\{1,2\}\) となる C4・共役 orbit 8 pair。
- mode addition、filter、collision変更、threshold tuningは行わない。
- fit window は事前に \(N=33,65,129,257\) の4点へ固定し、\(N=17\) は coarse
  diagnostic とする。
- 各 pair で full operator \(L\)、forcing \(b\)、SVD
  \(L=U\Sigma V^*\)、minimum-norm response \(x=L^{-1}b\) を保存する。

### 必須指標

各登録 pair について次を保存する。

- \(\sigma_{\min}(L)\)、\(\sigma_{\max}(L)\)、condition number
- input product eigenvalue と external eigenvalue set の最小複素 detuning
- \(\lVert b\rVert_2\) と最弱左特異方向の forcing
  \(\beta=|u_{\min}^*b|\)
- \(\lVert x\rVert_2\)、solve backward/relative residual
- symbol-local amplitude coefficient \(\lVert x\rVert_2\)
- global-\(\ell_2\)-isometric Fourier coefficient \(\lVert x\rVert_2/N\)
- C4・共役 orbit 内の各指標の relative spread
- 全136 pairの materially forced near witness class と最大 condition

global-\(\ell_2\) normalization は、二次元 \(N\times N\) 格子の unit-norm complex
Fourier basis が local population eigenvectorを \(1/N\) 倍することから固定する。
任意の後付け diagonal balancing を「物理正規化」とは扱わない。

### validity gate

1. 全20条件で pair count が136、登録 target が16 pairである。
2. Schur/projector/C4/conjugacy/fixed-leaf、product invariance、solve residual が
   各 \(10^{-10}\) 以下である。
3. numerically singular external block がゼロで、全登録 target の
   \(\sigma_{\min}\)、detuning、\(\beta\)、response norm が有限かつ正である。
4. orbit 内 relative spread は各指標で \(10^{-8}\) 以下である。
5. \(N=257\) で materially forced near かつ condition \(>10^4\) の pair が新しい
   witness classに現れた場合、completeness gate を失敗とし、登録16 pairだけの clean
   scaling conclusionを出さない。

### scaling 仮説と判定

各 \(\omega\)・各2 orbitについて、orbit medianを使い、固定4点 windowで
\(\log y=c+p\log N\) を最小二乗 fit する。次を全て満たす場合、
`genuine weakly-forced small-k resonance supported` とする。

- \(p_{\sigma_{\min}},p_{\mathrm{detuning}}\in[-2.25,-1.75]\)
- \(p_{\mathrm{condition}}\in[1.75,2.25]\)
- \(p_{\lVert b\rVert}\in[-0.25,0.25]\)
- \(p_{\beta}\in[-1.25,-0.75]\)
- \(p_{\lVert x\rVert}\in[0.75,1.25]\)
- \(p_{\lVert x\rVert/N}\in[-0.25,0.25]\)

この判定なら、near resonance は basis/numerical artifact ではなく、local-amplitude
coordinates では curvature が \(O(N)\) に増える一方、global-\(\ell_2\) coordinatesでは
bounded だと記録する。従って bare condition ceiling は global-\(\ell_2\) 係数の有界性と
同値ではないが、grid-uniform local-amplitude chart の根拠も得られない。

spectral scaling の最初の3項だけを通り forcing/response scalingを落とす場合は
`spectral-only near resonance`、spectral scaling自体を落とす場合は仮説を rejected、
validity/completenessを落とす場合は inconclusive とする。Q006n の封印判定はどの結果でも
遡及変更しない。Q006c が通っても negative normal gap は未解消なので full Q006 は保留する。

## Q006: full 2D fixed-leaf nonzero-mode quadratic parameterization — 保留

### 問い

全質量・全運動量を固定した不変葉上で、mode-added 2D hydrodynamic set を含む dense
candidate chart が residual order 2 → 3 を再現できるか。Q006r の
coefficient-solvability は通過したが、normal-dominance は落ちた。Q006n では viable
family がなく、Q006c の coefficient-scaling 切分けと後続の model-modification gate が
通るまで着手しない。

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
