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

## Q006c: small-wave second-harmonic coefficient scaling — 完了

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

### 結果と判定

全validity gateと全56個のscaling window gate
（8 fit × 7 metrics）が通過し、仮説は登録範囲で支持された。

- study classification:
  `genuine weakly-forced small-k resonance supported`
- registered conditions / fits: `20 / 8`
- pair / target count per condition: `136 / 16`
- maximum orbit relative spread: `1.6046e-10`
- \(N=257\) materially forced near witness: `56`
- 同gridのregistered target外 witness: `0`
- maximum target condition: `1.8260e5`
- maximum all-pair condition: `3.8074e8`
- maximum structural / solve residual: `6.6025e-14 / 1.7609e-13`

固定4点windowで得た8 fitのslope rangeは次のとおりである。

| metric | slope range | registered window |
|---|---:|---:|
| \(\sigma_{\min}\) | `-2.04791 … -1.98123` | `[-2.25,-1.75]` |
| eigenvalue detuning | `-2.04823 … -1.99309` | `[-2.25,-1.75]` |
| condition | `1.97607 … 2.04818` | `[1.75,2.25]` |
| \(\lVert b\rVert\) | `0.00257 … 0.00833` | `[-0.25,0.25]` |
| \(\beta\) | `-0.99574 … -0.98548` | `[-1.25,-0.75]` |
| \(\lVert x\rVert\) | `0.95557 … 1.05216` | `[0.75,1.25]` |
| \(\lVert x\rVert/N\) | `-0.04443 … 0.05216` | `[-0.25,0.25]` |

従って、small-wave near resonanceはbasisやroundoffだけのartifactではない。
weakest singular directionへのforcingは \(O(N^{-1})\) まで弱くなるが、separationが
\(O(N^{-2})\) なので、local-amplitude responseは \(O(N)\) に増える。unit
global-\(\ell_2\) Fourier coordinateでは入力basis自体が \(1/N\) scaleを持つため、
responseは \(O(1)\) となる。

これは「condition ceilingを無視してよい」という結論ではない。全pair最大conditionは
\(N=257\) で旧 \(10^8\) ceilingを超え、local-amplitude chartもgrid-uniformではない。
Q006nの `inconclusive` 判定はそのまま維持する。また4点fitを全odd gridの漸近定理とは
呼ばない。negative near-Nyquist normal gapも未解消である。

## Q006f: conservative checkerboard-filter model modification — 完了

### 問い

global conservation、uniform equilibrium、positivity、low-wave mode geometryを保つ
5点convex filterをBGK step後へ加えることで、near-Nyquist modeを減衰させ、登録した
odd-grid ladder上でnormal dominanceを回復できるか。同時にQ006cで同定した
small-wave coefficient scalingを新しい悪化へ変えずに保てるか。

### 変更する写像

各population \(q\) へ

\[
(\mathcal F_\eta f)_q(x,y)
=(1-\eta)f_q(x,y)
+\frac{\eta}{4}\left[
f_q(x+1,y)+f_q(x-1,y)+f_q(x,y+1)+f_q(x,y-1)
\right]
\]

を周期的に作用させ、

\[
\Phi_{\eta,\omega}=\mathcal F_\eta\circ\Phi_{\mathrm{BGK},\omega}
\]

とする。これは標準BGKとは別の変更モデルである。Fourier multiplierは

\[
\chi_\eta(k)
=1-\eta+\frac{\eta}{2}(\cos k_x+\cos k_y)
=1-\eta\left(\sin^2\frac{k_x}{2}+\sin^2\frac{k_y}{2}\right)
\]

なので、\(A_{\eta,\omega}(k)=\chi_\eta(k)A_\omega(k)\)、二次forcingは
\(\chi_\eta(k_{\rm out})B_{ij,k_{\rm out}}\) とする。

### 固定sweep

- \(\eta\in\{0,0.01,0.02,0.03,0.05\}\)
- \(\omega\in\{1.0,1.2,1.5,1.8\}\)
- odd grid \(N\in\{17,33,65,129,257\}\)
- 合計100条件。\(\eta=0\) はunfiltered baselineで、変更モデル候補には数えない。
- selected familyはQ006n/Q006cと同じ固定16実座標、全質量・全運動量固定葉とする。
- 各条件で全136 unordered pairを再監査し、mode additionは行わない。
- Q006cの登録16 target classとfit windowを変更しない。
- 結果を見て \(\eta\)、\(\omega\)、normal threshold、condition ceilingを追加・調整しない。

### filter algebra gate

1. 全候補でphysical-space weightが非負かつ総和1である。
2. seed `20260809` の64個の正値random statesとuniform equilibriaで、filter単独の
   global mass/momentum residual、constant-state residualを各 \(10^{-13}\) 以下とする。
3. 同試験で出力minimum populationが入力global minimumを下回らない。
4. 32個の登録random wave vectorでphysical filterのFourier actionと
   \(\chi_\eta(k)\) のrelative discrepancyを \(10^{-13}\) 以下とする。
5. \((\pi,0),(0,\pi)\) のcheckerboard anchorは、base \(-1\) modeを
   \(-(1-\eta)\) へ移し、その誤差を \(10^{-12}\) 以下とする。

### 各 \((\eta,\omega)\) family のgate

5 grid全てで次を満たす場合だけ、そのparameter pairをviableとする。

**spectral / low-wave gate**

- normal gap \(\ge10^{-6}\)
- local selected/external Sylvester separation \(\ge10^{-6}\)
- selected Riesz projector norm \(\le100\)
- Schur/projector/C4/conjugacy/fixed-leaf residual \(\le10^{-10}\)
- scalar filter前後のselected invariant subspace principal angle \(\le10^{-10}\)
- selected eigenvalueのphase change \(\le10^{-12}\)
- selected 16 modeのrelative modulus change \(\le5\times10^{-3}\)

**coefficient / scaling gate**

- pair count 136、numerically singular external block 0
- structural、fixed-leaf、solve residual \(\le10^{-10}\)
- 全external condition \(\le10^9\)
- \(N=257\) のmaterially forced near witnessにQ006c登録外classがない
- 各targetのglobal-\(\ell_2\) responseが同じ \((N,\omega)\) のunfiltered Q006c値の
  `1.10` 倍以下
- \(N=33,65,129,257\) の2 orbit fitがQ006cと同じ7個のslope windowを全て通る

### parameter選択と判定

viableな \((\eta,\omega)\) が1個以上あれば、次のlexicographic ruleで一意に選ぶ。

1. 最小の \(\eta>0\)
2. 同じ \(\eta\) では、5 gridのminimum normal gapが最大
3. さらに同値なら小さい \(\omega\)

filter algebra gateと全100条件のstudy validityが通り、選択されたpairが全family gateを
通れば仮説をacceptedとする。計算自体はvalidだがviable pairがなければrejected、
algebra・enumeration・residual gateを落とせばinconclusiveとする。

acceptedでも主張は `filtered finite-ladder prequalification passed` に限る。標準BGKの
Q006n判定は変更せず、全gridに対する定理、非線形normal attraction、manifoldの存在・
一意性、元の物理輸送係数の保存を主張しない。filterはsmall-\(k\) で追加減衰
\(\eta|k|^2/4+O(|k|^4)\) を導入するため、その変更を明記する。acceptedの場合だけ、
選択したfiltered mapでfull 2D dense Q006を新しく事前登録する。

### 結果と判定

100条件のstudy validity、filter algebra、全pair completeness、残差は通過したが、
viable familyは0で、仮説を`rejected`と判定した。全20 familyのcoefficient/scaling gateは
通過し、唯一の失敗はnormal gap \(\ge10^{-6}\) だった。raw gapが正となるfamilyは11個
あったが、最大の5-grid minimum gapも `9.5571481e-9` に留まった。

filterはNyquist modeを減衰させた。一方、十分に減衰したfamilyでは律速が同じ
\((\pm1,\pm1)\) sectorのselected shearとexcluded acousticへ移り、正の11 familyの
5-grid gap slopeは `-4.0284 … -4.0052` だった。このslopeはpost-hoc診断なので、
Q006fの判定やthresholdを変更しない。full Q006は引き続き保留する。

## Q006g: diagonal low-wave shear/acoustic tangency — 完了

### 問い

Q006fの唯一の失敗gateは、対角第一shell内でselected shearとexcluded acousticの
減衰率が低波数で4次接触し、scalar population filterが同一sector内の相対順序と
separation exponentを変えられないことに由来するか。

### 固定scope

- odd grid
  \(N\in\{33,65,129,257,513,1025,2049\}\)
- fit grid
  \(N\in\{129,257,513,1025,2049\}\)
- \(\eta\in\{0,0.01,0.02,0.03,0.05\}\)、
  \(\omega\in\{1.0,1.2,1.5,1.8\}\)
- C4対角orbit \((1,1),(-1,1),(-1,-1),(1,-1)\) を全て評価する。
- 合計140 parameter/grid条件、560 wave recordとする。
- full Brillouin-zone sweep、quadratic coefficient solve、mode addition、threshold tuningは
  行わない。Q006f artifactの100条件は変更せず、比較anchorとしてのみ使う。

各waveでunfiltered symbolのmoment participationからshearとacoustic pairを同定し、
filtered symbolの直接固有分解と

\[
\lambda_{\eta,j}(k)=\chi_\eta(k)\lambda_{0,j}(k)
\]

を独立に比較する。符号付きsame-sector gapを

\[
g_{\eta,N}=|\lambda_{\eta,\mathrm{shear}}|
-\max_{\pm}|\lambda_{\eta,\mathrm{acoustic}\pm}|
\]

と定義し、\(|g_{\eta,N}|\)、\(|g_{\eta,N}|/|\lambda_{\eta,\mathrm{shear}}|\)、
\(N^4g_{\eta,N}\) を保存する。

### validity gate

1. 140条件・560 wave recordに重複や欠落がない。
2. direct eigensystem residualとfiltered/unfiltered eigenvalue matching residualを
   各 \(10^{-11}\) 以下とする。
3. C4 orbit内のgap absolute spreadを \(5\times10^{-13}\) 以下とする。
4. scalar identity
   \(|g_{\eta,N}-\chi_\eta g_{0,N}|\le5\times10^{-13}\) を全recordで満たす。
5. 全記録がfiniteで、各filter multiplierが正である。

### 仮説gate

固定5点fitについて、全20 \((\eta,\omega)\) familyで

- \(\log |g|\) vs \(\log N\) slopeが `[-4.25,-3.75]`
- relative gapのslopeも `[-4.25,-3.75]`
- 最後の4 gridで \(N^4|g|\) のrelative spreadが `0.10` 以下

を要求する。さらに全fit grid・全\(\eta\)で、\(\omega=1.0\) のsigned gapは負、
\(\omega=1.2,1.5,1.8\) は正であることを要求する。

validityと全仮説gateが通れば
`same-sector hydrodynamic fourth-order tangency confirmed` としてaccepted、計算はvalidだが
符号または4次scalingが揃わなければrejected、validity失敗ならinconclusiveとする。

acceptedでも、Q006fを成功へ変更せず、\(10^{-6}\) thresholdを緩和せず、full chartの
存在・一意性やgrid-uniform normal attractionを主張しない。次のfamily変更はQ006g結果後に
別途事前登録する。

### 結果と判定

140条件・560 waveの全validity gateと20 familyの全仮説gateが通過し、
`same-sector hydrodynamic fourth-order tangency confirmed` と判定した。
absolute-gap slopeは `-4.00088 … -3.99980`、relative-gap slopeは
`-4.00092 … -4.00007`、最大\(N^4|g|\) relative spreadは `0.001804` だった。
全\(\eta\)で\(\omega=1.0\)のgapは負、他の3 \(\omega\) は正であり、最大scalar identity
errorは `5.0034e-15` だった。Q006fの棄却とthresholdは変更しない。

## Q006h: first-shell cluster-complete filtered family — 完了

### 問い

Q006gで4次接触したdiagonal acoustic pairをselected側へ昇格し、第一shellの全waveで
3個のhydrodynamic modeを含む24実座標familyを作ると、Q006fと同じfilter sweepで
coefficient solvabilityと有限ladder normal dominanceを同時に満たせるか。

### 固定selected family

\[
\mathcal K_1=\{(n_x,n_y):\max(|n_x|,|n_y|)=1\}
\]

の8 wave indexそれぞれで、`shear`、`acoustic_positive`、`acoustic_negative`を選ぶ。
従ってselected block / real-coordinate countは `24 / 24` である。C4 orbitと共役pairを
構成時に閉じ、全質量・全運動量固定葉を維持する。\(k=0\) conserved modeは含めない。

### 固定sweep

- \(\eta\in\{0,0.01,0.02,0.03,0.05\}\)
- \(\omega\in\{1.0,1.2,1.5,1.8\}\)
- odd grid \(N\in\{17,33,65,129,257\}\)
- 合計100条件。\(\eta=0\) はunfiltered baselineで候補選択から除く。
- 各条件で全 `300` unordered pairを列挙する。
- mode additionは行わず、結果後にblock、parameter、thresholdを追加しない。
- Q006cの16 target pair、7 slope window、global-\(\ell_2\) normalizationを維持する。

### study validity

1. 100条件を重複・欠落なく実行し、全条件でpair count 300、target count 16とする。
2. selected dimension 24、C4/conjugacy closure、fixed-leaf制約を全条件で確認する。
3. Schur/projector/product/fixed-leaf/solve residualを全て \(10^{-10}\) 以下とする。
4. SVD rank threshold、singular/near-singular分類、conditionがfinite ruleで再現できることを
   確認する。numerically singular blockはvalidity失敗ではなくfamily gate失敗とする。
5. 全artifact値をstrict JSONで保存する。全pairを計算し、各条件でpair table、condition
   quantile、最悪pair、materially forced near witnessを保存する。

### 各 \((\eta,\omega)\) family gate

5 grid全てで次を満たす正の\(\eta\) familyだけをviableとする。

**spectral / low-wave**

- normal gap \(\ge10^{-6}\)
- local selected/external Sylvester separation \(\ge10^{-6}\)
- selected Riesz projector norm \(\le100\)
- structural/fixed-leaf residual \(\le10^{-10}\)
- filter前後のselected subspace angle \(\le10^{-10}\)
- selected eigenvalue phase change \(\le10^{-12}\)
- selected relative modulus change \(\le5\times10^{-3}\)

**coefficient / scaling**

- numerical singular block 0、全solve residual \(\le10^{-10}\)
- 全external homological condition \(\le10^9\)
- materially forced near witnessを全件分類・保存する。登録外classの出現自体は失敗にせず、
  condition ceilingと残差で判定する。
- Q006c 16 targetのglobal-\(\ell_2\) responseが、同じ24-mode
  \((N,\omega,\eta=0)\) baselineの `1.10` 倍以下
- \(N=33,65,129,257\) の2 target orbitがQ006cと同じ7 slope windowを全て通る

### parameter選択と判定

viable familyがあれば、Q006fと同じlexicographic ruleを使う。

1. 最小の正の\(\eta\)
2. 同じ\(\eta\)では5-grid minimum normal gapが最大
3. 同値なら小さい\(\omega\)

study validityが通り、viable familyが1個以上なら
`cluster-complete filtered finite-ladder prequalification passed` としてaccepted、validだが
viable family 0ならrejected、validity失敗ならinconclusiveとする。

acceptedでも、これは変更モデル・有限5-grid・24座標familyのprequalificationに限る。
全grid theorem、grid-uniform有限次元family、非線形normal attraction、full chartの存在・
一意性は主張しない。Q006hがacceptedの場合だけ、選択pairを固定してfull 2D dense quadratic
chartを新たに事前登録する。

### 結果

全validity gateが通過し、20 family中6 familyがviableとなったため、登録範囲でacceptedと
判定した。事前登録した選択規則により \((\eta,\omega)=(0.01,1.5)\) を固定する。

- classification: `cluster-complete filtered finite-ladder prequalification passed`
- selected five-grid minimum normal gap: `6.9386924e-5`
- selected maximum external condition: `5.9581662e8`
- selected maximum target response ratio: `0.96477295`
- selected maximum structural/fixed-leaf/solve residual: `8.3841e-14`
- selected material witness: `40`
- witness class count: axial acoustic self `16`、axial shear–diagonal shear `16`、
  diagonal acoustic self `8`

新しい8件は \(N=257\) の対角acoustic self-productから \((\pm2,\pm2)\) を作るblockである。
事前登録どおり全件を分類・保存し、class出現自体を失敗とはしなかった。normal gapは高解像度
側で低下し、conditionも増大するため、有限5-grid prequalificationを越える主張はしない。

## Q006i: filtered full 2D dense quadratic chart — 完了

### 問い

Q006hが選んだ \((N,\eta,\omega)=(17,0.01,1.5)\) の変更D2Q9写像について、全質量・
全運動量を固定した不変葉上の24実座標dense quadratic candidate chartは、linear chartの
二次不変性残差を三次へ改善できるか。

### 固定構成

- gridはodd periodic \(17^2\)、BGK後のpopulation-wise five-point filterは
  \(\eta=0.01\)、relaxationは \(\omega=1.5\) に固定し、再探索しない。
- selected waveは \(\max(|n_x|,|n_y|)=1\) の8点、各waveでshear、acoustic-positive、
  acoustic-negativeを選ぶ。24 complex Fourier blockを共役制約で24実座標へrealifyする。
- 各right modeをunit population normとし、Fourier liftに \(1/(\sqrt2N)\) を使う。
  実座標は各共役pairのmode順 `shear, acoustic_positive, acoustic_negative`、各mode内
  `real, imag` のinterleaved順に固定する。
- 300 unordered coordinate pairをsymmetric-product normalizationで解く。出力waveは
  Fourier selection ruleで一意に定める。
- selected outputへ戻るpairではgraph gauge \(L_sW_2=0\) を課し、tangential forcingを
  \(R_2\) に置く。external成分だけをSylvester solveする。selected外outputでは
  \(R_2=0\) とする。
- zero-wave outputは \(\ker(\rho,j_x,j_y)\) のkinetic 6-spaceだけを許し、保存momentを
  持つmean correctionを禁止する。
- complex coefficientを先に解き、C4/conjugacyを検証してから実physical-spaceの
  symmetric packed dense tensorを構成する。

### 独立微分・algebra validity gate

1. selected block / real dimensionを `24 / 24`、unordered pairを `300` とし、欠落・重複を
   許さない。internal、zero-wave、external second-harmonic pair countを保存する。
2. 全homological blockでoperator rank、\(\sigma_{\min}\)、condition、solve residualを保存し、
   numerical singular blockを0、最大solve relative residualを \(10^{-10}\) 以下とする。
3. homological residual、graph gauge、zero-wave conserved-moment residual、C4 residual、
   conjugacy residual、realification imaginary leakageを各 \(10^{-10}\) 以下とする。
4. analytic filtered-map Hessianを、seed `20260808` の32 conjugacy-compatible direction pair、
   step `0.006, 0.003` のcentered mixed differenceとRichardson extrapolationで独立検証し、
   最大相対差を \(10^{-8}\) 以下とする。homological residualだけで微分を正当化しない。
5. \(R_2\)、zero-wave kinetic correction、axialおよびdiagonal second harmonicのnormとsupportを
   別々に保存する。予測外Fourier support leakageを \(10^{-12}\) 以下とする。
6. 全値をfiniteかつstrict JSONとして保存する。上記validity gate失敗時は、残差campaignの
   数値にかかわらず`inconclusive`とする。

### 局所不変性 gate

- seed `20260809` の未使用64方向をglobal-\(\ell_2\) coordinate normで正規化する。
- 振幅を `0.000625, 0.00125, 0.0025, 0.005, 0.01` に固定する。
- 各方向でfull filtered mapの不変性残差を測り、log-log slopeを保存する。linear chartは
  \(2\pm0.1\)、quadratic chartは \(3\pm0.1\) を全方向で満たす。
- 振幅 `0.01` でquadratic residualをlinear residualの `0.10` 未満とする。
- 全sampleでpopulationを正、global mass/momentum driftを \(10^{-12}\) 以下とする。

### 100-step shadowing gate

seed `20260810` の未使用32方向、初期振幅 `0.01` でfull mapとquadratic reduced mapを100 step
比較する。quadratic chartの最大absolute state errorを \(10^{-5}\) 以下、初期摂動に対する
relative errorを \(10^{-2}\) 以下、linear reduced modelの最大errorの `0.10` 未満とする。
projected-coordinate drift、保存量drift、最小populationは独立に保存する。

### 判定と主張範囲

validity gateが通り、局所不変性とshadowing gateを全て通れば
`N17 filtered full-2D quadratic candidate chart verified` としてacceptedとする。validityは
通るが仮説gateを落とせばrejected、validity失敗ならinconclusiveとする。

acceptedでも、これは固定した変更写像、\(17^2\)、登録有限方向・振幅・100 stepに対する
二次candidate chartの数値検証である。all-grid theorem、grid-uniform family、真の不変多様体の
存在・一意性、半径0.01のball全体、標準BGK写像への主張には拡張しない。

### 失敗時の切分け

1. branch misclassification
2. missing resonant mode
3. real/complex basis conversion
4. derivative error
5. coordinate normalization
6. local candidate-chart domain超過
7. fixed-conservation-leaf constraint 違反

### 結果

全validity gate、残差次数、positivity、shadowingは通過したが、global conservationだけが
登録上限 \(10^{-12}\) を超えたため`Q006i local chart hypothesis rejected`と判定した。

- maximum global conservation drift: `2.7284963e-12`
- linear / quadratic drift: `2.7284963e-12 / 2.7284953e-12`
- residual slope: linear `1.99982 ... 2.00026`、quadratic `2.99973 ... 3.00028`
- maximum quadratic/linear residual ratio: `0.00658935`
- quadratic shadow maximum absolute error: `1.51151e-7`
- quadratic/linear shadow-error ratio: `0.00512138`

失敗は単一gateだが、閾値を変更せず、Q006iを遡及的にacceptedへしない。次に保存量の集約と
full-map各stageを分解する。

## Q006j: float64 global-conservation drift source audit — 完了

### 問い

Q006iの100-step conservation drift \(2.7285\times10^{-12}\) は、通常のNumPy reductionだけで
生じた測定誤差か。それともcollision／filterのfloat64演算が実状態へ蓄積したroundoffか。

### 固定trajectory

- Q006iの \((N,\eta,\omega)=(17,0.01,1.5)\)、24実座標chartを変更しない。
- seed `20260810` の32方向、振幅 `0.01` を使う。
- linear chartとquadratic chartの両方、合計64 trajectoryを100 step追跡する。
- checkpointは `0, 1, 2, 5, 10, 20, 50, 100` とする。
- Q006iの通常写像を再実行し、Q006i artifactの保存driftを再現する。parameter、方向、step、
  thresholdを結果後に変更しない。

### 保存量の独立集約

各stateと各stageでmass、\(P_x\)、\(P_y\) を次の3方法で計算する。

1. Q006iと同じNumPy reduction
2. population寄与を `math.fsum` で集約するfaithful-rounded sum
3. 独立なNeumaier compensated sum

`math.fsum` とNeumaierの各component差を \(5\times10^{-14}\) 以下とする。通常和と補償和の差、
初期値からのsigned drift、drift normを全checkpointで保存する。

### stage分解

各stepをBGK collision、periodic streaming、five-point filterへ分ける。各stage前後の補償保存量
差を記録し、64 trajectory全体で次を監査する。

- streamingはpopulationのpermutationであり、`math.fsum` moment driftを \(5\times10^{-14}\) 以下
- collisionとfilterの1-step drift、符号、最大値、RMS、累積signed contribution
- collision + streaming + filterの累積contributionが100-step total driftを
  \(1\times10^{-13}\) 以下で再構成すること
- linear／quadratic双方で、最大driftを与えるtrajectory、component、stepを保存すること

### roundoff-projection control

診断対照として、各通常full step後に、直前stateとの差として補償和で測ったglobal moment errorを
uniform equilibrium tangentにより固定保存量葉へ射影し戻す。これはexact arithmeticではゼロの
補正であり、Q006i写像の置換やQ006i再判定には使わない。

- projected controlの100-step compensated driftを \(10^{-12}\) 以下
- 各projection correction norm、累積norm、standard trajectoryとの差を保存
- maximum single correction normを \(10^{-11}\) 以下
- positivityを全stateで維持

### validityと判定

64 trajectory、8 checkpoint、100 stage recordに欠落がなく、全値finite、独立補償和が一致し、
stage累積がtotal driftを再構成すればvalidとする。validity失敗は`inconclusive`とする。

validな場合、次の順で分類する。

1. 通常和は \(10^{-12}\) を超えるが `math.fsum` driftが \(10^{-12}\) 以下なら
   `reduction-only conservation measurement failure`。
2. `math.fsum` driftも \(10^{-12}\) を超え、stage累積で再構成され、projection controlが通れば
   `float64 map roundoff accumulation localized`。
3. projection controlまたは登録stage boundを落とせば
   `structural or unresolved conservation defect`。

どの分類でもQ006iの`rejected`、\(10^{-12}\) threshold、保存済みartifactを変更しない。
Q006jは有限64 trajectoryの算術診断であり、数学的な厳密保存や全状態・全stepへの誤差定理を
主張しない。分類後に初めて、保存的算術実装を新しい写像実装として採用するか、元のfloat64写像を
明示したまま次へ進むかを別gateとして事前登録する。

### 結果

全validity gateは通過した。NumPy最大drift `2.7284963e-12` を再現し、`math.fsum`とNeumaierでも
`2.7285042e-12` が残った。streaming driftとstage reconstruction errorは0、collisionの最大累積
寄与は`2.6716420e-12`、filterは`5.1159450e-13`だった。

一様projection controlはmaximum single correction `1.6729733e-15`、positivity維持にもかかわらず、
最大drift `2.1600519e-12` で保存上限を落とした。従って
`structural or unresolved conservation defect`として`rejected`とする。Q006i判定は変更しない。

## Q006k: fixed-leaf projection representability audit — 完了

### 問い

Q006jの一様fixed-leaf projectionは、intended correctionを289 siteへ分散したため各populationで
丸め落ちしたのか。同じglobal moment correctionを固定した3 populationへ局在化すれば、診断対照
として100-step保存driftを \(10^{-12}\) 以下へ制御できるか。

### 固定trajectoryとbaseline

- Q006jと同じ \((N,\eta,\omega)=(17,0.01,1.5)\)、seed `20260810`、振幅0.01を使う。
- linear／quadratic各32、合計64 trajectoryを100 step追跡する。
- 保存量は `math.fsum` とNeumaierで測り、両者のcomponent差を \(5\times10^{-14}\) 以下とする。
- standard mapとQ006jの一様projectionを変更せず再実行し、それぞれの最大driftを
  Q006j artifact値から \(5\times10^{-15}\) 以内で再現する。
- direction、step、projection error、閾値は結果後に変更しない。

### 一様projectionのrepresentability記録

各stepでQ006jと同じintended uniform correction

\[
\delta f(x)=-\frac{1}{N^2}E\,\Delta C
\]

を計算し、次を保存する。ここで \(E\) はuniform equilibrium tangent、\(\Delta C\) はfull step前後の
補償global moment差である。

- intended global moment correctionとそのnorm
- 実際の `corrected - mapped`、changed population count / fraction
- 各entryの \(|\delta f_q|/\operatorname{spacing}(f_q)\) の最小、median、最大
- realized global moment correctionとintended correctionとの差
- 一回補正後に残るlocal moment error

0 correction entryはULP ratio集計から除き、changed countの分母には全 `2601` populationを使う。

### localized 3-population control

固定site \((y,x)=(0,0)\) のpopulation \((q_0,q_1,q_2)\) だけへ一回補正を加える。D2Q9の
\(q_0=(0,0),q_1=(1,0),q_2=(0,1)\) より、full step error
\(e=(e_M,e_x,e_y)\) に対して

\[
\delta f_1=-e_x,\qquad
\delta f_2=-e_y,\qquad
\delta f_0=-e_M+e_x+e_y
\]

と固定する。追加site、反復refinement、別population選択は行わない。各stepでintended／realized
moment correction、残差、correction normを保存する。

### validity gate

1. 64 trajectory × 100 stepをstandard、uniform、localizedの3 controlで欠落なく実行する。
2. Q006jのstandard/uniform最大driftを登録再現誤差内で得る。
3. `math.fsum`とNeumaierの差を \(5\times10^{-14}\) 以下とする。
4. 3-population moment matrixのrankを3、conditionを \(10\) 以下、solve residualを
   \(10^{-15}\) 以下とする。
5. 全値finiteかつstrict JSONとして保存する。失敗時は`inconclusive`とする。

### 仮説gateと判定

次を全て満たす場合だけ
`uniform projection representability failure localized`としてacceptedとする。

- uniform projectionの実現global correction errorが0でないstepを1件以上観測する
- localized controlの100-step最大補償drift \(\le10^{-12}\)
- localized maximum single correction norm \(\le10^{-11}\)
- localized／standard maximum state difference \(\le10^{-10}\)
- 全localized stateのpopulationが正

validだが仮説gateを落とせば`localized correction does not resolve projection failure`として
rejected、validity失敗ならinconclusiveとする。acceptedでも、固定site補正はtranslation／C4
symmetryを破る診断対照にすぎず、本番写像、Q006i再判定、将来chartへ採用しない。Q006jの
`rejected`と全thresholdも変更しない。成功した場合だけ、local collisionとfilterを対称な
conservative arithmeticで実装する別gateを事前登録する。

### 結果

全validity／hypothesis gateを通過し、
`uniform projection representability failure localized`としてacceptedとした。

- uniform realization error: `6400 / 6400` step、maximum `5.7125343e-14`
- changed entries: minimum `0`、maximum `2601`、mean `1563.0384`
- ULP ratio: minimum `4.8020027e-20`、median-of-medians `1.5747789`、maximum `1.8158401`
- localized maximum drift: `1.5115007e-16`
- maximum localized correction / standard difference: `5.9292511e-14 / 1.0385189e-13`

acceptedでもfixed-site controlはtranslation／C4を壊す診断対照であり、production mapへ採用しない。
また、全uniform correctionがsub-ULPだったとは主張しない。Q006i／Q006jの判定は維持する。

## Q006l: stagewise state-covariant conservative arithmetic — 完了

### 問い

Q006kの固定site／fixed-population依存を除き、collisionとfilterの各stageでstateから共変に選ぶ
anchorとC4共変なpopulation right inverseを使う一回補正は、保存上限とtranslation／C4
equivarianceを同時に満たすか。

### 固定trajectoryとcontrols

- \((N,\eta,\omega)=(17,0.01,1.5)\)、seed `20260810`、振幅0.01、100 stepを維持する。
- linear／quadratic各32、合計64 trajectoryを使う。
- standardとQ006k fixed-site localized controlを変更せず再実行し、最大drift
  `2.7285041507210106e-12` と `1.5115007100657805e-16` を各 \(5\times10^{-15}\) 以内で再現する。
- 第3 controlだけをstagewise state-covariant arithmeticとし、結果後にstage、anchor rule、
  right inverse、反復回数を変更しない。streamingは変更しない。

### anchorとpopulation correction

raw collision後とraw filter後の各stateでrest population \(f_0(y,x)\) が最大のsiteをanchorにする。
各stageで最大値と第2最大値のgapを保存し、全stepでgap \(\ge10^{-12}\) を要求する。実装上のtieは
row-major最初を返すが、tieまたはgap不足はvalidity failureとし、科学判定には使わない。

site-local conserved-moment matrixを \(C\in\mathbb R^{3\times9}\) とし、固定right inverse

\[
G=C^T(CC^T)^{-1},\qquad CG=I_3
\]

を使う。collision前／raw collision後、streaming後／raw filter後の補償global moment errorを
それぞれ \(e_{\rm coll},e_{\rm filt}\) とし、各stageのanchor 9 populationsへ
\(\delta f=-Ge\) を一回だけ加える。その後に次stageへ進む。refinement、別anchor、別right inverseは
使わない。

### symmetry audit

各64×100 stepのcollision／filter correction operatorを次のgeneratorへ適用する。

- periodic translation: \((\Delta y,\Delta x)=(1,0),(0,1)\)
- C4 quarter-turn: spatial quarter rotationと対応するD2Q9 population permutation

変換前に各stageを補正してからstateを変換した結果と、stage前／raw stage後stateを変換してから
anchor選択・補正した結果のglobal-\(\ell_2\) 差を保存する。anchor indexもgeneratorどおり移ることを
確認する。

### validity gate

1. 64 trajectory × 100 step × 3 controlを欠落なく実行する。
2. standard／fixed-site driftを登録値から \(5\times10^{-15}\) 以内で再現する。
3. `math.fsum`とNeumaierのcomponent差を \(5\times10^{-14}\) 以下とする。
4. collision／filter双方の全anchor gapを \(10^{-12}\) 以上、anchor covariance failureを0とする。
5. \(G\) のconditionを10以下、\(\lVert CG-I\rVert_2\le10^{-14}\) とする。
6. 全値finiteかつstrict JSONとして保存する。失敗時は`inconclusive`とする。

### 仮説gateと判定

次を全て満たす場合だけ
`covariant anchor correction controls registered drift`としてacceptedとする。

- stagewise covariant controlの100-step maximum compensated drift \(\le10^{-12}\)
- collision／filterを通じたmaximum single correction norm \(\le10^{-11}\)
- covariant／standard maximum state difference \(\le10^{-10}\)
- translationおよびC4 correction equivariance error \(\le10^{-13}\)
- 全covariant stateのpopulationが正

validだが仮説gateを落とせば`covariant correction fails conservation or symmetry gate`としてrejected、
validity失敗ならinconclusiveとする。acceptedでも、各stageのglobal residual、unique argmax、登録有限
軌道に依存する非滑らかな算術controlである。production mapやQ006i再判定へ直ちに採用せず、full
chartの残差・shadowingをこの変更写像で再監査する前に、map定義と微分可能領域を別途事前登録する。

### 結果

全validity／hypothesis gateを通過し、
`covariant anchor correction controls registered drift`としてacceptedとした。

- covariant maximum drift: `1.1368684e-13`
- minimum collision / filter anchor gap: `1.6348855e-9 / 1.2466926e-9`
- anchor covariance failure: `0`
- translation / C4 equivariance error: `0 / 0`
- maximum correction / standard difference: `1.8963156e-14 / 1.1557707e-13`

acceptedはunique-anchorを保った登録有限trajectoryに限る。uniform equilibriumでは289-way tieとなる
ため、production map、Taylor微分、Q006i再判定へは進めない。

## Q006m: equivariant unique-anchor differentiability obstruction — 完了

### 問い

Q006lのunique-site anchor selectorは、周期translationに不変な一様平衡へequivariantかつ連続・
微分可能に延長できるか。それとも有限群作用だけで不可能と判定できるか。

### 解析設定

site集合を \(X=\mathbb Z_{17}\times\mathbb Z_{17}\)、translation群を \(G=X\) とする。population
stateへの作用を \(T_g\)、siteへの作用を \(g\cdot x=x+g\) とする。unique-site selector
\(s(f)\in X\) がequivariantなら

\[
s(T_gf)=g\cdot s(f)
\]

を満たす。一様平衡 \(f_*\) は全 \(g\) で \(T_gf_*=f_*\) なので、equivarianceは
\(s(f_*)=g\cdot s(f_*)\) を全 \(g\) に要求する。

### 固定監査

1. \(17^2\) uniform equilibriumで \(q_0\) maximum multiplicityを289、gapを0として直接計算する。
2. translation generator \((1,0),(0,1)\) それぞれについて、固定site数を全289 site列挙して0とする。
3. uniform stateが両generatorでbitwise invariantであることを確認する。
4. row-major tie breakが選ぶ \((0,0)\) は両generatorでcovarianceを破ることを直接記録する。
5. C4は補助診断として記録するが、translation contradictionだけでobstructionを判定する。

### 振幅縮小診断

- Q006lと同じseed `20260810` の32方向をlinear／quadratic chartで使う。
- amplitudeを `1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7` に固定する。
- 各初期stateのraw collision後とraw filter後について、最大 \(q_0\) multiplicity、top-two gap、anchorを
  保存する。filter入力はuncorrected collision後のperiodic streamingとする。
- 各directionで \(+a\) と \(-a\) を別々に測り、anchor一致率とgapを記録する。
- 各stage・符号についてamplitudeごとのmaximum gapが有限で、最小amplitudeのmaximum gapが
  最大amplitude値の \(10^{-4}\) 以下であることを要求する。これはgap→0の有限ladder診断であり、
  漸近fitや微分不可能性の証明には使わない。

### validityと判定

全384 direction-amplitude record（32 direction × 2 chart × 6 amplitude、各recordに \(\pm\) 2 state、
合計768 signed state）と2 stageを欠落なく実行し、全stateをpositive、全値finite、strict JSONとする。
uniform equilibrium、群作用、
enumerationのいずれかが不整合なら`inconclusive`とする。

次を全て満たす場合、
`equivariant unique-anchor obstruction confirmed`としてacceptedとする。

- base multiplicity 289、gap 0
- 2 translation generatorのcommon fixed siteが0
- uniform stateのgenerator invariance error 0
- row-major selectorのanchor covariance failureが2 / 2
- 振幅縮小gap gateが全chart／stage／signで通る

validだがいずれかを落とせば`unique-anchor obstruction not established`としてrejected、validity失敗は
inconclusiveとする。acceptedはunique-site selector classだけを排除し、全てのtranslation-equivariant
conservative arithmeticを排除しない。Q006lの有限軌道accepted、Q006i／Q006jの判定も変更しない。
acceptedなら次に、anchorを持たないsmooth correctionか、明示的なfloating-point forward-error budgetを
比較するgateを事前登録する。

### 結果

全validity／hypothesis gateを通過し、
`equivariant unique-anchor obstruction confirmed`としてacceptedとした。

- uniform \(q_0\) maximum multiplicity / gap: `289 / 0`
- 2 generatorのfixed-site count: `0 / 0`
- uniform translation invariance error: `0`
- row-major covariance failure: `2 / 2`
- direction-amplitude / signed-state / stage record: `384 / 768 / 1536`
- failed gap ladder: `0 / 8`
- maximum gap ratio: `1.0052062e-5`
- minimum population: `0.0275189`

translationで固定されたuniform stateにequivariant selectorの値を置くには、site側にも同じtranslationの
固定点が必要だが、そのようなsiteは存在しない。従ってunique-site selectorはuniform equilibriumで
定義すらできず、連続・微分可能な延長も不可能である。有限振幅ladderはこの厳密な固定点矛盾の証明
ではなく、Q006lで使った \(q_0\) gapが平衡へ向かって縮小する補助診断である。

## Q006o: anchor-free correction versus forward-error budget — 完了

### 問い

Q006lの非滑らかなunique-anchor correctionを採用せず、Q006jのanchor-free uniform projectionを使う
べきか。それとも、標準のsmooth・equivariant写像を変更せず、登録trajectoryの保存driftを明示的な
float64 ULP budgetで管理する方が妥当か。

### 固定設定

- grid、model: \(17^2\)、\(\omega=1.5\)、\(\eta=0.01\)
- chart: linear／quadratic各32方向、seed `20260810`、amplitude `0.01`
- horizon: 100 step
- controls: unmodified standard map、Q006jのuniform minimum-norm fixed-leaf projection
- 保存量測定: `math.fsum`を主測定、Neumaier和を独立照合
- collisionとfilterをconservation-sensitive stage、streamingをexact permutationとして扱う
- Q006lのanchor correctionとQ006kのfixed-site controlは比較対象へ入れない

Q006jのstandard／uniform maximum driftをそれぞれ
`2.7285041507210106e-12`／`2.1600518690316044e-12`、trajectory数64、step数6400として
許容誤差 `5e-15` 以内で再現する。再現できなければvalidity failureとする。

### 登録forward-error budget

保存moment matrixを \(C\in\mathbb R^{3\times9}\) とし、各初期stateについてcomponent scaleを

\[
S_c(f_0)=\sum_{x,q}|C_{cq}f_{0,x,q}|
\]

とする。`numpy.spacing`でこのscaleの1 ULPを \(u_c=\operatorname{spacing}(S_c)\) と定義し、step \(t\) の
componentwise operational budgetを

\[
B_c(t)=2t u_c
\]

に固定する。係数2は、1 stepにcollisionとfilterの2 conservation-sensitive stageがあることだけから
決め、観測driftからfitしない。全64 trajectory × 100 step × 3 component、合計19,200 checkで

\[
|Q_c(f_t)-Q_c(f_0)|\le B_c(t)
\]

を要求し、最大utilization、witness、component別final budgetを保存する。budgetの非自明性を保つため、
全trajectory・componentで最大final budgetを `1.2e-11` 以下とする。このbudgetは登録float64実装の
operational envelopeであり、任意state・任意horizonに対する丸め誤差定理とは呼ばない。

### uniform projectionの選択条件

uniform projectionを標準写像より選ぶには、次を両方要求する。

1. worst drift improvement factor
   \(D_{\rm standard}/D_{\rm uniform}\ge2\)
2. 全6,400 stepでprojection後のremaining local `fsum` driftがexactly zero

一方でも落とせば、uniform projectionは選ばない。これは既存 \(10^{-12}\) thresholdを変更して
projectionを成功扱いするためのgateではない。

### validityと判定

次をvalidity gateとする。

- 64 trajectory、6,400 trajectory-step、19,200 component-budget checkの完全列挙
- Q006j standard／uniform driftの登録値再現
- streaming `fsum` incrementが0
- `math.fsum`／Neumaier差が `5e-14` 以下
- 全state positive、全値finite、strict JSON

validity通過後、全standard budget checkが通り、最大final budgetが `1.2e-11` 以下で、uniform selection
条件を満たさない場合は、
`unmodified equivariant map with registered forward-error budget preferred`としてacceptedとする。
standard budgetも通りuniform selection条件も満たす場合は
`smooth uniform correction preferred`としてacceptedとする。standard budgetが破れ、uniformも選択条件を
満たさなければ`neither anchor-free arithmetic policy passes`としてrejected、validity failureは
inconclusiveとする。

acceptedでもQ006i／Q006jの封印判定や \(10^{-12}\) thresholdを遡及変更しない。結果は今後の写像定義を
選ぶ有限軌道policy gateである。standard budget方針が選ばれた場合だけ、次の別gateでQ006iのchart
residual／shadowingと保存判定をdual-reporting（旧thresholdと登録ULP budget）により再監査する。

### 結果

全validity gateとstandard policy gateを通過し、uniform policy gateは2個とも落ちた。従って
`unmodified equivariant map with registered forward-error budget preferred`としてacceptedとした。

- trajectory / step / component check: `64 / 6400 / 19200`
- standard budget violation: `0`
- maximum utilization: `0.5`
- maximum final component budget: `1.1368684e-11`
- standard / uniform maximum drift: `2.7285042e-12 / 2.1600519e-12`
- uniform improvement factor: `1.2631660`
- uniform exact-zero remaining drift: `0 / 6400`
- maximum remaining local drift: `5.7125343e-14`
- minimum population: `0.0275271`

standard mapを変更せず有限trajectory上のroundoffを明示的に管理する方針を選ぶ。ただしこの結果は
arithmetic policyの選択であり、Q006i／Q006jの旧 \(10^{-12}\) thresholdとrejected判定を変更しない。

## Q006p: Q006i dual-reporting integration audit — 完了

### 問い

Q006iのfull-2D quadratic chartについて、旧 \(10^{-12}\) conservation gateを失敗のまま保持しつつ、
Q006oのregistered forward-error policyを独立欄で通過させられるか。その場合、過去の判定を改変せずに
candidate chartの次段階へ進む根拠を作れるか。

### 固定設定

Q006iとQ006oをそれぞれsealed runnerから再実行し、artifactを入力データとして使わない。

- grid \(17^2\)、\(\omega=1.5\)、\(\eta=0.01\)
- reduced dimension 24、state dimension 2601、quadratic pair 300
- shadow seed `20260810`、linear／quadratic各32方向、amplitude `0.01`、100 step
- original conservation threshold `1e-12`
- Q006o component budget \(B_c(t)=2t\,\operatorname{spacing}(S_c)\)
- Q006l unique-anchor、Q006k fixed-site、Q006j uniform correctionはchart mapへ適用しない

### alignmentと再現

次をvalidity gateとする。

1. Q006i／Q006o両studyのvalidityが`passed`。
2. grid、\(\omega\)、\(\eta\)、seed、amplitude、step、chart種別が一致。
3. Q006i linear／quadratic各32方向とQ006oの対応方向のmaximum absolute differenceが0。
4. Q006i original drift `2.728496323152741e-12`、Q006o `math.fsum` drift
   `2.7285041507210106e-12`を各 `5e-15` 以内で再現。
5. 両driftの差が `5e-15` 以下。
6. Q006i original global-conservation gateはthreshold `1e-12`、`passed=false`のまま。
7. 全値finite、strict JSON。

### dual decision

Q006iの8 hypothesis gateを次の2欄に固定して報告する。

- original column: 既存8 gateをそのまま保存し、global conservationだけがfailed、他7 gateがpassed。
- policy column: global conservationだけをQ006o standard policyの
  `budget_violation_count=0`、maximum utilization `<=1`、maximum final budget `<=1.2e-11`で評価する。
  他7 gateはQ006iの値・threshold・判定を変更せず再利用する。

original failed gate数が1、policy failed gate数が0であり、Q006o uniform policyがfailed、standard policyが
passedなら、`dual reporting supports unmodified-map chart continuation`としてacceptedとする。original
gateも通ったと書き換えたり、Q006iをacceptedへ変更したりしてはならない。policy columnが1個でも
失敗すれば`forward-error policy does not clear Q006i continuation`としてrejected、validity failureは
inconclusiveとする。

acceptedは同一の登録64 trajectoryに対するintegration判定に限る。all-state conservation theoremや
SSM existenceを主張しない。acceptedなら次に、別seed・amplitude・horizonでQ006o budgetをholdout検証する
gateを事前登録し、それを通るまでdegree continuationへ進まない。

### 結果

全validity gateとdual decision gateを通過し、
`dual reporting supports unmodified-map chart continuation`としてacceptedとした。

- direction alignment record / maximum error: `64 / 0`
- Q006i original / Q006o `math.fsum` drift:
  `2.728496323152741e-12 / 2.7285041507210106e-12`
- drift difference: `7.82756826945652e-18`
- original failed gate: `1`（`global_conservation`）
- policy failed gate: `0`
- standard / uniform policy: `passed / failed`
- budget violation / maximum utilization: `0 / 0.5`
- maximum final component budget: `1.1368683772161603e-11`

Q006iのoriginal columnと`rejected`判定は変更していない。policy columnはglobal conservationだけを
Q006o policyへ置換し、他7 gateを値・threshold・判定まで保持した。同じ64 trajectoryを使うintegration
結果なので、独立holdoutを通過するまではdegree continuationへ進まない。

## Q006q: independent forward-error holdout — 完了

### 問い

Q006oで固定した

\[
B_c(t)=2t\,\operatorname{spacing}(S_c(f_0))
\]

を変更せず、Q006pまでに使っていないseed・amplitude・horizonでもunmodified standard mapの保存driftを
覆えるか。

### 固定設定

Q006iと同じfull-2D model、すなわちgrid \(17^2\)、\(\omega=1.5\)、\(\eta=0.01\) と24実座標の
linear／quadratic chartをsealed runnerから新規構築する。artifactを入力せず、uniform projection、
Q006k fixed-site control、Q006l unique-anchor controlは適用しない。

| scenario | direction seed | amplitude | horizon | directions per chart | trajectories |
|---|---:|---:|---:|---:|---:|
| long-horizon | `20260811` | `0.005` | 200 | 32 | 64 |
| large-amplitude | `20260812` | `0.02` | 50 | 32 | 64 |

各scenarioでは同じ32方向をlinear／quadratic chartで共有するが、2 scenario間およびQ006o seed
`20260810`とは方向を共有しない。合計128 trajectory、16,000 trajectory-step、48,000 component checkを
全列挙する。amplitude `0.02`はarithmetic policyのstress testにだけ使い、その振幅でchart invarianceや
shadowingの有効性を主張しない。

### 凍結するbudgetと記録

各trajectoryの初期stateだけから

\[
S_c(f_0)=\sum_{x,q}|C_{cq}f_{0,x,q}|,
\qquad
B_c(t)=2t\,\operatorname{spacing}(S_c(f_0))
\]

を計算する。係数2、`numpy.spacing`、component scale、`math.fsum`主測定、Neumaier独立測定をQ006oから
変更しない。各step・各componentのsigned drift、absolute drift、budget、utilization、pass/failを保存し、
scenario／chart／direction／componentごとの最大witnessを報告する。観測値から係数・thresholdをfitしない。

### validity gate

次を全て要求する。

1. grid、\(\omega\)、\(\eta\)、chart種別、2 seed、2 amplitude、2 horizonが登録値と一致。
2. 128 trajectory、16,000 trajectory-step、48,000 component checkを完全列挙。
3. 各方向のnorm errorが `5e-15` 以下で、Q006oおよび他scenarioとexact duplicateがない。
4. stagewise collision → streaming → filterと`full_map`のmaximum absolute differenceが0。
5. streamingのmaximum `math.fsum` incrementが0、`math.fsum`／Neumaierのmaximum component differenceが
   `5e-14` 以下。
6. 全初期・rollout stateのpopulationが正、全数値finite、strict JSON。

validity failureは`inconclusive`とし、policyの反証に数えない。

### holdout decision

各scenarioを別々に、かつaggregateでも判定する。次を全て満たす場合だけ
`independent holdout supports registered forward-error policy`としてacceptedとする。

1. 全48,000 component checkでbudget violationが0。
2. 各scenarioおよびaggregateのmaximum utilizationが1以下。
3. 全trajectoryのmaximum final component budgetが `2.4e-11` 以下。

validだが1項目でも失敗すれば
`registered forward-error policy rejected by independent holdout`としてrejectedとする。失敗後に係数2や
budget上限を調整せず、最初のviolation witnessとscenarioを固定して原因を分解する。acceptedでも、これは
登録した2 scenarioのfinite-trajectory operational envelopeであり、all-state／all-horizon roundoff theorem、
chartの存在・一意性、amplitude `0.02`でのinvarianceを主張しない。acceptedの場合だけQ007 degree
continuationを事前登録する。

### 結果

全validity gateとholdout policy gateを通過し、
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

Q006oの式・係数・上限を変更せず、2 scenarioの両方とaggregateが通過した。これで登録有限trajectoryの
算術policyに対する独立holdoutを完了する。all-state／all-horizon theoremやamplitude `0.02`でのchart
invarianceは引き続き主張しない。

## Q007a: cubic homological-family prequalification — 完了

### 問い

Q006iの24実座標clusterについて、3次係数を構築する前に必要な全order-three homological blockは、
登録grid上で一意に解ける非共鳴operator familyになっているか。

### 固定設定と列挙

- grid \(17^2\)、\(\omega=1.5\)、\(\eta=0.01\)
- Q006iと同じ8 wave × 3 hydrodynamic mode、合計24 complex conjugate-constrained mode
- unordered input tripleは
  \(\binom{24+3-1}{3}=2600\) 個を`combinations_with_replacement`順に完全列挙
- input triple \((i,j,k)\) のmultiplierは
  \(\mu_{ijk}=\lambda_i\lambda_j\lambda_k\)
- output waveは3入力waveの周期和とし、permutation multiplicity `1 / 3 / 6`を保存
- artifactを入力せず、mode、filtered Fourier symbol、fixed-leaf basisをsealed runnerから再構築

output sectorごとのoperatorを次に固定する。

\[
\begin{cases}
E_k^*\bigl(A(0)-\mu_{ijk}I\bigr)E_k,
& k_{\rm out}=0,\\
\begin{bmatrix}
A(k_{\rm out})-\mu_{ijk}I & -V_{\rm sel}\\
L_{\rm sel} & 0
\end{bmatrix},
& k_{\rm out}\in K_{\rm selected},\\
A(k_{\rm out})-\mu_{ijk}I,
& \text{otherwise}.
\end{cases}
\]

zero-wave blockはQ006iと同じ6次元fixed-leaf kinetic basis、internal blockは3 selected modeとgraph gaugeを
持つ12次元block、external blockは9次元とする。

### SVD、rank、near-resonance

全blockでfull singular-value listを保存する。数値rank thresholdは既存gateと同じ

\[
\tau=100\epsilon_{\rm mach}\max(m,n)\sigma_{\max}
\]

とし、\(\sigma_{\min}\le\tau\) をnumerically singularとする。nonsingular blockでは
\(\kappa_2=\sigma_{\max}/\sigma_{\min}\) を保存し、
\(\sigma_{\min}/\sigma_{\max}<10^{-4}\) をnear-resonant diagnosticとして数える。near-resonant count自体は
棄却条件にせず、condition ceilingで判定する。

### validity gate

1. 同じassemblyでorder-two 300 pairを独立再列挙し、Q006iの
   zero/internal/external count `36 / 108 / 156`、numerically singular `0`を再現する。
2. order-two minimum singular value `0.00015502435597333105` とmaximum condition
   `14513.930547954875`のrelative errorを各 `1e-10` 以下にする。
3. order-three triple countを2600、欠落・重複を0とし、3 output sectorを全て1件以上含める。
4. 各tripleの共役tripleが存在し、output wave、multiplier、singular valuesのconjugacy relative errorを
   `1e-10` 以下にする。
5. output-wave count tableが90度回転と共役でexactに閉じる。
6. 全値finite、全conditionがpositiveまたはsingular時だけ`null`、strict JSON。

validity failureは`inconclusive`とし、order-three resonanceの証拠には使わない。

### hypothesis gate

validity通過後、次を両方満たす場合だけ
`order-three homological family prequalified on registered grid`としてacceptedとする。

1. numerically singular blockが0。
2. zero-wave、internal、externalを含む全nonsingular blockのmaximum conditionが `1e9` 以下。

validだが一方でも失敗すれば
`order-three homological obstruction on registered grid`としてrejectedとする。acceptedはoperatorの
有限grid非共鳴性だけを意味し、cubic forcing、係数、独立微分、残差4次化、shadowing改善、SSM存在を
まだ主張しない。acceptedの場合だけQ007bを詳細に事前登録する。

### 結果

全validity／hypothesis gateを通過し、
`order-three homological family prequalified on registered grid`としてacceptedとした。

- order-2 pair / sector count: `300 / 36 / 108 / 156`
- order-2 minimum singular / maximum condition:
  `0.00015502435597333105 / 14513.930547954875`
- order-3 triple / sector count: `2600 / 108 / 1044 / 1448`
- order-3 numerical singular / near-resonant block: `0 / 24`
- order-3 minimum singular / maximum condition:
  `0.00020787972673242753 / 10821.814847751179`
- minimum rank margin: `4.6239929774875706e8`
- conjugate multiplier / singular-value relative error:
  `2.9151992739486325e-16 / 2.8470292165304574e-15`
- output wave count / rotation / conjugacy failure: `49 / 0 / 0`

Q007aはoperator-only finite-grid prequalificationである。3次forcing、係数、残差4次化、shadowing改善は
未検証なので、次のQ007bを独立gateとして扱う。

## Q007b: cubic coefficient and residual continuation — 事前登録

### 問い

全3次forcingとcubic chart／reduced mapを構築し、独立微分、homological residual、held-out残差次数
`3 → 4`、100-step shadowingをquadratic chartから改善できるか。

### 固定設定と表現

- grid \(17^2\)、\(\omega=1.5\)、\(\eta=0.01\)、24実reduced coordinates
- Q006iのquadratic chart、\(\Lambda\)、\(G=R_2\) をsealed runnerから再構築
- Q007aと同じ2,600 unordered complex-mode tripleを全て解く
- Q006oで選んだunmodified standard mapを使い、uniform／fixed-site／unique-anchor correctionは使わない
- 3次係数はsymmetric complex Fourier-fiberとして保存し、permutation multiplicity `1 / 3 / 6`を使う
- 物理空間の \(2601\times24^3\) full dense tensorはmaterializeせず、unique triple係数、output wave、
  coefficient hash、実評価結果をartifactへ保存する

chartとreduced mapの規約を

\[
W_3(a)=W_2(a)+\frac16T[a,a,a],\qquad
R_3(a)=R_2(a)+\frac16K[a,a,a]
\]

に固定する。

### 解析的3次forcing

各triple \((i,j,k)\) で、3次homological forcingを

\[
\begin{aligned}
F_{ijk}^{(3)}={}&D^3\Phi[V_i,V_j,V_k]\\
&+D^2\Phi[H_{ij},V_k]+D^2\Phi[H_{ik},V_j]+D^2\Phi[H_{jk},V_i]\\
&-H[G_{ij},\Lambda e_k]-H[G_{ik},\Lambda e_j]-H[G_{jk},\Lambda e_i]
\end{aligned}
\]

とし、Q007aと同じoperatorで \((T_{ijk},K_{ijk})\) を解く。D2Q9 equilibriumのrest stateでは、
保存moment \(m_r=(\delta\rho_r,\delta j_r)\) に対し

\[
D^3 f^{\rm eq}[m_1,m_2,m_3]
=-\delta\rho_1 H(\delta j_2,\delta j_3)
-\delta\rho_2 H(\delta j_1,\delta j_3)
-\delta\rho_3 H(\delta j_1,\delta j_2)
\]

を使い、collision、streaming phase、filter multiplierを順に適用する。観測残差からforcingをfitしない。

### 独立3次微分 gate

seed `20260814` の16正規化方向を使い、\(v=Vd\) に対する解析的
\(D^3\Phi(f_*)[v,v,v]\) を5点中心差分

\[
\frac{\Phi(f_*+2hv)-2\Phi(f_*+hv)+2\Phi(f_*-hv)-\Phi(f_*-2hv)}{2h^3}
\]

と比較する。step sweepは `0.02, 0.01, 0.005, 0.0025, 0.00125` に固定する。各方向で最良stepを
選ぶが方向や結果ごとにstep集合を変えない。解析的derivative normを `1e-12` より大きくし、16方向の
minimum relative errorの最大値を `5e-4` 以下とする。homological residualだけで3次微分を正当化しない。

### coefficient validity gate

1. Q007aのtriple count、sector count `108 / 1044 / 1448`、singular block `0`、maximum condition
   `10821.814847751179`をrelative error `1e-10` 以下で再現する。
2. 全2,600 solveのrelative residualを `1e-10` 以下にする。
3. 全tripleのhomological equation relative residual、coefficient conjugacy residual、graph-gauge residual、
   zero-wave conserved-moment residualを各 `1e-10` 以下にする。
4. seed `20260817` の16方向、amplitude `0.01`でchartとreduced mapのC4 equivariance relative errorを
   各 `1e-10` 以下にする。
5. coefficient、chart evaluation、reduced-map evaluationがfinite、全試験stateがpositive、strict JSON。

### held-out residual-order gate

Q006iのresidual seed `20260809`を再利用せず、seed `20260815` の32方向を使う。amplitudeは
`0.00125, 0.0025, 0.005, 0.0075, 0.01` とし、roundoff floorを避けるためslopeは後ろ4点だけでfitする。

- quadratic residual slopeを全方向で `3 ± 0.1`
- cubic residual slopeを全方向で `4 ± 0.15`
- amplitude `0.01`の各方向でcubic/quadratic residual ratioを `0.10` 以下
- 全lifted／mapped stateをpositive

とする。最大ratio、最悪方向、全residual列を保存する。

### held-out 100-step shadowing gate

Q006i shadow seed `20260810`を再利用せず、seed `20260816` の32方向、amplitude `0.01`、100 stepを使う。
同じ方向についてquadraticとcubic chartをそれぞれ自己整合的な初期state／reduced mapでrolloutし、
方向ごとのmaximum absolute error、final absolute error、maximum perturbation-relative errorを比較する。

各方向で次を全て要求する。

1. cubic/quadratic maximum absolute-error ratio `<=0.8`
2. cubic/quadratic final absolute-error ratio `<=0.8`
3. cubic/quadratic maximum perturbation-relative-error ratio `<=0.8`

さらにcubic trajectoryの全3,200 step × 3 componentでQ006oの
\(2t\operatorname{spacing}(S_c(f_0))\) budget違反を0、maximum final component budgetを `1.2e-11` 以下、
全stateをpositiveとする。旧Q006iの \(10^{-12}\) gateや`rejected`判定は変更しない。

### 判定

全独立微分・coefficient validity・residual-order・shadowing gateを通過した場合だけ
`cubic chart improves registered finite-grid invariance and shadowing`としてacceptedとする。validityを
通るが残差またはshadowing改善を落とせば
`cubic continuation does not improve the registered chart`としてrejected、独立微分・assembly・finite値・
serializationが失敗すればinconclusiveとする。

acceptedでも、登録finite grid・direction・amplitude・100-step horizonに限る。quartic改善、TT圧縮、
all-radius chart、grid-uniform family、真の不変多様体の存在・一意性・normal attractionを主張しない。
acceptedの場合だけQ007cを詳細に事前登録する。

### 結果

全7 validity gateを通過したが、held-out residual-ratio gateだけが失敗したため、事前登録どおり
`cubic continuation does not improve the registered chart`として`rejected`とした。

- independent derivative maximum best relative error: `3.3657127711273197e-6`
- maximum solve / homological residual:
  `7.507193302943194e-13 / 7.507420157100771e-13`
- coefficient conjugacy / C4 chart / C4 reduced error:
  `1.9424559059939878e-13 / 2.037693065234071e-14 / 1.1934586964246845e-15`
- quadratic / cubic slope range:
  `2.999458101008406–3.00050163830818 / 3.999307108046794–4.000367209086971`
- amplitude `0.01` residual-ratio maximum / failure count:
  `0.2286914274494018 / 9 of 32`
- shadow maximum-absolute / final-absolute / maximum-relative ratio:
  `0.15091634126760786 / 0.10970020315090677 / 0.13108685317368804`
- cubic budget component checks / violations / maximum utilization:
  `9600 / 0 / 0.5`

棄却は係数assemblyや次数改善の失敗ではなく、登録振幅`0.01`で要求した効果量の不足である。同じ方向の
maximum ratioはamplitude `0.00125 / 0.0025 / 0.005 / 0.0075 / 0.01`に対し
`0.028587 / 0.057175 / 0.114348 / 0.171520 / 0.228691`だった。このpost-hoc列は次のradiusを
calibrateするためだけに使い、次の判定データには再利用しない。Q006iとQ007bの既存判定は変更しない。

## Q007b1: independent cubic-radius and immersion audit — 事前登録

### 問い

Q007bとは独立な方向で、cubic chartは半径`0.004`まで全方向10倍の残差改善を示し、元の失敗半径
`0.01`まで局所immersionを保つか。

### calibrationと固定構成

- Q007bのworst ratioを一次外挿したcutoffは約`0.00437`なので、検証半径を`0.004`に固定する。
- Q007bの方向はcalibration専用とし、Q007b1のhypothesis gateへ再利用しない。
- grid \(17^2\)、\(\omega=1.5\)、\(\eta=0.01\)、24実座標、unmodified standard mapを維持する。
- Q007bの \(W_2,R_2,T,K\) を再構築し、係数を再fit・round・truncateしない。
- Q007bで得た係数hashを次に固定する。
  - triple indices: `e646d2de7212c823cbca5804fbf20e9543918ecca80452dd508c278dfc5f130c`
  - output waves: `d431bfabad714d9d7ee9d8bfaf779eb2362ab27c916740494a379610c1389a6f`
  - chart coefficients: `ed182069713bff0558b806ce7a70e77299ea9fbc6671de38c4fa58019da5615b`
  - reduced coefficients: `4ca5a953833d5913f160e9fc36061e31697c7531865c4ef06d7517898f7c597e`
  - forcing coefficients: `6e2559a194d2b1e6a96f01653c1bccbe1852db00233700e16b3b980ae96df8eb`

### 独立radius gate

seed `20260818`の64正規化方向を使う。amplitude ladderは

`0.00125, 0.002, 0.003, 0.004, 0.006, 0.008, 0.01`

に固定する。最初の4点でquadratic／cubic残差slopeをfitし、全7点で


\[
q(a)=\frac{\lVert\Phi(W_3(a))-W_3(R_3(a))\rVert}
{\lVert\Phi(W_2(a))-W_2(R_2(a))\rVert}
\]

のlog-log slopeをfitする。各方向で次を全て要求する。

1. quadratic slope `3 ± 0.1`
2. cubic slope `4 ± 0.15`
3. ratio slope `1 ± 0.1`
4. amplitude `0.004`のratio `<=0.10`
5. 全lifted／mapped／predicted stateがpositiveかつfinite

amplitude `0.006 / 0.008 / 0.01`は元の失敗領域を診断するため保存するが、そのratio自体をradius
acceptance gateには使わない。

### analytic chart-Jacobian validityとimmersion gate


\[
DW_3(a)d=Vd+H[a,d]+\frac12T[a,a,d]
\]

をFourier-fiberから直接評価する。seed `20260820`で16組のpoint/action方向を作り、point amplitude
`0.004`と`0.01`の両方で、centered finite difference step
`1e-5, 5e-6, 2.5e-6`と比較する。各組の最良relative errorの最大を`1e-7`以下、analytic action normを
`1e-12`より大きくする。

radius campaignの64方向について、amplitude `0, 0.002, 0.004, 0.006, 0.008, 0.01`でfull
\(2601\times24\) Jacobianを組み、

\[
\frac{\sigma_{\min}(DW_3(a))}{\sigma_{\min}(V)}\ge0.8
\]

を全点で要求する。これは登録radial samples上のimmersion prequalificationであり、ball全体のinjectivityや
chart fold不在の証明ではない。

### near-resonant contribution diagnostic

Q007aと同じrelative singular threshold `1e-4`、すなわちcondition `>=1e4`の24 tripleを固定する。
64方向のamplitude `0.004`と`0.01`で、near-resonant subsetによるchart／reduced cubic correction norm、
全cubic correctionに対する比、residual ratioとのSpearman correlation、上位quartile enrichmentを保存する。
これは原因候補の診断であり、Q007b1のaccept／reject gateには使わない。

### 独立shadowing gate

seed `20260819`の32正規化方向、amplitude `0.004`、100 stepを使い、quadraticとcubicを自己整合的に
rolloutする。各方向でmaximum absolute、final absolute、maximum perturbation-relative errorの
cubic/quadratic ratioを全て`<=0.8`とする。cubic trajectoryの全9,600 component checkでQ006o budget
違反0、maximum final component budget `<=1.2e-11`、全state positiveを要求する。

### 判定

係数hash、方向独立性、analytic Jacobian、finite／positive／strict JSONをvalidity gateとする。validityを通り、
radius、ratio-scaling、immersion、shadowing、forward-error gateを全て通過した場合だけ
`registered cubic improvement radius localized without fold signature`としてacceptedとする。validだがいずれかの
performance gateを落とせば`registered cubic radius not supported`としてrejected、validity失敗はinconclusiveとする。

acceptedでも、64／32方向の有限sampleに限り、半径`0.004`のball全体を保証しない。Q007bのamplitude
`0.01` rejectionを変更せず、quartic continuation、TT圧縮、grid-uniform family、真の不変多様体の
存在・一意性・normal attractionを主張しない。

### 結果

全5 validity gateと全6 hypothesis gateを通過し、
`registered cubic improvement radius localized without fold signature`として`accepted`とした。

- quadratic / cubic / ratio slope range:
  `2.9997535988860777–3.0003725714946294 / 3.999374269224645–4.00027779049691 /`
  `0.9994377578283731–1.000310528367947`
- radius `0.004` maximum ratio / failure count: `0.07800626791012572 / 0 of 64`
- amplitude ladder maximum ratios:
  `0.024376 / 0.039004 / 0.058505 / 0.078006 / 0.117007 / 0.156005 / 0.195002`
- analytic Jacobian maximum best relative error: `1.463877022273861e-10`
- minimum normalized singular value / maximum condition: `1.0 / 1.7676346838545076`
- shadow maximum-absolute / final-absolute / maximum-relative ratio:
  `0.044022136608928585 / 0.030088934796968496 / 0.03621745864325118`
- cubic budget component checks / violations / maximum utilization: `9600 / 0 / 0.5`

near-resonant 24 tripleのchart fractionは残差比と負相関`-0.5789377`、上位quartile enrichment
`0.4723544`だった。reduced寄与は全方向0で相関未定義と記録した。一方、全cubic／quadratic chart
correction ratioは残差比と`0.9607601`のSpearman相関を持った。従って登録sampleではnear resonanceや
foldより有限次数の全cubic curvatureが主要indicatorである。Q007bの半径`0.01` rejectionは変更しない。

## Q007c: quartic homological-family prequalification — 事前登録

### 問い

Q006iの24 complex modeに対する全order-4 homological blockは、登録grid上で一意に解ける
非共鳴operator familyか。

### 固定設定

- grid $17^2$、$\omega=1.5$、$\eta=0.01$、Q006i/Q007bと同じ24 complex mode
- input indexは`i <= j <= k <= l`のunordered 4-tupleとし、`C(27,4)=17,550`件を全列挙
- multiplierは`lambda_i lambda_j lambda_k lambda_l`、output waveは4入力waveのmod-17和
- zero-wave kinetic、internal selected、externalのoperator assemblyとrank thresholdはQ007aと同一
- numerical rank thresholdは
  `100 * eps * max(operator_shape) * largest_singular_value`
- near-resonant diagnosticは`smallest/largest <= 1e-4`
- quartic forcing、coefficient、residual、shadowingは計算しない

### order-2／order-3 control reproduction

同一runnerでQ007aのpair 300件とtriple 2,600件をartifact入力なしで再構築し、次を要求する。

1. order-2 sector count `36 / 108 / 156`、singular 0
2. order-2 minimum singular `0.00015502435597333105`、maximum condition
   `14513.930547954875`をrelative error `1e-10`以下で再現
3. order-3 sector count `108 / 1044 / 1448`、singular 0、near-resonant 24
4. order-3 minimum singular `0.00020787972673242753`、maximum condition
   `10821.814847751179`をrelative error `1e-10`以下で再現

このcontrolが失敗した場合、order-4結果は判定に使わない。

### order-4 completeness／symmetry validity

1. record countとunique tuple countが17,550、duplicate 0
2. permutation multiplicityの総和が`24^4 = 331,776`、出現値が`1 / 4 / 6 / 12 / 24`
3. zero-wave kinetic、internal selected、externalの各sector countが正
4. conjugate tupleが全て存在し、output wave／output kind failureが0
5. conjugate multiplierとoperator singular valuesのmaximum relative errorが各`1e-10`以下
6. C4およびconjugate output-wave count closureのfailureが0
7. 全record finite、strict JSON

全17,550 blockについてinput modes、wave、multiplier、operator dimension/rank、全singular values、rank
threshold、condition、near-resonant flag、permutation multiplicityをartifactへ保存する。

### 仮説gate

validity通過後、次を両方要求する。

1. numerically singular order-4 blockが0
2. zero／internal／externalを含む全nonsingular blockのmaximum conditionが`1e9`以下

両方通過すれば`order-four homological family prequalified on registered grid`としてacceptedとする。
validだが一方でも失敗すれば`order-four homological obstruction on registered grid`としてrejected、control、
enumeration、symmetry、finite、serializationが失敗すればinconclusiveとする。

acceptedはoperator-only finite-grid prequalificationに限る。quartic forcing／coefficient、残差次数`4 → 5`、
radius延長、shadowing、TT圧縮、grid-uniform family、真の不変多様体の存在・一意性・normal attractionを
主張しない。acceptedの場合だけQ007c1のforcing／coefficient gateを詳細に事前登録する。

### 結果

全6 validity gateと全2 hypothesis gateを通過し、
`order-four homological family prequalified on registered grid`として`accepted`とした。

- order-2 control: sector `36 / 108 / 156`、singular `0`、minimum singular
  `0.00015502435597333105`、maximum condition `14513.930547954875`
- order-3 control: sector `108 / 1044 / 1448`、singular／near `0 / 24`、minimum singular
  `0.00020787972673242753`、maximum condition `10821.814847751179`
- order-4 record／unique／duplicate: `17550 / 17550 / 0`
- order-4 sector: `846 / 4536 / 12168`
- order-4 singular／near-resonant: `0 / 8`
- minimum singular / maximum condition / minimum rank margin:
  `6.485706497181907e-05 / 34673.915552593266 / 144315965.0768939`
- multiplicity sum／values: `331776 / 1, 4, 6, 12, 24`
- maximum fixed-leaf invariance residual: `1.227779058661652e-16`
- conjugate missing／output-wave／output-kind failure: `0 / 0 / 0`
- maximum conjugate multiplier／singular-value relative error:
  `3.571246854667297e-16 / 3.019068596546352e-15`
- output wave count／rotation／conjugacy failure: `81 / 0 / 0`

従って次のforcing／coefficient gateへ進む。ただしoperator-onlyという主張境界は変更しない。

## Q007c1: quartic coefficient continuation — 事前登録

### 問い

Q007cを通過したsymmetric Fourier-fiberの4次forcing／coefficientは独立検証を通り、残差次数を
`4 → 5`へ改善して、Q007bが失敗した半径`0.01`の有限sample性能を回復できるか。

### 固定設定と係数規約

- grid \(17^2\)、\(\omega=1.5\)、\(\eta=0.01\)、24実座標、unmodified standard mapを維持する。
- Q006iの \(V,H,G\) とQ007bの \(T,K\) をartifactから読み込まず再構築し、再fit・round・truncateしない。
- Q007bの固定hashは次の通りとする。
  - triple indices: `e646d2de7212c823cbca5804fbf20e9543918ecca80452dd508c278dfc5f130c`
  - output waves: `d431bfabad714d9d7ee9d8bfaf779eb2362ab27c916740494a379610c1389a6f`
  - chart coefficients: `ed182069713bff0558b806ce7a70e77299ea9fbc6671de38c4fa58019da5615b`
  - reduced coefficients: `4ca5a953833d5913f160e9fc36061e31697c7531865c4ef06d7517898f7c597e`
  - forcing coefficients: `6e2559a194d2b1e6a96f01653c1bccbe1852db00233700e16b3b980ae96df8eb`
- 全17,550 tupleを`i <= j <= k <= l`で再列挙し、Q007cと同じoperator／rank規則を再計算する。
- chartとreduced mapは

\[
W_4(a)=Va+\frac12H[a,a]+\frac16T[a,a,a]+\frac1{24}U[a,a,a,a],
\]

\[
R_4(a)=\Lambda a+\frac12G[a,a]+\frac16K[a,a,a]+\frac1{24}L[a,a,a,a]
\]

とする。物理空間のfull dense quartic tensorはmaterializeせず、unordered complex Fourier-fiber、
permutation multiplicity、output-wave groupで保持する。

### quartic forcingの固定式

\(A,B,C,D\)をfull mapの1階から4階微分とする。各4-tupleの既知項は、全distinct set partitionを
一度ずつ加えた

\[
\begin{aligned}
F_4={}&D(V,V,V,V)
+\sum_{4}B(T,V)+\sum_{3}B(H,H)+\sum_{6}C(H,V,V)\\
&-\sum_{4}H(\Lambda,K)-\sum_{3}H(G,G)-\sum_{6}T(G,\Lambda,\Lambda)
\end{aligned}
\]

と固定する。添字が重複するtupleでも、上式の4／3／6個のlabelled partitionを省略・重複しない。
各sectorでQ007cのhomological operatorを使い、\(U,L\)を解く。

### 独立方向と差分登録

正規化Gaussian方向を次に固定する。

- map fourth derivative: seed `20260821`、16方向
- assembled forcing: seed `20260822`、16方向
- residual order／radius: seed `20260823`、32方向
- C4 field: seed `20260824`、16方向
- 100-step shadowing: seed `20260825`、32方向

全方向hashとnormを保存し、Q006i、Q007b、Q007b1および上記campaign間のexact duplicateを0とする。
4階中心差分のstep sweepは全て

`0.02, 0.015, 0.01, 0.0075, 0.005`

とし、

\[
\frac{f(2h)-4f(h)+6f(0)-4f(-h)+f(-2h)}{h^4}
\]

を使う。各方向でstepを事後追加せず、登録sweep中のminimum relative errorだけをgateに使う。

### derivative／forcing validity gate

1. 線形tangent \(Vd\) に対する解析的 \(D^4\Phi[Vd]^4\) のnormが`1e-12`より大きく、独立5点差分との
   maximum best relative errorが`5e-3`以下
2. cubic defect \(\Phi(W_3(a))-W_3(R_3(a))\) の4階差分と、全quartic forcing fiberを方向収縮した
   物理fieldのmaximum best relative errorが`2e-2`以下
3. 全差分state／map／defectがfiniteかつpositive

map derivative gateは \(D\) の式を、forcing gateは \(B,C,D,H,T,G,K\) の組合せと符号を独立に検証する。
homological solve residualが小さいことを、これらの代用にはしない。

### coefficient validity gate

1. Q007cのpair／triple controlとquartic count・sector・singular 0・maximum conditionをrelative
   tolerance `1e-10`で再現
2. 全17,550 recordがfiniteで、solve relative residualとhomological relative residualが各`1e-10`以下
3. internal sectorのgraph-gauge residualが`1e-10`以下
4. zero-wave forcing／coefficientの保存moment relative residualが各`1e-10`以下
5. forcing／chart／reduced coefficientのconjugacy relative residualが各`1e-10`以下
6. seed `20260824`の16方向、amplitude `0.01`でquartic chart／reduced／forcing fieldのC4 relative
   errorが各`1e-10`以下
7. realificationのimaginary leakageとquartic chart termのglobal conserved-moment relative residualが
   各`1e-10`以下
8. tuple completeness、multiplicity sum `24^4`、strict JSON serializationが通る

全tupleについてforcing norm、chart／reduced coefficient、solve／homological／gauge／保存残差をartifactへ
保存する。full dense physical quartic tensorは保存しない。

### residual-order／radius hypothesis gate

seed `20260823`の32方向とamplitude

`0.00125, 0.0025, 0.005, 0.0075, 0.01`

を使い、最後の4点でcubic／quartic residual slopeをfitする。各方向で次を全て要求する。

1. cubic slope `4 ± 0.15`
2. quartic slope `5 ± 0.30`
3. amplitude `0.01`のquartic/cubic residual ratio `<=0.8`
4. amplitude `0.01`のquartic/quadratic residual ratio `<=0.10`
5. 全lifted／mapped／predicted stateがpositiveかつfinite

Q007bの方向やQ007b1のradius方向はcalibrationにも再利用せず、既存判定を変更しない。

### 100-step shadowing／forward-error hypothesis gate

seed `20260825`の32方向をamplitude `0.01`から100 step進め、full LBM rolloutに対するquartic chartと
cubic chartを比較する。各方向で次を要求する。

1. maximum absolute、final absolute、maximum perturbation-relative errorのquartic/cubic ratioが全て`<=0.8`
2. Q006oのcomponentwise forward-error budgetを使い、9,600 component-stepの違反0、maximum
   utilization `<=1`、final budget `<=1.2e-11`
3. 全stateがpositiveかつfinite

### 判定規則

direction、upstream reproduction、derivative、forcing、coefficient、symmetry、finite、serializationの
いずれかが失敗すれば`inconclusive`とする。validityが全て通り、residual-order／radiusとshadowingの全gateが
通れば`quartic chart restores registered sampled radius-0.01 improvement`として`accepted`、性能gateの
いずれかだけが失敗すれば`quartic continuation does not restore registered radius`として有効な`rejected`
とする。

acceptedでも、32方向の有限sample、有限grid、100 stepに限る。半径`0.01`のball全体、global injectivity、
grid-uniform family、真の不変多様体の存在・一意性・normal attraction、TT圧縮優位性を主張しない。

### 結果

全8 validity gateは通過した。残差次数、半径`0.01`の1-step残差比、forward-error budgetは通過したが、
100-step shadowing比が失敗したため、`quartic continuation does not restore registered radius`として
有効な`rejected`とした。

- map fourth-derivative maximum best relative error: `3.096316945580041e-05`
- assembled-forcing maximum best relative error: `0.0003957993866089215`
- maximum solve／homological residual:
  `1.0006036636030973e-12 / 9.530583825936524e-13`
- maximum conjugacy／C4 relative error:
  `1.6766439496313294e-13 / 4.651395234795445e-12`
- cubic／quartic slope range:
  `3.9997142511488586–4.000288731411633 / 4.999739294776105–5.000472391642802`
- maximum quartic/cubic／quartic/quadratic residual ratio:
  `0.4391470445743498 / 0.09270518013931812`、failure `0 / 0 of 32`
- maximum absolute／final absolute／maximum relative shadow ratio:
  `0.7464493651463932 / 1.3715310087581642 / 0.8914189366016195`
- shadow failure count: `0 / 1 / 1 of 32`
- budget component check／violation／maximum utilization:
  `9600 / 0 / 0.5`

失敗方向14でもmaximum absolute errorは改善したが、instantaneous ratioはstep 15以降`0.8`を超えた。
step 100のabsolute errorは`5.219526416836927e-09 → 7.158742331724237e-09`であり、machine floorではない。
この方向は次のcalibration／reproduction controlだけに使い、Q007c1の棄却は変更しない。

## Q007c2: quartic shadow amplitude-horizon localization — 事前登録

### 問い

Q007c1のquartic chartは、独立方向で半径`0.01`・10 stepの短時間改善と、半径`0.004`・100 stepの
長時間改善をともに再現し、振幅・horizon依存の有効shadow領域を局在化できるか。

### 固定設定とupstream control

- grid \(17^2\)、\(\omega=1.5\)、\(\eta=0.01\)、24実座標、unmodified standard mapを維持する。
- Q007c1のquartic modelをartifactから読み込まず再構築し、係数を再fit・round・truncateしない。
- quartic coefficient hashを次に固定する。
  - quartet indices: `968b35d36cbd28c1f30e6cacb906649a42b36ba4e7bf4122394c2722cd809c16`
  - output waves: `9f9720e1114cc489ef7bbca81562e7d4cf211999e8d4a4958c06c02ee0df1fe8`
  - chart coefficients: `9597e0d31c32c940c76526754f0ec70c666e5fe03511977e80b3fd0610a7f29b`
  - reduced coefficients: `061cd66caf83850a45eeec05ed0f62fafb748a3076d7a6eb591bc69be2e008f7`
  - forcing coefficients: `6ab2337ea60b87dbe404e1aeb6b9c090fa8f950d43815966e0933879901b8eef`
- Q007c1 seed `20260825`の方向14をamplitude `0.01`、100 stepで再実行し、次の3比をrelative tolerance
  `1e-10`で再現する。
  - maximum absolute: `0.7464493651463932`
  - final absolute: `1.3715310087581642`
  - maximum perturbation-relative: `0.8914189366016195`
- このcontrolが失敗すれば新しいcampaignは判定に使わず`inconclusive`とする。

### 独立方向とcampaign grid

- seed `20260826`の64 normalized Gaussian方向を固定する。
- Q006i、Q007b、Q007b1、Q007c1の全登録方向とのexact duplicateを0とする。
- amplitudeは`0.004 / 0.007 / 0.01`、最大horizonは100 stepとする。
- 各amplitude・方向についてcubic／quarticを各chart上の初期状態から100 stepずつ一度だけ進める。
- 保存するprefix horizonは`10 / 25 / 50 / 100`とする。各prefixで
  - prefix maximum absolute error
  - horizon final absolute error
  - prefix maximum perturbation-relative error
  のquartic/cubic比を計算する。
- 64 × 3 × 2本のtrajectory、38,400 chart-step、quartic側57,600 conservation component-stepを
  全てartifactへ保存する。

### validity gate

1. 係数hashとQ007c1方向14 controlを再現
2. direction norm error `<=5e-15`、duplicate 0
3. 全state／coordinate／error／ratioがfinite、全populationがpositive
4. 各cellのdirection countが64、prefix horizonが`10 / 25 / 50 / 100`と一致
5. strict JSON serializationが通る

validityのいずれかが失敗すれば性能仮説を判定せず`inconclusive`とする。

### hypothesis gate

次を全て要求する。

1. amplitude `0.01`、horizon 10で3種類のquartic/cubic shadow比が全64方向`<=0.8`
2. amplitude `0.004`、horizon 100で3種類のquartic/cubic shadow比が全64方向`<=0.8`
3. quartic側57,600 component-stepでQ006o budget違反0、maximum utilization `<=1`、各trajectoryの
   final budget `<=1.2e-11`

amplitude `0.007`と、上記2 cell以外のhorizonは有効領域の境界を診断するため保存するが、acceptance gateへ
使わない。failure count、最初にratio `0.8`を超えるstep、方向別のcrossoverを報告する。観測後にhorizonや
amplitudeを追加・削除しない。

### 判定規則

validity通過後、3 hypothesis gateが全て通れば
`quartic shadowing domain localized on independent directions`として`accepted`、一つでも失敗すれば
`registered quartic shadowing domain not reproduced`として有効な`rejected`とする。

acceptedでも、独立64方向と登録した2 operating pointだけの有限sample claimである。半径`0.004`または
`0.01`のball全体、他のhorizon、global injectivity、grid-uniform family、真の不変多様体、TT優位性を
主張しない。Q007c1の100-step半径`0.01`棄却はどの結果でも変更しない。

### 実行結果（2026-08-08）

全4 validity gateと全3 hypothesis gateが通過し、
`quartic shadowing domain localized on independent directions`として`accepted`となった。

- coefficient hash match / Q007c1 control maximum relative error: `true / 0`
- direction maximum norm error / exact duplicate count: `2.220446049250313e-16 / 0`
- trajectory / chart-step / budget-component count: `384 / 38400 / 57600`
- budget violation / maximum utilization / maximum final budget:
  `0 / 0.5 / 1.1368683772161603e-11`
- amplitude `0.01`、horizon 10のmaximum 3 ratio:
  `0.46692017829349514 / 0.48393482249773484 / 0.4610632459952544`
- amplitude `0.004`、horizon 100のmaximum 3 ratio:
  `0.22081209266153715 / 0.339679128695444 / 0.2703146187976154`
- amplitude `0.01`、horizon 100の診断比:
  `0.5520626734869788 / 0.8505821724417485 / 0.675783734038649`
  （final absoluteのみ2方向失敗）

従って登録2点の有限sample局在化だけを採択し、Q007c1の長時間・大振幅棄却は変更しない。

## Q008a: quartic Fourier coefficient TT storage prequalification — 事前登録

### 問い

固定したQ007c1 complex Fourier chart係数に対し、4つの登録TT出力軸配置のいずれかが、
degree 4の自然なunordered sparse-fiberより、忠実度を保ったままcore stored real scalarsと
実serialized bytesの両方で小さくなるか。degree `2 / 3 / 4`のrank推移も測るが、3点から
漸近bounded rankを主張しない。

### 固定入力

- grid \(17^2\)、\(\omega=1.5\)、\(\eta=0.01\)、24 complex conjugate-constrained mode、
  D2Q9 local output 9を使う。
- mode順は`WAVE_ORDER`の8 waveを外側、`shear / acoustic_positive / acoustic_negative`を内側とし、
  mode table hashを
  `6e08a2706a44965143944b692615c6a8525799d3e01ca06a636d852d6610d4d9`に固定する。
- quadratic ordered coefficient \(T^{(2)}\in\mathbb{C}^{9\times24\times24}\) はQ006iと同じ
  complex Fourier solveから再構築し、chart coefficient hashを
  `4d0ddc917c3b722496b918f38f8e810e0f200c5fd2ffa138025a93aa2571f8db`に固定する。
- cubic unordered indices / chart coefficient hashを
  `e646d2de7212c823cbca5804fbf20e9543918ecca80452dd508c278dfc5f130c` /
  `ed182069713bff0558b806ce7a70e77299ea9fbc6671de38c4fa58019da5615b`に固定する。
- quartic unordered indices / chart coefficient hashを
  `968b35d36cbd28c1f30e6cacb906649a42b36ba4e7bf4122394c2722cd809c16` /
  `9597e0d31c32c940c76526754f0ec70c666e5fe03511977e80b3fd0610a7f29b`に固定する。
- cubic／quarticはunordered fiberを全ordered permutationへ同じ係数で展開する。multiplicityを
  係数へ重ねて掛けず、ordered contractionが既存の`multiplicity × unordered product`と一致する形にする。
- 対象はlocal coefficient tensor \(T^{(d)}_{q,i_1,\ldots,i_d}\)だけである。Fourier phaseは入力modeへ
  因数分解できるため、物理空間の \(2601\times24^d\) tensorはmaterializeしない。

### 固定tensorization

各degree \(d=2,3,4\)で次の4候補だけを比較する。

1. `flat-q-first`: \((9,24,\ldots,24)\)
2. `flat-q-last`: \((24,\ldots,24,9)\)
3. `d1q3-q-first`: \((3,3,24,\ldots,24)\)
4. `d1q3-q-last`: \((24,\ldots,24,3,3)\)

D1Q3 factorは`D2Q9_VELOCITIES`を\((c_y,c_x)\in\{-1,0,1\}^2\)のlexicographic順へ一意に
並べ替えてからreshapeする。入力mode 24のQTT factorization、axis-major／scale-interleaved順、
monomial／Chebyshev変換、shell-count sweepはこの結果を見て追加せず、必要なら別ゲートとして事前登録する。

### TT-SVDと忠実度

- complex128のTT-SVD、relative discarded-Frobenius budget `1e-13`、`max_rank=None`を固定する。
- seed `20260827`の64 normalized real方向をcomplex coordinate mapで変換し、unordered sparse action、
  ordered dense action、TT actionを比較する。
- dense expansionのmaximum relative action error `<=5e-14`を要求する。
- 各TT候補のrelative tensor reconstruction error `<=2e-13`、maximum relative action error
  `<=1e-11`を要求する。
- 全core、singular value、reconstruction、actionをfiniteとし、uncompressed NPZのsave/load後に
  core dtype／shape／値がbitwise一致することを要求する。
- validityが一つでも失敗すればstorage仮説を判定せず`inconclusive`とする。

### 格納量の固定定義

natural sparse-fiberは各degreeのunordered multi-indexを`uint8`、multiplicityを`uint8`、
9成分係数を`complex128`で保持する。degree 4は17,550 fiber、係数値は315,900 real scalarsである。

各表現について次を別々に保存する。

- coefficient stored real scalar count
- index／multiplicity／rank／shape metadata bytes
- raw array payload bytes
- `numpy.savez`によるuncompressed serialized bytes
- TT ranksと、複素TT gaugeを差し引いたnominal real dimension
- dense expansion bytes、TT-SVD wall time

scalar-sparseはbitwise nonzeroだけを格納するlossless診断として報告するが、acceptance baselineを
post-hocに切り替えない。TT core stored scalarsは複素core entry 1個をreal scalar 2個として数え、
gauge-adjusted dimensionと混同しない。

### 評価時間の診断

seed `20260828`の128 normalized real方向についてlocal 9-vector homogeneous actionを評価する。
2 warm-up後に7 blockを実行し、sparse／各TTのns/sample medianとMADを保存する。実行順はblockごとに
固定rotationする。wall timeは環境依存なのでQ008aのacceptance gateには使わない。full physical chart、
invariance residual、100-step rolloutはstorage候補が通った場合のQ008b holdoutへ残す。

### hypothesis gateと判定規則

validity通過後、degree 4で少なくとも1候補が次を同時に満たすことを要求する。

1. TT core stored real scalar count `<315900`
2. TTのuncompressed serialized bytes `<` natural sparse-fiberのuncompressed serialized bytes

通過候補が複数なら`(serialized bytes, core stored real scalars, candidate id)`のlexicographic minimumを
唯一のQ008b候補として固定する。通れば
`registered TT tensorization beats natural quartic sparse-fiber storage`として`accepted`、一つも通らなければ
`registered TT tensorizations do not beat natural quartic sparse-fiber storage`として有効な`rejected`とする。

acceptedでもlocal coefficient storageの有限degree結果に限り、online高速化、不変性残差保存、TT-cross、
他shell、他grid、漸近rank boundを主張しない。rejectedなら、この4 tensorizationに対するQ008b／Q009を
開始しない。別のQTT factorizationを試す場合は、新しい候補と判定を観測前に登録する。

### 実行結果（2026-08-08）

全4 validity gateは通過したが、degree-4 storage gateを通る候補は0だった。従って
`registered TT tensorizations do not beat natural quartic sparse-fiber storage`として有効な`rejected`となった。

- maximum dense-vs-sparse action error: `2.4453226833464242e-14`
- maximum TT reconstruction / action error:
  `1.0601074033942119e-13 / 2.0799628811140123e-13`
- degree-4 natural sparse stored real scalars / NPZ bytes:
  `315900 / 2615734`
- degree-4 best TT stored real scalars / NPZ bytes:
  `3550626 / 28406852`
- minimum TT/sparse scalar / byte ratio:
  `11.2397150997151 / 10.859992644512019`
- flat-q-last ranks by degree:
  `[1,24,9,1] / [1,24,216,9,1] / [1,24,300,216,9,1]`
- diagnostic sparse / fastest-TT median action time:
  `603107.8125 / 2783184.375 ns per sample`

全候補が忠実度を通過しているため、これは表現サイズの有効な棄却である。Q008bとQ009はこの4候補に
対して開始しない。

## Q008c: wave-branch / wave-QTT storage prequalification — 事前登録

### 問い

Q008aで未検証のmode構造 \(24=8\text{ waves}\times3\text{ branches}\) と、wave index 8の3-bit
factorizationを明示すれば、固定四次係数を忠実に保ちながらnatural sparse-fiberよりstored real scalarsと
serialized bytesの両方で小さいTTが得られるか。

### upstream controlと固定入力

- Q008aと同じgrid \(17^2\)、\(\omega=1.5\)、\(\eta=0.01\)、degree `2 / 3 / 4`、
  local D2Q9 output 9を使う。
- Q008aの6入力hashとfiber count `300 / 2600 / 17550`を完全一致で再現する。
- Q008a `flat-q-last` controlを再構築し、次を完全一致で要求する。
  - ranks: `[1,24,9,1] / [1,24,216,9,1] / [1,24,300,216,9,1]`
  - core stored real scalars: `11682 / 343458 / 3550626`
  - uncompressed NPZ bytes: `94772 / 2749244 / 28406852`
- controlの各tensor reconstruction errorは`<=2e-13`、action errorは`<=1e-11`とする。Q008aの
  wall timeは再現条件にしない。
- complex mode indexを \(i=3w+b\) と固定する。\(w=0,\ldots,7\) は`WAVE_ORDER`の位置、
  \(b=0,1,2\) は`shear / acoustic_positive / acoustic_negative`の位置である。
- outputはQ008aで同じ格納量かつ速かったflat-q-lastだけを使い、D1Q3 outputを再試行しない。

### 固定tensorization

各degree \(d=2,3,4\)で次の4候補だけを比較する。

1. `wave-branch-tuple-major`:
   \((w_1,b_1,w_2,b_2,\ldots,w_d,b_d,q)\)、mode shape \((8,3)^d\times9\)
2. `wave-branch-factor-major`:
   \((w_1,\ldots,w_d,b_1,\ldots,b_d,q)\)、mode shape \(8^d\times3^d\times9\)
3. `wave-qtt-tuple-major`:
   \((s_{1,2},s_{1,1},s_{1,0},b_1,\ldots,s_{d,2},s_{d,1},s_{d,0},b_d,q)\)
4. `wave-qtt-scale-interleaved`:
   \((s_{1,2},\ldots,s_{d,2},s_{1,1},\ldots,s_{d,1},s_{1,0},\ldots,s_{d,0},b_1,\ldots,b_d,q)\)

wave bitは \(w=4s_2+2s_1+s_0\)、各 \(s_j\in\{0,1\}\) とし、NumPy C-order reshapeで一意に
対応させる。4候補以外のbit encoding、Gray code、mode reorder、D1Q3 output、basis変換、rank capは
観測後に追加しない。

### 独立忠実度campaign

- complex128 TT-SVD、relative discarded-Frobenius budget `1e-13`、`max_rank=None`を維持する。
- seed `20260829`の64 normalized real方向を固定し、Q008aのaction seed `20260827`およびtiming seed
  `20260828`とのexact duplicateを0とする。
- 各tensorizationのdense reshape／transpose actionとcanonical ordered dense actionのmaximum relative
  error `<=5e-14`を要求する。
- 各TTのrelative tensor reconstruction error `<=2e-13`、maximum sparse-action error `<=1e-11`を
  要求する。
- 全core／singular value／actionをfinite、uncompressed NPZ roundtripをbitwise equal、summaryをstrict
  JSON serializableとする。一つでも失敗すればstorage仮説は`inconclusive`とする。

### 格納量とtiming

natural sparse-fiberとscalar-sparse診断のdtype、stored-real-scalar数、metadata、raw bytes、uncompressed
NPZ bytesはQ008aと同じ定義を使う。TTもcomplex core entryをreal scalar 2個として数え、rank／shape
metadataとnominal gauge-adjusted real dimensionを別報告する。

seed `20260830`の128 normalized real方向で2 warm-up／7 measured blockのlocal 9-vector action timingを
固定rotation順で測る。median／MADを保存するが、wall timeはacceptanceに使わない。

### hypothesis gateと判定規則

validity通過後、degree 4で少なくとも1候補が次を同時に満たすことを要求する。

1. TT core stored real scalar count `<315900`
2. TT uncompressed NPZ bytes `<2615734`

複数候補が通れば`(serialized bytes, core stored real scalars, candidate id)`のlexicographic minimumを
唯一の後続候補に固定する。通れば
`registered wave-factorized TT beats natural quartic sparse-fiber storage`として`accepted`、一つも通らなければ
`registered wave-factorized TTs do not beat natural quartic sparse-fiber storage`として有効な`rejected`とする。

acceptedでも固定degree・grid・coefficientのlocal storage claimに限る。full-chart residual／rollout、online
benefit、TT-cross、他shell／grid、漸近rank boundは未検証である。rejectedなら固定Q007c1係数に対する
TT-SVD圧縮経路を終了し、Q009 TT-crossへ進まない。

### 実行結果（2026-08-08）

全5 validity gateは通過したが、degree-4 storage gateを通る候補は0だった。従って
`registered wave-factorized TTs do not beat natural quartic sparse-fiber storage`として有効な
`rejected`となった。

- maximum canonical dense-vs-sparse / candidate mapping action error:
  `1.8460488990463964e-14 / 1.3427825001646324e-15`
- maximum TT reconstruction / sparse-action error:
  `1.4915465734115449e-13 / 6.624328755394939e-13`
- degree-4 natural sparse stored real scalars / NPZ bytes:
  `315900 / 2615734`
- degree-4 best wave-branch TT stored real scalars / NPZ bytes:
  `4465748 / 35728884`
- minimum TT/sparse scalar / byte ratio:
  `14.136587527698639 / 13.659219171368342`
- degree-4 best wave-QTT stored real scalars / NPZ bytes:
  `8121540 / 64977332`
- diagnostic sparse / fastest-candidate median action time:
  `573325.78125 / 22348794.53125 ns per sample`

全12候補がmapping、再構成、作用、serializationを通過しているため、これは表現サイズの有効な棄却で
ある。固定Q007c1係数に対するTT-SVD圧縮経路を閉じ、Q009 TT-crossへ進まない。

## Q007d: finite-radius projected tangent/normal cocycle — 事前登録

### 問い

Q006hで確認した平衡点の有限格子spectral gapは、Q007c2で局在化したquartic candidate chartの
有限shadow領域でも、10-step projected normal cocycleが最弱tangent cocycleより強く減衰するという
有限sampleのnormal-dominanceとして残るか。

### 数学的対象と固定入力

- Q007c1と同じfiltered periodic D2Q9 map、grid \(17^2\)、\(\omega=1.5\)、\(\eta=0.01\)、
  固定全質量・全運動量葉、24実座標quartic chart \(W_4\) とreduced map \(R_4\) を使う。
- Q007c1のmode、quadratic、cubic、quartic chart／reduced coefficient hashを完全一致で再現する。
- Q007c2が有限sampleで受理した二つのcellに合わせ、amplitude `0.004 / 0.01`、horizon `10`を使う。
  `0.004`の100-step受理や`0.01`の100-step棄却は変更しない。
- seed `20260831`の16 normalized real方向を使い、Q006iからQ008cまでの登録方向とのexact duplicateを
  0とする。平衡点 \(a=0\) を別controlとして1点加え、合計33 starting pointとする。
- 各starting pointから \(a_{n+1}=R_4(a_n)\) を10 step進め、各点で \(W_4(a_n)\)、
  \(D W_4(a_n)\)、full-map Jacobian \(J_n=D\Phi(W_4(a_n))\) を解析的に評価する。

### fixed-leaf tangent／normal projector

global mass／momentum matrixを \(C\) とし、Euclidean fixed-leaf projectorを

\[
P_L=I-C^\top(CC^\top)^{-1}C
\]

と固定する。\(P_LD W_4(a)\) のthin QRから \(Q(a)\in\mathbb R^{2601\times24}\) を作り、

\[
P_N(a)=P_L-Q(a)Q(a)^\top
\]

を登録normal projectorとする。別の重み付きnorm、oblique projector、Riesz bundle、basis最適化を
結果観測後に追加しない。

各stepのtangent blockとrelative tangent leakageを

\[
B_n=Q(a_{n+1})^\top J_nQ(a_n),\qquad
\ell_n=\frac{\|P_N(a_{n+1})J_nQ(a_n)\|_2}{\|J_nQ(a_n)\|_2}
\]

とする。10-step cocycleは

\[
T_{10}=B_9\cdots B_0,
\]

\[
N_{10}=P_N(a_{10})J_9P_N(a_9)\cdots J_0P_N(a_0)
\]

であり、primary ratioを

\[
\gamma_{10}=\frac{\sigma_{\max}(N_{10})}{\sigma_{\min}(T_{10})}
\]

と固定する。one-step \(\gamma_1\) も保存するが判定は変えない。

### 解析的微分と数値solverのvalidity

- BGK equilibriumの任意state微分、collision、periodic streaming、checkerboard filterを合成した
  matrix-free \(Jv\) と \(J^\top u\) を実装する。
- 平衡点と各amplitudeの先頭4方向、合計9点で、seed `20260902`の8 tangent／8 leaf-normal方向を使う。
  central-difference step `2e-5 / 1e-5 / 5e-6`のbest full-map derivative relative error
  `<=2e-8`、quartic chart derivative error `<=2e-9`を要求する。
- 同じ9点で4独立pairのadjoint inner-product relative error `<=5e-13`、全33軌道点でfixed-leaf
  conservation derivative residual `<=5e-13`を要求する。
- 全点で \(Q^\top Q-I\)、\(CQ\)、projector symmetry／idempotencyのrelative residualを
  `<=1e-12`、chart tangent rankを24、minimum singular valueを`>=1e-8`とする。
- seed `20260901`を起点とするmatrix-free two-sided Lanczos／SVDで\(\sigma_{\max}(N_{10})\)を求める。
  singular-triplet relative residual `<=1e-8`、別の決定的startとのsingular value relative agreement
  `<=1e-6`を要求する。
- 全trajectoryでpopulationを正、\(\|a_n\|_2\le1.05\|a_0\|_2\)（平衡点を除く）、
  \(\sigma_{\min}(T_{10})>=1e-8\)、全値をfinite、summaryをstrict JSONとする。
- maximum tangent leakageは`<=1e-3`をvalidity条件とする。超過時はnormal ratioを性能棄却に使わず
  `inconclusive`とする。

### hypothesis gateと判定規則

全validity通過後、次の3条件を別々に要求する。

1. 平衡点controlで \(\gamma_{10}<1\)
2. amplitude `0.004`の16方向すべてで \(\gamma_{10}<1\)
3. amplitude `0.01`の16方向すべてで \(\gamma_{10}<1\)

3条件が通れば`registered finite-sample projected normal-cocycle dominance observed`として`accepted`、
一つでも落ちれば`registered finite-sample projected normal-cocycle dominance not observed`として有効な
`rejected`とする。最大ratio、最小margin \(1-\gamma_{10}\)、方向別ratio、one-step診断をすべて保存する。

acceptedでも、固定grid・2半径・16方向・10 step・Euclidean orthogonal projectorに限る。ball全体、
他horizon、adapted norm、真のinvariant normal bundle、grid-uniform normal attraction、chartの存在・一意性を
主張しない。acceptedならQ007eでdefectとderivative Lipschitz boundを用いるa posteriori boundを事前登録する。
rejectedならEuclidean projector上の登録仮説だけを棄却し、Riesz／adapted bundleを試す場合は別gateで
候補と閾値を観測前に固定する。

### Q007d 結果

全7 validity gateは通過したが、3つのnormal-dominance gateはすべて失敗した。

- maximum best full-map／chart derivative relative error:
  `6.0343862358835346e-11 / 1.2051245689498942e-10`
- maximum adjoint／conservation derivative residual:
  `3.67240461070866e-17 / 2.0292205916090742e-16`
- maximum projector-family residual: `1.8367094929943913e-15`
- maximum normal SVD triplet residual／two-start disagreement:
  `2.8463046225927812e-15 / 8.9606828648914722e-16`
- maximum tangent leakage: `2.3392329166073374e-6`
- equilibrium `gamma_1 / gamma_10`: `2.4223625220259515 / 2.592215401693412`
- amplitude `0.004 / 0.01`のmaximum `gamma_10`:
  `2.5929140877584227 / 2.593947499641212`
- 両amplitudeのfailure count: `16 / 16`

従って`registered finite-sample projected normal-cocycle dominance not observed`として有効な
`rejected`とした。Q006hのeigenvalue-modulus gapはEuclidean singular-value gapを意味しない。
一方、棄却範囲は登録Euclidean projectorだけであり、adapted norm／Riesz splitはまだ判定していない。

## Q007e: equilibrium Riesz／Stein metric prequalification — 事前登録

### 問い

Q007dで平衡点から観測されたEuclidean transient amplificationは、Q006hのselected／excluded
spectral gapから観測前に固定するRiesz invariant splitとrate-weighted Stein metricでは除去できるか。

### 固定入力とinvariant split

- Q007dと同じgrid `17^2`、filtered periodic D2Q9 map、`omega=1.5`、`eta=0.01`、固定全質量・
  全運動量葉、平衡点Jacobian \(A_0\) を使う。quartic係数や有限半径trajectoryはmetric構築に使わない。
- Fourier変換は`numpy.fft.fft2/ifft2`の`norm="ortho"`、population-last、C-orderと固定する。
- Q006hの8 signed low-wave clusterに24 complex selected modeを置く。実stateの共役制約後は24実次元で
  ある。zero waveの3保存方向は固定葉から除き、それ以外をexcluded normal clusterとする。
- 各9次元Fourier blockでselected／excluded clusterをordered complex Schur subspaceとして分離する。
  cluster内部の個別固有ベクトル順序は判定に使わず、左右subspaceのbiorthogonalizationからRiesz
  coordinatesを作る。縮退内部のbasis回転は同一clusterとして扱う。
- selected blockを \(B_E\)、excluded blockを \(B_F\) とし、全blockで

  \[
  \rho_N=\max\rho(B_F),\qquad
  \mu_T=\min_{\lambda\in\sigma(B_E)}|\lambda|,
  \qquad r_*=\sqrt{\rho_N\mu_T}
  \]

  を一度だけ計算する。`rho_N < r_* < mu_T`が成立しなければmetricを作らず有効な`rejected`とする。

### rate-weighted Stein metric

各normal blockでは \(C_F=B_F/r_*\)、各tangent blockでは \(C_E=r_*B_E^{-1}\) と固定し、

\[
C_F^*H_FC_F-H_F=-I,
\qquad
C_E^*H_EC_E-H_E=-I
\]

の一意なHermitian正定値解を使う。Cholesky factorでwhitenしたRiesz coordinatesを登録adapted normと
する。右辺、rate、block scaling、追加balancingを結果観測後に変更しない。この構成ではvalidityが通れば
理論上 \(\|B_F\|_{H_F}<r_*<\sigma_{\min,H_E}(B_E)\) となるが、実装誤差とconditioningを
独立に監査する。

### validity gate

- Q007dのmode／coefficient hashと平衡点Euclidean `gamma_1 / gamma_10`をrelative error `<=1e-10`で
  再現する。
- selected real dimension `24`、fixed-leaf total dimension `2598`、欠落・重複mode 0とする。
- Schur reorder、invariant split、左右biorthogonality、block diagonalization、fixed-leaf residualを
  それぞれ`<=1e-10`とする。
- 全Stein equationのrelative residual `<=1e-10`、Hermitian residual `<=1e-12`、minimum eigenvalue
  `>1e-12`とする。
- 全Riesz basis、metric、whitening transformの2-norm condition numberを`<=1e10`とする。
- conjugate-wave metric residual `<=1e-10`とする。seed `20260906`の16 fixed-leaf real方向で
  Fourier／Riesz roundtrip relative error `<=1e-10`、imaginary leakage `<=1e-10`を要求する。
- seed `20260907`のmatrix-free two-start SVDでadapted one-step／10-step singular valueを再計算し、
  blockwise dense値とのrelative error `<=1e-8`、triplet residual `<=1e-8`、two-start disagreement
  `<=1e-6`とする。
- 全値finite、strict JSONとする。

### hypothesis gateと停止規則

全validity通過後、平衡点で

\[
\gamma^{(*)}_1
=\frac{\sigma_{\max,*}(N_1)}{\sigma_{\min,*}(T_1)}<1,
\qquad
\gamma^{(*)}_{10}
=\frac{\sigma_{\max,*}(N_{10})}{\sigma_{\min,*}(T_{10})}<1
\]

を別々に要求する。両方通れば
`equilibrium Riesz/Stein metric prequalified for finite-radius testing`として`accepted`とし、Q007fで
Q007dと同じ33 starting pointへmetricを固定したまま進む。一つでも落ちれば
`registered equilibrium adapted metric does not recover normal dominance`として有効な`rejected`とし、
このmetricによるfinite-radius campaignは開始しない。

acceptedでも平衡点・単一gridのmetric prequalificationに限り、有限半径normal attraction、真のnormal
bundle、grid-uniform bound、多様体の存在・一意性は主張しない。Q007dのEuclidean棄却も変更しない。

### Q007e 結果

全8 validity gateと2つのhypothesis gateが通過した。

- selected／excluded modulusと固定rate:
  `0.9837709569927492 / 0.9817098358325433 / 0.9827398560586499`
- maximum split／Stein residual:
  `4.478049432763522e-14 / 7.717980857245268e-14`
- minimum Stein eigenvalue／maximum registered condition number:
  `1.0914517112309456 / 1383.4345053355412`
- maximum conjugacy／real roundtrip／imaginary leakage residual:
  `2.2615002024861891e-13 / 4.1650348386053546e-16 / 6.534769174688447e-17`
- matrix-free SVDのmaximum blockwise error／triplet residual／two-start disagreement:
  `4.0053646874458993e-16 / 1.2331152676133846e-15 / 6.675607812409829e-16`
- adapted `gamma_1 / gamma_10`:
  `0.9988057257445229 / 0.9796329537956986`
- metric／whitening SHA-256:
  `23a18bd5f281ad21874da17a3a28bfeb66b36c9170fdb57308ef0eb40ff5c5d5 /`
  `acf2be2aaec50c3ffa19658325e7dad736a0bce438e3343a72527b96f27b196b`

従って`equilibrium Riesz/Stein metric prequalified for finite-radius testing`として`accepted`とする。
Q007dのEuclidean棄却は変更しない。これはnonnormal transient amplificationが登録計量で除去できることを
平衡点で示しただけであり、有限半径で同じ不等式が保たれるかは次の別gateで判定する。

## Q007f: fixed-metric finite-radius normal cocycle — 事前登録

### 問い

Q007eで平衡点だけから固定したFourier-Riesz Stein metricは、再調整なしにQ007dと同じ33 starting pointの
10-step projected tangent／normal cocycleでもnormal dominanceを回復するか。

### 固定入力とmetric

- Q007dと同じquartic chart、grid `17^2`、`omega=1.5`、`eta=0.01`、固定保存量葉を使う。
- seed `20260831`、direction SHA-256
  `99861e73b9204938e254cbfc1c01a81de7be0bd6fed726ab131b26708c741424`の16方向、amplitude
  `0.004 / 0.01`、平衡点を含む33 starting point、horizon `10`を完全に再利用する。この比較campaignを
  independent holdoutとは呼ばない。
- Q007eのmetric／whitening SHA-256を上記の値と完全一致で再現する。有限半径state、chart tangent、
  cocycle結果からStein equation、rate、block weight、balancingを更新しない。

Q007eの固定葉whiteningを \(S:L\to\mathbb C^{2598}\) とする。各trajectory点で

\[
\widetilde D(a)=S D W_4(a)
\]

のthin complex QRから \(\widetilde Q(a)\) を作り、登録normal projectorを

\[
\widetilde P_N(a)=I-\widetilde Q(a)\widetilde Q(a)^*
\]

とする。共役したfull-map derivativeを

\[
\widetilde J_n=S J_n S^{-1}
\]

とし、

\[
\widetilde B_n=\widetilde Q(a_{n+1})^*\widetilde J_n\widetilde Q(a_n),
\qquad
\widetilde T_{10}=\widetilde B_9\cdots\widetilde B_0,
\]

\[
\widetilde N_{10}
=\widetilde P_N(a_{10})\widetilde J_9\widetilde P_N(a_9)\cdots
\widetilde J_0\widetilde P_N(a_0)
\]

を使う。性能比は

\[
\widetilde\gamma_{10}
=\frac{\sigma_{\max}(\widetilde N_{10})}
       {\sigma_{\min}(\widetilde T_{10})}
\]

と固定する。one-step \(\widetilde\gamma_1\) は全点で保存するが、Q007dとの比較を保つため主hypothesis
gateには使わない。

### validity gate

- Q007dの全coefficient hash、direction hash、33 starting point、Euclidean equilibrium
  `gamma_1 / gamma_10`を完全一致またはrelative error `<=1e-10`で再現する。
- Q007eのmetric／whitening hash、全8 validity gate、adapted equilibrium `gamma_1 / gamma_10`を
  完全一致またはrelative error `<=1e-10`で再現する。
- \(S^{-1}S\)の実fixed-leaf roundtrip、imaginary leakageを`<=1e-10`とする。平衡点と各amplitudeの
  先頭4方向の合計9点で、seed `20260909`から作る8個のreal fixed-leaf adapted単位方向を使う。
  central-difference step `2e-5 / 1e-5 / 5e-6`で共役map action \(\widetilde Jv\)を検証し、
  best relative errorを`<=2e-8`とする。
- 同じseedから作る4個のnormalized complex adapted left／right pairで \(\widetilde J\) と実装adjointの
  inner-product relative errorを`<=5e-12`とする。方向は全9点で固定し、全hashを保存する。
- 全trajectory点でadapted tangent rankを24、minimum singular valueを`>=1e-8`、
  \(\widetilde Q^*\widetilde Q-I\)とprojector idempotency／Hermitian residualを`<=1e-11`とする。
- maximum adapted tangent leakageを`<=1e-3`、minimum \(\sigma_{\min}(\widetilde T_{10})\)を
  `>=1e-8`とする。
- seed `20260908`のcomplex matrix-free two-start SVDを全33点で使う。equilibriumのblockwise Q007e値との
  relative error `<=1e-8`、全triplet residual `<=1e-8`、two-start disagreement `<=1e-6`とする。
- Q007dと同じpositivity、reduced-coordinate growth、finite、strict JSON gateを維持する。

一つでもvalidity gateが落ちればnormal-dominance結果を性能判定に使わず`inconclusive`とする。

### hypothesis gateと停止規則

全validity通過後、次の3条件を別々に要求する。

1. 平衡点で \(\widetilde\gamma_{10}<1\)
2. amplitude `0.004`の16方向すべてで \(\widetilde\gamma_{10}<1\)
3. amplitude `0.01`の16方向すべてで \(\widetilde\gamma_{10}<1\)

3条件が通れば`registered finite-sample adapted-metric projected normal-cocycle dominance observed`として
`accepted`、一つでも落ちれば`registered finite-sample adapted-metric projected normal-cocycle dominance
not observed`として有効な`rejected`とする。各amplitudeのmin／max ratio、failure count、margin、全点の
one-step診断を保存する。結果を見てmetricをretuneしない。

acceptedでも固定grid・同じ32有限方向・2半径・10 step・candidate quartic tangentとmetric-orthogonal
projectorに限る。ball全体、独立holdout、真のinvariant normal bundle、grid-uniform attraction、多様体の
存在・一意性は主張しない。acceptedならQ007gでdefectとderivative variationを用いるa posteriori gateを
別途事前登録する。rejectedなら、半径・one-step・10-stepのどこで平衡marginを失うかだけを診断し、同じ
データからmetric候補を追加しない。

### Q007f 結果

全7 validity gateと3つのhypothesis gateが通過した。

- transform roundtrip／imaginary leakage:
  `3.9730855178692216e-16 / 5.782992871388017e-17`
- maximum adapted-map derivative／adjoint relative error:
  `1.9411413072870177e-10 / 1.1552411204406219e-16`
- maximum projector-family residual／adapted tangent leakage:
  `1.864754803590191e-15 / 1.5024964047170558e-7`
- maximum equilibrium blockwise error／normal triplet residual／two-start disagreement:
  `2.6702431249639317e-15 / 8.851836222444479e-15 / 1.0678514354388054e-15`
- minimum population／tangent-cocycle singular value:
  `0.02752853237565495 / 0.8485215443610019`
- equilibrium adapted `gamma_1 / gamma_10`:
  `0.9988057257445231 / 0.979632953795698`
- amplitude `0.004`の`gamma_10`範囲／failure count:
  `0.9798077420025896–0.980286028267377 / 0`
- amplitude `0.01`の`gamma_10`範囲／failure count:
  `0.9802276957977255–0.9815609124608508 / 0`
- 全点のmaximum one-step `gamma_1`: `0.9991153531281403`

従って`registered finite-sample adapted-metric projected normal-cocycle dominance observed`として
`accepted`とする。Q007dのEuclidean棄却とQ007eの平衡点採択は変更しない。one-stepも観測上は全点で
1未満だったが、Q007fの性能主張は事前登録どおり10-stepに限る。

次はQ007gのa posteriori defect／derivative-variation gateである。ただし、適用する定理、Banach norm、
domain、inverse bound、tail／roundoff majorant、十分条件を先に固定する必要がある。これらを事前登録する
までは数値campaignを開始せず、Q007fをball全体・独立holdout・真のinvariant normal bundle・存在定理へ
読み替えない。

## Q007g: nonresonant-manifold theorem／a posteriori readiness audit — 事前登録

### 問い

Q006iからQ007fまでの現行証拠だけで、固定保存量葉上の24実次元candidate chartに対して、
非共鳴スペクトル部分空間に接する局所不変多様体の定理を適用できるか。またquartic chart
\(W_4\)の近傍に真の解があることを定量的a posteriori boundで示す準備が整っているか。

このgateは新しい有限方向campaignではなく、定理の仮定と既存artifactの差分を監査する
theorem-applicability auditである。定理選定中の探索計算でspectral quotientが
\(L=89\)となることを既に観測したため、その再現を独立hypothesis testとは呼ばない。

### 固定する定理と空間

存在・局所一意性の基準には Cabré--Fontich--de la Llave,
*The Parameterization Method for Invariant Manifolds I: Manifolds Associated to
Non-Resonant Subspaces* の
[Theorem 1.2とRemark 5](https://upcommons.upc.edu/bitstream/handle/2117/876/0202cabre.pdf)
を使う。他のKAM torus、flowのstable manifold、またはradii-polynomial定理を今回の写像へ
そのまま転用しない。

- \(X\) は \(17^2\) D2Q9状態をrest equilibriumのまわりで中心化し、global mass・momentumを
  固定した実2598次元葉の複素化とする。
- \(F:X\to X\) は \((\eta,\omega)=(0.01,1.5)\) のstreaming、BGK collision、保存的5点filterから
  なる一step写像の固定葉制限とする。
- \(X_1\) はQ006hで固定した8 signed first-shell blockのshear／acoustic cluster、複素次元24とし、
  \(X_2\) はQ007eと同じRiesz不変補空間、複素次元2574とする。
- \(A=DF(0)\)、\(A_1=A|_{X_1}\)、\(A_2=A|_{X_2}\) とする。graph gauge以外のsplitへ
  post-hocに変更しない。

Theorem 1.2のtail条件を満たす最小整数を

\[
L_* = \min\left\{L\ge1:
\frac{\rho(A_1)^{L+1}}{\min_{\mu\in\operatorname{Spec}(A_2)}|\mu|}<1
\right\}
\]

と定義する。必要なexternal nonresonanceは全次数 \(2\le i\le L_*\) について

\[
\operatorname{Spec}(A_1)^{i}\cap\operatorname{Spec}(A_2)=\varnothing
\]

である。次数4までquartic係数を解けたことを、次数5以降の非共鳴へ外挿しない。

### 構造・数値validity gate

- source hashとQ006i、Q007a、Q007c、Q007e、Q007fの固定入力・次元・parameterを一致させる。
- BGK equilibriumが全local density非零の複素近傍で解析的であること、\(\omega\ne1\)、
  filter multiplierの厳密下界 \(1-2\eta>0\)、streamingの可逆性から、\(DF(0)\)とその固定葉制限が
  可逆であることを構造的に記録する。
- 289 Fourier blockから得る全2598固有値がfiniteかつnonzero、selected／excluded次元が
  `24 / 2574`、Q007eのselected minimum／excluded maximum modulusをrelative error
  `<=1e-10`で再現する。
- \(L_*\)について、登録比 \(\rho(A_1)^{L_*+1}/\min|\operatorname{Spec}(A_2)|<1\) と、
  一つ前の比 \(\rho(A_1)^{L_*}/\min|\operatorname{Spec}(A_2)|\ge1\) を同時に確認する。
  両境界からのmarginはそれぞれ`>=1e-6`を要求する。このfloat64計算は次数範囲の
  prequalificationであり、厳密なスペクトル包含とは呼ばない。
- 次数2、3、4について、それぞれ全`300 / 2600 / 17550` unordered monomial、numerical singular
  block `0`、既存artifactのminimum singular value／maximum conditionを再現する。artifact自体の
  SHA-256も保存する。
- 全値をfinite、strict JSONとし、一つでもvalidityが落ちれば`inconclusive`とする。

### theorem-readiness判定

validity通過後、次を別々に判定する。

1. `qualitative_theorem_ready`:
   解析性・局所可逆性・不変splitに加え、全次数 \(2,\ldots,L_*\) のexternal nonresonanceが
   interval／outward-rounded enclosureまたは代数的証明で認証済みであること。
2. `quantitative_chart_ready`:
   1に加え、対象Banach関数空間とnorm、chart domainとrange buffer、graph gauge、
   線形化不変性作用素のrigorous inverse bound、domain全体のdefect majorant、derivative-variation
   majorant、有限Taylor tail、roundoff enclosure、および採用定理そのものの厳密な十分不等式が
   全て固定され、strictに通過していること。

次数2--4のfloat64 SVDはnumerical prequalificationに限り、1の認証済み次数へ数えない。
`qualitative_theorem_ready`が偽なら`quantitative_chart_ready`も自動的に偽とする。

両方が真のときだけ`ready for a computer-assisted existence proof`として`accepted`とする。
どちらかが偽なら`current evidence is not theorem-ready`という有効な`not_ready`結果とし、最初の
未充足仮定、未認証次数、必要なproof objectを保存する。これはcandidate manifoldの不存在やQ007fの
有限sample結果の棄却を意味しない。

### 停止規則

Q007gでは新しい方向sample、defect最大化、metric retuning、存在半径の推定を行わない。
未認証次数またはproof objectが一つでも残れば、\(W_4\)近傍の存在・一意性・ball全体のnormal
attractionを主張せず、次の研究課題を最初のmissing layerに限定する。特に、一般の
radii-polynomial contraction theoremを引用するだけで、今回の離散写像に必要なoperator・tail boundを
省略しない。

### Q007g 結果

全6 validity gateが通過し、`current evidence is not theorem-ready`として有効な`not_ready`となった。

- selected spectral radius／excluded minimum modulus:
  `0.9920954673550985 / 0.49008513450158`
- spectral quotient \(L_*\): `89`
- degree-90 tail ratio／1つ前のratio:
  `0.9989422022329809 / 1.006901286320898`
- theoremが要求する次数: `2--89`の88次数
- sector-aware float64監査済み次数: `2, 3, 4`
- direct full-spectrum条件をinterval／代数的に認証した次数: `0`
- 未監査sector-aware次数／未認証direct次数: `85 / 88`

解析性、固定保存量葉の不変性、局所可逆性は構造的に通った。しかし既存homological SVDは各monomialの
Fourier和で決まるoutput sectorだけを監査しており、固定したTheorem 1.2の
\(\operatorname{Spec}(A_1)^i\cap\operatorname{Spec}(A_2)=\varnothing\)というfull-spectrum条件そのものでは
ない。Q007eのadapted state normもBanach関数normではない。rigorous inverse、domain buffer、defect、
derivative variation、Taylor tail、roundoff enclosure、十分不等式も未構築である。

従ってQ007fの有限sample採択、Q007dのEuclidean棄却、Q008cのTT棄却は変更しない。candidate manifoldの
不存在も主張しない。最初のmissing layerをoutward-rounded linear spectrumに固定する。

## Q007h: rational-interval linear spectral enclosure — 事前登録

### 問い

\((N,\eta,\omega)=(17,0.01,1.5)\) の固定保存量葉で、289 Fourier blockのselected／excluded
線形スペクトル、補空間の可逆性、normal gap、およびTheorem 1.2のdegree-90 tail不等式を、
platformの`sin`／`eig`の正確性を仮定せずoutward-roundedに認証できるか。

これは線形層だけのcomputer-assisted gateである。次数2--89のexternal nonresonance、Riesz projector norm、
quartic chart、有限半径normal cocycle、非線形多様体の存在・一意性は判定しない。

### exact symbolと区間生成

\(c_i\)をD2Q9速度、\(w_i\)を有理weightとし、collision symbolを有理数で

\[
C_{ij}=-\frac12\delta_{ij}
       +\frac32 w_i\left(1+3c_i\mathbin{\cdot}c_j\right)
\]

と構成する。wave index \((n_x,n_y)\) では

\[
A_n=m_n\,\operatorname{diag}
\left(e^{-2\pi i(n_xc_{ix}+n_yc_{iy})/17}\right)C,
\qquad
m_n=\frac{99}{100}+\frac1{200}
\left(\cos\frac{2\pi n_x}{17}+\cos\frac{2\pi n_y}{17}\right)
\]

を使う。

- `fractions.Fraction`だけでendpointを保持する。
- \(\pi=16\arctan(1/5)-4\arctan(1/239)\) を各96項の交代級数と次項remainderで包含する。
- canonical index `-8,...,8`のsin／cosを64項Taylor多項式とLagrange remainderで包含する。
- interval add／multiplyは全endpoint combinationから取り、floatへ丸めてgateを判定しない。
- \(n=(0,0)\) の固定葉は6重の厳密固有値\(-1/2\)として別扱いする。

### eigenvalue inclusion

各非零9次blockでNumPyの \((V,\Lambda)\) と \(W\simeq V^{-1}\) はpreconditionerとしてだけ使い、
全floatをexact dyadic rationalへ変換する。symbol intervalに対して

\[
R=AV-V\Lambda,
\qquad
\epsilon=\|I-WV\|_\infty<1,
\qquad
\beta=\frac{\|W\|_\infty}{1-\epsilon}
\]

を有理上界で評価する。これにより \(\|V^{-1}\|_\infty\le\beta\) であり、各真の固有値は

\[
r_{BF}=\|V\|_\infty\,\beta^2\,\|R\|_\infty
\]

を半径とする近似固有値円板の合併に入る。complex absolute valueの平方根もinteger `isqrt`から作る
有理上下界を使う。selected waveでは3個のselected円板群と6個のexcluded円板群が互いに素であることを
要求し、homotopyによる固有値countを固定する。

### validity gate

- Q007g source／artifact、grid、parameter、`24 / 2574 / 2598`次元を一致させる。
- Machin \(\pi\) intervalと全sin／cos intervalの幅を`<=1e-120`、全symbol entry rectangle幅を
  `<=1e-110`とする。
- 全288 nonzero blockで \(\epsilon<1\)、最大\(\epsilon\)`<=1e-10`、全Bauer--Fike radiusをfiniteかつ
  `<=1e-8`とする。
- 全8 selected waveでselected center countを3、selected／excluded円板群間距離を`>=1e-6`とする。
- float64 centerのselected minimum／maximum、excluded minimum／maximumをQ007g値からrelative error
  `<=1e-10`で再現する。
- conjugate waveとC4-related waveのcertified modulus boundsのendpoint差を`<=1e-12`とする。
- 全値finite、strict JSONとする。失敗時はspectral結論を使わず`inconclusive`とする。

### hypothesis gateと停止規則

validity通過後、有理endpointだけで次を別々に要求する。

1. selected spectral-radius upper bound \(<1\)
2. excluded minimum-modulus lower bound \(>0\)
3. selected minimum-modulus lower bound \(-\) excluded maximum-modulus upper bound \(>0\)
4. \(\rho_{F,+}^{90}/\mu_{E,-}<1\)
5. selected 24固有値とexcluded 2574固有値のcountが全block円板分離から確定する

全て通れば`registered linear spectral split and degree-90 tail certified`として`accepted`とする。
一つでも落ちれば`registered rational-interval linear certification failed`という有効な`not_certified`とする。
結果を見てTaylor項数、norm、radius式、selected clusterを変更しない。

acceptedでも、認証するのは固定17² filtered mapの線形層だけである。次数2--89のdirectまたは
translation-equivariant nonresonanceはQ007iへ残し、非線形存在主張を行わない。

### Q007h 封印結果

全288非零blockの有理区間計算は完了し、pi／trigonometric／symbol幅、Neumann inverse、Bauer--Fike半径、
selected円板群分離、Q007g再現、strict JSONは通過した。5 hypothesis gateもすべて通り、degree-90 tail
upperは`0.9989422022643313`だった。

しかし、各waveで独立に作ったpreconditionerによるC4-related modulus boundの最大endpoint差
`2.3299336398161276e-11`が登録閾値`1e-12`を超えた。共役差は0で、最悪C4 pairはexcluded群の
\((-5,4)\rightarrow(-4,-5)\)だった。停止規則に従いQ007hは`inconclusive`とし、線形認証を主張しない。
threshold、norm、radius式、selected clusterは変更しない。

## Q007h1: C4-orbit transported rational spectral enclosure — 事前登録

### 問い

Q007hの独立preconditionerだけをC4-equivariantに置き換え、exact symbol、区間幅、Neumann／Bauer--Fike式、
validity threshold、5 hypothesis gateを一切緩めず、固定17² mapの線形splitとdegree-90 tailを認証できるか。

これはQ007hの失敗値を削除・置換する再実行ではなく、観測されたC4 enclosure mismatchを対象にした新しい
封印gateである。Q007h artifactは`inconclusive`のまま入力として固定する。

### exact C4 orbitとpreconditioner輸送

wave rotationを

\[
r(n_x,n_y)=(-n_y,n_x)\pmod {17}
\]

とする。D2Q9 population permutation \(P\) は有理な0／1行列として、entrywiseに

\[
A_{r(n)}=P A_n P^{-1}
\]

を満たす向きへ一意に構成する。289 waveはzero orbit 1個とnonzero C4 orbit 72個に分け、各orbitの
lexicographic minimumを代表に固定する。

- NumPyの \((V,\Lambda)\) と \(W\simeq V^{-1}\) は72 nonzero代表でだけ計算する。
- \(r^j(n)\) では \(V_j=P^jV\)、\(W_j=WP^{-j}\)、\(\Lambda_j=\Lambda\) をexact dyadic／integer
  matrixとして使う。
- 各target blockでもQ007hと同じ区間残差、\(\epsilon\)、\(\beta\)、\(r_{BF}\) を独立に再評価する。
- selected／excluded labelは代表で固定し、permutationと同じorbit順で輸送する。
- zero waveはQ007hと同じ6重の厳密固有値\(-1/2\)とする。

### validity gate

- Q007h artifactのsource／scope／SHAを記録し、`failed / inconclusive`、失敗gateがC4 symmetryだけ、全5
  hypothesis gateがpassであることを要求する。
- orbit countを`73`、nonzero代表countを`72`、全nonzero member countを`288`とする。
- rational symbol rectangleについて、全C4 edgeで \(A_{r(n)}=P A_nP^{-1}\) がentrywiseに厳密一致し、
  mismatch countを0とする。
- Q007hと同じpi／trigonometric width `<=1e-120`、symbol width `<=1e-110`を要求する。
- 全288 nonzero blockで \(\epsilon<1\)、maximum \(\epsilon\)`<=1e-10`、全Bauer--Fike radiusをfiniteかつ
  `<=1e-8`とする。normとradius式はQ007hから変更しない。
- 全8 selected waveで3／6円板群gapを`>=1e-6`、countを`3 / 6`とする。
- Q007gのfloat64 center extremaをrelative error`<=1e-10`で再現する。
- conjugate／C4-related certified modulus endpoint differenceをexact `0`とする。
- 全値finite、strict JSONとする。失敗時は`inconclusive`とし、spectral結論を使わない。

### hypothesis gateと停止規則

validity通過後、Q007hと同じ有理endpointで次を要求する。

1. selected spectral-radius upper bound \(<1\)
2. excluded minimum-modulus lower bound \(>0\)
3. selected minimum-modulus lower bound minus excluded maximum-modulus upper bound \(>0\)
4. \(\rho_{F,+}^{90}/\mu_{E,-}<1\)
5. selected／excluded／fixed-leaf countが`24 / 2574 / 2598`

全て通れば`registered symmetry-equivariant linear spectral split and degree-90 tail certified`として
`accepted`とする。一つでも落ちれば`registered symmetry-equivariant linear certification failed`という有効な
`not_certified`とする。結果を見てorbit代表、permutation、Taylor項数、norm、radius式、selected cluster、閾値を
変更しない。

acceptedでも固定17² mapの線形層だけの認証である。次数2--89のdirect／translation-equivariant
nonresonanceはQ007iへ残し、非線形存在・一意性を主張しない。

### Q007h1 封印結果

全289 C4 symbol edgeはrational rectangleとしてentrywise exactに一致し、72代表から288 memberへ輸送した
\(\epsilon\)、\(\beta\)、Bauer--Fike radius、conjugate／C4 modulus endpointもexact 0差だった。全10
validity gateと全5 hypothesis gateが通過した。

selected spectral-radius upper、normal-gap lower、degree-90 tail upperはそれぞれ
`0.9920954673554099 / 0.0020611211596579977 / 0.9989422022620159`である。従ってQ007h1を
`registered symmetry-equivariant linear spectral split and degree-90 tail certified`として`accepted`とした。
Q007hの独立preconditioner版`inconclusive`は変更しない。

## Q007i: rational-log direct external nonresonance — 事前登録

### 問い

Q007h1が認証したselected spectrumについて、Cabré--Fontich--de la Llave Theorem 1.2のdirect条件

\[
\operatorname{Spec}(A_1)^i\cap\operatorname{Spec}(A_2)=\varnothing,
\qquad 2\le i\le89
\]

を、translation selection ruleへ弱めず、全次数で有理区間認証できるか。

Q007h1のdegree-90 tailと合わせれば、通過時には固定17²・固定保存量葉の有限次元解析写像へTheorem 1.2を
直接適用する。これはexplicit proof radiusを作るa posteriori theoremではなく、同論文の定性的な局所存在・
一意性定理の仮定監査である。

### certified diskの再構築

- Q007g、Q007h1 artifactのsource／scope／SHAを記録し、Q007h1が`passed / accepted`、全10 validity・全5
  hypothesis gate passであることを要求する。
- 72 nonzero C4代表だけでQ007h1のpreconditioner proofを再構築し、全representative blockの
  `exact_proof_digest_sha256`をartifactと一致させる。
- selected代表はaxis \((-1,0)\) とdiagonal \((-1,-1)\) の各3 disk、計6 diskとする。
- 各代表の虚部絶対値で、2 acoustic diskと1 real/shear diskを分ける。acoustic／shear center separationを
  `>=0.1`とし、曖昧ならvalidity failureとする。
- acoustic pairのmodulus intervalは2 diskのhullを取り、selected productを
  `axis acoustic / axis shear / diagonal acoustic / diagonal shear`の4型で過包含する。
- external spectrumは70通常代表の9 disk、2 selected代表の6 disk、zero waveの\(-1/2\) disk 1個、計643
  representative diskのunionで包含する。C4 multiplicityはQ007h1のexact similarityで処理する。

### rational logarithm

正の有理数 \(x<1\) に対し \(z=(x-1)/(x+1)\) として

\[
\log x=2\sum_{k=0}^{95}\frac{z^{2k+1}}{2k+1}+T,
\qquad
|T|\le
\frac{2|z|^{193}}{193(1-z^2)}
\]

を使う。endpointは`Fraction`で評価し、級数の各積・和は110桁decimal rational gridへ外向き丸めし、最終
log endpointを60桁gridへ再び外向き丸めする。全selected型とexternal diskのmodulus lower／upperへ単調性を
使ってlog intervalを作る。最大tail boundを`<=1e-90`とする。

degree \(n\) で4型のcountを \((a,b,c,d)\)、\(a+b+c+d=n\) とする。product modulusのlog intervalを

\[
aI_{aa}+bI_{as}+cI_{da}+dI_{ds}
\]

で包含する。次数2--89のaggregate countは`2,919,730`である。各acoustic pair内部の指数分配を展開した
6-center monomial product countが`869,107,778`となることも組合せ恒等式で照合する。

external log intervalは重なりをexact integer endpointでmergeし、各aggregate intervalとunionの交差を
binary searchで全件判定する。complex phaseは使わない。modulus intervalが交わらなければcomplex spectrumも
交わらないためである。

### design-only探索の開示

事前登録設計の計算量確認に限りfloat64 modulusで同じ圧縮を試したところ、radial overlap候補は0、予測最小
log-gapは約`6.91224e-10`、witnessはdegree 51、count \((1,19,27,4)\)だった。この値はQ007i artifactへ
流用せず、全endpoint、全aggregate、minimum witnessを有理log runnerから新規計算する。

### validity gate

- 入力artifact、`17² / 1.5 / 0.01 / 24 / 2574 / 2598` scopeを一致させる。
- C4 representative count `72`、proof-digest mismatch count `0`、selected disk `6`、selected modulus type `4`、
  external representative disk `643`を要求する。
- selected acoustic／shear分類marginを`>=0.1`とする。
- 96項log enclosureの最大tail boundを`<=1e-90`、110桁internal／60桁final外向き丸めを固定する。
- degree count `88`、aggregate count `2,919,730`、expanded product count `869,107,778`を一致させる。
- 全値finite、strict JSONとする。失敗時は`inconclusive`とし、非共鳴・定理適用を主張しない。

### hypothesis gateと停止規則

validity通過後、次を同時に要求する。

1. external merged log unionとのaggregate overlap countが0
2. 全2,919,730 aggregateを検査済み
3. global minimum rational log-gap lower boundが`>=1e-12`
4. Q007h1のdegree-90 tail gateとmap-structure gateがpass

全て通れば`registered direct external nonresonance through degree 89 certified`として`accepted`とする。
一つでも落ちれば`registered modulus-only direct nonresonance certification failed`という有効な
`not_certified`とする。同じgate内でcomplex phase、translation sector、項数、log精度、gap閾値を追加・変更しない。

### accepted時だけの定理帰結

Q007gの解析性・local diffeomorphism・固定保存量葉、Q007h1のstable selected split・excluded invertibility・
degree-90 tail、Q007iの次数2--89 direct nonresonanceが全て認証された場合に限り、Theorem 1.2から次を結論する。

- rest equilibrium近傍の固定保存量葉上に、selected 24実次元spectral subspaceへ接する局所解析的不変多様体が
  存在する。
- その多様体は、同じ接空間を持つ\(C^{90}\) locally invariant manifoldのクラスで局所一意である。
- 解析的parameterization \(K\) とreduced map \(R\) が存在する。

explicit neighborhood radius、Q007c1 quartic係数との厳密同定、finite-ball normal attraction、grid refinement、
continuum／infinite-lattice limitは結論しない。これらは次の定量・数値同定gateへ残す。

### Q007i 封印結果

全7 validity gateと全4 hypothesis gateが通過した。

- Q007h1 representative proof再構築: `72`、digest mismatch `0`
- selected representative／disk／modulus type: `2 / 6 / 4`
- external representative disk／merged log interval: `643 / 253`
- acoustic／shear分類margin lower: `0.20943761223015187`
- 96項log enclosure maximum tail: `1.5377133803221814e-92`
- degree／aggregate／expanded product count: `88 / 2,919,730 / 869,107,778`
- external overlap count: `0`
- global minimum rational log-gap lower: `6.912230841407495e-10`
- minimum witness: degree `51`、count `(1,19,27,4)`

従って`registered direct external nonresonance through degree 89 certified`として`accepted`とした。
Q007gの解析性・local diffeomorphism・固定保存量葉、Q007h1のstable split・excluded invertibility・degree-90
tailと合わせ、[Cabré--Fontich--de la Llave, Theorem 1.2](https://upcommons.upc.edu/bitstream/handle/2117/876/0202cabre.pdf)
を固定17² filtered mapへ直接適用できる。rest equilibrium近傍の固定保存量葉上に、selected 24実次元spectral
subspaceへ接する局所解析的不変多様体と解析的\(K,R\)が存在し、同じ接空間を持つ\(C^{90}\) locally invariant
manifoldのクラスで局所一意である。

これは定性的・局所的な存在結果である。explicit neighborhood radius、登録quartic係数との厳密同定、
finite-ball normal attraction、grid-uniform／continuum resultは得ていない。Q007hの独立preconditioner版
`inconclusive`、Q007dのEuclidean rejection、Q007fの有限sample acceptance、Q008cのTT rejectionも変更しない。
次の最小の未認証層は、Q006i以降の数値固有ベクトルが定理の厳密selected spectral subspaceを表すことの
区間固有対によるtangent bridgeである。

## Q007j: rational Krawczyk selected-eigencoordinate bridge — 事前登録

### 問い

Q006i以降の数値chartが使うselected right／left eigenvectorとbranch labelは、Q007iの定理で選ばれた厳密な
24実次元spectral subspaceおよびそのbiorthogonal coordinatesを表すと、有理矩形区間で認証できるか。

このgateはTaylor係数へ進む前の線形coordinate bridgeである。Q007iが既に示した多様体存在を再判定せず、
quadratic／cubic／quartic coefficient、explicit radius、finite-ball attractionは判定しない。

### 固定入力と上流再現

- `q006i_full2d_quadratic.json` SHA-256を
  `347d5349af349618333df17733ba372c8ca6f5ee02784a9e788898acefb5db89`へ固定する。source／scope、全validity
  pass、scientific outcome `rejected`、失敗hypothesisが`global_conservation`だけであることを照合する。
- Q006i modelをartifactから係数読込みせず再構築し、dense／reduced Hessian hashを
  `3f26eadcc6d25514671d9b741c53df5cf87c0dc598d0ff1cf9b9fd19f47d412f /`
  `61f5f3a9663a29022e1b41f56df0a6408d93d770a2821d012ba1974954645da5`と一致させる。
- `q007h1_equivariant_spectrum.json`／`q007i_direct_nonresonance.json`のSHA-256を
  `caee8fe382c0282e11e8139b8f434a944013f630288adf2e99223d0123c91af4 /`
  `c256b30ac5bfe0a6bc5e5f8e293016d3e0aa37c4bfa82ba81a0a2679d89e082f`へ固定し、それぞれ
  `passed / accepted`、Q007i `theorem_applies=true`を要求する。
- grid `17²`、`omega=1.5`、`eta=0.01`、固定保存量葉、selected実次元`24`を変更しない。

### 12個の正規化固有対問題

代表waveをaxis `(1,0)`、diagonal `(1,1)`、branch順を
`shear / acoustic_positive / acoustic_negative`とする。Q006iの数値right vectorで最大絶対成分をpivotに選ぶ
登録列は`2,0,0 / 1,0,0`、left vectorでは`5,7,8 / 8,7,5`とする。同率時は最小indexを使う。

right eigenpairではpivot成分を1へ固定し、残り8成分と固有値を

\[
z=(x_{j\ne p},\lambda)\in\mathbb C^9,
\qquad F_A(z)=Ax-\lambda x=0
\]

の9複素方程式として解く。left eigenpairにも \(A^*y-\mu y=0\)、\(\mu=\overline\lambda\) を同じ形式で使う。
従って2 wave × 3 branch × right／leftの12 systemを独立に認証する。

- \(A\) はQ007h1と同じMachin 96項、trigonometric 64項、140桁外向き丸めの有理Fourier symbolとする。
- center \(z_0\) はQ006i modeのfloat64値をexact dyadic rationalへ変換する。
- \(J_0=F'(z_0)\) のNumPy inverseはpreconditioner提案だけに使い、全entryをexact dyadic rationalへ変換する。
- 探索boxを各実部・虚部について固定半径 \(r=10^{-10}\) の
  \(X=z_0+[-r,r]+i[-r,r]\) とする。
- `Fraction` rectangleだけで

\[
K(z_0,X)=z_0-CF(z_0)+\bigl(I-CF'(X)\bigr)(X-z_0)
\]

  を評価する。各componentで\(K\)の\(z_0\)からの最大実部／虚部偏差を\(r\)で割った最大値を
  `Krawczyk utilization`と定義する。受理計算にfloat normやfinite-differenceを使わない。

### Q007h1 discとの対応と全24 modeへの輸送

- Q007h1のnegative axis／diagonal代表proofを再構築し、`exact_proof_digest_sha256`を一致させる。
- 各right-rootの固有値Krawczyk imageを共役し、対応するQ007h1 selected Bauer--Fike discの一つへ厳密に
  包含する。6 root全てが別のsimple selected discへ一対一対応することを要求する。
- right／left root boxから \(\langle y,x\rangle\) を区間評価し、0を含まないことを示す。Q006i rightの元のscaleを固定し、
  exact leftをbiorthogonalに再正規化して \(\langle \ell,r\rangle=1\) とする。
- Q007h1と同じexact population permutationと複素共役でaxis／diagonal代表を全8 selected waveへ輸送し、
  Q006iの全24 branch labelを被覆する。輸送後のexact root enclosureと登録mode centerのcomponentwise距離上界を
  right／biorthogonal-leftで保存する。

### design-only探索の開示

事前登録半径の計算量確認に限りfloat64で評価した。\(r=10^{-10}\)で予測maximum utilizationはright
`1.59798e-5`、left `3.31491e-5`、minimum pivot-normalized right／left overlap modulusは`1.27484`だった。
これらの値はartifactへ流用せず、全包含・距離・overlapを有理runnerから新規計算する。

### validity gate

1. 3 input artifactのSHA／source／scope／sealed outcomeとQ006i coefficient hashを再現する。
2. representative wave `2`、branch `6`、right／left system `12`、transport後mode label `24`、登録pivot列を一致させる。
3. pi／trigonometric width `<=1e-120`、symbol entry width `<=1e-110`、12 preconditioner inverse defect `<1`を要求する。
4. 全interval endpointをexact `Fraction`とし、全summaryをfinite・strict JSONにする。
5. Q007h1 representative proof digest mismatch、disc assignment collision、C4／conjugate label mismatchを全て0とする。

validityが一つでも落ちた場合は`inconclusive`とし、同じgateでpivot、半径、精度、normalizationを変更しない。

### hypothesis gateと停止規則

validity通過後、次を全て要求する。

1. 12 system全てで\(K(z_0,X)\subset\operatorname{int}X\)、maximum utilization `<=1e-3`
2. 6 right-root eigenvalue imageが相異なるQ007h1 selected discへ一意に包含される
3. 6 right／left overlap modulus lowerが`>=0.5`で、biorthogonal normalization denominatorが0を含まない
4. 全24輸送modeでregistered right／biorthogonal-left centerへのmaximum componentwise correction upperが`<=1e-9`

全て通れば`registered selected eigencoordinates rigorously bridge to the theorem spectral subspace`として
`accepted`とする。一つでも落ちれば`registered selected eigencoordinate bridge not certified`という有効な
`not_certified`とする。どちらの場合もQ007iの存在・一意性結論と過去の性能判定は変更しない。

acceptedの場合だけ、次のQ007kで300 quadratic pairのforcing／homological solveを区間化し、Q006iの数値二次jetを
定理多様体の厳密二次jetへ結び付ける。cubic／quarticとexplicit radiusはさらに別gateへ分ける。

## Q009: TT-cross は residual peak を見つけられるか — Q008cにより保留

### 問い

TT-cross chart は、dense/TT-SVD oracle と比較して independent \(L^\infty\) gate を
通るか。

cross points は validation に使わず、random、domain boundary、high-shear、
adversarial residual search を分けて保存する。

Q008cが登録TT-SVD候補を有効に棄却したため、固定Q007c1係数については開始しない。

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
