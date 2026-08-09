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

### Q007j 封印結果

全5 validity gateと全4 hypothesis gateが通過した。

- Q006i input／coefficient hash、Q007h1／Q007i input SHA reproduction: pass
- representative／branch／right-left system／transported mode: `2 / 6 / 12 / 24`
- maximum Krawczyk utilization: `3.453560282251993e-5`（登録上限`1e-3`）
- maximum interval-Jacobian contraction: `7.431317256896775e-9`
- Q007h1 selected-disc unique assignment／collision: `6 / 0`
- minimum right／left overlap modulus lower: `0.9888476879367266`
- maximum registered-center correction upper, right／biorthogonal-left:
  `1.153401559605646e-15 / 2.9617269241843315e-15`
- C4／conjugate label mismatch: `0`

従って`registered selected eigencoordinates rigorously bridge to the theorem spectral subspace`として
`accepted`とした。各代表固有対について、exact Fourier symbolを含むbox上で(K(X)\subset\operatorname{int}X)と
contraction `<1`を同時に示したため、固定pivot正規化のsimple eigenpairがbox内に一意に存在する。6 rootは
Q007h1の相異なるselected discへ一対一に入り、exact C4／共役輸送後もQ006iの全24 branch labelと対応する。

これはlinear eigencoordinate bridgeだけである。Q007iの多様体存在・一意性を変更せず、Q006i／Q007b／Q007c1の
quadratic／cubic／quartic係数、explicit neighborhood radius、finite-ball normal attraction、grid-uniform性は
まだ認証しない。次は300 quadratic pairだけをQ007kで扱う。

## Q007k: rational quadratic-jet bridge — 事前登録

### 問い

Q006iで保存した300 unordered pairの数値\(H_2,R_2\)は、Q007jが認証したexact eigencoordinatesを使う
graph-gauge quadratic homological equationの一意な厳密解を、登録誤差内で表しているか。

Q007iの定理多様体は解析的で、Q007jによりlinear coordinateは固定された。従ってこのgateが通れば、固定した
graph gaugeにおけるその多様体の二次Taylor jetとQ006i係数を結び付ける。cubic／quartic coefficient、explicit
neighborhood radius、finite-ball attractionは扱わない。

### 固定入力

- `q006i_full2d_quadratic.json`のnewline-normalized SHA-256を
  `347d5349af349618333df17733ba372c8ca6f5ee02784a9e788898acefb5db89`へ固定する。Q006iの全validity pass、
  `rejected`、失敗hypothesis `global_conservation`だけ、dense／reduced Hessian hashをQ007jと同じ値で再現する。
- `q007j_eigencoordinate_bridge.json` SHA-256を
  `feae846b81dc0991aa2c9babbd38ee72eb9ae493526655435cf0bf5951c7ec44`、runner source SHA-256を
  `7ef97e55ffff46244fee98d8017db1637a0e6c73ba3f1caf5c7dad77b7a26b57`へ固定する。`passed / accepted`、
  全5 validity／全4 hypothesis passを要求する。
- Q007jの12 representative Krawczyk proofをartifactからroot boxとして読まず再計算し、全
  `proof_digest_sha256`を一致させる。exact C4／共役輸送とbiorthogonal normalizationで全24 mode boxを再構築する。
- grid `17²`、`omega=1.5`、`eta=0.01`、固定保存量葉、mode／pair順序、Q006i係数を変更しない。

### exact quadratic forcing

各mode pair \((i,j)\)、output wave \(q=k_i+k_j\)について、Q007jのright-root rectangleから保存momentを作り、
D2Q9 equilibrium Hessian

\[
E_{s,11}=w_s(9c_{sx}^2-3),\quad
E_{s,22}=w_s(9c_{sy}^2-3),\quad
E_{s,12}=E_{s,21}=9w_sc_{sx}c_{sy}
\]

をexact rationalで適用する。streaming phaseとcheckerboard filter multiplierはQ007h1と同じMachin／Taylor
rational trigonometric tableから作る。従ってforcingの全entryは`Fraction` complex rectangleである。

保存moment行列 \(M\) について \(ME=0\) をentrywise exactに検証する。zero-wave pairではさらに
\(MA(0)=M\) と \(1-\lambda_i\lambda_j\ne0\) を有理区間で示し、厳密解の\(MH_{ij}=0\)を構造的に保証する。

### 300 homological system

- external output 156 pairとzero-wave kinetic 36 pairには

\[
B_{ij}=A(q)-\lambda_i\lambda_j I\in\mathbb C^{9\times9},
\qquad B_{ij}H_{ij}=-F_{ij}
\]

  を使う。zero-waveでもfull 9×9 systemを使い、上の保存恒等式からfixed-leaf解を同定する。
- selected internal output 108 pairには、output modeのexact right matrix \(V_q\) とbiorthogonal left matrix
  \(L_q^*\) を使うaugmented graph-gauge system

\[
\begin{bmatrix}
A(q)-\lambda_i\lambda_jI&-V_q\\
L_q^*&0
\end{bmatrix}
\begin{bmatrix}H_{ij}\\R_{ij}\end{bmatrix}
=
\begin{bmatrix}-F_{ij}\\0\end{bmatrix}
\]

  を使う。

pair countを`300 = 36 + 108 + 156`、output-wave supportを25、complex unknown countを
`36*9 + 156*9 + 108*12 = 3,024`へ固定する。Q006iのcomplex \(H_2,R_2\)をcenter \(z_0\)とし、各実部・
虚部の探索半径を\(r_2=10^{-6}\)に固定する。float64 inverseをexact dyadic preconditioner \(C\)へ変換し、

\[
K_2(z_0,X)=z_0-C(Bz_0-b)+(I-CB)(X-z_0)
\]

を全300 systemで有理矩形評価する。

### design-only探索の開示

Q006iのfloat64 operatorだけを再構築した設計計算では、pair countは`36 / 108 / 156`で一致し、maximum Newton
correction `1.1299557396374577e-12`、maximum inverse infinity norm `10453.339928940415`、maximum raw residual
`2.7817751139622836e-14`だった。これは半径と計算量の設定だけに使い、Q007kのforcing、operator、Krawczyk
image、witnessへ流用しない。

### validity gate

1. Q006i／Q007jのSHA、source、scope、sealed outcome、coefficient／runner／12 proof digestを全て再現する。
2. pair `300`、zero／internal／external `36 / 108 / 156`、support `25`、unknown `3,024`を一致させる。
3. rational equilibrium Hessian、\(ME=0\)、zero-wave \(MA(0)=M\)をentrywise exactに再現する。
4. pi／trigonometric width `<=1e-120`、symbol entry width `<=1e-110`、300 point inverse defect `<1`を要求する。
5. 全summaryをfinite・strict JSONとし、pair identifier、output wave／kindをQ006i artifactと全件一致させる。

validityが一つでも落ちた場合は`inconclusive`とし、同じgateで半径、basis、operator、精度を変更しない。

### hypothesis gateと停止規則

validity通過後、次を全て要求する。

1. 300 system全てで\(K_2(z_0,X)\subset\operatorname{int}X\)、maximum utilization `<=1e-2`
2. maximum interval contraction `<1`、singular／unassigned system `0`
3. exact rootから登録complex \(H_2,R_2\) centerへのmaximum componentwise correction upper `<=1e-8`
4. 36 zero-wave pair全てでproduct separation from 1が正、108 internal system全てでgraph-gauge rowを含む
   Krawczyk inclusionが通過

全て通れば`registered Q006i quadratic coefficients identify the theorem-manifold graph-gauge quadratic jet`として
`accepted`とする。一つでも落ちれば`registered quadratic-jet bridge not certified`という有効な`not_certified`とする。
Q006iのfloat64 global-conservation rejection、Q007i／Q007jの定理・線形認証、他の性能判定は変更しない。

acceptedの場合だけQ007lで2,600 cubic systemへ進む。quarticとexplicit radiusはさらに分離する。

### Q007k 封印結果

全5 validity gateと全4 hypothesis gateが通過した。

- Q006i／Q007j input SHA、Q007j runner SHA、coefficient hash、12 eigenpair proof digest reproduction: pass
- pair count zero／internal／external／total: `36 / 108 / 156 / 300`
- output-wave support／complex unknown: `25 / 3,024`
- rational equilibrium Hessianの \(ME=0\)、zero-wave \(MA(0)=M\): entrywise exact
- maximum point inverse defect: `4.42134771470068e-12`
- strict Krawczyk inclusion: `300 / 300`
- maximum Krawczyk utilization: `3.871467353051258e-6`（登録上限`1e-2`）
- maximum interval contraction: `2.262806292583543e-11`
- maximum registered-center correction upper, \(H_2 / R_2\):
  `4.012059355448033e-12 / 2.275730732794909e-14`
- maximum correction witness: `p00024`, `m001 × m001 → (2,0)`, external 9×9 system
- zero-wave product separation count／minimum lower: `36 / 0.015746583653469235`
- structural fixed-leaf／internal graph-gauge inclusion count: `36 / 108`
- pair identifier／wave／kind mismatch、singular／unassigned system: `0 / 0 / 0`

無丸めの有理端点を保持する最初の実装試行は、gate評価へ到達する前に20分で計算timeoutとなった。そこで
Q007h／Q007jの区間実装と同じ`INTERVAL_DECIMAL_DIGITS=140`を使い、各基本演算後に140桁有理格子へ
外向き丸めした。これは全boxを包含方向へ広げるだけで、探索半径、閾値、basis、operator、登録centerを
変更しない。timeout試行の部分値は判定へ使用していない。

従って
`registered Q006i quadratic coefficients identify the theorem-manifold graph-gauge quadratic jet`として
`accepted`とした。artifactのnewline-normalized SHA-256は
`022f9ded6b40dc754a1b935f69554db9407e5e07715bd9132990ca9876fc8bbf`、standalone runner source SHA-256は
`963862710b772a63a9293bbb100ea50a21f3469932ee54d84cfd197a384f89cb`である。

これは固定17²・固定保存量葉上の定理多様体について、固定graph gaugeの二次Taylor jetだけをQ006iの
登録complex係数へ同定する。Q006iのfloat64 global-conservation rejection、Q007b／Q007c1の有限振幅性能判定は
変更しない。cubic／quartic係数、explicit neighborhood radius、finite-ball normal attraction、grid-uniform性は
まだ認証しない。次はQ007lで2,600 cubic tripleだけを扱う。

## Q007l: rational cubic-jet bridge — 事前登録

### 問い

Q007bで保存した2,600 unordered tripleの数値\(H_3,R_3\)は、Q007jのexact eigencoordinatesとQ007kの
exact quadratic jetを使うgraph-gauge cubic homological equationの一意な厳密解を、登録誤差内で表しているか。

Q007iの定理多様体は解析的で、Q007j／Q007kにより一次・二次jetは固定された。従ってこのgateが通れば、固定した
graph gaugeにおけるその多様体の三次Taylor jetとQ007b係数を結び付ける。Q007bの有限振幅residual-ratio棄却は
性能判定として維持し、quartic coefficient、explicit neighborhood radius、finite-ball attractionは扱わない。

### 固定入力

- `q007b_cubic_continuation.json`のnewline-normalized SHA-256を
  `5524fd316bece33387a3d1f6590321bc74579c48a87ee31bba090a295f9fa6dd`へ固定する。`passed / rejected`、全7
  validity pass、失敗hypothesis `held_out_residual_ratio`だけを要求する。
- Q007bのcoefficient hashを次へ固定し、`build_full2d_cubic_model()`から再現する。
  - triple indices: `e646d2de7212c823cbca5804fbf20e9543918ecca80452dd508c278dfc5f130c`
  - output waves: `d431bfabad714d9d7ee9d8bfaf779eb2362ab27c916740494a379610c1389a6f`
  - chart coefficients: `ed182069713bff0558b806ce7a70e77299ea9fbc6671de38c4fa58019da5615b`
  - reduced coefficients: `4ca5a953833d5913f160e9fc36061e31697c7531865c4ef06d7517898f7c597e`
  - forcing coefficients: `6e2559a194d2b1e6a96f01653c1bccbe1852db00233700e16b3b980ae96df8eb`
- `q007k_quadratic_jet_bridge.json` SHA-256を
  `022f9ded6b40dc754a1b935f69554db9407e5e07715bd9132990ca9876fc8bbf`、runner source SHA-256を
  `963862710b772a63a9293bbb100ea50a21f3469932ee54d84cfd197a384f89cb`へ固定する。`passed / accepted`、
  全5 validity／全4 hypothesis passを要求する。
- Q007kをroot-box readerとして使わない。Q007jの12 eigenpair proofとQ007kの300 quadratic proofを再計算し、
  全`proof_digest_sha256`をartifactと一致させてから、対称な24×24のexact \(H_2,R_2\) boxを再構築する。
- grid `17²`、`omega=1.5`、`eta=0.01`、固定保存量葉、mode／triple順序、Q007b係数を変更しない。

### exact cubic forcing

unordered triple \((i,j,k)\)、output wave \(q=k_i+k_j+k_k\)について、Q007bと同じ三次forcing

\[
\begin{aligned}
F_{ijk}={}&D^3\Phi[V_i,V_j,V_k]
+D^2\Phi[H_{ij},V_k]+D^2\Phi[H_{ik},V_j]+D^2\Phi[H_{jk},V_i]\\
&-\sum_p\left(
\lambda_k H_{pk}R_{pij}
+\lambda_j H_{pj}R_{pik}
+\lambda_i H_{pi}R_{pjk}
\right)
\end{aligned}
\]

をexact complex rectangleで評価する。\(D^2\Phi\)にはQ007kのrational equilibrium Hessianを使う。
\(D^3\Phi\)は、保存moment \(m(x)=Mx\) と同じHessian \(E_s\) により

\[
D^3\Phi_q[x,y,z]_s=-\omega g(q)e^{-ic_s\cdot q}
\left[m_0(x)E_s(m(y),m(z))+m_0(y)E_s(m(x),m(z))+m_0(z)E_s(m(x),m(y))\right]
\]

とする。streaming／filterはQ007kと同じMachin／Taylor tableを使い、全基本演算後に
`INTERVAL_DECIMAL_DIGITS=140`の有理格子へ外向き丸めする。

保存恒等式 \(ME=0\) からzero-waveで \(M D^2\Phi=M D^3\Phi=0\) を構造的に示す。reduced-composition項は、
nonzero \(R_{pij}\) のwave-selection ruleとQ007kの36 fixed-leaf zero-wave \(H_{pk}\) certificateを列挙して
保存momentが0であることを示す。float64 cancellationを保存証明に使わない。

### 2,600 homological system

- external 1,448 tripleとzero-wave 108 tripleにはfull 9×9 system

\[
\left(A(q)-\lambda_i\lambda_j\lambda_k I\right)H_{ijk}=-F_{ijk}
\]

  を使う。Q007bのzero-wave 6×6 numerical restrictionはcenter生成だけの既存表現として再現し、Q007lの
  certificateはfull 9×9と積の1からの分離でfixed-leaf解を同定する。
- selected internal 1,044 tripleにはQ007kと同じexact \(V_q,L_q^*\) による12×12 augmented graph-gauge system

\[
\begin{bmatrix}
A(q)-\lambda_i\lambda_j\lambda_kI&-V_q\\
L_q^*&0
\end{bmatrix}
\begin{bmatrix}H_{ijk}\\R_{ijk}\end{bmatrix}
=
\begin{bmatrix}-F_{ijk}\\0\end{bmatrix}
\]

  を使う。

triple countを`2,600 = 108 + 1,044 + 1,448`、output-wave supportを49、complex unknown countを
`108*9 + 1,448*9 + 1,044*12 = 26,532`へ固定する。Q007bのcomplex \(H_3,R_3\)をcenter \(z_0\)とし、
各実部・虚部の探索半径を\(r_3=10^{-3}\)に固定する。float64 inverseをexact dyadic preconditioner \(C\)へ変換し、

\[
K_3(z_0,X)=z_0-C(Bz_0-b)+(I-CB)(X-z_0)
\]

を全2,600 systemで評価する。

### design-only探索の開示

Q007bの既存float64結果はmaximum condition number `10821.814847751179`、maximum homological residual
`7.5074201571007706e-13`である。Q007lのforcingを作らずQ007kの300 root boxだけを再構築した設計計算では、
maximum component width \(H_2/R_2\) は`5.787647966686327e-14 / 1.3739078996001612e-16`、maximum
component absolute upperは`34.04272577331188 / 1.0496353375362775`だった。これらは探索半径と計算量の設定だけに
使い、Q007lのcubic forcing、Krawczyk image、correction、witnessへ流用しない。

### validity gate

1. Q007b／Q007kのSHA、source、scope、sealed outcome、5 coefficient hash、runner、12＋300 proof digestを再現する。
2. triple `2,600`、zero／internal／external `108 / 1,044 / 1,448`、support `49`、unknown `26,532`を一致させる。
3. rational \(D^2\Phi,D^3\Phi\)、zero-wave保存恒等式、quadratic selection-rule chainをexactに再現する。
4. 140桁外向き丸め、pi／trigonometric width `<=1e-120`、symbol entry width `<=1e-110`、2,600 point inverse
   defect `<1`を要求する。
5. 全summaryをfinite・strict JSONとし、triple identifier、input modes、output wave／kindをQ007bと全件一致させる。

validityが一つでも落ちた場合は`inconclusive`とし、同じgateで半径、basis、operator、精度を変更しない。

### hypothesis gateと停止規則

validity通過後、次を全て要求する。

1. 2,600 system全てで\(K_3(z_0,X)\subset\operatorname{int}X\)、maximum utilization `<=1e-2`
2. maximum interval contraction `<1`、singular／unassigned system `0`
3. exact rootから登録complex \(H_3,R_3\) centerへのmaximum componentwise correction upper `<=1e-5`
4. 108 zero-wave triple全てでproduct separation from 1が正、1,044 internal system全てでgraph-gauge rowを含む
   Krawczyk inclusionが通過

全て通れば`registered Q007b cubic coefficients identify the theorem-manifold graph-gauge cubic jet`として
`accepted`とする。一つでも落ちれば`registered cubic-jet bridge not certified`という有効な`not_certified`とする。
Q007bの有限振幅性能棄却、Q007i／Q007j／Q007kの定理・jet認証、他の性能判定は変更しない。

acceptedの場合だけQ007mで17,550 quartic systemへ進む。explicit radiusはさらに分離する。

### Q007l 封印結果

全5 validity gateと全4 hypothesis gateが通過した。

- Q007b／Q007k input SHA、Q007k runner SHA、5 coefficient hash、12 eigenpair＋300 quadratic proof digest
  reproduction: pass
- triple count zero／internal／external／total: `108 / 1,044 / 1,448 / 2,600`
- output-wave support／complex unknown: `49 / 26,532`
- exact moment identities \(ME=0\)、\(M D^3\Phi=0\)、zero-wave selection chain: pass
- maximum point inverse defect: `2.9425645556416906e-12`
- strict Krawczyk inclusion: `2,600 / 2,600`
- maximum Krawczyk utilization: `2.2077918755524963e-5`（登録上限`1e-2`）
- maximum interval contraction: `1.4873927720660498e-11`
- maximum registered-center correction upper, \(H_3 / R_3\):
  `2.2540660753247895e-8 / 3.740068323953154e-12`
- maximum registered-forcing center difference upper: `2.811079918623627e-11`
- maximum correction witness: `t01623`
- zero-wave product separation count／minimum lower: `108 / 0.031245322922837878`
- structural fixed-leaf／internal graph-gauge inclusion count: `108 / 1,044`
- triple identifier／wave／kind mismatch、singular／unassigned system: `0 / 0 / 0`

従って
`registered Q007b cubic coefficients identify the theorem-manifold graph-gauge cubic jet`として
`accepted`とした。artifactのnewline-normalized SHA-256は
`aa0e572b43ed4f5544e2b8ead9d01c13bc08c47f40ec8963bcd37a1b51fc1bbd`、standalone runner source SHA-256は
`bb2be852c5413ceb2d27abd4f48db36ed2045ed79f2330e45ae89818067d33a4`である。

これは固定17²・固定保存量葉上の定理多様体について、固定graph gaugeの三次Taylor jetだけをQ007bの
登録complex係数へ同定する。Q007bの有限振幅residual-ratio棄却、Q007i／Q007j／Q007kの既存認証、
Q007c1の有限振幅quartic性能判定は変更しない。quartic jet、explicit neighborhood radius、finite-ball
normal attraction、grid-uniform性はまだ認証しない。次はQ007mを事前登録し、17,550 quartic systemだけを扱う。

## Q007m: rational quartic-jet bridge — 事前登録

### 問い

Q007c1で保存した17,550 unordered quartetの数値\(H_4,R_4\)は、Q007jのexact eigencoordinates、
Q007kのexact quadratic jet、Q007lのexact cubic jetを使うgraph-gauge quartic homological equationの
一意な厳密解を、登録誤差内で表しているか。

Q007iの定理多様体は解析的で、Q007j／Q007k／Q007lにより一次から三次までのjetは固定された。従って
このgateが通れば、固定graph gaugeにおけるその多様体の四次Taylor jetとQ007c1係数を結び付ける。
Q007c1の有限振幅directional-shadowing棄却は性能判定として維持し、explicit neighborhood radius、
finite-ball attraction、grid-uniform性は扱わない。

### 固定入力

- `q007c1_quartic_continuation.json`のnewline-normalized SHA-256を
  `680dddad3d84a8ea6fa030fb6e2ed7001e3bd0b4c55c79464a76daccef5ecdbc`へ固定する。`passed / rejected`、
  全8 validity pass、失敗hypothesis `held_out_directional_shadowing_ratios`だけを要求する。
- Q007c1のcoefficient hashを次へ固定し、`build_full2d_quartic_model()`から再現する。
  - quartet indices: `968b35d36cbd28c1f30e6cacb906649a42b36ba4e7bf4122394c2722cd809c16`
  - output waves: `9f9720e1114cc489ef7bbca81562e7d4cf211999e8d4a4958c06c02ee0df1fe8`
  - chart coefficients: `9597e0d31c32c940c76526754f0ec70c666e5fe03511977e80b3fd0610a7f29b`
  - reduced coefficients: `061cd66caf83850a45eeec05ed0f62fafb748a3076d7a6eb591bc69be2e008f7`
  - forcing coefficients: `6ab2337ea60b87dbe404e1aeb6b9c090fa8f950d43815966e0933879901b8eef`
- `q007l_cubic_jet_bridge.json`のnewline-normalized SHA-256を
  `aa0e572b43ed4f5544e2b8ead9d01c13bc08c47f40ec8963bcd37a1b51fc1bbd`、runner source SHA-256を
  `bb2be852c5413ceb2d27abd4f48db36ed2045ed79f2330e45ae89818067d33a4`へ固定する。`passed / accepted`、
  全5 validity／全4 hypothesis passを要求する。
- Q007lをroot-box readerとして使わない。Q007jの12 eigenpair proof、Q007kの300 quadratic proof、Q007lの
  2,600 cubic proofを再計算し、全`proof_digest_sha256`をartifactと一致させてから、対称なexact
  \(H_2,R_2,H_3,R_3\) boxを再構築する。
- grid `17²`、`omega=1.5`、`eta=0.01`、固定保存量葉、mode／quartet順序、Q007c1係数を変更しない。

### exact quartic forcing

unordered quartet \(I=(i_1,i_2,i_3,i_4)\)について、重複を含む4入力のpositionを保持し、output wave
\(q=k_{i_1}+k_{i_2}+k_{i_3}+k_{i_4}\)に対するQ007c1と同じ四次forcingを

\[
\begin{aligned}
F_I={}&D^4\Phi[V_{i_1},V_{i_2},V_{i_3},V_{i_4}]
+\sum_{a=1}^4D^2\Phi[H_{I_{\widehat a}},V_{i_a}]
+\sum_{\{a,b\}\mid\{c,d\}}D^2\Phi[H_{i_ai_b},H_{i_ci_d}]\\
&+\sum_{\{a,b\}\subset\{1,2,3,4\}}D^3\Phi[H_{i_ai_b},V_{i_c},V_{i_d}]-C_I,
\end{aligned}
\]

\[
\begin{aligned}
C_I={}&\sum_{a=1}^4\lambda_{i_a}\sum_p H_{p i_a}R^p_{I_{\widehat a}}
+\sum_{\{a,b\}\mid\{c,d\}}\sum_{p,r}H_{pr}R^p_{i_ai_b}R^r_{i_ci_d}\\
&+\sum_{\{a,b\}\subset\{1,2,3,4\}}\lambda_{i_c}\lambda_{i_d}
\sum_p H_{p i_c i_d}R^p_{i_ai_b},
\end{aligned}
\]

としてexact complex rectangleで評価する。pair-partitionは3個、pair subsetは6個で、最終二式の\(c,d\)は
選んだ\(a,b\)の補集合とする。\(D^2\Phi,D^3\Phi\)はQ007k／Q007lと同じexact actionを使う。
\(D^4\Phi\)は、保存moment \(m(x)=Mx\)、密度成分\(\rho(x)=m_0(x)\)、equilibrium Hessian \(E_s\) により

\[
D^4\Phi_q[x_1,x_2,x_3,x_4]_s=
2\omega g(q)e^{-ic_s\cdot q}
\sum_{\{a,b\}\subset\{1,2,3,4\}}
\rho(x_a)\rho(x_b)E_s\!\left(m(x_c),m(x_d)\right)
\]

とする。\(c,d\)は\(a,b\)の補集合である。streaming／filterはQ007lと同じMachin／Taylor tableを使い、
全基本演算後に`INTERVAL_DECIMAL_DIGITS=140`の有理格子へ外向き丸めする。

zero-waveでは\(M D^2\Phi=M D^3\Phi=M D^4\Phi=0\)をexactに示す。reduced-composition項は、
nonzero \(R_2,R_3\) のwave-selection ruleと、Q007kの36 zero-wave \(H_2\) certificate、Q007lの108
zero-wave \(H_3\) certificateを列挙し、保存momentが0であることを構造的に示す。float64 cancellationを
保存証明に使わない。

### 17,550 homological system

- external 12,168 quartetとzero-wave 846 quartetにはfull 9×9 system

\[
\left(A(q)-\lambda_i\lambda_j\lambda_k\lambda_l I\right)H_I=-F_I
\]

  を使う。Q007c1のzero-wave 6×6 numerical restrictionはcenter生成だけの既存表現として再現し、Q007mの
  certificateはfull 9×9と積の1からの分離でfixed-leaf解を同定する。
- selected internal 4,536 quartetにはQ007lと同じexact \(V_q,L_q^*\) による12×12 augmented
  graph-gauge system

\[
\begin{bmatrix}
A(q)-\lambda_i\lambda_j\lambda_k\lambda_lI&-V_q\\
L_q^*&0
\end{bmatrix}
\begin{bmatrix}H_I\\R_I\end{bmatrix}
=
\begin{bmatrix}-F_I\\0\end{bmatrix}
\]

  を使う。

quartet countを`17,550 = 846 + 4,536 + 12,168`、permutation multiplicity sumを`24^4 = 331,776`、
output-wave supportを81、full-9 zeroを含むcomplex unknown countを
`846*9 + 12,168*9 + 4,536*12 = 171,558`へ固定する。Q007c1のcomplex \(H_4,R_4\)をcenter \(z_0\)とし、
各実部・虚部の探索半径を\(r_4=1\)に固定する。float64 inverseをexact dyadic preconditioner \(C\)へ変換し、

\[
K_4(z_0,X)=z_0-C(Bz_0-b)+(I-CB)(X-z_0)
\]

を全17,550 systemで評価する。exact lower-jet actionはindex keyでmemoizeしてよいが、orbit reductionは行わず、
各quartet固有のoperator、forcing、Krawczyk image、proof digest、登録center比較を保存する。

### design-only探索の開示

Q007c1 artifactのfloat64 center／forcingからfull-9 zeroを含むoperatorを再構築した設計計算では、maximum
componentwise Newton correction `2.0390889938243303e-5`、maximum inverse infinity norm
`17069.89178200791`、maximum raw residual component `2.7055222062699613e-8`だった。maximum registered
component absolute value \(H_4/R_4\) は`37387748.021647185 / 51181.918535894125`だった。

四次forcingを作らず下位proofだけを再計算した設計計算では、maximum component width \(H_2/R_2\) は
`5.787647966686327e-14 / 1.3739078996001612e-16`、\(H_3/R_3\) は
`1.6758088396497935e-9 / 3.469449184104534e-12`、maximum component absolute upper \(H_2/R_2\) は
`34.04272577331188 / 1.0496353375362775`、\(H_3/R_3\) は
`11999.636051813919 / 30.28138575539409`だった。

これらは探索半径、補正上限、計算量の設定だけに使う。Q007mのexact quartic forcing、Krawczyk image、
correction、witnessへ流用しない。探索半径1は設計Newton補正の約49,000倍、登録補正上限`1e-2`は約490倍で、
最大登録\(H_4\)成分に対して探索半径は約`2.7e-8`の相対幅である。

### validity gate

1. Q007c1／Q007lのSHA、source、scope、sealed outcome、5 quartic coefficient hash、Q007l runner、
   12＋300＋2,600 proof digestを再現する。
2. quartet `17,550`、zero／internal／external `846 / 4,536 / 12,168`、multiplicity sum `331,776`、
   support `81`、unknown `171,558`を一致させる。
3. rational \(D^2\Phi,D^3\Phi,D^4\Phi\)、zero-wave保存恒等式、全reduced-composition selection chainを
   exactに再現する。
4. 140桁外向き丸め、pi／trigonometric width `<=1e-120`、symbol entry width `<=1e-110`、17,550 point
   inverse defect `<1`を要求する。
5. 全summaryをfinite・strict JSONとし、quartet identifier、input modes、output wave／kind、multiplicityを
   Q007c1と全件一致させる。memoizeした値は同じexact index keyの直接式と同一でなければならない。

validityが一つでも落ちた場合は`inconclusive`とし、同じgateで半径、basis、operator、精度、cache意味論を
変更しない。

### hypothesis gateと停止規則

validity通過後、次を全て要求する。

1. 17,550 system全てで\(K_4(z_0,X)\subset\operatorname{int}X\)、maximum utilization `<=1e-2`
2. maximum interval contraction `<1`、singular／unassigned system `0`
3. exact rootから登録complex \(H_4,R_4\) centerへのmaximum componentwise correction upper `<=1e-2`
4. 846 zero-wave quartet全てでproduct separation from 1が正、4,536 internal system全てでgraph-gauge rowを
   含むKrawczyk inclusionが通過

全て通れば`registered Q007c1 quartic coefficients identify the theorem-manifold graph-gauge quartic jet`として
`accepted`とする。一つでも落ちれば`registered quartic-jet bridge not certified`という有効な
`not_certified`とする。Q007c1の有限振幅性能棄却、Q007i／Q007j／Q007k／Q007lの定理・jet認証、
他の性能判定は変更しない。

acceptedの場合だけ、別のQ007nでexplicit local radiusを扱う。Q007m内でradiusやfinite-ball attractionへ
主張を拡張しない。

### Q007m 封印結果

全5 validity gateと全4 hypothesis gateが通過した。

- Q007c1／Q007l input SHA、Q007l runner SHA、5 coefficient hash、12 eigenpair＋300 quadratic＋2,600 cubic
  proof digest reproduction: pass
- quartet count zero／internal／external／total: `846 / 4,536 / 12,168 / 17,550`
- permutation multiplicity sum／output-wave support／complex unknown: `331,776 / 81 / 171,558`
- exact moment identities \(ME=0\)、\(M D^3\Phi=0\)、\(M D^4\Phi=0\)、zero-wave selection chain: pass
- zero-wave reduced-composition term count: `23,922`
- maximum point inverse defect: `7.49148423385146e-12`
- strict Krawczyk inclusion: `17,550 / 17,550`
- maximum Krawczyk utilization: `9.230907576183161e-5`（登録上限`1e-2`）
- maximum interval contraction: `5.4768769188623044e-11`
- maximum registered-center correction upper, \(H_4 / R_4\):
  `9.431388896713633e-5 / 5.8254184922091534e-8`
- maximum registered-forcing center difference upper: `7.961141571801268e-7`
- maximum correction witness: `q06996`
- zero-wave product separation count／minimum lower: `846 / 0.031245212410182764`
- structural fixed-leaf／internal graph-gauge inclusion count: `846 / 4,536`
- quartet identifier／wave／kind mismatch、singular／unassigned system: `0 / 0 / 0`

従って
`registered Q007c1 quartic coefficients identify the theorem-manifold graph-gauge quartic jet`として
`accepted`とした。artifactのnewline-normalized SHA-256は
`19090371bb7f8be1f59e47502f303f1c3eea18d3ccb365972363d377a214364b`、standalone runner source SHA-256は
`d086f2cc27684521c13daf7d2594cd21e5c0ad92f3953cca884c57d06986a918`である。

これは固定17²・固定保存量葉上の定理多様体について、固定graph gaugeの四次Taylor jetだけをQ007c1の
登録complex係数へ同定する。Q007c1の有限振幅directional-shadowing棄却、Q007i／Q007j／Q007k／Q007lの
既存認証、他の性能判定は変更しない。explicit neighborhood radius、finite-ball normal attraction、
grid-uniform性、continuum limitはまだ認証しない。次はQ007nを事前登録し、explicit local radiusだけを扱う。

## Q007n: fixed-leaf theorem manifold の explicit local radius — 事前登録

### 問いと主張範囲

Q007iが定性的に存在・局所一意性を与え、Q007j／Q007k／Q007l／Q007mが固定graph gaugeの
一次から四次までを同定した定理多様体について、複素化したselected modal coordinateの明示的な
\(\ell^1\) ball上で、解析的parameterization \(W\) とreduced map \(R\) の存在をBanach収縮として
直接認証できるか。

このgateは固定\(17^2\)、\(\omega=1.5\)、\(\eta=0.01\)、固定保存量葉だけを扱う。得られる値は
登録した候補格子上の保証半径であり、最大の数学的存在半径ではない。finite-ball normal attraction、
forward invariance、positivity、grid-uniform性、continuum limit、Q007c1の有限振幅性能棄却は扱わない。

### 固定入力

次のartifactのnewline-normalized SHA-256へ固定する。

- Q007h1: `caee8fe382c0282e11e8139b8f434a944013f630288adf2e99223d0123c91af4`
- Q007i: `c256b30ac5bfe0a6bc5e5f8e293016d3e0aa37c4bfa82ba81a0a2679d89e082f`
- Q007j: `feae846b81dc0991aa2c9babbd38ee72eb9ae493526655435cf0bf5951c7ec44`
- Q007k: `022f9ded6b40dc754a1b935f69554db9407e5e07715bd9132990ca9876fc8bbf`
- Q007l: `aa0e572b43ed4f5544e2b8ead9d01c13bc08c47f40ec8963bcd37a1b51fc1bbd`
- Q007m: `19090371bb7f8be1f59e47502f303f1c3eea18d3ccb365972363d377a214364b`

standalone runner source SHA-256はQ007j／Q007k／Q007l／Q007mについて順に
`7ef97e55ffff46244fee98d8017db1637a0e6c73ba3f1caf5c7dad77b7a26b57`、
`963862710b772a63a9293bbb100ea50a21f3469932ee54d84cfd197a384f89cb`、
`bb2be852c5413ceb2d27abd4f48db36ed2045ed79f2330e45ae89818067d33a4`、
`d086f2cc27684521c13daf7d2594cd21e5c0ad92f3953cca884c57d06986a918`へ固定する。
全artifactのsource、scope、sealed outcome、validity／hypothesis gateを再確認し、登録係数hashも
`build_full2d_quartic_model()`から再現する。既存artifactの証明箱自体は再探索しない。

### Banach空間、graph gauge、実半径への変換

24個のselected complex modeを\(b=(b_1,\ldots,b_{24})\)とし、
\(\|b\|_1=\sum_i|b_i|\)とする。full stateには、各離散Fourier waveの9 population係数を全部足す
Wiener \(\ell^1\) normを使う。これは周期畳み込みに対して劣乗法的である。

\[
 W(b)=Vb+H(b),\qquad R(b)=\Lambda b+G(b),
\]

とし、\(H,G\)は0次・1次係数を持たず、Q007jと同じgraph gauge
\(L_q^*H_q=0\)を満たす。次数\(n\)の対称多重線形係数には、入力\(\ell^1\)から出力
\(\ell^1\)へのoperator normを使い、半径\(\rho\)で次数別normを足す。pair normは

\[
 \|(H,G)\|_\rho=\max\{\|H\|_\rho,c_V\|G\|_\rho\},\qquad
 c_V=\max_i\sum_{s=0}^8 |(V_i)_s|
\]

とする。\(c_V\)はQ007jのexact root boxに対して、登録float64中心の
\(|\Re z|+|\Im z|\)とcomponent correction upperから有理数で上から囲む。

登録real coordinate \(a\in\mathbb R^{24}\)では
\(b_+=a_\mathrm{scale}(a_{\rm re}+ia_{\rm im})\)、
\(b_-=\overline{b_+}\)、\(a_\mathrm{scale}=1/(\sqrt2\,17)\)なので、

\[
 \|b\|_1\le {\sqrt{24}\over17}\|a\|_2.
\]

従って認証modal radius \(\rho_*\)から
\(r_{\mathbb R,2}=17\rho_*/\sqrt{24}\)を、含まれるreal Euclidean ballの半径として報告する。

### 全次数homological inverseの上界

Q007iのglobal rational log-gap lowerを\(\gamma\)、Q007h1のselected modulus lower／upperを
\(\underline\sigma_E,\overline\sigma_E\)、excluded modulus lowerを
\(\underline\sigma_\perp\)とする。modulus差の一様下界を

\[
 \delta_{2:89}=\min(\underline\sigma_\perp,\underline\sigma_E^{89})\gamma,
 \quad
 \delta_{90:}=\underline\sigma_\perp-\overline\sigma_E^{90},
 \quad
 \delta=\min(\delta_{2:89},\delta_{90:})
\]

とする。\(e^x-1\ge x\)により、最初の式はlog-gapからabsolute modulus gapへの厳密な変換である。
Q007h1の最大\(\beta\)を\(\beta_*\)とする。selectedでないnonzero output blockではQ007h1の
近似固有基底残差とBauer--Fike半径を使い、\(\|S\|_\infty\le9\)、
\(\|M\|_1\le9\|M\|_\infty\)から

\[
 C_{\rm ext}=81\beta_*/\delta
\]

とする。zero-wave fixed-leaf blockでは衝突作用が厳密に\(-I/2\)なので
\(C_0=1/\delta\)とする。

selected outputでは各次数・各monomial product \(p\)に対する12次bordered行列

\[
 B_q(p)=\begin{bmatrix}A(q)-pI&-V_q\\L_q^*&0\end{bmatrix}
\]

を使う。exact biorthogonalityと左右固有方程式により
\(|\det B_q(p)|\)は6個のexcluded eigenvalueとの差の積であり、\(\delta^6\)以上である。
exact collision entry、\(|p|<1\)、Q007j root boxから全entryのabsolute upperが2未満であることを
再確認し、Leibniz adjugate bound

\[
 C_{\rm int}=12!\,2^{11}/\delta^6
\]

を使う。対角化可能性や個別external eigenvectorの一意性は仮定しない。最終的なpair inverse boundは

\[
 C_L=\max\{C_{\rm ext},C_0,\max(1,c_V)C_{\rm int}\}
\]

とする。全式は`fractions.Fraction`で評価する。

### quartic centerとD2Q9非線形majorant

Q007k／Q007l／Q007mのexact root boxから、次数\(n=2,3,4\)のchart／reduced coefficient
operator norm upperを\(h_n,g_n\)とする。登録float64 complex centerには
\(|\Re z|+|\Im z|\)を使い、各出力成分へ登録component correction upperを加え、\(n!\)で割る。

\[
 h(t)=h_2t^2+h_3t^3+h_4t^4,\qquad
 g(t)=g_2t^2+g_3t^3+g_4t^4.
\]

D2Q9 equilibriumの保存moment表示と\(\omega=3/2\)から、density perturbationのWiener normが
\(x<1\)なら、streaming／filter後も含む非線形部は

\[
 n(x)={21\over2}{x^2\over1-x},\qquad
 n'(x)={21\over2}{x(2-x)\over(1-x)^2}
\]

で上から抑える。係数\(21/2\)は、D2Q9 weightsについて
\(\sum_sw_s(|c_{sx}|X+|c_{sy}|Y)^2\le8x^2/9\)、
\(X,Y\le x\)をexact rationalで再計算して確認する。

\(\sigma=\overline\sigma_E\)、\(v(t)=c_Vt+h(t)\)として、exact quartic jetの不変性残差は
4次まで厳密に消える。従って残差majorantを

\[
 E(\rho)=\operatorname{Tail}_{\ge5}
 \left[
 {21\over2}{v(t)^2\over1-v(t)}+
 \sum_{n=2}^4h_n\{(\sigma t+g(t))^n-(\sigma t)^n\}
 \right]_{t=\rho}
\]

とする。tailは方向samplingやfloat subtractionを使わず、非負係数の有理多項式／有理級数として
次数別に計算する。

### 固定したradii inequalityと候補選択

候補modal radiusは、順序も含めて

\[
 \mathcal R=\{10^{-j}:j=2,3,\ldots,120\}
\]

へ固定する。各\(\rho\)について

\[
 Y=C_LE(\rho),\qquad \tau=2Y,
\]

\[
 x=c_V\rho+h(\rho)+\tau,\qquad
 s=\sigma\rho+g(\rho)+\tau/c_V,
\]

\[
 Z=C_L\left[
 n'(x)+{g(\rho)+\tau/c_V\over\rho-s}
       +{h(\rho)+\tau\over c_V(\rho-s)}
 \right]
\]

をexact rationalで評価する。\(x<1\)、\(s<\rho\)、\(Z<1/2\)、
\(Y+Z\tau<\tau\)を全て満たす候補だけをpassとし、そのうち最大の\(\rho\)を\(\rho_*\)とする。
\(\tau=2Y\)を実行後に変えない。pass候補が無ければ有効な`not_certified`とする。

### validity gate

1. 全6 input artifact SHA、4 runner SHA、source、scope、sealed outcome、全既存gateを一致させる。
2. Q007c1の5 coefficient hashを再現し、Q007j／Q007k／Q007l／Q007m correction upperから
   \(c_V,h_2,h_3,h_4,g_2,g_3,g_4\)を有理数で構成する。
3. \(\gamma,\underline\sigma_E,\overline\sigma_E,\underline\sigma_\perp,\beta_*\)をartifactの
   base-16有理数から復元し、\(\delta>0\)、tail gap正、全bordered entry upper `<2`を確認する。
4. Wiener algebra、fixed-leaf zero block、bordered determinant identity、D2Q9 \(21/2\) majorantに必要な
   exact finite-dimensional identityを再計算する。
5. 全119候補についてtail非負、分母正の判定を保存し、全summaryをfinite・strict JSONとする。

validityが一つでも落ちれば`inconclusive`とし、basis、norm、候補、閾値を変更しない。

### hypothesis gateと停止規則

validity通過後、次を全て要求する。

1. \(\delta>0\)かつ\(C_L<\infty\)
2. 少なくとも一つの登録候補で\(x<1\)、\(s<\rho\)
3. 少なくとも一つの同じ候補で\(Z<1/2\)かつ\(Y+Z\tau<\tau\)
4. 保存した\(\rho_*\)が全pass候補の最大値であり、直前の大きい登録候補がfailするか\(10^{-2}\)である

全て通れば`registered quartic-centered contraction gives an explicit fixed-leaf local radius`として
`accepted`とする。これは\(\|b\|_1<\rho_*\)でexact analytic \(W,R\)を与え、exact certified quartic
jetからpair norm \(\tau\)以内にあることだけを主張する。Q007iの局所一意性と合わせて同じ定理多様体を
同定するが、normal attractionや実用的な大きさは主張しない。

一つでも落ちれば`registered explicit local radius not certified`という有効な`not_certified`とする。
acceptedでも半径が極端に小さい場合はそのまま記録し、次の改善gateでresolvent／bordered inverse boundを
鋭くする。候補格子やadjugate boundを事後変更して結果を良く見せない。

### Q007n 封印結果

全5 validity gateと全4 hypothesis gateが通過した。

- 全6 input artifact SHA、全4 predecessor runner SHA、source／scope／sealed gate: pass
- Q007c1の5 coefficient hash reproduction: pass
- Q007i representative proof count／stored proof-digest mismatch: `72 / 0`
- registered candidate／nonnegative-tail／positive-domain／pass count: `119 / 119 / 100 / 46`
- raw／80桁外向きworking absolute gap lower:
  `1.611328085325626e-10 / 1.611328085325626e-10`
- representative \(S_\infty\) upper／bordered-entry upper:
  `6.025984057925574 / 1.6509200830138158`（登録上限`9 / 2`）
- working \(c_V\): `2.7869014191713024`
- working \((h_2,h_3,h_4)\):
  `57.79951938835994 / 9032.836456317458 / 7811697.725656692`
- working \((g_2,g_3,g_4)\):
  `1.5391451988086782 / 16.74466889386485 / 4471.844336719125`
- pair homological inverse upper \(C_L\): `1.5620130640618827e71`
- largest passing modal radius／previous larger fail: `1e-75 / 1e-74`
- selected／previous contraction upper: `0.449393612526706 / 4.49393612526706`
- selected correction radius \(\tau=2Y\): `1.620396579477627e-295`
- selected radii-inequality margin: `8.2002417161445e-297`
- contained real \(\ell^2\) coordinate radius lower: `3.470110468942836e-75`

元のartifact／coefficient有理upperは保存したまま、候補走査に使うupperを80桁10進格子へ上向き、gap lowerを
下向きに丸めた。その後の全119判定は`fractions.Fraction`で行った。全候補にはexact signとbit lengthを、
選択候補`1e-75`と直前fail`1e-74`には完全なbase-16有理数を保存した。これは判定式や閾値の変更ではなく、
巨大分母を外向きに縮約した保守的な証明表現である。

従って
`registered quartic-centered contraction gives an explicit fixed-leaf local radius`として`accepted`とした。
artifactのnewline-normalized SHA-256は
`7fe09089744e41229e71666540e4885d560a4c27a2e8bc95a94d5959af0fbc36`、standalone runner source SHA-256は
`6eefae3386e5c49f151b1cd4537eb84fbb92858578fe4fce7768e50ad43c5dc9`である。

これは固定17²・固定保存量葉上で、Q007mのexact quartic jetからpair norm \(\tau\)以内にあるanalytic
parameterization \(W\) とreduced map \(R\)の存在を、\(\|b\|_1<10^{-75}\)で保証する。Q007iの局所一意性と
合わせて同じ定理多様体を同定する。ただし、この半径は登録10進格子上の保証値であって最適半径ではない。
極端な小ささは、内部bordered blockへ対角化不要の\(12!2^{11}\delta^{-6}\) adjugate boundを使ったためである。
Q007c1の有限振幅性能棄却、forward invariance、positivity、finite-ball normal attraction、grid-uniform性、
continuum limitは変更・認証しない。次はこの結論を維持したまま、内部resolvent boundだけを別gateで鋭くする。

## Q007o: exact external complement による internal resolvent 改善 — 事前登録

### 問い

Q007nで用いたselected-outputの12次bordered adjugate bound

\[
C_{\mathrm{adj}}=12!\,2^{11}\delta^{-6}
\]

を、graph-gauge右辺に固有のexact external complementへ制限したresolvent boundへ置き換えると、
Q007nの全次数gap、非線形majorant、候補半径格子を一切変更せずに、pair homological inverseと
explicit local radiusを厳密に改善できるか。

### 固定入力とscope

- `q007h1_equivariant_spectrum.json` SHA-256:
  `caee8fe382c0282e11e8139b8f434a944013f630288adf2e99223d0123c91af4`
- `q007j_eigencoordinate_bridge.json` SHA-256:
  `feae846b81dc0991aa2c9babbd38ee72eb9ae493526655435cf0bf5951c7ec44`
- `q007n_explicit_local_radius.json` newline-normalized SHA-256:
  `7fe09089744e41229e71666540e4885d560a4c27a2e8bc95a94d5959af0fbc36`
- Q007n standalone runner SHA-256:
  `6eefae3386e5c49f151b1cd4537eb84fbb92858578fe4fce7768e50ad43c5dc9`
- 固定map／葉／norm: \(17^2\), \(\omega=3/2\), \(\eta=1/100\),
  \(\delta M=\delta P_x=\delta P_y=0\), modal \(\ell^1\)／Fourier-population Wiener \(\ell^1\)／
  Q007nのpair max norm。
- Q007nのworking all-degree absolute gap lower、80桁外向き丸め、degree-2--4 jet majorant、
  D2Q9非線形majorant、`1e-2,...,1e-120`の119候補、収縮閾値`1/2`を固定する。
- 変更を許すのはselected-output internal blockのinverse upperだけである。external-output blockと
  zero-wave fixed-leaf blockのupperはQ007nからそのまま引き継ぐ。

### 固定したexternal-complement構成

selected output wave \(k\)で、Q007jが囲んだexact selected right／left matrixを
\(V_k,L_k\in\mathbb C^{9\times3}\)とする。simple eigenpairの異なる枝の直交性から
\(L_k^*V_k=I_3\)であり、

\[
P_k=V_kL_k^*,\qquad Q_k=I-P_k
\]

はexact selected／external spectral projectorで、\(A_kQ_k=Q_kA_k\)である。Q007jに保存された
maximum right／biorthogonal-left correctionを各実部・虚部へ外向きに加えたrectangleを
\(V_k,L_k\)の入力boxとする。

C4で全8 selected waveへ運ばれる2代表だけを直接評価する。

- axial representative \(k=(1,0)\): selector rows
  \(J=(0,1,2,3,7,8)\)
- diagonal representative \(k=(1,1)\): selector rows
  \(J=(0,1,2,3,4,5)\)

各代表でQ007h1と同じ`numpy.linalg.eig` centerを再構成し、modulus最大の3列をselected、残り6列を
返却順のまま\(E\in\mathbb C^{9\times6}\)、対応固有値を\(D=\operatorname{diag}(d_j)\)とする。
Q007h1のexact proof digestが一致しなければinvalidとする。上のselector rowsは実装後に選び直さない。

\[
U=Q_kE,\qquad C=JU,\qquad K=\operatorname{mid}(C)^{-1}
\]

とし、float centerの\(K\)はIEEE-754 dyadic rational point matrixとして固定する。complex rectangleの
induced \(\ell^1\) norm upperを用いて

\[
\epsilon_C=\|I-KC\|_1,\qquad
\kappa_C=\frac{\|K\|_1}{1-\epsilon_C}
\]

をexact `Fraction`で計算する。さらに

\[
R=A_kE-ED,\qquad
\gamma=\kappa_C\|JQ_kR\|_1
\]

とする。\(Q_k\)のexact可換性から
\(A_kU=UD+Q_kR\)であり、Q007nの固定gap lowerを\(\delta\)とすれば、

\[
C_H=
\frac{\|U\|_1\,\kappa_C\,\|JQ_k\|_1}{\delta-\gamma}
\]

はgraph-gauge chart correctionのinternal inverse upperになる。reduced correctionはbordered全逆行列を
評価せず、exact identity \(G=-L_k^*F\)から

\[
C_G=\|L_k^*\|_1
\]

で抑える。各代表のpair upperを

\[
C_{\mathrm{int},k}=\max(C_H,c_VC_G)
\]

とし、C4 permutation／complex conjugationが\(\ell^1\) normを保つことを用いて全8 waveへ適用する。
最終upperは2代表、Q007n external upper、zero-wave upperの最大を80桁格子へ上向きに丸める。

### validity gate

1. 3入力SHA、source／scope、Q007nの全validity／hypothesis gateとrunner SHAが一致する。
2. 2代表のQ007h1 proof digest、selected／external列数`3 / 6`、上記selector rowsが一致する。
3. 全interval endpointが有限で、両代表について
   \(\epsilon_C<10^{-8}\)、\(\gamma<\delta/2\)、従って\(\delta-\gamma>0\)である。
4. 2代表がC4の全8 selected waveを被覆し、Q007h1のexact covariance／Q007jの24 mode対応を変更しない。
5. Q007nのexternal／zero inverse、係数majorant、候補格子をbitwiseに再利用し、strict JSONを生成する。

一つでも落ちれば研究判定は`inconclusive`とし、半径改善を主張しない。

### hypothesis gate

validity通過時だけ次を判定する。

1. new internal pair inverse upperが`1e14`以下である。
2. new total pair inverse upperがQ007n値よりstrictに小さく、改善率が少なくとも`1e40`である。
3. 固定119候補のexact `Fraction`再走査で、Q007nの`1e-75`が引き続きpassし、最大pass候補が
   strictに大きくなる。
4. 新しい最大pass候補で`density buffer > 0`、`reduced range buffer > 0`、`Z < 1/2`、
   `Y + Z*tau < tau`がすべてstrictであり、直前の大きい候補はfailする。

全て通れば
`exact external-complement resolvent strictly sharpens the registered explicit radius`
として`accepted`とする。一つでも落ちれば
`registered external-complement resolvent did not certify a sharper radius`
という有効な`not_certified`とする。

### 主張境界

acceptedでも、これはQ007nと同じ固定17²・固定保存量葉上のanalytic existence radiusを鋭くするだけである。
最適半径、Q007c1の有限振幅directional shadowing、finite-ball normal attraction、forward invariance、
positivity、grid-uniform性、continuum limitは認証しない。external eigenvalueの個別一意性も仮定せず、
使うのはexact selected projectorと6次元external complement全体である。

### Q007o 封印結果

全6 validity gateと全4 hypothesis gateが通過した。

- 3 input artifact SHA／source／scope／Q007n runner SHA: pass
- Q007h1 axial／diagonal transported proof digest: `2 / 2` match
- selected／external column count: 各代表`3 / 6`
- C4 selected-wave coverage／Q007j 24-mode transport: pass
- Q007n old 119 candidate records exact reproduction: pass
- axial \(\epsilon_C/\gamma/C_{\mathrm{int}}\):
  `2.6657034780660514e-13 / 4.4155560973760785e-15 / 1.3284288681133191e11`
- diagonal \(\epsilon_C/\gamma/C_{\mathrm{int}}\):
  `3.724809047388777e-13 / 1.1339793519314153e-14 / 2.1920952274236575e11`
- Q007n working all-degree gap lower:
  `1.611328085325626e-10`
- working internal pair inverse upper:
  `2.1920952274236575e11`
- unchanged external-output／zero-wave inverse upper:
  `2.746444556852928e13 / 6.2060607588672085e9`
- new total pair inverse upper／Q007n old upper:
  `2.746444556852928e13 / 1.5620130640618827e71`
- registered inverse-upper reduction factor:
  `5.687400680142434e57`
- registered／passing candidate count: `119 / 103`
- largest passing modal radius／previous larger fail: `1e-18 / 1e-17`
- selected／previous contraction upper:
  `0.07901564138003579 / 0.7901564138003603`
- selected correction radius \(\tau\)／radii margin:
  `2.8490986842816327e-68 / 1.199425982247287e-68`
- contained real \(\ell^2\) coordinate radius lower:
  `3.470110468942836e-18`

Q007h1 artifactのpositive wave blockは独立固有分解ではなく、negative C4 representativeの
preconditionerをpopulation permutationでexact transportしている。この封印手順をそのまま再構成し、
`(1,0)`／`(1,1)`のproof digestを一致させた。exact selected projector \(Q=I-VL^*\)へQ007h1の
external center vectorsを射影し、固定selectorで\(JU\)の可逆性と
\(\gamma<\delta/2\)を有理intervalで認証した。external eigenvectorが個別に一意であることは使っていない。

従って
`exact external-complement resolvent strictly sharpens the registered explicit radius`
として`accepted`とした。artifactのnewline-normalized SHA-256は
`36a350b27658ce0699727640d65c48cf0700f999ca1881b07d45825d086158fd`、standalone runner source SHA-256は
`d34afda382784610ea2b8997e6c44376188b02c42668ade8e2d53ff9bc9afea7`である。

これはQ007nの全次数gap、degree-2--4 jet、D2Q9 nonlinear majorant、119候補を変えず、inverse upperだけを
改善した結果である。従って同じ定理多様体のfixed-leaf analytic existence radiusを`1e-18`へ鋭くした。
ただし新しいtotal inverseは据え置いたexternal-output upperに支配される。`1e-18`は最適半径ではなく、
Q007c1の有限振幅性能棄却、finite-ball normal attraction、forward invariance、positivity、grid-uniform性、
continuum limitは変更・認証しない。次はこの半径を固定入力としてfinite-ball normal attractionだけを
独立gateで扱う。

## Q007p: exact manifold の finite-tube normal attraction — 事前登録

### 問い

Q007oで存在を認証したexact fixed-leaf manifoldをgraph gaugeで固定し、その周囲の有限tube全体で
one-step fiber contractionとtangentに対するnormal dominationを同時に厳密化できるか。

### 固定入力

- `q007h1_equivariant_spectrum.json` SHA-256:
  `caee8fe382c0282e11e8139b8f434a944013f630288adf2e99223d0123c91af4`
- `q007n_explicit_local_radius.json` SHA-256:
  `7fe09089744e41229e71666540e4885d560a4c27a2e8bc95a94d5959af0fbc36`
- `q007o_external_complement_radius.json` SHA-256:
  `36a350b27658ce0699727640d65c48cf0700f999ca1881b07d45825d086158fd`
- Q007n／Q007o runner SHA-256:
  `6eefae3386e5c49f151b1cd4537eb84fbb92858578fe4fce7768e50ad43c5dc9` /
  `d34afda382784610ea2b8997e6c44376188b02c42668ade8e2d53ff9bc9afea7`
- map／葉: 固定17² filtered periodic D2Q9、\(\omega=3/2\)、\(\eta=1/100\)、
  \(\delta M=\delta P_x=\delta P_y=0\)。
- Q007oのanalytic chart domain \(\rho=10^{-18}\)と、そのselected boundary certificateの
  correction pair radius \(\tau\)を変更しない。
- finite tubeのbase modal radiusを
  \(r=10^{-19}\)、normal-coordinate radiusを\(\zeta=10^{-20}\)に固定する。
  結果を見てこれらを変更しない。

### graph-gauge tube

Q007j--Q007oが同定したexact selected analysisを\(\mathcal L\)、exact manifoldを

\[
W(a)=Va+H(a),\qquad \mathcal L W(a)=a,\qquad \mathcal L H(a)=0
\]

とする。固定external spectral complementを\(X_n=\ker\mathcal L\)とし、

\[
\mathcal T_{r,\zeta}
=\{\,x=W(a)+z:\|a\|_1\le r,\ z\in X_n,\ \|z\|_*\le\zeta\,\}
\]

を判定対象とする。real stateではFourier共役制約を課し、zero waveは保存3成分を除いたkinetic 6次元だけを
含める。

### 固定external-coordinate norm

各Fourier blockのnormal coordinateを次で固定し、global \(\|\cdot\|_*\)はblock normの和とする。

1. \(k=0\): fixed-leaf kinetic population vectorのphysical complex \(\ell^1\) norm。
2. 8 selected wave: Q007oの\(U_k=Q_kE_k\)、\(C_k=J_kU_k\)を使い、
   \(z_k=U_kc_k\)、\(\|z_k\|_*=\|c_k\|_1\)。
3. その他280 nonzero wave: Q007h1のC4 representativeで得たfull
   \(E_k\in\mathbb C^{9\times9}\)をexact transportし、
   \(z_k=E_kc_k\)、\(\|z_k\|_*=\|c_k\|_1\)。

nonselected 70 C4 representativeではQ007h1と同じ`numpy.linalg.eig` center、returned column order、
inverse candidateを用いる。rational symbol boxに対し

\[
\epsilon_k=\|I-K_kE_k\|_1,\quad
\kappa_k=\frac{\|K_k\|_1}{1-\epsilon_k},\quad
\gamma_k=\kappa_k\|A_kE_k-E_kD_k\|_1
\]

を`Fraction`で評価し、

\[
q_{0,k}=\max_j|d_{k,j}|+\gamma_k
\]

とする。selected 2代表はQ007oのcoordinate inverse／projected residualを再利用し、
同じ式の6次元external \(q_{0,k}\)を作る。zero blockは\(q_{0,0}=1/2\)とする。C4
population permutation／complex conjugationは\(\ell^1\) normを保つので代表upperをorbit全体へ用いる。

global conversion constantを

\[
K_s=\sup_{z\ne0}\frac{\|z\|_{\mathrm W}}{\|z\|_*},\qquad
K_a=\sup_{y\ne0}\frac{\|Qy\|_*}{\|y\|_{\mathrm W}},\qquad
K_L=\|\mathcal L\|_{\mathrm W\to\ell^1}
\]

とする。ここで\(\|\cdot\|_{\mathrm W}\)はQ007nのFourier-population Wiener \(\ell^1\) normである。
各定数はblockwise synthesis／certified inverse／selected-left boxの最大から構成する。

### nonlinear tube majorant

Q007nのworking \(c_V,h_2,h_3,h_4,g_2,g_3,g_4\)、Q007oの\(\rho,\tau\)をbitwiseに再利用する。

\[
\begin{aligned}
w(s)&=c_Vs+\sum_{j=2}^4h_js^j+\tau,\\
r_R(s)&=\rho_s s+\sum_{j=2}^4g_js^j+\tau/c_V,\\
d_H(s)&=\sum_{j=2}^4j h_js^{j-1}+\frac{\tau}{\rho-s},\\
d_G(s)&=\sum_{j=2}^4j g_js^{j-1}
       +\frac{\tau}{c_V(\rho-s)},\\
d_N(x)&=\frac{21}{2}\frac{x(2-x)}{(1-x)^2}.
\end{aligned}
\]

\(d_H,d_G\)の最後の項はfull \(\rho\)-ball上のanalytic correctionに対するCauchy boundである。
次をexact rationalで順に計算する。

\[
\begin{aligned}
x_*&=w(r)+K_s\zeta,\\
a_*&=r_R(r)+K_Ld_N(x_*)K_s\zeta,\\
q_*&=q_0+K_aK_sd_N(x_*)\bigl(1+K_Ld_H(a_*)\bigr),\\
m_T&=\underline\mu_s-d_G(r),\\
\Gamma_*&=q_*/m_T.
\end{aligned}
\]

ここで\(q_0=\max_kq_{0,k}\)、\(\underline\mu_s\)はQ007h1 selected minimum-modulus lowerである。
linear external vectorには\(\mathcal L A_0z=0\)がexactに成り立つため、off-manifold base driftには
nonlinear derivativeだけが入る。

fiber mapを

\[
a_+=\mathcal L\Phi(W(a)+z),\qquad
z_+=\Phi(W(a)+z)-W(a_+)
\]

とすると、そのfiber derivativeは

\[
\bigl(Q-DH(a_+)\mathcal L\bigr)D\Phi(W(a)+z)|_{X_n}
\]

である。上の\(q_*\)はこのoperatorの\(\|\cdot\|_*\) upperであり、segment積分から
\(\|z_+\|_*\le q_*\|z\|_*\)を与える。

### validity gate

1. 3 artifact SHA、2 runner SHA、source／scope、全upstream validity／hypothesis gateが一致する。
2. nonselected 70 representativeのQ007h1 proof digestが全一致し、C4 orbit count
   `70*4 + 2*4 + 1 = 289`を再現する。
3. 全70 full coordinateで\(\epsilon_k<10^{-8}\)、selected 2 coordinateでQ007o certificateを再現する。
4. \(K_s\le4\)、\(K_a\le40\)、\(K_L\le2\)で、全boundがfinite positive rationalである。
5. Q007n coefficient majorant、Q007o \(\rho,\tau\)、D2Q9 \(21/2\) derivative majorantをexactに再利用する。
6. fixed-leaf zero block、\(\mathcal L A_0Q=0\)、C4 norm invarianceの構造auditとstrict JSONを通す。

一つでも落ちれば`inconclusive`とし、normal-attraction値を解釈しない。

### hypothesis gate

validity通過時だけ次を判定する。

1. density／analytic domain: \(x_*<1\)、\(a_*<r<\rho\)。
2. base forward invariance: \(a_*<r\)がstrictである。
3. normal fiber contraction: \(q_*<0.99<1\)、従って\(q_*\zeta<\zeta\)。
4. tangent invertibility／normal domination:
   \(m_T>0\)、\(\Gamma_*=q_*/m_T<0.999<1\)。

全て通れば
`registered fixed-leaf tube is uniformly normally attracting in the external-coordinate norm`
として`accepted`とする。一つでも落ちれば
`registered finite tube did not certify uniform normal attraction`
という有効な`not_certified`とする。

### 主張境界

acceptedなら、固定17²・固定保存量葉のexact theorem manifoldについて、
\(\|a\|_1\le10^{-19}\)、\(\|z\|_*\le10^{-20}\)の明示tubeがforward invariantで、
normal fiberがone-stepで一様収縮し、tangentよりstrictに速く収縮すると主張する。
これはQ007fのsampled 10-step observationではなくfull registered tubeの解析boundである。

ただし\(\|\cdot\|_*\)は固定Fourier external-coordinate normであり、Euclidean normではない。
Q007dのEuclidean棄却、Q007c1の有限振幅性能棄却、population positivity、より大きいtube、
global basin、grid-uniform性、continuum limitは変更・認証しない。

### Q007p 封印結果

判定は`accepted`である。

- 3 input artifact SHA／source／scope／全upstream gate: pass
- registered Q007n／Q007o runner SHA: pass
- nonselected／selected C4 representative: `70 / 2`
- represented wave block／external complex dimension: `289 / 2574`
- Q007h1 proof digest mismatch／Q007o selected replay mismatch: `0 / 0`
- maximum nonselected coordinate defect: `9.306827894107678e-15`
- global linear external contraction \(q_0\): `0.981709835832552`
- \(K_s/K_a/K_L\):
  `2.888267212368763 / 29.917136268364473 / 1.5106842091904618`
- \(x_*/a_*/r/\rho\):
  `3.075728140408179e-19 / 9.920954673554099e-20 / 1e-19 / 1e-18`
- base forward-invariance margin: `7.904532644590156e-22`
- normal contraction \(q_*\)／registered-cap margin:
  `0.9817098358325526 / 0.008290164167447421`
- normal tube margin \(\zeta-q_*\zeta\): `1.8290164167447423e-22`
- tangent conorm \(m_T\): `0.9837709569923394`
- domination ratio \(\Gamma_*\)／registered-cap margin:
  `0.9979048769989224 / 0.0010951230010776572`
- runner SHA-256:
  `23ff283acb3f872fd2ff489f17d94b8e022e3f45a5c65b5523bf976c534a9f2a`
- artifact newline-normalized SHA-256:
  `a5e766938cfee0174deba9c529be9aec2cce4bff9225a3a4a1da83f7d255a751`

従って固定17²・固定保存量葉のQ007o exact manifoldについて、登録した
\(\|a\|_1\le10^{-19}\)、\(\|z\|_*\le10^{-20}\)のtubeはforward invariantであり、normal fiberは
one-stepで一様に収縮し、tangentよりstrictに速く収縮する。これはQ007fの有限sample観測ではなく、
登録tube全体のexact rational majorantである。

ただし認証normは固定Fourier external-coordinate block-sum \(\ell^1\)であり、Euclidean normではない。
Q007dのEuclidean棄却、Q007c1の有限振幅性能棄却、population positivity、より大きいtube、global basin、
grid-uniform性、continuum limitは変更・認証しない。次の研究gateではこのtubeを拡大解釈せず、未解決課題を
別途事前登録する。

## Q007q: registered finite tube の population positivity — 事前登録

### 問い

Q007pでforward invariantと認証した固定tube全体が、rest equilibriumを中心とするphysical D2Q9
populationのstrict positive coneに含まれることを、Fourier--Wiener normから厳密に認証できるか。

### 固定入力

- `q007p_finite_tube_attraction.json` newline-normalized SHA-256:
  `a5e766938cfee0174deba9c529be9aec2cce4bff9225a3a4a1da83f7d255a751`
- Q007p runner SHA-256:
  `23ff283acb3f872fd2ff489f17d94b8e022e3f45a5c65b5523bf976c534a9f2a`
- map／葉／tube: Q007pと同じ固定17² filtered periodic D2Q9、\(\omega=3/2\)、
  \(\eta=1/100\)、固定保存量葉、
  \(\|a\|_1\le10^{-19}\)、\(\|z\|_*\le10^{-20}\)。
- Q007pのexact tube-state Wiener upper \(x_*\)を変更せず再利用する。追加のradius、rounding、
  sampling parameterは導入しない。

### exact positivity bound

rest equilibriumを\(f_i^*=w_i\)とし、D2Q9 weightsを

\[
w_0=\frac49,\qquad
w_{1,\ldots,4}=\frac19,\qquad
w_{5,\ldots,8}=\frac1{36}
\]

とする。Q007pのFourier-population Wiener normでは、real state
\(\delta f=f-f^*\)に対し、各site \(x\)、各population \(i\)で

\[
\left|\delta f_i(x)\right|
=\left|\sum_k\widehat{\delta f}_{k,i}e^{ik\cdot x}\right|
\le \sum_k\left|\widehat{\delta f}_{k,i}\right|
\le \|\delta f\|_{\mathrm W}
\le x_*.
\]

従って全populationとdensityに対する登録lowerを

\[
p_*=\frac1{36}-x_*,
\qquad
d_*=1-x_*
\]

と固定する。Q007pのtube forward invarianceと組み合わせ、初期時刻だけでなくfull-map sampling
時刻 \(n=0,1,2,\ldots\) の全iteratesへ同じlowerを適用する。

### validity gate

1. Q007p artifact／runner SHA、source、scope、全validity／hypothesis gate、
   4 theorem-consequence flagが一致する。
2. exact D2Q9 weight tableが`1 + 4 + 4` population、sum `1`、minimum `1/36`を再現し、
   全weightがstrict positiveである。
3. 17² Fourier index count `289`、phase modulus `1`、Q007pのWiener block-sum norm definitionから、
   \(\|\delta f\|_{\infty,\mathrm{population}}\le\|\delta f\|_{\mathrm W}\)のtriangle-inequality auditを通す。
4. Q007pの\(x_*\)、base／normal radius、forward-invariance theorem flagをexactに再利用する。
5. 全boundがfinite rationalで、strict JSONを生成する。

一つでも落ちれば`inconclusive`とし、positivity値を解釈しない。

### hypothesis gate

validity通過時だけ次を判定する。

1. density positivity: \(d_*=1-x_*>0\)。
2. population positivity: \(p_*=1/36-x_*>0\)。
3. forward positivity: Q007pのregistered tubeがforward invariantで、同じ\(p_*\)が全full-map iterateへ
   適用される。

全て通れば
`registered Q007p tube lies in the strictly positive population cone at every full-map iterate`
として`accepted`とする。一つでも落ちれば
`registered Q007p tube did not certify strict population positivity`
という有効な`not_certified`とする。

### 主張境界

acceptedなら、固定17²・固定保存量葉・登録Q007p tubeのreal stateについて、full one-step mapの入力／出力時刻で
全9 populationとdensityがstrict positiveであると主張する。

これはBGK collision直後、streaming直後、filter内部などのstagewise positivityを認証しない。entropy、
monotonicity、maximum principle、より大きいtube、global basin、grid-uniform性、continuum limit、
Q007c1の有限振幅性能、Q007dのEuclidean判定も変更・認証しない。

### Q007q 封印結果

判定は`accepted`である。

- Q007p artifact／runner SHA、source／scope／全sealed gate／4 theorem flag: pass
- exact D2Q9 population count／weight multiplicity: `9 / (1, 4, 4)`
- exact weight sum／minimum: `1 / 1/36`
- Fourier wave count／Wiener norm-definition audit: `289 / pass`
- Q007p base／normal radius:
  \(\|a\|_1\le10^{-19}\)、\(\|z\|_*\le10^{-20}\)
- chart radius upper \(w(r)\): `2.7869014191713026e-19`
- synthesis upper \(K_s\): `2.888267212368763`
- exact tube-state identity:
  \(x_*=w(r)+K_s\zeta\)
- tube-state Wiener upper \(x_*\): `3.075728140408179e-19`
- population lower: exact \(p_*=1/36-x_*>0\)
- density lower: exact \(d_*=1-x_*>0\)
- validity／hypothesis gate: `5 / 5`、`3 / 3` passed
- runner SHA-256:
  `026b4d549e92bf74ac29393244a4400fb7a8d1bb3eb263ee729d81432c8290e5`
- artifact newline-normalized SHA-256:
  `e8c763419f6e803f102f81a3beb957261b736754ab490ca3cb914dc9247269cb`

従って固定17²・固定保存量葉・登録Q007p tubeの全real stateは、D2Q9のstrict positive population coneに
含まれる。Q007pのforward invarianceと合わせ、全9 populationとdensityはfull one-step mapの
入力／出力時刻 \(n=0,1,2,\ldots\) でstrict positiveである。

浮動小数表示では\(x_*\)が機械精度より十分小さいため、\(p_*\)は`1/36`、\(d_*\)は`1`と
同じ表示へ丸められる。判定は保存した16進分子・分母から復元したexact rational差で行い、
strict inequalityをテストで再構成した。

この結果はcollision／streaming／filter内部stageのpositivity、entropy、monotonicity、maximum principle、
より大きいtube、global basin、grid-uniform性、continuum limitを認証しない。Q007c1の有限振幅性能棄却と
Q007dのEuclidean棄却も変更しない。stagewise positivityやtube拡大は、同じ判定へ混ぜず別gateとして
事前登録する。

## Q007r: registered finite tube の exact stagewise positivity — 事前登録

### 問い

Q007qでfull-map sampling時刻のstrict positivityを認証した同じ固定tubeについて、各one-step内部の
equilibrium evaluation、BGK collision後、periodic streaming後、five-point filter後でも全9 populationが
strict positiveであることを、exact Fourier--Wiener majorantから認証できるか。

### 固定入力

- `q007q_population_positivity.json` newline-normalized SHA-256:
  `e8c763419f6e803f102f81a3beb957261b736754ab490ca3cb914dc9247269cb`
- Q007q runner SHA-256:
  `026b4d549e92bf74ac29393244a4400fb7a8d1bb3eb263ee729d81432c8290e5`
- map／葉／tube: Q007p／Q007qと同じ固定17² filtered periodic D2Q9、\(\omega=3/2\)、
  \(\eta=1/100\)、固定保存量葉、
  \(\|a\|_1\le10^{-19}\)、\(\|z\|_*\le10^{-20}\)。
- input state upperはQ007qのexact \(x_*\)を変更せず再利用する。新しいradius、sample、rounding parameterは
  導入しない。
- stage順序は`equilibrium evaluation -> BGK collision -> periodic streaming -> five-point filter`とする。

### exact stage majorant

各full-map sampling時刻ではQ007pのforward invarianceにより
\(\|\delta f\|_{\mathrm W}\le x_*<1\)である。D2Q9のmoment map \(M\)、rest-equilibrium tangent \(E\)、
BGK collision linearization \(C=(1-\omega)I+\omega EM\)について、population-summed Fourier--Wiener
\(\ell^1\)誘導normをentrywise exactに評価し、

\[
\|EM\|_1=\frac{13}{6},
\qquad
\|C\|_1=\frac{19}{6}
\]

を再構成する。equilibriumの非線形部分は

\[
N_i(\delta f)
=w_i\left[
\frac92\frac{(c_i\cdot j)^2}{1+\delta\rho}
-\frac32\frac{|j|^2}{1+\delta\rho}
\right]
\]

である。D2Q9 weight sum、weighted absolute velocity quadratic、cyclic Fourier convolutionをexactに
監査し、

\[
\|N(\delta f)\|_{\mathrm W}
\le 7\frac{x_*^2}{1-x_*}
\]

を用いる。従ってequilibrium evaluationとpost-collision perturbationの登録upperを

\[
e_*=\frac{13}{6}x_*+7\frac{x_*^2}{1-x_*},
\qquad
c_*=\frac{19}{6}x_*+\frac{21}{2}\frac{x_*^2}{1-x_*}
\]

と固定し、lowerを

\[
p_{\mathrm{eq}}=\frac1{36}-e_*,
\qquad
p_{\mathrm{coll}}=\frac1{36}-c_*
\]

とする。

periodic streamingは各population componentのsite置換なので\(p_{\mathrm{stream}}=p_{\mathrm{coll}}\)とする。
登録filterは

\[
(\mathcal F_\eta f)_i(x)
=\frac{99}{100}f_i(x)
+\frac1{400}\sum_{y\sim x}f_i(y)
\]

という5点凸結合なので、\(p_{\mathrm{filter}}=p_{\mathrm{coll}}\)とする。full-map outputではQ007qの
\(p_*=1/36-x_*\)も独立に再利用する。

### validity gate

1. Q007q artifact／runner SHA、source、scope、全validity／hypothesis gate、
   3 theorem-consequence flagが一致する。
2. exact \(M,E,C\)が実装したD2Q9 weight／velocity／\(\omega=3/2\)から再構成され、
   \(\|EM\|_1=13/6\)、\(\|C\|_1=19/6\)である。
3. weight sum \(1\)、weighted absolute velocity quadratic \(8/9\)、equilibrium nonlinear constant \(7\)、
   collision nonlinear constant \(21/2\)をexactに再構成し、\(1-x_*>0\)である。
4. streamingが9個のpopulation-wise periodic permutation、filter coefficientが
   \(99/100,1/400,1/400,1/400,1/400\)で全てnonnegativeかつsum \(1\)である。
5. Q007qの\(x_*\)、base／normal radius、forward-invariance flagをexactに再利用する。
6. 全boundがfinite rationalでstrict JSONを生成する。

一つでも落ちれば`inconclusive`とし、stagewise positivity値を解釈しない。

### hypothesis gate

validity通過時だけ次を判定する。

1. equilibrium evaluation: \(p_{\mathrm{eq}}>0\)。
2. post-collision: \(p_{\mathrm{coll}}>0\)。
3. post-streaming: streaming permutationが同じstrict lowerを保つ。
4. post-filter: five-point convex filterが同じstrict lowerを保つ。
5. all-iterate stagewise positivity: Q007pのtube forward invarianceにより、同じ4 stage boundを
   全one-step \(n=0,1,2,\ldots\)へ適用できる。

全て通れば
`registered Q007p tube is population-positive at every exact BGK, streaming, and filter stage`
として`accepted`とする。一つでも落ちれば
`registered Q007p tube did not certify exact stagewise population positivity`
という有効な`not_certified`とする。

### 主張境界

acceptedなら、固定17²・固定保存量葉・登録Q007p tubeのreal stateについて、exact mathematical mapの
equilibrium evaluation、BGK collision後、periodic streaming後、five-point filter後で全populationが
strict positiveであると主張する。

これはIEEE-754演算の全中間加算・除算に対するroundoff enclosureではなく、entropy、monotonicity、
maximum principle、より大きいtube、global basin、grid-uniform性、continuum limitも認証しない。
Q007c1の有限振幅性能棄却とQ007dのEuclidean棄却も変更しない。

### Q007r 封印結果

判定は`accepted`である。

- Q007q artifact／runner SHA、source／scope／全sealed gate／3 theorem flag／transitive Q007p input: pass
- equilibrium projector／collision linear induced \(\ell^1\) norm:
  `13/6 / 19/6`
- exact projector／collision column-sum pattern:
  `[1,(5/3)*4,(13/6)*4] / [1,2*4,(19/6)*4]`
- D2Q9 weight sum／weighted absolute velocity quadratic:
  `1 / 8/9`
- equilibrium／collision nonlinear majorant constant:
  `7 / 21/2`
- density denominator lower: exact \(1-x_*>0\)
- equilibrium nonlinear remainder upper:
  `6.622072515589128e-37`
- collision nonlinear remainder upper:
  `9.933108773383692e-37`
- equilibrium deviation upper \(e_*\):
  `6.66407763755105e-19`
- post-collision deviation upper \(c_*\):
  `9.73980577795923e-19`
- equilibrium／collision／streaming／filter population lower:
  exact \(1/36-e_*>0\)、\(1/36-c_*>0\)、\(1/36-c_*>0\)、\(1/36-c_*>0\)
- streaming permutation replay: `9 / 9`
- filter coefficient: \(99/100\)と4個の\(1/400\)、sum `1`、全nonnegative
- filter basis replay／wrapped composition replay: pass
- validity／hypothesis gate: `6 / 6`、`5 / 5` passed
- runner SHA-256:
  `0f990cb4c046f9c7aedd4f68d6255ed014e1bdb694401505c5e4cc65ead028d6`
- artifact newline-normalized SHA-256:
  `f88710066712720552594e96aad24d8ca216fd8ffa2dc7eb2877a3287647ba67`

従って固定17²・固定保存量葉・登録Q007p tubeの全real stateについて、exact equilibrium evaluation、
BGK collision後、periodic streaming後、five-point filter後の全9 populationはstrict positiveである。
Q007pのforward invarianceにより、この結論は初回だけでなく全one-step iterateへ適用される。

\(e_*,c_*\)は機械精度より小さいため、保存artifactのpopulation lowerは浮動小数表示では全て
`0.027777777777777776`へ丸められる。判定は16進分子・分母から復元したexact rational差で行い、
各formula、operator norm、convex coefficientを独立テストで再構成した。

これはexact mathematical mapに対する結果であり、NumPy／IEEE-754の全中間加算・除算を外向き区間で
囲ってはいない。entropy、monotonicity、maximum principle、より大きいtube、global basin、
grid-uniform性、continuum limitも認証せず、Q007c1とQ007dの既存棄却も変更しない。

## Q007s: exact-manifold finite tube の登録格子拡大 — 事前登録

### 問い

Q007pで認証した\(r=10^{-19}\)、\(\zeta=10^{-20}\)のtubeを、同じ固定17² map、固定保存量葉、
exact theorem manifold、external-coordinate norm、analytic majorantのまま、有限事前登録格子上で
base／normal両方向にstrictに拡大できるか。

### 固定入力

- `q007p_finite_tube_attraction.json` newline-normalized SHA-256:
  `a5e766938cfee0174deba9c529be9aec2cce4bff9225a3a4a1da83f7d255a751`
- Q007p runner SHA-256:
  `23ff283acb3f872fd2ff489f17d94b8e022e3f45a5c65b5523bf976c534a9f2a`
- map／葉／norm: Q007pと同じ固定17² filtered periodic D2Q9、\(\omega=3/2\)、
  \(\eta=1/100\)、固定保存量葉、固定Fourier external-coordinate block-sum \(\ell^1\) norm。
- Q007o analytic radius \(\rho=10^{-18}\)、correction radius \(\tau\)、Q007nの
  \(c_V,h_2,h_3,h_4,g_2,g_3,g_4\)、Q007pの
  \(q_0,K_s,K_a,K_L\)、selected spectral radius／minimum modulus、
  nonlinear derivative constant \(21/2\)を変更せずexactに再利用する。
- Q007pのcontrol candidate \((r,\zeta)=(10^{-19},10^{-20})\)を候補格子に含める。

### 事前登録候補格子

base radiusは

\[
\mathcal R=\{m\,10^{-19}:m=1,\ldots,9\}
\]

の9点とする。normal radiusは

\[
\mathcal Z
=\{m\,10^{-e}:e=10,\ldots,20,\ m=1,\ldots,9\}
\]

の99点とする。全\(9\times99=891\) candidateを`Fraction`で評価し、途中で単調性を仮定して
枝刈りしない。

passing candidateの選択は結果を見る前に次の辞書式規則へ固定する。

1. passing candidateのうちbase radius \(r\)を最大化する。
2. そのbase radiusでnormal radius \(\zeta\)を最大化する。

これはvolume最大化でもEuclidean radius最大化でもない。base analytic domainを優先してから、
同じbase slice内でnormal thicknessを最大化する有限登録規則である。

### exact candidate majorant

Q007pと同じ式を各candidateへ適用する。

\[
\begin{aligned}
w(r)&=c_Vr+\tau+\sum_{n=2}^4h_nr^n,\\
r_R(r)&=\lambda_sr+\tau/c_V+\sum_{n=2}^4g_nr^n,\\
x(r,\zeta)&=w(r)+K_s\zeta,\\
dN(x)&=\frac{21}{2}\frac{x(2-x)}{(1-x)^2},\\
a_*(r,\zeta)&=r_R(r)+K_LdN(x)K_s\zeta,\\
dH(a_*)&=\frac{\tau}{\rho-a_*}+\sum_{n=2}^4nh_na_*^{n-1},\\
dG(r)&=\frac{\tau}{c_V(\rho-r)}+\sum_{n=2}^4ng_nr^{n-1},\\
q_*(r,\zeta)&=q_0+K_aK_sdN(x)\left(1+K_LdH(a_*)\right),\\
m_T(r)&=\lambda_{\min}-dG(r),\\
\Gamma_*(r,\zeta)&=q_*(r,\zeta)/m_T(r).
\end{aligned}
\]

分母がnonpositiveなcandidateは対応するdomain gateをfailとし、その先の商を評価しない。

### validity gate

1. Q007p artifact／runner SHA、source、scope、全6 validity gate、全4 hypothesis gate、
   4 theorem-consequence flagが一致する。
2. Q007pから抽出した\(\rho,\tau,c_V,h_n,g_n,q_0,K_s,K_a,K_L,\lambda_s,\lambda_{\min}\)、
   nonlinear constantが保存recordとexactに一致する。
3. control candidate \((10^{-19},10^{-20})\)の\(w,r_R,x,a_*,dN,dH,dG,q_*,m_T,\Gamma_*\)と
   全strict marginをQ007p artifactからexactに再現する。
4. \(\mathcal R,\mathcal Z\)が重複なく`9 / 99`点、Cartesian productが`891`点で、
   全candidateを欠落なく評価する。
5. candidateのpass/fail、最大選択、slice boundaryをfloat比較なしのexact rational signで決め、
   canonical digestを保存する。
6. 全保存値がfiniteでstrict JSONを生成する。

一つでも落ちれば`inconclusive`とし、larger-tube結果を解釈しない。

### candidate gate

validity通過時、各candidateは次を全て満たす場合だけpassとする。

1. analytic base domain: \(0<r<\rho\)。
2. population-Wiener domain: \(x(r,\zeta)<1\)。
3. base forward invariance: \(a_*(r,\zeta)<r\)。
4. normal contraction: \(q_*(r,\zeta)<0.99\)かつ\(q_*\zeta<\zeta\)。
5. tangent invertibility: \(m_T(r)>0\)。
6. strict normal domination: \(\Gamma_*(r,\zeta)<0.999\)。

### hypothesis gate

1. Q007p control candidateがpassする。
2. passing candidateが少なくとも一つ存在する。
3. 辞書式selected candidateがQ007pより
   \(r>10^{-19}\)、\(\zeta>10^{-20}\)を同時に満たす。
4. selected base sliceでselectedより大きい全登録\(\zeta\)がfailし、selectedより大きい全登録base sliceに
   passing candidateがない、またはselectedが対応する登録上端にある。
5. selected candidateの6 candidate gateが全てstrictに通る。

全て通れば
`registered exact-manifold tube enlarged on the fixed rational candidate grid`
として`accepted`とする。3または5が落ちれば
`registered rational grid did not enlarge both finite-tube radii`
という有効な`not_certified`とする。

### 主張境界

acceptedなら、辞書式selected \((r_*,\zeta_*)\)について、固定17²・固定保存量葉・同じexact manifold・
同じexternal-coordinate normで、tubeのforward invariance、uniform one-step normal contraction、
strict normal dominationを主張する。

これは連続最適化、最大可能tube、Euclidean／grid-uniform attraction、global basin、continuum limitを
意味しない。Q007q／Q007rのpositivity certificateは旧tubeだけに封印されたままで、新tubeへは自動拡張しない。
Q007c1の有限振幅性能棄却とQ007dのEuclidean棄却も変更しない。

### Q007s 封印結果

全6 validity gateと全5 hypothesis gateが通過した。

- Q007p artifact／runner SHA、source／scope、全upstream／sealed gate、4 theorem flag: pass
- Q007p majorant constant reuse、control candidateの12 field／8 strict margin exact replay: pass
- registered base／normal／Cartesian candidate count: `9 / 99 / 891`
- passing candidate count: `676`
- canonical candidate digest:
  `91fcc70355acfc4b7163c951227188960ef275408b06a678d45d5e4ec4c85300`
- lexicographic selected base／normal radius:
  `9e-19 / 5e-12`
- Q007p controlからのbase／normal improvement factor:
  `9 / 500000000`
- selected tube-state Wiener upper \(x_*\): `1.44413385700551e-11`
- selected base-image modal upper \(a_*\): `8.9950210818665e-19`
- base forward-invariance margin \(r-a_*\): `4.97891813350137e-22`
- normal contraction \(q_*\): `0.9817098620375503`
- tangent conorm lower \(m_T\): `0.9837709569923394`
- domination ratio \(\Gamma_*\): `0.9979049036362179`
- domination-cap margin \(0.999-\Gamma_*\): `0.001095096363782186`
- selected base sliceのfirst larger normal candidate:
  `6e-12`、`base_forward_invariance`だけでfail
- runner SHA-256:
  `6c8633f7e99874ac3be7dd14d3caa253b0dc8c499bb2f6edbb392fa695975b1e`
- artifact newline-normalized SHA-256:
  `7b70fd20df8fb7db5e5460a08d3f86fe8b81a55b56864c860a2c24e9cab63292`

従って
`registered exact-manifold tube enlarged on the fixed rational candidate grid`
として`accepted`とした。固定17²・固定保存量葉・Q007o exact graph-gauge manifold・Q007p
external-coordinate normについて、辞書式selected tubeのforward invariance、一様one-step normal contraction、
strict normal dominationが成立する。

これは9×99有限格子上の辞書式最大であり、連続最適化、最大可能tube、Euclidean／grid-uniform attraction、
global basin、continuum limitを意味しない。Q007q／Q007rのpopulation／stagewise positivity certificateは旧Q007p
tubeだけに封印されたままで、新tubeへは自動拡張しない。次は新tubeのpositivityを別gateとして事前登録する。

## Q007t: enlarged registered tube の full-map population positivity — 事前登録

### 問い

Q007sで認証した拡大tube全体が、rest equilibriumを中心とするphysical D2Q9 populationのstrict positive
coneに含まれ、full one-step mapの入力／出力時刻で全iterateにわたり正値性を保つことを、
Fourier--Wiener normから厳密に認証できるか。

### 固定入力

- `q007s_finite_tube_enlargement.json` newline-normalized SHA-256:
  `7b70fd20df8fb7db5e5460a08d3f86fe8b81a55b56864c860a2c24e9cab63292`
- Q007s runner SHA-256:
  `6c8633f7e99874ac3be7dd14d3caa253b0dc8c499bb2f6edbb392fa695975b1e`
- map／葉／tube: Q007sと同じ固定17² filtered periodic D2Q9、\(\omega=3/2\)、
  \(\eta=1/100\)、固定保存量葉、
  \(\|a\|_1\le9\times10^{-19}\)、\(\|z\|_*\le5\times10^{-12}\)。
- Q007s selected candidateのexact tube-state Wiener upper \(x_*\)を変更せず再利用する。追加のradius、
  rounding、sampling parameterは導入しない。

### exact positivity bound

rest equilibrium \(f_i^*=w_i\)とD2Q9 weights

\[
w_0=\frac49,\qquad
w_{1,\ldots,4}=\frac19,\qquad
w_{5,\ldots,8}=\frac1{36}
\]

をexact `Fraction`で再構成する。Q007sのFourier-population Wiener normでは、real state
\(\delta f=f-f^*\)に対し、

\[
\max_{x,i}|\delta f_i(x)|
\le \max_i\sum_k|\widehat{\delta f}_{k,i}|
\le\|\delta f\|_{\mathrm W}
\le x_*.
\]

従って全populationとdensityに対する登録lowerを

\[
p_*=\frac1{36}-x_*,
\qquad
d_*=1-x_*
\]

と固定する。Q007sのselected-tube forward invarianceと組み合わせ、full-map sampling時刻
\(n=0,1,2,\ldots\)の全iteratesへ同じlowerを適用する。

### validity gate

1. Q007s artifact／runner SHA、source、scope、全6 validity gate、全5 hypothesis gate、
   4 theorem-consequence flag、canonical candidate digestが一致する。
2. exact D2Q9 weight tableが`1 + 4 + 4` population、sum `1`、minimum `1/36`を再現し、
   全weightがstrict positiveである。
3. 17² Fourier index count `289`、phase modulus `1`、Q007sのWiener block-sum norm definitionから、
   \(\|\delta f\|_{\infty,\mathrm{population}}\le\|\delta f\|_{\mathrm W}\)のtriangle-inequality
   auditを通す。
4. Q007s selected candidateの\(x_*\)、base／normal radius、全6 candidate gate、
   forward-invariance theorem flagをexactに再利用する。
5. 全boundがfinite rationalで、strict JSONを生成する。

一つでも落ちれば`inconclusive`とし、positivity値を解釈しない。

### hypothesis gate

validity通過時だけ次を判定する。

1. density positivity: \(d_*=1-x_*>0\)。
2. population positivity: \(p_*=1/36-x_*>0\)。
3. forward positivity: Q007sのselected tubeがforward invariantで、同じ\(p_*\)が全full-map iterateへ
   適用される。

全て通れば
`registered Q007s larger tube lies in the strictly positive population cone at every full-map iterate`
として`accepted`とする。一つでも落ちれば
`registered Q007s larger tube did not certify strict population positivity`
という有効な`not_certified`とする。

### 主張境界

acceptedなら、固定17²・固定保存量葉・登録Q007s selected tubeのreal stateについて、full one-step mapの
入力／出力時刻で全9 populationとdensityがstrict positiveであると主張する。

これはequilibrium evaluation、BGK collision直後、streaming直後、filter直後などのstagewise positivityを
認証しない。Q007rのstagewise certificateは旧Q007p tubeだけに封印されたままである。entropy、
monotonicity、maximum principle、IEEE-754 roundoff enclosure、連続最適tube、global basin、
grid-uniform性、continuum limit、Q007c1の有限振幅性能、Q007dのEuclidean判定も変更・認証しない。

### Q007t 封印結果

全5 validity gateと全3 hypothesis gateが通過した。

- Q007s artifact／runner SHA、source／scope、全sealed gate、4 theorem flag、candidate digest: pass
- transitive Q007p artifact／norm definition／real conjugacy constraint: pass
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
として`accepted`とした。Q007sのforward invarianceにより、固定17²・固定保存量葉・selected tube内の
全real stateについて、full one-step mapの入力／出力時刻 \(n=0,1,2,\ldots\) で全9 populationとdensityに
同じstrict lowerを適用できる。

これはfull-map sampling時刻だけの結論である。equilibrium evaluation、BGK collision、streaming、filterの
stagewise positivityは未認証であり、Q007rのstagewise certificateは旧Q007p tubeだけに封印されたままである。
entropy、monotonicity、maximum principle、IEEE-754 roundoff enclosure、連続最適tube、global basin、
grid-uniform性、continuum limit、Q007c1／Q007dの既存判定も変更しない。次は拡大tubeのexact stagewise
positivityを別gateとして事前登録する。

## Q007u: enlarged registered tube の exact stagewise positivity — 事前登録

### 問い

Q007tでfull-map sampling時刻のstrict positivityを認証したQ007s selected tubeについて、exact mathematical
mapのequilibrium evaluation、BGK collision output、periodic streaming output、five-point filter outputでも、
全populationがstrict positiveであることを認証できるか。

### 固定入力

- `q007t_larger_tube_population_positivity.json` newline-normalized SHA-256:
  `2089d97aa19248cc17689f3e7a01e113540e5afc329ffa5cb3a4c511a43a8529`
- Q007t runner SHA-256:
  `1e00281c71b5ea5d06fedcebd9bd483a73e6ec111388df20e8255ae3aefed877`
- map／葉／tube: Q007s／Q007tと同じ固定17² filtered periodic D2Q9、\(\omega=3/2\)、
  \(\eta=1/100\)、固定保存量葉、
  \(\|a\|_1\le9\times10^{-19}\)、\(\|z\|_*\le5\times10^{-12}\)。
- input state upperはQ007tのexact \(x_*\)を変更せず再利用する。追加のradius、sample、rounding
  parameterは導入しない。

### exact stage bounds

D2Q9 moment map \(M\)、rest-equilibrium tangent \(E\)、BGK collision linearization

\[
C=(1-\omega)I+\omega EM
\]

をexact `Fraction`で再構成し、population-summed Fourier--Wiener \(\ell^1\) induced normを

\[
\|EM\|_1=\frac{13}{6},\qquad
\|C\|_1=\frac{19}{6}
\]

と固定する。Q007rと同じD2Q9 convolution majorantを再構成し、

\[
\|N_{\mathrm{eq}}\|_{\mathrm W}
\le 7\frac{x_*^2}{1-x_*},
\qquad
\|N_{\mathrm{coll}}\|_{\mathrm W}
\le \frac{21}{2}\frac{x_*^2}{1-x_*}
\]

を使う。従って

\[
e_*=\frac{13}{6}x_*+7\frac{x_*^2}{1-x_*},
\qquad
c_*=\frac{19}{6}x_*+\frac{21}{2}\frac{x_*^2}{1-x_*}
\]

とし、equilibrium／post-collision population lowerを

\[
p_{\mathrm{eq}}=\frac1{36}-e_*,
\qquad
p_{\mathrm{coll}}=\frac1{36}-c_*
\]

と固定する。periodic streamingはpopulation-wise permutationなので
\(p_{\mathrm{stream}}=p_{\mathrm{coll}}\)とする。登録filterは

\[
(1-\eta)f(x)+\frac{\eta}{4}
\left[f(x+e_x)+f(x-e_x)+f(x+e_y)+f(x-e_y)\right]
\]

というexact 5点凸結合なので、\(p_{\mathrm{filter}}=p_{\mathrm{coll}}\)とする。

### validity gate

1. Q007t artifact／runner SHA、source、scope、全5 validity gate、全3 hypothesis gate、
   3 theorem-consequence flag、transitive Q007s inputが一致する。
2. exact \(M,E,EM,C\)が登録mapと一致し、全column sumからinduced norm \(13/6,19/6\)を再現する。
3. D2Q9 weight sum、velocity quadratic、cyclic convolutionからnonlinear constant \(7,21/2\)を再現し、
   \(1-x_*>0\)である。
4. 17² periodic streamingが全9 populationでbijectionとなり、filter coefficientが
   \(99/100\)と4個の\(1/400\)からなるnonnegative sum-one convex combinationで、実装compositionを再現する。
5. Q007tの\(x_*,p_*\)、base／normal radiusと、transitive Q007s forward-invariance flagをexactに再利用する。
6. 全boundがfinite rationalで、strict JSONを生成する。

一つでも落ちれば`inconclusive`とし、stage lowerを解釈しない。

### hypothesis gate

validity通過時だけ次を判定する。

1. equilibrium positivity: \(p_{\mathrm{eq}}>0\)。
2. collision positivity: \(p_{\mathrm{coll}}>0\)。
3. streaming positivity: 9 population-wise permutationが\(p_{\mathrm{coll}}\)を保持する。
4. filter positivity: nonnegative sum-one 5点filterが\(p_{\mathrm{coll}}\)を保持する。
5. all-iterate stagewise positivity: Q007sのtube forward invarianceにより同じ4 stage boundを
   全one-step iterateへ再適用できる。

全て通れば
`registered Q007s larger tube is population-positive at every exact BGK, streaming, and filter stage`
として`accepted`とする。一つでも落ちれば
`registered Q007s larger tube did not certify exact stagewise population positivity`
という有効な`not_certified`とする。

### 主張境界

acceptedなら、固定17²・固定保存量葉・登録Q007s selected tubeの全real stateについて、exact mathematical
mapのequilibrium evaluation、BGK collision output、periodic streaming output、five-point filter outputで
全9 populationがstrict positiveであり、Q007s forward invarianceにより全iterateへ適用できると主張する。

これはNumPy／IEEE-754の全中間加算・除算を外向きroundoff intervalで囲った結果ではない。entropy、
monotonicity、maximum principle、連続最適tube、global basin、grid-uniform性、continuum limit、
Q007c1の有限振幅性能、Q007dのEuclidean判定も変更・認証しない。

### Q007u 封印結果

全6 validity gateと全5 hypothesis gateが通過した。

- Q007t artifact／runner SHA、source／scope、全5 validity gate、全3 hypothesis gate、
  3 theorem flag、transitive Q007s input／tube reuse: pass
- exact equilibrium projector／collision induced \(\ell^1\) norm:
  `13/6 / 19/6`
- exact equilibrium／collision nonlinear constant:
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
- periodic streaming bijections／filter coefficients／wrapped composition: pass
- runner SHA-256:
  `56fc99f1f381e97e70710c7da0cee8d1262d0c10190cf617316f822d1eb29014`
- artifact newline-normalized SHA-256:
  `b568fc304fd939121dd52543f316cb571ae6f4be4f4f664c68fe1c749b566c55`

従って
`registered Q007s larger tube is population-positive at every exact BGK, streaming, and filter stage`
として`accepted`とした。固定17²・固定保存量葉・Q007s selected tube内の全real stateについて、
exact equilibrium evaluation、BGK collision output、periodic streaming output、five-point filter outputで
全9 populationがstrict positiveである。Q007s forward invarianceにより同じ4 stage boundを全iterateへ
帰納的に再適用できる。

これはexact mathematical mapの結論であり、NumPy／IEEE-754の全中間演算を外向きroundoff intervalで
囲っていない。entropy、monotonicity、maximum principle、連続最適tube、global basin、grid-uniform性、
continuum limit、Q007c1／Q007dの既存判定も変更しない。

## Q007v: enlarged tube の binary64 stage-roundoff enclosure — 事前登録

### 問い

Q007uのexact stagewise positivityを、現行NumPy実装のIEEE-754 binary64演算へ拡張できるか。また、
一段のpositivityとは別に、roundoff perturbationを含む出力がQ007s selected tubeのstrict
forward-invariance marginへ再び入ることを認証し、同じ主張を全iterateへ帰納できるか。

### 固定入力

- `q007u_larger_tube_stagewise_positivity.json` newline-normalized SHA-256:
  `b568fc304fd939121dd52543f316cb571ae6f4be4f4f664c68fe1c749b566c55`
- Q007u runner SHA-256:
  `56fc99f1f381e97e70710c7da0cee8d1262d0c10190cf617316f822d1eb29014`
- `q007s_finite_tube_enlargement.json` newline-normalized SHA-256:
  `7b70fd20df8fb7db5e5460a08d3f86fe8b81a55b56864c860a2c24e9cab63292`
- Q007s runner SHA-256:
  `6c8633f7e99874ac3be7dd14d3caa253b0dc8c499bb2f6edbb392fa695975b1e`
- current D2Q9 implementation source SHA-256:
  `6e6c5aa6734844d0393eb402e21203831faaf5f325b35249941eaa59145c6f53`
- current checkerboard-filter implementation source SHA-256:
  `5fb6b67e8527b0b1f5f45511ba7cd5d077ee443220632ba3019b7bf28010a7ea`
- map／葉／tubeはQ007uと同じ固定17²、\(\omega=3/2\)、\(\eta=1/100\)、固定保存量葉、
  \(r=9\times10^{-19}\)、\(\zeta=5\times10^{-12}\)とする。
- 入力対象は、Q007s exact tube内のreal stateを各populationでround-to-nearest ties-to-evenにより
  binary64へ正しく丸めた配列とする。任意の既に摂動したbinary64配列は対象に含めない。

### binary64 enclosure

unit roundoffとsubnormal用absolute fallbackを

\[
u=2^{-53},\qquad h=2^{-1075}
\]

に固定する。有限なexact scalar result \(y\)をbinary64へ丸める各演算について

\[
|\operatorname{fl}(y)-y|\le u|y|+h
\]

を用いる。全intermediate magnitudeがoverflow threshold未満で、density denominatorがstrict positiveで
あることを別gateで確認する。D2Q9 weight、`0.01`、`1.0-0.01`、
`0.25*0.01`は`Fraction.from_float`で実際のdyadic valueを固定し、対応するexact rational
\(4/9,1/9,1/36,1/100,99/100,1/400\)との差を直接含める。

各quantityを、exact target interval \(X=[\underline x,\overline x]\)とabsolute forward-error upper
\(\epsilon_X\)のpairとして伝播する。加減算、乗除算はinput error、constant representation error、
上記rounding errorを全て含める。長さ\(n\)のreductionは演算順に依存しない

\[
\gamma_{n-1}=\frac{(n-1)u}{1-(n-1)u}
\]

とterm absolute sumを用いる。density／momentumは最大8 additions、`einsum`の2成分dotと
speed-squareは最大1 addition、4-neighbour sumは最大3 additionsと固定する。FMAはseparate
multiply-add enclosureを改善する側なので許すが、演算の省略・precision変更・非IEEE rounding modeは
対象外とする。

Q007uのpopulation-summed Fourier--Wiener upper \(x_*\)から、各exact input populationを
\([w_i-x_*,w_i+x_*]\)で囲む。このcomponent boxはQ007s tubeより広いが、相関を仮定しない安全な
one-step enclosureとして固定する。現行sourceの順でmacroscopic reduction、velocity division、
equilibrium polynomial、BGK update、streaming permutation、five-point filterを伝播し、各stageの
binary64 lowerを

\[
\underline p_{\mathrm{fl},s}
=\min_i\{\underline X_{s,i}-\epsilon_{s,i}\}
\]

とする。

### roundoff-robust tube re-entry

post-filter component error upperを\(\epsilon_i\)とし、normalized 17² DFTのtriangle inequalityから

\[
\epsilon_{\mathrm W}
=289\sum_{i=0}^{8}\epsilon_i
\]

を登録Wiener error upperとする。Q007sがexactに固定したselected analysis upper
\(K_a\)、full external analysis upper \(K_z\)を用い、

\[
\epsilon_a=K_a\epsilon_{\mathrm W},\qquad
\epsilon_z=K_z\epsilon_{\mathrm W}
\]

とする。Q007s selected candidateのstrict margin
\(m_a\)（base forward invariance）と\(m_z\)（normal-tube forward invariance）に対し、

\[
\epsilon_a<m_a,\qquad \epsilon_z<m_z
\]

の両方をroundoff-robust re-entryの必要な登録sufficient gateとする。失敗後にDFT係数、operation count、
analysis norm、marginを調整しない。

### validity gate

1. Q007u／Q007s artifact・runner SHA、source、scope、全sealed gate／theorem flag、selected tubeが一致する。
2. D2Q9／filter source SHA、対象関数、stage order、shape、binary64 dtypeが固定入力と一致する。
3. \(u,h\)、binary64 exponent／mantissa、全実装定数のdyadic valueとexact-rational差を再現する。
4. paired intervalのadd／subtract／multiply／divide／reduction boundがexact `Fraction`で構成され、
   全denominatorが正、全intermediateがfinite range内にある。
5. density／momentum、equilibrium polynomial、BGK、streaming、filterのoperation scheduleとreduction countを
   source auditおよびdeterministic implementation replayで再現する。
6. Q007uの\(x_*\)とexact stage lower、Q007sの\(K_a,K_z,m_a,m_z\)、base／normal radiusをexactに再利用する。
7. 全boundがfinite rationalでstrict JSONを生成する。

一つでも落ちれば`inconclusive`とし、stage lowerおよびre-entry比を解釈しない。

### hypothesis gateと停止規則

validity通過時だけ次を判定する。

1. binary64 equilibrium lower \(>0\)。
2. binary64 post-collision lower \(>0\)。
3. streamingが算術を行わず、post-collision lowerを保つ。
4. binary64 post-filter lower \(>0\)。
5. 上の4 stageが全てstrict positiveで、one-step binary64 stage positivityが成立する。
6. \(\epsilon_a<m_a\)かつ\(\epsilon_z<m_z\)で、Q007s tubeへのroundoff-robust re-entryが成立する。

全て通れば
`binary64 stage positivity and roundoff-robust Q007s tube invariance certified`
として`accepted`とする。1--5が通り6だけが落ちた場合は
`binary64 one-step stages remain positive, but the registered Q007s tube is not certified roundoff-invariant`
という有効な`not_certified`とする。1--5のいずれかが落ちた場合は
`binary64 stage positivity is not certified on the registered Q007s input tube`
とする。

### 主張境界

one-step positivityが通れば、Q007s exact tube内のreal stateを正しくbinary64へ丸めた入力に対して、
現行source・binary64 round-to-nearest modelの一段内部stageがpositiveであると主張する。re-entry gateが
落ちた場合、その結論を全iterateへ帰納しない。これは実際のtrajectoryがtubeを脱出する反例ではなく、
登録したworst-case enclosureがQ007sのstrict marginへ収まらないという`not certified`判定である。
nonstandard rounding、FTZ／DAZ、GPU kernel、BLAS変更、compiler fast-math、entropy、monotonicity、
maximum principle、連続最適tube、grid-uniform性、continuum limitは扱わない。

### Q007v 封印結果

全7 validity gateが通過した。6 hypothesis gateのうちone-step positivityに関する5 gateは通過し、
roundoff-robust Q007s tube re-entryだけが失敗した。

- Q007u／Q007s artifact・runner SHA、source／scope、全sealed gate／theorem flag、
  selected-tube reuse: pass
- D2Q9／filter source SHA、required operation snippets、stage order: pass
- binary64 \(u/h\): `2^-53 / 2^-1075`
- registered operation count:
  input rounding `9`、exact sign/zero product `36`、add/subtract/multiply/divide
  `36 / 18 / 83 / 2`、reduction `22 calls / 61 additions`
- equilibrium lower／maximum component error:
  `0.027777777759726004 / 7.154770604839416e-16`
- post-collision lower／maximum component error:
  `0.02777777771459676 / 1.2459169501537343e-15`
- post-streaming lower:
  `0.02777777771459676`
- post-filter lower／maximum component error:
  `0.027777777714596753 / 1.3501237168549712e-15`
- registered Wiener roundoff upper:
  `1.1666869562204168e-12`
- selected/base coordinate error upper／strict margin／utilization:
  `1.7624955618306674e-12 / 4.978918133501365e-22 / 3.539916734062091e9`
- external/normal coordinate error upper／strict margin／utilization:
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
入力に対し、現行source・round-to-nearest modelの一段内部stageは全てstrict positiveである。一方、
post-filter roundoffをQ007s analysis normで座標へ戻したworst-case upperはbase／normal両marginを超える。
従って、この一段positivityを同じtube上で全iterateへ帰納しない。

これは実際のtrajectoryがtubeを脱出する反例ではない。登録したcomponent-box、normalized-DFT
triangle bound、analysis normからなるworst-case enclosureではroundoff-robust re-entryを示せないという
判定である。次に進める場合は、同じgateを後付けで緩めず、roundoff-robust tube enlargementまたは
higher-precision mapを別途事前登録する。

## Q007w: roundoff-robust re-entry の ideal binary precision threshold — 事前登録

### 問い

Q007vと同じexact tube、component box、operation schedule、DFT triangle bound、analysis norm、
strict re-entry marginを一切変更せず、仮数precisionだけを増やした理想的な二進round-to-nearest演算では、
何bitからQ007s tubeへのroundoff-robust re-entryを認証できるか。

### 固定入力

- `q007v_binary64_stage_enclosure.json` newline-normalized SHA-256:
  `c4c1c45941a6f6ac302691efd8e795e431f6acc1fa4f4629cb0c7a0afac3c0a5`
- Q007v runner SHA-256:
  `a0d3cea0fcae8a627f4a96db56d46727589411b2557e2aa91433569576a0575c`
- precision candidateはtotal significand bit数
  \[
  p=53,54,\ldots,128
  \]
  の76個とし、全候補を昇順に評価する。候補の追加、間引き、adaptive refinementは行わない。
- exponent rangeはbinary64と同じminimum normal exponent \(-1022\)とし、
  \[
  u_p=2^{-p},\qquad h_p=2^{-1022-p}
  \]
  を用いる。
- Q007vのfixed 17² map、\(x_*\)、base／normal radius、operation count、source SHA、
  \(K_a,K_z,m_a,m_z\)、normalized DFT coefficient `289`をbitwise／exactに再利用する。

### ideal p-bit constant rounding

有限nonzero rational \(c\)に対し、\(2^e\le |c|<2^{e+1}\)となる整数\(e\)と

\[
\Delta_{p,c}=2^{e-p+1}
\]

をexact integer arithmeticで求め、\(c/\Delta_{p,c}\)をnearest integer ties-to-evenへ丸めて
\(\widehat c_p\)を得る。D2Q9 weightと\(\eta=1/100\)はこの規則で一度丸める。filter係数は実装順を保ち、

\[
\widehat\eta_p=\operatorname{RN}_p(1/100),\quad
\widehat c_{0,p}=\operatorname{RN}_p(1-\widehat\eta_p),\quad
\widehat c_{1,p}=\operatorname{RN}_p(\widehat\eta_p/4)
\]

とする。\(3,9/2,3/2,1/4\)はexact binary constantである。

各\(p\)でQ007vと同じpaired interval演算を再実行し、全stage lower、post-filter component error sum、
\(\epsilon_{\mathrm W},\epsilon_a,\epsilon_z\)、base／normal margin utilizationをexact `Fraction`で保存する。
candidate passは

\[
\min_s\underline p_{\mathrm{fl},s}>0,\qquad
\epsilon_a<m_a,\qquad
\epsilon_z<m_z
\]

の全成立とする。passing candidateがあれば最小の\(p\)を\(p_*\)とし、\(p_*-1\)が少なくとも一方の
re-entry gateでfailすることを境界確認する。

### validity gate

1. Q007v artifact／runner SHA、source／scope、全7 validity gate、6 hypothesis gateのうちre-entryだけfail、
   6 theorem flagのうちall-iterate robust flagだけfalseというmixed outcomeが一致する。
2. Q007vの\(x_*,K_a,K_z,m_a,m_z\)、source SHA、operation count、DFT coefficientをexactに再利用する。
3. exact ties-to-even routineがknown halfway caseを通り、\(p=53\)で全weight／filter dyadicとQ007vの
   全stage lower、component error、Wiener／coordinate error、margin utilizationをexactに再現する。
4. `53..128`の76候補を欠落・重複なく評価し、canonical candidate digestを保存する。
5. precision増加に対しcomponent／Wiener／coordinate error upperとmargin utilizationがnonincreasingで、
   選択境界が最初のpassと一致する。
6. 全候補でdensity divisorが正、全intermediateがfinite range内、全one-step stage lowerが正である。
7. 全boundがfinite rationalでstrict JSONを生成する。

一つでも落ちれば`inconclusive`とし、precision thresholdを解釈しない。

### hypothesis gateと停止規則

validity通過時だけ次を判定する。

1. \(p=53\) controlがQ007vのone-step pass／robust re-entry failをexactに再現する。
2. 登録範囲に少なくとも一つpassing candidateがある。
3. selected \(p_*\)がpassing setの最小値である。
4. selected \(p_*\)で全one-step stage lowerがstrict positiveである。
5. selected \(p_*\)でbase／normal re-entryがともにstrict passする。
6. \(p_*>53\)かつ\(p_*-1\)が少なくとも一方のre-entry gateでfailする。

全て通れば
`registered ideal binary precision threshold restores roundoff-robust Q007s tube re-entry`
として`accepted`とする。passing candidateが無ければ
`registered ideal precision ladder does not certify roundoff-robust Q007s tube re-entry`
という有効な`not_certified`とする。

### 主張境界

acceptedなら、固定operation scheduleと固定worst-case enclosureに対するideal \(p_*\)-bit arithmeticの
sufficient thresholdを主張する。これは実装済みのNumPy dtype、MPFR／decimal backend、実測trajectory、
性能、正しいrounding modeを認証しない。\(p_*\)未満で実際のtrajectoryが必ずtubeを脱出するという
necessary thresholdでもない。Q007vのbinary64 `not_certified`、Q007uのexact-map acceptance、Q007sの
finite-grid tube selectionは変更しない。

### Q007w 封印結果

全7 validity gateと全6 hypothesis gateが通過した。

- Q007v artifact／runner SHA、source／scope、mixed outcome、transitive inputs: pass
- ties-to-even halfway case: `4 / 4` pass
- \(p=53\) weight／filter dyadic、全population target/error、stage summary、re-entry quantity:
  exact Q007v reproduction
- candidate coverage: `53..128 / 76 candidates / no missing or duplicate`
- passing precision: `85..128 / 44 candidates`
- error／utilization monotonic nonincrease、stage lower monotonic nondecrease: pass
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
として`accepted`とした。固定Q007v worst-case enclosureでは、84 bitsはnormal marginを通るが
base marginを通らず、85 bitsで初めてbase／normal両方をstrictに通る。従って85 significand bitsを
最小の登録sufficient thresholdとする。

これはideal arithmetic familyの設計値であり、lower precisionが実際に必ずtubeを脱出するという
necessary thresholdではない。具体的なNumPy／MPFR／decimal／hardware backend、rounding mode、
trajectory、performanceも認証しない。Q007vのbinary64 `not_certified`はそのまま保持する。次に実装mapの
roundoff-robust claimへ進む場合は、85 bits以上の一つのconcrete correctly-rounded backendを別gateとして
事前登録し、Q007wとbitwise／interval cross-checkする。

## Q007x: concrete MPFR-85 backend と fixed-leaf closure — 事前登録

### 問い

Q007wで選んだideal \(p_*=85\) binary round-to-nearest演算を、固定した
`gmpy2`／MPFR backendがoperation-by-operationで実現するか。さらに、componentwise
correct roundingと一段mapが

\[
\delta M=\delta P_x=\delta P_y=0
\]

というQ006以降の保存量固定葉をexactに保ち、Q007wのbase／normal re-entry boundを
all-iterate inductionへ接続できるか。

MPFRは基本演算をexact resultからdestination precisionへ正しく丸め、nearest modeではties-to-evenを
用いる。`gmpy2` contextはprecisionをbinary bit数で指定できる
（[MPFR manual](https://www.mpfr.org/mpfr-current/mpfr.html)、
[gmpy2 contexts](https://gmpy2.readthedocs.io/en/stable/contexts.html)）。

### 固定入力とbackend

- `q007w_ideal_precision_threshold.json` newline-normalized SHA-256:
  `bac362d9dca4a681387b986a5f5802278ef61a1a3bcf1a0f8577c7f3ab0a07af`
- Q007w runner SHA-256:
  `86dcc0a507e24216775650d5467d0ebf6e90eac0865190d0d5186e08afb7eac8`
- backend package: `gmpy2==2.3.1`
- runtime libraries: `MPFR 4.2.2`、`GMP 6.3.0`
- grid／model: \(17^2\)、D2Q9、\(\omega=3/2\)、\(\eta=1/100\)
- context:
  - precision: `85` total significand bits
  - rounding: `RoundToNearest`
  - exponent range: `emin=-1105`、`emax=1024`
  - `subnormalize=True`
  - invalid／division-by-zero／overflow／underflow trap: enabled
  - inexact trap: disabled
- \(-1105=-1022-(85-1)+1\)により、smallest positive subnormalを
  \(2^{-1106}\)、half-ulp fallbackをQ007wと同じ\(2^{-1107}\)にする。
- exact rationalはPython `Fraction`から`mpq(n,d)`を作り、そこから`mpfr`へ
  一度だけ丸める。Python `float`やdecimal stringを経由しない。
- weightは各exact D2Q9 rationalを個別に丸める。filterはQ007wと同じ順序で
  \[
  \widehat\eta=\operatorname{RN}_{85}(1/100),\quad
  \widehat c_0=\operatorname{RN}_{85}(1-\widehat\eta),\quad
  \widehat c_1=\operatorname{RN}_{85}(\widehat\eta/4)
  \]
  とする。FMA、fast-math、並列reductionは使わない。

### concrete map と独立oracle

`research/q007x_mpfr_backend.py`に、density／momentum、velocity、second-order equilibrium、
BGK collision、periodic streaming、five-point filterを明示loopで実装する。reductionは先頭要素からの
left foldに固定し、各加減乗除を個別MPFR operationとして実行する。

この配置は既存artifactが固定する`src/ttim_lbm` package fingerprintを変更せず、Q007x自身が
backend source SHAを独立に封印するためである。

全primitive operationについて、operandとresultをexact dyadic ratioへ戻し、Q007wの
exact integer ties-to-even oracleで

\[
\widehat r_{\rm MPFR}
=\operatorname{RN}_{85}(r_{\rm exact})
\]

を照合する。constant construction、input encoding、全map operationのcanonical trace digestと
mismatch countを保存する。sourceを実装コミットで固定した後、そのSHAをQ007x runnerへ登録する。

また同じprobeをexact `Fraction` mapで一段進め、equilibrium／post-collision／
post-streaming／post-filterのobserved component errorが、Q007w selected 85-bit candidateの
registered maximum-component error upper以下であることを検証する。

### fixed-leaf probes

\(\delta=10^{-13}\)とし、全probeをexact rationalで作る。

1. `rest`: 全siteをexact D2Q9 rest weightsとする。
2. `axial_x_pair`: population \(q=1\)の二siteへ \(+\delta,-\delta\)を加える。
3. `axial_y_pair`: population \(q=2\)の二siteへ \(+\delta,-\delta\)を加える。
4. `all_populations_paired`: 各\(q=0,\ldots,8\)について異なる二siteへ
   \((-1)^q(q+1)\delta/10\)とその負を加える。

各populationのpaired perturbationはglobal mass／momentumをexactに相殺する。全component deviationが
Q007wの登録\(x_*\)未満、全density／populationがpositiveであることをgateにする。これらは
backend semanticと保存収支を診断するfinite probeであり、Q007s tube全体のsampling proofとは呼ばない。

各probeについて、exact input、componentwise MPFR encoding、post-collision、post-streaming、
post-filterのglobal \(M,P_x,P_y\)をexact rational summationで測る。成功条件はtoleranceではなく
bitwise／rational equalityである。

### validity gate

1. Q007w artifact／runner SHA、全7 validity gate、全6 hypothesis gate、selected \(p_*=85\)、
   \(p=84\) boundary、Q007v transitive inputsが一致する。
2. backend package／MPFR／GMP version、85-bit context、rounding、exponent range、subnormal設定、
   trap、context restorationが登録値と一致する。
3. backend source SHA、`pyproject.toml` dependency、D2Q9／filter upstream source SHA、
   stage order、constant construction orderが一致する。
4. 4 exact probesが固定recipe、fixed-leaf cancellation、component box、positivityを満たす。
5. constant／input／mapの全trace operationがQ007w ties-to-even oracleとbitwise一致し、
   mismatch countが0である。
6. 各probeのper-site operation countがQ007wの
   `9 / 36 / 36 / 18 / 83 / 2 / 22 / 61` recordと一致し、全intermediateがfinite、
   divisorがpositive、invalid／division-by-zero／overflow／underflow flagがfalseである。
7. exact `Fraction` stageとの差が全probe／全stageでQ007w selected 85-bit
   component-error upper以下で、MPFR stage populationがstrict positiveである。
8. 全値がfiniteでstrict JSONを生成し、probe／trace／result digestが再現する。

一つでも落ちれば`inconclusive`とし、conservation hypothesisを解釈しない。

### hypothesis gateと停止規則

validity通過時だけ次を判定する。

1. registered MPFR backendがQ007w ideal 85-bit operation semanticsを実現する。
2. Q007w one-step stage positivityとbase／normal roundoff boundがconcrete backendへ適用できる。
3. componentwise correct input encodingが全4 probeで\(M,P_x,P_y\)をexactに保存する。
4. collisionがencoded inputの\(M,P_x,P_y\)を全probeでexactに保存する。
5. streaming／filter後もencoded inputの\(M,P_x,P_y\)を全probeでexactに保存する。
6. 1--5が全て通り、Q007s fixed leaf上のone-step re-entryを同じbackendへ反復適用できる。

全て通れば
`registered MPFR-85 backend closes the Q007w roundoff-robust fixed-leaf induction`
として`accepted`とする。

validityと1--2が通るが3--6のいずれかが落ちれば、
`MPFR-85 realizes the Q007w one-step arithmetic bound but not the fixed conservation leaf`
という有効な`not_certified`とする。丸めweightの和やfilter partition-of-unity defect、
operation roundoffを保存量別に分解し、Q007wの閾値を変更せず次の保存補正gateへ渡す。

### 主張境界

finite probeのexact conservation成功だけでtube全体の保存を証明しない。acceptedには、
backend sourceの代数構造と全trace semantic bridgeを併用する。`not_certified`の場合も、
Q007wのideal complement-coordinate error threshold、Q007uのexact-map positivity、Q007sの
exact fixed-leaf invarianceを撤回しない。ただしconcrete all-iterate claimは行わない。
性能、multi-step trajectory、GPU、threaded reduction、他のgmpy2／MPFR版、D3Q27を扱わない。

### Q007x 封印結果

全8 validity gateが通過した。6 hypothesis gateのうち、MPFR semantic bridgeとQ007w一段boundの
2件は通過し、encoding／collision／streaming-filter exact conservationとfixed-leaf inductionの
4件は失敗した。

- package／runtime:
  `gmpy2 2.3.1 / MPFR 4.2.2 / GMP 6.3.0`
- context:
  `p=85 / RoundToNearest / emin=-1105 / emax=1024 / subnormalize`、dangerous flagなし
- backend source SHA-256:
  `25ad43629e2487c5c062920cbb5319dac4e8fbded339dc856548bfab7f18a0dc`
- probe count／trace count:
  `4 / 70,824 per probe / 283,296 total`
- trace mismatch:
  `0`
- all operation count／domain／stage bound／positivity gates: pass
- maximum observed Q007w component-bound utilization:
  `0.15250294804773457`
- exact conservation summary:
  - componentwise encoding: fail
  - collision: fail
  - periodic streaming: pass
  - five-point filter: fail
  - full step: fail
- rounded-weight sum defect:
  `1/154742504910672534362390528 = 6.462348535570529e-27`
- rounded-filter partition defect:
  `5/618970019642690137449562112 = 8.077935669463161e-27`
- rest 17² encoding mass defect:
  `1.8676187267798828e-24`
- rest filter mass defect:
  `8.404284270509473e-24`
- probe digest:
  `a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329`
- aggregate trace digest:
  `49ce9b304b4b6a07fdf7d7baed6c9118a97c5a08e489e3aa5eacde28662c2351`
- result digest:
  `12cb83a87895d50523c909ad314b9ad155ac507af73e05f1b28cfb2a65328c7d`
- runner SHA-256:
  `de16e86ab365e6e64b15fd62ebdb442a54e05d4e4e529ae1e018299983d7491b`
- artifact newline-normalized SHA-256:
  `20ba483c4c627de015673a2f8873cc020a5c1a43ee48c7715121a00330e13566`

従って
`MPFR-85 realizes the Q007w one-step arithmetic bound but not the fixed conservation leaf`
として有効な`not_certified`とした。Q007wの85-bit paired enclosureはconcrete backendの
全registered primitive operationと4 probeのexact Fraction stage errorを覆う。しかしQ007sの
all-iterate theoremを適用する保存量固定葉は、componentwise correct encodingだけでもexactには維持されず、
非一様collisionとfilterでも追加driftが生じる。streamingだけはexact permutationとして保存した。

これはQ007wのideal sufficient thresholdやQ007s／Q007uのexact-map theoremを棄却しない。Q007wが測った
selected／external座標誤差だけでは、roundoffで生成される3中心保存方向を閉じられないことを示す。
次は85-bit semantic bridgeを固定したまま、conservation-exact encodingとpost-stage repairを別gateとして
事前登録し、そのrepair errorがQ007w strict marginに収まるかを評価する。

## Q007y: distributed dyadic conservation repair と repair-aware error budget — 事前登録

### 問い

Q007xで固定した85-bit MPFR backendの演算順序とQ007wの誤差上界を変更せず、
componentwise encoding直後とpost-filter直後に決定論的な保存量補正を加える。この補正は

\[
M=17^2,\qquad P_x=P_y=0
\]

をexact dyadic equalityで回復し、fixed-leaf mapを定義できるか。さらに、その補正を含む
worst-case Wiener誤差がQ007wのbase／normal strict marginの両方へ収まるか。

有限な4 probeで補正が成功することと、Q007s tube全体で既存のre-entry予算が閉じることを
別の仮説とする。前者だけの成功をall-iterate certificateへ昇格しない。

### 封印する入力

- Q007w artifact newline-normalized SHA-256:
  `bac362d9dca4a681387b986a5f5802278ef61a1a3bcf1a0f8577c7f3ab0a07af`
- Q007w runner SHA-256:
  `86dcc0a507e24216775650d5467d0ebf6e90eac0865190d0d5186e08afb7eac8`
- Q007x artifact newline-normalized SHA-256:
  `20ba483c4c627de015673a2f8873cc020a5c1a43ee48c7715121a00330e13566`
- Q007x runner SHA-256:
  `de16e86ab365e6e64b15fd62ebdb442a54e05d4e4e529ae1e018299983d7491b`
- Q007x backend source SHA-256:
  `25ad43629e2487c5c062920cbb5319dac4e8fbded339dc856548bfab7f18a0dc`
- backend／grid／probe:
  `gmpy2 2.3.1 / MPFR 4.2.2 / p=85 / RoundToNearest / 17^2 / D2Q9 / Q007xの4 exact probes`

Q007w／Q007xのrunner、backend、artifactは変更しない。Q007yはそれらをread-only inputとして
importし、観測SHAとartifact内SHAを再検証する。

### 補正格子と整数solver

Q007wの登録boxでは、対角population \(q=5,6,7,8\) は同じbinade
\([2^{-6},2^{-5})\) にある。85-bit MPFR格子幅を

\[
h=2^{-90}
\]

と固定する。raw stateの保存量とtargetとの差を \((d_M,d_x,d_y)\) とし、加えるべき補正を

\[
(m,x,y)=(-d_M/h,-d_x/h,-d_y/h)\in\mathbb Z^3
\]

とする。D2Q9の全populationはこのbox内で \(h\) の整数倍であり、rest／axial速度の
より粗い格子幅により \(m\equiv x\equiv y\pmod 2\) が成立することを検証する。

対角4 populationへ加える総unit数を \((a,b,c,d)\) とし、自由整数 \(t\) を用いて

\[
\begin{aligned}
a&=(m+x+y+t)/4, & b&=(m-x+y-t)/4,\\
c&=(m-x-y+t)/4, & d&=(m+x-y-t)/4
\end{aligned}
\]

とする。compatibleな \(t\) を

\[
|t|\le |m|+|x|+|y|+4
\]

の範囲で全探索し、

\[
\left(\sum_i|a_i|,\ \max_i|a_i|,\ |t|,\ t\right)
\]

を辞書式最小化する。探索区間は全breakpointとabsolute valueが最小のcompatible residueを
含む。従ってsolverのrepair \(\ell^1\) は、\(|t|\le2\) のcompatible候補との比較から

\[
h\sum_i|a_i|
\le |d_M|+|d_x|+|d_y|+2h
\]

を満たす。

各 \(a_i\) はPythonの `divmod(a_i,289)` で商 \(s\) と非負剰余 \(r\) に分け、
row-major順 \((y,x)=(0,0),(0,1),\ldots,(16,16)\) の先頭 \(r\) siteへ
\((s+1)h\)、残りへ \(sh\) を加える。これは総和をexactに保ち、site間のunit差を高々1にする。
MPFR addition後の値が同じbinadeに残り、exact rational sumとbitwise一致することをgateにする。

### repaired map

初期化は

\[
E_{\rm leaf}=\mathcal C\circ E_{85},
\]

一段mapは

\[
\widehat\Phi_{\rm leaf}
=\mathcal C\circ\widehat\Phi_{85}
\]

とする。\(\mathcal C\) は上記のglobal repairである。map入力が既に85-bit fixed-leaf stateなら
Q007x backendの `evaluate_encoded_stages` を用い、再encodingしない。collision内部の保存誤差は
許すが、periodic streaming後のpost-filter出力をtarget leafへ戻す。Q007wのstage orderや
primitive operationを変更せず、repair operationを別に数える。

### finite probe audit

Q007xと同じ4 exact probeについて次を保存する。

1. raw encoding defect、整数unit triple、選択した \(t\)、対角4総unit、site配分digest。
2. repaired encodingの \(M,P_x,P_y\) とexact input targetのbitwise equality。
3. repaired encodingから実行したraw MPFR stagesのQ007w bound／positivity。
4. raw post-filter defectとpost-filter repairの全整数記録。
5. repaired post-filterの \(M,P_x,P_y\) と一段targetのbitwise equality。
6. 全repair additionのexactness、same-binade、strict positivity、dangerous context flag。
7. exact Fraction stageに対するraw／repaired maximum component errorとQ007w bound utilization。

Q007x probe recipeとdigestが一致しなければ`inconclusive`とする。

### tube-wide repair-aware bound

Q007wの85-bit post-filter population別component boundを \(e_q\)、site数を \(N=289\) として

\[
\begin{aligned}
B_M &=N\sum_q e_q,\\
B_x &=N\sum_q |c_{qx}|e_q,\\
B_y &=N\sum_q |c_{qy}|e_q
\end{aligned}
\]

をexact rationalで計算する。fixed leaf上ではexact mapが保存量を保つため、raw backendの
global defectはそれぞれこの値以下である。repairのphysical \(\ell^1\)、従ってnormalized-DFT
Wiener \(\ell^1\) への追加上界を

\[
B_C=B_M+B_x+B_y+2h
\]

とし、総誤差を

\[
B_{\rm repaired}=B_M+B_C
\]

で評価する。Q007w artifactに封印されたselected／external analysis normを掛け、同じ
base／normal marginとstrict比較する。このtriangle boundはcenter誤差の相殺やrepair配置の
Fourier phaseを利用しない。ここでbase gateが落ちても、有限補正の実装失敗とは区別する。

### validity gate

1. Q007w／Q007x artifact・runner SHA、source、scope、upstream gateが全て一致する。
2. Q007x backend SHAとMPFR contextが一致し、Q007yが封印済みsourceを変更していない。
3. Q007xの4 probe recipe、fixed-leaf target、probe digestが一致する。
4. 登録boxのbinade／\(h\)-lattice／parity条件と、全probeの整数化が成立する。
5. solverが整数Hadamard方程式、登録objective、repair \(\ell^1\) bound、balanced distributionを満たす。
6. 全repair additionがexact、same-binade、finiteで、dangerous MPFR flagを立てない。
7. backend operation/domain、Q007w stage enclosure、strict positivityが全probeで通る。
8. exact rationalでtube-wide boundを再計算し、全値finiteなstrict JSONとdigestを再現する。

一つでも失敗すれば`inconclusive`とし、保存補正仮説を解釈しない。

### hypothesis gateと停止規則

validity通過時だけ次を判定する。

1. repaired encodingが全4 probeでtarget \(M,P_x,P_y\) をexactに満たす。
2. repaired post-filterが全4 probeで同じtargetをexactに満たす。
3. 全finite repairがexact representable、strict positiveで、登録stage boundを破らない。
4. lattice／binade／worst-case correction boundにより、repair mapがQ007w tube全体で定義できる。
5. repair-aware normal-coordinate error upperがQ007w normal margin未満である。
6. repair-aware base-coordinate error upperがQ007w base margin未満である。
7. 1--6が全て通り、repaired MPFR-85 mapのfixed-leaf re-entryをall-iterateへ帰納できる。

全て通れば
`distributed MPFR-85 repair closes the Q007w fixed-leaf tube induction`
として`accepted`とする。

1--5が通るが6--7が落ちた場合は
`distributed MPFR-85 repair restores the registered fixed-leaf probes but not the Q007w tube-wide base budget`
として有効な`not_certified`とする。この場合、次はcenter cancellationとspatial phaseを保つ
projector-aware repair normを別ゲートとして事前登録する。有限probe自体が失敗した場合は、
integer solver／binade／配分を原因別に記録し、tube budgetを成功扱いしない。

### 主張境界

本ゲートは保存量固定葉の案Aだけを扱う。中心3座標を縮約座標へ含めない。有限4 probeの成功だけで
tube-wide sampling、multi-step trajectory、性能、並列reduction、他のMPFR build、D3Q27を主張しない。
また、粗いWiener triangle boundの失敗は、より鋭いprojector-aware boundや別の保存補正の
不存在を意味しない。Q007w／Q007xおよびQ007s／Q007uの既存結論は変更しない。

### Q007y 封印結果

全8 validity gateが通過した。7 hypothesis gateのうち、finite input／post-filter repair、
exact addition・positivity・stage enclosure、tube-wide repair定義、normal budgetの5件は通過した。
base budgetと、それに依存するall-iterate inductionの2件は失敗した。

- repair quantum／diagonal populations:
  `2^-90 / q=5,6,7,8`
- finite repaired conservation:
  `input 4/4 exact / post-filter 4/4 exact`
- finite MPFR additions:
  `9,248 / 9,248 exact, same-binade, positive`
- maximum finite Q007w component-bound utilization:
  `0.15776531320758136`
- post-filter raw Wiener error upper:
  `2.706739822688458e-22`
- mass／x-momentum／y-momentum defect upper:
  `2.706739822688458e-22 / 1.1263608552978353e-22 / 1.1263608552978353e-22`
- repair Wiener addition upper:
  `4.959477689155467e-22`
- repaired total Wiener error upper:
  `7.666217511843926e-22`
- repaired／raw error factor:
  `2.832269820536163`
- base error／margin／utilization:
  `1.158123373936201e-21 / 4.978918133501365e-22 / 2.326054260951996` (`fail`)
- normal error／margin／utilization:
  `2.2935127396475674e-20 / 9.145068981224883e-14 / 2.507922842743146e-7` (`pass`)
- finite campaign digest:
  `f47bb30b0e2280d339a40b196d1ca3dcb84f94b9e8de087bbff215d07a220fe6`
- runner SHA-256:
  `ba757030c852b68d5a4c643ec150422c0a7b4c3ba125211d2715ba1445e89811`
- artifact newline-normalized SHA-256:
  `a3afa87c4ee3f5d45e667eac9a6a89a1726f1d4bad0a9f90a624c562fb598648`

従って
`distributed MPFR-85 repair restores the registered fixed-leaf probes but not the Q007w tube-wide base budget`
として有効な`not_certified`とした。整数Hadamard solverとbalanced row-major distributionは、
Q007w登録box全体でrepairをexactに定義できる。4 probeでは入力と一段出力の保存量をexactに戻し、
backend stage boundとpositivityも維持した。しかし、center cancellationとspatial phaseを捨てた
Wiener triangle boundでは、repair追加分がraw boundの1.832倍となり、base marginを2.326倍使用する。

これはrepair実装の失敗でも、projector-aware certificateの不存在でもない。次はbackendとrepairを
固定し、raw errorとrepairがglobal conserved centerでexactに相殺すること、およびbalanced配置の
非零Fourier係数を直接使うselected-projector boundをQ007zとして事前登録する。

## Q007z: balanced repair の selected-wave Fourier certificate — 事前登録

### 問い

Q007yのbackend、integer solver、row-major balanced distributionを一切変更せず、補正の一様成分が
selected非零波数でexactに消えることを使えば、Q007yで失敗したbase re-entry budgetを閉じられるか。
normal側はQ007yの保守的なfull-Wiener boundをそのまま再利用し、base側だけをselected wave setと
per-orbit left-operator normで再評価する。

### 封印する入力

- Q007p artifact newline-normalized SHA-256:
  `a5e766938cfee0174deba9c529be9aec2cce4bff9225a3a4a1da83f7d255a751`
- Q007p runner SHA-256:
  `23ff283acb3f872fd2ff489f17d94b8e022e3f45a5c65b5523bf976c534a9f2a`
- Q007y artifact newline-normalized SHA-256:
  `a3afa87c4ee3f5d45e667eac9a6a89a1726f1d4bad0a9f90a624c562fb598648`
- Q007y runner SHA-256:
  `ba757030c852b68d5a4c643ec150422c0a7b4c3ba125211d2715ba1445e89811`
- Q007y backend source SHA-256:
  `25ad43629e2487c5c062920cbb5319dac4e8fbded339dc856548bfab7f18a0dc`
- grid／repair:
  \(17^2\)、\(N=289\)、\(h=2^{-90}\)、populations \(5,6,7,8\)、
  Python `divmod(total,289)`、row-major prefix distribution

Q007pが封印するselected orbitsを

\[
\begin{aligned}
K_{\rm axis}&=\{(-1,0),(0,-1),(1,0),(0,1)\},\\
K_{\rm diag}&=\{(-1,-1),(1,-1),(1,1),(-1,1)\}
\end{aligned}
\]

とする。各orbitのexact rational left-operator upperをQ007p artifactから読み、
観測floatがそれぞれ

\[
L_{\rm axis}=1.5106842091904618,\qquad
L_{\rm diag}=1.4732828143196361
\]

であることを固定する。Q007pのselected waveがこの8点だけで、\(k=0\)を含まないこと、
Q007w／Q007yのglobal selected-analysis upperが
\(\max(L_{\rm axis},L_{\rm diag})=L_{\rm axis}\)とexactに一致することをgateにする。

### exact balanced-prefix Fourier lemma

一つの対角populationへ加える総unitを

\[
n=Ns+r,\qquad 0\le r<N
\]

とする。Q007y実装は先頭\(r\) row-major siteへ\(s+1\)、残りへ\(s\)を置く。
normalized DFTを

\[
\widehat c(k)=\frac{h}{N}\sum_{j=0}^{N-1}c_j\chi_k(j)
\]

とする。任意の非零離散波数では\(\sum_j\chi_k(j)=0\)なので、一様な\(s\)成分はexactに消え、

\[
\widehat c(k)=\frac{h}{N}\sum_{j<r}\chi_k(j)
=-\frac{h}{N}\sum_{j\ge r}\chi_k(j)
\]

となる。従ってtriangle inequalityから

\[
|\widehat c(k)|
\le \frac{h}{N}\min(r,N-r)
\le \frac{144}{289}h.
\]

これはtotal unitの大きさや符号に依存しない。4対角populationのpopulation
\(\ell^1\) Fourier normは各selected waveで

\[
B_{\rm wave}=4\frac{144}{289}h
\]

以下である。

この補題をコード表現と結び付けるため、8 selected wavesと全\(r=0,\ldots,288\)の
2,312組をexact integer phase histogramで全走査する。各非零characterについてfull 17² gridの
17 phase residueが各17回現れること、prefix／complement countが\(r,N-r\)であること、
最大\(\min(r,N-r)=144\)であることを検証する。complex floatの実測値は証明に使わない。

### selected-projector repair bound

Q007pの各orbitは4波数を持つため、repairがbase座標へ加える上界を

\[
B_{\rm repair}^{\rm sel}
=4\left(L_{\rm axis}+L_{\rm diag}\right)B_{\rm wave}
\]

とする。raw MPFR mapのbase errorはQ007wの登録値

\[
B_{\rm raw}^{\rm sel}
=L_{\rm axis} B_M
\]

を変更せず、総base errorを

\[
B_{\rm repaired}^{\rm sel}
=B_{\rm raw}^{\rm sel}+B_{\rm repair}^{\rm sel}
\]

とする。raw errorの波数相関やcenter cancellationを用いて\(B_{\rm raw}^{\rm sel}\)を小さくしない。
repairのconstant quotientがselected非零波数でゼロであることだけを用いる。

normal errorはQ007yの

\[
B_{\rm repaired}^{\rm ext}
=2.2935127396475674\times10^{-20}
\]

をそのまま用いる。これはrepairのzero-wave kinetic成分を含むfull-Wiener triangle boundなので、
baseと同じphase改善をnormal側へ流用しない。

### fixed leaf と帰納

Q007yにより、各sampling timeのrepair後状態は

\[
M=289,\qquad P_x=P_y=0
\]

をexactに満たし、登録tube全体でrepair additionはsame-binade、exact、positiveである。
Q007wのraw one-step stage enclosure、Q007s exact-map margin、Q007u exact stage positivityを
変更しない。base／normalの両strict marginが通れば、`already encoded, repaired MPFR-85 state`が
Q007s tube内にあることを初期条件として、repaired one-step mapのtube re-entry、fixed leaf、
stage positivityを全iterateへ帰納する。

任意のexact boundary stateをcomponentwise encodingしただけで初期tube membershipが自動的に
保たれるとは主張しない。Q007yのinput repairは別に記録するが、本帰納の初期条件はrepair済みMPFR state
が登録tube内にあることとする。

### validity gate

1. Q007p／Q007y artifact・runner SHA、source、scope、upstream validityと判定が一致する。
2. Q007pのselected 2 orbit／8 waves、C4 member、left-operator norm、global maximumが再現する。
3. Q007y source、\(h\)、対角population、`divmod`、row-major prefix recipe、finite campaignが
   artifactとfresh replayで一致する。
4. 全2,312 phase-histogram caseで非零character、full-grid cancellation、
   prefix／complement count、144 boundがexact integerで通る。
5. \(B_{\rm wave}\)、\(B_{\rm repair}^{\rm sel}\)、raw／repaired base、Q007y normalを
   exact rationalで再計算し、登録恒等式が通る。
6. 全値finiteなstrict JSONを生成し、selected-input／phase／result digestを再現する。

一つでも失敗すれば`inconclusive`とし、re-entry仮説を解釈しない。

### hypothesis gateと停止規則

validity通過時だけ次を判定する。

1. selected base coordinatesがQ007pの非零8波数だけから成る。
2. balanced repairのselected-wave population normが全tube stateで\(B_{\rm wave}\)以下である。
3. projector-aware repair base contributionが\(B_{\rm repair}^{\rm sel}\)以下である。
4. \(B_{\rm repaired}^{\rm sel}\)がQ007w base margin未満である。
5. Q007yのfull-Wiener normal errorがQ007w normal margin未満である。
6. Q007yのexact fixed-leaf repair、tube-wide well-definedness、stage positivityが維持される。
7. 1--6により、登録tube内から開始するrepaired MPFR-85 mapのall-iterate re-entryが閉じる。

全て通れば
`selected-wave certificate closes the repaired MPFR-85 fixed-leaf tube induction`
として`accepted`とする。

baseが落ちる場合は
`balanced repair phase is insufficient for the Q007w base budget`
として有効な`not_certified`とし、repair配置の整数最適化またはraw errorのwave-resolved enclosureを
次gateへ渡す。normal／fixed-leaf／source gateが落ちた場合はprojector改善を成功扱いしない。

### 主張境界

本ゲートは固定17²、固定保存量葉、封印済み85-bit backend、特定row-major balanced repairに限る。
条件付きall-iterate tube invarianceを認証しても、任意のexact stateの初期encoding、trajectory精度、
shadowing時間、性能、GPU／parallel reduction、他のgrid／MPFR build、center-slow構成、D3Q27を
主張しない。Q007yの粗いtriangle-bound `not_certified`は、その判定法として保存する。

### Q007z 封印結果

全6 validity gateと全7 hypothesis gateが通過した。

- selected wave set:
  `2 C4 orbits / 8 nonzero waves / k=0 excluded`
- axis／diagonal left-operator upper:
  `1.5106842091904618 / 1.4732828143196361`
- exact phase cases／balanced distribution cases:
  `2,312 / 4,624`
- maximum prefix／complement unit bound:
  `144`
- per-population／four-population per-selected-wave upper:
  `4.024992167483374e-28 / 1.6099968669933496e-27`
- repair base-coordinate error upper:
  `1.9216710236250915e-26`
- raw／repaired base-coordinate error upper:
  `4.089029108522444e-22 / 4.0892212756248066e-22`
- base margin／headroom／utilization:
  `4.978918133501365e-22 / 8.896968578765586e-23 / 0.8213071928437413` (`pass`)
- unchanged normal utilization:
  `2.507922842743146e-7` (`pass`)
- phase-aware／Q007y coarse base-error ratio:
  `0.353090298292354`
- selected-input／phase／result digest:
  `ea5d303e4333638447d70ef8ec6692599948260657e7cb51c133b8c3c5d20b90` /
  `f0da04edcc58edd6b96b2869ee67c79cc44b020278545bc52d03a142c0fa4a83` /
  `62262fe2cfb0bf361e5b79aaf89c8ba319ad1df046bf59aff56be8b7a54d4054`
- runner SHA-256:
  `0e2b3aebdc30d6a441178e3ac05fe417ab66673885a52ac9da801bd787dd8f79`
- artifact newline-normalized SHA-256:
  `b1ca382a76e874c18b804c7614ff8ad1ded3a5d0b9dda583facf6641b24f0c53`

従って
`selected-wave certificate closes the repaired MPFR-85 fixed-leaf tube induction`
として`accepted`とした。balanced distributionの大きなuniform quotientはselected非零波数でexactに
消え、剰余prefixだけがbase座標へ寄与する。repair追加base upperはQ007yのphysical-\(\ell^1\)
triangle estimateより十分小さく、base／normalの両marginをstrictに通した。

これにより、`already encoded, repaired MPFR-85 state`が登録Q007s tube内にあることを初期条件として、
fixed leaf、one-step re-entry、MPFR stage positivityを全iterateへ帰納できる。任意のexact boundary
stateの初期encoding、trajectory accuracy、shadowing時間はまだ示していない。次は初期化interiorを
別定義した後、exact mapとのmulti-step shadowingを新しいgateとして扱う。

## Q007aa: exact-state encoding の初期化 interior — 事前登録

### 問い

Q007sの登録tubeより明示的に小さいexact-state tubeを固定すれば、任意のその内部状態を
componentwise MPFR-85へround-to-nearest encodingし、Q007yのbalanced conservation repairを
適用した直後の状態がQ007s tube内に入ることを、Q007zのselected-wave boundとQ007sの
analytic chart majorantだけで認証できるか。

### 封印する入力

- Q007s artifact newline-normalized SHA-256:
  `7b70fd20df8fb7db5e5460a08d3f86fe8b81a55b56864c860a2c24e9cab63292`
- Q007s runner SHA-256:
  `6c8633f7e99874ac3be7dd14d3caa253b0dc8c499bb2f6edbb392fa695975b1e`
- Q007y artifact newline-normalized SHA-256:
  `a3afa87c4ee3f5d45e667eac9a6a89a1726f1d4bad0a9f90a624c562fb598648`
- Q007y runner SHA-256:
  `ba757030c852b68d5a4c643ec150422c0a7b4c3ba125211d2715ba1445e89811`
- Q007z artifact newline-normalized SHA-256:
  `b1ca382a76e874c18b804c7614ff8ad1ded3a5d0b9dda583facf6641b24f0c53`
- Q007z runner SHA-256:
  `0e2b3aebdc30d6a441178e3ac05fe417ab66673885a52ac9da801bd787dd8f79`
- grid／map／leaf:
  \(17^2\)、\(\omega=1.5\)、\(\eta=0.01\)、
  \(M=289,\ P_x=P_y=0\)、MPFR precision 85 bits、\(h=2^{-90}\)

Q007sの外側tubeを

\[
\mathcal T(r,\zeta),\qquad
r=9\times10^{-19},\qquad \zeta=5\times10^{-12}
\]

とし、事前登録する初期化interiorを

\[
\boxed{
r_0=8.9998\times10^{-19},\qquad
\zeta_0=4.999999999\times10^{-12}
}
\]

とする。従って登録した内向き余裕はexact rationalで

\[
\Delta r=2\times10^{-23},\qquad
\Delta\zeta=10^{-21}
\]

である。radiusを結果に合わせて動かさない。

### coordinate perturbation lemma

Q007p／Q007sのgraph gaugeを

\[
W(a)=Va+H(a),\qquad L W(a)=a,\qquad Q=I-VL
\]

と書く。exact初期状態は固定保存量葉上で

\[
x=W(a)+Uz,\qquad \|a\|_1\le r_0,\qquad \|z\|_*\le\zeta_0
\]

を満たすものに限定する。componentwise encodingとrepair後を
\(\tilde x=x+e\)とし、\(\tilde a=L\tilde x=a+\delta a\)と置く。
Q007sのselected／external analysis upperをそれぞれ\(K_L,K_a\)とする。

Q007y input boundのraw encoding Wiener errorを\(E_{\rm raw}\)、repair additionの
physical Wiener boundを\(E_{\rm rep}\)とし、

\[
E_W=E_{\rm raw}+E_{\rm rep}
\]

とする。baseにはQ007zのphase-aware repair upper \(B_{\rm rep}^{\rm sel}\)を使い、

\[
\epsilon_a
=K_L E_{\rm raw}+B_{\rm rep}^{\rm sel}
\]

と評価する。raw encodingのFourier相関による追加改善は使わない。

Q007sのmajorant係数を\(h_2,h_3,h_4,\tau,\rho\)とし、外側base radiusで

\[
d_H(r)
=2h_2r+3h_3r^2+4h_4r^3+\frac{\tau}{\rho-r}
\]

をexact rationalに再計算する。\(\|a\|_1\le r_0\)かつ
\(\|\delta a\|_1\le\epsilon_a<\Delta r\)なら、\(a\)から\(\tilde a\)までの線分は
\(\|\cdot\|_1<r\)にある。graph gaugeから

\[
\tilde x-W(\tilde a)
=Uz+Qe-\bigl(H(\tilde a)-H(a)\bigr)
\]

なので、encoding後のnormal-coordinate増分を

\[
\epsilon_z
=K_a\left(E_W+d_H(r)\epsilon_a\right)
\]

で評価する。\(K_a E_W\)を直接摂動、
\(K_a d_H(r)\epsilon_a\)をchart移動分として別記する。

封印値から期待される概数は

\[
\begin{aligned}
E_{\rm raw}&\simeq7.4704749081\times10^{-24},\\
E_{\rm rep}&\simeq1.2452407101\times10^{-23},\\
\epsilon_a&\simeq1.1304745189\times10^{-23},\\
d_H(r)&\simeq1.0403913490\times10^{-16},\\
\epsilon_z&\simeq5.9603557593\times10^{-22}.
\end{aligned}
\]

これらは診断値であり、判定はartifactのexact rational recordだけで行う。

### validity gate

1. Q007s／Q007y／Q007z artifact・runner SHA、source、scope、upstream validityと
   登録判定が一致する。
2. Q007sの\(r,\zeta,\rho,\tau,h_2,h_3,h_4,K_L,K_a\)をexactに再利用し、
   selected candidateの全gateが通っている。
3. Q007yのtube-wide input encoding bound、repair lattice、fixed-leaf target、
   same-binade positivityがfresh replayとartifactで一致する。
4. Q007zのselected-wave set、phase histogram、\(B_{\rm rep}^{\rm sel}\)、accepted判定が
   fresh replayとartifactで一致する。
5. \(E_W,\epsilon_a,d_H(r),\epsilon_z\)とtight interior radius
   \(r-\epsilon_a,\zeta-\epsilon_z\)をexact rationalで再計算し、全恒等式が通る。
6. 全値finiteなstrict JSONを生成し、input／result digestを再現する。

一つでも失敗すれば`inconclusive`とし、初期化仮説を解釈しない。

### hypothesis gateと停止規則

validity通過時だけ次を判定する。

1. 登録initialization tubeはQ007s tubeのstrict subsetで、解析半径内にある。
2. Q007y input repairは登録initialization tube全体でwell-defined、exact fixed-leaf、positiveである。
3. \(\epsilon_a<\Delta r\)であり、encoding前後のbase線分がQ007s base ball内に留まる。
4. \(\epsilon_z<\Delta\zeta\)であり、direct external errorとgraph移動分の双方を含む。
5. encoding＋repair後に\(\|\tilde a\|_1<r\)、
   \(\|\tilde z\|_*<\zeta\)が成り立つ。
6. Q007zの条件付き帰納を接続し、その後の全sampling timeでfixed leaf、tube membership、
   stage positivityが維持される。

全て通れば
`registered exact-state interior survives MPFR-85 encoding and repair`
として`accepted`とする。

baseまたはnormal余裕が落ちた場合は
`registered initialization interior is too shallow for encoding and repair`
として有効な`not_certified`とし、radiusを事後変更せず、次gateでより内側の候補または
wave-resolved input enclosureを事前登録する。source／scope／upstream gateが落ちた場合は
`inconclusive`とする。

### 主張境界

本ゲートは固定17²、固定保存量葉、Q007sのexact graph-gauge manifold、封印済みMPFR-85 backend、
Q007yのrow-major balanced repair、および上記coordinate interiorに限定する。任意のQ007s boundary
state、固定保存量葉外、任意精度実装、exact軌道とのtrajectory accuracy／shadowing、性能、他grid、
center-slow構成、D3Q27は主張しない。Q007zの条件付き定理を置換せず、その初期条件を一段だけ具体化する。

### Q007aa 封印結果

全6 validity gateと全6 hypothesis gateが通過した。

- registered initial base／normal radii:
  `8.9998e-19 / 4.999999999e-12`
- registered base／normal inward margins:
  `2e-23 / 1e-21`
- raw／repair／total physical Wiener upper:
  `7.470474908090484e-24 / 1.2452407101265335e-23 / 1.992288200935582e-23`
- raw／repair／total base increment:
  `1.1285528478805861e-23 / 1.9216710236250915e-26 / 1.1304745189042113e-23`
- base headroom／utilization:
  `8.69525481095789e-24 / 0.5652372594521056`
- chart derivative \(d_H(r)\):
  `1.0403913489904792e-16`
- direct／graph-shift／total normal increment:
  `5.96035575932445e-22 / 3.5186618281273335e-38 / 5.960355759324451e-22`
- normal headroom／utilization:
  `4.03964424067555e-22 / 0.596035575932445`
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
として`accepted`とした。raw encodingのselected incrementにはQ007sの\(K_L\)を使い、
repair incrementにはQ007zのphase-aware boundを使った。normal側はcombined physical errorに加えて、
base shiftによる\(H(\tilde a)-H(a)\)を外側radiusでの\(d_H(r)\)により明示的に課金した。
後者は小さいが、初期化定理から省略していない。

これにより、上記exact fixed-leaf coordinate interiorからcomponentwise encoding／repairを経て
Q007s tubeへ入り、その後のQ007z all-iterate inductionへ接続できる。任意のQ007s boundary stateや
trajectory accuracyはまだ示していない。次はrepaired MPFR-85 mapとexact mapのmulti-step shadowingを、
本tube-invariance定理を変更せず別gateとして事前登録する。

## Q007ab: fixed-coordinate all-iterate forward shadowing — 事前登録

### 問い

Q007aaのexact initial state \(x_0\)と、そのcomponentwise MPFR-85 encoding／repair
\(\tilde x_0\)から出発する二つの軌道を考える。Q007s tube全体でexact mapが固定線形
eigencoordinate normに関してstrict contractionであることを認証し、Q007zの一段local defectを
幾何級数で蓄積すれば、sampling timeにおけるsame-initial-state forward errorを全iterateで
一様に抑えられるか。

### 封印する入力

- Q007s artifact newline-normalized SHA-256:
  `7b70fd20df8fb7db5e5460a08d3f86fe8b81a55b56864c860a2c24e9cab63292`
- Q007s runner SHA-256:
  `6c8633f7e99874ac3be7dd14d3caa253b0dc8c499bb2f6edbb392fa695975b1e`
- Q007z artifact newline-normalized SHA-256:
  `b1ca382a76e874c18b804c7614ff8ad1ded3a5d0b9dda583facf6641b24f0c53`
- Q007z runner SHA-256:
  `0e2b3aebdc30d6a441178e3ac05fe417ab66673885a52ac9da801bd787dd8f79`
- Q007aa artifact newline-normalized SHA-256:
  `cf6a0566b91e9b034d2c93290302182fe8b4a0bf0f7e7bbbbb232f3d4a12ee64`
- Q007aa runner SHA-256:
  `a7a6334fdb157ec317f65fca2475bf3b03775af88ea6d68eec2c02c5ba74188e`
- grid／map／leaf／backend:
  \(17^2\)、\(\omega=1.5\)、\(\eta=0.01\)、
  \(M=289,\ P_x=P_y=0\)、85-bit MPFR、Q007y row-major balanced repair

Q007aaのinitialization interiorとQ007s／Q007zのtube inductionを変更しない。

### fixed linear coordinate norm

Q007p／Q007sが封印したselected analysis \(L\)、external analysis \(JQ\)を使い、
固定線形座標

\[
\mathcal Cx=(Lx,JQx),\qquad
\|\mathcal Cx\|_\oplus=\|Lx\|_1+\|JQx\|_*
\]

を定義する。これはgraph-relative normal coordinateではなく、平衡点で固定したlinear
eigencoordinateである。selected synthesis upperを\(c_V\)、external synthesis upperを\(K_s\)とし、

\[
K_{\rm syn}=\max(c_V,K_s)
\]

とする。従って固定保存量葉上で

\[
\|x\|_W\le K_{\rm syn}\|\mathcal Cx\|_\oplus
\]

を使う。selected／external linear contraction upperを\(q_s,q_0\)、
selected／external nonlinear analysis upperを\(K_L,K_a\)とする。

Q007s tubeのphysical Wiener radiusを\(R_T\)、そこでのfull-map nonlinear derivative
majorantを\(d_N(R_T)\)とする。tube内の二状態を結ぶ線分はphysical Wiener ball内にあるため、
exact map \(\Phi=A+N\) のfixed-coordinate Lipschitz upperを

\[
\boxed{
L_\oplus
=\max(q_s,q_0)
+(K_L+K_a)d_N(R_T)K_{\rm syn}
}
\]

とする。Q007sのgraph-coordinate normal contraction \(q_*\)を、この全状態Lipschitz定数の代用に
使わない。

### initial errorとone-step local defect

exact initial stateとQ007aa repair後状態のfixed-coordinate誤差を

\[
d_0
=\epsilon_{a,0}+K_aE_{W,0}
\]

で抑える。\(\epsilon_{a,0}\)はQ007aaのphase-aware base increment、
\(E_{W,0}\)はraw encoding＋repair physical Wiener upperである。graph-shift項はQ007aaの
graph-relative membershipには必要だが、\(\mathcal C\)がlinearなので\(d_0\)へ重複加算しない。

各sampling stepで、同じMPFR入力にexact mapを適用した値とrepaired MPFR出力との差を

\[
\epsilon_{\rm step}
=B_{\rm step}^{\rm sel}+B_{\rm step}^{\rm ext}
\]

とする。baseにはQ007zのrepaired selected-wave upper、externalにはQ007y由来でQ007zが
変更せず再利用したfull-Wiener external upperを用いる。

### 誤差再帰と登録accuracy gate

exact軌道 \(x_{n+1}=\Phi(x_n)\) とrepaired MPFR軌道
\(\tilde x_{n+1}=\widetilde\Phi(\tilde x_n)\) に対し、

\[
d_n=\|\mathcal C(\tilde x_n-x_n)\|_\oplus
\]

と置く。Q007s exact invarianceとQ007aa／Q007z repaired invarianceにより両軌道は全時刻で
同じtube内にあるので、

\[
d_{n+1}\le L_\oplus d_n+\epsilon_{\rm step}
\]

を反復する。\(L_\oplus<1\)なら

\[
d_n\le
L_\oplus^nd_0
+\epsilon_{\rm step}\frac{1-L_\oplus^n}{1-L_\oplus}
\le
D_\oplus,
\qquad
D_\oplus=\max\left(d_0,\frac{\epsilon_{\rm step}}{1-L_\oplus}\right).
\]

physical Wiener error upperを

\[
D_W=K_{\rm syn}D_\oplus
\]

とする。accuracy thresholdは結果を見る前に

\[
\boxed{D_W<10^{-6}R_T}
\]

と固定する。これはQ007s tubeのphysical state radiusに対する相対accuracy gateであり、
population componentの相対誤差とは呼ばない。

封印値から期待される診断概数は

\[
\begin{aligned}
L_\oplus&\simeq0.9920954949,\\
d_0&\simeq6.0734\times10^{-22},\\
\epsilon_{\rm step}&\simeq2.3344\times10^{-20},\\
D_\oplus&\simeq2.9533\times10^{-18},\\
D_W&\simeq8.5298\times10^{-18}.
\end{aligned}
\]

判定はartifactのexact rational recordだけで行う。

### validity gate

1. Q007s／Q007z／Q007aa artifact・runner SHA、source、scope、upstream validity／outcomeと
   Q007aa fresh replayが一致する。
2. \(q_s,q_0,c_V,K_s,K_L,K_a,R_T,d_N(R_T)\)と固定保存量葉のcoordinate coverageを
   Q007sからexactに再現する。
3. Q007aaのinitial selected／external errorとQ007zのstep selected／external defectを
   exact rationalで再構成する。
4. linear block、nonlinear mean-value bound、analysis／synthesis normから\(L_\oplus\)の式を
   exactに再現し、graph-relative \(q_*\)と混同しない。
5. \(d_0,\epsilon_{\rm step},D_\oplus,D_W,D_W/R_T\)の恒等式をexactに再現する。
6. 全値finiteなstrict JSONを生成し、input／result digestを再現する。

一つでも失敗すれば`inconclusive`とし、shadowing仮説を解釈しない。

### hypothesis gateと停止規則

validity通過時だけ次を判定する。

1. exact／repaired両軌道が同じQ007s physical Wiener ballに全iterateで留まる。
2. \(L_\oplus<1\)である。
3. \(d_0\)がQ007aa initialization errorをfixed-coordinate normで覆う。
4. \(\epsilon_{\rm step}\)が各repaired MPFR stepのlocal coordinate defectを覆う。
5. 幾何級数による\(D_\oplus\)が全\(n\ge0\)のsame-initial forward errorを覆う。
6. \(D_W<10^{-6}R_T\)を満たす。

全て通れば
`fixed-coordinate contraction certifies all-iterate MPFR-85 forward shadowing`
として`accepted`とする。

\(L_\oplus\ge1\)なら
`registered fixed-coordinate majorant is not contractive`、
contractionは通るがaccuracy gateが落ちるなら
`uniform shadow bound exceeds the registered tube-scale accuracy threshold`
として有効な`not_certified`とする。thresholdやnormを事後変更せず、必要ならblock-weighted
coordinate normを次gateとして事前登録する。

### 主張境界

本ゲートのshadowingは、Q007aaの同じexact initial stateから出発するexact軌道と、そこから
encoding／repairしたrepaired MPFR軌道とのsampling-time forward errorを意味する。古典的な
bi-infinite shadowing lemma、backward error、各intermediate stageのtrajectory distance、componentwise
relative error、任意のQ007s boundary initialization、性能、他grid／MPFR build、center-slow構成、
D3Q27を主張しない。Q007s／Q007z／Q007aaのinvariance定理は変更しない。

### Q007ab 封印結果

全6 validity gateと全6 hypothesis gateが通過し、
`fixed-coordinate contraction certifies all-iterate MPFR-85 forward shadowing`
として`accepted`とした。

- selected／external linear contraction upper:
  `0.9920954673554099 / 0.981709835832552`
- direct-sum synthesis upper:
  `2.888267212368763`
- nonlinear derivative／coordinate Lipschitz increment:
  `3.0326810997772634e-10 / 2.7528235726518938e-8`
- \(L_\oplus\)／contraction gap:
  `0.9920954948836456 / 0.007904505116354432`
- \(d_0\)／\(\epsilon_{\rm step}\):
  `6.073403211214871e-22 / 2.3344049524038155e-20`
- \(D_\oplus\)／\(D_W\):
  `2.9532588290365307e-18 / 8.529800645544777e-18`
- \(R_T\)／\(D_W/R_T\):
  `1.4441338570055092e-11 / 5.90651663221288e-7`
- registered absolute Wiener accuracy threshold:
  `1.4441338570055092e-17`
- input／result digest:
  `83c98750b8a18aa98cae710fad0a4d2fa139428d791a085bdd086e39e435225f` /
  `268a5e2098011561c3bc521c845e6eb804692713502fbbd54c3b3106b8f9c014`
- runner SHA-256:
  `4958e1aa5140bdbd1a32ce074c77ce2739636a34f7da2531c792ec165401c01a`
- artifact newline-normalized SHA-256:
  `3770e53e5fd169ea8ba16a568a1a1a3052afdd95d2779ba630c7ba7113bdc7ae`

固定線形座標を用いるため、Q007aaのgraph-relative membershipで必要だったgraph-shiftを\(d_0\)へ
重複加算しない。Q007s exact tube invarianceとQ007aa／Q007z repaired tube invarianceにより二軌道を
同じphysical Wiener ballへ閉じ込め、\(L_\oplus<1\)の幾何級数で全\(n\ge0\)を覆った。
derived physical boundは事前登録した\(10^{-6}R_T\)の約0.59065倍である。

本結果はQ007aa exact interiorから同じ初期状態をencoding／repairして得る軌道とのsampling-time
forward errorに限る。bi-infinite shadowing、backward error、intermediate-stage距離、componentwise
relative error、任意のQ007s boundary state、性能、他grid／MPFR build、center-slow構成、D3Q27は
認証しない。Q009はQ008cの有効なTT-SVD棄却により保留を維持し、次はsparse baselineを外さずQ010の
cost／break-even判定を独立に事前登録する。

## Q009: TT-cross は residual peak を見つけられるか — Q008cにより保留

### 問い

TT-cross chart は、dense/TT-SVD oracle と比較して independent \(L^\infty\) gate を
通るか。

cross points は validation に使わず、random、domain boundary、high-shear、
adversarial residual search を分けて保存する。

Q008cが登録TT-SVD候補を有効に棄却したため、固定Q007c1係数については開始しない。

## Q010: sealed TT-SVD representation cost and break-even — 事前登録

### 問い

Q008a／Q008cで忠実度を通過しstorage仮説を棄却された固定8 TT-SVD候補について、natural
quartic sparse-fiberを必須baselineとする独立holdout cost campaignを行う。TTに有利なoffline
費用除外を置いても、local homogeneous quartic actionの総時間または格納量に有限break-evenを
持つ候補はあるか。

### 封印する入力

- Q008a artifact newline-normalized SHA-256:
  `97dd1614dc62a1f58bafb74ddb7ee980763247ddc7e91686637a55f3be05d6f3`
- Q008c artifact newline-normalized SHA-256:
  `058dd425504fd0cd003d50e7b7c4a118b0200cb3ac6a15e556468af425a0b73e`
- package source SHA-256:
  `114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2`
- fixed quartic coefficient SHA-256:
  `9597e0d31c32c940c76526754f0ec70c666e5fe03511977e80b3fd0610a7f29b`
- grid／map:
  \(17^2\)、\(\omega=1.5\)、\(\eta=0.01\)、24 complex input modes、9 local outputs、
  degree 4、17,550 natural fibers
- TT-SVD:
  relative discarded Frobenius budget \(10^{-13}\)、maximum rankなし

Q008a／Q008cの`passed / rejected`、全validity pass、全候補fidelity pass、selected
candidateなしを要求する。Q008のtiming値は入力整合と参考診断として記録するが、Q010 hypothesisの
成否には使わない。

### 固定候補とbaseline

natural sparse-fiber、ordered-dense coefficient oracle、および次の8 TTを比較する。

1. `flat-q-first`
2. `flat-q-last`
3. `d1q3-q-first`
4. `d1q3-q-last`
5. `wave-branch-tuple-major`
6. `wave-branch-factor-major`
7. `wave-qtt-tuple-major`
8. `wave-qtt-scale-interleaved`

stored real scalar countはcore格納スカラー数であって数学的独立自由度とは呼ばない。
格納判定には、sparse index／multiplicity metadataを含むraw array payload bytesとuncompressed NPZ
serialized bytesも必ず併記する。TTについてはnominal gauge-adjusted dimensionを診断値として記録するが、
判定指標へ置き換えない。

### offline cost protocol

full quartic modelとnatural coefficient familyの構築、およびordered-dense oracleのmaterializationは
全methodの共通入力としてtimingから除外する。これはTT-SVDに有利な除外であり、full pipeline costを
過小評価する。

- sparse offline preparation:
  registered dtypeへのfresh copy、storage record生成、uncompressed NPZ roundtrip
- TT offline preparation:
  sealed tensorization、TT-SVD、storage record生成、uncompressed NPZ roundtrip
- ordered-dense control:
  fresh dense copy、uncompressed NPZ roundtrip
- warmup 1回、measured 3回
- 各回でbitwise serialization roundtrip、fidelity、finite timeを検査する

method \(m\) のoffline blockを\(B_{m,j}\)とし、

\[
B_m^-=\min_jB_{m,j},\qquad B_m^+=\max_jB_{m,j}
\]

を保存する。

### independent online campaign

- seed: `20260901`
- normalized real reduced directions: 16
- Q008a action／timing seed `20260827 / 20260828` と
  Q008c action／timing seed `20260829 / 20260830` の全方向に対するexact duplicate: 0
- warmup block: 1
- measured block: 5
- method order: blockごとのcyclic rotation
- timer: `perf_counter_ns`
- scope: local homogeneous quartic 9-vector action only
- 各blockで16方向のoutput norm checksumを保存し、sparseに対する相対差を\(10^{-11}\)以下とする

sample当たりonline timeを\(t_{m,j}\)とし、

\[
t_m^-=\min_jt_{m,j},\qquad
t_m^+=\max_jt_{m,j}
\]

を保存する。環境固有の有限campaignであるため、漸近計算量や他machineの速度とは解釈しない。

### break-even定義

natural sparse-fiberを\(s\)、TT候補を\(m\)とする。TTに最も有利な観測下界とsparseに最も不利な
観測上界を使い、

\[
T_m^-(N)=B_m^-+Nt_m^-,
\qquad
T_s^+(N)=B_s^++Nt_s^+,
\qquad N\in\mathbb Z_{\ge0}
\]

を定義する。

\[
B_m^->B_s^+,\qquad t_m^->t_s^+
\]

なら、登録campaignの全\(N\ge0\)で\(T_m^-(N)>T_s^+(N)\)なので
`robust no finite sparse-baseline time break-even`とする。どちらかが逆転した候補には、
median cost lineの最小整数break-evenを別途計算する。時間上のbreak-evenがあっても、raw payloadと
serialized bytesの両方でsparseをstrictに下回らなければTT採択とはしない。

ordered-dense controlとのbreak-evenも診断として計算するが、natural sparse baselineを判定から
外さない。ordered-dense coefficient oracleをfull dense LBMとは呼ばない。

### validity gate

1. Q008a／Q008c artifact SHA、package source、scope、outcome、全validity／fidelityが一致する。
2. fixed coefficient hash、fiber count、8 candidate mapping、TT rank／storageをfresh buildで再現する。
3. holdout方向が正規化され、hashが再現し、Q008a／Q008c全既登録方向とのexact duplicateが0である。
4. sparse／dense／8 TT actionが全有限で、全block checksum relative errorが\(10^{-11}\)以下である。
5. offline／onlineの回数、cyclic order、全time record、storage／serialization roundtripが再現する。
6. strict JSON、input digest、result digestが再現する。

一つでも失敗すれば`inconclusive`とし、cost仮説を解釈しない。

### hypothesis gateと停止規則

validity通過時だけ次を判定する。

1. 8 TT全てでcore stored real scalars、raw array payload bytes、serialized bytesがnatural
   sparse-fiberより大きい。
2. 8 TT全てで\(B_m^->B_s^+\)である。
3. 8 TT全てで\(t_m^->t_s^+\)かつmedian online slowdownが2以上である。
4. 8 TT全てが`robust no finite sparse-baseline time break-even`である。
5. 従って時間と格納量を同時にsparseより小さくする採択候補が0である。

全て通れば
`sealed TT-SVD path is cost-dominated by natural quartic sparse-fiber`
としてnegative hypothesisを`accepted`とし、固定Q007c1係数に対するQ009／TT-SVD
online rolloutを開始しない。

onlineまたはoffline dominanceが一候補でも崩れた場合はtiming結論を
`not_certified`とする。ただしQ008a／Q008cのstorage rejectionは変更しない。
時間break-evenとstorage lossが併存する場合は
`time break-even observed but sparse storage still dominates`
と分類し、総合TT採択はしない。threshold、方向数、候補を結果後に変更しない。

### 主張境界

本ゲートは固定Q007c1 quartic coefficient、8 full-rank TT-SVD候補、現在のCPU／Python／NumPy環境、
local homogeneous quartic actionに限る。full reduced-chart rollout、full dense LBM、direct TT-LBM、
MPFR backend、GPU、parallel／thread scaling、compressed TT rounding、TT-cross、別tensorization、
別grid、D3Q27、energy consumption、asymptotic rank／complexityを主張しない。runtime noiseを含む
有限campaignなので、結果はartifactに記録した環境とblock envelopeに限定する。

### Q010 封印結果

全6 validity gateと全5 hypothesis gateが通過し、
`sealed TT-SVD path is cost-dominated by natural quartic sparse-fiber`
としてnegative hypothesisを`accepted`とした。

- holdout direction hash／prior exact duplicate:
  `ed625949a32c1cbf6cb7f00e0a4cca5e05675481159b29c61db59c769890609b / 0`
- maximum norm error:
  `2.220446049250313e-16`
- sparse offline min／median／max:
  `20.9392 / 20.9547 / 21.6592 ms`
- fastest TT offline min／median／max（`flat-q-last`）:
  `1.3654306 / 1.3732766 / 1.3768735 s`
- sparse online min／median／max:
  `0.5805375 / 0.58298125 / 0.61728125 ms per sample`
- fastest TT online min／median／max（`flat-q-last`）:
  `2.85776875 / 2.89795 / 3.0604 ms per sample`
- fastest median slowdown／best-TT-min to sparse-max envelope ratio:
  `4.9709145877333105 / 4.629605629524629`
- sparse stored real scalars／raw payload／serialized bytes:
  `315900 / 2614950 / 2615734`
- best TT core stored real scalars／raw payload／serialized bytes:
  `3550626 / 28405096 / 28406852`
- best TT/sparse ratios:
  `11.2397150997151 / 10.8625771047248 / 10.859992644512`
- maximum dense-vs-sparse action error:
  `1.20460032995549e-14`
- maximum TT reconstruction／action error:
  `1.49154657341154e-13 / 6.63724332998628e-13`
- maximum block checksum relative error:
  `4.65675471404282e-14`
- flat／D1Q3 candidatesのordered-dense median break-even:
  `120--144 actions`
- wave candidatesのordered-dense median break-even:
  なし
- input／result digest:
  `566d3ce0569736c140dae7c4f19d36223957e5ad2b25abc4b9d6a012558d0841` /
  `79545f0cbf14a53fef52d46bc44cbb8586efb95e1b6645d7c8cc00b45ceed6dc`
- runner SHA-256:
  `c6e99082a3418d604f7d09687685cf5e6ab9efe341ea36153123bb8ad4b26b4e`
- artifact newline-normalized SHA-256:
  `2885a029ecfe2c17aebe3b05b305caebd927d78476971e4ab186455d0ee30b7f`

全8 TTでbest offline timeがworst sparse offline timeを、best online timeがworst sparse online
timeをstrictに上回った。従って、TTに有利な共通費用除外のもとでも登録campaignの全\(N\ge0\)で
有限sparse-baseline time break-evenはない。さらに全候補がcore stored real scalars、raw payload、
serialized bytesの3指標でsparseより大きいので、時間と格納量を同時に通す候補は0である。

ordered-dense coefficient oracleに対するflat系の時間break-evenは、natural sparse-fiberを外す理由に
ならない。またordered-dense controlはfull dense LBMではない。本結果は固定8 full-rank TT-SVD候補と
現在のCPU finite campaignだけに限る。TT一般、TT-cross、別tensorization、GPU、full rollout、他grid、
D3Q27の不可能性は主張しない。固定Q007c1係数のQ009／TT-SVD online pathは閉じる。新しい表現を試す
場合はcandidate familyを結果前に別途事前登録する。

## Q007ac: phase-aware external-output resolvent refinement — 事前登録

### 問い

Q007oのtotal homological inverseを支配しているQ007n由来のexternal-output upper

\[
C_{\rm ext}=81\beta_*/\delta
=2.746444556852928\times10^{13}
\]

について、modulusだけでなく複素位相を保持した固有値discとselected eigenvalue productを比較する。
Q007oのselected-output internal inverse、zero-wave inverse、quartic center、非線形majorant、
119候補を一切変えずに、external-output blockをtotal inverseの支配要因から外し、登録existence
radiusをstrictに改善できるか。

### 封印する入力とscope

- Q007h1 artifact newline-normalized SHA-256:
  `caee8fe382c0282e11e8139b8f434a944013f630288adf2e99223d0123c91af4`
- Q007i artifact newline-normalized SHA-256:
  `c256b30ac5bfe0a6bc5e5f8e293016d3e0aa37c4bfa82ba81a0a2679d89e082f`
- Q007n artifact newline-normalized SHA-256:
  `7fe09089744e41229e71666540e4885d560a4c27a2e8bc95a94d5959af0fbc36`
- Q007o artifact newline-normalized SHA-256:
  `36a350b27658ce0699727640d65c48cf0700f999ca1881b07d45825d086158fd`
- Q007i／Q007h1 implementation source SHA-256:
  `22209c56184eff9556db13b553cb89644eea11ffd77a3af69d0316a747118294` /
  `d2d857c1b9ac20f88c9b1a1a44e59bd1d15dad043d5e96fde5069ea0c1865a94`
- Q007n／Q007o standalone runner SHA-256:
  `6eefae3386e5c49f151b1cd4537eb84fbb92858578fe4fce7768e50ad43c5dc9` /
  `d34afda382784610ea2b8997e6c44376188b02c42668ade8e2d53ff9bc9afea7`
- 固定map／葉／norm:
  \(17^2\)、\(\omega=3/2\)、\(\eta=1/100\)、
  \(\delta M=\delta P_x=\delta P_y=0\)、Q007nのmodal／Wiener \(\ell^1\)とpair max norm

Q007oのworking selected-output internal inverse
`2.1920952274236575e11`、Q007nのzero-wave inverse
`6.2060607588672085e9`、80桁外向き丸め、次数2--4 coefficient majorant、
D2Q9 nonlinear majorant、候補 \(10^{-2},\ldots,10^{-120}\)、収縮閾値\(1/2\)を固定する。
変更を許すのはnonzero nonselected output blockのinverse upperだけである。

### 対称なselected nominal discs

Q007iと同じQ007h1 proof reconstructionを行い、selected C4 representativeを
axis \((-1,0)\)、diagonal \((-1,-1)\)へ固定する。返却固有値indexは

- axis acoustic／shear: `(0,1) / 4`
- diagonal acoustic／shear: `(0,1) / 6`

とする。各type \(X\in\{A,D\}\)について、float64 centerをexact dyadic point
\(z_{X,+},z_{X,-},z_{X,s}\)へ戻し、

\[
\widehat z_{X,+}=z_{X,+},\qquad
\widehat z_{X,-}=\overline{z_{X,+}},\qquad
\widehat z_{X,s}=\Re z_{X,s}
\]

をnominal centerとする。Q007h1のBauer--Fike radiusに
\(|z_{X,-}-\overline{z_{X,+}}|\)または\(|\Im z_{X,s}|\)を加え、元の3個のexact
selected eigenvalue discを上の共役対／実軸discで覆う。Q007h1のexact C4 transportにより、
この6 nominal discsを全24 selected modeへ適用する。全nominal centerとdiscがQ007nのworking
selected spectral-radius upper \(\sigma\)以下であることをvalidity gateにする。

### external-output target discs

Q007h1の72 nonzero C4 representativesのうちselected representative 2個を除く70個について、
9個全てのfloat64 eigenvalue centerをexact dyadic pointへ戻し、保存された
Bauer--Fike radiusを付ける。従ってtargetは

\[
70\times9=630
\]

個のnonzero nonselected-output eigenvalue discsである。selected output waveの6次元external
complementはQ007oのinternal inverseが、zero waveはQ007nのfixed-leaf inverseが既に担当するため、
この630 targetへ混ぜない。

本gateでは入力waveの和によるFourier selection ruleを使わず、全selected productを全630 targetと
比較する。これは実際に許されるpairのsupersetなので、通過すれば保守的だが有効な一様upperになる。
失敗時だけ、別gateでwave-sum restrictionを事前登録する。

### modulus screen

Q007iと同じ96項rational logarithm、110桁内部／60桁最終外向き格子を使う。selected側は
`axis_acoustic, axis_shear, diagonal_acoustic, diagonal_shear`の4 type、
external側は上記630 discsとする。次数\(n=2,\ldots,89\)の全

\[
\sum_{n=2}^{89}{n+3\choose3}=2{,}919{,}730
\]

modulus aggregateを同じ順序で列挙する。screen幅は結果後に変えず

\[
g_{\rm screen}=10^{-6}
\]

へ固定する。aggregate log intervalと全external log intervalの距離が
\(g_{\rm screen}\)以上なら、Q007nのfinite-degree modulus floor

\[
m_*=\min(\underline\sigma_\perp,\underline\sigma_E^{89})
\]

と \(e^x-1\ge x\) により、複素距離も
\(m_*g_{\rm screen}\)以上である。validity gateでは

\[
m_*g_{\rm screen}>\delta_{\rm phase},\qquad
\delta_{\rm phase}=10^{-7}
\]

をexact rationalで要求する。

距離が\(g_{\rm screen}\)未満のaggregateだけを`dangerous`とし、そのaggregateから
screen幅内にある全external merged intervalと全source disc identifierを保存する。nearest一個だけへ
省略しない。

### dangerous aggregateの完全なphase展開

dangerous aggregateを
\((a_a,a_s,d_a,d_s)\)とする。axis／diagonal acoustic countを

\[
a_++a_-=a_a,\qquad d_++d_-=d_a
\]

の全ての方法で分割し、

\[
\widehat p=
\widehat z_{A,+}^{a_+}
\widehat z_{A,-}^{a_-}
\widehat z_{A,s}^{a_s}
\widehat z_{D,+}^{d_+}
\widehat z_{D,-}^{d_-}
\widehat z_{D,s}^{d_s}
\]

をcomplex `Fraction` pairとして計算する。積記号の代わりに上式では隣接積を意味する。
各factorのnominal-disc inflationを\(\epsilon_j\)、total degreeを\(n\)とすると、telescopingから

\[
\epsilon_p
\le \sigma^{n-1}\sum_{j=1}^{n}\epsilon_j
\]

でexact selected productを囲む。各nearby external disc center／radiusを
\((\widehat\mu,r_\mu)\)とし、全展開pairについて平方根を使わず

\[
 |\widehat p-\widehat\mu|^2
 >
 \left(\delta_{\rm phase}+\epsilon_p+r_\mu\right)^2
\]

をexact `Fraction`で要求する。dangerous aggregate数、expanded product数、
disc comparison数、最小strict marginとwitnessを保存する。screen外はmodulus proof、
screen内はこの完全展開で被覆し、未判定pairを許さない。

次数90以上はQ007nの

\[
\delta_{\rm tail}
=\underline\sigma_\perp-\overline\sigma_E^{90}
\]

をそのまま使い、\(\delta_{\rm tail}>\delta_{\rm phase}\)を要求する。

### inverse upperと固定radius再走査

finite degreeとtailを合わせたworking external gapを
\(\delta_{\rm ext}=\delta_{\rm phase}=10^{-7}\)へ固定し、Q007nと同じ
\(\beta_*\)およびnorm conversionを使って

\[
C_{\rm ext}^{\rm phase}=81\beta_*/\delta_{\rm ext}
\]

を80桁10進格子へ上向きに丸める。新しいtotal pair inverseは

\[
C_L^{\rm new}
=\max\left\{
C_{\rm ext}^{\rm phase},
C_0,
C_{\rm int}^{\rm Q007o}
\right\}
\]

とする。Q007oの旧total inverseで119 candidate recordをexact再現した後、変更した
\(C_L^{\rm new}\)だけで同じ`_radius_scan`を再実行する。

### validity gate

1. 4 artifact SHA、4 implementation／runner SHA、source、scope、Q007h1／Q007i／Q007n／Q007oの
   sealed outcomeと全gateが一致する。
2. 72 proof digestを再現し、selected representative／index、C4 transport、6 nominal-disc containment、
   70 nonselected representative／630 target discをexactに確認する。
3. Q007i logarithm設定、2,919,730 aggregate count、全screen partitionを再現し、
   \(m_*g_{\rm screen}>\delta_{\rm phase}\)をexactに確認する。
4. 全dangerous aggregateを完全展開し、全nearby target discとの上記平方距離判定を実行する。
   tail gapもstrictに\(\delta_{\rm phase}\)を超える。
5. Q007o internal inverse、Q007n zero inverse、全majorant、119候補をbitwiseに再利用し、
   Q007o旧candidate recordをexact再現する。
6. 全数値がfiniteでstrict JSON、input digest、phase-certificate digest、result digestを再現する。

一つでも落ちれば`inconclusive`とし、external inverseや半径改善を解釈しない。

### hypothesis gateと停止規則

validity通過時だけ次を判定する。

1. finite degreeの全screen内pairとdegree-90 tailが
   \(\delta_{\rm ext}=10^{-7}\)をstrictに満たす。
2. \(C_{\rm ext}^{\rm phase}<C_{\rm int}^{\rm Q007o}\)であり、external-outputがtotal inverseの
   支配要因から外れる。
3. \(C_L^{\rm Q007o}/C_L^{\rm new}\ge100\)である。
4. Q007oの\(10^{-18}\)がpassし、新しい最大pass候補がstrictに大きい。
5. 新しい最大pass候補でdensity／reduced-range buffer、\(Z<1/2\)、
   \(Y+Z\tau<\tau\)が全てstrictで、直前の大きい候補がfailするか\(10^{-2}\)である。

全て通れば
`phase-aware external-output discs remove the registered resolvent bottleneck`
として`accepted`とする。一つでも落ちれば
`registered phase-aware external-output refinement did not remove the bottleneck`
という有効な`not_certified`とする。screen幅、target gap、target discs、半径候補を結果後に
変更しない。

### 主張境界

acceptedでも、固定17²・固定保存量葉・固定modal／Wiener normに対するanalytic existence radiusだけを
鋭くする。位相付きgapの最適値、Fourier wave-sumを使ったsharp bound、Q007o selected-output internal
inverseの追加改善、zero-wave phase改善、連続最適化、Euclidean／grid-uniform normal attraction、
global basin、Q007c1の有限振幅性能、既存Q007p--Q007abのtube／MPFR定数の拡大、境界、外力、
D3Q27は認証しない。既存の小さいtubeとforward-shadowing結論はそのまま有効であり、再解釈しない。

### Q007ac 封印結果

validity 6件中5件、hypothesis 5件中4件が通過した。事前登録したvalidityとphase gapの双方に
反例があるため、
`registered Q007ac phase-aware audit invalid`
として`inconclusive`で停止した。

- 72 Q007h1 representative proof digest mismatch: `0`
- nonselected representative／target disc: `70 / 630`
- modulus aggregate／expanded product: `2,919,730 / 869,107,778`
- safe／dangerous aggregate: `2,918,904 / 826`
- dangerous expanded product／exact comparison: `108,273 / 287,929`
- target phase gap: `1e-7`
- nominal selected discs contain all original selected discs: pass
- nominal selected discs remain inside Q007n working \(\sigma\): fail
- required factor-modulus inflation: `1.6653345369377348e-16`
- failed exact phase comparison: `4`
- minimum witness:
  degree `71`、modulus counts `(24,38,2,7)`、acoustic positive／negative
  split `(12,12,1,1)`、external
  `wave=(-7,-7);eigenvalue_index=6`
- certified complex distance lower: `2.4028360293239852e-8`
- phase comparison digest:
  `5039563c60ab57b85b683b324506049535372847b1a5adef3362da2b16a954ab`
- input／result digest:
  `15166f90e39b132c0d6956b7a14f821095cc1b31da9d9e83b9b3f5b9cf3314b9` /
  `369809e953652c9e99ade3553e2754a06c1b0add52549e2f53dbcdb0ab15f018`
- runner SHA-256:
  `8c2757c4c3771007dc15135bc407551bbef74906294ab897b1a4f251d5abe2ae`
- artifact newline-normalized SHA-256:
  `b3c9d99088492bf157cbb651d958597573a9c7b5386a189b6b9e4ee5d88dbcf5`

診断上は、登録gapを仮定したexternal inverse
`4.425423249246816e10`がQ007o internal inverse
`2.1920952274236575e11`を下回り、total改善率`125.28856057411295`、
最大pass候補`1e-16`となった。しかし停止規則により、このcounterfactual scanを定理半径へ採用しない。
Q007oの`1e-18`、Q007p--Q007abのtube／positivity／MPFR／forward-shadowing結論、Q007c1とQ008c／
Q010のnegative outcomeは全て据え置く。

次は別gateで、original asymmetric selected discsを直接使うか、必要な
`1.6653345369377348e-16` inflationを明示したproduct-factor upperを固定する。そのうえで
\(81\beta_*/C_{\rm int}^{\rm Q007o}\)からexternal bottleneckを外すためのcritical gapを先に計算し、
Q007acの失敗witnessから十分離した新しいtarget gapを事前登録する。Fourier wave-sumを使う場合も
追加改善として明示し、Q007acの`1e-7`を事後に書き換えない。

## Q007ad: asymmetric-disc critical phase certificate — 事前登録

### 問いと位置づけ

Q007acは、対称化したselected nominal discがQ007n working spectral radiusを
`1.6653345369377348e-16`超え、登録gap \(10^{-7}\)にも4反例があったため無効・
`inconclusive`で停止した。この結果を変更せず、元のQ007h1 asymmetric selected discsを
直接使い、external inverseをQ007o internal inverseより小さくするために必要なcritical gapを先に
導いた別のcertificateを問う。

本gateはQ007acの失敗witnessを見た後のfollow-up certificateであり、独立な探索仮説ではない。
Q007acのcounterfactualを証明入力として使わず、新しい閾値、disc、停止規則を結果計算前に固定する。

### 封印する入力

- Q007h1 artifact newline-normalized SHA-256:
  `caee8fe382c0282e11e8139b8f434a944013f630288adf2e99223d0123c91af4`
- Q007i artifact newline-normalized SHA-256:
  `c256b30ac5bfe0a6bc5e5f8e293016d3e0aa37c4bfa82ba81a0a2679d89e082f`
- Q007n artifact newline-normalized SHA-256:
  `7fe09089744e41229e71666540e4885d560a4c27a2e8bc95a94d5959af0fbc36`
- Q007o artifact newline-normalized SHA-256:
  `36a350b27658ce0699727640d65c48cf0700f999ca1881b07d45825d086158fd`
- Q007ac artifact newline-normalized SHA-256:
  `b3c9d99088492bf157cbb651d958597573a9c7b5386a189b6b9e4ee5d88dbcf5`
- Q007i／Q007h1／Q007n／Q007o implementation／runner SHA-256:
  `22209c56184eff9556db13b553cb89644eea11ffd77a3af69d0316a747118294` /
  `d2d857c1b9ac20f88c9b1a1a44e59bd1d15dad043d5e96fde5069ea0c1865a94` /
  `6eefae3386e5c49f151b1cd4537eb84fbb92858578fe4fce7768e50ad43c5dc9` /
  `d34afda382784610ea2b8997e6c44376188b02c42668ade8e2d53ff9bc9afea7`
- Q007ac runner SHA-256:
  `8c2757c4c3771007dc15135bc407551bbef74906294ab897b1a4f251d5abe2ae`
- Q007ac input／result／phase-comparison digest:
  `15166f90e39b132c0d6956b7a14f821095cc1b31da9d9e83b9b3f5b9cf3314b9` /
  `369809e953652c9e99ade3553e2754a06c1b0add52549e2f53dbcdb0ab15f018` /
  `5039563c60ab57b85b683b324506049535372847b1a5adef3362da2b16a954ab`

固定scopeは \(17^2\)、\(\omega=3/2\)、\(\eta=1/100\)、
\(\delta M=\delta P_x=\delta P_y=0\)、Q007nのmodal／Wiener \(\ell^1\)およびpair max normとする。
Q007o internal inverse、Q007n zero-wave inverse、80桁外向き丸め、全majorant、119 radius候補、
収縮閾値 \(1/2\)を変えない。変更対象はnonzero nonselected-output inverseだけである。

### critical gapと登録target

Q007n working \(\beta_*\)とQ007o working internal pair inverseから

\[
\delta_{\rm crit}
=\frac{81\beta_*}{C_{\rm int}^{\rm Q007o}}
=2.0188097642308912\ldots\times10^{-8}
\]

をexact `Fraction`として先に計算する。既約分数の16進表現を

- numerator:
  `0x137064b41f6973f11f3f0d50cba3d16b9eacb4ae5b8d89232971db9f7ebae6994c7dad`
- denominator:
  `0x3964a0243f0d52700d16c0516ff99b6188ae3fabc5034ea22cf4ab1268f148a006530509af97`

へ封印する。新しいtarget gapは

\[
\delta_{\rm ad}=\frac{21}{10^9}=2.1\times10^{-8}
\]

とする。これは \(\delta_{\rm ad}/\delta_{\rm crit}
=1.0402168828423712\ldots>1\) であり、Q007acの診断上の最小distance lower
`2.4028360293239852e-8`より約12.6%小さい。後者は閾値選択の動機に限り、
Q007adのcertificateとして再利用しない。80桁上向き丸め後にも

\[
\left\lceil81\beta_*/\delta_{\rm ad}\right\rceil_{80}
<C_{\rm int}^{\rm Q007o}
\]

をexactに要求する。

### original asymmetric selected discs

Q007h1 proofを72 C4 representativeについて再構成する。selected representativeとindexは
Q007acと同じく

- axis \((-1,0)\): acoustic `(0,1)`、shear `4`
- diagonal \((-1,-1)\): acoustic `(0,1)`、shear `6`

へ固定する。ただし共役化・実軸化・再中心化を一切行わない。6個それぞれについて、保存された
float64 eigenvalueをexact dyadic center \(z_j\)へ戻し、同じrepresentativeのQ007h1
Bauer--Fike radius \(r_j\)をそのまま使う。

全6 discで

\[
\overline{|z_j|}+r_j\le\sigma_{\rm Q007n}
\]

をexact rationalで確認し、product telescoping factorには新しいmaxやinflationではなく
Q007nの封印済み \(\sigma_{\rm Q007n}\) を使う。C4 transportにより全24 selected modeを覆うことも
再確認する。Q007acで無効だったsymmetric nominal discsは比較診断としてのみ再現し、
Q007adのproduct center／radiusへ混ぜない。

### target、screen、phase expansion

external targetはQ007acと同一の70 nonselected C4 representative \(\times9=630\) original
Bauer--Fike discsとし、selected-output external complementとzero waveは除く。Fourier wave-sum
restrictionは今回も使わず、全selected productと全630 targetのsupersetを証明する。

modulus screenはQ007acの \(g_{\rm screen}=10^{-6}\)、96項rational logarithm、
110／60桁格子、次数2--89を固定する。2,919,730 aggregate、826 dangerous aggregate、
108,273 expanded product、287,929 nearby comparison、およびdangerous identifier列が
Q007ac artifactとexactに一致することをvalidity gateにする。screen外は

\[
m_*g_{\rm screen}>\delta_{\rm ad}
\]

で覆う。

dangerous aggregate \((a_a,a_s,d_a,d_s)\)では、axis／diagonal acousticを全て
positive／negative indexへ分割し、original asymmetric centersからproduct center
\(\widehat p\)をexact dyadic arithmeticで計算する。各splitのdisc uncertaintyは

\[
\epsilon_p
\le \sigma_{\rm Q007n}^{n-1}
\sum_j c_j r_j
\]

とし、nearby external disc \((\widehat\mu,r_\mu)\)ごとに

\[
|\widehat p-\widehat\mu|^2
>
\left(\delta_{\rm ad}+\epsilon_p+r_\mu\right)^2
\]

を要求する。右辺thresholdだけを256 binary bit dyadic格子へ上向きに丸め、丸め増分が
\(2^{-256}\)未満であることを保存する。degree 90以上はQ007n tail gapを再利用し、
\(\delta_{\rm tail}>\delta_{\rm ad}\)を要求する。

### inverseとradius再走査

phase certificateが通れば

\[
C_{\rm ext}^{\rm ad}
=\left\lceil81\beta_*/\delta_{\rm ad}\right\rceil_{80},\qquad
C_L^{\rm ad}
=\max\{C_{\rm ext}^{\rm ad},C_0,C_{\rm int}^{\rm Q007o}\}
\]

とする。Q007o旧119 recordをexact再現してから、\(C_L^{\rm ad}\)だけを差し替えて同じ
radius scanを行う。Q007acで観測済みのcounterfactual scanに依存せず、Q007o入力から再計算する。

### validity gate

1. 5 artifact SHA、5 implementation／runner SHA、source、scope、sealed outcomeが一致し、
   Q007acのinvalid／`inconclusive`結果と3 digestをexact再現する。
2. 72 proof digest、selected representative／index、C4 coverage、6 original asymmetric discs、
   Q007n \(\sigma\) containment、70 representative／630 targetをexact確認する。
3. Q007acと同じ全screen partition・dangerous identifiers・4 countをexact再現し、
   safe floorとtailが \(\delta_{\rm ad}\)をstrictに超える。
4. 108,273 original-center productと287,929 nearby comparisonを省略なく実行し、
   最小margin、witness、comparison digestを保存する。
5. Q007o internal、Q007n zero、majorant、119候補をbitwiseに再利用し、旧Q007o recordsをexact再現する。
6. 全数値がfinite strict JSONであり、input／phase／result digestを再現する。

一つでも落ちれば`inconclusive`で停止し、external inverseとradiusを更新しない。

### hypothesis gateと停止規則

validity通過時だけ次を判定する。

1. 全finite-degree comparisonとdegree-90 tailが \(\delta_{\rm ad}=2.1\times10^{-8}\)をstrictに満たす。
2. 80桁working \(C_{\rm ext}^{\rm ad}<C_{\rm int}^{\rm Q007o}\)で、new totalがinternal-limitedになる。
3. \(C_L^{\rm Q007o}/C_L^{\rm ad}\ge100\)である。
4. Q007oの`1e-18`がpassし、新しい最大pass候補がexactに`1e-16`、
   直前の大きい`1e-15`がfailする。
5. `1e-16`でdensity／reduced-range buffer、\(Z<1/2\)、
   \(Y+Z\tau<\tau\)が全てstrictである。

全て通れば
`original asymmetric discs certify the critical external-output phase gap`
として`accepted`とする。validityは通るが一つでも仮説が落ちれば
`registered asymmetric-disc critical phase certificate did not pass`
という有効な`not_certified`とする。gap、disc、screen、candidateを結果後に変更しない。

### 主張境界

acceptedでも、固定17²・固定保存量葉・固定normに対するQ007o analytic existence radiusを
`1e-16`へ改善するだけである。これはQ007acの`1e-7`主張を復活させず、
\(\delta_{\rm ad}\)がoptimal gapであるとも主張しない。Fourier wave-sum、selected-output internal／
zero-wave inverseの改善、連続最適化、Euclidean／grid-uniform bound、finite-ball normal attraction、
global basin、Q007c1 finite-amplitude性能、境界、外力、D3Q27は扱わない。既存Q007p--Q007abの
tube／positivity／MPFR／forward-shadowing定数は`1e-18`を前提に据え置き、拡大するなら
別gateを必要とする。

### Q007ad 封印結果

validity 6件、hypothesis 5件が全て通過し、
`original asymmetric discs certify the critical external-output phase gap`
として`accepted`とした。

- Q007ac invalid input、artifact／runner／3 digest reproduction: pass
- 72 Q007h1 proof digest mismatch: `0`
- original asymmetric selected disc／target disc: `6 / 630`
- selected discのQ007n working \(\sigma\) containment: pass
- minimum \(\sigma\) slack: `7.672593033162951e-81`
- product-factor inflation over Q007n \(\sigma\): `0`
- critical gap:
  `2.0188097642308912e-8`
- registered target／critical ratio:
  `2.1e-8 / 1.0402168828423712`
- Q007ac screen partition／identifier exact reproduction: pass
- aggregate／dangerous aggregate: `2,919,730 / 826`
- dangerous expanded product／comparison: `108,273 / 287,929`
- failed comparison: `0`
- minimum witness:
  degree `71`、counts `(24,38,2,7)`、acoustic split `(12,12,1,1)`、
  external `wave=(-7,-7);eigenvalue_index=6`
- certified complex distance lower:
  `2.4028364427409988e-8`
- working external／internal／new total inverse:
  `2.107344404403246e11 / 2.1920952274236575e11 / 2.1920952274236575e11`
- total improvement factor: `125.28856057411295`
- selected／previous candidate: `1e-16 pass / 1e-15 fail`
- input／result digest:
  `b1b1b2750e871c6ee3b243f7df590ec19dd6d604d9699f183af007b89d0f7935` /
  `f5df89c55a86978c85542eeec82e6419884b69b919c0385ca77e9677b1c1d17f`
- phase comparison digest:
  `086516b273f30d7c94c276399c16f8a6433bd90e3dc03fb740d2ab45754e4a37`
- runner SHA-256:
  `3ca5e39c3ddb79c886ef7bf4d6e6ad923deb66e53da3663251f183abbab7b0ae`
- artifact newline-normalized SHA-256:
  `6a6f642cb681409ca160773180e025c1ffbc1929d6ec84423c384c57007571e4`

従って固定17²・固定保存量葉・固定modal／Wiener normに対するQ007i analytic manifoldの
explicit modal \(\ell^1\) radiusを`1e-16`へ更新する。Q007acの`1e-7` certificateは
依然としてinvalidであり、Q007ad gapの最適性も主張しない。

Q007p--Q007abは`1e-18` analytic radiusとそれより小さいtubeを入力にした別certificateである。
Q007adではそれらを再走査していないため、tube／positivity／MPFR／forward-shadowing定数を拡大しない。
次の数学的bottleneckはQ007o selected-output internal inverse
`2.1920952274236575e11`である。これをphase-awareに改善するか、先に`1e-16` radiusを
使って下流tubeを再監査するかは、別の事前登録gateとして扱う。

## Q007ae: phase-aware selected-output internal resolvent — 事前登録

### 問いとbottleneck再現

Q007ad後のtotal inverseはQ007o diagonal selected-output internal block
`2.1920952274236575e11`に支配される。Q007oのexact recordから、そのchart upperは

\[
C_{{\rm int},k}
=\frac{N_k}{\delta_{\rm global}-\gamma_k},\qquad
N_k=\|U_k\|_1\kappa_k\|J_kQ_k\|_1
\]

であり、axial／diagonalについて

- \(N_A=21.404760870264376\ldots\)、
  \(\gamma_A=4.4155560973760785\times10^{-15}\)
- \(N_D=35.31936026583468\ldots\)、
  \(\gamma_D=1.1339793519314153\times10^{-14}\)

だった。ここで再利用されたQ007n global absolute gapは
`1.611328085325626e-10`である。一方、その元となるQ007i global minimum log-gap
witnessはdegree `51`、counts `(1,19,27,4)`、external
`wave=(-2,-2);eigenvalue_index=(8,7)`であり、selected output waveではない。

そこで、selected outputのexternal coordinate centersだけをoriginal selected product discsと
complex phase付きで比較し、Q007oのglobal modulus gapを置き換える。Q007adのexternal-output
certificateと全majorantを固定したまま、internal blockをtotalの支配要因から外せるかを問う。

### 封印する入力

- Q007h1 artifact newline-normalized SHA-256:
  `caee8fe382c0282e11e8139b8f434a944013f630288adf2e99223d0123c91af4`
- Q007i artifact newline-normalized SHA-256:
  `c256b30ac5bfe0a6bc5e5f8e293016d3e0aa37c4bfa82ba81a0a2679d89e082f`
- Q007n artifact newline-normalized SHA-256:
  `7fe09089744e41229e71666540e4885d560a4c27a2e8bc95a94d5959af0fbc36`
- Q007o artifact newline-normalized SHA-256:
  `36a350b27658ce0699727640d65c48cf0700f999ca1881b07d45825d086158fd`
- Q007ad artifact newline-normalized SHA-256:
  `6a6f642cb681409ca160773180e025c1ffbc1929d6ec84423c384c57007571e4`
- Q007i／Q007h1／Q007n／Q007o／Q007ad implementation／runner SHA-256:
  `22209c56184eff9556db13b553cb89644eea11ffd77a3af69d0316a747118294` /
  `d2d857c1b9ac20f88c9b1a1a44e59bd1d15dad043d5e96fde5069ea0c1865a94` /
  `6eefae3386e5c49f151b1cd4537eb84fbb92858578fe4fce7768e50ad43c5dc9` /
  `d34afda382784610ea2b8997e6c44376188b02c42668ade8e2d53ff9bc9afea7` /
  `3ca5e39c3ddb79c886ef7bf4d6e6ad923deb66e53da3663251f183abbab7b0ae`
- Q007ad input／result／phase digest:
  `b1b1b2750e871c6ee3b243f7df590ec19dd6d604d9699f183af007b89d0f7935` /
  `f5df89c55a86978c85542eeec82e6419884b69b919c0385ca77e9677b1c1d17f` /
  `086516b273f30d7c94c276399c16f8a6433bd90e3dc03fb740d2ab45754e4a37`

固定scopeは \(17^2\)、\(\omega=3/2\)、\(\eta=1/100\)、
\(\delta M=\delta P_x=\delta P_y=0\)、Q007n pair max normおよびmodal／Wiener \(\ell^1\)とする。
Q007ad external inverse、Q007n zero-wave inverse、Q007o external-complement coordinate
constants、80桁外向き丸め、全majorant、119候補を変更しない。

### target gapとcritical internal gap

新しいphase gapは探索せず、Q007adと同じ

\[
\delta_{\rm ae}=\frac{21}{10^9}=2.1\times10^{-8}
\]

へ固定する。Q007o internal upperをQ007n zero-wave upper \(C_0\)より小さくするための各代表の
critical gapは

\[
\delta_{{\rm crit},k}
=\gamma_k+\frac{N_k}{C_0}
\]

である。maximumはdiagonalの
`5.691119055000859e-9`で、exact既約分数の16進表現を

- numerator:
  `0x13b365003d68998a2eff2773756558d32ebe28d1a2d8f901f16ac1fcb4787a91e6a181a003a99e14f9735a6c54a7d153fad5d6f931002887e9b498dda887fcde8201bc36f4f4de76bdc9467222a8603a6d9768d3f0c66e798187db670d0ed9e455960aef38632333de25ffba5b21bb8d0f07c947cbdf3cd29f3cba3410234571c00057afe4f22bce515bc4541e485acb69f11f545c12dbf8ef45`
- denominator:
  `0xce54d951f6b1b735456e9141526f4160dafe61661b02c9c49be7c18aa2cabce02d1d2c83a3aba864c96ece92e130d585fe3409cfce8d627aabd927c60e874d75edc1fac720de10bcc2b25b16124f937daa544038adc15d83e51808e736f429c6941a2cb56b9d53f7747285969bcc3c454c3d4844306b3dcde3034000000000000000000000000000000000000000000000000000000000000000000000`

へ封印する。target／critical ratioは`3.6899597068782164`である。これらはQ007o sealed
constantsだけから計算し、phase comparison結果を見て選んでいない。

### original selected product discs

Q007adと同じQ007h1 original asymmetric discsを使用する。

- axis \((-1,0)\): acoustic index `(0,1)`、shear `4`
- diagonal \((-1,-1)\): acoustic index `(0,1)`、shear `6`

再中心化・共役化・radius inflationは行わず、product uncertaintyはQ007n working
\(\sigma^{n-1}\sum_jc_jr_j\)で覆う。Q007adの6-disc auditとminimum sigma slack
`7.672593033162951e-81`をexact再現する。

### selected-output external center targets

Q007oの2 representativeについて、Q007h1 source blockで`numpy.linalg.eig`が返した
eigenvalue centerのうちselected 3 indexを除いた6 indexを返却順で使う。

- output \((1,0)\): source \((-1,0)\)、external index `(2,3,5,6,7,8)`
- output \((1,1)\): source \((-1,-1)\)、external index `(2,3,4,5,7,8)`

従ってtargetは12個のexact dyadic point center \(d_{k,j}\)である。ここではQ007h1
Bauer--Fike radiusをtargetへ加えない。Q007o identity

\[
A_kU_k=U_kD_k+Q_kR_k
\]

では \(D_k\)がこのpoint centerで、target eigenpairの残差は既に
\(\gamma_k=\kappa_k\|J_kQ_kR_k\|_1\)として分母から差し引くためである。target radiusと
\(\gamma_k\)を二重計上しない。

C4 transportにより2代表が全8 selected output waveを覆うことを再確認する。本gateではFourier
wave-sum restrictionを使わず、全selected productを全12 centerと比較する。これは許容される
homological pairのsupersetであり、通過すれば保守的に有効である。

### modulus screenとphase比較

Q007adと同じ96項rational logarithm、110／60桁格子、screen
\(g_{\rm screen}=10^{-6}\)、次数2--89の全2,919,730 aggregateを使う。selected typeは4、
external log intervalは上記12 point centerから作る。screen外はQ007n finite modulus floorにより

\[
m_*g_{\rm screen}>\delta_{\rm ae}
\]

で覆う。screen内aggregateだけをaxis／diagonal acoustic +/-へ完全展開し、全nearby centerに対して

\[
|\widehat p-d_{k,j}|^2
>
\left(\delta_{\rm ae}+\epsilon_p\right)^2
\]

をexact dyadic arithmeticで判定する。thresholdは256 binary bit格子へ上向きに丸める。
dangerous aggregate、expanded product、comparison数は結果として保存するが、結果前に特定値を
仮定しない。未判定pairを許さない。degree 90以上はQ007n tail gapを再利用し、
\(\delta_{\rm tail}>\delta_{\rm ae}\)を要求する。

### internal inverseと固定radius再走査

phase certificateが通れば、Q007o各代表のcenter／coordinate constantsを変えず

\[
\begin{aligned}
C_{H,k}^{\rm ae}
&=\frac{N_k}{\delta_{\rm ae}-\gamma_k},\\
C_{{\rm int},k}^{\rm ae}
&=\max\{C_{H,k}^{\rm ae},c_VC_{G,k}\},\\
C_{\rm int}^{\rm ae}
&=\max_k C_{{\rm int},k}^{\rm ae}
\end{aligned}
\]

をexact `Fraction`で計算し、80桁格子へ上向きに丸める。new totalは

\[
C_L^{\rm ae}
=\max\{C_{\rm int}^{\rm ae},C_{\rm ext}^{\rm Q007ad},C_0\}
\]

とする。Q007ad旧119 candidate recordをexact再現してから \(C_L^{\rm ae}\)だけで再走査する。

### validity gate

1. 5 artifact SHA、5 implementation／runner SHA、source、scope、Q007ad accepted outcomeと3 digestが一致する。
2. Q007i global witness、Q007o 2 representative record、\(N_k,\gamma_k\)、critical fractionをexact再現する。
3. Q007ad original 6 discs、Q007o external indices、12 dyadic point targets、C4 coverageをexact確認する。
4. 2,919,730 aggregateを完全partitionし、全dangerous split／nearby centerを比較し、tailを確認する。
5. Q007ad external、Q007n zero、Q007o coordinate constants、majorant、119候補をbitwiseに再利用し、
   Q007ad旧candidate recordsをexact再現する。
6. 全数値がfinite strict JSONで、input／phase／result digestを再現する。

一つでも落ちれば`inconclusive`とし、internal inverseを更新しない。

### hypothesis gateと停止規則

validity通過時だけ次を判定する。

1. 全finite-degree selected-output center comparisonとdegree-90 tailが
   \(\delta_{\rm ae}=2.1\times10^{-8}\)をstrictに満たす。
2. working \(C_{\rm int}^{\rm ae}<2\times10^9<C_0\)で、selected-output internal blockが
   totalを支配しなくなる。
3. new totalがQ007ad external inverseに一致し、
   \(C_L^{\rm Q007ad}/C_L^{\rm ae}\ge1.04\)である。
4. Q007adの`1e-16`が引き続き最大passで、`1e-15`はfailする。
5. `1e-16`の全buffer、\(Z<1/2\)、radii inequalityがstrictである。

全て通れば
`phase-aware selected-output centers remove the internal resolvent bottleneck`
として`accepted`とする。validity通過後に一つでも落ちれば
`registered selected-output phase certificate did not remove the internal bottleneck`
という有効な`not_certified`とする。target gap、target centers、screen、radius候補を
結果後に変更しない。

### 主張境界

acceptedでもQ007adのexplicit analytic radius`1e-16`をstrictに拡大するとは限らず、
今回の登録では同じ10進候補が維持されることを仮説にする。selected-output internal bottleneckを外した後の
支配要因はQ007ad nonselected-output external inverseになる。phase gapの最適性、Fourier wave-sumによる
sharp化、external／zero-waveの追加改善、連続radius最適化、Q007p--Q007ab tubeの拡大、
Euclidean／grid-uniform attraction、global basin、境界、外力、D3Q27は認証しない。

### Q007ae 封印結果

validity 6件、hypothesis 5件が全て通過し、
`phase-aware selected-output centers remove the internal resolvent bottleneck`
として`accepted`とした。

- Q007ad artifact／runner／accepted outcome／3 digest reproduction: pass
- Q007i global minimum witness reproduction: pass
- global witness selected-output membership: false
- original selected disc／selected-output point center: `6 / 12`
- target point radius／Fourier wave-sum restriction: `0 / unused`
- aggregate／dangerous aggregate: `2,919,730 / 81`
- dangerous expanded product／comparison: `15,773 / 19,870`
- failed comparison: `0`
- minimum witness:
  degree `63`、counts `(1,39,17,6)`、acoustic split `(0,1,3,14)`、
  target `selected_output_wave=1,0;external_index=6`
- certified complex distance lower:
  `5.228929928706603e-4`
- minimum squared margin:
  `2.7341709557261616e-7`
- maximum critical gap／target ratio:
  `5.691119055000859e-9 / 3.6899597068782164`
- axial resolvent numerator／working internal:
  `21.404760870264376 / 1.0192745414727758e9`
- diagonal resolvent numerator／working internal:
  `35.31936026583468 / 1.6818752065691547e9`
- working internal／zero／external／new total:
  `1.6818752065691547e9 / 6.2060607588672085e9 / 2.107344404403246e11 / 2.107344404403246e11`
- total improvement factor:
  `1.0402168828423712`
- selected／previous candidate:
  `1e-16 pass / 1e-15 fail`
- input／result digest:
  `23fba479cfa07ec50721d9b05bcaf40a0ac04126497ff64b04785e1d20534e0e` /
  `3e1792c5215952d9126bf5bd61409a2a0d72ebc12970ad1e4aaca481d4fcb687`
- phase／selected-center certificate digest:
  `4aea091076179e7ef8eb14c9c4828b41d6af3ef25665e5b2dbbf562acf692b3b` /
  `3cc524ebb82c3e375bf35d456f96be11fa5d124728873046ed59a7032a2058d7`
- runner SHA-256:
  `f2e0d90ae6bb5f9694c799d2ea850a014f66f2ab9681d94dc1c850cc753db600`
- artifact newline-normalized SHA-256:
  `c6d28bba13fcf831dfccaf03854072256f7e8ff1a241b54aaf84552dd06a2a55`

従ってselected-output internal upperはtotalを支配しなくなった。新しいbottleneckはQ007adの
nonselected-output external inverse`2.107344404403246e11`である。10進候補上のexplicit
analytic radiusは`1e-16`のままで、strictなradius upgradeはない。

minimum selected-center distanceが登録gapより大幅に大きいことは診断結果だが、Q007aeでは
gapを結果後に拡大しない。external gapのsharp化、連続radius最適化、または`1e-16`での
Q007p--Q007ab tube再監査は別gateにする。

## Q007af: external phase-disc certificateのradius-step obstruction — 事前登録

### 問いと固定scope

Q007ae後のtotal inverseを支配するQ007ad nonselected-output external upperを、同じoriginal
asymmetric disc比較族の中でsharp化すれば、次の10進候補
\(r_*=10^{-15}\)を通せる余地が残っているかを先に判定する。本gateは新しいgapを探索して
Q007adを更新するものではない。Q007nのscalar majorantから\(r_*\)に許されるinverse上限を逆算し、
Q007adで既に封印された一つのexact comparisonがその必要gapを妨げるかを調べる。

固定scopeは \(17^2\)、\(\omega=3/2\)、\(\eta=1/100\)、
\(\delta M=\delta P_x=\delta P_y=0\)、Q007n pair max normおよびmodal／Wiener
\(\ell^1\)とする。次を封印入力とする。

- Q007n artifact／runner SHA-256:
  `7fe09089744e41229e71666540e4885d560a4c27a2e8bc95a94d5959af0fbc36` /
  `6eefae3386e5c49f151b1cd4537eb84fbb92858578fe4fce7768e50ad43c5dc9`
- Q007ad artifact／runner SHA-256:
  `6a6f642cb681409ca160773180e025c1ffbc1929d6ec84423c384c57007571e4` /
  `3ca5e39c3ddb79c886ef7bf4d6e6ad923deb66e53da3663251f183abbab7b0ae`
- Q007ae artifact／runner SHA-256:
  `c6d28bba13fcf831dfccaf03854072256f7e8ff1a241b54aaf84552dd06a2a55` /
  `f2e0d90ae6bb5f9694c799d2ea850a014f66f2ab9681d94dc1c850cc753db600`
- 使用するQ007ac／Q007o implementation SHA-256:
  `8c2757c4c3771007dc15135bc407551bbef74906294ab897b1a4f251d5abe2ae` /
  `d34afda382784610ea2b8997e6c44376188b02c42668ade8e2d53ff9bc9afea7`

Q007nのworking coefficient、selected spectral radius、\(\beta_*\)、非線形majorant、
Q007adのoriginal selected／target discs、Q007aeのinternal／zero／external inverse、
80桁外向き丸め、および119個のradius候補を変更しない。Q007ad／Q007aeのaccepted outcomeと
input／result／phase digestもexactに再現する。

### \(10^{-15}\) candidateのinverse threshold

Q007nの`_candidate_record`をそのまま用い、pair inverse \(C>0\)だけを変える。
予備的なexact algebraから得た整数幅1のbracketを、実装前に

\[
C_- = 173791195571,\qquad C_+ = 173791195572
\]

へ固定する。`Fraction` arithmeticで \(C_-\)がpass、\(C_+\)がfailすることを再現する。
独立な整数二分探索は初期区間 \([1,10^{13}]\)から開始し、結果後に端点を変更しない。

残差tailを \(T>0\)、quartic center stateを \(s\)、zero-inverse時のreduced-range
bufferを \(b_0>0\)とすると、

\[
\begin{aligned}
x(C)&=s+2CT,\\
b(C)&=b_0-\frac{2CT}{c_V},\\
D(C)&=\frac{21}{2}\{(1-x(C))^{-2}-1\}
 +\frac{g(r_*)+2CT/c_V}{b(C)}
 +\frac{h(r_*)+2CT}{c_Vb(C)},\\
Z(C)&=C D(C).
\end{aligned}
\]

positive domainでは各項が非減少で、\(Z(C)\)はstrictに増加する。domainを外れればcandidateは
定義通りfailである。従って \(C_+\)で \(Z>1/2\)なら全 \(C\ge C_+\)がfailする。
またcorrection radiusを\(\tau=2CT\)とするQ007n radii marginは
\(CT(1-2Z)\)なので、\(T,C>0\)では同じthresholdになる。この単調性を係数の符号と
両端のexact recordから監査する。

### radius stepに必要なexternal gap

Q007ad norm formulaを固定すると

\[
C_{\rm ext}^{\rm raw}(\delta)=\frac{81\beta_*}{\delta},\qquad
C_{\rm ext}^{\rm work}\ge C_{\rm ext}^{\rm raw}.
\]

従って \(10^{-15}\) candidateがpassするためには \(C_{\rm total}<C_+\)が必要で、

\[
\delta>\delta_{\rm req}:=\frac{81\beta_*}{C_+}
 \simeq 2.546402442702229\times10^{-8}
\]

が必要である。ここではroot自体をfloat最適化せず、fail側のexact整数端点から必要条件だけを使う。

### 固定obstruction witness

Q007adのminimum-margin witnessを変更せず使用する。

- degree: `71`
- counts: `(24,38,2,7)`
- acoustic split: `(12,12,1,1)`
- target: `wave=(-7,-7);eigenvalue_index=6`

artifactに保存されたproduct centerとtarget centerからexact squared center distanceを再計算し、
product uncertaintyとexternal radiusもexactに再現する。100桁integer-`isqrt` enclosureの
上端を用いて、このcomparisonが許せるgapの楽観的上限を

\[
\delta_{\rm witness}^+
=\sqrt{d^2}^{\, +}-\epsilon_{\rm product}-r_{\rm external}
\]

とする。Q007adに保存されたlower側
`2.4028364427409988e-8`だけで不可能性を推論せず、必ずsqrt upper側を使う。
判定は

\[
\delta_{\rm witness}^+<\delta_{\rm req},\qquad
\frac{\delta_{\rm witness}^+}{\delta_{\rm req}}<0.95
\]

とする。この一対がfailすれば、同じQ007ad disc比較族では必要gapを一様に認証できないため、
全287,929 comparisonの再探索は行わない。

### validity gate

1. 3 artifact SHA、5 implementation／runner SHA、source、scope、Q007ad／Q007ae accepted
   outcomeと封印digestが一致する。
2. Q007n coefficient、selected radius、\(\beta_*\)、Q007ae inverse orderingをexact再現し、
   Q007aeの119 candidate recordsがbitwiseに一致する。
3. \([1,10^{13}]\)のinteger bisectionが完全に終了し、唯一の幅1 bracket
   \((C_-,C_+)\)を再現する。
4. \(T>0\)、全必要係数の非負性、両端のpositive domain、\(Z(C_-)<1/2<Z(C_+)\)、
   radii-margin符号をexactに確認する。
5. Q007ad witness identifier、counts、center distance、uncertainty、radiusを再現し、
   sqrt enclosure幅が \(10^{-100}\)以下である。
6. 全数値がfinite strict JSONで、input／result digestを再現する。

一つでも落ちれば`inconclusive`とし、obstructionを主張しない。

### hypothesis gateと停止規則

validity通過時だけ次を判定する。

1. \(C_-\)がpassし \(C_+\)がfailし、fail理由がpositive domain内の
   \(Z>1/2\)およびnegative radii marginである。
2. exact単調性監査により、全 \(C\ge C_+\)がfailする。
3. \(\delta_{\rm witness}^+<\delta_{\rm req}\)で、ratioが`0.95`未満、
   absolute shortfallが`1.4e-9`より大きい。
4. \(\,81\beta_*/\delta_{\rm witness}^+>C_+\)で、そのratioが`1.05`を超える。
5. Q007aeの`1e-16 pass / 1e-15 fail`を維持し、Q007p--Q007abのtube／MPFR
   constantsを変更しない。

全て通れば
`sealed external phase-disc family cannot certify the 1e-15 radius step`
というnegative obstructionを`accepted`とする。validity通過後に一つでも落ちれば
`sealed witness does not obstruct the 1e-15 radius step`という有効な
`not_certified`とする。bracket、witness、sqrt precision、ratio thresholdを結果後に変更しない。

### 主張境界

acceptedでも、真のspectral separationや真の解析半径が \(10^{-15}\)未満だとは主張しない。
証明するのは、Q007n scalar majorant、Q007ad original asymmetric discs、Q007ad norm formulaを
同時に固定したcertificate familyでは次の10進radiusへ届かないことだけである。別のwave-sum
selection rule、別norm、blockwise majorant、より高次chart、別spectral enclosureなら結論は変わり得る。
continuous optimal radius、Q007p--Q007ab tube enlargement、Euclidean／grid-uniform attraction、
global basin、境界、外力、D3Q27は認証しない。

### Q007af 封印結果

validity 6件、hypothesis 5件が全て通過し、
`sealed external phase-disc family cannot certify the 1e-15 radius step`
というnegative obstructionを`accepted`とした。

- sealed artifact input: Q007n／Q007ad／Q007ae `3 / 3` pass
- sealed implementation source: Q007ac／Q007ad／Q007ae／Q007n／Q007o
  `5 / 5` pass
- Q007ae candidate records exact reproduction: `119 / 119`
- integer bisection iteration: `44`
- maximum passing／minimum failing inverse:
  `173791195571 / 173791195572`
- passing／failing \(Z\):
  `0.4999999999994811 / 0.5000000000023581`
- passing／failing radii margin:
  `9.35528407264837e-68 / -4.2513570828920896e-67`
- necessary external gap lower:
  `2.546402442702229e-8`
- Q007ad witness allowable gap upper:
  `2.4028364427409988e-8`
- allowable／required ratio、absolute shortfall:
  `0.9436200666659436 / 1.4356599996123017e-9`
- required gapでのexact squared margin:
  `-7.109332998428586e-17`
- optimistic raw external inverse floor／failing-endpoint ratio:
  `1.841749679890231e11 / 1.059748552755201`
- input／result digest:
  `6cfeabe16a18fdb6de08e67c575a0b0db2f3ab1341c35c434faff100fd959255` /
  `3d210cf25513e373ac6a2e7a276163998a602c529878f3c95f085c9e0625bfdd`
- integer-bisection digest:
  `24b0e993f676082579158cfeddfe74009161d72412bf228f715baa396246c31b`
- runner SHA-256:
  `819679b22d7552a3f247d7c3389a83890f56c60522154bdb5ea05d7eb77a48a4`
- artifact newline-normalized SHA-256:
  `a686526552c33f5f1f01a9f1d9c49036d1c9491a2092b07ac8c8621a33d4ada1`

単調性監査により、positive domainで \(Z(C)\)はstrictに増加し、domain外ではbuffer gateが
failするため、`173791195572`以上のinverseは全て`1e-15` candidateをfailさせる。
一方、Q007adの固定witnessは100桁sqrt upperを使っても必要gapへ届かず、threshold roundingなしでも
直接failした。従って同じoriginal-disc familyのgap micro-sharpeningはここで停止する。

これは真のspectral separationやanalytic radiusの上限ではない。wave-sum restriction、blockwise
majorant、別norm、より高次chart、別spectral enclosureは排除していない。Q007aeの
`1e-16 pass / 1e-15 fail`とQ007p--Q007abのtube／MPFR constantsは変更しない。
次は、認証済み`1e-16` chart domainを使うQ007p-style downstream tube再監査を
別gateとして事前登録する。構造的に異なるexternal certificateは、その後も独立候補として残す。

## Q007ag: Q007ae analytic radiusのfinite-tube伝播 — 事前登録

### 問いと固定scope

Q007p／Q007sのfinite-tube majorantでanalytic chart radiusとcorrection-pair boundだけを
Q007aeのaccepted `1e-16` boundaryへ更新すると、Q007sで認証した
\((r,\zeta)=(9\times10^{-19},5\times10^{-12})\)を両方向へstrictに拡大できるかを問う。
固定scopeは \(17^2\)、\(\omega=3/2\)、\(\eta=1/100\)、
\(\delta M=\delta P_x=\delta P_y=0\)、Q007p external-coordinate block-sum \(\ell^1\) norm、
Q007n quartic-centered exact manifoldとする。

封印入力は次の4 artifactとrunnerである。

- Q007p artifact／runner SHA-256:
  `a5e766938cfee0174deba9c529be9aec2cce4bff9225a3a4a1da83f7d255a751` /
  `23ff283acb3f872fd2ff489f17d94b8e022e3f45a5c65b5523bf976c534a9f2a`
- Q007s artifact／runner SHA-256:
  `7b70fd20df8fb7db5e5460a08d3f86fe8b81a55b56864c860a2c24e9cab63292` /
  `6c8633f7e99874ac3be7dd14d3caa253b0dc8c499bb2f6edbb392fa695975b1e`
- Q007ae artifact／runner SHA-256:
  `c6d28bba13fcf831dfccaf03854072256f7e8ff1a241b54aaf84552dd06a2a55` /
  `f2e0d90ae6bb5f9694c799d2ea850a014f66f2ab9681d94dc1c850cc753db600`
- Q007af artifact／runner SHA-256:
  `a686526552c33f5f1f01a9f1d9c49036d1c9491a2092b07ac8c8621a33d4ada1` /
  `819679b22d7552a3f247d7c3389a83890f56c60522154bdb5ea05d7eb77a48a4`
- Q007ae radius recordsの再生成に直接使うQ007n／Q007o implementation SHA-256:
  `6eefae3386e5c49f151b1cd4537eb84fbb92858578fe4fce7768e50ad43c5dc9` /
  `d34afda382784610ea2b8997e6c44376188b02c42668ade8e2d53ff9bc9afea7`

Q007s old 891 candidate、passing count `676`、candidate digest
`91fcc70355acfc4b7163c951227188960ef275408b06a678d45d5e4ec4c85300`、
selected candidateと全gateをexact再現してから新しい評価へ進む。Q007aeのinput／result／phase／
selected-center digestとQ007afのinput／result／integer-bisection digestも再現する。

### 変更する2定数

Q007pから保存された13 coefficient、selected spectral bounds、nonlinear constant、
linear external contraction \(q_0\)、synthesis／analysis／selected-analysis constants、
normal／domination capを変更しない。変更するのは

\[
\rho_{\rm old}=10^{-18}
\longrightarrow
\rho_{\rm ag}=10^{-16}
\]

と、対応するQ007ae exact boundaryの

\[
\tau_{\rm old}=2.8490986842816327\times10^{-68}
\longrightarrow
\tau_{\rm ag}=2.186110822784426\times10^{-60}
\]

だけである。どちらもQ007ae
`internal_phase_refined_radius_search.exact_boundary_certificate.selected`
からexact fractionとして読む。Q007aeの全119 recordを再生成して、selected
`1e-16 pass / 1e-15 fail`と \((\rho_{\rm ag},\tau_{\rm ag})\)を照合する。

### 固定candidate grid

Q007sのanalytic radiusが100倍になったことに合わせ、base gridだけをexactに100倍する。

\[
r_m=m\times10^{-17},\qquad m=1,\ldots,9.
\]

normal gridはQ007sと同じ

\[
\zeta_{m,e}=m\times10^{-e},
\qquad m=1,\ldots,9,\quad e=10,\ldots,20
\]

のunique 99値を使う。従ってcandidateは \(9\times99=891\) 個である。selection ruleはQ007sと
同じく、全6 gateを通る点の中でbase radius、次にnormal radiusをlexicographicに最大化する。
結果後にgrid、cap、selection ruleを変更しない。

予備的exact evaluationから得たselection boundaryを実装前に次へ固定する。

- passing candidate count: `757`
- canonical candidate digest:
  `a7a6a8f605339b0e8ffd16a5d3190967cb7329771d322f8edc0a53bc4b45e408`
- selected:
  \((r_{\rm ag},\zeta_{\rm ag})=(9\times10^{-17},5\times10^{-11})\)
- Q007s selectedからのimprovement:
  `100 / 10`
- selected base sliceのfirst larger normal:
  \(6\times10^{-11}\)、`base_forward_invariance`だけがfail

base gridの上端を選ぶため、これはcontinuous maximum base radiusの主張ではない。

### exact candidate formula

Q007sの`_evaluate_candidate`をそのまま使う。

\[
\begin{aligned}
w(r)&=c_Vr+\tau+h_2r^2+h_3r^3+h_4r^4,\\
r_R(r)&=\lambda_*r+\tau/c_V+g_2r^2+g_3r^3+g_4r^4,\\
x(r,\zeta)&=w(r)+K_s\zeta,\\
a_+(r,\zeta)&=r_R(r)+K_L\,dN(x)\,K_s\zeta,\\
q_*(r,\zeta)&=q_0+K_aK_s\,dN(x)
 \{1+K_LdH(a_+)\}.
\end{aligned}
\]

全candidateについて次の6 gateをexact `Fraction` signsで判定する。

1. \(0<r<\rho_{\rm ag}\)
2. \(0\le x<1\)
3. \(a_+<r\)
4. \(q_*<0.99\)かつ \(q_*\zeta<\zeta\)
5. selected tangent conorm \(m_T>0\)
6. \(q_*/m_T<0.999\)

### validity gate

1. 4 artifact／runner SHA、source、scope、accepted outcome、封印digestが一致する。
2. Q007s old audit、891 candidate、676 passing、digest、selected boundaryをexact再現する。
3. Q007ae 119 radius records、accepted boundary、\(\rho_{\rm ag}\)、\(\tau_{\rm ag}\)をexact再現する。
4. \(\rho,\tau\)以外のQ007p／Q007s定数がbitwise不変で、Q007s selected controlがnew constantsでもpassする。
5. 9 unique base、99 unique normal、891 Cartesian candidateを重複なく生成し、
   全6 gateとfixed selectionをexactに完走する。
6. 全数値がfinite strict JSONで、input／candidate／result digestを再現する。

一つでも落ちれば`inconclusive`とし、新tubeを採用しない。

### hypothesis gateと停止規則

validity通過時だけ次を判定する。

1. passing countが`757`、candidate digestが登録値と一致する。
2. selected candidateがexactに
   \((9\times10^{-17},5\times10^{-11})\)で、全6 gateをstrictに通る。
3. Q007s selectedに対するbase／normal improvementがexactに`100 / 10`である。
4. selected sliceで全larger normalがfailし、first larger
   \(6\times10^{-11}\)は`base_forward_invariance`だけをfailする。
5. selected candidateで \(q_*<0.99\)、\(m_T>0\)、\(q_*/m_T<0.999\)がstrictである。

全て通れば
`Q007ae analytic radius enlarges the registered external-coordinate tube`
として`accepted`とする。validity通過後に一つでも落ちれば
`registered scaled grid did not propagate the Q007ae analytic radius to both tube radii`
という有効な`not_certified`とする。

### 主張境界

acceptedでも固定scaled grid上の一候補だけを認証する。continuous optimum、maximum tube、
Euclidean／grid-uniform attraction、global basin、continuum limitは示さない。Q007t／Q007uの
exact positivity、Q007v--Q007abのbinary64／MPFR／repair／forward-shadowingはQ007s old tubeに
封印された別certificateなので、新tubeへ自動拡張しない。new tubeのpopulationおよびstagewise
positivityは次の別gateとする。Q007c1 finite-amplitude rejection、Q007d Euclidean rejection、
Q007af external-disc obstruction、Q010 TT cost rejectionは変更しない。

### Q007ag 封印結果

validity 6件、hypothesis 5件が全て通過し、
`Q007ae analytic radius enlarges the registered external-coordinate tube`
として`accepted`とした。

- sealed artifact／runner input: Q007p／Q007s／Q007ae／Q007af `4 / 4` pass
- sealed implementation source: Q007n／Q007o／Q007p／Q007s／Q007ae／Q007af
  `6 / 6` pass
- Q007s old candidate／pass reproduction: `891 / 676`
- Q007ae radius records exact reproduction: `119 / 119`
- new candidate／passing count: `891 / 757`
- selected base／normal radius:
  `9e-17 / 5e-11`
- Q007s selectedからのbase／normal improvement: `100 / 10`
- selected state Wiener upper: `1.4441361143956586e-10`
- selected base image／forward margin:
  `8.995021185299983e-17 / 4.978814700017615e-20`
- selected normal contraction／tangent conorm／domination ratio:
  `0.9817100978829438 / 0.9837709569923392 / 0.9979051433722989`
- selected strict analytic／population-domain margins:
  `1e-17 / 0.9999999998555864`
- selected normal-cap／domination-cap margins:
  `0.008289902117056176 / 0.001094856627701151`
- first larger normal `6e-11`のbase forward margin:
  `-2.4132428529856413e-19`（`base_forward_invariance`だけfail）
- input／candidate／result digest:
  `262cbeccacf858bd798de06f363635f15c78ff3d361b44bdd5850aeb90679613` /
  `a7a6a8f605339b0e8ffd16a5d3190967cb7329771d322f8edc0a53bc4b45e408` /
  `6f52c6f1cfa618ca881439504f1bd5b46e45eb245670f1a2c6341669aa024f43`
- runner SHA-256:
  `bafd9a56d2d2ceb94acb709609bd710c9fff0f6c0bf543202fa411b9456fb6e0`
- artifact newline-normalized SHA-256:
  `5783df74abb4b6ec7d658fd7e3dd272cf100cd134783c31863d643fcd17d4200`

Q007aeの`1e-16` boundaryへ更新したのは\(\rho,\tau\)だけであり、他のQ007p／Q007s
majorant定数はbitwiseに維持した。固定scaled grid上ではbase半径を100倍、normal半径を10倍に
同時拡大できた。選択base sliceの次のnormal候補はbase forward invarianceだけをfailした。

これはcontinuous optimum、maximum tube、Euclidean／grid-uniform attraction、global basin、
continuum limitの主張ではない。Q007t／Q007uのexact positivityとQ007v--Q007abの
binary64／MPFR／repair／forward-shadowingは旧Q007s tubeに封印されている。次はQ007ag selected
tubeのfull-map population positivityを一つの独立gateとして事前登録し、その後にstagewise
positivityを別gateで扱う。

## Q007ah: Q007ag selected tubeのfull-map population positivity — 事前登録

### 問いと固定scope

Q007agで認証した

\[
\|a\|_1\le9\times10^{-17},\qquad
\|z\|_*\le5\times10^{-11}
\]

のforward-invariant tubeは、full one-step mapの入力／出力時刻でD2Q9の全9 populationと
densityがstrict positiveとなる領域へ含まれるかを問う。固定scopeはQ007agと同じ
\(17^2\)、\(\omega=3/2\)、\(\eta=1/100\)、固定mass／momentum leaf、Q007ae exact
graph-gauge manifold、Q007p Fourier external-coordinate block-sum \(\ell^1\) normとする。

このgateではexact full-map sampling timeだけを扱う。equilibrium evaluation、BGK collision、
streaming、filter各段階のpositivityは扱わず、通過時にも次のQ007aiへ残す。

### 封印入力

- Q007ag artifact／runner SHA-256:
  `5783df74abb4b6ec7d658fd7e3dd272cf100cd134783c31863d643fcd17d4200` /
  `bafd9a56d2d2ceb94acb709609bd710c9fff0f6c0bf543202fa411b9456fb6e0`
- Q007t old-tube population oracle artifact／runner SHA-256:
  `2089d97aa19248cc17689f3e7a01e113540e5afc329ffa5cb3a4c511a43a8529` /
  `1e00281c71b5ea5d06fedcebd9bd483a73e6ec111388df20e8255ae3aefed877`
- transitive Q007p artifact／runner SHA-256:
  `a5e766938cfee0174deba9c529be9aec2cce4bff9225a3a4a1da83f7d255a751` /
  `23ff283acb3f872fd2ff489f17d94b8e022e3f45a5c65b5523bf976c534a9f2a`

訂正記録: 事前登録直後の最初のinput-only実装監査で、Q007t artifactに当初記した
`de5ee6db33e06459c64e5cea92b206673938d5f8d6fef948e5b4496dcca92283`がraw-byte SHA-256であり、
この研究でartifact provenanceに用いるnewline-normalized SHA-256ではないことを検出した。
既存Q007t封印結果、Q007u input、研究ログに保存済みのnewline-normalized値`2089...`へ、
Q007ahのvalidityがfailした状態のまま、hypothesis結果を採用する前に訂正した。ファイル内容、runner、
数値bound、成功条件は変更していない。

Q007agについてscope、accepted classification、validity `6 / 6`、hypothesis `5 / 5`、
input／candidate／result digest、selected candidate、全6 candidate gate、forward-invariance theoremを
照合する。Q007tについてもscope、accepted classification、validity `5 / 5`、hypothesis `3 / 3`、
3 theorem flag、D2Q9 weight table、Q007s old tube boundsをexactに再現する。

### exact positivity bound

Q007ag selected stateの保存exact Wiener upperを

\[
x_{\rm ag}=1.4441361143956586\times10^{-10}
\]

とする。artifactのbase-16 numerator／denominatorから`Fraction`を復元し、丸めた表示値は符号判定に
使わない。inverse Fourier conventionと位相の絶対値1から、各格子点・各populationについて

\[
|\delta f_i(x)|\le
\max_i\sum_k|\widehat{\delta f_i}(k)|
\le \sum_{k,i}|\widehat{\delta f_i}(k)|
\le x_{\rm ag}
\]

を使う。D2Q9 rest equilibriumの最小weightはexactに\(1/36\)、densityは1なので、

\[
p_{\rm ag}=\frac1{36}-x_{\rm ag},\qquad
d_{\rm ag}=1-x_{\rm ag}
\]

をexactに評価する。事前登録値は

- population lower: `0.027777777633364167`
- density lower: `0.9999999998555864`
- population upper: `0.44444444458885807`

である。

### validity gate

1. Q007ag／Q007t／Q007p artifactとrunner SHA、package source、scope、schema、sealed outcomeが一致する。
2. Q007ag selected \((r,\zeta)\)、state upper identity、全6 candidate gate、forward invarianceをexact再現する。
3. Q007t old oracleのweight table、Wiener norm argument、old exact positivity bounds、全gateを再現する。
4. 現行D2Q9 velocity／weight tableを`Fraction`へ変換し、multiplicity `1 / 4 / 4`、sum 1、
   minimum \(1/36\)、全weight strict positiveを再構成する。
5. Q007pの289 wave、norm definition、real conjugacy constraintを直接読み、componentwise physical
   population boundへ移るtriangle inequalityの前提を照合する。
6. 全数値がfinite strict JSONで、canonical input／result digestを再現する。

一つでも落ちれば`inconclusive`とし、positivityを採用しない。

### hypothesis gateと停止規則

validity通過時だけ次を判定する。

1. \(d_{\rm ag}=1-x_{\rm ag}>0\)。
2. \(p_{\rm ag}=1/36-x_{\rm ag}>0\)。
3. Q007ag tubeがforward invariantであり、同じstrict lower boundを全full-map iterateへ帰納できる。

全て通れば
`registered Q007ag propagated tube lies in the strictly positive population cone at every full-map iterate`
として`accepted`とする。validity通過後に一つでも落ちれば
`registered Q007ag propagated tube did not certify strict full-map population positivity`
という有効な`not_certified`とする。

### 主張境界

acceptedでも、固定Q007ag tube内のreal stateに対するexact full-map入力／出力時刻だけの結論である。
equilibrium／collision／streaming／filter stage、entropy、monotonicity、maximum principle、IEEE-754
roundoff、Q007v--Q007ab有限精度帰納、continuous optimum、global basin、grid-uniformity、continuum
limitは認証しない。Q007c1 finite-amplitude rejection、Q007d Euclidean rejection、Q007af
external-disc obstruction、Q010 TT cost rejectionは変更しない。acceptedなら次にQ007aiとして、同じ
Q007ag tube上のexact stagewise positivityを独立に事前登録する。

### Q007ah 封印結果

validity 6件、hypothesis 3件が全て通過し、
`registered Q007ag propagated tube lies in the strictly positive population cone at every full-map iterate`
として`accepted`とした。

- sealed Q007ag／Q007t／Q007p inputs: `3 / 3` pass
- Q007ag stored cycle／3 digest fresh reproduction: pass
- Q007t old population oracle fresh reproduction: pass
- D2Q9 weight multiplicities／sum／minimum: `1 / 4 / 4`、`1`、`1/36`
- Fourier wave count／Q007p norm audit: `289 / pass`
- selected base／normal radius: `9e-17 / 5e-11`
- exact tube population deviation upper: `1.4441361143956586e-10`
- exact population lower／upper:
  `0.027777777633364167 / 0.44444444458885807`
- exact density lower: `0.9999999998555864`
- input／result digest:
  `6d7bd69b5c90ff7dbabd5193a4536809f4b79eef36a41fb288ab7caec44321b4` /
  `caea5280667e909f17922260ef0d78998b6a8b374cd048b4b3e526185f040921`
- runner SHA-256:
  `f29a974f0219af1767140e977775aa95dcf22b41a36de7a97bb553d540968d27`
- artifact newline-normalized SHA-256:
  `cab5ecc090b794a21a21fded8e5c503eca40be2bbc6502767c29844ba8209fa9`

最初のinput-only実装監査ではQ007t artifactのraw-byte SHAを事前登録したためvalidityがfailし、
hypothesisを採用せず停止した。既存ログに封印済みのnewline-normalized SHAへ訂正した後、全入力、
fresh replay、exact boundが通過した。科学的入力、数値bound、成功条件は変更していない。

Q007ag forward invarianceにより、population／density lowerはexact full-mapの全入力／出力時刻へ
帰納できる。しかしequilibrium／collision／streaming／filter stageのpositivityはまだ認証していない。
次はQ007aiとして同じQ007ag tubeのexact stagewise positivityだけを事前登録する。Q007v--Q007abの
binary64／MPFR／repair／forward-shadowing再監査はQ007ai通過後まで開始しない。

## Q007ai: Q007ag selected tubeのexact stagewise positivity — 事前登録

### 問いと固定scope

Q007ahでfull-map入力／出力時刻のpositivityを認証したQ007ag selected tubeについて、exact
equilibrium evaluation、BGK collision output、periodic streaming output、five-point filter outputの
全内部stageでも全9 populationがstrict positiveかを問う。

固定scopeは\(17^2\)、\(\omega=3/2\)、\(\eta=1/100\)、固定mass／momentum leaf、
Q007ae exact graph-gauge manifold、Q007p external-coordinate norm、
\((r,\zeta)=(9\times10^{-17},5\times10^{-11})\)とする。exact mathematical mapだけを扱い、
IEEE-754 roundoff enclosureは含めない。

### 封印入力と実装

- Q007ah artifact／runner SHA-256:
  `cab5ecc090b794a21a21fded8e5c503eca40be2bbc6502767c29844ba8209fa9` /
  `f29a974f0219af1767140e977775aa95dcf22b41a36de7a97bb553d540968d27`
- Q007u old-tube stagewise oracle artifact／runner SHA-256:
  `b568fc304fd939121dd52543f316cb571ae6f4be4f4f664c68fe1c749b566c55` /
  `56fc99f1f381e97e70710c7da0cee8d1262d0c10190cf617316f822d1eb29014`
- current D2Q9 implementation SHA-256:
  `6e6c5aa6734844d0393eb402e21203831faaf5f325b35249941eaa59145c6f53`
- current checkerboard-filter implementation SHA-256:
  `5fb6b67e8527b0b1f5f45511ba7cd5d077ee443220632ba3019b7bf28010a7ea`

Q007ahのstored cycle、input／result digest、Q007ag tube reuse、6 validity gate、3 hypothesis gate、
full-map theoremをfresh replayする。Q007uもstored cycle、6 validity gate、5 hypothesis gate、5 theorem
flag、linear／nonlinear／streaming／filter boundをfresh replayする。結果後にoperator norm、nonlinear
constant、filter、stage orderを変更しない。

### exact stage majorant

Q007ahからexact fractionとして

\[
x_{\rm ag}=1.4441361143956586\times10^{-10}
\]

を読む。Q007uと同じexact D2Q9 operatorを再構成し、

\[
\|EM\|_1=\frac{13}{6},\qquad
\|C\|_1=\frac{19}{6}
\]

および

\[
\|N_{\rm eq}\|_{\rm W}\le7\frac{x_{\rm ag}^2}{1-x_{\rm ag}},
\qquad
\|N_{\rm coll}\|_{\rm W}\le\frac{21}{2}\frac{x_{\rm ag}^2}{1-x_{\rm ag}}
\]

を使う。stage deviation upperを

\[
e_{\rm ag}=\frac{13}{6}x_{\rm ag}+7\frac{x_{\rm ag}^2}{1-x_{\rm ag}},
\qquad
c_{\rm ag}=\frac{19}{6}x_{\rm ag}+\frac{21}{2}\frac{x_{\rm ag}^2}{1-x_{\rm ag}}
\]

とし、population lowerを

\[
p_{\rm eq}=\frac1{36}-e_{\rm ag},\qquad
p_{\rm coll}=\frac1{36}-c_{\rm ag}
\]

とする。periodic streamingは各populationのbijection、filterは係数
\((99/100,1/400,1/400,1/400,1/400)\)の凸結合なので、
\(p_{\rm stream}=p_{\rm filter}=p_{\rm coll}\)とする。

事前登録した表示値は次のとおりで、符号判定にはexact fractionだけを使う。

- density denominator lower: `0.9999999998555864`
- equilibrium／collision nonlinear remainder:
  `1.459870382042079e-19 / 2.1898055730631184e-19`
- equilibrium deviation／population lower:
  `3.1289615826504644e-10 / 0.02777777746488162`
- collision deviation／population lower:
  `4.5730976977760583e-10 / 0.027777777320468006`
- streaming／filter population lower:
  `0.027777777320468006 / 0.027777777320468006`

### validity gate

1. Q007ah／Q007u artifactとrunner SHA、source、scope、schema、accepted outcome、全sealed gateが一致する。
2. Q007ah stored cycle、2 digest、selected tube、state identity、forward invarianceをfresh replayする。
3. Q007u old stagewise oracleのstored cycle、operator／majorant／stage structure、exact boundsをfresh replayする。
4. exact \(M,E,EM,C\)がcurrent rational mapと一致し、induced \(\ell^1\) norm \(13/6,19/6\)を再現する。
5. nonlinear constants \(7,21/2\)、17² streamingの9 bijection、sum-one nonnegative filter、
   current wrapped compositionを再現する。
6. 全boundがfinite strict JSONで、canonical input／result digestを再現する。

一つでも落ちれば`inconclusive`とし、stage lowerを採用しない。

### hypothesis gateと停止規則

validity通過時だけ次を判定する。

1. equilibrium evaluation: \(p_{\rm eq}>0\)。
2. post-collision: \(p_{\rm coll}>0\)。
3. post-streaming: 9 population-wise permutationが\(p_{\rm coll}\)を保持する。
4. post-filter: nonnegative sum-one filterが\(p_{\rm coll}\)を保持する。
5. all-iterate: Q007ag forward invarianceにより同じ4 stage boundを全iterateへ再適用できる。

全て通れば
`registered Q007ag propagated tube is population-positive at every exact BGK, streaming, and filter stage`
として`accepted`とする。validity通過後に一つでも落ちれば
`registered Q007ag propagated tube did not certify exact stagewise population positivity`
という有効な`not_certified`とする。

### 主張境界

acceptedでもfixed Q007ag tube上のexact mathematical stagesだけの結論である。NumPy／IEEE-754の
各中間加算、乗除算、実装定数を外向きroundoff intervalで囲わない。entropy、monotonicity、maximum
principle、Q007v--Q007ab有限精度帰納、continuous optimum、global basin、grid-uniformity、continuum
limitは認証しない。既存のQ007c1／Q007d／Q007af／Q010結論も変更しない。acceptedなら次はQ007ajで、
このnew tubeに対する現行binary64 one-step stage enclosureを独立に事前登録する。

### Q007ai 封印結果

validity 6件、hypothesis 5件が全て通過し、
`registered Q007ag propagated tube is population-positive at every exact BGK, streaming, and filter stage`
として`accepted`とした。

- sealed Q007ah／Q007u inputs: `2 / 2` pass
- D2Q9／checkerboard-filter implementation SHA: `2 / 2` pass
- Q007ah stored cycle／2 digest fresh reproduction: pass
- Q007u old stagewise oracle fresh reproduction: pass
- exact equilibrium／collision induced \(\ell^1\) norm: `13/6 / 19/6`
- exact equilibrium／collision nonlinear constant: `7 / 21/2`
- input state Wiener upper: `1.4441361143956586e-10`
- density denominator lower: `0.9999999998555864`
- equilibrium nonlinear／deviation／population lower:
  `1.459870382042079e-19 / 3.1289615826504644e-10 / 0.02777777746488162`
- collision nonlinear／deviation／population lower:
  `2.1898055730631184e-19 / 4.5730976977760583e-10 / 0.027777777320468006`
- post-streaming／post-filter lower:
  `0.027777777320468006 / 0.027777777320468006`
- input／result digest:
  `0dff47e8b0ed6e9b87cb73e6dea20192088495b51283c57b9d58630b7344c6a3` /
  `c101313957c738ccee9fd3d7f1ed36b77c6f3dad4e1130651f5be4d8757ef18a`
- runner SHA-256:
  `3235b2dc31445e5912f2aaf7fc080e8295035801ade9b27d3f683d34da61173d`
- artifact newline-normalized SHA-256:
  `3ce5fa6358eaa6f3a64f93fe773e3fbc1990abfb83886aad1a4ade9c82425804`

従って固定Q007ag tube内の全real stateについて、exact equilibrium evaluation、BGK collision、
periodic streaming、five-point filterの各出力で全9 populationがstrict positiveである。Q007ag forward
invarianceにより同じstage boundを全iterateへ再適用できる。

これはexact mathematical mapの結論であり、NumPy／IEEE-754中間演算を外向きroundoff intervalで
囲っていない。次はQ007ajで同じnew tubeに対するcurrent binary64 one-step stage enclosureを独立に
監査する。all-iterate finite-precision re-entryは同じgate内でもstage positivityと分けて判定する。

## Q007aj: Q007ag selected tubeのcurrent binary64 one-step enclosure — 事前登録

### 問いと固定scope

Q007aiでexact stagewise positivityを認証したQ007ag selected tubeについて、current NumPy
implementationのbinary64 equilibrium evaluation、BGK collision output、periodic streaming output、
five-point filter outputを、Q007vと同一のFraction-based outward forward-error modelで一段階だけ
包囲したとき、全stageのpopulation lowerがstrict positiveかを問う。同時に、post-filter roundoff
errorをQ007p Fourier coordinateへ戻したupperがQ007agのbase／normal forward-invariance marginへ
収まるかを別々に判定する。

固定scopeは\(17^2\)、\(\omega=3/2\)、\(\eta=1/100\)、固定mass／momentum leaf、
Q007ae exact graph-gauge manifold、Q007p Fourier external-coordinate block-sum \(\ell^1\) norm、
\((r,\zeta)=(9\times10^{-17},5\times10^{-11})\)とする。inputはexact real tube stateを
correctly rounded binary64へencodeしたものとし、round-to-nearest ties-to-even、unit roundoff
\(u=2^{-53}\)、subnormal fallback \(h=2^{-1075}\)を固定する。FTZ／DAZ、GPU kernel、BLAS変更、
compiler fast-math、非標準roundingは扱わない。

### 封印入力と実装

- Q007ag artifact／runner SHA-256:
  `5783df74abb4b6ec7d658fd7e3dd272cf100cd134783c31863d643fcd17d4200` /
  `bafd9a56d2d2ceb94acb709609bd710c9fff0f6c0bf543202fa411b9456fb6e0`
- Q007ai artifact／runner SHA-256:
  `3ce5fa6358eaa6f3a64f93fe773e3fbc1990abfb83886aad1a4ade9c82425804` /
  `3235b2dc31445e5912f2aaf7fc080e8295035801ade9b27d3f683d34da61173d`
- Q007v old-tube binary64 oracle artifact／runner SHA-256:
  `c4c1c45941a6f6ac302691efd8e795e431f6acc1fa4f4629cb0c7a0afac3c0a5` /
  `a0d3cea0fcae8a627f4a96db56d46727589411b2557e2aa91433569576a0575c`
- current D2Q9 implementation SHA-256:
  `6e6c5aa6734844d0393eb402e21203831faaf5f325b35249941eaa59145c6f53`
- current checkerboard-filter implementation SHA-256:
  `5fb6b67e8527b0b1f5f45511ba7cd5d077ee443220632ba3019b7bf28010a7ea`

Q007agはstored cycle、3 digest、6 validity gate、5 hypothesis gate、selected candidateとその6 strict
gate／margin、forward invariance theoremをfresh replayする。Q007aiはstored cycle、2 digest、6 validity
gate、5 hypothesis gate、exact stage boundsとall-iterate exact-stage theoremをfresh replayする。Q007vは
stored cycle、7 validity gate、binary64 model、primitive interval arithmetic、83 multiplicationを含む固定
operation schedule、source schedule、deterministic NumPy replay、および「old tubeではone-step acceptedだが
robust re-entryはnot certified」という分離結果をfresh replayする。Q007vのoverall `not_certified`を
invalid inputとは扱わず、全validity gate通過と封印された分離結果の一致を要求する。

### binary64 stage enclosureとre-entry bound

Q007ag／Q007aiから同一のexact fractionとして

\[
x_{\rm ag}=1.4441361143956586\times10^{-10}
\]

を読み、各site／population inputを

\[
f_i\in[w_i-x_{\rm ag},w_i+x_{\rm ag}]
\]

で包囲する。Q007vのpaired quantity \((I,e)\)と同一の演算順序を用い、各binary64基本演算後に
\(u|x|+h\)を加える。streamingはpopulation-wise `np.roll` permutationなので新しい算術誤差を
加えず、filterまでのtarget intervalとforward-error upperをexact Fractionで計算する。各stage lowerは

\[
p_s^{64}=\min_i\{\inf I_{s,i}-e_{s,i}\}
\]

とする。Q007vの登録operation countが一件でも変わればvalidity failureであり、新しいscheduleへ
結果を合わせない。

post-filterのcomponent error upper \(e_i^{\rm filt}\)から

\[
\epsilon_W=17^2\sum_{i=0}^{8}e_i^{\rm filt},\qquad
\epsilon_B=K_B\epsilon_W,\qquad
\epsilon_N=K_N\epsilon_W
\]

を作る。\(K_B,K_N\)はQ007vで封印したQ007p selected／external analysis upperを変更せず再利用する。
比較対象はQ007ag selected candidateのexact strict margin

- base forward-invariance margin: `4.978814700017615e-20`
- normal-tube forward-invariance margin: `9.144951058528087e-13`

とする。等号は不合格とし、baseとnormalを独立に判定する。

### validity gate

1. Q007ag／Q007ai／Q007v artifactとrunner SHA、source、scope、schema、登録classificationと分離outcomeが一致する。
2. Q007ag stored cycle、3 digest、selected tube、6 gate、strict margin、forward invarianceをfresh replayする。
3. Q007ai stored cycle、2 digest、new-tube exact stage bounds、全accepted gate／theoremをfresh replayする。
4. Q007v stored cycle、old one-step acceptance／re-entry rejection、binary64 model、interval primitives、operation
   count、source schedule、deterministic replayをfresh replayする。
5. current D2Q9／filter source SHAと必要operation snippetが一致し、new-tube rest-state replayが全包囲へ入る。
6. Q007agとQ007aiの\(x_{\rm ag}\)がexact一致し、Q007vの\(K_B,K_N\)とQ007ag strict marginが正である。
7. 全boundがfinite strict JSONで、canonical input／result digestを出力する。

一つでも落ちれば`inconclusive`とし、stage lowerもre-entry判定も採用しない。

### hypothesis gateと停止規則

validity通過時だけ次を独立に判定する。

1. equilibrium evaluation: \(p_{\rm eq}^{64}>0\)。
2. post-collision: \(p_{\rm coll}^{64}>0\)。
3. post-streaming: arithmetic-free permutationがpost-collision lowerを保持する。
4. post-filter: \(p_{\rm filt}^{64}>0\)。
5. one-step stage positivity: 上の4件が全て通る。
6. base-coordinate re-entry: \(\epsilon_B<m_B^{\rm ag}\)。
7. normal-coordinate re-entry: \(\epsilon_N<m_N^{\rm ag}\)。

one-step stage positivityが通れば`one_step_outcome=accepted`とする。base／normalの両方が通った場合だけ
`robust_reentry_outcome=accepted`とし、overallを
`binary64 stage positivity and roundoff-robust Q007ag tube invariance certified`
として`accepted`にする。one-stepが通るがre-entryの一方でも落ちればoverallは
`binary64 one-step stages remain positive, but the registered Q007ag tube is not certified roundoff-invariant`
という有効な`not_certified`とする。one-step自体が落ちれば
`binary64 stage positivity is not certified on the registered Q007ag input tube`
という有効な`not_certified`とする。

re-entry不合格は実際のtube escapeや反例ではなく、この固定worst-case enclosureがstrict marginへ収まらない
ことだけを意味する。不合格時はone-step positivityを全iterateへ帰納せず、Q007akで原因をmargin不足、
analysis norm、Wiener lifting、local roundoff accumulationへ分解するまでMPFR／repair／shadowing拡張へ進まない。

### 主張境界

accepted one-step結果も、correctly rounded binary64 encodingから始めたfixed component boxと、登録された
current NumPy演算順序だけに適用する。component box内の状態がfixed mass／momentum leafを満たすことは
利用しないためconservativeだが、arbitrary compiler／hardware実行を認証しない。entropy、monotonicity、
maximum principle、continuous optimum、global basin、grid-uniformity、continuum limit、およびre-entry不合格時の
all-iterate finite-precision positivityは認証しない。既存Q007ag／Q007ai acceptance、Q007v old-tube mixed
result、Q007c1／Q007d／Q007af／Q010結論は変更しない。

### Q007aj 封印結果

全7 validity gateが通過した。hypothesisはequilibrium／collision／streaming／filter／one-step stage
positivityの5件がpassし、base／normal roundoff re-entryの2件がfailした。従って
`one_step_outcome=accepted`、`base_reentry_outcome=not_certified`、
`normal_reentry_outcome=not_certified`、overallは
`binary64 one-step stages remain positive, but the registered Q007ag tube is not certified roundoff-invariant`
という有効な`not_certified`とした。

- sealed Q007ag／Q007ai／Q007v inputs: `3 / 3` pass
- Q007ag／Q007ai／Q007v stored cycle fresh reproduction: `3 / 3` pass
- binary64 model／Fraction primitives／registered operation counts: pass
- current D2Q9／filter source schedule／new-tube rest replay: pass
- input state Wiener upper: `1.4441361143956586e-10`
- equilibrium／collision／streaming／filter population lower:
  `0.02777777759726066 / 0.027777777145968068 / 0.027777777145968068 / 0.02777777714596806`
- post-filter component-error sum／Wiener error upper:
  `4.036979113491066e-15 / 1.1666869637989181e-12`
- base coordinate error／strict margin／utilization:
  `1.7624955732793895e-12 / 4.978814700017615e-20 / 35399902.97837664`
- normal coordinate error／strict margin／utilization:
  `3.490393287849664e-11 / 9.144951058528087e-13 / 38.16743540245316`
- input／result digest:
  `040bf7e2c62094ea66a4cf8a6190ea78e53745e30c70a3b3ce856a7e4d1c5284` /
  `517846a3a99f1e684f40c2ea6d5a8ae7b3db8c0849dae3097fc7f380f4eca923`
- runner／artifact SHA-256:
  `e91cd0740ca9d639f6eaeeea8ed71552a0323897f45eee50070f4c8cdf947ac5` /
  `29b8cd320f40396cc24ae30b46e46eecc7e23564600284aeb916a90af3a1fd8e`

従ってnew tubeでもcurrent binary64一段stage positivityは認証できたが、固定worst-case enclosureでは
両coordinateのroundoff-robust re-entryを認証できない。これは実際のtube escapeではない。次はQ007akで
strict margin、analysis norm、289-wave Wiener lifting、local roundoff accumulationを独立因子へ分解し、
必要改善率を封印する。Q007akまではone-step結果を反復せず、new-tube MPFR／repair／shadowingへ進まない。

## Q007ak: Q007ag roundoff re-entry obstructionの因子分解 — 事前登録

### 問いと固定scope

Q007ajでbase／normal re-entryがともにfailした固定worst-case enclosureについて、utilizationを

\[
U_B=\frac{K_B N E_{53}}{m_B},\qquad
U_N=\frac{K_N N E_{53}}{m_N}
\]

へexactに分解し、strict margin \(m\)、analysis upper \(K\)、normalized-DFT Wiener lifting
\(N=17^2=289\)、post-filter local component-error sum \(E_{53}\)のどの改善率が必要かを定量化する。
さらにQ007wのideal-binary evaluatorを同じnew-tube入力へ適用し、base、normal、両方をそれぞれ初めて
通すsignificand precisionを決める。

固定scopeはQ007ajと同じ\(17^2\)、\(\omega=3/2\)、\(\eta=1/100\)、fixed mass／momentum leaf、
Q007ae exact graph-gauge manifold、Q007p Fourier external-coordinate block-sum \(\ell^1\) norm、
\((r,\zeta)=(9\times10^{-17},5\times10^{-11})\)とする。precision campaignは全整数
\(p=53,54,\ldots,128\)、round-to-nearest ties-to-even、minimum normal exponent \(-1022\)、
\(u_p=2^{-p}\)、subnormal fallback \(h_p=2^{-1075-(p-53)}\)に固定する。

### 封印入力と実装

- Q007aj artifact／runner SHA-256:
  `29b8cd320f40396cc24ae30b46e46eecc7e23564600284aeb916a90af3a1fd8e` /
  `e91cd0740ca9d639f6eaeeea8ed71552a0323897f45eee50070f4c8cdf947ac5`
- Q007w old-tube ideal-precision oracle artifact／runner SHA-256:
  `bac362d9dca4a681387b986a5f5802278ef61a1a3bcf1a0f8577c7f3ab0a07af` /
  `86dcc0a507e24216775650d5467d0ebf6e90eac0865190d0d5186e08afb7eac8`
- current D2Q9／checkerboard-filter source SHA-256:
  `6e6c5aa6734844d0393eb402e21203831faaf5f325b35249941eaa59145c6f53` /
  `5fb6b67e8527b0b1f5f45511ba7cd5d077ee443220632ba3019b7bf28010a7ea`

Q007ajはstored cycle、7 validity gate、7 hypothesis gateのうちbase／normal re-entryだけfail、split outcome、
binary64 stage／re-entry quantities、2 digestをfresh replayする。Q007wはstored cycle、7 validity gate、6
hypothesis gate、old-tube selected precision `85`、76-candidate digest
`440a08dc36990d3e34edf1886fd7e47eacb4766c4a42352022897fd79dbb3ce2`、ties-to-even controlと
\(p=53\) Q007v exact reproductionをfresh replayする。Q007w runnerの`_evaluate_precision`、rounding routine、
candidate digest、monotonicity checkerを結果後に変更しない。

### exact factor audit

Q007ajから次をexact Fractionとして読む。

- \(E_{53}=4.036979113491066\times10^{-15}\)
- \(K_B=1.5106842091904618\)、\(K_N=29.917136268364473\)
- \(m_B=4.978814700017615\times10^{-20}\)、\(m_N=9.144951058528087\times10^{-13}\)
- \(N=289\)

各coordinate \(X\in\{B,N\}\)について、次をexactに記録する。

\[
E_X^{\max}=\frac{m_X}{K_XN},\qquad
K_X^{\max}=\frac{m_X}{NE_{53}},\qquad
N_X^{\max}=\frac{m_X}{K_XE_{53}},\qquad
m_X^{\min}=K_XNE_{53}.
\]

単一因子だけを変える場合のstrict必要改善率はすべて\(U_X\)である。等号は不合格なので、表示値の
丸めではなくexact `<`だけで判定する。counterfactual \(N=1\)、\(K=1\)も記録するが、これらを実現可能な
新normやFourier certificateとは主張しない。目的は、wave liftingまたはanalysis factor単独の理論的な
除去だけで各marginへ届くかを診断することである。

### ideal-precision campaign

各\(p=53,\ldots,128\)でQ007wと同じpaired arithmetic、constant rounding、83 multiplicationを含むoperation
scheduleを、新しい\(x_{\rm ag},K_B,K_N,m_B,m_N\)へ適用する。各候補についてone-step stage positivity、
base re-entry、normal re-entryを独立に保存する。selectionを

\[
p_B=\min\{p:\epsilon_B(p)<m_B\},\quad
p_N=\min\{p:\epsilon_N(p)<m_N\},\quad
p_*=\min\{p:\epsilon_B(p)<m_B,\epsilon_N(p)<m_N\}
\]

とする。候補がなければ対応値は`null`とする。first-passの直前候補は必ず該当gateをfailしなければならない。
\(p=53\)候補はQ007ajの全stage summary、component-error sum、Wiener／coordinate error、utilization、分離outcomeを
exact再現しなければならない。

### validity gate

1. Q007aj／Q007w artifactとrunner SHA、source、scope、schema、登録classification／outcomeが一致する。
2. Q007aj stored cycle、2 digest、7 validity gate、5 pass／2 fail hypothesis、全stage／re-entry quantityをfresh replayする。
3. Q007w stored cycle、old 85-bit boundary、76候補digest、全gate、ties-to-even、\(p=53\) controlをfresh replayする。
4. new-tube \(p=53\)候補がQ007ajのtarget／error stage summary、operation counts、re-entry quantityをexact再現する。
5. \(U_X=K_XNE_{53}/m_X\)と4 single-factor threshold identityを両coordinateでexact再現し、全量が正である。
6. 53--128の全76整数候補を重複なく評価し、全domain／operation count、error nonincrease、stage-lower
   nondecreaseを通し、base／normal／joint selection boundaryをexactに再構成する。
7. 全boundがfinite strict JSONで、canonical input／candidate／result digestを出力する。

一つでも落ちれば`inconclusive`とし、factor診断もprecision thresholdも採用しない。

### hypothesis gateと停止規則

validity通過時だけ次を判定する。

1. Q007aj control: \(U_B>1\)、\(U_N>1\)。
2. factorization: 両coordinateでutilizationと4 threshold identityがexactに閉じる。
3. base threshold: finite \(p_B\)が存在し、\(p_B\)はpass、\(p_B-1\)はbase fail。
4. normal threshold: finite \(p_N\)が存在し、\(p_N\)はpass、\(p_N-1\)はnormal fail。
5. joint threshold: finite \(p_*\)が存在し、\(p_*=\max(p_B,p_N)\)、直前候補はjoint fail、全候補のstage lowerは正。
6. dominant coordinate: \(U_B>U_N\)、\(p_B>p_N\)、\(p_*=p_B\)、\(p_N\)候補でbaseはfail。
7. wave-only counterfactual: \(U_B/289>1\)かつ\(U_N/289<1\)。

全て通れば
`registered factor audit isolates base re-entry as the dominant Q007ag binary64 obstruction`
として`accepted`とする。validity通過後に一件でも落ちれば
`registered factor audit did not isolate a finite dominant Q007ag re-entry threshold`
という有効な`not_certified`とする。

### 主張境界

acceptedでも、固定Q007aj component box、Q007w ideal-binary operation model、53--128整数campaign内の十分条件で
ある。\(p_B,p_N,p_*\)は実装precisionの必要条件でも、actual trajectory escapeの閾値でもない。counterfactual
\(N=1\)、\(K=1\)は新しいcertificateの存在を示さない。FTZ／DAZ、GPU、compiler、MPFR backend trace、
fixed-leaf closure、repair、same-initial shadowing、continuous optimum、grid-uniformity、continuum limitは扱わない。
既存Q007aj mixed result、Q007w old-tube 85-bit threshold、Q007ag／Q007ai acceptance、Q007c1／Q007d／Q007af／
Q010結論は変更しない。acceptedなら次のgateは結果に従い、new-tube ideal thresholdが85以下ならQ007alで
既存MPFR-85 backendの一段包囲を再監査する。85を超えるなら先にprecision選択を再登録する。

### Q007ak 封印結果

validity 7件、hypothesis 7件が全て通過し、
`registered factor audit isolates base re-entry as the dominant Q007ag binary64 obstruction`
として`accepted`とした。

- sealed Q007aj／Q007w inputs: `2 / 2` pass
- Q007aj／Q007w stored cycle fresh reproduction: `2 / 2` pass
- Q007aj \(p=53\) target／error／stage／re-entry exact control: pass
- exact base／normal 4-factor identities: `2 / 2` pass
- precision coverage／domain／monotonicity: `76 / 76` pass
- binary64 base／normal utilization: `35399902.97837664 / 38.16743540245316`
- maximum local component-error sum at boundary:
  `1.1403927055836785e-22 / 1.0577024814278182e-16`
- maximum analysis factor at boundary:
  `4.26748121347461e-08 / 0.7838393109965568`
- maximum wave factor at boundary:
  `8.163864182806664e-06 / 7.5718998919540965`
- unit-wave base／normal utilization:
  `122491.01376600914 / 0.13206725052751958`
- minimal sufficient ideal precision base／normal／joint: `79 / 59 / 79`
- base `p=78 / 79` utilization: `1.049142142753718 / 0.5226851687280066`
- normal `p=58 / 59` utilization: `1.1922608315359098 / 0.5970734654373829`
- input／candidate／result digest:
  `333ce7e6b4537947808a369f1c218c2d930a11df4b826994df0947fa42489d46` /
  `eacc824a8f0fc891971c210883d05f7178e4fe5848ab3b2432dc94adf289e567` /
  `a4d10df4c1d6edd83488115d501af21ad6727dd6321e159e37b2b0e434858644`
- runner／artifact SHA-256:
  `c8bb3f7a84d19d9ab2794d9a1c27334ecd53e62dabce7862343b51ef30cd29b1` /
  `aae6b560125cd29dad5b87bf20e9806ae26a5b1b6ae2ee9c055580042561cf7c`

従って固定Q007aj／Q007w enclosureではbase coordinateが支配障害であり、joint ideal sufficient thresholdは
79 bitsである。これはactual escape thresholdでもimplemented backend証明でもない。79が85以下なので、
次はQ007alで既存Q007x concrete MPFR-85 backendの一段stage／re-entry包囲をnew tube上へ再監査する。
fixed-leaf closure、repair、all-iterate induction、same-initial shadowingはまだ開始しない。

## Q007al: propagated tubeとconcrete MPFR-85 backendの一段bridge — 事前登録

### 問いと固定scope

Q007akでnew-tube joint ideal sufficient thresholdが79 bitsとなり、既存Q007x backendの85 bitsを
下回った。ここではQ007xで固定した`gmpy2`／MPFR-85 backendを変更せず、Q007ag selected
tubeのcomponent box上で次を別々に問う。

1. registered operation scheduleの全primitiveがideal $p=85$ ties-to-even演算と一致するか。
2. concrete equilibrium／collision／streaming／filter stageの観測誤差がQ007ak $p=85$
   component forward-error upperに収まり、各stage populationがstrict positiveか。
3. Q007akのideal $p=85$ Wiener lifting後のbase／normal complement-coordinate error upperが、
   Q007agの対応するstrict forward-invariance marginに収まるか。

固定scopeは$17^2$、D2Q9、$\omega=3/2$、$\eta=1/100$、Q007agの
$(r,\zeta)=(9\times10^{-17},5\times10^{-11})$、Q007p Fourier external-coordinate block-sum
$\ell^1$ normとする。backend、context、constant construction、operation order、4 exact probeは
Q007xから変更しない。

ただしQ007xではcomponentwise encoding、collision、filterが固定質量／運動量葉をexactに
保たないことが既に封印されている。従ってQ007alは、一段算術包囲とcomplement-coordinate
誤差予算の実装bridgeだけを判定する。丸め後stateのactual fixed-leaf tube membership、
one-step re-entry、all-iterate invarianceは判定しない。

### 封印入力とbackend

- Q007ak artifact／runner SHA-256:
  `aae6b560125cd29dad5b87bf20e9806ae26a5b1b6ae2ee9c055580042561cf7c` /
  `c8bb3f7a84d19d9ab2794d9a1c27334ecd53e62dabce7862343b51ef30cd29b1`
- Q007x artifact／runner SHA-256:
  `20ba483c4c627de015673a2f8873cc020a5c1a43ee48c7715121a00330e13566` /
  `de16e86ab365e6e64b15fd62ebdb442a54e05d4e4e529ae1e018299983d7491b`
- Q007x concrete backend SHA-256:
  `25ad43629e2487c5c062920cbb5319dac4e8fbded339dc856548bfab7f18a0dc`
- `pyproject.toml` SHA-256:
  `97e8ed6af7906243a656191f96c80b8f7c1ef4b737587c888092c476be508d94`
- current D2Q9／checkerboard-filter source SHA-256:
  `6e6c5aa6734844d0393eb402e21203831faaf5f325b35249941eaa59145c6f53` /
  `5fb6b67e8527b0b1f5f45511ba7cd5d077ee443220632ba3019b7bf28010a7ea`

Q007akはstored cycle、7 validity gate、7 hypothesis gate、79／59／79-bit selection boundary、
$p=85$ candidateとinput／candidate／result digestをfresh replayする。Q007xはstored cycle、8 validity
gate、2 pass／4 fail hypothesis、runtime／context／source／probe／trace登録、mixed classification、
probe／trace／result digestをfresh replayする。両runnerとbackendはQ007al結果後も変更しない。

concrete backendはQ007xと同じ`gmpy2==2.3.1`、MPFR `4.2.2`、GMP `6.3.0`、
precision `85`、`RoundToNearest`、`emin=-1105`、`emax=1024`、`subnormalize=True`、
dangerous trap enabledとする。constant construction traceは19 operations、map traceは245 operations/site、
$17^2$ full map traceは70,805 operations、constructionを含む各probeのtraceは70,824 operationsに固定する。

### new-tube ideal $p=85$ certificate

Q007ak artifactから85-bit candidateを読み、Q007wの封印済み`_evaluate_precision`を同じ
state radius、analysis upper、strict marginでfreshに評価する。stored candidateとの比較は
display floatではなくexact rational recordとcanonical digestで行う。封印値は次である。

- post-filter local component-error sum:
  `9.365881800643092e-25`
- Wiener error upper:
  `2.7067398403858536e-22`
- base error／margin／utilization:
  `4.08902913525762e-22 / 4.978814700017615e-20 / 0.008212856636827946`
- normal error／margin／utilization:
  `8.097790464783468e-21 / 9.144951058528087e-13 / 8.8549303467643e-09`
- equilibrium／collision-stream／filter error upper:
  `1.637128299597522e-25 / 2.8577941370245856e-25 / 3.1286383452856557e-25`
- minimum stage population lower:
  `0.027777777145968227`

判定は全てexact `<`と`>`で行い、丸めた表示値は判定に使わない。

### concrete campaign

Q007x登録済みの`rest`、`axial_x_pair`、`axial_y_pair`、
`all_populations_paired`をexact Fractionから再構成する。各probeはQ007agのnew component box、
exact fixed-leaf cancellation、input positivityを満たさなければならない。各probeに対し、

- constant／encoding／mapの全operation traceをQ007w ties-to-even oracleと照合する。
- exact Fraction mapに対するequilibrium／collision／streaming／filterのcomponent discrepancyを
  Q007ak 85-bit candidateの各stage boundと比較する。
- 各concrete stage populationがstrict positiveであることを比較する。
- Q007xと同じglobal mass／momentum defectをexact rationalで再計測する。

最後のconservation auditは既知のfixed-leaf障害を回帰検証する診断であり、Q007alの
acceptance hypothesisにはしない。同じsource／probeでQ007xと異なるconservation結果になれば
validity failureとする。

### validity gate

1. Q007ak／Q007x artifactとrunner SHA、source、scope、schema、登録classification／outcomeが一致する。
2. Q007ak stored cycle、3 digest、7 validity／7 hypothesis gate、79／59／79-bit boundary、
   85-bit candidateをfresh replayする。
3. Q007x stored cycle、3 digest、8 validity gate、2 pass／4 fail hypothesis、runtime／context／source／
   probe／trace登録、mixed classificationをfresh replayする。
4. fresh $p=85$ ideal evaluationがQ007ak stored candidateとexact一致し、85がjoint threshold 79より大きい。
5. package／runtime／context、backend／`pyproject.toml`／D2Q9／filter source SHA、constant algebra、
   operation orderが登録と一致する。
6. 4 exact probeが登録recipe、new component box、exact fixed-leaf cancellation、input positivityを満たし、
   全trace／operation count／domain／context restorationが通る。
7. 全probe／全stageのconcrete discrepancyがQ007ak 85-bit component-error upper以下で、
   concrete population lowerがstrict positiveであり、Q007x conservation diagnosticをexact再現する。
8. 全値がfinite strict JSONで、canonical input／probe／trace／result digestを出力する。

一つでも落ちれば`inconclusive`とし、一段bridgeも後続gateも採用しない。

### hypothesis gateと停止規則

validity通過時だけ次を独立に判定する。

1. registered MPFR-85 backendがQ007akで使ったideal 85-bit operation semanticsを実現する。
2. 全4 probeのconstant／encoding／map operation trace、count、domain gateが通る。
3. 全4 probeの全stage discrepancyが85-bit upper以下で、全concrete stage populationがstrict positiveである。
4. ideal 85-bit base complement-coordinate error upperがQ007ag base strict margin未満である。
5. ideal 85-bit normal complement-coordinate error upperがQ007ag normal strict margin未満である。

全て通れば
`registered MPFR-85 backend realizes the Q007ag one-step arithmetic and complement-coordinate error budgets`
として`accepted`とする。validity通過後に一件でも落ちれば
`registered MPFR-85 backend does not realize the Q007ag one-step arithmetic budget`
という有効な`not_certified`とする。

### 主張境界

acceptedでも、固定source／context／operation scheduleに対するMPFR semantic bridge、Q007ag component
boxを用いたQ007akの一段worst-case forward-error budget、登録した4 finite probeのconcrete stage
checkだけを意味する。finite probeは全tubeのsampling proofではない。base／normal margin比較は
ideal exact-map outputに対する算術誤差予算であり、fixed-leaf defectを吸収も修復もしない。

従ってactual rounded stateのfixed-leaf membership、Q007ag tube re-entry、all-iterate induction、
same-initial shadowing、repair map、multi-step trajectory、性能、他のgmpy2／MPFR版、FTZ／DAZ、
GPU／threaded reduction／compiler変更、grid-uniformity、continuum limitは扱わない。
Q007x mixed result、Q007ak threshold、Q007ag／Q007ai acceptance、Q007c1／Q007d／Q007af／Q010結論は
変更しない。acceptedなら次はfixed-leaf defectを修正するnew-tube repair gateを別途事前登録する。

### Q007al 封印結果

validity 8件、hypothesis 5件が全て通過し、
`registered MPFR-85 backend realizes the Q007ag one-step arithmetic and complement-coordinate error budgets`
として`accepted`とした。

- sealed Q007ak／Q007x inputs: `2 / 2` pass
- Q007ak／Q007x stored cycle fresh reproduction: `2 / 2` pass
- Q007ak base／normal／joint threshold: `79 / 59 / 79` bits
- concrete runtime／context:
  `gmpy2 2.3.1 / MPFR 4.2.2 / GMP 6.3.0 / p=85 / RoundToNearest`
- probe／trace count: `4 / 70,824 per probe / 283,296 total`
- trace mismatch／operation-domain failure: `0 / 0`
- 85-bit post-filter component-error sum／Wiener error upper:
  `9.365881800643092e-25 / 2.7067398403858536e-22`
- 85-bit base error／margin／utilization:
  `4.08902913525762e-22 / 4.978814700017615e-20 / 0.008212856636827946`
- 85-bit normal error／margin／utilization:
  `8.097790464783468e-21 / 9.144951058528087e-13 / 8.8549303467643e-09`
- registered equilibrium／collision-stream／filter error upper:
  `1.637128299597522e-25 / 2.8577941370245856e-25 / 3.1286383452856557e-25`
- registered minimum ideal stage lower: `0.027777777145968227`
- maximum concrete stage-bound utilization:
  `0.15250294771440714` (`all_populations_paired`, post-filter)
- minimum observed concrete stage population:
  `0.027777777777759027` (`all_populations_paired`, post-collision)
- conservation regression:
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

従って既存MPFR-85 backendはnew component boxの一段stage包囲とideal complement-coordinate
誤差予算を実現する。ただしQ007xと同じfixed-leaf defectもexact再現したため、
actual rounded stateのtube re-entry、all-iterate invariance、same-initial shadowingは依然として未認証である。
次はQ007amでnew tubeのfixed-leaf repairとその追加算術誤差を別途事前登録し、
all-iterate／shadowingへはまだ帰納しない。

## Q007am: propagated tubeのdistributed fixed-leaf repair — 事前登録

### 問いと固定scope

Q007alで一段MPFR-85 stage包囲とbase／normal complement-coordinate error budgetは
new Q007ag tube上で通過したが、componentwise encoding、collision、filterはexact fixed leafを
保たない。Q007amではQ007yと同一のdistributed diagonal dyadic repairを変更せず、

1. componentwise encoded inputとraw post-filter outputの全保存量欠陥をexactに修正できるか。
2. repairがtube全体のbinade／integer lattice／parity条件上でwell-definedか。
3. raw MPFR-85 errorとrepair correctionのcoarse Wiener triangle boundを合成しても、
   Q007agのbase／normal strict marginに収まるか。

を別々に判定する。固定scopeは$17^2$、D2Q9、$\omega=3/2$、$\eta=1/100$、
Q007agの$(r,\zeta)=(9\times10^{-17},5\times10^{-11})$、Q007p external-coordinate
block-sum $\ell^1$ norm、MPFR precision 85 bitsとする。

repair quantumは$h=2^{-90}$、repair populationsは対角速度$q=5,6,7,8$、targetは
$(M,P_x,P_y)=(289,0,0)$に固定する。Hadamard integer systemのobjectiveは
`sum_abs_diagonal_units / max_abs_diagonal_units / abs_free_unit / free_unit`の辞書式順序、
各対角populationのunitsは289 siteへPython `divmod`でrow-major balanced distributionする。
Q007y repair sourceとQ007x backendは一切変更しない。

Q007amはrepairのfixed-leaf closureと追加誤差budgetのみを判定する。このgate内では
Q007ag exact forward invarianceと合成したall-iterate induction、arbitrary exact boundary stateからの
initial encoding／repair interior、same-initial shadowingを主張しない。

### 封印入力とrepair implementation

- Q007al artifact／runner SHA-256:
  `bf1a2d9959f24cfc83a4efb2926ec76d9ced97755846ee310490585940d8dcf5` /
  `b82e03145e0c7f1c20b1d1345b87acbae5ce526b732969c391b88141118dfd8e`
- Q007y old-tube repair artifact／runner SHA-256:
  `a3afa87c4ee3f5d45e667eac9a6a89a1726f1d4bad0a9f90a624c562fb598648` /
  `ba757030c852b68d5a4c643ec150422c0a7b4c3ba125211d2715ba1445e89811`
- Q007x concrete backend SHA-256:
  `25ad43629e2487c5c062920cbb5319dac4e8fbded339dc856548bfab7f18a0dc`
- `pyproject.toml` SHA-256:
  `97e8ed6af7906243a656191f96c80b8f7c1ef4b737587c888092c476be508d94`
- current D2Q9／checkerboard-filter source SHA-256:
  `6e6c5aa6734844d0393eb402e21203831faaf5f325b35249941eaa59145c6f53` /
  `5fb6b67e8527b0b1f5f45511ba7cd5d077ee443220632ba3019b7bf28010a7ea`

Q007alはstored cycle、6 digest、8 validity／5 hypothesis gate、MPFR context／source／trace、
85-bit candidate、conservation nonclosureをfresh replayする。Q007yはstored cycle、8 validity gate、
5-pass／2-fail hypothesis、old coarse base utilization `2.326054260951996`、normal utilization
`2.507922842743146e-7`、probe digest
`a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329`、finite result digest
`f47bb30b0e2280d339a40b196d1ca3dcb84f94b9e8de087bbff215d07a220fe6`をfresh replayする。

### tube-wide repair bound

Q007alのfresh 85-bit paired quantitiesにQ007yの同一`_tube_stage_repair_bound`を適用する。
各population error upperを$e_q$とし、

$$
E_{\rm raw}=289\sum_q e_q,
$$

$$
E_{\rm rep}=D_M+D_{P_x}+D_{P_y}+2h,
\qquad E_{\rm total}=E_{\rm raw}+E_{\rm rep}
$$

をexact Fractionで記録する。$D_M,D_{P_x},D_{P_y}$はpopulation-wise errorとinteger velocityから
Q007yと同じabsolute triangle boundで作る。center cancellation、spatial Fourier phase、Q007z selected-wave
certificateは使わない。

事前固定するnew-tube値は次である。判定は表示floatではなくexact `<`で行う。

- input-encoding repair $\ell^1$ upper: `1.2452407121655381e-23`
- input maximum-site correction upper: `4.362085261510107e-26`
- post-filter $E_{\rm raw}$: `2.7067398403858536e-22`
- post-filter $E_{\rm rep}$: `4.959477728036884e-22`
- post-filter $E_{\rm total}$: `7.666217568422737e-22`
- total／raw ratio: `2.8322698229209555`
- base coordinate error／margin／utilization:
  `1.1581233824834727e-21 / 4.978814700017615e-20 / 0.02326102601246388`
- normal coordinate error／margin／utilization:
  `2.2935127565743277e-20 / 9.144951058528087e-13 / 2.5079552005207522e-08`

Q007y old-tube coarse base failureがnew marginでpassに変わることは新しいhypothesisである。
Q007zのphase-aware boundを後付けで追加せず、上のcoarse boundだけで判定する。

### finite concrete campaign

Q007x／Q007alと同じ`rest`、`axial_x_pair`、`axial_y_pair`、
`all_populations_paired`を使う。各exact inputをcomponentwise MPFR-85へencodeし、input repair、
raw MPFR map、output repairの順に実行する。次をtoleranceではなくexact rational／bitwiseに比較する。

- repaired inputとrepaired post-filter outputの$(M,P_x,P_y)$がtargetに一致する。
- Hadamard integer solution、balanced distribution、repair additionがexactである。
- repair前後populationがpositiveで、registered binade内に留まる。
- backend operation count／domainが通る。
- raw各stageとrepaired outputのexact Fraction mapに対するdiscrepancyが、Q007al
  85-bit component upper以下である。

finite probeはconcrete implementation regressionであり、tube全体のsampling proofとは扱わない。

### validity gate

1. Q007al／Q007y artifactとrunner SHA、source、scope、schema、登録classification／outcomeが一致する。
2. Q007al stored cycle、6 digest、8 validity／5 hypothesis gate、85-bit candidate、trace／context／
   conservation diagnosticをfresh replayする。
3. Q007y stored cycle、8 validity、5-pass／2-fail hypothesis、old tube bound、probe／finite digest、
   solver／distribution／conservationをfresh replayする。
4. backend／Q007y repair／`pyproject.toml`／D2Q9／filter source、MPFR context、probe recipeが登録と一致する。
5. fresh 85-bit candidateとnew tubeのrepair boundが事前固定値、binade／lattice／parity、
   $E_{\rm total}=E_{\rm raw}+E_{\rm rep}$をexact再現する。
6. 全4 probeのinteger solver、balanced distribution、exact repair operation、operation domainが通る。
7. 全4 probeのrepaired input／outputがtarget保存量にexact一致し、全raw／repaired stage boundと
   positivityが通る。
8. 全値がfinite strict JSONで、canonical input／probe／result digestを出力する。

一つでも落ちれば`inconclusive`とし、repair closureもerror budgetも採用しない。

### hypothesis gateと停止規則

validity通過時だけ次を独立に判定する。

1. repaired componentwise encodingが全4 probeでtarget fixed leafをexactに回復する。
2. repaired post-filter outputが全4 probeでtarget fixed leafをexactに回復する。
3. 全finite repairがexact、positive、binade内、Q007al component bound内である。
4. repair mapがnew registered component tube全体でwell-definedである。
5. repair-aware normal error upperがQ007ag normal strict margin未満である。
6. repair-aware base error upperがQ007ag base strict margin未満である。
7. 1--6が同時に通り、distributed repairがfixed-leaf closureと両一段error budgetを共存させる。

全て通れば
`distributed MPFR-85 repair restores the Q007ag fixed leaf and fits both registered one-step budgets`
として`accepted`とする。validityと1--5が通り6だけ落ちれば
`distributed MPFR-85 repair restores the Q007ag fixed leaf but not its base budget`
という有効な`not_certified`とする。その他のhypothesis failureは
`registered distributed MPFR-85 repair does not close the Q007ag one-step budgets`
とする。

### 主張境界

acceptedでも、封印MPFR-85 backend、Q007yのdistributed repair、Q007ag component boxと
Q007al 85-bit paired error modelに対するfixed-leaf repair feasibilityと一段誤差予算だけを意味する。
finite probeは実装回帰であり、tube sampling proofではない。coarse repair boundはcenter
cancellationやspatial phaseを使わず、Q007z selected-wave結論をnew tubeへ移さない。

Q007amでは、repair-aware budgetをQ007ag exact forward invarianceと合成したtube self-map定理、
all-iterate induction、exact-state initialization interior、same-initial shadowingをまだ主張しない。
arbitrary target conserved values、他のrepair lattice／distribution、parallel reduction、性能、他MPFR版、
GPU／compiler、grid-uniformity、continuum limitも扱わない。Q007y／Q007z old-tube結論、
Q007al acceptance、Q007ag／Q007ai exact結論、Q007c1／Q007d／Q007af／Q010結論は変更しない。
acceptedなら次はQ007anでexact tube invariance、stage positivity、repair-aware budgetを明示的に合成し、
already-repaired MPFR-85 stateのall-iterate inductionを別途事前登録する。

### Q007am 封印結果

validity 8件、hypothesis 7件が全て通過し、
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
- finite campaign: 4 probeのinput／output repair、exact conservation、operation domain、
  positivity、component enclosureが全て通過し、Q007yのrepair operation／distribution digestを再現した。
- input／probe／finite-result／result digest:
  `f1a0dfd0b90cf354e9847cb076058fd241ab813a90bdee0bfdbafa9dfee17de5` /
  `a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329` /
  `905b65f13ee01711f3b083a0bd93e44b32d0fc5201007fad77e99de03063ab6d` /
  `2217172b48bf86b987a316c9b8c14db6aaeceb3e50f304fa7fefb021c2fd5bd2`
- runner／artifact newline-normalized SHA-256:
  `a0bdebc150c4c3ad055e1840b98196dee95bf967c417d17097f7a35579f2aa16` /
  `3b1b6f3c839cec572d0279f41c158dfafa09088e5f8ee1c3eab84f5bd279b781`

従ってQ007yでold tubeのbase budgetを2.326倍超過した同じcoarse repairは、Q007agの縮小component
boxではbase marginの約2.326%、normal marginの約\(2.51\times10^{-8}\)だけを使い、fixed leafを
exactに回復する。ただしQ007ag exact forward invarianceとの自己写像合成、all-iterate induction、
initialization、same-initial shadowingは未認証である。次はQ007anを事前登録する。

## Q007an: propagated tubeのrepaired MPFR-85 all-iterate induction — 事前登録

### 問いと固定scope

Q007agのexact-map forward invariance、Q007aiのexact stagewise positivity、Q007alのconcrete
MPFR-85 stage enclosure、Q007amのdistributed fixed-leaf repairと修復込み一段誤差予算を、
一つのrepaired sampling mapの自己写像定理へ明示的に合成できるか。

Q007yと同じpost-filter repairを\(\mathcal R\)、Q007xと同じ85-bit BGK／streaming／filter mapを
\(\widetilde\Phi_{85}\)とし、sampling mapを

\[
\widetilde\Psi_{85}=\mathcal R\circ\widetilde\Phi_{85}
\]

と固定する。初期条件は`already encoded and repaired MPFR-85 state`であり、exact dyadic stateとして

\[
M=289,\qquad P_x=P_y=0,
\]

およびQ007agと同じgraph-gauge／external coordinatesで

\[
\lVert a\rVert_1\le r=9\times10^{-17},\qquad
\lVert z\rVert_*\le\zeta=5\times10^{-11}
\]

を満たすことを仮定する。任意のexact stateを最初にencode／repairした結果がこの集合へ入ることは
Q007anでは仮定せず、後続のinitialization gateへ残す。

### 封印入力

- Q007ag artifact／runner newline-normalized SHA-256:
  `5783df74abb4b6ec7d658fd7e3dd272cf100cd134783c31863d643fcd17d4200` /
  `bafd9a56d2d2ceb94acb709609bd710c9fff0f6c0bf543202fa411b9456fb6e0`
- Q007ag input／candidate／result digest:
  `262cbeccacf858bd798de06f363635f15c78ff3d361b44bdd5850aeb90679613` /
  `a7a6a8f605339b0e8ffd16a5d3190967cb7329771d322f8edc0a53bc4b45e408` /
  `6f52c6f1cfa618ca881439504f1bd5b46e45eb245670f1a2c6341669aa024f43`
- Q007ai artifact／runner newline-normalized SHA-256:
  `3ce5fa6358eaa6f3a64f93fe773e3fbc1990abfb83886aad1a4ade9c82425804` /
  `3235b2dc31445e5912f2aaf7fc080e8295035801ade9b27d3f683d34da61173d`
- Q007ai input／result digest:
  `0dff47e8b0ed6e9b87cb73e6dea20192088495b51283c57b9d58630b7344c6a3` /
  `c101313957c738ccee9fd3d7f1ed36b77c6f3dad4e1130651f5be4d8757ef18a`
- Q007al artifact／runner newline-normalized SHA-256:
  `bf1a2d9959f24cfc83a4efb2926ec76d9ced97755846ee310490585940d8dcf5` /
  `b82e03145e0c7f1c20b1d1345b87acbae5ce526b732969c391b88141118dfd8e`
- Q007al result digest:
  `a46f4850d57b0e7d503177205c2cb3d1ed91679cc4c13b9ef31382dbd7bdcd06`
- Q007am artifact／runner newline-normalized SHA-256:
  `3b1b6f3c839cec572d0279f41c158dfafa09088e5f8ee1c3eab84f5bd279b781` /
  `a0bdebc150c4c3ad055e1840b98196dee95bf967c417d17097f7a35579f2aa16`
- Q007am input／probe／finite-result／result digest:
  `f1a0dfd0b90cf354e9847cb076058fd241ab813a90bdee0bfdbafa9dfee17de5` /
  `a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329` /
  `905b65f13ee01711f3b083a0bd93e44b32d0fc5201007fad77e99de03063ab6d` /
  `2217172b48bf86b987a316c9b8c14db6aaeceb3e50f304fa7fefb021c2fd5bd2`

Q007agはvalidity／hypothesis `6 / 5`、Q007aiは`6 / 5`、Q007alは`8 / 5`、
Q007amは`8 / 7`が全通過したaccepted cycleとしてfresh replayする。Q007am内のQ007al／Q007y
reproductionも再利用し、同じ85-bit backend、operation order、\(h=2^{-90}\) repair、target、
row-major balanced distributionから変更しない。

### 一段自己写像の合成

Q007agが与えるexact-map interior marginを

\[
\Delta_a=4.978814700017615\times10^{-20},\qquad
\Delta_z=9.144951058528087\times10^{-13}
\]

とする。Q007ag artifactの`base_forward_invariance`／`normal_tube_forward_invariance` strict marginと、
Q007amが使用したbase／normal marginがexact rationalで一致することを検証する。

Q007amのraw-map誤差とrepair correctionを含むcoordinate error upperは

\[
E_a^{\rm rep}=1.1581233824834727\times10^{-21},\qquad
E_z^{\rm rep}=2.2935127565743277\times10^{-20}
\]

である。任意の登録tube内fixed-leaf input \(x\)について、Q007agとQ007amを同じexact inputへ適用し、

\[
\begin{aligned}
\lVert a(\widetilde\Psi_{85}(x))\rVert_1
&\le (r-\Delta_a)+E_a^{\rm rep}<r,\\
\lVert z(\widetilde\Psi_{85}(x))\rVert_*
&\le (\zeta-\Delta_z)+E_z^{\rm rep}<\zeta
\end{aligned}
\]

をexact rationalで再構成する。残るheadroomはbase／normalでそれぞれ
`4.863002361769267e-20 / 9.144950829176811e-13`、margin utilizationは
`0.02326102601246388 / 2.5079552005207522e-08`と事前登録する。

### fixed leaf、表現可能性、stage positivity

fixed leaf上ではinput repairのdefect unitsがexactに`(0,0,0)`となり、Hadamard solver、4 diagonal
unit、289-site balanced distributionが全てzeroになることを確認する。従ってinput repairはこの集合上で
identityであり、帰納時に誤差を二重加算しない。

raw mapの各内部stageにはQ007alのtube-wide MPFR-85 paired enclosureを用い、最悪population lower
`0.027777777145968227`がstrict positiveであることを確認する。Q007amのpost-filter repairは
全tubeでexact／same-binadeであり、対角populationを\([1/64,1/32)\)内に保つ。repair後のglobal
mass／momentumはexact targetへ戻り、出力は再び85-bit MPFR dyadic stateなので、同じ仮説を次stepへ
再適用できる。

finite 4-probe campaignはimplementation regressionとしてexact再現するが、自己写像の証明には
上のtube-wide rational boundsだけを用いる。

### validity gate

1. Q007ag／Q007ai／Q007al／Q007am artifact・runner SHA、schema、source、scope、classification、
   accepted outcome、gate count、全登録digestが一致する。
2. Q007ag、Q007ai、Q007am cycleをfresh replayし、Q007am内のQ007al／Q007y reproductionも通る。
3. \(r,\zeta\)、fixed-leaf target、coordinate norm、MPFR context、operation order、repair source／lattice／
   distributionが全入力で一致する。
4. Q007ag strict marginとQ007am登録marginがexactに一致し、二つのtriangle identityとheadroomを
   exact rationalで再計算できる。
5. Q007ai exact positivity、Q007al MPFR stage enclosure、Q007am post-repair binade／positivityが
   同じcomponent box上の連続するstage時刻として整合する。
6. zero-defect input repairがidentityで、post-filter repairがexact fixed leafと85-bit表現可能性を回復する。
7. 全値finiteなstrict JSONを生成し、input／composition／result digestを再現する。

一つでも失敗すれば`inconclusive`とし、自己写像仮説を解釈しない。

### hypothesis gateと停止規則

validity通過時だけ次を独立に判定する。

1. Q007ag exact mapが登録fixed-leaf tubeを\(\Delta_a,\Delta_z\)だけstrict interiorへ送る。
2. Q007alのconcrete MPFR-85 raw mapがtube全体で定義され、全内部stage populationがstrict positiveである。
3. Q007am repairがtube-wideに定義され、exact fixed leaf、same-binade positivity、85-bit表現可能性を回復する。
4. \(E_a^{\rm rep}<\Delta_a\)でbase coordinateがstrictに再入する。
5. \(E_z^{\rm rep}<\Delta_z\)でnormal coordinateがstrictに再入する。
6. 1--5から\(\widetilde\Psi_{85}\)が登録repaired fixed-leaf tubeの一段自己写像となる。
7. input repairのidentityと6により、全sampling timeのfixed leaf／tube membershipと全内部stageの
   strict positivityを数学的帰納で閉じる。

全て通れば
`coarse repair certificate closes the Q007ag repaired MPFR-85 fixed-leaf tube induction`
として`accepted`とする。

base／normalのいずれかが落ちる場合は
`Q007am one-step budgets do not compose with the Q007ag exact margins`
として有効な`not_certified`とする。stage／repair／identityのいずれかが落ちる場合は
`registered repaired MPFR-85 map does not close the Q007ag tube induction`
とし、帰納を主張しない。

### 主張境界

acceptedでも、固定17²、固定\((M,P_x,P_y)=(289,0,0)\)葉、封印Q007ae coordinates、
85-bit MPFR backend、Q007y row-major repairに限り、すでにencode／repairされQ007ag tube内にある
初期stateを条件とする。sampling-time fixed leaf／tube membershipと各step内部stage positivityを
全iterateへ帰納するが、任意exact stateのinitial encoding interior、同じinitial stateからのexact軌道との
shadowing／trajectory error、性能、GPU／parallel reduction、他grid／MPFR build、grid-uniformity、
continuum limit、D3Q27は主張しない。Q007zのold-tube selected-wave帰納とQ007amの一段限定結果は
それぞれのscopeで保存する。

acceptedなら次はQ007aoで、事前登録したstrict inner exact-state setのcomponentwise MPFR-85
encodingとinput repairがQ007ag repaired tubeへ入るinitialization interiorを独立に判定する。

### Q007an 最終結果

validity `7/7`、hypothesis `7/7`が全て通過し、
`coarse repair certificate closes the Q007ag repaired MPFR-85 fixed-leaf tube induction`
として`accepted`とした。

- Q007ag exact base／normal margin:
  `4.978814700017615e-20 / 9.144951058528087e-13`
- Q007am repair-aware base／normal error:
  `1.1581233824834727e-21 / 2.2935127565743277e-20`
- repaired-map base／normal headroom:
  `4.863002361769267e-20 / 9.144950829176811e-13`
- exact／MPFR-85 minimum internal-stage lower:
  `0.027777777320468006 / 0.027777777145968227`
- post-repair diagonal lower: `0.015625`
- input／composition／result digest:
  `7d93718b4e8375ea3983c37042d0aaedc98f4a16a329687afa69f75511e29657` /
  `7ce1bde2ddc99ace52610c1a814a65dada1711baf048ec5410241ce497f809d7` /
  `80bae2065ec27d22c7e5a392f764e422ef57d521e0848d6c9eae3e0ed07e8bf7`
- runner／artifact newline-normalized SHA-256:
  `bacf2eca47348ebbb5f5fbfe739f3239ebdb49eedc0d615efc144eb113b5f1bf` /
  `dd28dc89f2096252db80e2ad7461ebdf71bb757e879b8657df01da766849ebdb`

zero-defect input repairがfixed leaf上でidentityであること、raw MPFR-85 mapのtube-wide stage positivity、
post-filter repairのexact fixed-leaf回復と85-bit表現可能性を合成したため、同じ仮説を次stepへ再適用できる。
従ってalready encoded and repaired MPFR-85 stateが登録tube内にあるという条件のもとで、sampling-time
fixed leaf／tube membershipと全内部stage positivityを全iterateへ帰納できる。

任意exact stateのinitial encoding／repairがこの条件付き初期集合へ入ることと、same-initial exact軌道との
shadowingは証明していない。Q007aoで前者だけを次の独立gateとして扱う。

## Q007ao: propagated tubeのexact-state initialization interior — 事前登録

### 問いと固定scope

Q007anのall-iterate inductionは、初期stateがすでにcomponentwise MPFR-85へencode・repairされ、
Q007ag fixed-leaf tube内にあることを仮定する。そこでfixed leaf上のexact state

\[
x=W(a)+Uz,\qquad M=289,\qquad P_x=P_y=0
\]

について、事前登録したstrict inner coordinate set

\[
\lVert a\rVert_1\le r_0=8.9998\times10^{-17},\qquad
\lVert z\rVert_*\le\zeta_0=4.999999999\times10^{-11}
\]

をcomponentwise MPFR-85へround-to-nearestでencodeし、Q007amと同じ\(h=2^{-90}\) row-major
distributed repairを一回適用したstateが、Q007ag outer tube

\[
r=9\times10^{-17},\qquad \zeta=5\times10^{-11}
\]

へstrictに入るかを判定する。内側半径はQ007aaの登録半径をQ007agのtube拡大率
base `100`、normal `10`で写した値であり、結果を見て変更しない。

このgateはinitializationだけを扱う。encoded/repaired軌道と同じexact initial stateから始まるexact軌道の
shadowing、trajectory error、より大きい初期集合は含めない。

### 封印入力

- Q007ag artifact／runner newline-normalized SHA-256:
  `5783df74abb4b6ec7d658fd7e3dd272cf100cd134783c31863d643fcd17d4200` /
  `bafd9a56d2d2ceb94acb709609bd710c9fff0f6c0bf543202fa411b9456fb6e0`
- Q007ag input／candidate／result digest:
  `262cbeccacf858bd798de06f363635f15c78ff3d361b44bdd5850aeb90679613` /
  `a7a6a8f605339b0e8ffd16a5d3190967cb7329771d322f8edc0a53bc4b45e408` /
  `6f52c6f1cfa618ca881439504f1bd5b46e45eb245670f1a2c6341669aa024f43`
- Q007am artifact／runner newline-normalized SHA-256:
  `3b1b6f3c839cec572d0279f41c158dfafa09088e5f8ee1c3eab84f5bd279b781` /
  `a0bdebc150c4c3ad055e1840b98196dee95bf967c417d17097f7a35579f2aa16`
- Q007am input／probe／finite-result／result digest:
  `f1a0dfd0b90cf354e9847cb076058fd241ab813a90bdee0bfdbafa9dfee17de5` /
  `a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329` /
  `905b65f13ee01711f3b083a0bd93e44b32d0fc5201007fad77e99de03063ab6d` /
  `2217172b48bf86b987a316c9b8c14db6aaeceb3e50f304fa7fefb021c2fd5bd2`
- Q007an artifact／runner newline-normalized SHA-256:
  `dd28dc89f2096252db80e2ad7461ebdf71bb757e879b8657df01da766849ebdb` /
  `bacf2eca47348ebbb5f5fbfe739f3239ebdb49eedc0d615efc144eb113b5f1bf`
- Q007an input／composition／result digest:
  `7d93718b4e8375ea3983c37042d0aaedc98f4a16a329687afa69f75511e29657` /
  `7ce1bde2ddc99ace52610c1a814a65dada1711baf048ec5410241ce497f809d7` /
  `80bae2065ec27d22c7e5a392f764e422ef57d521e0848d6c9eae3e0ed07e8bf7`

Q007an cycleをfresh replayし、その内部でQ007ag／Q007ai／Q007amとQ007am内のQ007al／Q007yまで
再現する。backend precision、rounding、operation order、repair lattice／distribution、fixed-leaf target、
Q007ae graph-gauge／external normは変更しない。

### exact initialization bound

Q007amのinput-encoding tube boundから、physical Wiener errorを

\[
E_{\rm raw}=7.470474916829075\times10^{-24},\qquad
E_{\rm rep}=1.2452407121655381\times10^{-23},
\]

\[
E_W=E_{\rm raw}+E_{\rm rep}
=1.9922882038484456\times10^{-23}
\]

と固定する。今回は新tubeでQ007amのcoarse boundが十分なので、Q007zのselected-wave cancellationを
用いない。Q007amのanalysis upperとQ007ag selected candidateのchart derivativeを

\[
K_L=1.5106842091904618,\qquad
K_a=29.917136268364473,\qquad
d_H(r)=1.0398158027969315\times10^{-14}
\]

として、base shiftとgraph-gauge normal shiftを

\[
\epsilon_a=K_LE_W,
\qquad
\epsilon_z=K_a\left(E_W+d_H(r)\epsilon_a\right)
\]

でexact rational評価する。事前登録値は次のとおりとする。

- base inward margin／increment／headroom／utilization:
  `2e-21 / 3.009718329710275e-23 / 1.969902816702897e-21 / 0.015048591648551374`
- direct external／graph-shift／total normal increment:
  `5.960355768038905e-22 / 9.362725402249564e-36 / 5.960355768038998e-22`
- normal inward margin／headroom／utilization:
  `1e-20 / 9.4039644231961e-21 / 0.05960355768038998`
- tight base／normal initialization radius:
  `8.99999699028167e-17 / 4.9999999999403966e-11`

全比較は表示floatではなくartifact由来のexact `Fraction`で行う。physical errorからbaseとnormalを
同時に評価するため、center cancellation、spatial Fourier phase、Q007z boundは使わない。

### validity gate

1. Q007ag／Q007am／Q007an artifact・runner SHA、schema、source、scope、classification、accepted outcome、
   gate count、全登録digestが一致する。
2. Q007an stored cycleをfresh replayし、transitiveなQ007ag／Q007ai／Q007al／Q007am／Q007y再現が通る。
3. fixed leaf、outer tube、graph-gauge／external norm、MPFR context、repair lattice／distributionが全入力で一致する。
4. Q007am input encoding／repair boundがexactに再構成され、repairがinner setを含むcomponent tube全体で
   lattice-defined、positive、exact fixed-leaf restoringである。
5. \(K_L,K_a,d_H(r)\)と二つのincrement formula、登録inner marginがexact rationalで再現する。
6. encoded／repaired baseとnormal radiusがQ007ag outer radius未満へstrictに入る。
7. 全値finiteなstrict JSONを生成し、input／bound／result digestを再現する。

一つでも失敗すれば`inconclusive`とし、initialization hypothesisを解釈しない。

### hypothesis gateと停止規則

validity通過時だけ次を独立に判定する。

1. 登録exact-state inner setがQ007ag tubeのstrict subsetである。
2. componentwise MPFR-85 encoding後のinput repairがtube-wideに定義され、exact fixed leaf、positivity、
   85-bit表現可能性を回復する。
3. \(\epsilon_a<r-r_0\)でbase coordinateがstrictにouter ballへ入る。
4. \(\epsilon_z<\zeta-\zeta_0\)でgraph shift込みnormal coordinateがstrictにouter ballへ入る。
5. 1--4からencoded／repaired initial stateがQ007ag repaired fixed-leaf tubeへ入る。
6. 5をQ007anと合成し、登録exact-state inner setからsampling-time fixed leaf／tube membershipと
   全内部stage positivityを全iterateへ帰納できる。

全て通れば
`registered propagated-tube exact-state interior survives MPFR-85 encoding and repair`
として`accepted`とする。

base／normalのいずれかが落ちる場合は
`registered Q007ao initialization interior is too shallow for encoding and repair`
として有効な`not_certified`とする。repairまたはQ007an接続が落ちる場合は
`exact-state initialization does not connect to the Q007an repaired induction`
とし、全iterate結論を主張しない。

### 主張境界

acceptedでも、固定17²、固定\((M,P_x,P_y)=(289,0,0)\)葉、封印Q007ae coordinates、登録inner set、
componentwise MPFR-85 round-to-nearest、Q007y row-major repairに限る。任意Q007ag boundary state、
arbitrary exact physical state、same-initial shadowing／trajectory error、性能、GPU／parallel reduction、
他grid／MPFR build、grid-uniformity、continuum limit、D3Q27は主張しない。Q007aa old-tube initializationと
Q007an conditional inductionはそれぞれのscopeで保存する。

acceptedなら次はQ007apで、Q007abのfixed-coordinate contraction／local defect boundをQ007ag tubeと
Q007ao初期集合へ移し、same-initial repaired-MPFR forward shadowingを独立に判定する。

### Q007ao 最終結果

validity 7/7、hypothesis 6/6が全て通過し、
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

登録strict inner exact-state setのcomponentwise MPFR-85 encodingとinput repairは、base／normalの
両coordinateでQ007ag outer tubeへstrictに入る。Q007anと合成できるため、この登録initial setから
sampling-time fixed leaf／tube membershipと全内部stage positivityを全iterateへ帰納できる。

任意Q007ag boundary state、arbitrary exact physical state、same-initial exact軌道とのshadowingは
証明していない。次はQ007apでshadowingだけを独立gateとして扱う。

## Q007ap: propagated tubeのsame-initial all-iterate forward shadowing — 事前登録

### 問いと固定scope

Q007aoの登録inner exact-state setから同じfixed-leaf state xを選び、

- exact orbit: x_n=Phi^n(x)
- repaired orbit: y_0=R(E_85(x))、y_(n+1)=Psi_85(y_n)

をsampling timeで比較する。ここでE_85はcomponentwise MPFR-85 round-to-nearest、RはQ007y
row-major repair、Psi_85はQ007anのrepaired sampling mapである。

Q007abと同じequilibriumで固定した線形座標

\[
\mathcal Cx=(Lx,JQx),\qquad
\|\mathcal Cx\|_\oplus=\|Lx\|_1+\|JQx\|_*
\]

を用い、Q007ag tube全体でexact mapがstrict contractionとなるか、Q007ao initialization defectと
Q007am one-step local defectを幾何級数へ足し上げられるかを判定する。graph-relative normal coordinateを
trajectory distanceへ使わず、Q007aoのgraph shiftを初期fixed-coordinate errorへ二重加算しない。

### 封印入力

- Q007ab artifact／runner newline-normalized SHA-256:
  3770e53e5fd169ea8ba16a568a1a1a3052afdd95d2779ba630c7ba7113bdc7ae /
  4958e1aa5140bdbd1a32ce074c77ce2739636a34f7da2531c792ec165401c01a
- Q007ab input／result digest:
  83c98750b8a18aa98cae710fad0a4d2fa139428d791a085bdd086e39e435225f /
  268a5e2098011561c3bc521c845e6eb804692713502fbbd54c3b3106b8f9c014
- Q007ag artifact／runner newline-normalized SHA-256:
  5783df74abb4b6ec7d658fd7e3dd272cf100cd134783c31863d643fcd17d4200 /
  bafd9a56d2d2ceb94acb709609bd710c9fff0f6c0bf543202fa411b9456fb6e0
- Q007ag input／candidate／result digest:
  262cbeccacf858bd798de06f363635f15c78ff3d361b44bdd5850aeb90679613 /
  a7a6a8f605339b0e8ffd16a5d3190967cb7329771d322f8edc0a53bc4b45e408 /
  6f52c6f1cfa618ca881439504f1bd5b46e45eb245670f1a2c6341669aa024f43
- Q007am artifact／runner newline-normalized SHA-256:
  3b1b6f3c839cec572d0279f41c158dfafa09088e5f8ee1c3eab84f5bd279b781 /
  a0bdebc150c4c3ad055e1840b98196dee95bf967c417d17097f7a35579f2aa16
- Q007am input／probe／finite-result／result digest:
  f1a0dfd0b90cf354e9847cb076058fd241ab813a90bdee0bfdbafa9dfee17de5 /
  a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329 /
  905b65f13ee01711f3b083a0bd93e44b32d0fc5201007fad77e99de03063ab6d /
  2217172b48bf86b987a316c9b8c14db6aaeceb3e50f304fa7fefb021c2fd5bd2
- Q007ao artifact／runner newline-normalized SHA-256:
  c6262043848a479b90634fc8aa82dbd02bfcaea4bcb3467d240b956fd7602b8f /
  2cd4c852c2855b93efaeb618bc3b1cb488885375c69f11e2c7624f0ea84614f7
- Q007ao input／bound／result digest:
  4793702239a7bc6252b71b5fff43cc68e78dcad1d1b9446db94544b85270deb3 /
  b747e0a635cf4d747728fd5447e613b62a0b951813634f8a98c9e80a17f3308a /
  6c2a41f2ff2d610d8f542cb132a50a678298098245063d54bcd2a38b6e6a8360

Q007abとQ007aoをそれぞれfresh replayする。Q007ao replay内のQ007anと全transitive upstreamも通す。
Q007abはold-tube結果を新tubeへ流用せず、fixed-coordinate formulaと、rho／tau変更で不変なlinear
analysis／synthesis constantsの独立oracleとしてだけ使う。

### Q007ag tube上のfixed-coordinate Lipschitz bound

Q007abで封印したlinear constantsを

\[
q_s=0.9920954673554099,\qquad q_0=0.981709835832552,
\]

\[
c_V=2.7869014191713024,\qquad K_s=2.888267212368763,
\]

\[
K_L=1.5106842091904618,\qquad K_a=29.917136268364473
\]

とする。Q007ag selected candidateから新tubeのphysical Wiener radiusとnonlinear derivativeを

\[
R_T=1.4441361143956586\times10^{-10},\qquad
d_N(R_T)=3.032685840887825\times10^{-9}
\]

と固定する。fixed-coordinate full-map Lipschitz upperを

\[
L_\oplus=
\max(q_s,q_0)
+(K_L+K_a)d_N(R_T)\max(c_V,K_s)
\]

でexact rational評価する。事前登録値は次のとおりとする。

- linear direct-sum contraction: 0.9920954673554099
- nonlinear coordinate increment: 2.7528278762500916e-7
- full Lipschitz upper: 0.9920957426381974
- contraction gap 1-L: 0.007904257361802534

Q007agのgraph-relative normal contraction 0.9817100978829438は比較診断に残すが、このfixed-coordinate
Lipschitz formulaへ代入しない。

### initial／local defectと幾何級数

Q007aoからinitial fixed-coordinate errorを

\[
d_0\le
\epsilon_{a,0}+K_aE_{W,0}
\]

とする。Q007aoのgraph shiftはencoded stateのgraph-relative tube membershipにだけ必要であり、線形差
\(\mathcal C(y_0-x)\)には二重加算しない。

- initial selected／physical／external／total coordinate error:
  3.009718329710275e-23 / 1.9922882038484456e-23 /
  5.960355768038905e-22 / 6.261327601009932e-22

Q007amのtube-wide repaired-map local defectから

\[
\epsilon_{\rm step}
=E_a^{\rm rep}+E_z^{\rm rep}
\]

とする。

- step selected／external／total coordinate defect:
  1.1581233824834727e-21 / 2.2935127565743277e-20 / 2.4093250948226748e-20

各sampling timeで

\[
d_{n+1}\le L_\oplus d_n+\epsilon_{\rm step}
\]

を用い、

\[
D_*=\frac{\epsilon_{\rm step}}{1-L_\oplus},\qquad
D=\max(d_0,D_*)
\]

をexact rationalで構成する。事前登録値は次のとおりとする。

- stationary／uniform coordinate error: 3.0481359405954845e-18
- direct-sum synthesis upper: 2.888267212368763
- uniform physical Wiener error: 8.803831096064757e-18
- physical error／Q007ag tube state radius: 6.096261293035372e-8
- registered relative accuracy threshold: 1e-6
- absolute Wiener threshold: 1.4441361143956587e-16

### validity gate

1. Q007ab／Q007ag／Q007am／Q007ao artifact・runner SHA、schema、source、scope、classification、
   accepted outcome、gate count、全登録digestが一致する。
2. Q007abとQ007ao stored cycleをfresh replayし、Q007aoのtransitive upstream reproductionも全て通る。
3. fixed linear coordinate definition、linear analysis／synthesis constants、fixed leaf、grid、backend、
   repair、trajectory comparison timeが全入力で一致する。
4. Q007ag state radius／nonlinear derivativeとQ007ab fixed-coordinate constantsからLipschitz formulaを
   exact rationalで再構成し、old graph-relative normal contractionを使っていない。
5. Q007ao initial defectとQ007am one-step local defectをfixed-coordinate normでexactに再構成し、
   graph shiftを二重加算していない。
6. stationary／uniform coordinate bound、physical synthesis、tube-relative ratio、recurrence fixed-point identityを
   exact rationalで再現する。
7. 全値finiteなstrict JSONを生成し、input／recurrence／result digestを再現する。

一つでも失敗すればinconclusiveとし、shadowing hypothesisを解釈しない。

### hypothesis gateと停止規則

validity通過時だけ次を独立に判定する。

1. exact orbitとrepaired MPFR-85 orbitがともにQ007ag tubeに全iterate留まる。
2. fixed-coordinate exact mapがL_oplus<1でstrict contractionである。
3. Q007ao initial fixed-coordinate errorがd_0で包囲される。
4. Q007am repaired-map one-step local defectがepsilon_stepで包囲される。
5. [0,D]がd -> L_oplus d + epsilon_stepで不変で、d_0を含む。
6. uniform physical Wiener error／R_T < 1e-6である。

全て通れば
「propagated-tube fixed-coordinate contraction certifies all-iterate MPFR-85 forward shadowing」
としてacceptedとする。

L_oplus>=1なら
「registered propagated-tube fixed-coordinate majorant is not contractive」、
accuracy gateだけが落ちれば
「uniform propagated-tube shadow bound exceeds the registered accuracy threshold」
として有効なnot_certifiedとする。それ以外は
「registered propagated-tube recurrence does not certify all-iterate forward shadowing」
とする。

### 主張境界

acceptedでも、Q007ao inner exact-state setから同じstateを初期化したexact／repaired二軌道の
nonnegative sampling timesにおけるfixed-coordinate forward errorだけを意味する。bi-infinite
shadowing lemma、backward error、内部stage間距離、componentwise relative error、任意Q007ag boundary
initialization、性能、他grid／MPFR build、GPU／parallel reduction、grid-uniformity、continuum limit、
D3Q27は主張しない。Q007ab old-tube shadowing、Q007ao initialization、Q007an conditional inductionは
それぞれのscopeで保存する。

acceptedならpropagated-tube finite-precision chainを閉じる。Q009 TT-crossはQ008c／Q010の固定経路棄却に
より保留したままとし、次はQ011 boundary／forcingか、Q007afが残した別norm certificateを別gateとして
事前登録してから進む。

### Q007ap 最終結果

validity 7/7、hypothesis 6/6が全て通過し、
「propagated-tube fixed-coordinate contraction certifies all-iterate MPFR-85 forward shadowing」
としてacceptedとした。

- fixed-coordinate full Lipschitz upper／gap:
  `0.9920957426381974 / 0.007904257361802534`
- initial／one-step coordinate defect upper:
  `6.261327601009932e-22 / 2.4093250948226748e-20`
- uniform coordinate／physical Wiener error upper:
  `3.0481359405954845e-18 / 8.803831096064757e-18`
- physical error／Q007ag tube state radius:
  `6.096261293035372e-8 < 1e-6`
- input／recurrence／result digest:
  `06692ce9d11691d2a45cd57220ea3e5e201b5c2beb2d0b55776a60f15456830f` /
  `108cb6d50ecaa2d9ad50c02777f6c0bb03a979903849149e30f686c8004fc1ce` /
  `1ee4dc09badbba0264ccc05317ba87de68557d5df148cb7085b158097d17a910`
- runner／artifact newline-normalized SHA-256:
  `095bd3cf728e916d937df22bf9e6773698801064213cd679af52d39719f94d3d` /
  `3b35ad0c3f8979f295214ae16c7be09f6a1047b2779f9eeabe3dabec759e49f0`

これでQ007ag拡大tubeについて、exact-state initialization、repaired-map tube induction、
内部stage positivity、same-initial sampling-time forward errorが一つの有限精度証明鎖として閉じた。
bi-infinite／backward shadowing、内部stage間距離、任意boundary初期化、他gridは未解決のままである。
Q009は再開せず、次の実験はQ011または別norm certificateを観測前に事前登録してから行う。

## Q011: boundary/forcing で candidate manifold は維持されるか

periodic forcing → Poiseuille → Couette の順に fixed point と spectrum を作り直す。
boundary mask rank、保存収支、normal attraction を測る。

## Q011a: nonzero-mean periodic forcingのfixed-point compatibility — 事前登録

### 問い

境界・drag・momentum repairを持たない周期D2Q9 mapへ、各siteで同じ非零body-force sourceを加えたとき、
定常fixed pointは存在し得るか。fixed point探索や固有値分類の前に、global momentum ledgerだけで
必要条件が破れるかを判定する。

このgateはQ007apのperiodic unforced manifoldをforced manifoldへ摂動継続するものではない。
まずnonzero-mean forcingの構造的compatibilityを独立に監査し、通らなければ次のfixed-point campaignは
zero-mean periodic forcingまたはwall momentum sinkを持つ問題として別登録する。

### 固定mapとsource

- gridはodd periodic \(17^2\)、\(\omega=3/2\)、checkerboard filterは\(\eta=1/100\)とする。
- 一段mapのstage順序を

  \[
  \Phi_F=\mathcal H_\eta\circ\mathcal S\circ
  (\mathcal C_\omega+S(F))
  \]

  とする。BGK collision後にsitewise sourceを加え、periodic streaming、population-wise
  conservative five-point filterを行う。
- D2Q9 weights／velocitiesは現行modelを固定し、state-independent rest-linear source

  \[
  S_q(F)=3w_q(c_{qx}F_x+c_{qy}F_y)
  \]

  を使う。Guo velocity correction、exact-difference forcing、half-step macroscopic velocityを
  結果観測後に追加しない。
- forceは全siteで

  \[
  F=(3\,2^{-40},0)
  \]

  と固定する。この選択では全source populationがdyadicとなる。exact source momentは

  \[
  \sum_qS_q=0,\qquad
  \sum_qc_qS_q=F
  \]

  でなければならない。
- boundary、drag、pressure gradient reset、global momentum projection／repair、Q007y repairは使わない。
  従ってglobal massは保存され、global momentum increment候補は各stepで

  \[
  \Delta P=(17^2F_x,17^2F_y)=(867\,2^{-40},0)
  \]

  と事前登録する。

### exact obstructionとspectrum診断

collisionはlocal mass／momentumを、periodic streamingとfilterはglobal mass／momentumを保存するため、
exact arithmeticでは任意の定義域内state \(f\) に対し

\[
\mathcal M(\Phi_F(f))-\mathcal M(f)=(0,867\,2^{-40},0)
\]

を要求する。従って\(\Phi_F(f)=f\)なら右辺は0でなければならず、登録forceとは矛盾する。
さらにpopulation \(\ell^1\) residualにはdual moment inequalityから

\[
\|\Phi_F(f)-f\|_1\ge867\,2^{-40}
\]

というstate-independent lower boundを登録する。

sourceはstate-independentなので、その微分は0である。rest stateでのforced-map Jacobianは
unforced filtered symbol

\[
D\Phi_F(f_{\rm rest};k)=h_\eta(k)A_\omega(k)
\]

と一致することを診断する。odd grid上のstrict unit-circle countは3を要求するが、rest stateは
forced mapのfixed pointではないため、これをforced fixed-point spectrumまたはstabilityとは呼ばない。
unit-circle判定は\(\bigl||\lambda|-1\bigr|<10^{-10}\)と固定する。

### finite implementation probe

- rest equilibrium、一様moving equilibrium
  \((\delta\rho,j_x,j_y)=(2^{-8},2^{-10},-2^{-11})\) 1個を使う。さらにseed `20260809`の
  standard-normal arrayをfixed global mass／momentum leafへ射影し、maximum absolute componentを1へ
  normalizeして\(2^{-18}\)倍した8個のpositive rest perturbationを使う。direction hashをartifactへ
  保存する。
- forced／unforced mapはcollision結果まで同じ値を共有し、その後の差だけを監査する。
- source populationのfloat値はexact dyadic値とbitwise一致、local source moment residualは
  absolute `<=2^-90`とする。
- forced-minus-unforced outputとuniform streamed／filtered sourceのmaximum component absolute errorを
  `<=5e-16`、compensated global moment差と登録\(\Delta P\)のmaximum absolute errorを
  `<=5e-14`とする。
- 上のseeded directionの先頭4個をrest stateで使い、central difference step
  `2^-12 / 2^-13 / 2^-14`でforced／unforced derivative actionを比較し、各方向のbest relative
  discrepancyを`<=1e-9`とする。これはsource微分0の実装回帰であり、
  fixed-point spectrum検証ではない。
- rest stateのforced one-step minimum populationを`>0`とし、obstructionが未定義mapや即時negative
  populationだけに由来しないことを確認する。

### validity gate

1. D2Q9 rational weight／velocity tableからsource populationとmass／momentum momentsをexactに再構成する。
2. float sourceが登録dyadic vectorとbitwise一致し、local moment residualが閾値内である。
3. 全10 probeでforced-minus-unforced state／global moment差が登録source／\(\Delta P\)を再現する。
4. source derivative zeroをfinite differenceで再現し、rest Fourier symbol、odd-grid strict unit count 3を
   unforced oracleと一致させる。
5. global momentum identity、非零increment、population \(\ell^1\) fixed-point residual lower boundを
   exact rationalで再現する。
6. 全値finiteなstrict JSON、source／probe／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、fixed-point obstructionを解釈しない。

### hypothesis gateと停止規則

validity通過時だけ次を独立に要求する。

1. 登録forceのspatial meanが非零である。
2. exact global momentum increment \(867\,2^{-40}\) がstrict positiveである。
3. 登録mapにこのincrementを相殺するboundary／drag／repair termがない。
4. fixed-point仮定とglobal momentum identityの矛盾、およびstrict residual lower boundが成立する。

全て通れば
`nonzero-mean periodic body force is incompatible with a fixed point of the registered conservative map`
としてnegative obstructionを`accepted`とする。incrementが0なら
`registered periodic forcing has zero mean and is not obstructed by the global momentum ledger`
としてこのnonzero-mean hypothesisを`not_certified`とする。validityは通るが矛盾が閉じなければ
`global momentum ledger does not exclude a registered forced fixed point`とする。

acceptedなら非零平均periodic fixed-point Newton solveやmanifold continuationを開始しない。次はQ011bで
zero-mean single-wave periodic forcingを事前登録し、そこで初めてforced fixed point、保存量葉、
Fourier-sector closure、spectrumを判定する。Poiseuille／Couetteはwall momentum exchangeを明示する
別gateまで開始しない。

### 主張境界

acceptedでもexact real-arithmetic mapのglobal-ledger obstructionに限る。finite-precision mapの
bitwise fixed point不存在、Guo／EDM forcingの高次精度、zero-mean forcing、drag、pressure boundary、
bounce-back、Poiseuille／Couette、forced invariant manifold、normal attraction、他gridを主張しない。
rest Jacobianはnon-fixed reference-state diagnosticに限り、forced fixed-point spectrumではない。
Q007apまでのunforced periodic certificateは変更しない。

### Q011a 最終結果

validity 6/6、hypothesis 4/4が全て通過し、
`nonzero-mean periodic body force is incompatible with a fixed point of the registered conservative map`
としてnegative obstructionをacceptedとした。

- exact per-step global momentum increment／population-l1 residual lower:
  `867*2^-40 / 867*2^-40`（`7.885319064371288e-10`）
- source moment residual:
  `0.0`
- maximum finite state／compensated global ledger error:
  `1.3877787807814457e-17 / 1.2032042029375134e-14`
- maximum best source-derivative discrepancy:
  `5.062223386808321e-14`
- rest reference strict unit-circle count／largest nonunit modulus:
  `3 / 0.9920954673551`
- source／probe／result digest:
  `75fd3fe1050b39a333f483375969a67c79ab9ec75009a2048359d0f0dabb7492` /
  `43d0b722ba63a45ccf6b5a41cffaef387448fcc2cd9324538887fd3169571001` /
  `9b1f0c1516a365481c72617957b30424a7873136d221bd164b6d0617c4c3d958`
- runner／artifact newline-normalized SHA-256:
  `41e45565066fd4c96c2ae927bc8cc6a1218377f67b711f6cc312ecbf0d1c68de` /
  `31c427660b10771af7756c249408606578a9b7a02d756bc77b918b56e7a5b14a`

従ってnonzero-mean periodic fixed-point Newton solveは開始しない。rest symbolはsource微分0を示す
non-fixed reference-state診断に限る。次はQ011bでzero-mean single-wave sourceを事前登録し、
forced fixed point、保存量葉、Fourier-sector closure、spectrumを初めて判定する。
wall-bounded Poiseuille／Couetteはさらに別gateとする。

## Q011b: zero-mean single-wave periodic forced fixed point — 事前登録

### 問い

Q011aと同じperiodic filtered BGK mapで、spatial meanが0のsingle-wave body forceならglobal momentum
obstructionを回避し、固定mass／momentum leaf上にpositiveな定常fixed pointを数値的に解けるか。
さらに、そのfixed pointの全x-Fourier blockを用いたfixed-leaf spectrumはstrictにstableか。

このgateはforced invariant manifoldをまだ構築しない。まずx-independent forced fixed point、
保存収支、nonlinear Fourier response、full linear spectrumを独立oracleとして固定する。

### 封印入力とforced map

- Q011a artifact／runner newline-normalized SHA-256:
  `31c427660b10771af7756c249408606578a9b7a02d756bc77b918b56e7a5b14a` /
  `41e45565066fd4c96c2ae927bc8cc6a1218377f67b711f6cc312ecbf0d1c68de`
- Q011a source／probe／result digest:
  `75fd3fe1050b39a333f483375969a67c79ab9ec75009a2048359d0f0dabb7492` /
  `43d0b722ba63a45ccf6b5a41cffaef387448fcc2cd9324538887fd3169571001` /
  `9b1f0c1516a365481c72617957b30424a7873136d221bd164b6d0617c4c3d958`

Q011a stored cycleをfresh replayし、validity 6/6、hypothesis 4/4、accepted classification、
source scheme、stage order、\(17^2\)、\(\omega=3/2\)、\(\eta=1/100\)をexactに再現する。
Q011a runnerはread-onlyとし、source definitionを変更しない。

force waveformを

\[
F_x(y)=A\cos(2\pi y/17),\qquad F_y(y)=0,qquad
A=3\,2^{-24}
\]

と固定し、全x siteへ同じ値をliftする。float実装は`numpy.cos(2*pi*y/17)`をそのまま使い、
結果観測後のmean subtractionやwaveform修正をしない。analytic discrete meanは0である。
float waveform sumのabsolute値を`<=1e-14`、orthonormal FFTで\(k_y=\pm1\)外のrelative
\(\ell^2\) leakageを`<=1e-13`とする。

各siteのsourceはQ011aと同じ

\[
S_q(y)=3w_qc_{qx}F_x(y)
\]

とし、collision後、periodic streaming前に加える。boundary、drag、momentum repairは使わない。
各siteで再構成したsourceの\((\rho,j_x,j_y)\)と\((0,F_x(y),0)\)のmaximum absolute
residualを`<=1e-20`、public forced stepとcollision→source→streaming→filterを独立に並べた
stage replayのmaximum absolute discrepancyを`<=1e-15`とする。

### fixed-leaf stripe solve

fixed pointはx-independent stripe \(f(y,q)\in\mathbb R^{17\times9}\)で解き、全17 x-siteへliftする。
target conserved momentsはstripeで\((17,0,0)\)、full gridで\((289,0,0)\)とする。
global moment matrixのorthonormal nullspace basis \(B\in\mathbb R^{153\times150}\)を
`scipy.linalg.null_space`で一度だけ作り、

\[
f(z)=f_{\rm rest}+Bz,qquad
r(z)=B^T(\Phi_F(f(z))-f(z))
\]

を解く。basis orthogonality、moment annihilation、dimensionをそれぞれ
Frobenius normで`<=1e-12 / <=1e-12 / 150`とする。

一段mapのanalytic Jacobianは、各siteのdensity／momentumに関するD2Q9 equilibrium derivative、
BGK、streaming、filterをchainして構成する。seed `20260812`の4 fixed-leaf direction、
central step `2e-5 / 1e-5 / 5e-6`で、best action relative errorを各方向`<=2e-8`とする。
有限差分は後述のrest linear-response stateで評価する。linear-response equationのrelative residualは
`<=1e-12`とする。

Newton法はanalytic reduced Jacobian

\[
Dr(z)=B^T(D\Phi_F(f(z))-I)B
\]

を使い、maximum 12 iterationとする。full stepがresidualを減らさない場合だけ
\(1,1/2,\ldots,1/64\)の最初のdecreasing factorを使い、それもなければ失敗とする。
次の二初期値を独立に走らせる。

1. zero coordinate \(z=0\)
2. rest linear response

   \[
   z_{\rm lin}=(I-B^TJ_0B)^{-1}B^T(\Phi_F(f_{\rm rest})-f_{\rm rest})
   \]

各solveでprojected residual \(\ell^2\)`<=5e-13`、full residual \(\ell^2\)`<=5e-12`、
maximum component residual `<=5e-13`を要求する。二解のpopulation \(\ell^2\) distanceを
`<=1e-11`とし、relative distanceはそのdistanceを二解それぞれのrestからの\(\ell^2\) departureの
大きい方で割って`<=1e-9`とする。各runはstep開始時のprojected residualが閾値内なら
停止し、そうでなければ最大12 Newton stepを試す。二startを同じprocess内でもう一度ずつ再実行し、
terminal coordinateとline-search traceのbitwise／exact JSON一致を要求する。結果観測後にmethod、
start、toleranceを変えない。

物理・spectrum診断のrepresentative stateはzero-start第1 runのterminal iterateとする。未収束でも同じ
有限stateで実装validity診断を完走するが、fixed-point／spectrumの科学的解釈はsolver hypothesis通過時
だけ行う。

### fixed pointの物理・Fourier gate

- minimum population／densityを別々に`>0`とする。
- full-grid global mass／momentum target residualをcompensated sumで`<=5e-11`とする。
- orthonormal y-FFTでfirst-harmonic \(j_x\) cosine amplitudeを
  \(2|\widehat j_x(1)|/\sqrt{17}\)と定義し、strict positiveかつforce amplitudeより大きくする。
- rest差のorthonormal y-FFTについて、\(k_y=0,\pm1,\pm2\)外のrelative \(\ell^2\) leakageを
  `<=1e-8`とする。これはsmall-amplitude sector concentrationであり、exact finite Fourier closureとは
  呼ばない。
- x-independent lift／stripe restriction roundtripをbitwise一致とする。

### full fixed-point spectrum

fixed pointはx translationを保つので、linearizationを17個の\(k_x\) blockへ分解する。各blockは
y×populationの153 complex次元とする。collision derivativeはfixed pointのy-dependent fieldで評価し、
streamingのx phase、periodic y shift、filterのx multiplierを明示的に組み込む。

- \(k_x=0\)のunrestricted blockではglobal mass／momentumに対応する
  \(|\lambda-1|\le10^{-9}\)のeigenvalueを3個要求する。
- stability判定では\(k_x=0\)だけを同じ\(B\)で150次元fixed leafへ制限し、\(k_x\ne0\)は153次元
  block全体を使う。
- 全blockをordered labelingではなくcomplex Schur spectrumとして扱う。reconstructionは
  \(\|J-QTQ^*\|_F/\max(\|J\|_F,\mathrm{tiny})\)、unitarityは
  \(\|Q^*Q-I\|_F\)とし、そのmaximumを各`<=1e-10`とする。
  \(k_x\leftrightarrow-k_x\) spectrum間のabsolute Hausdorff errorを`<=1e-10`とする。
- block action検証はseed `20260813`のstandard-normal real／imaginary y-population directionを
  \(k_x\) index `0 / 1 / 4 / 8`へ一つずつ割り当て、unit \(\ell^2\) normへ正規化してfull-gridへ
  liftする。block actionとfull-grid analytic Jacobian actionのrelative errorを各方向`<=2e-10`とする。
- 全fixed-leaf eigenvalueのmaximum modulusを`<=0.9999`とする。
- 全fixed-leaf \(I-J(k_x)\)のminimum singular valueを`>=1e-4`、maximum condition numberを
  `<=1e6`とする。

individual shear／acoustic labels、forced slow spectral subspace、spectral quotient、nonresonanceは
このgateで判定しない。

### validity gate

1. Q011a artifact／runner／scope／classification／gate／digestを封印し、stored cycleをfresh replayする。
2. registered cosine sourceのfloat mean、FFT support、source moments、stage orderが閾値内である。
3. fixed-leaf basis、analytic Jacobian、finite-difference action、linear-response equationを再現する。
4. 二Newton trace、residual、line-search decision、solution agreementを完全記録し、solver arithmeticが
   finiteかつdeterministicである。
5. x-Fourier block Jacobianをdirect full-grid actionの登録4 directionで`<=2e-10`に再現し、
   Schur／conjugacy residualが閾値内である。
6. 全値finiteなstrict JSON、input／fixed-point／spectrum／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、fixed point／stability hypothesisを解釈しない。

### hypothesis gateと停止規則

validity通過時だけ次を独立に要求する。

1. 二Newton startが全residual閾値内へ収束し、同じfixed pointへ一致する。
2. fixed pointがpositive、target fixed leaf、nontrivial first-harmonic response、登録sector leakage内である。
3. full x-Fourier fixed-leaf spectral radiusが`<=0.9999`である。
4. 全blockの\(I-J\) singular-value／condition gateが通る。

全て通れば
`zero-mean single-wave periodic forcing yields a numerically resolved stable fixed-leaf fixed point`
として`accepted`とする。fixed pointは解けるがspectral radius gateが落ちれば
`registered zero-mean forced fixed point is not spectrally stable on the fixed leaf`
として有効な`rejected`とする。solver hypothesisが閉じなければ
`registered zero-mean forced fixed point was not numerically certified`として`not_certified`とする。

acceptedでもfloating-point Newton／Schurによる単一grid・単一amplitudeのnumerical prequalificationに
限る。rigorous existence／uniqueness、basin、forced invariant manifold、slow-subspace selection、
nonresonance、normal attraction、finite-precision all-iterate shadowing、他amplitude／grid、boundary、
Poiseuille／Couetteを主張しない。acceptedなら次はQ011cでforced fixed pointにおけるslow
spectral clusterと外部gapを別途事前登録する。rejected／not_certifiedなら原因をfixed-point solveと
spectrumに分離し、同じ結果からamplitudeやthresholdを変更しない。

### Q011b 最終結果

validity 6/6、hypothesis 4/4を通過し、
`zero-mean single-wave periodic forcing yields a numerically resolved stable fixed-leaf fixed point`
として`accepted`とした。

- float force sum／FFT leakage:
  `-2.3822801641527197e-22 / 3.7252978093103943e-16`
- maximum source moment／stage replay discrepancy:
  `2.6469779601696886e-23 / 0.0`
- basis orthogonality／moment-annihilation residual:
  `1.259169632432682e-14 / 1.4118649012697392e-14`
- linear-response residual／maximum best Jacobian action error:
  `4.779732994797796e-14 / 3.105943967977383e-11`
- Newton accepted steps（zero／linear-response start）:
  `2 / 1`
- maximum terminal projected／full／component residual:
  `3.4838391155252677e-16 / 4.088062755440557e-16 / 1.6653345369377348e-16`
- two-solution absolute／forced-departure-relative distance:
  `7.901660672580398e-16 / 2.444328466505941e-11`
- minimum population／density:
  `0.027775908313351423 / 0.9999999999999997`
- compensated target residual／first-harmonic \(j_x\) amplitude／sector leakage:
  `5.898059818321144e-16 / 2.202356130540601e-05 / 9.755400055442727e-12`
- unrestricted zero-block unit count／fixed-leaf eigenvalue count:
  `3 / 2598`
- maximum fixed-leaf eigenvalue modulus:
  `0.9920954673551019` at \(k_x\) index 0
- minimum \(\sigma_{\min}(I-J)\)／maximum condition:
  `0.00649328212134047 / 360.53472657220163`
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

従って、零平均sourceではQ011aのglobal-ledger obstructionを回避し、登録fixed leaf上のpositive
fixed pointとstrictly stableな全x-Fourier spectrumを数値的に得た。ただし単一grid／amplitudeの
binary64 prequalificationであり、rigorous existence／uniqueness、forced slow cluster、
external gap、nonresonance、normal attraction、不変多様体は未認証である。次はQ011cでslow
spectral clusterと外部gapを事前登録する。

## Q011c: forced slow spectral cluster continuation — 事前登録

### 問い

Q006hで選んだunforced first-shell hydrodynamic 24-mode subspaceは、Q011bの零平均single-wave
forced fixed pointまで、固定保存量葉上の共役閉invariant clusterとして連続化できるか。さらに、
そのclusterは全external spectrumから分離され、linear modulusでstrictにnormally dominantか。

このgateでは個別shear／acoustic labelをforced endpointへ割り当てない。追跡対象はordered-Schur
invariant subspace、Riesz projector、cluster全体のeigenvalue setである。通過してもforced invariant
manifold、nonlinear normal attraction、nonresonance、homological equationはまだ主張しない。

### 封印入力

- Q011b artifact／runner newline-normalized SHA-256:
  `477202184694da1386c6b5bc0f0441e004a7a44f7a7b064f1d060d50adc66c27` /
  `bac9448f280ce2dfb2e1627ce1558b792cb53e05746b94246baa6c329b8c8ef0`
- Q011b input／fixed-point／spectrum／result digest:
  `53dea81353ed4bcd77ab0c06533528f6d867d8b1bfa80d3d2ac3eddd7cf7dfbb` /
  `8db05ad1e7ae7806b70b6330d798f6dad05bc8718027ba13cb315116b021b17c` /
  `3ab8866e141b64a4d1d81bdfae1a70c61d8e7964d8480e2bd7ec7c7e174850fc` /
  `66c4b579dbd7d7c391fd2017f165c2de251ecf850b7c485cb936b9742c8addf6`
- Q006h artifact newline-normalized SHA-256:
  `71ff668cbc247450029840bf5de71e6ecbd364c5fcca21c9e8ec8085a5ee956c`
- sealed package-source SHA-256:
  `114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2`

Q011b stored cycleをfresh replayし、validity 6/6、hypothesis 4/4、accepted classification、
forced fixed point、全2598 fixed-leaf spectrumをexact JSON一致で再現する。Q006hはread-onlyで
`cluster-complete filtered finite-ladder prequalification passed`、selected
\((\eta,\omega)=(0.01,1.5)\)、24-mode first-shell cluster、registered normal-gap threshold
\(10^{-6}\)、projector ceiling 100を再現する。

### fixed-point amplitude path

Q011b forceを

\[
F_x^{(t)}(y)=t\,3\,2^{-24}\cos(2\pi y/17),\qquad
t_j=j/8,\quad j=0,\ldots,8
\]

とscaleする。観測後のadaptive subdivisionは行わない。Q011bと同じ153×150 fixed-leaf basis、
analytic Jacobian、Newton最大12 step、line-search
\(1,1/2,\ldots,1/64\)、residual閾値を再利用する。

forward pathはrestから\(t_0\to t_8\)、backward pathはQ011b stored endpointから
\(t_8\to t_0\)へ進み、各solveの直前node stateを初期値とする。各nodeでprojected／full／maximum
component residualを`5e-13 / 5e-12 / 5e-13`以下とする。対応nodeのforward／backward state distanceを
`<=1e-11`、二stateのrest departureの大きい方を分母とするrelative distanceを`<=1e-8`とする。
ただし\(t=0\)はdepartureが厳密に0なのでabsolute gateだけを使い、relative gateの対象は非零8 nodeに
限定する。forward endpointとQ011b stored stripe stateも同じ二閾値内で一致させる。全trace、
line-search decision、state hashを保存する。

### unforced reference cluster

Q006hの8 first-shell wave

\[
(n_x,n_y)\in\{-1,0,1\}^2\setminus\{(0,0)\}
\]

にあるshear／acoustic-positive／acoustic-negativeの全3 modeをreferenceとする。外力後はy-translationが
失われるため、x-Fourier blockごとのselected dimensionだけを次のように固定する。

\[
\begin{array}{c|c|c}
k_x\text{ index} & t=0\text{ selected }k_y\text{ indices} & \dim_{\mathbb C}\\
\hline
0 & -1,+1 & 6\\
1 & -1,0,+1 & 9\\
16\ (-1) & -1,0,+1 & 9
\end{array}
\]

\(k_x=0\) blockはQ011bと同じ150次元fixed leafへ制限し、\(k_x=1,16\)は153次元full blockを使う。
従ってtotal selected complex dimensionは24で、\(k_x=1\)と16の共役制約および\(k_x=0\)の
real-conjugacy closureによりphysical real dimensionも24とする。

\(t=0\)ではregistered filtered Fourier symbolのhydrodynamic eigenvalue setをtargetとして
ordered complex Schur分解を行う。次nodeでは前node selected eigenvalue setと全current eigenvalueの
absolute-distance costをHungarian assignmentし、そのpartitionをnearest selected／excluded
Schur selectorへ渡す。cluster内部のpermutationは失敗としない。backward trackingはforward endpoint
clusterから逆順に同じ規則を使う。さらに\(t=1\)でunforced targetから直接選んだcontrol clusterを
一つ作る。

### path／projector gate

全9 node、3 selected blockで次を要求する。

- ordered selected dimensionが`6 / 9 / 9`で一定、Schur selector count failureが0。
- 隣接nodeのmaximum principal angleを`<=0.05` radとする。
- 各node selected rangeと対応unforced reference rangeのminimum singular-value alignmentを
  `>=0.95`とする。
- selected／excluded eigenvalue setのminimum absolute separationを`>=1e-6`とする。
- selected Riesz projector 2-normを`<=100`とする。
- Schur reconstruction relative residual、unitarity Frobenius residual、selected invariance relative
  residual、projector idempotency Frobenius residual、projector commutator relative residualを
  各`<=1e-10`とする。
- forward／backward対応clusterと、forward endpoint／direct endpoint controlのmaximum principal
  angleを各`<=1e-6`とする。
- \(k_x=1\) projectorと\(k_x=16\) projectorのcomplex-conjugacy relative error、selected-spectrum
  absolute Hausdorff errorを`<=1e-10`、subspace principal angleを`<=1e-6`とする。
- \(k_x=0\) selected projectorのimaginary relative normを`<=1e-10`とする。

individual eigenvector、forced shear／acoustic label、cluster内部branch permutationはgateに使わない。

### checkpoint external separation／normal dominance

\(t=0,1/2,1\)だけを登録checkpointとし、各selected blockのordered Schur partition

\[
T=\begin{pmatrix}T_s&C\\0&T_e\end{pmatrix}
\]

からSylvester operator

\[
\mathcal S=I_e\otimes T_s-T_e^T\otimes I_s
\]

を明示的に構成する。全9 checkpoint-blockのminimum singular valueを`>=1e-5`とする。

同じ3 checkpointでは全17個のx-Fourier fixed-leaf spectrumを再列挙する。selected 24 eigenvalueの
minimum modulusと、上記3 blockのexcluded eigenvalueおよび残り14 blockの全eigenvalueからなる
external spectrumのmaximum modulusを比較し、

\[
\Delta_{\rm normal}
=\min_{\lambda\in\sigma_s}|\lambda|
-\max_{\mu\in\sigma_e}|\mu|
\ge10^{-6}
\]

を要求する。全fixed-leaf spectral radiusも`<=0.9999`とする。参考値として
\(\log(\max|\sigma_e|)/\log(\min|\sigma_s|)\)を記録するが、整数spectral quotientやsmoothness classは
このgateで主張しない。

\(t=1\)のfull fixed-leaf spectral radius、unit count、resolvent singular-value／condition witnessは
Q011b artifactとabsolute`<=1e-12`で一致させる。

### validity gate

1. Q011b artifact／runner／四digest／stored cycleとQ006h artifact／selected family／package sourceを
   封印どおりfresh replayする。
2. 登録9-node fixed-point forward／backward pathがfiniteに完走し、residual、state agreement、
   Q011b endpoint reproductionを満たす。
3. unforced 8-wave×3-mode reference、`6 / 9 / 9` partition、fixed-leaf restriction、
   ordered-Schur／Riesz constructionを再現する。
4. 全nodeのSchur／projector／path reversal／direct endpoint／conjugacy診断が登録閾値内である。
5. 3 checkpointでSylvester operatorと全fixed-leaf spectrumを再列挙し、Q011b endpoint spectrumを
   登録誤差内に再現する。
6. 全値finiteなstrict JSON、input／path／spectrum／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、cluster hypothesisを解釈しない。

### hypothesis gateと停止規則

validity通過時だけ次を独立に要求する。

1. fixed-point amplitude pathが両方向で同じQ011b endpointへ接続する。
2. 24-dimensional conjugacy-closed selected clusterがdimension、alignment、adjacent／reversal／direct
   endpoint angle gateを通り、external clusterとの交換がない。
3. 全nodeのexternal eigenvalue separation、Riesz projector norm、3 checkpointのSylvester
   separationが閾値内である。
4. 3 checkpoint全てでglobal modulus normal-dominance gapが`>=1e-6`、full fixed-leaf spectrumが
   strictly stableである。

全て通れば
`the Q006h first-shell hydrodynamic subspace continues to a separated linearly normally dominant forced fixed-leaf spectral cluster`
として`accepted`とする。validityは通るがdimension exchange、separation、projector、
normal-dominanceのいずれかが落ちれば
`the registered first-shell cluster does not remain spectrally separated under forcing`
として`rejected`とする。

acceptedでもfinite 9-node amplitude path、単一\(17^2\) grid、単一endpoint amplitudeのlinear
prequalificationに限る。continuous-\(t\) theorem、rigorous projector enclosure、individual mode label、
external nonresonance、spectral quotient smoothness、forced SSM existence／uniqueness、quadratic chart、
normal attraction、basin、他grid／amplitude、wall boundaryを主張しない。acceptedなら次はQ011dで
forced selected clusterに対するquadratic external nonresonance／homological operatorを別途事前登録する。

### Q011c 最終結果

validity gateは`5 / 6`で、`checkpoint_spectrum_and_q011b_endpoint_reproduce`だけが失敗した。
停止規則どおりhypothesisは解釈せず、
`registered forced spectral-cluster audit is invalid`として`inconclusive`とした。

- forward／backward fixed-point 9 node、unforced `6 / 9 / 9` reference、27 ordered-Schur
  selection、path reversal、direct endpoint、共役projector診断は全てvalid。
- maximum adjacent principal angle／minimum reference alignment:
  `1.0421788015551248e-05 / 0.9999999965243628`
- minimum external eigenvalue separation／maximum projector 2-norm:
  `0.023905378580598713 / 1.5115930042152532`
- minimum 9-block Sylvester separation:
  `0.019362054767979874`
- minimum global modulus normal gap／maximum full fixed-leaf radius:
  `0.002061121154971146 / 0.9920954673551043`
- Q011b stored endpointとのstate absolute／relative distance:
  `3.2437399411382716e-15 / 1.0034303173230714e-10`
- spectral radius／minimum \(\sigma(I-J)\)のartifactとの差:
  `1.6653345369377348e-15 / 1.231653667943533e-16`（通過）
- maximum \(\kappa_2(I-J)\)のartifactとの差:
  `7.048583938740194e-12`（登録`1e-12`を超過）
- minimum-singular／maximum-condition witness index:
  Q011b stored `16`、continued endpoint `1`。両者は実写像の共役blockである。

従ってraw cluster／checkpoint hypothesis checkは全てtrueだが、これをacceptedへ読み替えない。
閾値やamplitude pathも変更しない。次はQ011cのartifactを封印し、(i) stored endpointのexact replay、
(ii) continued endpointのstate perturbation、(iii) \(k_x=\pm1\)共役orbit上のset-valued extrema、
(iv) resolvent metricの局所感度を分離する修復gateを観測前に事前登録する。これを通すまでQ011dへ
進まない。

- input／path／spectrum／result digest:
  `7d8d4a593dc29a715c995e237890da4de17314c4feffabe10111b289120435ee` /
  `06254ea5569d8b0c8c5369477c82ea685284aec9970574c46c24fea749280b92` /
  `5b1e79280b752268248f5150dd12c73a96719cb20d86cbd34fb3ff1e1b8b472c` /
  `4b41c4e7bda3a45f1ece871c183d321bed637d255053e22a82e7000dd83f5751`
- runner／artifact newline-normalized SHA-256:
  `10222da26fe14b97cd9565c517838d3a03e21f19e605d4a60cb2461e011d1d13` /
  `dbb562dd3628dc7589219baa94ae6791e084847f302c69dbcdc328b94ac6d2b3`

## Q011c1: conjugacy-orbit endpoint reproducibility localization — 事前登録

### 問いと停止規則

Q011cの唯一のvalidity failureは、Q011b stored endpointと許容誤差内のcontinued endpointの間で、
\(k_x=16\)から\(k_x=1\)へworst resolvent witnessが交換し、maximum condition numberの
absolute differenceが登録`1e-12`を超えたことで説明できるか。具体的には、これは

\[
\{1,16\}
\]

という同じcomplex-conjugacy orbit内の数値tie交換であり、continued block singular valuesの変化は
実測Jacobian perturbationから得る行列摂動区間内に収まるか。

Q011cのthreshold、gate、`inconclusive` classificationは変更しない。このgateもQ011cを再採点せず、
失敗原因だけを`conjugate-witness tie instability`または`unexplained endpoint discrepancy`に
分類する。validity failureなら`inconclusive`とする。

### 封印入力

- Q011c artifact／runner newline-normalized SHA-256:
  `dbb562dd3628dc7589219baa94ae6791e084847f302c69dbcdc328b94ac6d2b3` /
  `10222da26fe14b97cd9565c517838d3a03e21f19e605d4a60cb2461e011d1d13`
- Q011c input／path／spectrum／result digest:
  `7d8d4a593dc29a715c995e237890da4de17314c4feffabe10111b289120435ee` /
  `06254ea5569d8b0c8c5369477c82ea685284aec9970574c46c24fea749280b92` /
  `5b1e79280b752268248f5150dd12c73a96719cb20d86cbd34fb3ff1e1b8b472c` /
  `4b41c4e7bda3a45f1ece871c183d321bed637d255053e22a82e7000dd83f5751`
- Q011b stored／Q011c forward endpoint state SHA-256:
  `612ef4aca91a5c0100286988e0e7979342a9046c3c78fe60ee59ca4e232a7613` /
  `275726b73e03e9d5cb8300b672233f7497abc6b607c1f76c2ef4b176e3788be7`
- sealed package-source SHA-256:
  `114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2`

Q011c cycleをfresh replayし、artifactとのexact JSON一致、validity `5 / 6`、唯一のfailed gate、
`inconclusive` classification、全raw cluster／checkpoint hypothesis checkを再現する。
stored stateとforward endpointもsealed hashから一意に再構築する。

### block metricと共役orbit

両endpointについてQ011cと同じ17個のfixed-leaf block \(J_k\) を構成し、

\[
A_k=I-J_k,\qquad
m_k=\sigma_{\min}(A_k),\quad
M_k=\sigma_{\max}(A_k),\quad
\kappa_k=M_k/m_k
\]

をfull SVDで計算する。各SVDのreconstruction relative residualと左右unitarity Frobenius residualを
`<=1e-10`とする。block matrix、singular spectrum、metricのhashを保存する。

判定単位は

\[
\{0\},\{1,16\},\{2,15\},\ldots,\{8,9\}
\]

の9 conjugacy orbitとする。各endpoint、各非零orbitで
\(J_k=\overline{J_{17-k}}\)のrelative Frobenius residualを`<=1e-12`とする。
個別indexの一致は要求しない。

stored endpointではQ011b artifactのunit count、spectral radius、minimum \(m_k\)、maximum
\(\kappa_k\)をabsolute `1e-12`以内で再現し、original witness index `0 / 16 / 16`もそのまま
controlとして記録する。continued endpointではQ011c artifactの対応値・index・failure booleanを
exact JSONで再現する。

### perturbation enclosure

stored／continuedの対応block差に対し、binary64丸めpaddingを

\[
p_k=64\,\epsilon_{\rm mach}
\max\!\left(1,\|A_k^{s}\|_F,\|A_k^{c}\|_F\right),
\qquad
d_k=\|A_k^{c}-A_k^{s}\|_F+p_k
\]

と固定する。\(d_k<m_k^s\)を要求し、Weyl boundから

\[
\begin{aligned}
m_k^c&\in[\max(0,m_k^s-d_k),\,m_k^s+d_k],\\
M_k^c&\in[\max(0,M_k^s-d_k),\,M_k^s+d_k],\\
\kappa_k^c&\in
\left[
\frac{\max(0,M_k^s-d_k)}{m_k^s+d_k},
\frac{M_k^s+d_k}{m_k^s-d_k}
\right]
\end{aligned}
\]

を全17 blockで満たすことを要求する。2-normをFrobenius normで上から置いた保守的区間であり、
観測後に係数64を変更しない。

さらに上の区間だけを使い、

- spectral-radius actual witness orbitは両stateで`{0}`のまま、
- minimum-\(m_k\) orbitは`{1,16}`で、そのorbitのupper boundが全外部orbitのlower boundより小さい、
- maximum-\(\kappa_k\) orbitは`{1,16}`で、そのorbitのlower boundが全外部orbitのupper boundより大きい、

ことを要求する。これにより個別indexが交換しても、extremal orbitが外部orbitと交換していないことを
摂動区間込みで判定する。stored／continued exact witnessが異なり、双方`{1,16}`に属することも
localization hypothesisに含める。

### validity gate

1. Q011c artifact／runner／四digest／cycle、Q011b input、package sourceを封印どおり再現する。
2. stored／continued endpoint hash、Q011c path distance、Q011c endpoint failure recordをexactに再現する。
3. 34 block SVDがfiniteに完走し、dimension、reconstruction、unitarity、matrix conjugacyを満たす。
4. stored endpointでQ011b spectrum／resolvent controlを元の`1e-12`以内に再現する。
5. 全値finiteなstrict JSON、input／metric／enclosure／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、localization hypothesisを解釈しない。

### hypothesis gate

validity通過時だけ次を全て要求する。

1. 全17 blockのcontinued \(m_k,M_k,\kappa_k\)が登録perturbation enclosure内にある。
2. radius witness orbit`{0}`、minimum-singular／maximum-condition orbit`{1,16}`が両endpointで一致する。
3. minimum-singular／maximum-condition winning orbitはenclosure込みで全外部orbitからstrictに分離する。
4. exact witness交換は`16 -> 1`で同じ共役orbit内に限られ、Q011cのraw cluster／normal-dominance
   diagnosticsは全てtrueのままである。

全て通れば
`the Q011c endpoint failure is localized to perturbation-consistent conjugate-witness tie instability`
として`accepted`とする。一つでもvalidに失敗すれば
`the Q011c endpoint discrepancy is not explained by conjugate-witness tie instability`として
`rejected`とする。

acceptedでもQ011c自体は`inconclusive`のままで、forced cluster selection、individual mode label、
continuous-amplitude theorem、rigorous SVD enclosure、external nonresonance、forced invariant manifold、
normal attractionは主張しない。acceptedなら次は、共役orbit意味論を最初から採用し、Q011cで使って
いないheld-out amplitude nodesを含むQ011c2 reissued cluster gateを別途事前登録する。rejectedなら
Q011c endpoint Jacobian差のblock／state component原因をさらに分解し、Q011dへは進まない。

### Q011c1 最終結果

validity `5 / 5`、hypothesis `4 / 4`を通過し、
`the Q011c endpoint failure is localized to perturbation-consistent conjugate-witness tie instability`
として`accepted`とした。

- 34 full SVDのmaximum reconstruction／unitarity residual:
  `2.94286841789878e-15 / 2.5479952376461563e-14`
- maximum matrix-conjugacy relative residual:
  `6.577836273397531e-16`
- maximum resolvent Frobenius difference／registered perturbation bound:
  `4.2352782748696136e-14 / 2.9468087840500247e-13`
- maximum minimum／maximum singular-value change utilization:
  `0.0009382376259671139 / 0.010647618003265125`
- minimum-singular winning-orbit interval margin:
  `2.694725883406468e-10`
- maximum-condition winning-orbit interval margin:
  `0.5844815558106689`
- stored／continued radius orbit:
  `{0} / {0}`
- stored／continued minimum-singular and maximum-condition orbit:
  `{1,16} / {1,16}`
- exact individual witness exchange:
  minimum singular、maximum conditionとも`16 -> 1`

従ってQ011c endpoint差は全17 blockで登録摂動区間内にあり、extremal orbitは外部orbitから
区間込みでstrictに分離した。個別index交換は同じreal-map conjugacy orbit内のtie-breakingである。
ただしQ011c1は同じ二endpointを使うfailure-localization gateなので、Q011cの`inconclusive`、
validity `5 / 6`、失敗閾値`1e-12`を変更していない。forced clusterもまだselectedと呼ばない。

- input／metric／enclosure／result digest:
  `e9ea01348fe839dd745c3ccb7cf2e622bec3c0a4f080a1ab1c62a92a02ced064` /
  `fca5a81f3fc47e24a6f17578065adb527d892400d5d88c8eb18cf7089e234a9e` /
  `7a6cd761f88b328c2ffa74de5b9fb7952f454b86a99630d6266973e8fa6fea20` /
  `ad8b47548ebc04595246301864314502158e686520197377b3a33d30db1d4f86`
- runner／artifact newline-normalized SHA-256:
  `1f777dc50c6748cb8d8a64d643822b55733ac247b5de7d08b119d628b63c52a6` /
  `939baa85fa4db1efaf701985d81665f863e5f77f6ec2c95cfc2bacf004c0c45c`

次は共役orbit endpoint semanticsを最初から固定し、Q011cで未使用のforce-amplitude midpointを
holdoutにするQ011c2を観測前に事前登録する。それを通るまでQ011dへ進まない。

## Q011c2: held-out forced spectral-cluster reissue — 事前登録

### 問いと独立性

Q011c1で局在したpointwise witness問題を最初から共役orbit意味論へ置き換え、Q011cで未使用だった
8個のforce-amplitude midpointでも、Q006h first-shell 24-mode subspaceはdimension exchangeなく
継続し、external spectrumから分離され、linear modulusでnormally dominantか。

Q011cの9 node

\[
t=j/8,\qquad j=0,\ldots,8
\]

をtraining／reproduction nodeとし、新しいholdoutを

\[
t=(2j+1)/16,\qquad j=0,\ldots,7
\]

と固定する。reissued pathは両者を合わせた\(t=j/16\), \(j=0,\ldots,16\)の17 nodeである。
観測後のnode追加、adaptive subdivision、threshold変更は行わない。

### 封印入力

- Q011c1 artifact／runner newline-normalized SHA-256:
  `939baa85fa4db1efaf701985d81665f863e5f77f6ec2c95cfc2bacf004c0c45c` /
  `1f777dc50c6748cb8d8a64d643822b55733ac247b5de7d08b119d628b63c52a6`
- Q011c1 input／metric／enclosure／result digest:
  `e9ea01348fe839dd745c3ccb7cf2e622bec3c0a4f080a1ab1c62a92a02ced064` /
  `fca5a81f3fc47e24a6f17578065adb527d892400d5d88c8eb18cf7089e234a9e` /
  `7a6cd761f88b328c2ffa74de5b9fb7952f454b86a99630d6266973e8fa6fea20` /
  `ad8b47548ebc04595246301864314502158e686520197377b3a33d30db1d4f86`
- Q011c artifact／runner SHA-256:
  `dbb562dd3628dc7589219baa94ae6791e084847f302c69dbcdc328b94ac6d2b3` /
  `10222da26fe14b97cd9565c517838d3a03e21f19e605d4a60cb2461e011d1d13`
- Q011c input／path／spectrum／result digest:
  `7d8d4a593dc29a715c995e237890da4de17314c4feffabe10111b289120435ee` /
  `06254ea5569d8b0c8c5369477c82ea685284aec9970574c46c24fea749280b92` /
  `5b1e79280b752268248f5150dd12c73a96719cb20d86cbd34fb3ff1e1b8b472c` /
  `4b41c4e7bda3a45f1ece871c183d321bed637d255053e22a82e7000dd83f5751`
- Q011b stored endpoint state SHA-256:
  `612ef4aca91a5c0100286988e0e7979342a9046c3c78fe60ee59ca4e232a7613`
- sealed package-source SHA-256:
  `114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2`

Q011c1をfresh replayし、validity `5 / 5`、hypothesis `4 / 4`、accepted classificationと
四digestをexactに再現する。Q011cも`5 / 6`、`inconclusive`、唯一のendpoint failure、raw
cluster／checkpoint diagnostics trueをexactに保存する。いずれの過去判定も変更しない。

### 17-node fixed-point path

Q011cと同じfixed-leaf basis、analytic Jacobian、Newton最大12 step、line-search列、residual閾値を
そのまま使う。forwardはrestから0→1、backwardはQ011b stored endpointから1→0へ17 nodeを進む。

- 各solveのprojected／full／maximum-component residual:
  `<=5e-13 / 5e-12 / 5e-13`
- 全17対応nodeのforward／backward state absolute distance:
  `<=1e-11`
- 非零16 nodeのrest-departure relative distance:
  `<=1e-8`
- forward endpoint／Q011b stored stateも同じ二閾値。
- 全forward／backward stateのpopulationとdensityをstrict positiveとする。

training 9 nodeでは、Q011c original pathを別に再構築し、reissued stateとのabsolute／relative distanceを
同じ`1e-11 / 1e-8`以内とする。\(t=0\)のrelative gateは使わない。全traceとstate hashを保存する。

### 17-node cluster path

Q011cと同じunforced reference、selected block \(k_x=0,1,16\)、dimension`6 / 9 / 9`、Hungarian
eigenvalue-set assignment、ordered complex Schur selectorを変更しない。17 node全てで

- adjacent maximum principal angle `<=0.05`、
- reference minimum singular alignment `>=0.95`、
- selected／excluded eigenvalue absolute separation `>=1e-6`、
- Riesz projector 2-norm `<=100`、
- Schur reconstruction、unitarity、invariance、projector idempotency／commutator residual
  `<=1e-10`、
- \(k_x=\pm1\) projector／spectrum conjugacy `<=1e-10`、subspace angle `<=1e-6`、
- \(k_x=0\) projector imaginary relative norm `<=1e-10`

を要求する。forward／backward対応clusterのangle、forward endpoint／unforced-target direct
endpointのangleも`<=1e-6`とする。

さらにtraining 9 nodeではQ011c original selected rangeとのangleを`<=1e-6`、selected-spectrum
Hausdorff errorを`<=1e-10`とする。Q011b stored endpointからunforced targetで直接選んだcanonical
clusterを追加し、forward endpointとのangleを各block`<=1e-6`とする。個別branch labelやcluster内
permutationは使わない。

### 8 held-out checkpoint

holdout 8 node全てでQ011cと同じ明示的Sylvester operator

\[
\mathcal S=I_e\otimes T_s-T_e^T\otimes I_s
\]

を3 selected blockについて構成し、全24 operatorのminimum singular valueを`>=1e-5`とする。
同じ8 nodeで全17 fixed-leaf block、合計2598 eigenvalueを再列挙し、

- selected 24／external 2574のcountをexactに再現、
- global modulus normal-dominance gap `>=1e-6`、
- full fixed-leaf spectral radius `<=0.9999`

を要求する。Q011cの3 training checkpoint値はsealed replayだけに使い、held-out decisionへ混ぜない。

### endpoint conjugacy-orbit semantics

Q011b stored endpointとreissued forward endpointについてQ011c1と同じ34 full SVDを行い、
reconstruction／unitarity`<=1e-10`、matrix conjugacy`<=1e-12`を要求する。
Q011c1と同じ固定式

\[
d_k=\|A_k^c-A_k^s\|_F+
64\epsilon_{\rm mach}\max(1,\|A_k^s\|_F,\|A_k^c\|_F)
\]

から全17 blockの\(\sigma_{\min}\)、\(\sigma_{\max}\)、\(\kappa_2\) intervalを作り、continued値を
全て囲む。radius winning orbitは`{0}`、minimum-singular／maximum-condition winning orbitは
`{1,16}`とし、後者二つはinterval込みで全外部orbitからstrictに分離させる。個別indexの一致、
Q011b condition numberとの固定absolute differenceはgateにしない。

### validity gate

1. Q011c1／Q011c／Q011b artifact、runner、全digest、cycle、package sourceを封印どおりfresh replayする。
2. 17-node forward／backward Newton path、training-node reproduction、positivity、state hashを再現する。
3. unforced referenceと17-node ordered-Schur／projector／conjugacy constructionがstructurally validである。
4. training cluster、direct endpoint、canonical stored-endpoint controlを登録閾値内に再現する。
5. 8 held-out node × 3 Sylvesterと8 full spectrumを完全列挙する。
6. endpoint 34 SVD、matrix conjugacy、Weyl intervalを登録式どおり構成する。
7. 全値finiteなstrict JSON、input／path／holdout-spectrum／endpoint／result digest、
   runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、cluster hypothesisを解釈しない。

### hypothesis gateと判定

validity通過時だけ次を全て要求する。

1. 17-node fixed-point pathが両方向で同じpositive branchを通り、Q011b endpointへ接続する。
2. 17 node全てで24-dimensional conjugacy-closed clusterがdimension、alignment、
   adjacent／reversal／training／direct／canonical angle gateを通る。
3. 全17 nodeのexternal gap／projectorと、全24 held-out Sylvester separationが閾値内である。
4. 8 held-out node全てでglobal normal-dominance gapとstrict fixed-leaf stabilityが成立する。
5. endpoint resolvent metricがQ011c1のorbit意味論とperturbation interval gateを通る。

全て通れば
`the forced first-shell cluster passes a conjugacy-orbit reissue with eight held-out amplitude nodes`
として`accepted`とし、この有限数値prequalificationの範囲でforced candidate spectral clusterを
selectedとする。validだが一つでも落ちれば
`the forced first-shell cluster fails the registered held-out reissue`として`rejected`とする。

acceptedでもQ011cの`inconclusive`は変更しない。これは単一17² grid、登録17 amplitude node、
binary64 Newton／Schur／SVDによるfinite prequalificationであり、continuous-\(t\) theorem、
rigorous projector／SVD enclosure、individual forced-mode label、external nonresonance、
spectral-quotient smoothness、forced SSM existence／uniqueness、quadratic chart、nonlinear normal
attraction、basin、他grid／amplitude、wall boundaryは主張しない。acceptedの場合だけQ011dの
quadratic external nonresonance／homological operatorを事前登録する。

### Q011c2 最終結果

validity `7 / 7`、hypothesis `5 / 5`を通過し、
`the forced first-shell cluster passes a conjugacy-orbit reissue with eight held-out amplitude nodes`
として`accepted`とした。

- 17-node forward／backward maximum state distance:
  `5.037082596836928e-15`
- 9 training-node maximum state distance:
  `4.318359172954769e-15`
- endpoint Q011b stored-state absolute／relative distance:
  `9.417935011590327e-16 / 2.913378288239695e-11`
- minimum population／density:
  `0.027775908313351423 / 0.9999999999999997`
- maximum structural residual／adjacent principal angle:
  `7.560599367895308e-14 / 5.2108940113403335e-06`
- minimum reference alignment／external separation:
  `0.999999996524363 / 0.02390537858060371`
- maximum projector norm／reversal angle:
  `1.5115930042152512 / 2.009181800848714e-13`
- maximum training／canonical endpoint angle:
  `1.8103036342337398e-13 / 8.532131573213541e-14`
- minimum 24 held-out Sylvester separation:
  `0.019362054855570406`
- minimum 8 held-out global normal gap:
  `0.0020611211556098574`
- maximum 8 held-out full fixed-leaf radius:
  `0.9920954673551043`
- endpoint resolvent difference／registered bound:
  `1.1428197375089487e-14 / 2.639179006344862e-13`
- endpoint minimum-singular／maximum-condition orbit margin:
  `2.6953366361742725e-10 / 0.5844815592084842`

8 held-out nodeの全24 Sylvester operator、20,784 fixed-leaf eigenvalue、normal gap、stabilityが
登録閾値を通過した。training control、direct endpoint、Q011b stored canonical endpoint、
共役orbit endpoint semanticsも通った。従ってQ011c自体の`inconclusive`は変更しない一方、
独立holdoutを持つQ011c2としてcandidate forced spectral clusterをselectedとする。

- input／path／holdout-spectrum／endpoint／result digest:
  `de4b0c4d38d0efcff9c7db4bbef66ba6d081a6703c732dbd7116a294020459f2` /
  `36be8801af32ae178e91e049b2640ed4bb058107abdf2df2af8860930c53c27d` /
  `d7319399578d3755ee0679122dec5e6b6d3454e394295bd62886920d104b0d72` /
  `8c78791883b82f4a964d0c102006d9295b7b96733e77dea93249f30dc427b6a8` /
  `8c23b985d69ffaa980e752e5d262184c0a6d466681d9d44fa4f0e9101df02b0c`
- runner／artifact newline-normalized SHA-256:
  `87bdfc1ed20e6e68e4a395d36399adbab19e82809c626ecefa65a342ce42b9d2` /
  `c1794ca72eebd60c4bc097278495218e9e2d2e84bdacd0f478e510a80fcba42a`

次はQ011dで、selected 24-dimensional forced clusterに対するquadratic external
nonresonance、spectral quotient、homological operatorを観測前に事前登録する。

## Q011d: forced quadratic external homological-family prequalification — 事前登録

### 問いと範囲

Q011c2でselectedとしたforced 24-dimensional clusterについて、quadratic monomial全300個の
external graph-gauge homological blockは数値的に非共鳴であり、5個の\(k_x\)-sector Sylvester
operatorは登録probeを安定に解けるか。

このgateではforced-map Hessian、quadratic forcing、\(W_2\)、\(R_2\)をまだ構築しない。
通過してもquadratic invariant chart、不変性残差次数、SSM existence／uniqueness、nonlinear normal
attractionは主張しない。まずlinear selected／quotient dynamicsとquadratic input actionだけを固定する。

### 封印入力

- Q011c2 artifact／runner newline-normalized SHA-256:
  `c1794ca72eebd60c4bc097278495218e9e2d2e84bdacd0f478e510a80fcba42a` /
  `87bdfc1ed20e6e68e4a395d36399adbab19e82809c626ecefa65a342ce42b9d2`
- Q011c2 input／path／holdout-spectrum／endpoint／result digest:
  `de4b0c4d38d0efcff9c7db4bbef66ba6d081a6703c732dbd7116a294020459f2` /
  `36be8801af32ae178e91e049b2640ed4bb058107abdf2df2af8860930c53c27d` /
  `d7319399578d3755ee0679122dec5e6b6d3454e394295bd62886920d104b0d72` /
  `8c78791883b82f4a964d0c102006d9295b7b96733e77dea93249f30dc427b6a8` /
  `8c23b985d69ffaa980e752e5d262184c0a6d466681d9d44fa4f0e9101df02b0c`
- Q011b stored endpoint state SHA-256:
  `612ef4aca91a5c0100286988e0e7979342a9046c3c78fe60ee59ca4e232a7613`
- Q006i unforced quadratic artifact SHA-256:
  `347d5349af349618333df17733ba372c8ca6f5ee02784a9e788898acefb5db89`
- sealed package-source SHA-256:
  `114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2`

Q011c2をfresh replayし、validity `7 / 7`、hypothesis `5 / 5`、accepted classification、5 digestを
exactに再現する。Q011c originalの`inconclusive`とQ011c1 localizationも変更しない。Q006iは
read-only calibrationとしてpair count 300、minimum operator singular value
`0.00015502435597333105`、maximum condition `14513.930547954875`、singular block 0を再現する。

### canonical forced linear split

base pointはQ011b stored endpointとする。Q011c2と同じunforced targetから\(k_x=0,1,16\)の
ordered-Schur clusterを直接選び、selected dimensionsを`6 / 9 / 9`とする。selected dynamicsを

\[
R_1=\operatorname{diag}(T_{s,0},T_{s,1},T_{s,16})\in\mathbb C^{24\times24}
\]

とする。external quotient dynamicsは

\[
A_{e,k}=
\begin{cases}
T_{e,k}, & k=0,1,16,\\
T_k, & k=2,15,
\end{cases}
\]

とする。\(k=0\)は150-dimensional fixed leaf内なのでexternal dimension 144、
\(k=1,16\)も144、\(k=2,15\)はfull 153とする。\(k=2,15\)はcomplex Schurでunitary triangularize
する。全Schur reconstruction／unitarity／invariance／projector residualを`<=1e-10`、
conjugate-sector spectrum Hausdorff errorを`<=1e-10`とする。

全17 fixed-leaf blockも再列挙し、selected 24／external 2574、normal gap`>=1e-6`、
full radius`<=0.9999`を要求する。spectral quotient diagnostic

\[
q_{\rm spec}=
\frac{\log\max_{\mu\in\sigma_e}|\mu|}
{\log\min_{\lambda\in\sigma_s}|\lambda|}
\]

をfiniteに記録し、`1<q_spec<2`を確認する。ただし整数smoothness classやuniqueness次数の定理とは
解釈しない。

### symmetric quadratic input action

selected coordinateはblock順\(k_x=0,1,16\)、各block内Schur順とする。unordered pair
\((i,j)\), \(0\le i\le j<24\)をlexicographicに全列挙し、pair countを
\(\binom{25}{2}=300\)とする。output sectorは\(k_i+k_j\bmod17\)で決める。

| output \(k_x\) | pair count | external dimension | homological scalar dimension |
|---:|---:|---:|---:|
| 0 | 102 | 144 | 14,688 |
| 1 | 54 | 144 | 7,776 |
| 16 | 54 | 144 | 7,776 |
| 2 | 45 | 153 | 6,885 |
| 15 | 45 | 153 | 6,885 |

monomial vectorを\(m_{ij}(a)=a_i a_j\)とし、

\[
m(R_1a)=K\,m(a)
\]

を満たす300×300 symmetric-product matrix \(K\)を直接assemblyする。sector外leakageを
`<=1e-12`、seed `20260821`の8 normalized complex directionでaction relative errorを
`<=1e-12`とする。各sector \(K_k\)のspectrumと、対応selected eigenvalue product multisetの
Hausdorff errorを`<=1e-10`とする。

### 300 external homological block

各pairのmultiplier product \(\mu_{ij}\)とoutput sector \(k\)に対し、

\[
H_{ij}=A_{e,k}-\mu_{ij}I
\]

を構成する。全300 blockでfull singular spectrum、numerical rank、spectral distance、
condition numberを計算する。rank thresholdは

\[
100\,\epsilon_{\rm mach}\,
\max(\operatorname{shape}H_{ij})\,\sigma_{\max}(H_{ij})
\]

とする。seed `20260820`のpairごとのnormalized complex RHSを`numpy.random.Generator`で順に生成し、
direct solve relative residualも保存する。

登録thresholdは次のとおり。

- numerical singular block count: 0
- minimum \(\sigma_{\min}(H_{ij})\): `>=1e-5`
- minimum spectral distance
  \(\min_{\nu\in\sigma(A_{e,k})}|\nu-\mu_{ij}|\): `>=1e-5`
- maximum condition number: `<=1e6`
- maximum direct-solve relative residual: `<=1e-10`

sector \(1/16\)、\(2/15\)ではpair-product、smallest-singular、condition multisetのconjugacy
Hausdorff／relative discrepancyを各`<=1e-8`とする。個別shear／acoustic labelは付けない。

### 5 sector-wide Sylvester probe

各sectorで

\[
\mathcal H_k(X)=A_{e,k}X-XK_k
\]

を使う。seed `20260822`からsectorごとに4 normalized complex RHS、合計20 probeを生成し、
`scipy.linalg.solve_sylvester(A_e,-K,B)`で解く。

- maximum relative equation residual: `<=1e-10`
- maximum response amplification \(\|X\|_F/\|B\|_F\): `<=1e6`
- nonfinite／solver failure: 0

とする。これはoperator normのrigorous upper boundではなく、full nonnormal sector actionに対する
登録probe診断である。invertibilityの主判定はcomplete pair-product spectrumと300 blockの
nonresonanceから行う。

### validity gate

1. Q011c2／Q011c1／Q011c／Q011b、Q006i、package sourceを封印どおり再現する。
2. canonical stored-endpoint selected／external Schur splitと全fixed-leaf spectrumをstructurally再現する。
3. 300 pair、sector count`102 / 54 / 54 / 45 / 45`、各dimension、pair hashを完全再現する。
4. symmetric-product \(K\)のaction、sector closure、product spectrumを独立に再現する。
5. 全300 SVD／rank／direct solveと20 sector-wide Sylvester probeを完全列挙する。
6. conjugate-sector scalar diagnosticsが登録閾値内である。
7. 全値finiteなstrict JSON、input／linear-split／pair-family／sector-probe／result digest、
   runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、nonresonance hypothesisを解釈しない。

### hypothesis gateと判定

validity通過時だけ次を全て要求する。

1. 全300 external homological blockがfull rankでminimum singular／spectral-distance gateを通る。
2. 全300 condition／direct-solve residualが登録上限内である。
3. 全5 sectorの\(K\) spectrumがselected pair productsを再現し、conjugate sectorが閉じる。
4. 全20 sector-wide Sylvester probeがresidual／amplification gateを通る。
5. canonical forced clusterがglobal normal dominance／stabilityを保持し、\(1<q_{\rm spec}<2\)である。

全て通れば
`the forced quadratic external homological family is numerically nonresonant and solvable`として
`accepted`とする。validだが一つでも落ちれば
`the forced quadratic external homological family fails prequalification`として`rejected`とする。

acceptedでもこれはbinary64 canonical endpointのlinear／quadratic-input operator
prequalificationである。実際のHessian、forcing support、\(W_2\)、\(R_2\)、homological residual、
independent derivative、invariance residual order、forced SSM existence／uniqueness、normal attractionは
未認証である。acceptedの場合だけQ011e dense forced quadratic chartを事前登録する。

### Q011d 最終結果

validity `7 / 7`、hypothesis `5 / 5`を通過し、
`the forced quadratic external homological family is numerically nonresonant and solvable`
として`accepted`とした。

- selected／external／full fixed-leaf eigenvalue count:
  `24 / 2574 / 2598`
- maximum structural／conjugate-spectrum residual:
  `7.35746952368904e-14 / 1.3286214932264194e-14`
- global normal gap／full fixed-leaf radius／spectral quotient:
  `0.0020611211549740327 / 0.9920954673551019 / 1.128181043680419`
- 300 pairのsector count \(k_x=0,1,16,2,15\):
  `102 / 54 / 54 / 45 / 45`
- sector leakage／maximum action error／product-spectrum error:
  `0.0 / 2.4215004011706513e-16 / 0.0`
- numerical singular block count:
  `0`
- minimum operator singular value／spectral distance:
  `0.0001550243474275936 / 0.00019318395013023792`
- maximum condition／direct-solve residual:
  `15018.139810898925 / 3.0754729793416724e-15`
- maximum conjugate-sector scalar discrepancy:
  `2.0227681201111162e-11`
- 20 sector-wide probe maximum residual／response amplification:
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

全300 blockのfull singular spectrum、rank、spectral distance、condition、direct solveと、
5 sector × 4 RHSのfull nonnormal Sylvester probeを完全列挙した。従ってcanonical forced
endpointのquadratic external operator familyは有限binary64範囲でprequalifiedである。

これはforced quadratic chartの構築ではない。実Hessian、quadratic forcing support、\(W_2\)、
\(R_2\)、homological residual、独立微分、invariance residual orderはまだ観測していない。
20 probeもrigorous inverse norm boundではなく、spectral quotientをsmoothness／uniqueness定理には
読み替えない。次はQ011e dense forced quadratic chartを観測前に事前登録する。

## Q011e: dense forced quadratic fixed-leaf chart — 事前登録

### 問いと数学的範囲

Q011b stored forced fixed pointとQ011dの24-dimensional selected clusterに対し、forced mapの
解析的二階微分から、固定保存量葉上のdense quadratic parameterization

\[
W(a)=x_*+W_1a+\frac12W_2[a,a],\qquad
R(a)=R_1a+\frac12R_2[a,a]
\]

を構築すると、一段不変性欠陥はlinear chartの二次からquadratic chartの三次へ改善するか。

本gateは保存量の扱いとして案Aを採用し、

\[
\delta M=\delta P_x=\delta P_y=0
\]

の不変葉に制限する。\(k_x=0\)のquadratic mean correctionは許すが、そのglobal conserved
momentはbinary64 tolerance内でゼロでなければならない。\(k=0\)の3 center coordinateは
reduced coordinateへ含めず、center-slow構成と混ぜない。

### 封印入力

- Q011d artifact／runner newline-normalized SHA-256:
  `c3acb9b7acc6e3121cb6e48a04bb060b5c95d7b128fe15fb11b67ee456337fd0` /
  `815fe7e0101cc05cc44fcb224534762f0ef7625f8c9604ff0a822c13171a617d`
- Q011d input／linear-split／pair-family／sector-probe／result digest:
  `ee2713e8169ea0f475ddee1b1233964ba40739d2276b78db3fff5410158dd2f8` /
  `7208875ff95f3a768e4b822cf9be854228d6664800dfc69218c0e6a030a0c63e` /
  `f9caee5b591e74b40b497ca7eb8244f1bbaeba71d239684c47d8215c46c2fb0b` /
  `feb864e2725e0cf726b43c443bb48b53f34ba0ac54693bb97a2b986f598a1414` /
  `a6941371e54a5e4d4abbea2f835196ddd7cce35c7c266ce399020764ed5b9dd7`
- Q011b stored endpoint state SHA-256:
  `612ef4aca91a5c0100286988e0e7979342a9046c3c78fe60ee59ca4e232a7613`
- sealed package-source SHA-256:
  `114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2`

Q011dをfresh replayし、validity `7 / 7`、hypothesis `5 / 5`、accepted classification、
5 digest、artifact cycleをexactに再現する。Q011c originalの`inconclusive`、Q011c1／Q011c2の
accepted outcomeも変更しない。

### invariant Schur complementとgraph gauge

\(k_x=0,1,16\)のordered Schur formを

\[
U^*A_kU=
\begin{bmatrix}
T_{s,k}&C_k\\0&T_{e,k}
\end{bmatrix}
\]

とし、

\[
T_{s,k}Y_k-Y_kT_{e,k}=C_k
\]

を解く。selected basis、invariant external basis、selected／external left coordinateを

\[
W_{s,k}=U_{s,k},\quad
V_{e,k}=U_{e,k}-U_{s,k}Y_k,\quad
L_{s,k}=U_{s,k}^*+Y_kU_{e,k}^*,\quad
L_{e,k}=U_{e,k}^*
\]

とする。これにより

\[
L_sW_s=I,\quad L_sV_e=0,\quad L_eV_e=I,\quad
A_kV_e=V_eT_e
\]

を要求する。単なるSchur orthogonal complementをgraph gaugeには使わない。
\(k_x=0\)ではQ011b fixed-leaf basisの150 coordinate内でこの構成を行い、物理153 stripe
coordinateへ戻す。\(k_x=2,15\)はfull Schur basisをexternal basisとする。

full-grid Fourier embeddingはunitary convention

\[
(E_kv)(y,x,q)=N^{-1/2}e^{2\pi ikx/N}v(y,q)
\]

を使う。complex selected tangent \(W_1\)のorthonormality、linear invariance、spectral-left
duality、conjugacy closureを各`<=1e-10`とする。Q011dのselected／external dynamics、
projector、pair enumeration、\(K_k\) hashをexactに再現する。

### forced-map解析Hessianと独立微分

local equilibriumを保存moment \(m=(\rho,j_x,j_y)\)で

\[
f_q^{eq}=w_q\left[
\rho+3c_q\cdot j+
\frac{\frac92(c_q\cdot j)^2-\frac32j\cdot j}{\rho}
\right]
\]

と書き、Q011b forced endpointの各siteで解析Hessianを構成する。BGK係数、streaming、
conservative filterを順に作用させる。additive force sourceの二階微分はゼロとする。

解析Hessianを用いた\(B(W_1u,W_1v)\)とは別に、seed `20260823`の16 normalized real
direction pairについてforced mapそのもののcentered mixed differenceをstep
`0.004 / 0.002`で計算し、Richardson extrapolationする。

- maximum analytic relative discrepancy: `<=1e-6`
- maximum coarse-to-fine relative change: `<=1e-4`
- minimum analytic directional Hessian norm: `>=1e-8`
- perturbed state／mapped stateは全てstrict positive

とする。homological equationを解けたことだけでHessianを正しいとは判定しない。

### sector-wide quadratic solve

unordered pair \((i,j)\)のpolynomial coefficientは、off-diagonalでHessian係数そのもの、
diagonalでHessian係数の`1/2`とする。これを\(C_2\)、解析forcingを\(B_2\)、
reduced coefficientを\(G_2\)と書けば、

\[
JC_2+B_2-W_1G_2-C_2K=0
\]

である。output sectorごとに

\[
T_{e,k}X_k-X_kK_k=-L_{e,k}B_{2,k},\qquad
G_{2,k}=L_{s,k}B_{2,k}
\]

を解き、\(C_{2,k}=V_{e,k}X_k\)とする。Q011dと同じ
sector pair count `102 / 54 / 54 / 45 / 45`、合計300を使う。

登録thresholdは次のとおり。

- maximum sector Sylvester solve relative residual: `<=1e-10`
- full homological relative residual: `<=1e-10`
- maximum pairwise homological relative residual: `<=1e-9`
- graph-gauge relative residual \(L_sC_2\): `<=1e-10`
- tangent／Hessian global conservation relative residual: `<=1e-10`
- zero-\(k_x\) quadratic correction global conserved-moment relative residual: `<=1e-10`
- Hessian／reduced-Hessian symmetry relative residual: `<=1e-12`
- \(k_x\)-selection leakage outside `0 / 1 / 16 / 2 / 15`: `<=1e-12`
- analytic forcing、\(W_2\)、\(R_2\) Frobenius norm: each `>=1e-12`

### real fixed-leaf chart

complex \(W_1\)のreal／imaginary columnsを並べ、column-pivoted QRの先頭24列からdeterministicな
real orthonormal tangent \(V\)を作る。\(C=W_1^*V\)でcomplex Schur coordinateとreal coordinateを
結び、

\[
A_r=C^*R_1C,\quad
H_r=W_2[C\,\cdot,C\,\cdot],\quad
G_r=C^*R_2[C\,\cdot,C\,\cdot]
\]

とする。real tangent／linear／Hessian／reduced-Hessianのimaginary leakage、range residual、
\(C^*C-I\)、real extractor dualityを各`<=1e-10`とする。

### 一段不変性残差次数

seed `20260824`の32 normalized real directionとamplitude

\[
(10^{-5},2\times10^{-5},4\times10^{-5},8\times10^{-5},1.6\times10^{-4})
\]

を観測する。residual `>=1e-13`の点だけをlog-log fitに使い、4点未満の方向はdegenerateとして
slope判定から除外する。degenerate方向の小残差を成功に数えない。

- slope-eligible direction count: `>=28 / 32`
- eligible linear slope: `1.85 <= slope <= 2.15`
- eligible quadratic slope: `2.70 <= slope <= 3.30`
- largest-amplitude quadratic／linear residual ratio: `<=0.25`
- chart state／mapped state minimum population: `>0`
- maximum global conservation drift: `<=1e-10`

とする。これは有限方向・有限振幅の次数監査であり、一様Taylor remainder boundではない。

### validity gate

1. Q011d／Q011c2／Q011c1／Q011c／Q011bとpackage sourceを封印どおり再現する。
2. invariant Schur complement、unitary Fourier embedding、complex／real tangentをstructurally再現する。
3. analytic forced Hessianと16-pair independent finite differenceを完全列挙する。
4. 全300 pair forcing、5 sector Sylvester solve、\(W_2/R_2\)を完全列挙する。
5. homological、graph-gauge、conservation、symmetry、Fourier-support診断を完全列挙する。
6. 32方向×5 amplitudeのlinear／quadratic residualとpositivityを完全列挙する。
7. 全値finiteなstrict JSON、input／derivative／chart／residual／result digest、runner provenanceを
   再現する。

一つでも落ちれば`inconclusive`とし、quadratic chart hypothesisを解釈しない。

### hypothesis gateと判定

validity通過時だけ次を全て要求する。

1. independent Hessian discrepancy／step-dependence／positivity gateを通る。
2. 全sector solveとfull／pairwise homological residual gateを通る。
3. graph gauge、固定葉保存、zero-\(k_x\) conserved-moment、symmetry、Fourier supportを通る。
4. complex-to-real chartとlinear invariance／dualityを通る。
5. linear chartの二次、quadratic chartの三次residual slope gateを通る。
6. largest amplitudeでquadratic residualがlinear residualの`0.25`以下となり、全stateがpositiveで
   conservation driftが登録上限内である。

全て通れば
`the forced fixed-leaf quadratic chart satisfies the registered homological and residual-order tests`
として`accepted`とする。validだが一つでも落ちれば
`the forced fixed-leaf quadratic chart fails the registered construction tests`として`rejected`とする。

acceptedでもこれは単一17² grid、登録forced endpoint、有限方向／振幅のbinary64 dense chartである。
continuous-amplitude family、rigorous derivative／inverse enclosure、SSM existence／uniqueness、
uniform Taylor remainder、nonlinear normal attraction、basin、他grid／force／wall boundaryは主張しない。
acceptedの場合だけ、Q011fでforced chartのamplitude／multi-step holdoutまたはTT／sparse費用評価の
どちらを先に行うかを、Q011eの観測結果から事前登録する。

### Q011e 最終結果

validityは`7 / 7`を通過した。independent Hessian、全300 pairの5 sector solve、full／pairwise
homological equation、graph gauge、固定葉保存、Fourier support、complex-to-real変換も全て登録閾値を
通過した。従って有限binary64 dense quadratic chart自体は構築できた。

一方、seed `20260824`の32方向ではlinear residualは各5 amplitude全てがnoise floor以上だったが、
quadratic residualは各方向1点だけが`1e-13`以上だった。全32方向が4点未満のdegenerate方向となり、
slope-eligible countは登録下限`28 / 32`に対して`0 / 32`だった。従ってhypothesisは`5 / 6`で、
Q011eを`rejected`とした。

- classification:
  `the forced fixed-leaf quadratic chart is constructed, but the registered residual-order window is underresolved`
- maximum complex structural／real linear invariance residual:
  `7.35746952368904e-14 / 8.341890217669523e-15`
- analytic forcing／\(W_2\)／\(R_2\) norm:
  `6.834040875959414 / 14.084081139824606 / 0.5789086833342865`
- maximum sector solve／full／pairwise homological residual:
  `8.463492700134046e-16 / 1.2377387705494087e-14 / 1.3875757356771478e-14`
- graph-gauge／zero-\(k_x\) conservation residual:
  `2.028243962507091e-15 / 8.28412455635593e-15`
- maximum independent-Hessian discrepancy／step change:
  `1.2602687807695985e-9 / 3.254644954471969e-7`
- slope-eligible／degenerate directions: `0 / 32`、`32 / 32`
- linear／quadratic fit points per direction: `5 / 1`
- maximum largest-amplitude quadratic／linear residual ratio:
  `8.954201113852774e-5`
- minimum population／maximum conservation drift:
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

事前登録したbinary ruleは変更せず、Q011eを合格へ読み替えない。観測後に、唯一の失敗が
constructionではなく残差窓の未解像だったことを正確に表すため、genericなreject reporting stringだけを
上記classificationへ精密化した。threshold、seed、amplitude、noise floor、gate count、outcomeは変更していない。

次はQ011e1を別gateとして観測前に事前登録する。同じQ011e chart、noise floor `1e-13`、linear／quadratic
slope区間、最低eligible方向数を固定し、別seedと拡大振幅窓で三次残差を再測定する。Q011e artifactは
再採点せず、Q011e1が通るまでforced quadratic residual orderを確認済みとは扱わない。

## Q011e1: independent enlarged residual-window reissue — 事前登録

### 問いと修復範囲

Q011eで構築・封印した同一のforced fixed-leaf quadratic chartを変更せず、独立方向と拡大振幅窓で
一段不変性残差を再測定すると、linear chartの二次とquadratic chartの三次を登録noise floor上で
判定できるか。

これはQ011eの再採点ではない。Q011eの`rejected`、元seed `20260824`、元振幅、noise floor、slope
interval、最低eligible方向数を変更しない。Q011e1はmeasurement-window underresolutionだけを扱う
独立再発行gateであり、Hessianやhomological coefficientを再fitしない。

### 封印入力とchart再構築

- Q011e artifact／runner newline-normalized SHA-256:
  `45d563103678d790aa3df4db692bbe781c9c86ed550c7499c61b397688666fca` /
  `3aa608852be7a1df7dbe37b4d3c7e1bb3fbf125eae115260fc45a223e0757955`
- Q011e input／derivative／chart／residual／result digest:
  `f0bd65361d0cdc39e6499b8b0065ce6d7705945927ed77af5d2b231d0572bc9c` /
  `d017d3ea204ad337f538b6f1819e215b6ab8a69f89090cc51ca9eb4885b75fce` /
  `6d4ee0102a6df052fac857890468ed911cff994e07c573dde837eb54a4a22e05` /
  `5570cb7acfc465f57850f960c6c9d68770182856b6a9aba62e81256c77e84948` /
  `89b39a6a6a80452142a2c9288780a08c1b24b49614080b5412fff82171a8188e`
- real tangent／extractor／linear dynamics SHA-256:
  `e0b6fb929d49a1371d1eebf836308a795a7f0e9dbad44f55b2386add9f3d0628` /
  `e77d149787d187ca756a23efcf6b833cfd6ab15b5fd617b5d3ae3ba5c0859f6f` /
  `b6521e3090b61c72d0689b765e1fad0a0318029a0ab5767bd3c7679d4ce2c525`
- analytic second derivative／real \(W_2\)／real \(R_2\) SHA-256:
  `6bfea17a7bbfa1dcdded5dadec15296ec2f478aefe7984dd1e4885498a186221` /
  `ab55a8b50f2565be494fcf3d5f140f93fc0112484da56e1333ce58dfd220a6c2` /
  `7ae45cbabda8da17ec73d6779761077a67e19fae4dc53ca11fe98b78bcf074e2`
- sealed package-source SHA-256:
  `114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2`

Q011e artifactのvalidity `7 / 7`、hypothesis `5 / 6`、`rejected` outcome、唯一の失敗gate、
全5 digestをexactに照合する。次にQ011eと同じ解析手順を一度だけfresh実行してreal tangent、extractor、
linear dynamics、analytic second derivative、\(W_2\)、\(R_2\)を再構築し、上記array hashとQ011eの
全construction thresholdを再現する。Q011eの元residual campaignはartifactから封印し、再採点しない。

### 独立方向と拡大振幅窓

未使用seed `20260825`から32本の標準正規real coordinate vectorを生成し、それぞれEuclidean norm 1へ
正規化する。Q011e1の振幅は観測前に

\[
(1.6\times10^{-4},\ 3.2\times10^{-4},\ 6.4\times10^{-4},\
1.28\times10^{-3},\ 2.56\times10^{-3})
\]

と固定する。最小振幅`1.6e-4`はQ011e窓とのbridgeで、残る4点は未観測の拡大窓である。方向seedは
全て未使用なので、bridge amplitudeもQ011eとは独立方向上のholdoutである。

linear／quadratic chartの一段不変性残差を同じfull forced mapで測定する。各chart state、reduced image、
mapped state、global mass／momentum drift、minimum populationを全160 sampleで保存する。fitにはQ011eと
同じくresidual `>=1e-13`の点だけを使い、4点未満の方向はdegenerateとしてslope判定から除く。

主fitに加え、5点全てがeligibleな方向では最小bridge点を除いた上位4点のsecondary slopeも保存する。
primary slopeとの絶対差をlinear／quadraticとも`<=0.15`とし、単一の低振幅点だけに依存した次数判定を
避ける。4点だけeligibleな方向ではprimary fit自体が上位4点なので差を0とする。

### validity gate

1. Q011e artifact／runner／package source、5 digest、validity／outcome／唯一の失敗gateを封印どおり再現する。
2. Q011e constructionを一度だけfresh再構築し、6 array hashと全construction thresholdを再現する。
3. seed `20260825`、32 unit direction、登録5 amplitude、合計160 sampleを完全列挙する。
4. linear／quadratic residual、eligible mask、primary／secondary fit、positivity／conservationを全方向で保存する。
5. 全値finiteなstrict JSON、input／chart／residual／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、残差次数を解釈しない。

### hypothesis gateと判定

validity通過時だけ次を全て要求する。

1. slope-eligible direction count: `>=28 / 32`。
2. eligible linear primary／secondary slope: each `1.85 <= slope <= 2.15`。
3. eligible quadratic primary／secondary slope: each `2.70 <= slope <= 3.30`。
4. eligible方向のprimary／secondary slope差: linear／quadratic each `<=0.15`。
5. largest-amplitude quadratic／linear residual ratio: every direction `<=0.25`。
6. chart／mapped state minimum population: `>0`、maximum global conservation drift: `<=1e-10`。

全て通れば
`the independent enlarged window resolves second- and third-order forced chart residuals`
として`accepted`とする。validだが一つでも落ちれば
`the enlarged residual window does not confirm the registered forced chart orders`
として`rejected`とする。

acceptedでも、これは単一17² grid、単一forced endpoint、32方向、登録5振幅のbinary64 holdoutである。
uniform Taylor remainder、continuous-amplitude family、forced SSM existence／uniqueness、nonlinear normal
attraction、basin、他grid／force／wall boundaryを主張しない。acceptedの場合だけ次のQ011fで
multi-step shadowing windowを事前登録し、その後にnatural Fourier-sparse baselineを保った
TT／sparse費用評価へ進む。

### Q011e1 最終結果

Q011e artifact、runner、package source、5 digest、`passed / rejected` outcome、唯一の失敗gateを
exactに再現した。同じ解析手順でQ011e chartを一度だけfresh再構築し、real tangent／extractor／linear
dynamics／analytic second derivative／\(W_2\)／\(R_2\)の6 array hashと全construction gateも再現した。

未使用seed `20260825`の32方向、登録5振幅、160 sampleは全てfiniteかつpositiveで、全方向が
slope-eligibleとなった。primary fitと上位4点secondary fitの双方がlinear二次／quadratic三次の
登録区間を通り、window差も登録上限を通過した。validity `5 / 5`、hypothesis `6 / 6`として
Q011e1を`accepted`とする。

- classification:
  `the independent enlarged window resolves second- and third-order forced chart residuals`
- slope-eligible／degenerate directions: `32 / 32`、`0 / 32`
- linear primary／secondary slope range:
  `1.9999592141961493 -- 2.0000652994279995` /
  `1.9999478838445748 -- 2.000083440834926`
- quadratic primary／secondary slope range:
  `2.9998586349153378 -- 3.000154889315294` /
  `2.999908289307265 -- 3.000145181102861`
- maximum linear／quadratic primary-secondary difference:
  `1.8141406926464043e-5 / 1.7126610593187763e-4`
- maximum largest-amplitude quadratic／linear residual ratio:
  `0.0013091448869808333`
- minimum population／maximum conservation drift:
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

これはQ011eの再採点ではない。Q011eは元の小振幅measurement windowに対して`rejected`のままであり、
Q011e1だけが独立拡大窓の有限holdoutとしてacceptedである。従ってforced quadratic chartの一段残差次数は
登録有限範囲で確認したが、uniform Taylor remainder、continuous-amplitude family、forced SSM
existence／uniqueness、nonlinear normal attraction、basinは主張しない。次はQ011f multi-step
shadowing windowを観測前に事前登録する。

## Q011f: independent multi-step forced-chart shadowing window — 事前登録

### 問いと範囲

Q011e1で一段残差次数を確認した同じforced fixed-leaf quadratic chartについて、別seedの初期座標から
full forced mapとquadratic reduced mapを64 step追跡すると、有限horizonのlifted reduced orbitは
linear chartより小さいshadowing errorを保ち、振幅に対する三次次数を維持するか。

本gateは有限binary64 trajectory campaignであり、shadowing lemma、uniform-in-time bound、basin、
normal attractionの証明ではない。linear baselineとquadratic chartは同じ初期reduced coordinate
\(a_0\)を使うが、full初期状態はそれぞれ\(W_{\rm lin}(a_0)\)、\(W_2(a_0)\)とする。従って両者は
各chart自身のsame-chart initial stateから始まる比較であり、二つのfull orbitが同一初期physical stateを
共有するとは主張しない。

### 封印入力

- Q011e1 artifact／runner newline-normalized SHA-256:
  `989801d1e4e1396ebba279e11c396f7f6d4e9616d2aa170f5687f9ba08a95840` /
  `bb8a052f387d2748fee823af10f2ab4ea4a9a08ebe62e8b4ff87d68d55c2929f`
- Q011e1 input／chart-reconstruction／residual-window／result digest:
  `8e979deeed0e5f4151addb5f3b06c1a9815a28f4e0c5762726d7c29a03d035c0` /
  `2e739657032352d7d0496568a216b761000a68beb6d00749e1e427e6447598fb` /
  `20267150710538f797f21cc2846ee6be14060ad9ea6bef98ef29e4731121410b` /
  `0370a24ce7a74da71ee978b3892ea23412c3d18adb110e2b2b53aaf02ccdf039`
- Q011e1 direction SHA-256:
  `64b017fb5a3c55378ccee4d457b4d2a8c75a92cd5b421897f9b7de1ad6a77b1d`
- Q011e real tangent／extractor／linear／second derivative／\(W_2\)／\(R_2\) hashは
  Q011e1事前登録の6値をそのまま固定する。
- sealed package-source SHA-256:
  `114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2`

Q011e1 artifactのvalidity `5 / 5`、hypothesis `6 / 6`、accepted classification、4 digest、
direction hashをexactに照合する。Q011eの元`rejected` outcomeも変更しない。Q011e1と同じhelperで
Q011e chartを一度だけfresh再構築し、6 array hashとconstruction auditを再現する。

### 独立trajectory campaign

未使用seed `20260826`から32 unit directionを生成する。初期振幅はQ011e1と同じ

\[
(1.6\times10^{-4},\ 3.2\times10^{-4},\ 6.4\times10^{-4},\
1.28\times10^{-3},\ 2.56\times10^{-3})
\]

とし、合計160 initial coordinateを使う。各初期値についてlinear／quadraticのfull orbitとreduced orbitを
64 step進め、各stepで

\[
e_n^{\rm lin}=\|\Phi^n(W_{\rm lin}(a_0))-W_{\rm lin}(R_{\rm lin}^n(a_0))\|_2,
\]

\[
e_n^{\rm quad}=\|\Phi^n(W_2(a_0))-W_2(R_2^n(a_0))\|_2
\]

を保存する。全stepでfull／lifted stateのminimum population、global mass／momentum drift、reduced
coordinate normも保存し、horizon

\[
n\in\{1,2,4,8,16,32,64\}
\]

ではfull／lifted state hashを追加で保存する。

各direction・horizonについて5 amplitudeに対するlog-log slopeを求める。error `>=1e-12`の点だけを
fitに使い、linear／quadraticとも4点以上ある場合だけslope-eligibleとする。これはQ011e1の一段
noise floorより10倍大きくし、64-step roundoff accumulationをslopeへ数えないための事前固定値である。

### validity gate

1. Q011e1 artifact／runner／package source、4 digest、accepted outcome、direction hashを封印どおり再現する。
2. Q011e chartを一度だけfresh再構築し、6 array hashとconstruction auditを再現する。
3. seed `20260826`、32 unit direction、5 amplitude、linear／quadratic各160 trajectoryを完全列挙する。
4. 全trajectoryの64 step error／positivity／conservation／coordinate normと7 checkpoint hashを保存する。
5. 全224 direction-horizon fitのmask／slope／ratioを完全列挙する。
6. 全値finiteなstrict JSON、input／chart／trajectory／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、multi-step shadowing hypothesisを解釈しない。

### hypothesis gateと判定

validity通過時だけ次を全て要求する。

1. slope-eligible direction-horizon count: `224 / 224`。
2. eligible linear shadow-error slope: each `1.75 <= slope <= 2.25`。
3. eligible quadratic shadow-error slope: each `2.50 <= slope <= 3.50`。
4. every registered direction／amplitude／horizonで
   \(e_n^{\rm quad}/e_n^{\rm lin}\le0.05\)。
5. horizon 64でevery trajectoryの\(e_{64}^{\rm quad}/\|a_0\|_2\le10^{-3}\)。
6. full／lifted state minimum population: `>0`、maximum global conservation drift: `<=1e-10`。

全て通れば
`the sealed forced quadratic chart passes the registered 64-step shadowing window`
として`accepted`とする。validだが一つでも落ちれば
`the forced quadratic chart fails the registered finite shadowing window`
として`rejected`とする。

acceptedでもこれは160 initial condition、64 step、7 horizonのfinite binary64 evidenceである。
all-time shadowing、uniform remainder、basin、normal attraction、forced SSM existence／uniqueness、他grid／
force／wall boundaryを主張しない。acceptedの場合だけQ011gでこのforced quadratic coefficient tensorの
natural Fourier-sparse storageを確定し、TT-SVDを同じ残差・action・実メモリ基準で比較する。

### Q011f 最終結果

validity `6 / 6`を通過した。Q011e1 accepted artifactとQ011e rejected artifact、全digest、chartの6 array
hashを再現し、linear／quadratic各160 trajectory、全10,240 step、1,120 checkpoint、224 fitを完全に
保存した。

hypothesisはeligible fitのlinear／quadratic slope、全checkpointのquadratic改善、64-step相対誤差、
positivity／conservationの5 gateを通った。一方、全224 fit eligibleという登録gateだけが`222 / 224`で
落ちたため、Q011fを`rejected`とした。

- classification:
  `the forced quadratic chart fails the registered finite shadowing window`
- degenerate direction-horizon:
  `(direction 4, horizon 1)`、`(direction 4, horizon 2)`
- 両witnessのlinear／quadratic fit-point count: `5 / 3`
- quadratic fit mask: `[false, false, true, true, true]`
- horizon 1 quadratic errors at first two amplitudes:
  `1.1752258806252989e-13 / 9.402263023336189e-13`
- horizon 2 quadratic errors at first two amplitudes:
  `1.1463003790416861e-13 / 9.171105405464717e-13`
- eligible linear／quadratic slope range:
  `1.9999216343019504 -- 2.000128344576816` /
  `2.999096737571295 -- 3.000265091846932`
- maximum checkpoint quadratic／linear error ratio:
  `0.002547526388856511`
- maximum horizon-64 quadratic error／initial amplitude:
  `1.1019505895816554e-6`
- minimum population／maximum conservation drift:
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

失敗は二つのearly-horizon fitのmeasurement-floor underresolutionへ局在化した。第2振幅のerrorは
`1e-12`を約6--8%下回り、高振幅側3点だけが残った。他の222 fitと全長時間性能gateが通っても、登録した
`224 / 224`を緩めずQ011fは再採点しない。次はQ011f1を別gateとして、同じdirection set・floor・horizon・
slope／performance thresholdを固定し、未使用midpoint amplitude `4.8e-4`の32 trajectoryだけを追加する。
Q011f1が通るまでfinite multi-step shadowing windowを確認済みとは扱わず、Q011gへ進まない。

## Q011f1: held-out amplitude multi-step reissue — 事前登録

### 問いと修復範囲

Q011fの同じ32 direction・64 step・7 horizonに、未使用amplitude `4.8e-4`のtrajectoryを1本ずつ追加し、
元5点と合わせた6点fitを行うと、登録floor `1e-12`を変えずに全224 direction-horizon fitを解像できるか。

これはQ011fの再採点ではない。Q011fの`rejected`、seed、元5 amplitude、horizon、noise floor、slope、
quadratic／linear ratio、64-step relative-error、positivity／conservation thresholdを変更しない。
Q011f1は2つのearly-horizon measurement-floor failureだけを、未使用amplitudeで修復する独立再発行gateである。

### 封印入力

- Q011f artifact／runner newline-normalized SHA-256:
  `9c091dbafd60617850cd3168f3ad9235a353b0990cbd003df9be0b487ead1591` /
  `e9c0a8e38b94dbe693855dc836f8cf02393675b417ff3f43fc43059ab361a741`
- Q011f input／chart-reconstruction／trajectory／result digest:
  `e9b29c95d41af0062259d3aab19ab2c58175cd98582ed82f3af36863f023bc53` /
  `aa1da452db8ff6b84e88a32f7a7119c63816b12e283147daaa303e9e09c3ae42` /
  `aa62fc11a36bef881bbcdb05919818f6db167f3f95eee396fcdaf79fead5e182` /
  `629a5a7a3d3bfed12a590646c375d4977db1726ddc521ddb86394786b1005f22`
- Q011f direction SHA-256:
  `4d0bef57236d4f70a8a8f422b1bdfa39cd5737c88401c2441decdd98d886d2f9`
- Q011e1 artifact／runner／4 digest、Q011e chartの6 array hash、package-source hashはQ011fが封印した値を
  そのまま再現する。

Q011f artifactのvalidity `6 / 6`、hypothesis `5 / 6`、`rejected` outcome、唯一の失敗gate、
degenerate witness `(direction 4, horizon 1 / 2)`とraw error／maskをexactに照合する。Q011e1 accepted、
Q011e rejected outcomeも変更しない。Q011f helperでchartを一度だけfresh再構築する。

### held-out amplitude campaign

Q011fと同じseed `20260826`から同じ32 unit directionを再現し、direction hashを照合する。新しい振幅は

\[
a_{\rm hold}=4.8\times10^{-4}
\]

に固定する。これは元の`3.2e-4`と`6.4e-4`の間にある未使用点で、Q011f artifact生成前には観測して
いない。各directionについてlinear／quadratic full orbitとreduced-lift orbitを64 step進め、Q011fと同じ
全step診断と7 checkpoint hashを保存する。合計32 trajectory per chart、2,048 step、224 checkpointである。

元Q011f artifactの5 amplitude errorとheld-out errorを振幅順

\[
(1.6\times10^{-4},\ 3.2\times10^{-4},\ 4.8\times10^{-4},\
6.4\times10^{-4},\ 1.28\times10^{-3},\ 2.56\times10^{-3})
\]

にmergeし、floor `1e-12`以上の点だけで224 fitを再計算する。元artifactのstateやerrorは再計算値で
置き換えない。特に2つの元degenerate witnessでは、held-out quadratic errorがfloor以上でfitへ入り、
combined quadratic fit-point countが4以上になることを明示的に要求する。

### validity gate

1. Q011f artifact／runner／package source、4 digest、direction hash、valid/rejected outcome、2 witnessを再現する。
2. Q011e1／Q011e outcomeを保持し、Q011e chartを一度だけfresh再構築して6 array hashを再現する。
3. 同じ32 directionとheld-out amplitude `4.8e-4`の32 trajectoryを64 step完全列挙する。
4. held-out全2,048 step診断、224 checkpoint hash、positivity／conservationを保存する。
5. 元5点とheld-out点を正しい振幅順へmergeし、全224 mask／slope／ratioを完全列挙する。
6. 全値finiteなstrict JSON、input／chart／heldout／merged-fit／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、再発行shadowing hypothesisを解釈しない。

### hypothesis gateと判定

validity通過時だけ次を全て要求する。

1. 2 repaired witnessでheld-out quadratic pointがfloor以上かつcombined fit-point count `>=4`。
2. slope-eligible direction-horizon count: `224 / 224`。
3. eligible linear slope: each `1.75 <= slope <= 2.25`。
4. eligible quadratic slope: each `2.50 <= slope <= 3.50`。
5. merged 6 amplitudeのevery checkpointでquadratic／linear error ratio `<=0.05`、every trajectoryの
   horizon-64 quadratic error／initial amplitude `<=1e-3`。
6. held-out full／lifted state minimum population `>0`、maximum global conservation drift `<=1e-10`。

全て通れば
`the forced quadratic chart passes a held-out-amplitude 64-step shadowing reissue`
として`accepted`とする。validだが一つでも落ちれば
`the held-out amplitude does not repair the registered finite shadowing window`
として`rejected`とする。

acceptedでも、Q011f自体は`rejected`のままである。Q011f1は元5点を含む6 amplitude、32 direction、64 step、
7 horizonのfinite binary64 reissueに限る。all-time shadowing、uniform remainder、basin、normal attraction、
forced SSM existence／uniqueness、他grid／force／wall boundaryを主張しない。acceptedの場合だけQ011gの
natural Fourier-sparse／TT-SVD比較を事前登録する。

### Q011f1 実行結果

validity `6 / 6`、hypothesis `6 / 6`を通過し、
`the forced quadratic chart passes a held-out-amplitude 64-step shadowing reissue`
として`accepted`とした。Q011f artifactの`rejected` outcomeと二つの元witnessはexactに再現され、
Q011e chartの6 array hashも一致した。

- merged slope-eligible／degenerate fit: `224 / 224`、`0 / 224`
- merged linear slope range:
  `1.9999204011998797 -- 2.000130424734462`
- merged quadratic slope range:
  `2.9992217798368643 -- 3.00027147080911`
- direction `4`、horizon `1 / 2`のheld-out quadratic error:
  `3.1730810288365184e-12 / 3.0952409781368448e-12`
- 同witnessのcombined quadratic fit-point count／slope:
  `4 / 4`、`3.000037106494855 / 3.0000355600774475`
- maximum merged checkpoint quadratic／linear ratio:
  `0.002547526388856511`
- maximum merged horizon-64 quadratic error／initial amplitude:
  `1.1019505895816554e-6`
- minimum merged population／maximum conservation drift:
  `0.027704572566416702 / 1.8214860035899544e-12`
- input／chart／heldout／merged-fit／result digest:
  `101adcdc6fc2d40dc984e6ba900d234b913f7c78aa34381a08d0a77aa9e23000` /
  `ba50ee295551dae970d33e1bba735ac0502987aef0f4a82987f2998ae884f732` /
  `243c41522a9eb7d7b78b2031bdbe8f55eb23b447e8d84162b1aae2f53b651829` /
  `2e3fcee7bebec5c82f2fbd2b78ddac8c44401fd0681ad5d9feb60c7257a8326e` /
  `484580786b6c535856f0693b14c58815462e1de979759057dc3b402d475bcbc7`
- runner／artifact newline-normalized SHA-256:
  `eab2d63a075f2c43b4c6adfaa7941e9c23bf85a351427057130f68945346ce62` /
  `79ddb64e0965b5b87b7ad68c6dc8698efdd2281540c798ed27f355747d265bc1`

この結果は事前登録した有限再発行範囲だけを受理する。Q011fを再採点せず、all-time shadowingや
normal attractionを追加認証しない。従って次の課題はQ011gであり、forced dense quadratic coefficientを
Fourier selection ruleで表したnatural sparse baselineとTT-SVDを、格納量だけでなく実メモリ、評価時間、
rounding時間、実効自由度、不変性残差で比較する。Q011gは実装・観測前に別途事前登録する。

## Q011g: forced quadratic Fourier-sparse／TT-SVD representation audit — 事前登録

### 問いと判定対象

Q011f1で有限multi-step shadowing windowを通過したforced quadratic chartの二次係数
\(W_2,R_2\)について、Fourier selection ruleをそのまま使うnatural sparse-fiber表現より、登録した
TT-SVD tensorizationの少なくとも一つが忠実度、格納量、現在環境でのjoint action時間を同時に改善するか。

これはTT採用を前提にしたgateではない。natural Fourier-sparseを必須baselineとし、TTがこれをstrictに
上回らなければ、固定17² forced quadratic coefficientに対して
`registered TT-SVD bundles do not beat the natural Fourier-sparse forced-quadratic baseline`
としてTT優位性仮説を`rejected`とする。TT-crossはこのgateの対象外で、TT-SVD winnerが出た場合だけ
別gateとして検討する。

### 封印入力

- Q011f1 artifact／runner newline-normalized SHA-256:
  `79ddb64e0965b5b87b7ad68c6dc8698efdd2281540c798ed27f355747d265bc1` /
  `eab2d63a075f2c43b4c6adfaa7941e9c23bf85a351427057130f68945346ce62`
- Q011f1 input／chart／heldout／merged-fit／result digest:
  `101adcdc6fc2d40dc984e6ba900d234b913f7c78aa34381a08d0a77aa9e23000` /
  `ba50ee295551dae970d33e1bba735ac0502987aef0f4a82987f2998ae884f732` /
  `243c41522a9eb7d7b78b2031bdbe8f55eb23b447e8d84162b1aae2f53b651829` /
  `2e3fcee7bebec5c82f2fbd2b78ddac8c44401fd0681ad5d9feb60c7257a8326e` /
  `484580786b6c535856f0693b14c58815462e1de979759057dc3b402d475bcbc7`
- package-source SHA-256:
  `114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2`
- Q011e artifact／runner newline-normalized SHA-256:
  `45d563103678d790aa3df4db692bbe781c9c86ed550c7499c61b397688666fca` /
  `3aa608852be7a1df7dbe37b4d3c7e1bb3fbf125eae115260fc45a223e0757955`
- Q011e native complex \(W_2/R_2\) SHA-256:
  `0b4c2f6967624e62b8b45a1fde67d0a092894ff367ed402a076c15c46a2206db` /
  `b450cba9d58d0853bed95acaa9b4f2a69659e5c24b943708c0700d11c8962ee9`
- complex-to-real coordinate map SHA-256:
  `ba7e73e99f82b5c14fb0d96005d7952248c4f6da9a48e1430b7c389ba42674f1`
- real \(W_2/R_2\) SHA-256:
  `ab55a8b50f2565be494fcf3d5f140f93fc0112484da56e1333ce58dfd220a6c2` /
  `7ae45cbabda8da17ec73d6779761077a67e19fae4dc53ca11fe98b78bcf074e2`

Q011f1のvalidity `6 / 6`、hypothesis `6 / 6`、`accepted` outcomeをexactに再現し、Q011fの
`rejected` outcomeを変更しない。Q011e chartは一度だけfresh再構築し、real tangent、extractor、
reduced linear map、analytic Hessianを含む既登録6 array hashを全て照合する。

### canonical Fourier coefficientとnatural sparse baseline

Q011eのnative complex coordinate順と300 unordered pair順を固定する。pair \(p=(i,j)\), \(i\le j\)の
polynomial coefficientを

\[
C^W_p=\begin{cases}\frac12W_2[:,i,i],&i=j,\\W_2[:,i,j],&i<j,\end{cases}
\qquad
C^R_p=\begin{cases}\frac12R_2[:,i,i],&i=j,\\R_2[:,i,j],&i<j\end{cases}
\]

とする。Q011dのpair-sector tableに従い、\(x\)出力へunitary FFT `fft / sqrt(17)`を適用する。
各\(C^W_p\)は登録output sector \(s_p\in\{0,1,2,15,16\}\)の17×9 fiberだけを残し、それ以外を
構造的zeroとする。\(C^R_p\)はsector `0 / 1 / 16`について対応するselected output block
`6 / 9 / 9`だけを残し、sector `2 / 15`では構造的zeroとする。元native tensorからこのprojectionで
捨てる相対normを`1e-12`以下と要求する。

natural representationは次だけを所有する。

- pair indices: `(300, 2)`、`uint8`
- output sectors: `(300,)`、`uint8`
- \(W_2\) fibers: `(300, 17, 9)`、`complex128`
- \(R_2\) active fibers: `(102, 6)`、`(54, 9)`、`(54, 9)`、`complex128`

pair indicesからdiagonal factorを決めるため、multiplicityを重複格納しない。係数payloadは
`47,484 complex = 94,968 stored real scalars`、indexを含むraw array payloadは事前計算上
`760,644 bytes`である。これらは数学的独立自由度ではなく格納量である。bitwise nonzeroだけを保存する
scalar-sparse表現も診断として併記するが、natural Fourier-fiber baselineを判定から外さない。

natural tableから構成したprojected ordered-dense oracleは

- \(W_2^F\): `(17, 17, 9, 24, 24)`、`complex128`
- \(R_2^F\): `(24, 24, 24)`、`complex128`

とする。全TTとdense controlはこの同じprojected tensorを入力とし、natural sparseだけが数値noiseを
捨てて有利になる比較にはしない。dense materialization費用は共通入力としてoffline timingから除外する。

### 登録TT-SVD bundle

relative discarded-Frobenius toleranceを`1e-13`、rank capを`None`に固定する。各candidateは\(W_2^F\)と
\(R_2^F\)の二つのTTを一つのbundleとして持つ。

1. `flat-output-first`: \(W=(2601,24,24)\)、\(R=(24,24,24)\) output-first
2. `flat-output-last`: \(W=(24,24,2601)\)、\(R=(24,24,24)\) output-last
3. `fourier-output-first`: \(W=(17,17,9,24,24)\)、\(R\) output-first
4. `fourier-output-last`: \(W=(24,24,17,17,9)\)、\(R\) output-last
5. `d1q3-output-first`: velocityをlexicographic D1Q3×D1Q3へ並べ、
   \(W=(17,17,3,3,24,24)\)、\(R\) output-first
6. `d1q3-output-last`: \(W=(24,24,17,17,3,3)\)、\(R\) output-last

全tensorization／untensorizationをbitwiseに検証する。比較する格納指標は、二TTの合計について

- core stored real scalar count
- core payloadとrank／shape metadataを含むraw array payload bytes
- `sys.getsizeof`で数えた所有array／containerのin-memory object bytes
- uncompressed NPZ serialized bytes
- core shapeとTT rank
- nominal gauge-adjusted real dimension

である。最後の値はTT gaugeを差し引く診断的parameter countで、数学的独立自由度や格納scalar数の代替には
使わない。TT-SVD construction／truncation wall timeを`rounding/preparation time`として別記し、
tensorization、SVD、serializationのsubphaseを分ける。

### independent fidelity／invariance campaign

- action seed: `20260902`
- normalized real reduced directions: `32`
- invariance seed: `20260903`
- normalized real reduced directions: `16`
- invariance amplitude: `2.56e-3`
- Q011e／Q011e1／Q011fの登録方向とのexact duplicate: `0`

real direction \(a\)をsealed coordinate mapでnative complex coordinate \(z\)へ移す。natural、dense、
各TTについて同じhomogeneous quadratic joint action

\[
\left(\frac12W_2^F[z,z],\frac12R_2^F[z,z]\right)
\]

を評価する。natural-vs-dense maximum relative action errorを`1e-12`、TT tensor reconstructionを
`2e-13`、TT joint action errorをnatural／dense双方に対して`1e-11`以下とする。complex actionを
physical real chartへ戻した結果もsealed real \(W_2/R_2\) actionと`1e-11`以下で一致させる。

invariance campaignではdense Q011e chart、natural projected chart、各TT-backed chartのone-step defectを
同じ16初期座標で計算する。natural-vs-denseおよびTT-vs-natural defect-vector relative differenceを
`1e-4`以下、全初期／写像stateのminimum populationをstrict positive、global conservation driftを
`1e-10`以下とする。これは既存residual-order slopeを再採点せず、係数表現が登録点の不変性残差を壊さない
ことだけを検査する。

### offline／online cost protocol

共通のchart再構築、native係数生成、Fourier projection、ordered-dense materializationは全methodの
timingから除外する。これはTTに有利な費用除外である。

- methods: `natural-fourier-sparse`、`ordered-dense-control`、上記6 TT bundle
- offline warmup／measured blocks: `1 / 3`
- online warmup／measured blocks: `1 / 5`
- online vectors: action seed `20260902`の32方向
- method order: blockごとのcyclic rotation
- timer: `perf_counter_ns`
- garbage collector: 各timed block内でdisableし、終了時に元の状態へ戻す
- online scope: \(W_2/R_2\) joint homogeneous quadratic actionだけ
- 各blockで両output normのchecksumを保存し、natural比`1e-11`以下とする

offlineではnaturalのfresh array copy／serialization、dense controlのfresh copy／serialization、TTの
tensorization／二TT-SVD／serializationを測る。全blockでstorage recordとserialization roundtripが一致する
ことを要求する。runtime、BLAS、CPU、thread環境をartifactへ保存し、他machineの性能へ外挿しない。

method \(m\)のoffline／online envelopeを\(B_m^-,B_m^+,t_m^-,t_m^+\)とする。TTが時間でnaturalを
robustに上回る条件を

\[
t_m^+<t_s^-
\]

とする。この場合だけ、TTに不利・sparseに有利なcost line

\[
T_m^+(N)=B_m^+ + Nt_m^+,
\qquad T_s^-(N)=B_s^-+Nt_s^-
\]

から最小整数break-evenを計算する。envelopeが重なればmedianが速くても`timing advantage not certified`
とする。ordered-dense controlとのbreak-evenは診断に留め、natural baselineを外す理由にしない。

### validity gate

1. Q011f1 artifact／runner／package source、5 digest、accepted outcome、Q011f rejected outcomeを再現する。
2. Q011e chartをfresh再構築し、native complex／real係数、coordinate map、既登録array hashを再現する。
3. 300 pair、sector `0 / 1 / 16 / 2 / 15`のcount `102 / 54 / 54 / 45 / 45`、natural storage
   shape／事前計算量、projection、serialization roundtripが一致する。
4. 全6 tensorizationがbitwise reversibleで、TT-SVD、rank、core、reconstruction、actionがfiniteかつ
   登録fidelity／realification／invariance thresholdを通る。
5. 独立方向hash、prior duplicate 0、offline／online block数、cyclic order、checksum、subphase time、
   storage／memory recordが完全である。
6. 全値finiteなstrict JSON、input／coefficient／fidelity／cost／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、TT／sparse優位性を解釈しない。

### TT優位性hypothesis gateと選択規則

validity通過後、candidateごとに次を判定する。

1. fidelity、realification、invariance-residual preservationを全て通る。
2. core stored real scalarsがnaturalの`94,968`よりstrictに小さい。
3. raw payload、in-memory object bytes、uncompressed NPZ bytesがnaturalより全てstrictに小さい。
4. \(t_m^+<t_s^-\)で、naturalに対するconservative finite break-evenが存在する。

同じcandidateが4条件を全て満たした場合だけ`joint winner`とする。winnerが複数なら

1. conservative break-evenが小さい
2. raw payloadが小さい
3. online maximumが小さい
4. candidate IDの辞書順

で一意に選ぶ。一つ以上あれば
`a registered TT-SVD bundle beats the natural Fourier-sparse forced-quadratic baseline`
としてTT優位性仮説を`accepted`とする。0個なら
`registered TT-SVD bundles do not beat the natural Fourier-sparse forced-quadratic baseline`
として`rejected`とし、このforced coefficientに対するTT-SVD／TT-cross rolloutを開始しない。

storage-onlyまたはtiming-onlyの候補はそのまま診断に残すが採択しない。結果後にtolerance、候補、baseline、
seed、block数、閾値を変更しない。negative outcomeでもTT一般の不可能性とは解釈せず、固定tensorizationと
現在環境に限って「このテンソル化ではTTは不適切」と結論する。

### 主張境界

本gateは固定17²、固定zero-mean force、固定保存量葉、Q011eのquadratic \(W_2/R_2\)、binary64、登録6
uncapped TT-SVD bundle、現在CPU／NumPy／BLAS環境のlocal quadratic actionに限る。TT-cross、rank cap付き
rounding、GPU、parallel scaling、full 64-step TT rollout、higher-order coefficient、他grid／force／wall、
D3Q27、asymptotic complexity、energy、forced SSM existence／uniqueness、normal attraction、basinを
主張しない。Q011e、Q011e1、Q011f、Q011f1の既存outcomeは変更しない。

### Q011g 実行結果

validity `6 / 6`を通過した。全6 TT bundleはreconstruction、joint action、realification、one-step
invariance-defect preservationを通過したが、natural sparseより4格納指標を全て小さくする候補は0だった。
robust online-time winnerは3個あったもののstorage winnerと交わらず、hypothesisは`1 / 4`通過、
joint winner `0`で
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
- sparse／best-storage-TT offline median:
  `2.7488 / 401.5353 ms`
- sparse／fastest-TT online median:
  `0.7321 / 0.47460625 ms per joint action`
- fastest-TT online ratio／stored-scalar ratio:
  `0.6482806310613304 / 15.2224538792014`
- maximum TT reconstruction／action／realification error:
  `2.41559062578165e-14 / 3.84139374578316e-14 / 3.82602037711869e-14`
- natural (W_2/R_2) projection loss:
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

全候補の忠実度は十分なので、negative outcomeはTT近似不良ではなく、固定tensorizationの格納損失に
よる。output-lastのonline速度改善は診断として保持するが、storage-only／timing-onlyを採択しない規則を
変えない。従ってこのsealed forced coefficientではnatural Fourier-sparseを保持し、TT-crossへ進まない。
TT一般、別tensorization、GPU、full rollout、他grid／forceの不可能性は主張しない。

## Q011h: natural Fourier-sparse 64-step chart equivalence — 事前登録

### 問いと判定対象

Q011gで必須baselineとして残ったnatural Fourier-sparse (W_2/R_2)係数作用は、
Q011eのordered-dense real quadratic chartおよびreduced mapと、独立初期値から64 stepに
わたって同じ計算を行うか。

これはQ011f／Q011f1のshadowing成立を再採点するgateではない。各stepでパラメータ化法の
reduced coordinateとlifted stateをdense実装とsparse実装で別々進め、表現差の蓄積だけを
測る。全LBM orbitの64-step shadowing、残差次数、normal attraction、SSMの存在・一意性は
判定対象にしない。

### 封印入力

- Q011g artifact／runner newline-normalized SHA-256:
  `842ddbae2a28ccd2f11a112f23205cb049668b82691fdd180edc5ac20fecaa25` /
  `84ed56dabd0b0f870f1c6b27c9907c9566439ff03affe5aacc61ba611f4678fe`
- Q011g input／coefficient／fidelity／cost／result digest:
  `0632be40fccc212f23a271fa00ed80696f9a146a1b107e513b3a47edb9870a20` /
  `fc9edec10ee22abfaa2b763be9f69c9d72bfc59543aa34faea6ab206c35ab264` /
  `30dabea285da9070e2ebc0b351afde4695deb275d5f96ee66de1b1ca0468fcad` /
  `222a42321f4ae814478cc65102afcbc8926754d8cb7c48ed8ca2952e350767a7` /
  `e0874eabe2c5b924d0b5d7b56533cd695406166d4370b493a0dabdc0b22dbb2a`
- package-source SHA-256:
  `114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2`
- natural pair／sector／(W_2) fiber SHA-256:
  `a8917518620a67b9a2e3cbc2bddde81d0e4cb72033265e6a0c863cf0bdc02327` /
  `c47ee20550188307589755188d2d856e763e466430acadeb0e3342bd93db3114` /
  `3b1e553bee7a9231087639fdd8d72524eae93347175a393bb3d48d207f144d66`
- natural (R_2) sector `0 / 1 / 16` fiber SHA-256:
  `6689974b4f081a51a347930e5a74128b532a0727b27bd7f6de7a4b9348a89c40` /
  `7b49bd25f1eff1c2347e3493797113a2d3023417d9c4e970528562b5c4f275b6` /
  `0c66ebad5cc3a86048a8c6caeb38da081700cce37cfeea9d17380d395bec0678`
- projected ordered-dense (W_2/R_2) SHA-256:
  `a0b14a224a6f4d5921c4e21894821018d1df6badca8dd6b5d21d571756515ddc` /
  `b450cba9d58d0853bed95acaa9b4f2a69659e5c24b943708c0700d11c8962ee9`

Q011gのvalidity `6 / 6`、hypothesis `1 / 4`、`rejected` outcome、storage winner `0`、
joint winner `0`、TT-cross非許可をexactに再現する。Q011gを通じてQ011f1の`accepted`と
Q011fの`rejected`も封印する。係数はQ011gと同じ手順で一度だけfresh再構築し、
300 pair、sector count `102 / 54 / 54 / 45 / 45`、`94,968`格納real scalar、
`760,644` raw bytesと上記係数hashを照合する。

### independent 64-step campaign

- direction seed: `20260906`
- normalized real reduced directions: `24`
- direction SHA-256:
  `25fec4f35db569404d83f20f45bb510c226679999e1fa8bc21aa4e96d22926c8`
- amplitudes: `4.0e-4 / 9.6e-4 / 2.4e-3`
- amplitude SHA-256:
  `ee39c1d89f58484222107e494e8e2b87525544708f7c0067e18268ed9fb5b8a5`
- maximum reduced step: `64`
- checkpoints: `0 / 1 / 2 / 4 / 8 / 16 / 32 / 64`
- trajectory count: `24 * 3 = 72`
- reduced update count per implementation: `72 * 64 = 4,608`
- common-input action comparison count:
  `72 * 65 * 2 = 9,360`（dense-streamとsparse-streamの両coordinateで比較）
- checkpoint defect count per implementation: `72 * 8 = 576`

方向はQ011e、Q011e1、Q011f、Q011g action／invariance campaignの全方向とbitwise exact duplicate
`0`を要求する。3振幅はQ011f1までの
`1.6e-4 / 3.2e-4 / 4.8e-4 / 6.4e-4 / 1.28e-3 / 2.56e-3`およびQ011gの
`2.56e-3`と一致しない。この方向・振幅でshadowing slopeをfitしない。

### dense／sparseの独立更新

real reduced coordinate \(a\)に対し、Q011gのcoordinate map \(C\)で \(z=Ca\) へ移した
natural Fourier-fiber actionをphysical real spaceへ戻し、\(S_W(a),S_R(a)\)と書く。dense oracleは

\[
D_W(a)=\frac12W_2[a,a],\qquad D_R(a)=\frac12R_2[a,a]
\]

とする。同じ \(a_0\) から、二つの経路を独立に

\[
\begin{aligned}
a^d_{n+1}&=La^d_n+D_R(a^d_n), &
x^d_n&=b+Ta^d_n+D_W(a^d_n),\\
a^s_{n+1}&=La^s_n+S_R(a^s_n), &
x^s_n&=b+Ta^s_n+S_W(a^s_n)
\end{aligned}
\]

で64 step進める。sparse経路のquadratic actionにordered-dense tensorやreal Hessianを使わない。
ただしcommon linear term \(b,T,L\)とcomplex-to-real mapは共有する。各 \(n=0,\ldots,64\) で
\(a^d_n\)と \(a^s_n\) の両方をcommon inputとしてdense／sparse actionを比較する。

各checkpoint \(n\) では

\[
d^d_n=F(x^d_n)-W_d(a^d_{n+1}),\qquad
d^s_n=F(x^s_n)-W_s(a^s_{n+1})
\]

を別々計算する。これは縮約orbit上のone-step invariance defectであり、Q011f1の
full-state orbitに対する64-step shadowing errorとは異なる。

### 登録誤差と閾値

各trajectoryの \(A_0=\lVert a_0\rVert_2\)、\(X_0=\lVert Ta_0\rVert_2\) を固定し、

\[
E_a(n)=\frac{\lVert a^s_n-a^d_n\rVert_2}{A_0},\qquad
E_x(n)=\frac{\lVert x^s_n-x^d_n\rVert_2}{X_0},\qquad
E_d(n)=\frac{\lVert d^s_n-d^d_n\rVert_2}{A_0}
\]

を使う。分母を時間発展中の減衰normにせず、初期スケールで固定する。

- common-input dense／sparse joint action relative error: maximum `1e-11`
- sparse realification imaginary leakage relative norm: maximum `1e-11`
- \(E_a(n)\): all 72 trajectories／65 statesでmaximum `1e-11`
- \(E_x(n)\): all 72 trajectories／65 statesでmaximum `1e-11`
- \(E_d(n)\): all 576 checkpointsでmaximum `1e-10`
- dense／sparse defect norm差:
  `abs(||d_s||-||d_d||) / A_0 <= 1e-10`
- dense／sparseのchart、reduced coordinate、quadratic action、defectは全てfinite
- 全chart／full-map／next-lifted stateのminimum population: strict positive
- baseとのglobal conservation drift: maximum `1e-10`

relative joint actionは\((W\ action,R\ action)\)を連結したEuclidean normで計算する。dense action normが
machine tiny未満の場合のみmachine tinyを分母に使う。各trajectoryのcheckpoint hash、全65-state
metric array hash、aggregate digestをartifactに保存する。

### validity gate

1. Q011g artifact／runner／package source／5 digest／`rejected` outcomeとTT-cross非許可を再現し、
   Q011f1 `accepted`／Q011f `rejected`を変更しない。
2. natural係数を一度だけfresh再構築し、pair／sector count、shape、storage、projection、
   serialization、登録係数hashを全て再現する。
3. seed／direction／amplitude hash、prior duplicate `0`、72 trajectory、4,608 update、9,360 action比較、
   576 checkpointが完全である。
4. dense経路とsparse経路を独立更新し、sparse runtime pathがordered-dense係数作用を
   呼ばず、全値とhashが再現可能である。
5. finite strict JSON、input／coefficient／campaign／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、表現同値性を解釈しない。

### equivalence hypothesis gate

validity通過後、次の4項目を全て要求する。

1. 9,360 common-input作用のmaximum relative errorとimaginary leakageが登録閾値以下。
2. 全4,680 state record（72×65）で \(E_a,E_x\le10^{-11}\)。
3. 全576 checkpointで \(E_d\) とdefect norm差が`1e-10`以下。
4. completeness、finiteness、strict positivity、global conservation `1e-10`を通過。

全項目が通れば
`the natural Fourier-sparse chart reproduces the dense forced quadratic reduced trajectory through 64 steps`
として`accepted`とする。validityは通るが一つでも落ちれば
`the natural Fourier-sparse chart does not reproduce the dense forced quadratic reduced trajectory through 64 steps`
として`rejected`とする。結果後にseed、振幅、step、checkpoint、正規化、閾値を
変更しない。

### 主張境界

本gateは固定17²、固定zero-mean force、固定保存量葉、Q011eのquadratic chart、binary64、
登録72初期値、64 reduced step、8 one-step-defect checkpointに限る。Q011f／Q011f1の
shadowing outcome、all-time equivalence、uniform remainder、higher order、他grid／force／wall、D3Q27、
SSM存在・一意性、normal attraction、basinは主張しない。Q011gのTT棄却を変更せず、
TT-crossを開始しない。

### Q011h 実行結果

validity `5 / 5`、equivalence hypothesis `4 / 4`を通過し、
`the natural Fourier-sparse chart reproduces the dense forced quadratic reduced trajectory through 64 steps`
として`accepted`とした。Q011gの`rejected`とTT-cross非許可、Q011f1の`accepted`、
Q011fの`rejected`は変更していない。

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

sparse runtimeはdense quadratic fieldを所有せず、natural pair／sector／fiber作用だけで縮約経路を
更新した。全応答は登録閾値を大きく下回ったため、今後のforced quadratic chart実装には
natural Fourier-sparseを採用する。ただし本campaignは縮約経路とcheckpointのone-step defectであり、
full LBM orbitの64-step shadowingを新たに実行していない。all-time equivalence、uniform remainder、
forced SSM存在・一意性、normal attraction、basinは未認証である。

## Q011i: exact-dyadic zero-mean forcing compatibility repair — 事前登録

### 問いと先行するobstruction

Q011bの`zero-mean` waveformはbinary64 cosine値の和をtoleranceで判定している。しかし、
その17個のbinary64をexact dyadic rationalとして足すと

\[
\sum_{y=0}^{16}f_y
=-\frac{71}{302231454903657293676544}
=-\frac{71}{2^{78}}\ne0
\]

である。従ってこのraw sourceをexact-real mapの定数として読むと、Q011aと同じglobal
運動量ledgerによりexact fixed pointは存在できない。Q011bの結果はあくまbinary64数値解であり、
rigorous existence／uniquenessを主張していないため、Q011bの`accepted`を変更しない。

Q011iの問いは、このexact obstructionを除くreflection-symmetric binary64 waveformと、
local／global conserved momentがexact dyadic arithmeticで一致するbinary64 source tableを一意に作り、
Q011bの数値fixed-point／linear-spectrum baselineを登録摂動範囲で保てるか、である。

この修復mapはQ011b--Q011hのraw mapと数学的には別のmapである。通過してもQ011e--Q011hの
chart coefficientやshadowing outcomeを自動的に移さない。後続のfixed-point interval proofの対象を
厳密に定義するcompatibility gateである。

### 封印入力

- Q011b artifact／runner newline-normalized SHA-256:
  `477202184694da1386c6b5bc0f0441e004a7a44f7a7b064f1d060d50adc66c27` /
  `bac9448f280ce2dfb2e1627ce1558b792cb53e05746b94246baa6c329b8c8ef0`
- Q011b input／fixed-point／spectrum／result digest:
  `53dea81353ed4bcd77ab0c06533528f6d867d8b1bfa80d3d2ac3eddd7cf7dfbb` /
  `8db05ad1e7ae7806b70b6330d798f6dad05bc8718027ba13cb315116b021b17c` /
  `3ab8866e141b64a4d1d81bdfae1a70c61d8e7964d8480e2bd7ec7c7e174850fc` /
  `66c4b579dbd7d7c391fd2017f165c2de251ecf850b7c485cb936b9742c8addf6`
- Q011b raw waveform／source／stripe-state SHA-256:
  `0c1d55dfbd0611f7dcc3413ecde839e01487d6317e232c9362aad984e5bab162` /
  `7d69bfc45429c43e8094e03565fd71c83e5f48d3077437949b38d185d5fe7972` /
  `612ef4aca91a5c0100286988e0e7979342a9046c3c78fe60ee59ca4e232a7613`
- Q011h artifact／runner newline-normalized SHA-256:
  `2cfcf5cb76698ae8e451f448a3048e3d29a1b8aed034d3afa5c25f7fd66038f5` /
  `1e6848e572137d019531514235741b18ca10644dd7d14e304dc26d92d81cda9e`
- Q011h input／coefficient／campaign／result digest:
  `c9ea06c8961940f54dd3c02e3d68d7ba777e77fc9be2f0a7c3eecab5ab257b83` /
  `2ab44a23811ef9f7e1975fb27561dd92660938778bf73ef149e46ed04f399669` /
  `bbb6a489fc76af150a3a162f585b0b2e1a65d0445d5eb14ab11b280bc492a035` /
  `a78812d93063ed7deeaca09dad5feb2cf018fb1bec315dab94b4f02d27f75864`
- package-source SHA-256:
  `114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2`

Q011bのvalidity `6 / 6`、hypothesis `4 / 4`、numerical `accepted`、rigorous existence／uniqueness
`false`を再現する。Q011hのvalidity `5 / 5`、hypothesis `4 / 4`、`accepted`、Q011g
`rejected`とTT-cross非許可も再現する。

### reflection-symmetric exact-zero-sum waveform

`Fraction.from_float`を使い、入力binary64を最初からexact dyadicとして扱う。
nearest-even binary64への一回丸めを`RN`と書く。

1. \(g_0=f_0=3/2^{24}\) は変更しない。
2. \(i=1,\ldots,8\) で
   \[
   m_i=\operatorname{RN}\!\left(\frac{f_i+f_{17-i}}2\right),\qquad
   g_i=g_{17-i}=m_i
   \]
   とする。
3. 一つのpairだけを同じ向きにULP shiftする候補
   \(s=0,+1,-1,+2,-2,\ldots,+128,-128\) を各pairで列挙し、exact dyadic sumが0になる
   候補を探す。選択順は \((|s|,i,s)\) の辞書順とする。

この登録searchは pair `(3,14)`、`+7 ULP`を一意に選ぶ。修復後waveform SHA-256を
`025d6122db8e0d3512224ce4a2af82d57b5728ce0c7450425436218dd561bcbf`と登録する。
次を要求する。

- exact dyadic sum: `0`
- \(g_i=g_{17-i}\): bitwise exact for all 8 pairs
- \(g_0=f_0\): bitwise exact
- changed entry count: `<=11`
- maximum component perturbation: `<=5e-22`
- relative ℓ2 perturbation: `<=1e-14`
- FFT leakage outside \(k_y=\pm1\): `<=1e-14`
- zero modeとfirst-harmonic imaginary part: bitwise zero

raw exact sum nonzero、reflection-symmetrization直後のexact sum
`-7 / 37778931862957161709568`、selected pair／ULP countもartifactに保存する。

### exact-moment binary64 source table

各 \(g_y\) に対し、axis source amplitude \(c_y\)とdiagonal source amplitude \(d_y\)を次で決める。

1. \(d_y^{(0)}=\operatorname{RN}(g_y/12)\)。
2. \(d_y^{(0)}\)から `0,+1,-1,...,+8,-8 ULP` の順でcandidateを調べ、
   \[
   c_y=\frac{g_y}{2}-2d_y
   \]
   がexact binary64で表せる最初の \(d_y\) を選ぶ。
3. D2Q9 velocity \(q=(c_{qx},c_{qy})\) に対し
   \[
   S_q(y)=
   \begin{cases}
   0,&c_{qx}=0,\\
   c_{qx}c_y,&c_{qy}=0,\\
   c_{qx}d_y,&|c_{qy}|=1
   \end{cases}
   \]
   とする。

これによりexact dyadic arithmeticで各siteの

\[
\sum_q S_q=0,\qquad
\sum_q c_{qx}S_q=g_y,\qquad
\sum_q c_{qy}S_q=0
\]

が成り立つ。さらに \(\sum_y g_y=0\) なのでglobal 3-momentもexact zeroである。
登録source shapeは`(17,1,9)`、nonzero count `102`、SHA-256は
`24bb558464cce4ac154b3f2574bd1fe816d11d58c9365e8312f12b0a389df490`とする。

- all 17 local exact-moment identities: exact pass
- global mass／x-momentum／y-momentum source: exact `0 / 0 / 0`
- \(d_y\) search maximum shift: `<=1 ULP`
- raw Q011b sourceに対するmaximum component perturbation: `<=1e-22`
- raw Q011b sourceに対するrelative ℓ2 perturbation: `<=1e-14`

各加減算の中間binary64値ではなく、保存した各source entryをexact dyadicに変換した後の
ledgerをgateに使う。

### repaired numerical fixed-point／spectrum bridge

修復sourceを加える以外はQ011bと同じBGK collision、periodic streaming、conservative filter、
\((\omega,\eta)=(1.5,0.01)\)を使う。Q011bと150-dimensional fixed-leaf basisは数値bridgeにのみ
再利用する。このbasisをrigorous coordinateとは呼ばない。

Newtonはstart `zero / sealed-Q011b-coordinate`、maximum 12 step、line search
`1,1/2,...,1/64`とし、次を要求する。

- projected／full／maximum-component residual:
  `<=5e-13 / 5e-12 / 5e-13`
- two-start solution distance／relative distance:
  `<=1e-11 / <=1e-9`
- repaired／sealed-Q011b stripe-state ℓ2 distance:
  `<=1e-11`
- same distance / sealed-state departure from rest:
  `<=1e-6`
- minimum population／density: strict positive

修復stateでQ011bの17 \(k_x\)-block spectrumをfresh再計算し、

- fixed-leaf eigenvalue count: `2,598`
- maximum block-matrix relative perturbation vs sealed Q011b state: `<=1e-10`
- maximum blockwise spectrum absolute Hausdorff distance: `<=1e-9`
- full fixed-leaf spectral radius: `<=0.9999`
- minimum σmin(I-J): `>=1e-4`
- maximum condition(I-J): `<=1e6`
- conjugate-spectrum／Schur／block-action gate: Q011bと同じ閾値を通過

を要求する。これはnumerical stability bridgeであり、区間固有値包含や厳密fixed-point proofではない。

### validity gate

1. Q011b／Q011h artifact、runner、package source、登録digest、outcomeとclaim boundaryを再現する。
2. raw waveform／source／state hash、raw exact dyadic sum、Q011a型global-momentum obstructionを再現する。
3. waveform repair searchを全候補で完了し、選択順、pair／ULP witness、hash、exact symmetry／sumを再現する。
4. source constructionを17 siteで完了し、shape／count／hash／search trace／local／global exact ledgerを再現する。
5. repaired Newtonと2 start、17 spectrum blockを登録protocolで完了し、全値がfiniteである。
6. finite strict JSON、input／repair／fixed-point／spectrum／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、repaired mapのcompatibilityを解釈しない。

### compatibility hypothesis gateと停止規則

validity通過後、次の4項目を全て要求する。

1. raw exact-momentum obstructionがnonzeroで、repaired waveform／sourceのexact local／global ledgerが0。
2. waveform／source摂動、reflection symmetry、Fourier leakageが登録閾値内。
3. repaired two-start Newton、sealed-Q011b-state bridge、positivityが登録閾値内。
4. repaired full fixed-leaf spectrumとsealed Q011b spectrumの差、stability、resolventが登録閾値内。

全項目が通れば
`the exact-dyadic zero-mean repair preserves the numerical forced fixed-point and linear-spectrum baseline`
として`accepted`とする。validityは通るが一つでも落ちれば
`the exact-dyadic zero-mean repair does not preserve the registered numerical baseline`
として`rejected`とする。結果後にpair、ULP search、source allocation、Newton start、閾値を変更しない。

acceptedの場合だけ、次のQ011jでexact affine fixed-leaf coordinateとinterval Newton／Krawczykによる
repaired fixed pointの存在・局所一意性認証を事前登録する。それまでforced SSM existence／
uniqueness、rigorous spectrum、full external nonresonance、normal attractionへ進まない。

### 主張境界

本gateは固定17²、固定振幅、periodic repaired source、fixed-leaf numerical Newton、binary64 linear
spectrumに限る。Q011b--Q011hのraw-map outcomeを変更せず、repaired mapへのchart coefficient、
residual order、shadowingを移さない。区間fixed-point存在・一意性、区間spectrum、external nonresonance、
forced SSM、normal attraction、basin、他grid／force／wall、D3Q27は主張しない。

### Q011i 実行結果

validity `6 / 6`、hypothesis `4 / 4`を通過し、
`the exact-dyadic zero-mean repair preserves the numerical forced fixed-point and linear-spectrum baseline`
として`accepted`とした。

- raw exact waveform sum／global x-momentum source:
  `-71 / 2^78` / `-267 / 2^80`
- waveform search candidate count／selected pair／shift: `2,056 / (3,14) / +7 ULP`
- repaired exact waveform sum／changed entry count: `0 / 11`
- waveform maximum-component／relative-ℓ2／Fourier-leakage perturbation:
  `1.4558378780933287e-22 / 3.9903677672599853e-16 / 2.661531424982623e-16`
- source shape／nonzero count／maximum selected shift: `(17,1,9) / 102 / 1 ULP`
- source maximum-component／relative-ℓ2 perturbation:
  `4.963083675318166e-23 / 4.0883745079611583e-16`
- repaired local exact ledger: `17 / 17` pass
- repaired global mass／x-momentum／y-momentum ledger: exact `0 / 0 / 0`
- repaired waveform／source SHA-256:
  `025d6122db8e0d3512224ce4a2af82d57b5728ce0c7450425436218dd561bcbf` /
  `24bb558464cce4ac154b3f2574bd1fe816d11d58c9365e8312f12b0a389df490`
- zero／sealed-coordinate start Newton steps: `2 / 0`
- terminal projected／full／component residual:
  `3.4838391155252677e-16 / 4.088062755440557e-16 / 1.6653345369377348e-16`
- two-start state distance／repaired-vs-sealed Q011b state distance: `0 / 0`
- representative repaired／sealed stripe-state SHA-256:
  `612ef4aca91a5c0100286988e0e7979342a9046c3c78fe60ee59ca4e232a7613`
- minimum population／density: `0.027775908313351423 / 0.9999999999999997`
- maximum block-matrix relative perturbation／spectrum Hausdorff distance: `0 / 0`
- fixed-leaf eigenvalue count／spectral radius: `2,598 / 0.9920954673551019`
- minimum σmin(I-J)／maximum condition(I-J): `0.00649328212134047 / 360.53472657220163`
- input／repair／fixed-point／spectrum／result digest:
  `81a1dc3f9fe934d8e9391dbfe6b80701d68c04b7db954da2f62e92b581dd5b51` /
  `910a82fa1485ce8ad6b488c5bb71ad0c8bcb12b98b6202ebc3805caa8f4a3239` /
  `3adfbcfc7d5e9c3396bbfb60b8d10dce6ff080b90097b82f40b4c057b8518f1e` /
  `5e63b9cc22a662238391dc83b8de1a81eb259af25b3ad2335e481bb0cf83466d` /
  `ac94658b95d2ae1f190fab57af3bd80dbf50a4addd37f6bb7bee27d6aa1d2398`
- runner／artifact newline-normalized SHA-256:
  `2cec0472422ba02bb925e8c90336000058def7c36303479a4037405f873b9b88` /
  `1c8b11a3ae47895a79639a5cfe901ec936fbdde8d10273c56c1578b9a88780ea`

修復後のsourceはexact-real ledgerを閉じる一方、登録binary64計算ではQ011b fixed pointと全17
linear blockをbitwiseに変えなかった。これは修復mapのfixed-point numerical baselineを確立するが、
Q011e--Q011hのraw-map coefficient、residual-order、shadowingは移植しない。Q011bのnumerical
`accepted`も再採点しない。次は事前登録どおりQ011jでexact affine fixed-leaf coordinateと
interval Newton／Krawczykによる存在・局所一意性証明を行う。それまではrigorous fixed point、
rigorous spectrum、forced SSM存在・一意性、normal attractionを主張しない。

## Q011j: repaired fixed-point interval Krawczyk proof — 事前登録

### 問いと対象map

Q011iでexact dyadic local／global source ledgerを閉じたrepaired \(17\times1\) stripe mapは、
固定mass／momentum葉上にexact fixed pointを持ち、その解は登録box内で局所一意か。ここで対象は
binary64実装そのものではなく、D2Q9 weight、\(\omega=3/2\)、\(\eta=1/100\)、Q011i sourceの
保存されたbinary64 entryをexact rationalとして読むreal-analytic mapである。x-independent stripeを
17列へexact replicationしたfull \(17^2\) periodic stateにも同じfixed pointを与えることを構造的に確認する。

### 封印入力

- Q011i artifact／runner newline-normalized SHA-256:
  `1c8b11a3ae47895a79639a5cfe901ec936fbdde8d10273c56c1578b9a88780ea` /
  `2cec0472422ba02bb925e8c90336000058def7c36303479a4037405f873b9b88`
- Q011i input／repair／fixed-point／spectrum／result digest:
  `81a1dc3f9fe934d8e9391dbfe6b80701d68c04b7db954da2f62e92b581dd5b51` /
  `910a82fa1485ce8ad6b488c5bb71ad0c8bcb12b98b6202ebc3805caa8f4a3239` /
  `3adfbcfc7d5e9c3396bbfb60b8d10dce6ff080b90097b82f40b4c057b8518f1e` /
  `5e63b9cc22a662238391dc83b8de1a81eb259af25b3ad2335e481bb0cf83466d` /
  `ac94658b95d2ae1f190fab57af3bd80dbf50a4addd37f6bb7bee27d6aa1d2398`
- Q011i waveform／source／representative stripe-state SHA-256:
  `025d6122db8e0d3512224ce4a2af82d57b5728ce0c7450425436218dd561bcbf` /
  `24bb558464cce4ac154b3f2574bd1fe816d11d58c9365e8312f12b0a389df490` /
  `612ef4aca91a5c0100286988e0e7979342a9046c3c78fe60ee59ca4e232a7613`
- package-source SHA-256:
  `114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2`

Q011i validity `6 / 6`、hypothesis `4 / 4`、`accepted`、exact-zero repaired ledger、
Q011b raw numerical outcome不変、Q011e--Q011h coefficient非移植をexactに再現する。

### exact affine fixed-leaf coordinate

stripe populationをsite-major／D2Q9 velocity orderで153成分にflattenする。pivotをsite 0の
population `q=0,1,2`、すなわちvelocity `(0,0),(1,0),(0,1)`とし、残る150成分を
coordinate \(x\in\mathbb R^{150}\) とする。free entryのglobal mass／momentumを
\((M_f,P_{x,f},P_{y,f})\)とすると、target stripe moment `(17,0,0)`に対して

\[
f_{0,1}=-P_{x,f},\qquad
f_{0,2}=-P_{y,f},\qquad
f_{0,0}=17-M_f-f_{0,1}-f_{0,2}
\]

でpivotをexactに復元する。このaffine liftを \(L(x)\)、free-entry extractionを \(E\) とする。
pivot moment matrixのdeterminantはexact `1`、linear lift shapeは`153 x 150`、rankは`150`、
infinity operator normは`186`でなければならない。全coordinateで

\[
M(Lx)=17,\qquad P_x(Lx)=P_y(Lx)=0,\qquad E(Lx)=x
\]

をentrywise exact rational arithmeticで確認する。center \(x_0\)はQ011i representative
stripe-stateの150 free binary64 entryを`Fraction.from_float`でexact化したものとする。
\(L(x_0)\)とsealed stateはfree entryがbitwise同一で、3 pivotだけがexact leafへ移る。
maximum pivot correction `<=1e-14`を要求する。

reduced residualは

\[
G(x)=E\{\Phi_{\rm repaired}(Lx)-Lx\}\in\mathbb R^{150}
\]

とする。repaired sourceのglobal momentがexact 0で、collision、periodic streaming、filterが
global 3-momentをexactに保つため、\(G(x)=0\)ならpivot residualもexact 0であることを
pivot moment matrixから確認する。

### exact map／Jacobian oracle

D2Q9 equilibriumを

\[
f_q^{eq}=w_q\left[\rho+3c_q\cdot j+
\frac{9(c_q\cdot j)^2-3(j\cdot j)}{2\rho}\right]
\]

として`Fraction`だけで評価し、collision、Q011i source、periodic streaming、x-independent
filter `(1-eta/2, eta/4, eta/4)`をexactに合成する。Jacobianもこの式を解析微分し、
\(J_G=E(D\Phi L)-I\)をexact rational point／interval matrixとして構成する。

- exact center mapをfloatへ変換した値とQ011i repaired binary64 stepのrelative ℓ2 discrepancy:
  `<=1e-12`
- exact center Jacobianをfloatへ変換した値と独立Q011b analytic Jacobian actionから組み立てた
  affine reduced Jacobianのmaximum relative discrepancy: `<=1e-12`
- exact quadrature moments、source ledger、collision／streaming／filter global-moment identities:
  entrywise exact pass
- 全候補boxでdensity lower: strict positive
- point Jacobian \(J_G(x_0)\)は各interval Jacobian enclosureにentrywise含まれる

このoracle checkが落ちた場合は証明結果を解釈しない。

### outward interval Krawczyk protocol

point preconditioner \(C\)は、exact \(J_G(x_0)\)をbinary64へ変換して一度だけ
`scipy.linalg.inv`した150×150 matrixとし、その各binary64 entryをexact dyadic pointとして扱う。
radius候補を次の10個に固定する。

`1e-12 / 1e-11 / 1e-10 / 1e-9 / 1e-8 / 1e-7 / 1e-6 / 1e-5 / 1e-4 / 1e-3`

各 \(r\) で \(X_r=x_0+[-r,r]^{150}\) とする。map／Jacobian enclosureまではexact `Fraction`、
dense preconditioner積だけをGMPY2 `2.3.1`／MPFR `4.2.2`で外向き丸めする。primary precisionは
256 bit、independent replayは384 bitとし、rational endpoint変換、積、和、absolute row sumの
下端には`RoundDown`、上端には`RoundUp`を使う。全MPFR endpointは`as_integer_ratio`でexact dyadicへ
戻してからgate判定する。caller context不変、overflow／underflow／invalid／division-by-zero flagなしを要求する。

\[
z=C G(x_0),\qquad
\beta=\|I-CJ_G(x_0)\|_\infty,
\]

\[
\Delta(r)=\sup_{J\in J_G(X_r)}\|J-J_G(x_0)\|_\infty,qquad
q(r)=\beta+\|C\|_\infty\Delta(r),
\]

\[
u(r)=\frac{\|z\|_\infty}{r}+q(r)
\]

の外向きupperを計算する。このときKrawczyk imageは
\(x_0+[-\|z\|_\infty-q(r)r,\|z\|_\infty+q(r)r]^{150}\)に含まれる。
robust passをprimary／replayの両方で

\[
\beta\le10^{-8},\qquad q(r)\le0.9,\qquad u(r)\le0.9
\]

と定義する。少なくとも1候補のpassを要求し、採択radiusは両precisionでpassする最大候補とする。
384-bit upperは対応する256-bit upper以下、採択radiusは両precisionで同一でなければならない。

### validity gate

1. Q011i artifact／runner／package source／5 digest／3 hash／`accepted` outcomeとclaim boundaryを再現する。
2. exact affine lift／extractor、pivot determinant、shape／rank／norm、center、全moment identityを再現する。
3. exact map／Jacobian oracleと独立binary64 map／Jacobian comparisonを登録閾値内で完了する。
4. 全10 radiusでexact interval Jacobian、point containment、positive-density domainを完了する。
5. 256／384-bit outward protocol、context／flag監査、preconditioner、全scalar upperを完了する。
6. finite strict JSON、input／coordinate／oracle／proof／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、fixed-point theoremを主張しない。

### existence／local-uniqueness hypothesis gateと停止規則

validity通過後、次の4項目を全て要求する。

1. repaired exact mapがfixed leafとx-independent replicationを保ち、\(G=0\)がfull residual 0を含意する。
2. center boxがstrict-positive population／density domain内にあり、point inverse defectが`<=1e-8`。
3. 少なくとも1候補が両precisionで`q<=0.9`かつ`u<=0.9`を満たし、最大pass radiusが一致する。
4. selected Krawczyk imageがbox interiorにstrict inclusionし、`q<1`からpreconditioner／Jacobian regularityと
   box内の局所一意性条件が成立する。

全項目が通れば
`the repaired periodic forcing admits a locally unique exact fixed-leaf fixed point in the registered rational box`
として`accepted`とする。validityは通るが一項目でも落ちれば
`the registered interval boxes do not certify a locally unique repaired fixed point`
として`rejected`とする。これはfixed pointの不存在を意味しない。結果後にpivot、center、precision、
radius grid、preconditioner、`0.9` capを変更しない。

acceptedの場合だけ、次のQ011kでinterval fixed-point box上のrigorous fixed-leaf spectrum、
selected／external split、nonresonance readinessを事前登録する。rejectedなら最初のinverse-defect、
domain、Jacobian-variation、inclusion failureを局在化する。

### 主張境界

本gateは固定17²、固定振幅、periodic repaired source、x-independent fixed leaf、登録rational box内の
存在と局所一意性に限る。raw Q011b map、Q011e--Q011h coefficient、区間spectrum、forced SSM、
normal attraction、basin、他grid／force／wall、D3Q27は主張しない。局所一意性をglobal uniquenessや
wall-bounded Poiseuille／Couette解へ読み替えない。

### Q011j 実行結果

validity `6 / 6`、hypothesis `4 / 4`を通過し、
`the repaired periodic forcing admits a locally unique exact fixed-leaf fixed point in the registered rational box`
として`accepted`とした。

- affine pivot determinant／lift shape／rank／infinity norm:
  `1 / 153 x 150 / 150 / 186`
- center maximum pivot correction: `1.1032841307212493e-15`
- exact-center reduced residual maximum: `2.2024432251775355e-16`
- exact-vs-binary64 map／independent-Jacobian relative discrepancy:
  `1.994466096750315e-16 / 1.4468366996163912e-16`
- registered／passing radius count: `10 / 5`
- selected free-coordinate radius／first failed radius: `1e-8 / 1e-7`
- selected ambient-component radius upper: `1.86e-6`
- selected-box population／density lower:
  `0.02777589831335142 / 0.9999944000000008`
- point Jacobian condition／preconditioner infinity norm:
  `1672.0533600047117 / 714.5779769798695`
- 256-bit point inverse-defect／center-correction upper:
  `2.0361209046326675e-13 / 9.043895266505443e-16`
- selected 256-bit contraction／Krawczyk utilization upper:
  `0.1997569427734526 / 0.19975703321240526`
- 384-bit upper containment／selected-radius agreement: `pass / pass`
- coordinate／lifted-center／exact-Jacobian／preconditioner SHA-256:
  `508f175fc7d1d62d253b5e34877a25fded6f4d207ef26f281a01d10eb5571ed8` /
  `c85cddc2072cb2e86d1a73024da97828d4a7f21f10b631c86a5d9ee0297c72dd` /
  `236083b8ad6f5f8426deb3371df3043bd9a8ee50071a90f466659173fe1dc504` /
  `1d157cd3ef26ae109f45698dd049e50677f6ec6432be0d17b8a09b6d41152035`
- input／coordinate／oracle／proof／result digest:
  `a183f4830c757b58122132cf64111fd5375636affdb6c0b31e1cd90e89085799` /
  `adaef353b8b64509334794c6014dc8b88e81ca2b776c3b65bd4d50911ae9452b` /
  `177468a48f667ddd922ed4b979d3e7e5d4cc0ed3afffe27a34651060da8e0f5f` /
  `1080fcea24358422514bba7fb9881928269c853cb4d12b0282e63840c56124c0` /
  `ddad5beca9693eeab726382ac864d01a27b749d579c2ec8f12dd9f8c499db934`
- runner／artifact newline-normalized SHA-256:
  `23a7a3a272264be3eb5330b2456192bd797aa968c4f795e2cbe8e337fc8fe4b5` /
  `74a2e084137699739c14d980b05676e14e6802b4018b3893d3d05270850c2c5a`

`q<=0.199757<1`でNewton-like mapがselected boxをstrict self-mapとし、preconditionerも
Neumann boundでnonsingularなので、exact repaired stripe mapにはfixed pointが存在してbox内で一意である。
periodic x-independent replicationによりfull 17² mapにも同じfixed pointが存在する。ただし本結果は
global uniqueness、basin、raw Q011b exact map、Q011e--Q011h coefficient、区間spectrum、forced SSM、
normal attractionへ広げない。次はQ011kでcertified box上のrigorous fixed-leaf spectrumと
selected／external splitを事前登録する。

## Q011k: repaired fixed-point interval spectrum and selected／external split — 事前登録

### 問いと証明対象

Q011jで存在・局所一意性を認証したexact repaired fixed point \(x_\ast\) におけるfull
\(17^2\) periodic mapのfixed-leaf linearizationはstrictly stableか。またQ011c2から引き継ぐ
24-dimensional first-shell selected clusterは2574-dimensional external spectrumから交換なく分離され、
quadratic selected eigenvalue productは対応するexternal sectorとspectrally nonresonantか。

本gateはcluster内部の個別branch labelを要求しない。判定単位はx-Fourier blockごとのselected
invariant clusterであり、selected／external disc unionの分離とhomotopy eigenvalue countを証明する。

### 封印入力

- Q011j artifact／runner newline-normalized SHA-256:
  `74a2e084137699739c14d980b05676e14e6802b4018b3893d3d05270850c2c5a` /
  `23a7a3a272264be3eb5330b2456192bd797aa968c4f795e2cbe8e337fc8fe4b5`
- Q011j input／coordinate／oracle／proof／result digest:
  `a183f4830c757b58122132cf64111fd5375636affdb6c0b31e1cd90e89085799` /
  `adaef353b8b64509334794c6014dc8b88e81ca2b776c3b65bd4d50911ae9452b` /
  `177468a48f667ddd922ed4b979d3e7e5d4cc0ed3afffe27a34651060da8e0f5f` /
  `1080fcea24358422514bba7fb9881928269c853cb4d12b0282e63840c56124c0` /
  `ddad5beca9693eeab726382ac864d01a27b749d579c2ec8f12dd9f8c499db934`
- Q011c2 artifact／runner newline-normalized SHA-256:
  `c1794ca72eebd60c4bc097278495218e9e2d2e84bdacd0f478e510a80fcba42a` /
  `87bdfc1ed20e6e68e4a395d36399adbab19e82809c626ecefa65a342ce42b9d2`
- Q011c2 input／path／holdout-spectrum／endpoint／result digest:
  `de4b0c4d38d0efcff9c7db4bbef66ba6d081a6703c732dbd7116a294020459f2` /
  `36be8801af32ae178e91e049b2640ed4bb058107abdf2df2af8860930c53c27d` /
  `d7319399578d3755ee0679122dec5e6b6d3454e394295bd62886920d104b0d72` /
  `8c78791883b82f4a964d0c102006d9295b7b96733e77dea93249f30dc427b6a8` /
  `8c23b985d69ffaa980e752e5d262184c0a6d466681d9d44fa4f0e9101df02b0c`

Q011j validity `6 / 6`、hypothesis `4 / 4`、`accepted`、selected radius `1e-8`、
256／384-bit containmentを再現する。Q011c2 validity／hypothesis、`accepted`、endpoint factor `1`の
block `0 / 1 / 16` selected dimensions `6 / 9 / 9`と24 selected eigenvalue recordsを再現する。
Q011c2 projectorや個別eigenvectorは証明入力にせず、selected centerの識別にendpoint eigenvalue setだけを使う。

### Q011j contractionからのroot enclosure

Q011jのselected box \(X=x_0+[-10^{-8},10^{-8}]^{150}\) 上で、Newton-like map
\(T(x)=x-CG(x)\) は

\[
\|T(x)-T(y)\|_\infty\le \bar q\|x-y\|_\infty,
\qquad
\|T(x_0)-x_0\|_\infty\le \bar z
\]

を満たす。256-bit primary artifactのexact dyadic upperを変更せず読み、

\[
\rho_\ast=\frac{\bar z}{1-\bar q}
\]

をexact `Fraction`で計算する。Q011jの一意なfixed pointについて
\(\|x_\ast-x_0\|_\infty\le\rho_\ast\) が従う。登録sanity capを

\[
\rho_\ast\le2\times10^{-15}
\]

とし、affine liftの登録norm `186`からambient population component radiusを
\(186\rho_\ast\)で包囲する。384-bit replayから同じ式で得るupperは256-bit upper以下でなければならない。
元の`1e-8` box全体のspectrumを主張せず、その内部で唯一存在するexact rootを含むこの導出boxを対象にする。

### exact interval block family

x-translation invarianceによりfull linearizationを17個のx-Fourier blockへexactに分解する。

- block `0`: Q011jのexact affine fixed-leaf chartで
  \(A_0(x)=I+J_G(x)\in\mathbb R^{150\times150}\) とする。
- block `n=1,...,16`: stripe population全153成分上のcomplex block
  \(A_n(x)\in\mathbb C^{153\times153}\) とする。global conservation constraintはnonzero x-waveに
  自動的に直交するため3成分を除去しない。
- dimension countは`150 + 16 * 153 = 2598`でなければならない。

equilibrium derivativeはQ011jのexact rational式、collisionは\(\omega=3/2\)、y-streamingはexact permutation、
x-streaming phaseとfilterの`sin/cos(2*pi*n/17)`はQ007hと同じ96-term Machin pi、64-term Taylor、
degree-127 remainderでrational rectangle enclosureを作る。root coordinate boxをQ011j affine liftで包囲し、
全block entryを`Fraction` endpointのcomplex rectangleとして構成する。density lowerはstrict positive、
conjugate block `n`／`17-n`はentrywise conjugate enclosureを持たなければならない。

各blockのbinary64 proposal \(\widehat A_n\)はexact lifted centerをfloatへ変換し、登録analytic block actionから
一度だけ組み立てる。block `0`はexact rational \(I+J_G(x_0)\)のbinary64 conversionを使う。
interval familyとproposalの差をentrywise包囲し、

\[
\delta_n=\sup_{x\in X_\ast}\|A_n(x)-\widehat A_n\|_\infty
\]

の外向きupperを得る。全proposal entryは対応するfamily rectangleから有限距離にあり、独立binary64
block actionとのrelative discrepancy `<=1e-12`を要求する。

### dual-precision Bauer--Fike protocol

各代表block `n=0,...,8`で`numpy.linalg.eig`からproposal
\((\widehat\Lambda_n,V_n)\)を得る。列はeigenvalueのreal／imaginary partでstable sortし、各列の最大絶対値pivotを
最小index tie-breakで選び、そのpivotがnonnegative realとなるようphase normalizeする。
\(W_n=V_n^{-1}\)を一度だけbinary64で計算し、全binary64 entryをexact dyadic pointとして扱う。
block `9,...,16`は対応する代表blockのconjugate proofをtransportし、独立float spectrumとのHausdorff
discrepancy `<=1e-10`を確認する。

exact dyadic dot productとcomplex absolute row sumはGMPY2／MPFRの外向き丸めで計算する。
primary `256 bit`、independent replay `384 bit`とし、下端は`RoundDown`、上端は`RoundUp`、
全endpointを`as_integer_ratio`でexact dyadicへ戻す。各blockで

\[
\epsilon_n=\|I-W_nV_n\|_\infty,
\qquad
\beta_n=\frac{\|W_n\|_\infty}{1-\epsilon_n},
\]

\[
r_n=\|\widehat A_nV_n-V_n\widehat\Lambda_n\|_\infty
      +\delta_n\|V_n\|_\infty,
\qquad
R_n=\|V_n\|_\infty\beta_n^2r_n
\]

のupperを求める。`epsilon_n<=1e-8`を全blockに要求する。すると\(V_n\)はnonsingularで、
\(\widehat A_n\)のapproximate diagonal formから任意の\(A_n(x_\ast)\)までのhomotopy spectrumは
center \(\widehat\lambda_{n,j}\)、radius \(R_n\)のdisc unionに入る。384-bitの全upperは対応する
256-bit upper以下で、全hash／extremal block／判定が一致しなければならない。

### selected／external cluster countとquadratic spectral distance

Q011c2 endpointのblock `0 / 1 / 16` selected eigenvalue setを、同blockのBauer--Fike centerへ
minimum-total-distance bijectionで対応させる。selected countは`6 / 9 / 9`、maximum matching distance
`<=1e-10`を要求し、他のcenterは全てexternalとする。他blockは全centerをexternalとする。

各selected blockで

\[
d_{\mathrm{split},n}
=\min_{s\in S_n,e\in E_n}|\widehat\lambda_s-\widehat\lambda_e|-2R_n
\]

をexact outward lowerで評価する。これが正ならhomotopy中にselected disc unionとexternal disc unionは
交わらず、cluster内部のpermutationを許したままeigenvalue countが保存される。

さらに24 selected centerのunordered pair `24 * 25 / 2 = 300`を全列挙する。x-wave sectorを
`(n_i+n_j) mod 17`とし、product disc radiusを

\[
R_{ij}^{\times}=|\widehat\lambda_i|R_j+|\widehat\lambda_j|R_i+R_iR_j
\]

で包囲する。対応output sectorの全external center \(\widehat\mu_e\)に対し

\[
d_{ij,e}=|\widehat\lambda_i\widehat\lambda_j-\widehat\mu_e|
          -R_{ij}^{\times}-R_e
\]

のminimum lowerを求める。これはeigenvalue-level quadratic external nonresonanceだけを意味し、
nonnormal homological inverse norm、coefficient bound、SSM存在・一意性を意味しない。

### validity gate

1. Q011j／Q011c2のartifact、runner、全登録digest、outcome、claim boundaryを再現する。
2. contraction-derived root radius、384-bit containment、affine lift、positive densityをexactに再現する。
3. 17 block、dimension `2598`、exact interval analytic action、conjugacy、independent block actionを再現する。
4. 全代表blockのdeterministic eig proposal、phase／sort、inverse、residual、interval-family距離を完了する。
5. 256／384-bit outward context／flag監査、全Bauer--Fike upper／lower、transport proofを完了する。
6. Q011c2 selected matching、count `24 / 2574`、300 pairと全external比較を漏れなく完了する。
7. finite strict JSON、input／root／block／proof／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、spectrum enclosureを解釈しない。

### spectrum／split／nonresonance hypothesis gateと停止規則

validity通過後、次の5項目を全て要求する。

1. 全代表blockで`epsilon<=1e-8`、dual-precision containment、transport conjugacyが通る。
2. 全2598 eigenvalue discのmodulus upperがQ011b ceiling `0.9999`以下である。
3. selected／external countが`24 / 2574`で、minimum complex disc-union gapが`>=1e-6`である。
4. selected minimum modulus lower minus external maximum modulus upperが`>=1e-6`である。
5. 300 selected quadratic productsに対するminimum external spectral-distance lowerが`>=1e-6`である。

全項目が通れば
`the exact repaired fixed point has a rigorously stable and quadratically nonresonant selected/external spectral split`
として`accepted`とする。validityは通るが一項目でも落ちれば
`the registered Bauer--Fike enclosures do not certify the repaired selected/external spectral split`
として`rejected`とする。これはstability、split、nonresonanceの数学的不成立を意味せず、最初に落ちた
block、inverse defect、disc radius、stability margin、split gap、quadratic pairを記録する。結果後にroot bound、
block coordinate、eig normalization、precision、`1e-8 / 0.9999 / 1e-6` thresholdを変更しない。

acceptedの場合だけ、次のQ011lでinterval Sylvester／homological inverse boundを事前登録する。
rejectedなら個別eigenvector discをordered Schur cluster／Riesz projector enclosureへ置き換えるか、
contraction centerを認証付きで更新してroot boxを縮小する。inconclusiveなら最初のprotocol failureだけを修復する。

### 主張境界

本gateは固定17²、固定振幅、periodic repaired exact map、その一意なx-independent fixed point、
fixed-leaf linear spectrumとeigenvalue-level quadratic external nonresonanceに限る。raw Q011b map、
Q011e--Q011h raw-map coefficient、rigorous homological inverse、forced SSM存在・一意性、spectral quotient smoothness、
nonlinear normal attraction、basin、他grid／force／wall、D3Q27は主張しない。selected／external modulus gapを
非線形normal attractionへ読み替えない。

### Q011k 実行結果

validity `7 / 7`、hypothesis `5 / 5`を通過し、
`the exact repaired fixed point has a rigorously stable and quadratically nonresonant selected/external spectral split`
として`accepted`とした。

- contraction-derived root coordinate／ambient component radius upper:
  `1.1301435463682045e-15 / 2.1020669962448604e-13`
- root-box population／density lower:
  `0.027775908313350292 / 0.999999999999368`
- block／fixed-leaf dimension: `17 / 2598`
- maximum point-proposal／interval-family infinity distance upper:
  `2.6239799629414762e-15 / 3.159514510653837e-11`
- maximum inverse defect／point eigendecomposition residual upper:
  `2.659104047707985e-12 / 1.364939039226648e-13`
- maximum Bauer--Fike radius／witness block: `0.000785981566123045 / 4`
- fixed-leaf modulus upper／witness: `0.9921085054987441 / block 0, center 147`
- selected／external／total count: `24 / 2574 / 2598`
- maximum Q011c2 selected matching distance: `9.447267645531843e-15`
- minimum selected／external complex disc gap lower: `0.023904592735975918`
- selected minimum／external maximum modulus bound:
  `0.9837705640652026 / 0.9817228739761981`
- normal modulus gap lower: `0.0020476900890045394`
- quadratic unordered pair／external comparison count: `300 / 44010`
- minimum quadratic external spectral-distance lower: `0.0001793727151978435`
- minimum quadratic witness:
  `pair 173: block 1 center 144 * block 16 center 144 -> block 0 external center 143`
- exact quadratic-pair digest:
  `be8548cd8ac4bea69b71b7bb0617f232ddcc9535d33b13279e371cc242cf2b79`
- input／root／block／proof／result digest:
  `f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2` /
  `f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc` /
  `7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8` /
  `1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4` /
  `2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e`
- runner／artifact newline-normalized SHA-256:
  `d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07` /
  `8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a`

Q011jの元box全体ではなく、同box内の一意なexact rootをcontraction inequalityで導出したboxに包み、
17 Fourier blockの全2598 spectrumを認証した。Q011c2 selected eigenvalue setはclusterの識別にだけ使い、
cluster内部の個別label不変性は要求していない。disc-union gapが正なのでhomotopy中のselected／external
交換はなく、全300 quadratic selected productも対応external sectorから分離する。

ただしQ011c2のcontinuous-amplitude continuation自体はrigorousになっておらず、quadratic distanceは
eigenvalue-levelである。nonnormal Sylvester／homological inverse norm、Q011e--Q011h raw-map coefficient、
forced SSM存在・一意性、nonlinear normal attraction、basinへ広げない。次は事前登録どおりQ011lで
repaired split上のrigorous interval homological inverse boundを構成する。

## Q011l: repaired split の rigorous invariant-graph / homological inverse certificate — 事前登録

### 問いと設計上の障害

Q011kが認証したeigenvalue-level external distanceを、exact repaired fixed pointにおける
quadratic homological operator全体の逆作用素境界へ持ち上げられるか。Q011dの数値oracleは
300 scalar-shift blockと5 sector Sylvester actionを通したが、binary64 Schur coordinate、
Q011b raw endpoint、probe residualに基づくため、exact repaired root上の非正規な逆作用素を
まだ認証していない。

全空間resolvent \(A_n-\lambda_i\lambda_j I\) への置換は採用しない。Q011k artifactを用いた
実装前監査では、300 pairのうち8 pairでproduct discがoutput sectorのselected discと重なり、
external spectrumだけからは分離している。この8 pairを除外して結論を作らず、selected invariant
subspaceをrigorousに囲んでexternal quotientを構成する。登録unsafe pair indexは
`11 / 19 / 33 / 43 / 56 / 64 / 76 / 86`とし、exact再計算で一致しなければvalidity failureとする。

### 封印入力

- Q011k artifact／runner newline-normalized SHA-256:
  `8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a` /
  `d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07`
- Q011k input／root／block／proof／result digest:
  `f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2` /
  `f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc` /
  `7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8` /
  `1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4` /
  `2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e`
- Q011d artifact／runner newline-normalized SHA-256:
  `c3acb9b7acc6e3121cb6e48a04bb060b5c95d7b128fe15fb11b67ee456337fd0` /
  `815fe7e0101cc05cc44fcb224534762f0ef7625f8c9604ff0a822c13171a617d`
- Q011d input／linear-split／pair-family／sector-probe／result digest:
  `ee2713e8169ea0f475ddee1b1233964ba40739d2276b78db3fff5410158dd2f8` /
  `7208875ff95f3a768e4b822cf9be854228d6664800dfc69218c0e6a030a0c63e` /
  `f9caee5b591e74b40b497ca7eb8244f1bbaeba71d239684c47d8215c46c2fb0b` /
  `feb864e2725e0cf726b43c443bb48b53f34ba0ac54693bb97a2b986f598a1414` /
  `a6941371e54a5e4d4abbea2f835196ddd7cce35c7c266ce399020764ed5b9dd7`

両artifactの全digest、runner、outcome、claim boundaryを再現する。Q011kの256-bit exact
fraction upper、binary64 eigenvalue center、selected center index、300 pair orderだけを証明入力とする。
Q011dはpair／sector dimension `102 / 54 / 54 / 45 / 45`、数値oracleとの対応、既存の否定されていない
prequalificationを照合するだけであり、そのbinary64 Schur basisをrigorous basisとして流用しない。

### exact eigencoordinate residual bound

Q011kの各必要block \(n\in\{0,1,2,15,16\}\) について、binary64 proposalをexact dyadic
\((\widehat\Lambda_n,V_n,W_n)\) と読む。Q011kが与えた

\[
\beta_n\ge\lVert V_n^{-1}\rVert_\infty,
\qquad
r_n\ge\lVert A_n(x_\ast)V_n-V_n\widehat\Lambda_n\rVert_\infty
\]

から

\[
M_n:=V_n^{-1}A_n(x_\ast)V_n
=\widehat\Lambda_n+F_n,
\qquad
\lVert F_n\rVert_\infty\le\theta_n:=\beta_n r_n
\]

をexact `Fraction`で導く。block `15 / 16`は`2 / 1`のconjugate transportを使う。
decimal値を再入力せず、artifactのbase-16 numerator／denominatorから全upperを復元する。

### selected invariant graph

selectedを持つblock \(n\in\{0,1,16\}\) では、Q011kのselected center indexで
\(M_n\)をselected／externalに分割する。対角center間について

\[
g_n=\min_{e\in E_n,s\in S_n}
\max\bigl(|\Re(\widehat\lambda_e-\widehat\lambda_s)|,
          |\Im(\widehat\lambda_e-\widehat\lambda_s)|\bigr)
\]

をexact dyadic lowerとして全列挙し、
\(h_n=\theta_n/g_n\)、登録graph radius \(r_n^G=2h_n\) とする。
外部行×selected列のmatrix infinity norm ball上でRiccati map

\[
\mathcal T_n(X)=-(\widehat\Lambda_{E,n}\,\cdot-
\cdot\,\widehat\Lambda_{S,n})^{-1}
\left(F_{ES}+F_{EE}X-XF_{SS}-XF_{SE}X\right)
\]

を使う。次の二不等式をexact rational arithmeticで要求する。

\[
h_n(1+2r_n^G+(r_n^G)^2)\le r_n^G,
\qquad
h_n(2+2r_n^G)<1.
\]

これにより一意なgraph \(X_n\)、
\(\lVert X_n\rVert_\infty\le r_n^G\) を得る。登録capは
`maximum graph radius <= 1e-4`、self-map utilization／contractionはそれぞれ`<=0.9`とする。
Q011kのeigenvalue countだけをprojector存在と読み替えず、このRiccati certificateを必須とする。

triangular change

\[
P_n=\begin{bmatrix}I&0\\X_n&I\end{bmatrix}
\]

によりexact selected dynamicsとexternal quotient dynamicsを

\[
S_n=M_{SS}+M_{SE}X_n,
\qquad
E_n=M_{EE}-X_nM_{SE}
\]

と定める。両者の対角centerからのずれを

\[
\eta_n=\theta_n(1+r_n^G)
\]

で包む。selectedを持たないsector `2 / 15`はfull blockをexternalとし、
\(\eta_n=\theta_n\) とする。

### symmetric-product action と5 sector Sylvester operator

selected global dynamicsはblock `0 / 1 / 16`のdirect sumとする。unscaled symmetric monomial
\(a_i a_j\;(i\le j)\) をQ011dと同じ順序で使い、sector pair countを
`0:102 / 1:54 / 16:54 / 2:45 / 15:45`とする。selected centerのcomplex modulusは
sqrtを使わず

\[
L=\max_s(|\Re\widehat\lambda_s|+|\Im\widehat\lambda_s|)
\]

で上から包み、
\(\eta_S=\max(\eta_0,\eta_1,\eta_{16})\) とする。exact symmetric-product action
\(K_q(S)\) とcenter product diagonal \(D_q\) の差に

\[
\lVert K_q(S)-D_q\rVert_\infty
\le\kappa:=2L\eta_S+\eta_S^2
\]

を用いる。このboundはsquare monomialのfactor `2`を含むunscaled basisに対して、各rowの
absolute sumを直接評価したものとする。scaled／orthonormal symmetric basisへ途中で変更しない。

各output sector \(q\in\{0,1,16,2,15\}\) で、全external centerと全対応pair product centerを列挙し、

\[
d_q=\min_{e,(i,j)\in q}
\max\bigl(|\Re(\widehat\lambda_e-\widehat\lambda_i\widehat\lambda_j)|,
          |\Im(\widehat\lambda_e-\widehat\lambda_i\widehat\lambda_j)|\bigr)
\]

をexact lowerとする。center productはstored decimalを掛け直さず、二つのbinary64 centerを
exact dyadic complex multiplicationして作る。full sector homological operator

\[
\mathcal H_q(Z)=E_qZ-ZK_q(S)
\]

について

\[
\Delta_q=\eta_q+\kappa,
\qquad
\nu_q=\Delta_q/d_q
\]

とし、`d_q >= 1e-5`、`nu_q <= 0.1`を全5 sectorに要求する。Neumann lemmaから

\[
\lVert\mathcal H_q^{-1}\rVert_{\infty\to\infty}
\le B_q:=\frac{1}{d_q-\Delta_q}
\]

を得る。ここでmatrix infinity normはexternal rowごとのpair-column absolute row sumであり、
`maximum B_q <= 1e5`を要求する。これは300 scalar diagonal blockだけでなく、selected dynamicsの
非対角couplingを含む5個のfull sector Sylvester operatorのboundである。

さらにambient fixed-leaf quotientへのlift／projectionを

\[
B_q^{\mathrm{amb}}
\le\lVert V_{E,q}\rVert_\infty(1+r_q^G)\beta_q B_q
\]

で包む。selectedを持たないsectorでは \(r_q^G=0\)。
\(\lVert V_{E,q}\rVert_\infty\le\lVert V_q\rVert_\infty\) を使い、
`maximum ambient lifted inverse bound <= 1e7`を要求する。これは登録eigencoordinate quotient normと
ambient fixed-leaf infinity normの橋であり、Euclidean minimum singular valueと同一視しない。

### validity gate

1. Q011k／Q011d artifact、runner、全登録digest、outcome、claim boundaryを再現する。
2. Q011k exact fraction records、center index、conjugate transport、block／pair／sector countをexactに復元する。
3. full-space substitution監査を全300 pairで完了し、unsafe pair count／indexが登録した8件と一致する。
4. \(\theta_n=\beta_nr_n\)、center gap、Riccati self-map／contractionをexact `Fraction`で全列挙する。
5. 24 selected center、300 unordered pair、44,010 external comparison、5 sector pair countを欠落なく再構成する。
6. \(L,\eta_S,\kappa,d_q,\Delta_q,\nu_q,B_q,B_q^{\mathrm{amb}}\) をexact rational formulaだけで計算する。
7. finite strict JSON、input／graph／pair／homological／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、inverse certificateを解釈しない。

### homological-inverse hypothesis gate と停止規則

validity通過後、次の5項目を全て要求する。

1. block `0 / 1 / 16`のgraph radiusが`<=1e-4`、self-map utilization／contractionが各`<=0.9`である。
2. 全graph gapと全5 sector base homological distanceがstrict positiveで、後者は`>=1e-5`である。
3. 全5 sectorでNeumann quotient `nu_q <= 0.1`である。
4. full sector coordinate inverse boundの最大が`<=1e5`である。
5. ambient lifted inverse boundの最大が`<=1e7`である。

全項目が通れば
`the exact repaired selected/external split has a rigorously bounded quadratic homological inverse in the registered quotient norm`
として`accepted`とする。validityは通るが一項目でも落ちれば
`the registered invariant-graph and Neumann bounds do not certify the repaired quadratic homological inverse`
として`rejected`とする。これは実operatorのsingularityを意味しない。最初に落ちたblock／sector／pair witness、
graph gap、Neumann marginを記録する。結果後にcenter ordering、pair basis、graph radius formula、
`1e-4 / 0.9 / 1e-5 / 0.1 / 1e5 / 1e7` thresholdを変更しない。

acceptedの場合だけ、次のQ011mでrepaired exact mapのquadratic jetをinterval／analyticに構成し、
このinverse boundと合成したcoefficient／residual majorantを事前登録する。rejectedなら対角center Neumann
majorantを個別block inverse／verified Schur-Sylvester solveへ鋭化する。inconclusiveなら最初のprotocol
failureだけを修復する。

### 主張境界

本gateは固定17²、固定振幅、periodic repaired exact map、その一意なx-independent fixed point、
Q011k-designated selected cluster、quadratic order、登録eigencoordinate quotient normに限る。
Q011c2 continuous-amplitude path、cluster内部の個別branch continuity、raw Q011b map、Q011d／Q011e--Q011h
raw coefficientの移植、quadratic jet／coefficient自体、higher-order nonresonance、SSM存在・一意性・滑らかさ、
nonlinear normal attraction、basin、他grid／force／wall、D3Q27は主張しない。inverse boundをSSM theoremや
normal attractionへ読み替えない。

### Q011l 実行結果

validity `7 / 7`、hypothesis `5 / 5`を通過し、
`the exact repaired selected/external split has a rigorously bounded quadratic homological inverse in the registered quotient norm`
として`accepted`とした。

Q011kのexact dyadic centerと256-bit outward upperから

\[
\theta_n=\beta_n r_n\ge
\lVert V_n^{-1}(A_n(x_\ast)V_n-V_n\widehat\Lambda_n)\rVert_\infty
\]

を構成した。block `0 / 1 / 16`ではRiccati mapが登録graph ballをstrict self-map／contractionとし、
selected invariant graphをexact root上で認証した。graphでblock triangularizeしたselected dynamicsと
external quotientを使い、unscaled 300-dimensional symmetric-product actionの非対角perturbationも含めて
5 sectorのfull Sylvester operatorをNeumann lemmaで認証した。

- full-space substitution unsafe pair count／indices:
  `8 / [11, 19, 33, 43, 56, 64, 76, 86]`
- selected block graph dimensions:
  `0: 144 x 6 / 1: 144 x 9 / 16: 144 x 9`
- minimum graph diagonal component gap:
  `0.023905378580609926`
- maximum graph radius／self-map utilization／contraction upper:
  `1.6628540517032178e-6 / 0.5000016628554342 / 1.662856816786815e-6`
- minimum graph split-identification margin lower:
  `0.02390537645745014`
- selected center complex-l1／selected dynamics perturbation upper:
  `1.230405331961541 / 2.029994575335569e-8`
- symmetric-product action perturbation upper:
  `4.9954323399005556e-8`
- sector pair dimensions:
  `0:102 / 1:54 / 16:54 / 2:45 / 15:45`
- unordered pair／external comparison count:
  `300 / 44010`
- minimum base homological distance／witness:
  `0.00019318395012417515 / sector 0, pair 173, external center 143`
- maximum Neumann quotient／sector:
  `0.0003636651445795734 / 0`
- maximum quotient-coordinate inverse bound／sector:
  `5178.2966276547 / 0`
- maximum ambient-output lifted inverse bound／sector:
  `3325900.503434659 / 0`
- exact base-pair／reproduced Q011k pair／sector digest:
  `e6068c78d608d765d77dcfdaa0efb0f15a24d941c45c2859e51482d4c70d83bf` /
  `be8548cd8ac4bea69b71b7bb0617f232ddcc9535d33b13279e371cc242cf2b79` /
  `6cfb130f45822becdca29ae6841e7c4069b03c670781501f94a59c0d2a5b2fc3`
- input／graph／pair／homological／result digest:
  `1810f989a0328521e8b6d6ccbc2153cb9a945bb2c129c70d7b25a0c227fc7011` /
  `a7d0f320fa7391c506f42853a94ede66fc73e81b004dfccda144028082cb8db3` /
  `694cc2955bcef05df13ad30582f46f84bb627aaa7b336b5278e9b5139e29d377` /
  `14d67f1d915aa3bd6bc34117562da4908e19036943e60fb638eddf6a42b20915` /
  `c372aa5962a7f3d0c83a126303a9e36e4f0830d113f9c49b922d03beb2f09a45`
- runner／artifact newline-normalized SHA-256:
  `59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7` /
  `2878d8ebaaedc29990700ccac25b78185e0b6139dd371521f14602caf4514c0a`

8 pairはselected output discと重なるため、全空間resolventへ置き換えると証明できない。しかし一件も
除外せず、rigorous selected graphのexternal quotient上では全5 full sector operatorがinvertibleである。
従ってQ011kのeigenvalue-level distanceを非正規coupling込みのquadratic homological inverseへ持ち上げた。

ただしQ011e--Q011hのraw-map Hessian／coefficientはrepaired mapへ移植しておらず、本gateはquadratic jet、
coefficient bound、残差majorant、higher order、SSM存在・一意性、normal attractionを認証しない。
次は停止規則どおりQ011mでrepaired exact mapのquadratic jetと、このinverse boundに合成する
coefficient／residual majorantを観測前に事前登録する。

## Q011m: repaired exact quadratic jet and cubic-defect majorant — 事前登録

### 問いと証明対象

Q011lで認証したexact selected invariant graphと5 sector homological inverseに、repaired exact map自身の
二階微分を合成し、graph-gauge quadratic jetの一意な存在と係数normを認証できるか。さらに三階微分の
domain majorantを用い、その二次多項式chartの不変性欠陥を全方向一様な \(O(\lVert a\rVert_\infty^3)\)
で包めるか。

本gateでいう「quadratic jetの構成」は、componentwise binary64 coefficientを保存することではない。
Q011lのexact invariant subspace／quotient上でhomological equationの一意解を定義し、そのexact解を
registered norm ballへ包むcomputer-assisted existence certificateである。Q011e--Q011hのraw-map
Hessian／coefficientは入力に使わない。

### 封印入力

- Q011j artifact／runner newline-normalized SHA-256:
  `74a2e084137699739c14d980b05676e14e6802b4018b3893d3d05270850c2c5a` /
  `23a7a3a272264be3eb5330b2456192bd797aa968c4f795e2cbe8e337fc8fe4b5`
- Q011j input／coordinate／oracle／proof／result digest:
  `a183f4830c757b58122132cf64111fd5375636affdb6c0b31e1cd90e89085799` /
  `adaef353b8b64509334794c6014dc8b88e81ca2b776c3b65bd4d50911ae9452b` /
  `177468a48f667ddd922ed4b979d3e7e5d4cc0ed3afffe27a34651060da8e0f5f` /
  `1080fcea24358422514bba7fb9881928269c853cb4d12b0282e63840c56124c0` /
  `ddad5beca9693eeab726382ac864d01a27b749d579c2ec8f12dd9f8c499db934`
- Q011k artifact／runner newline-normalized SHA-256:
  `8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a` /
  `d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07`
- Q011k input／root／block／proof／result digest:
  `f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2` /
  `f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc` /
  `7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8` /
  `1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4` /
  `2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e`
- Q011l artifact／runner newline-normalized SHA-256:
  `2878d8ebaaedc29990700ccac25b78185e0b6139dd371521f14602caf4514c0a` /
  `59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7`
- Q011l input／graph／pair／homological／result digest:
  `1810f989a0328521e8b6d6ccbc2153cb9a945bb2c129c70d7b25a0c227fc7011` /
  `a7d0f320fa7391c506f42853a94ede66fc73e81b004dfccda144028082cb8db3` /
  `694cc2955bcef05df13ad30582f46f84bb627aaa7b336b5278e9b5139e29d377` /
  `14d67f1d915aa3bd6bc34117562da4908e19036943e60fb638eddf6a42b20915` /
  `c372aa5962a7f3d0c83a126303a9e36e4f0830d113f9c49b922d03beb2f09a45`

三artifactのhash、runner、全digest、accepted outcome、claim boundaryを再現する。Q011jからexact affine
center／liftを、Q011kからcontraction-derived root boxとdyadic eigencoordinate normを、Q011lからgraph、
selected dynamics、5 inverse boundを読む。Q011e--Q011hは照合にも使わず、非移植を明示する。

### normとFourier規約

x-Fourier係数は

\[
\widehat f_n(y,q)=\frac1{17}\sum_{x=0}^{16}f(y,x,q)e^{-2\pi i nx/17},
\qquad
f(y,x,q)=\sum_{n=0}^{16}\widehat f_n(y,q)e^{2\pi i nx/17}
\]

とする。selected reduced coordinateはblock `0 / 1 / 16`の24 complex coordinateで、conjugacy-real sliceへ
制限する。reduced normは24成分のcomplex \(\ell^\infty\)、population normはfull 17² stateのcomplex
component \(\ell^\infty\) とする。quadratic coordinateはQ011lと同じunscaled lexicographic monomial

\[
m(a)=(a_i a_j)_{0\le i\le j<24}
\]

とする。coefficient matrix normはmaximum population／coordinate row sum over 300 pair columnsである。

zero-wave fixed-leaf coordinateをpopulationへ戻すlift norm `186`を必ず含める。block `1 / 16`は153
population coordinateのままである。Fourier inverseのtriangle inequalityを使い、異なるsector間のcancelは
majorantに利用しない。

### 事前登録する単純有理envelope

Q011j--Q011lの巨大denominatorを後段formulaへ直接増殖させず、まず次の単純 `Fraction` envelopeに含める。
各包含はexact recordとの比較で検証し、一つでも外れればvalidity failureとする。

- exact-root population component radius: `<= 3e-13`
- root population／density floor: `>= 0.027 / 0.999`
- center local momentum component absolute upper: `<= 3e-5`
- eigencolumn infinity norm upper: block `0 <= 13`、block `1 / 16 <= 16`
- graph radius upper: block `0 <= 2e-6`、block `1 / 16 <= 1e-7`
- selected inverse-coordinate norm upper: block `0 <= 53`、block `1 / 16 <= 25`
- ambient-output homological inverse upper:
  sector `0 <= 3.4e6`、`1 / 16 <= 2.4e4`、`2 / 15 <= 2.3e6`
- selected linear dynamics infinity norm upper: `<= 1.24`

後段証明はartifactの観測floatではなく、これらの外側envelopeだけを使う。

### repaired exact mapの二階・三階微分

sourceはstate-independentであるため全二階以上の微分は0である。streamingと5-point filterも線形で、
population \(\ell^\infty\) operator normはそれぞれ1以下である。非線形性はlocal equilibrium

\[
f_q^{eq}=w_q\left[\rho+3c_q\cdot j+
\frac{Q_q(j)}{\rho}\right],
\qquad
Q_q(j)=\frac92(c_q\cdot j)^2-\frac32|j|^2
\]

だけから来る。moment coordinate \(z=(\rho,j_x,j_y)\) に対し、二階微分を

\[
\partial_{\rho\rho}f_q^{eq}=\frac{2w_qQ_q}{\rho^3},
\quad
\partial_{\rho j}f_q^{eq}=-\frac{w_q\nabla Q_q}{\rho^2},
\quad
\partial_{jj}f_q^{eq}=\frac{w_q\nabla^2Q_q}{\rho}
\]

とし、三階微分を

\[
\partial_{\rho\rho\rho}f_q^{eq}=-\frac{6w_qQ_q}{\rho^4},
\quad
\partial_{\rho\rho j}f_q^{eq}=\frac{2w_q\nabla Q_q}{\rho^3},
\quad
\partial_{\rho jj}f_q^{eq}=-\frac{w_q\nabla^2Q_q}{\rho^2},
\quad
\partial_{jjj}f_q^{eq}=0
\]

とする。符号はabsolute majorantでは消えるが、symmetry／conservation auditでは保持する。
population perturbation1成分あたりのmoment row-sumを`(9,6,6)`とし、全site／population／tensor indexを
exact rationalで列挙する。BGK factor `omega=3/2`を掛ける。登録state displacement domain
`U <= 1e-4`上で

\[
\lVert D^2\Phi\rVert_{\infty,\mathrm{bil}}\le145,
\qquad
\lVert D^3\Phi\rVert_{\infty,\mathrm{tri}}\le4000
\]

を要求する。D2Q9 quadratureとequilibrium moment identityから二階・三階forcingのglobal conserved
momentsがexact zeroであることも検証する。

### quadratic jetの存在と係数bound

Q011lのexact selected tangent／dynamicsを \(T,S\)、graph-gauge external quadratic coefficientを \(Z\)、
selected reduced coefficientを \(P\) とし、

\[
W^{[2]}(a)=x_\ast+Ta+Zm(a),
\qquad
R^{[2]}(a)=Sa+Pm(a)
\]

と定める。zero-wave liftを含むtangent boundを

\[
K_T=186\cdot13(1+2\times10^{-6})
    +2\cdot16(1+10^{-7})
\]

とする。quadratic forcing coefficient row-sumは

\[
K_F=\frac12\cdot145\,K_T^2
\]

で包む。factor `1/2`はunscaled symmetric monomialでdiagonal pairを半分にする規約を含む。

Q011lの5 ambient-output inverse envelopeを使い、population chart coefficientを

\[
K_Z=K_F\left(186\cdot3.4\times10^6
 +2\cdot2.4\times10^4+2\cdot2.3\times10^6\right)
\]

で包む。zero sectorだけpopulation lift `186`をもう一度掛ける。selected projectionから

\[
K_P=53K_F,
\qquad
K_S=1.24
\]

とする。全300 pairとsector count `102 / 54 / 54 / 45 / 45`を維持し、Q011l invertibilityから
graph-gauge \(Z\) の一意性を得る。登録capは

\[
K_T\le2500,
\quad K_F\le5\times10^8,
\quad K_Z\le3\times10^{17},
\quad K_P\le3\times10^{10}.
\]

### cubic-defect majorantとradius campaign

\(r=\lVert a\rVert_\infty\) に対して

\[
U(r)=K_Tr+K_Zr^2,
\qquad
A_R(r)=K_Sr+K_Pr^2
\]

とする。二次homological equationでdegree 2までをexactに消去した後の不変性欠陥を

\[
\begin{aligned}
D(r)={}&145K_TK_Zr^3+\frac{145}{2}K_Z^2r^4\\
&+2K_ZK_SK_Pr^3+K_ZK_P^2r^4\\
&+\frac{4000}{6}U(r)^3
\end{aligned}
\]

で包む。第1行はHessianへのlinear／quadratic chart cross term、第2行は
\(m(Sa+Pm(a))-m(Sa)\)、第3行はmapのthird-derivative Taylor remainderである。
全係数がnonnegativeなので \(D(t)/t^3\le D(r)/r^3\) for `0 < t <= r`もexactに検証する。

radius candidatesは昇順に

`[1e-14, 3e-14, 1e-13, 3e-13, 1e-12, 3e-12, 1e-11, 3e-11]`

と固定する。各radiusで次を評価する。

1. `U(r) <= 1e-4`。
2. root floorから `population >= 0.02`、`density >= 0.99`。
3. `A_R(r) / r <= 2`。
4. `D(r) <= 2e-5`。
5. `D(r) / U(r) <= 0.75`。

全5条件を通る最大radiusを選ぶ。少なくとも`1e-11`が通ることをhypothesis gateとする。
larger candidateのfailは棄却ではなく、first failed constraintを記録する。candidate、envelope、thresholdは
結果後に変更しない。

### validity gate

1. Q011j／Q011k／Q011l artifact、runner、全digest、accepted outcome、claim boundaryを再現する。
2. exact affine center、root enclosure、simple rational envelopeの全包含を再現する。
3. Fourier規約、zero-wave lift `186`、selected／pair／sector countを再現する。
4. local equilibriumの二階／三階tensor、mixed-partial symmetry、quadrature／conservation identityをexactに列挙する。
5. \(K_T,K_F,K_Z,K_P,K_S\) とgraph-gauge quadratic homological solutionの存在／一意性を登録式から導く。
6. 全8 radius recordと \(U,A_R,D,D/r^3\) をexact `Fraction`で計算する。
7. finite strict JSON、input／derivative／coefficient／majorant／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、quadratic jet／majorantを解釈しない。

### quadratic-jet / cubic-defect hypothesis gate と停止規則

validity通過後、次の5項目を全て要求する。

1. derivative domainでHessian／third derivative norm upperが`<=145 / 4000`である。
2. coefficient boundsが`K_T <=2500`、`K_F <=5e8`、`K_Z <=3e17`、`K_P <=3e10`である。
3. Q011l inverseにより全5 sectorのgraph-gauge quadratic solutionが一意に存在する。
4. passing radiusが存在し、最大passing radiusが`>=1e-11`である。
5. selected radiusでpopulation／density／reduced expansion／residual／utilizationの全capが通り、
   \(D(t)\le[D(r)/r^3]t^3\) が`0 <= t <= r`で成立する。

全項目が通れば
`the repaired exact map admits a unique graph-gauge quadratic jet with the registered coefficient and cubic-defect majorants`
として`accepted`とする。validityは通るが一項目でも落ちれば
`the registered derivative and coefficient envelopes do not certify the repaired quadratic jet majorant`
として`rejected`とする。これはquadratic jetやSSMの不存在を意味しない。最初に落ちたderivative tensor、
sector、coefficient、radius constraintを記録する。

acceptedの場合だけ、次のQ011nでこのfinite second-order defectとQ011l inverseを使うa posteriori
radii-polynomial／graph-transform correctionを事前登録する。rejectedならcomponentwise verified forcing／
coefficient enclosureでscalar majorantを鋭化する。inconclusiveなら最初のprotocol failureだけを修復する。

### 主張境界

本gateは固定17²、固定振幅、periodic repaired exact map、その一意なx-independent fixed point、
Q011k／Q011l selected invariant graph、quadratic graph-gauge jet、登録normと有限radius majorantに限る。
componentwise coefficient array、raw Q011b map、Q011e--Q011h coefficientの移植、Q011c2 continuous-amplitude
path、higher-order jet、exact invariant manifold／SSMの存在・一意性・滑らかさ、nonlinear normal attraction、
basin、他grid／force／wall、D3Q27は主張しない。finite cubic defectをexact invarianceへ読み替えない。

### Q011m 実行結果

validity `7 / 7`、hypothesis `5 / 5`を通過し、
`the repaired exact map admits a unique graph-gauge quadratic jet with the registered coefficient and cubic-defect majorants`
として`accepted`とした。

exact root enclosureは全simple envelopeに入り、登録domain上のanalytic derivative boundは

\[
\lVert D^2\Phi\rVert_{\infty,\mathrm{bil}}
\le144.5474473239429<145,
\qquad
\lVert D^3\Phi\rVert_{\infty,\mathrm{tri}}
\le3910.210477654001<4000
\]

となった。mixed-partial symmetry、D2Q9 equilibrium moment identity、二階／三階forcingのglobal conserved
component zeroもexactに通過した。

単純envelopeだけから得た係数boundは

- `K_T = 2450.0048392`
- `K_F = 435182969.1274978`
- `K_Z = 2.772324401167342e17`
- `K_P = 23064697363.75738`
- `K_S = 1.24`

で、全登録cap内にある。Q011lの5 sector invertibilityによりgraph-gauge quadratic solutionは一意である。

8 radius中7件が通り、最大passing radiusは`1e-11`だった。このradiusで

- `U = 2.7747744060065423e-5`
- `population lower = 0.026972252255939935`
- `density lower = 0.9987502703034594`
- `A_R/r = 1.4706469736375738`
- `D = 1.738847670176358e-5`
- `D/U = 0.6266627176653649`

である。次の`3e-11`は`U <= 1e-4`、`D <= 2e-5`、`D/U <= 0.75`の3条件でfailした。
これはQ011mの棄却ではなく、登録majorantが閉じる最大candidateの局在である。

- exact tensor／radius-record digest:
  `f77acf8cff113b906284b077841284de307649e1afc04019b6de7147d0670b08` /
  `dd14364d4c60d8c47bf593538a414178db440a6a25e226088a69332188618f52`
- input／derivative／coefficient／majorant／result digest:
  `dd30ead5c7c6081502bc34a6163ce64321dd4f9a339c7f24959dfc76891591cb` /
  `0b8f345fdf2bda5b95f2c1624920968f1ad499f4d5e765c0b8305e2045ac7e3a` /
  `1d708042f97c8c42164b07ff7104a68bdef95c14faf90dcb0171749d92b8a514` /
  `bf7144f407dd3e6aabf2161bf3d8c48dbb2e6c89a48cde9cfccf1cff60455e00` /
  `f47a1a4c1712fcff129c3840d7e64dfe1bbbe4bdacc049e28be6f868dbfc9cd4`
- runner／artifact newline-normalized SHA-256:
  `0cdc6ec9697d25bea3b28cf90f01f3f639062b3c04a64c4a88e6bd7221163150` /
  `b76b0ec1a1436aa3c2b48fcc29485e60e03675bf9a1f4f85ac3106d30687da3f`

componentwise coefficient array、raw-map係数移植、exact invariant manifold／SSM、smoothness、normal
attraction、basinは認証していない。停止規則どおり、次はQ011nを観測前に事前登録する。

## Q011n: a posteriori correction readiness and scalar obstruction — 事前登録

### 問い

Q011lのquadratic homological inverseとQ011mのfinite cubic defectだけで、repaired exact mapのexact local
invariant manifoldをa posterioriに認証できるか。認証できない場合、単なる「定理未選定」ではなく、
operator domainの不一致と、登録scalar majorantが最初に破る十分条件をexactに局在できるか。

本gateはQ011mのfinite defectをexact invarianceへ読み替える前のtheorem-readiness gateである。
Q011l inverseを次数3以上の関数へ無断で作用させない。scalar productが小さくてもtyped inverseがなければ
存在証明とはせず、逆にscalar productが大きくてもmanifoldの不存在とは解釈しない。

### 封印入力

- Q011k artifact／runner newline-normalized SHA-256:
  `8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a` /
  `d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07`
- Q011k input／root／block／proof／result digest:
  `f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2` /
  `f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc` /
  `7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8` /
  `1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4` /
  `2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e`
- Q011l artifact／runner newline-normalized SHA-256:
  `2878d8ebaaedc29990700ccac25b78185e0b6139dd371521f14602caf4514c0a` /
  `59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7`
- Q011l input／graph／pair／homological／result digest:
  `1810f989a0328521e8b6d6ccbc2153cb9a945bb2c129c70d7b25a0c227fc7011` /
  `a7d0f320fa7391c506f42853a94ede66fc73e81b004dfccda144028082cb8db3` /
  `694cc2955bcef05df13ad30582f46f84bb627aaa7b336b5278e9b5139e29d377` /
  `14d67f1d915aa3bd6bc34117562da4908e19036943e60fb638eddf6a42b20915` /
  `c372aa5962a7f3d0c83a126303a9e36e4f0830d113f9c49b922d03beb2f09a45`
- Q011m artifact／runner newline-normalized SHA-256:
  `b76b0ec1a1436aa3c2b48fcc29485e60e03675bf9a1f4f85ac3106d30687da3f` /
  `0cdc6ec9697d25bea3b28cf90f01f3f639062b3c04a64c4a88e6bd7221163150`
- Q011m input／derivative／coefficient／majorant／result digest:
  `dd30ead5c7c6081502bc34a6163ce64321dd4f9a339c7f24959dfc76891591cb` /
  `0b8f345fdf2bda5b95f2c1624920968f1ad499f4d5e765c0b8305e2045ac7e3a` /
  `1d708042f97c8c42164b07ff7104a68bdef95c14faf90dcb0171749d92b8a514` /
  `bf7144f407dd3e6aabf2161bf3d8c48dbb2e6c89a48cde9cfccf1cff60455e00` /
  `f47a1a4c1712fcff129c3840d7e64dfe1bbbe4bdacc049e28be6f868dbfc9cd4`

三artifactのhash、runner、全digest、accepted outcome、theorem consequence、claim boundaryを再現する。
Q011mがQ011j--Q011lを既に封印している事実も照合するが、nested sealだけで直接hash照合を省略しない。

### operator type audit

Q011lが認証したoperatorは各output sector \(q\) に対する

\[
\mathcal H_q^{(2)}:
\mathbb C^{d_q^{ext}\times m_q^{(2)}}
\longrightarrow
\mathbb C^{d_q^{ext}\times m_q^{(2)}},
\qquad
m_q^{(2)}\in\{102,54,54,45,45\}
\]

であり、全体でもdegree-2の300 monomial columnに限る。Q011m defectは

\[
\mathcal E^{[2]}(a)=
\Phi(W^{[2]}(a))-W^{[2]}(R^{[2]}(a)),
\qquad
\lVert\mathcal E^{[2]}(a)\rVert_\infty\le D(r)
\]

というdegree 3以上を含む関数である。従って

\[
(\mathcal H^{(2)})^{-1}\mathcal E^{[2]}
\]

は現状では型が合わず、定義しない。a posteriori theoremに必要なのは、例えば次のどちらかである。

1. 固定したanalytic／coefficient Banach space上のfull linearized invariance operator inverseとtail bound。
2. selected／external graph space、cutoff／localization、base inverse、operator-norm normal dominanceを含む
   self-contained graph transform contraction。

Q011kのeigenvalue modulus gap、Q011lのdegree-2 inverse、Q011mのphysical defectを、これらの代用品として
混同しない。利用可能／不足のproof objectを明示的なboolean matrixとして保存する。

### 登録scalar surrogate

typed theoremが未完成でも、現在のscalar envelopeがどの程度粗いかを局在するため、Q011mと同じ
cross-sector cancellationなしのtotal inverse envelope

\[
C_I=186(3.4\times10^6)+2(2.4\times10^4)+2(2.3\times10^6)
=637048000
\]

を固定する。これはfull function-space inverseではなく、5個のdegree-2 output boundをtriangle inequalityで
合計したsurrogateである。

Q011mの8 radius recordを変更せず、各 \(r\) のexact \(U(r),D(r)\) から

\[
V(r)=145U(r)+2000U(r)^2,
\qquad
Y(r)=C_ID(r),
\qquad
Z(r)=C_IV(r),
\qquad
\tau(r)=2Y(r)
\]

をexact `Fraction`で評価する。`2000 = 4000/2`はderivative variationの二次Taylor envelopeである。
これはformal Newton scalar prequalificationにすぎず、\(C_I\)をfull inverseと呼ばない。

各candidateのscalar passを次の全条件で定義する。

1. Q011mでそのradiusがoriginal domain／positivity／defect gateを通っている。
2. \(Z(r)<1/2\)。
3. \(Y(r)+Z(r)\tau(r)<\tau(r)\)。
4. \(U(r)+\tau(r)\le10^{-4}\)。
5. \(0.027-U(r)-\tau(r)\ge0.02\) かつ
   \(0.999-9[U(r)+\tau(r)]\ge0.99\)。
6. \(\tau(r)\le U(r)\)。

最大passing candidateだけを選ぶ。passing candidateがなくてもthresholdやradius gridを変更しない。
最初のcandidate、最小 \(Z\)、最小correction utilization、各constraintのfailure countを保存する。

### validity gate

1. Q011k／Q011l／Q011m artifact、runner、15 digest、accepted outcome、claim boundaryを再現する。
2. Q011l degree-2 operatorとQ011m function defectのdomain／codomainを別々に記録する。
3. 5 sector countと \(C_I=637048000\) を登録式からexactに再現する。
4. Q011mの8 radius record、順序、selected radius、exact radius digestを変更なく再現する。
5. 全candidateの \(V,Y,Z,\tau\) と6 scalar conditionをexact `Fraction`で計算する。
6. scalar surrogateのpass／failをexact-manifold theoremのpass／failへ読み替えていないことを記録する。
7. finite strict JSON、input／typing／scalar／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、theorem readinessもscalar obstructionも解釈しない。

### a posteriori readiness hypothesis gate と停止規則

validity通過後、次の5項目を別々に要求する。

1. 適用するa posteriori theorem、Banach space、norm、domain、gaugeが固定されている。
2. full linearized invariance inverse＋tail、またはself-contained graph-transform contractionがrigorousにある。
3. 少なくとも一つの登録radiusが上の6 scalar conditionを全て通る。
4. 同じradiusでchart range、density、population、correction ballのstrict bufferがある。
5. defect、derivative variation、roundoff／exact arithmeticを採用定理の各hypothesisへ型付きで対応できる。

全5項目が通る場合だけ
`the registered repaired quadratic chart is ready for an a posteriori invariant-manifold proof`
として`ready`とする。一つでも落ちれば
`the registered Q011l/Q011m certificates are not sufficient for an a posteriori invariant-manifold proof`
として有効な`not_ready`とする。これはexact invariant manifold／SSMの不存在、Q011l／Q011mの棄却、
または別norm・別majorantでの証明不能を意味しない。

`not_ready`の場合は最初のmissing proof objectと、scalar側の最初のfailed constraintを保存する。
operator typeが未解決なら、scalar boundだけを鋭化する前に、次のQ011oでfixed split上のgraph-transform
Banach space、coordinate lift／inverse、linear conorm／external norm、cutoff／localizationを事前登録する。
typed theorem objectが揃ってscalarだけ落ちる場合に限り、componentwise forcing／inverse boundを鋭化する。

### 主張境界

本gateは固定17² repaired exact map、Q011k split、Q011l degree-2 inverse、Q011m quadratic chart／finite defectの
theorem-readiness auditに限る。新しいcoefficient、higher-degree inverse、full analytic tail、graph transform、
exact invariant manifold／SSM、smoothness、normal attraction、basin、他grid／force／wall、D3Q27を構成・
認証しない。scalar surrogateは存在定理でも非存在定理でもない。

### Q011n 実行結果

validity `7 / 7`はすべて通過した。Q011l operatorのdomainは5個のexternal-by-degree-2-monomial matrix
space、Q011m defectのdomainは24-coordinate ball、codomainはfull repaired fixed-leaf population stateであり、
`(H^(2))^(-1) E^[2] is undefined`を再現した。最初のmissing proof objectは
`specified_a_posteriori_theorem`だった。

readiness hypothesisは`0 / 5`で、結果は`not_ready`である。Q011mと同じ8 radiusではscalar passing
candidateも`0 / 8`だった。最小radius `1e-14`で既に

- `U = 5.222329240367342e-11`
- `D = 1.5859449210967877e-14`
- `Y = 1.0103230400948665e-5`
- `Z = 4.823967880455232`
- `tau = 2.020646080189733e-5`
- `tau / U = 386924.2989451196`

となり、`Z < 1/2`、strict radii inequality、`tau <= U`がfailした。従って分類は
`the registered Q011l/Q011m certificates are not sufficient for an a posteriori invariant-manifold proof`
である。これはexact manifold／SSMの不存在ではなく、Q011l／Q011mのaccepted outcomeも変更しない。

- input／typing／scalar／result digest:
  `f916b59d1c9fba0e4ace57b110f4b960d5dce078578a77ac28f8a8d005e1e0d0` /
  `e3952e5ac897ba9250f3a77ec5d8760c0f3ee2a3df350ba4451837a46dd91f76` /
  `ee7f21a6075963c510e234a032aa8de40f65989c609d10228aca54f6e371ed8d` /
  `9893aed4a7ce4d05cbd21e849de4ddd4f1c9f86c7fcc3fad7a4504b823d6a321`
- runner／artifact newline-normalized SHA-256:
  `7e526dcf013efce628137023f69de7b929d31e52f19378cb05c483284e36dc57` /
  `1277170b85d2f515a5b9dabbc1cf23cfdf36e109c5ab212e3a123ee07a50683b`

停止規則どおり、次はQ011oでtype-correct graph-transform setupを観測前に事前登録する。scalar forcing／
inverse envelopeの鋭化は、Banach spaceとoperator mappingを固定した後に行う。

## Q011o: type-correct localized graph-transform setup — 事前登録

### 問い

Q011kのrepaired fixed-leaf spectral splitとQ011lのselected invariant graphを、一つの明示的な
Banach coordinate normへ持ち上げ、selected base inverse、external linear norm、coordinate lift／inverse、
およびlocal nonlinear mapを扱うcutoffを同じ型で定義できるか。そのnormでlinear normal domination

\[
q_E<m_S
\]

をrigorousに閉じられるか。

本gateはQ011nで不足したproof objectのうち、graph-transformの**空間・座標・線形部・局所化**だけを
構成する。nonlinear graph transformのself-map、base-map inverse、contraction、fixed graphは次の独立gateへ
残す。従ってlinear setupが通ってもexact invariant manifold／SSMの存在とは呼ばない。

### 封印入力

- Q011k artifact／runner newline-normalized SHA-256:
  `8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a` /
  `d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07`
- Q011k input／root／block／proof／result digest:
  `f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2` /
  `f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc` /
  `7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8` /
  `1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4` /
  `2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e`
- Q011l artifact／runner newline-normalized SHA-256:
  `2878d8ebaaedc29990700ccac25b78185e0b6139dd371521f14602caf4514c0a` /
  `59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7`
- Q011l input／graph／pair／homological／result digest:
  `1810f989a0328521e8b6d6ccbc2153cb9a945bb2c129c70d7b25a0c227fc7011` /
  `a7d0f320fa7391c506f42853a94ede66fc73e81b004dfccda144028082cb8db3` /
  `694cc2955bcef05df13ad30582f46f84bb627aaa7b336b5278e9b5139e29d377` /
  `14d67f1d915aa3bd6bc34117562da4908e19036943e60fb638eddf6a42b20915` /
  `c372aa5962a7f3d0c83a126303a9e36e4f0830d113f9c49b922d03beb2f09a45`
- Q011m artifact／runner newline-normalized SHA-256:
  `b76b0ec1a1436aa3c2b48fcc29485e60e03675bf9a1f4f85ac3106d30687da3f` /
  `0cdc6ec9697d25bea3b28cf90f01f3f639062b3c04a64c4a88e6bd7221163150`
- Q011m input／derivative／coefficient／majorant／result digest:
  `dd30ead5c7c6081502bc34a6163ce64321dd4f9a339c7f24959dfc76891591cb` /
  `0b8f345fdf2bda5b95f2c1624920968f1ad499f4d5e765c0b8305e2045ac7e3a` /
  `1d708042f97c8c42164b07ff7104a68bdef95c14faf90dcb0171749d92b8a514` /
  `bf7144f407dd3e6aabf2161bf3d8c48dbb2e6c89a48cde9cfccf1cff60455e00` /
  `f47a1a4c1712fcff129c3840d7e64dfe1bbbe4bdacc049e28be6f868dbfc9cd4`
- Q011n artifact／runner newline-normalized SHA-256:
  `1277170b85d2f515a5b9dabbc1cf23cfdf36e109c5ab212e3a123ee07a50683b` /
  `7e526dcf013efce628137023f69de7b929d31e52f19378cb05c483284e36dc57`
- Q011n input／typing／scalar／result digest:
  `f916b59d1c9fba0e4ace57b110f4b960d5dce078578a77ac28f8a8d005e1e0d0` /
  `e3952e5ac897ba9250f3a77ec5d8760c0f3ee2a3df350ba4451837a46dd91f76` /
  `ee7f21a6075963c510e234a032aa8de40f65989c609d10228aca54f6e371ed8d` /
  `9893aed4a7ce4d05cbd21e849de4ddd4f1c9f86c7fcc3fad7a4504b823d6a321`

Q011k--Q011mの`accepted`、Q011nのvalid `not_ready`、全19 digest、runner／artifact hash、
theorem consequence、claim boundaryを直接再現する。Q011nのnested sealだけで直接照合を省略しない。

### fixed-leaf Fourier／eigencoordinate space

physical perturbation \(x\) にはx方向の正規化forward DFT

\[
\widehat x_k=\frac1{17}\sum_{n=0}^{16}e^{-2\pi i kn/17}x_n,
\qquad
x_n=\sum_{k=0}^{16}e^{2\pi i kn/17}\widehat x_k
\]

を使う。zero blockはQ011jの150次元fixed-conservation-leaf coordinate、非零16 blockは各153次元で、
合計2598実次元である。Q011lのcertified eigencolumn matrix \(V_k\) により

\[
y_k=V_k^{-1}\widehat x_k
\]

とする。real stateには \(y_{17-k}=\overline{y_k}\) を課し、complex coordinateを独立な実自由度として
二重計数しない。

selected block \(k\in\{0,1,16\}\) では \(y_k=(s_k,y_{E,k})\) と分け、Q011lのcertified invariant graph
\(G_k\) を用いて

\[
e_k=y_{E,k}-G_ks_k,
\qquad
y_k=(s_k,e_k+G_ks_k)
\]

とする。他の14 blockは全成分をexternal coordinateとする。selected／external実次元は`24 / 2574`、
全次元は`2598`でなければならない。

Banach normはcomplex modulusを用いるglobal block-sup norm

\[
\lVert(s,e)\rVert_{\mathcal X}
=\max\left\{\max_i|s_i|,\max_j|e_j|\right\}
\]

に固定する。固有値centerには有理sqrt enclosure、matrix perturbationにはcomplex absolute row-sum normを
用いる。componentwise `|Re|+|Im|`を線形dominationの代用にせず、eigenvalue modulus gapとoperator normを
混同しない。

### coordinate lift／inverse bound

Q011k primary 256-bit proofの

\[
v_k\ge\lVert V_k\rVert_\infty,
\qquad
\beta_k\ge\lVert V_k^{-1}\rVert_\infty
\]

とQ011l graph radius \(r_{G,k}\) を使う。zero blockの \(V_0\) は150次元leaf coordinateへ
値を返すため、populationへのQ011j affine lift normを \(\ell_0=186\) とする。非零blockでは
\(\ell_k=1\)、nonselected blockでは \(r_{G,k}=0\) とし、

\[
K_L=\sum_{k=0}^{16}\ell_kv_k(1+r_{G,k}),
\qquad
K_P=\max_{0\le k\le16}\beta_k(1+r_{G,k})
\]

をexact `Fraction`で評価する。DFT conventionから

\[
\lVert x\rVert_\infty\le K_L\lVert(s,e)\rVert_{\mathcal X},
\qquad
\lVert(s,e)\rVert_{\mathcal X}\le K_P\lVert x\rVert_\infty
\]

となる。登録capは \(K_L\le2600\)、\(K_P\le900\) とする。cross-block cancellationは使わない。
`186`を省略した旧式は使用しない。

### 同一norm上のlinear triangular split

Q011lのtransformed residual upperを \(\theta_k\)、graph radiusを \(r_{G,k}\) とし、selected blockで

\[
\eta_k=\theta_k(1+r_{G,k})
\]

を固定する。invariant-graph coordinateでlinear mapは

\[
\begin{pmatrix}s'_k\\e'_k\end{pmatrix}
=
\begin{pmatrix}S_k&B_k\\0&E_k\end{pmatrix}
\begin{pmatrix}s_k\\e_k\end{pmatrix}
\]

となる。各selected blockについて

\[
m_k=\min_{i\in S_k}|\lambda_{k,i}|_{\rm lower}-\eta_k,
\quad
q_k=\max_{j\in E_k}|\lambda_{k,j}|_{\rm upper}+\eta_k,
\quad
\lVert B_k\rVert\le\theta_k
\]

をexactに計算する。nonselected blockでは

\[
q_k=\max_j|\lambda_{k,j}|_{\rm upper}+\theta_k
\]

とする。global constantsは

\[
m_S=\min_{k\in\{0,1,16\}}m_k,
\qquad
q_E=\max_{0\le k\le16}q_k,
\qquad
\gamma_0=\frac{q_E}{m_S}
\]

である。登録閾値は次に固定する。

- \(m_S\ge0.983\)
- \(q_E\le0.982\)
- \(m_S-q_E\ge10^{-3}\)
- \(\gamma_0\le0.999\)
- \(1/m_S\le1.02\)
- \(\max_k\lVert B_k\rVert\le10^{-6}\)

Q011kのeigenvalue-level normal gapだけではpassにしない。Q011lのsame-norm residualとgraph transformを
必ず含める。

### cutoff／graph Banach space

localization radiusを観測前に

\[
\rho=10^{-11}
\]

へ固定する。\(C_\rho:\mathcal X\to\mathcal X\) は各complex coordinateを閉円板
\(\{|z_j|\le\rho\}\)へmetric projectionするcomponentwise radial clampとする。これは

- \(C_\rho z=z\) on \(\lVert z\rVert_{\mathcal X}\le\rho\)
- \(C_\rho(0)=0\)
- \(1\)-Lipschitz in \(\lVert\cdot\rVert_{\mathcal X}\)
- complex conjugacy preserving

を満たす。coordinate mapを \(F(z)=Az+N(z)\) と書き、localized mapを

\[
F_\rho(z)=Az+N(C_\rho z)
\]

と定義する。これはcore ball上で元のrepaired exact mapと一致する。

physical localization upper \(K_L\rho\) は`<=3e-8`を要求する。Q011mのexact-root population／density floorから

\[
f_{\min}\ge f_{*,\min}-K_L\rho\ge0.02,
\qquad
\rho_{\min}\ge\rho_*-9K_L\rho\ge0.99
\]

を確認し、Q011m derivative domain `1e-4`内に含める。

selected／external closed ballsを \(B_S(\rho),B_E(\rho)\) とし、

\[
\mathcal G_{\rho,1}
=\{h:B_S(\rho)\to B_E(\rho):h(0)=0,
h(\overline s)=\overline{h(s)},\operatorname{Lip}(h)\le1\}
\]

をuniform metricで扱う。これはclosed complete graph spaceである。ただし本gateでは、\(F_\rho\) が誘導する
graph transformのwell-definedness、self-map、base inverse、contractionは判定しない。

### validity gate

1. Q011k--Q011nのartifact／runner、19 digest、outcome、claim boundaryを直接再現する。
2. 17 Fourier block、zero／nonzero dimension、conjugacy、`24 + 2574 = 2598`を再現する。
3. \(V_k,V_k^{-1},G_k\) の型、zero-block population lift `186`、same-norm boundを
   Q011k--Q011m recordから再構成する。
4. 全17 blockのmodulus interval、\(\theta_k,\eta_k,m_k,q_k,B_k\)をexact arithmeticで評価する。
5. \(K_L,K_P,m_S,q_E,\gamma_0\)の式とwitness block／centerを保存する。
6. cutoff、localized map、graph spaceのdomain／codomain、conjugacy、core一致を明示する。
7. finite strict JSON、input／coordinate／linear／localization／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、linear dominationもgraph-transform readinessも解釈しない。

### hypothesis gate と停止規則

validity通過後、次の5項目を別々に要求する。

1. fixed-leaf Fourier／eigencoordinate／graph triangular mapがbijectiveで、全dimensionとconjugacyが閉じる。
2. \(K_L\le2600\)、\(K_P\le900\)、\(K_L\rho\le3\times10^{-8}\) と
   population／density／derivative-domain bufferが通る。
3. same normで \(m_S\ge0.983\)、\(q_E\le0.982\)、\(m_S-q_E\ge10^{-3}\) が通る。
4. \(\gamma_0\le0.999\)、\(1/m_S\le1.02\)、selected-external coupling upper `<=1e-6`が通る。
5. \(C_\rho,F_\rho,\mathcal G_{\rho,1}\) のdomain／codomainが型付きで固定され、scalar surrogateを
   operator theoremへ読み替えていない。

全5項目が通る場合だけ
`the repaired fixed-leaf split admits a type-correct localized graph-transform setup with rigorous linear domination`
として`accepted`とする。一つでも落ちれば
`the registered block-sup norm does not support the localized graph-transform setup`
として`rejected`とする。これはinvariant manifold／SSMの不存在を意味しない。

`accepted`なら次のQ011pで、Q011mのanalytic \(D^2/D^3\) boundをcoordinate normへ変換し、
\(F_\rho\) が \(\mathcal G_{\rho,1}\) 上でbase inverse、self-map、strict contractionを持つかを
事前登録する。`rejected`なら最初のfailed block／constantだけを用いてblock weightまたはgraph slope capを
再設計する。`inconclusive`なら最初のprotocol failureだけを修復する。

### 主張境界

本gateは固定17²、固定保存量葉、repaired exact map、Q011k split、Q011l linear invariant graph、
complex block-sup norm、radius`1e-11`のcutoff setupに限る。nonlinear graph-transform self-map／contraction、
fixed graph、exact invariant manifold／SSM、smoothness／一意性、normal attraction、basin、componentwise
quadratic coefficient、raw Q011b map、他grid／force／wall、D3Q27を構成・認証しない。

### Q011o 実行結果

validity `7 / 7`はすべて通過した。hypothesisは`4 / 5`で、結果は有効な`rejected`、分類は
`the registered block-sup norm does not support the localized graph-transform setup`である。

数値条件はすべて通った。

- fixed-leaf／selected／external real dimension: `2598 / 24 / 2574`
- \(K_L / K_P / K_L\rho\):
  `2577.1878203041115 / 891.1458398501893 / 2.5771878203041115e-8`
- \(m_S / q_E / (m_S-q_E)\):
  `0.9837709559259398 / 0.9817098561324995 / 0.002061099793440198`
- \(\gamma_0 / 1/m_S / \max\lVert B_k\rVert\):
  `0.9979048987154736 / 1.0164967708960113 / 2.0299911997564775e-8`

唯一のfailed hypothesisは`fixed_leaf_triangular_coordinate_is_bijective_and_real_typed`である。非零8組の
conjugate blockはすべて一致したが、自己共役なzero Fourier blockのselected center 6個は、現在のdyadic
eigencoordinateではexactな標準共役multisetを作らない。従って登録した成分ごとの標準共役をzero blockへ
適用できない。

- input／coordinate／linear／localization／result digest:
  `0bddd90fc21a745b910ff47e133e72045842c77b589a818a21e946f85ba63da0` /
  `6c00ce5d9df986830a4ad2d98df3970417d47e4fb9f1784364ce32b64d7396b7` /
  `f9aaea144b0e79c6adf42296b7e8dcd562f2b75525b6abf4ac99c43dcbd1859c` /
  `5799e9997ac1ec692ddce97465174204ee22debaea942ed7fab637209c912e0d` /
  `6ec0a97c1b3d653e5edd3ffc7f4b8b9fa746e86e8d706e251753eecb8ab9a864`
- runner／artifact newline-normalized SHA-256:
  `60d9c445dace16d114e46263f2b47fe2db993b894337cdd462f204da09543f1f` /
  `bbbc26939d4ef73aae95ad6517f5f1549f2eaf7b6edcbac5e5171f329064bc07`

これはlinear dominationの失敗でも、invariant manifold／SSMの不存在でもない。停止規則どおり、次は
zero blockの実構造だけを修復し、通過するまでnonlinear graph transformへ進まない。

## Q011p: zero-block invariant-subspace reality certificate — 事前登録

### 問い

Q011oで唯一failした自己共役zero Fourier blockについて、Q011lが認証した6次元complex selected
invariant subspaceが、6次元real invariant subspaceのcomplexificationであることをrigorousに示せるか。

本gateはzero blockの**invariant subspaceの実構造**だけを判定する。real basis、Q011oのcoordinate
lift／inverse再評価、conjugacy-equivariant cutoff、nonlinear graph transform、fixed graphは構成しない。

### 封印入力

- Q011j artifact／runner newline-normalized SHA-256:
  `74a2e084137699739c14d980b05676e14e6802b4018b3893d3d05270850c2c5a` /
  `23a7a3a272264be3eb5330b2456192bd797aa968c4f795e2cbe8e337fc8fe4b5`
- Q011j input／coordinate／oracle／proof／result digest:
  `a183f4830c757b58122132cf64111fd5375636affdb6c0b31e1cd90e89085799` /
  `adaef353b8b64509334794c6014dc8b88e81ca2b776c3b65bd4d50911ae9452b` /
  `177468a48f667ddd922ed4b979d3e7e5d4cc0ed3afffe27a34651060da8e0f5f` /
  `1080fcea24358422514bba7fb9881928269c853cb4d12b0282e63840c56124c0` /
  `ddad5beca9693eeab726382ac864d01a27b749d579c2ec8f12dd9f8c499db934`
- Q011k artifact／runner newline-normalized SHA-256:
  `8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a` /
  `d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07`
- Q011k input／root／block／proof／result digest:
  `f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2` /
  `f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc` /
  `7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8` /
  `1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4` /
  `2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e`
- Q011l artifact／runner newline-normalized SHA-256:
  `2878d8ebaaedc29990700ccac25b78185e0b6139dd371521f14602caf4514c0a` /
  `59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7`
- Q011l input／graph／pair／homological／result digest:
  `1810f989a0328521e8b6d6ccbc2153cb9a945bb2c129c70d7b25a0c227fc7011` /
  `a7d0f320fa7391c506f42853a94ede66fc73e81b004dfccda144028082cb8db3` /
  `694cc2955bcef05df13ad30582f46f84bb627aaa7b336b5278e9b5139e29d377` /
  `14d67f1d915aa3bd6bc34117562da4908e19036943e60fb638eddf6a42b20915` /
  `c372aa5962a7f3d0c83a126303a9e36e4f0830d113f9c49b922d03beb2f09a45`
- Q011o artifact／runner newline-normalized SHA-256:
  `bbbc26939d4ef73aae95ad6517f5f1549f2eaf7b6edcbac5e5171f329064bc07` /
  `60d9c445dace16d114e46263f2b47fe2db993b894337cdd462f204da09543f1f`
- Q011o input／coordinate／linear／localization／result digest:
  `0bddd90fc21a745b910ff47e133e72045842c77b589a818a21e946f85ba63da0` /
  `6c00ce5d9df986830a4ad2d98df3970417d47e4fb9f1784364ce32b64d7396b7` /
  `f9aaea144b0e79c6adf42296b7e8dcd562f2b75525b6abf4ac99c43dcbd1859c` /
  `5799e9997ac1ec692ddce97465174204ee22debaea942ed7fab637209c912e0d` /
  `6ec0a97c1b3d653e5edd3ffc7f4b8b9fa746e86e8d706e251753eecb8ab9a864`

Q011j--Q011lの`accepted`とQ011oのvalid `rejected`を直接再現する。Q011oのnested sealだけで
Q011j--Q011lの直接照合を省略しない。Q011oの他4 hypothesisとclaim boundaryも変更しない。

### zero-block conjugation operator

Q011kと同じcanonical binary64 eigencolumn matrix \(V_0\) とinverse candidate \(W_0\) を再構成し、全
binary64 entryをexact dyadic rationalとして扱う。zero blockのexact fixed-leaf linear operator \(A_0\) が
real、\(V_0\) がinvertibleであることをQ011j／Q011k certificateから再現する。

physical conjugationをeigencoordinateへpull backしたantilinear involutionは

\[
\mathcal J_0(y)=J_0\overline y,
\qquad
J_0=V_0^{-1}\overline{V_0}
\]

である。Q011oで棄却した \(y_0=\overline y_0\) を仮定し直さず、\(J_0\) を明示的に扱う。

Q011kのdirected inverse defect

\[
\delta_V=\lVert I-W_0V_0\rVert_\infty<1,\qquad
w=\lVert W_0\rVert_\infty,\qquad v=\lVert V_0\rVert_\infty
\]

から、point product \(J_c=W_0\overline{V_0}\) に対する

\[
\lVert J_0-J_c\rVert_\infty
\le
\varepsilon_J
:=\frac{\delta_V}{1-\delta_V}wv
\]

を使う。selected indexはQ011lと同じ6個、external indexは残る144個とし、

\[
J_0=
\begin{pmatrix}
J_{EE}&J_{ES}\\
J_{SE}&J_{SS}
\end{pmatrix}
\]

の4 blockをcomplex absolute row-sum normで包絡する。\(J_{SS}\) のinverseは6次元point candidateと
Neumann defectから直接認証し、

\[
m_{SS}:=\frac1{\lVert J_{SS}^{-1}\rVert_\infty}
\]

のlower boundを作る。full condition numberやeigenvalue pairingだけを代用しない。

### conjugated graph とexpanded uniqueness ball

Q011l zero-block invariant graphを \(G:S\to E\)、そのradius upperを \(r_G\) とする。物理共役した
subspaceが同じreference split上のgraphで表せる場合、そのgraphは

\[
\mathcal C(G)=
(J_{EE}\overline G+J_{ES})
(J_{SE}\overline G+J_{SS})^{-1}
\]

である。block boundを \(j_{\alpha\beta}\) と書き、

\[
d_C=m_{SS}-j_{SE}r_G,
\qquad
r_C=\frac{j_{EE}r_G+j_{ES}}{d_C}
\]

をdirected upper／lower arithmeticで評価する。

Q011lのRiccati contractionを再利用するexpanded uniqueness radiusは観測前に

\[
R_{\rm real}=10^{-2}
\]

へ固定する。Q011lの \(h=\theta/g\) を用い、

\[
h(1+2R_{\rm real}+R_{\rm real}^2)\le R_{\rm real},
\qquad
h(2+2R_{\rm real})<1,
\qquad
g-2\theta(1+R_{\rm real})>0
\]

をexactに再評価する。\(G\) と \(\mathcal C(G)\) がともにこのball内のRiccati fixed pointなら、一意性から
\(\mathcal C(G)=G\) であり、selected invariant subspaceはcomplex conjugation invariantである。

### arithmetic と登録閾値

primary proof laneはMPFR `256 bit`、independent containment laneは`192 bit`に固定する。binary64 inputの
exact conversion、directed lower／upper、forbidden flag、caller context restorationを両laneで検査する。
gate判定にbinary64 normを使わない。

次を観測前に固定する。

- \(\varepsilon_J\le10^{-8}\)
- \(j_{ES}\le10^{-6}\)
- \(j_{EE}\le100\)
- \(j_{SE}\le100\)
- \(\lVert J_{SS}^{-1}\rVert_\infty\le20\)
- \(d_C>0\)
- \(r_C\le R_{\rm real}=10^{-2}\)
- expanded Riccati self-map／strict contraction／identification marginの3条件がすべてpass

最初の5 capは良いcondition numberを主張するためではなく、conjugated graphを同じuniqueness ballへ
入れるための有限な登録包絡である。

### validity gate

1. Q011j／Q011k／Q011l／Q011oのartifact、runner、20 digest、outcome、claim boundaryを直接再現する。
2. zero block \(A_0,V_0,W_0\)、selected／external dimension `6 / 144`、Q011l graph certificateを再構成する。
3. \(A_0\) のexact reality、\(V_0\) のcertified invertibility、\(\mathcal J_0\) のdomain／codomainを確認する。
4. \(J_c\)、\(\varepsilon_J\)、4 block bound、\(J_{SS}^{-1}\) boundをdirected arithmeticで再現する。
5. \(d_C,r_C\) とexpanded Riccati self-map／contraction／identification式をexactに再現する。
6. 192／256-bit laneのcontainment、MPFR flag、caller context、全boundのfinite性を確認する。
7. strict JSON、input／conjugation／uniqueness／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、zero-block realityを解釈しない。

### hypothesis gate と停止規則

validity通過後、次の5項目を別々に要求する。

1. zero-block physical operatorがexact realで、\(J_0\overline{J_0}=I\) と
   \(J_0\overline{(V_0^{-1}A_0V_0)}=(V_0^{-1}A_0V_0)J_0\) が定義から従う。
2. \(\varepsilon_J,j_{ES},j_{EE},j_{SE},\lVert J_{SS}^{-1}\rVert_\infty\) が登録cap内に入る。
3. \(d_C>0\) かつ \(r_C\le R_{\rm real}\) で、共役subspaceが同じreference split上のgraphになる。
4. radius \(R_{\rm real}\) でRiccati mapがself-mapかつstrict contractionで、spectral identificationが保たれる。
5. \(G\) と \(\mathcal C(G)\) が同じuniqueness ballのfixed pointとなり、selected subspaceがconjugation
   invariantで、そのreal fixed subspaceのdimensionが6になる。

全5項目が通る場合だけ
`the Q011l zero-block selected invariant subspace is the complexification of a six-dimensional real invariant subspace`
として`accepted`とする。一つでも落ちれば
`the registered Q011l zero-block certificate does not close a conjugation-invariant uniqueness neighborhood`
として`rejected`とする。これはreal invariant subspaceまたはmanifold／SSMの不存在を意味しない。

`accepted`なら次のQ011qで、このreal subspaceの明示real frame、external real complement、coordinate
lift／inverse、linear domination、equivariant cutoffを事前登録し、Q011oのfailed hypothesisを再発行する。
`rejected`ならzero blockだけをdirect real Schur／Riesz projectorで再構成する。`inconclusive`なら最初の
protocol failureだけを修復する。

### 主張境界

本gateは固定17² repaired exact mapのfixed-conservation leaf、zero Fourier linear block、Q011lの6次元
selected invariant graphとその実構造に限る。明示real basis、real-coordinate norm、Q011o acceptance、
nonlinear cutoffのequivariance、nonlinear graph transform、fixed graph、exact invariant manifold／SSM、
smoothness／一意性、normal attraction、basin、他grid／force／wall、D3Q27を構成・認証しない。

### Q011p 実行結果

validity `7 / 7`、hypothesis `5 / 5`がすべて通過した。結果は`accepted`、分類は
`the Q011l zero-block selected invariant subspace is the complexification of a six-dimensional real invariant subspace`
である。

zero blockのexact operator familyがrealであることを再現し、canonical \(V_0,W_0\) から
\(J_c=W_0\overline{V_0}\) をdirected MPFRで包絡した。primary 256-bit proofはindependent 192-bit
enclosureへ包含され、両laneでforbidden flagなし、caller context保存を確認した。

- \(\lVert V_0\rVert_\infty / \lVert W_0\rVert_\infty / \delta_V\):
  `12.325418776439488 / 52.109861896176966 / 7.887561672581473e-13`
- \(\varepsilon_J\): `5.065990537433956e-10`
- \(j_{EE} / j_{ES} / j_{SE} / j_{SS}\):
  `3.4122262852713123 / 5.066312585495729e-10 / 5.06743891662501e-10 / 1.3024942843903295`
- \(\lVert J_{SS}^{-1}\rVert_\infty / m_{SS}\):
  `1.3024942847431704 / 0.7677576874720666`
- Q011l graph radius／\(d_C\)／\(r_C\)／\(R_{\rm real}\):
  `1.6628540517032178e-6 / 0.7677576874720659 / 7.391057136444022e-6 / 0.01`
- expanded self-map／contraction／identification margin:
  `8.481387090712263e-7 / 1.6794825922202499e-6 / 0.02441570609690408`
- input／conjugation／uniqueness／result digest:
  `49a2df9f7f8db4ba95ebb93413324e667d2237a52a390e2e6f44b512c5fd953f` /
  `087bcf415559cf0985194ad50dcbb0748ecdadda4df6b53ad7172f5b7cba1a05` /
  `41eee5097e7a0c2ea18ac79cd1b48abb1223d1925e953d7b2f34a4fb24777339` /
  `19edd32732a658a3811ebedc07a9a4483f1fff3d4a26ff64d7917ad2ea01c7f7`
- runner／artifact newline-normalized SHA-256:
  `fec9509068939663d6172539630f577383ad4da15f4c4575ef5caab7c65971f7` /
  `68968f8d01135fa3575a69c878b5ab89952ae39ec8e44b7fb398a3384f2fa6e1`

\(G\) と物理共役graph \(\mathcal C(G)\) はともにradius `1e-2`のRiccati一意性球内のfixed pointである。
従って両者は一致し、selected complex 6-planeはconjugation invariant、そのreal fixed spaceは6次元である。

この受理は明示real frameをまだ与えず、Q011oのvalid `rejected`も変更しない。nonlinear cutoff、nonlinear
graph transform、fixed graph、exact invariant manifold／SSMも未認証である。停止規則どおり、次はQ011qで
explicit real zero-block frameとexternal real complementを観測前に事前登録し、real-coordinate
lift／inverse、linear domination、equivariant cutoffを再評価する。

## Q011q: explicit real frame, complement, and localized setup reissue — 事前登録

### 問い

Q011pが存在を認証したzero-blockの6次元real selected spaceに対し、固定seedから明示real frameを構成し、
144次元external real complementと合わせて、Q011oのcoordinate lift／inverse、linear domination、
localizationをreal-typed setupとして再発行できるか。

本gateはlinear coordinateとcutoffの型だけを修復する。nonlinear derivative bound、induced graph transform、
self-map／contraction、fixed graph、exact invariant manifold／SSMは判定しない。

### 封印入力

次の6 artifactを直接照合する。nested sealで直接入力の照合を代用しない。

- Q011j artifact／runner newline-normalized SHA-256:
  `74a2e084137699739c14d980b05676e14e6802b4018b3893d3d05270850c2c5a` /
  `23a7a3a272264be3eb5330b2456192bd797aa968c4f795e2cbe8e337fc8fe4b5`
- Q011j input／coordinate／oracle／proof／result digest:
  `a183f4830c757b58122132cf64111fd5375636affdb6c0b31e1cd90e89085799` /
  `adaef353b8b64509334794c6014dc8b88e81ca2b776c3b65bd4d50911ae9452b` /
  `177468a48f667ddd922ed4b979d3e7e5d4cc0ed3afffe27a34651060da8e0f5f` /
  `1080fcea24358422514bba7fb9881928269c853cb4d12b0282e63840c56124c0` /
  `ddad5beca9693eeab726382ac864d01a27b749d579c2ec8f12dd9f8c499db934`
- Q011k artifact／runner newline-normalized SHA-256:
  `8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a` /
  `d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07`
- Q011k input／root／block／proof／result digest:
  `f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2` /
  `f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc` /
  `7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8` /
  `1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4` /
  `2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e`
- Q011l artifact／runner newline-normalized SHA-256:
  `2878d8ebaaedc29990700ccac25b78185e0b6139dd371521f14602caf4514c0a` /
  `59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7`
- Q011l input／graph／pair／homological／result digest:
  `1810f989a0328521e8b6d6ccbc2153cb9a945bb2c129c70d7b25a0c227fc7011` /
  `a7d0f320fa7391c506f42853a94ede66fc73e81b004dfccda144028082cb8db3` /
  `694cc2955bcef05df13ad30582f46f84bb627aaa7b336b5278e9b5139e29d377` /
  `14d67f1d915aa3bd6bc34117562da4908e19036943e60fb638eddf6a42b20915` /
  `c372aa5962a7f3d0c83a126303a9e36e4f0830d113f9c49b922d03beb2f09a45`
- Q011m artifact／runner newline-normalized SHA-256:
  `b76b0ec1a1436aa3c2b48fcc29485e60e03675bf9a1f4f85ac3106d30687da3f` /
  `0cdc6ec9697d25bea3b28cf90f01f3f639062b3c04a64c4a88e6bd7221163150`
- Q011m input／derivative／coefficient／majorant／result digest:
  `dd30ead5c7c6081502bc34a6163ce64321dd4f9a339c7f24959dfc76891591cb` /
  `0b8f345fdf2bda5b95f2c1624920968f1ad499f4d5e765c0b8305e2045ac7e3a` /
  `1d708042f97c8c42164b07ff7104a68bdef95c14faf90dcb0171749d92b8a514` /
  `bf7144f407dd3e6aabf2161bf3d8c48dbb2e6c89a48cde9cfccf1cff60455e00` /
  `f47a1a4c1712fcff129c3840d7e64dfe1bbbe4bdacc049e28be6f868dbfc9cd4`
- Q011o artifact／runner newline-normalized SHA-256:
  `bbbc26939d4ef73aae95ad6517f5f1549f2eaf7b6edcbac5e5171f329064bc07` /
  `60d9c445dace16d114e46263f2b47fe2db993b894337cdd462f204da09543f1f`
- Q011o input／coordinate／linear／localization／result digest:
  `0bddd90fc21a745b910ff47e133e72045842c77b589a818a21e946f85ba63da0` /
  `6c00ce5d9df986830a4ad2d98df3970417d47e4fb9f1784364ce32b64d7396b7` /
  `f9aaea144b0e79c6adf42296b7e8dcd562f2b75525b6abf4ac99c43dcbd1859c` /
  `5799e9997ac1ec692ddce97465174204ee22debaea942ed7fab637209c912e0d` /
  `6ec0a97c1b3d653e5edd3ffc7f4b8b9fa746e86e8d706e251753eecb8ab9a864`
- Q011p artifact／runner newline-normalized SHA-256:
  `68968f8d01135fa3575a69c878b5ab89952ae39ec8e44b7fb398a3384f2fa6e1` /
  `fec9509068939663d6172539630f577383ad4da15f4c4575ef5caab7c65971f7`
- Q011p input／conjugation／uniqueness／result digest:
  `49a2df9f7f8db4ba95ebb93413324e667d2237a52a390e2e6f44b512c5fd953f` /
  `087bcf415559cf0985194ad50dcbb0748ecdadda4df6b53ad7172f5b7cba1a05` /
  `41eee5097e7a0c2ea18ac79cd1b48abb1223d1925e953d7b2f34a4fb24777339` /
  `19edd32732a658a3811ebedc07a9a4483f1fff3d4a26ff64d7917ad2ea01c7f7`

Q011j--Q011mとQ011pの`accepted`、Q011oのvalid `rejected`と唯一のfailed hypothesisを再現する。
Q011qの新setupはQ011oの履歴を書き換えず、別のreal-coordinate reissueとして採点する。

### graph coordinate上の共役

zero-block eigencoordinateをexternal／selected順に \(y=(y_E,y_S)\)、Q011l graphを
\(y_E=G s\) とする。graph coordinateをselected／external順の

\[
e=y_E-Gs,
\qquad
(s,e)\longmapsto y=(e+Gs,s)
\]

とする。Q011pの \(J_0\) をこの座標へ移すと、selected graphの共役不変性により

\[
\mathcal K(s,e)=
\left(K_{SS}\overline s+K_{SE}\overline e,
K_{EE}\overline e\right),
\]

\[
K_{SS}=J_{SE}\overline G+J_{SS},
\qquad
K_{SE}=J_{SE},
\qquad
K_{EE}=J_{EE}-GJ_{SE}.
\]

selectedからexternalへの欠落blockがexactにzeroであることを、Q011pの
\(\mathcal C(G)=G\) と同じRiccati identityから再現する。\(\mathcal K^2=I\) から
\(K_{SS}\overline{K_{SS}}=I\)、\(K_{EE}\overline{K_{EE}}=I\) も確認する。

binary64 point product \(J_f=\operatorname{fl}(W_0\overline{V_0})\) はseed選択だけに使う。
全entryをexact dyadicへ戻し、Q011pのdirected product enclosureからpoint-product error
\(\varepsilon_f\) を求める。\(G\) のpointはzeroに固定し、

\[
\varepsilon_K=\varepsilon_J+\varepsilon_f+j_{SE}r_G
\]

をselected／external diagonal conjugation blockの共通perturbation upperとする。gate判定に未包絡の
binary64 matrix normを使わない。

### 固定seedによるreal frame

各 \(n\times n\) point conjugation block \(K_c\) に対し、candidate poolを

\[
P_c=[I+K_c,\ i(I-K_c)]
\]

とする。binary64 modified Gram--Schmidtのgreedy pivotを、最大残差、同値なら小さいpool index優先で
固定し、最初の \(n\) pivotからseed matrix \(C\) を選ぶ。pivotingはseed proposalだけであり、rank判定は
しない。seedは \([I,iI]\) の列なのでexact Gaussian-integer matrixとして再構成する。

actual frameは

\[
F_S=C_S+K_{SS}\overline{C_S},
\qquad
F_E=C_E+K_{EE}\overline{C_E}
\]

とする。各列はexactに共役固定である。point frame inverse candidateのdefectとnormをdirected MPFRで
包絡し、\(\lVert F-F_c\rVert\le\varepsilon_K\lVert C\rVert\) を加えたNeumann argumentでactual
\(F_S,F_E\) のinvertibilityを認証する。seed index、frame、inverse candidate、interval productのhashを
artifactへ保存する。

primary proof laneは`256 bit`、independent containment laneは`192 bit`に固定する。両laneでexact
binary64 conversion、directed endpoint、forbidden flag、caller context restorationを検査する。

### external real section とdirect sum

\(S_{\mathbb R}=\{s:K_{SS}\bar s=s\}\)、
\(E_{\mathbb R}=\{e:K_{EE}\bar e=e\}\) とする。external quotientのcanonical real sectionを

\[
H(e)=\frac12K_{SE}\overline e
\]

と固定する。これは \((0,e)\) とその共役像の平均であり、

\[
X_{0,\mathbb R}^{G}
=
\{(s,0):s\in S_{\mathbb R}\}
\oplus
\{(H(e),e):e\in E_{\mathbb R}\}
\]

を与える。従ってzero blockの明示real frameは

\[
\widehat F_S=\binom{F_S}{0},
\qquad
\widehat F_E=\binom{HF_E}{F_E}
\]

で、real dimensionは`6 + 144 = 150`である。section normは
\(h\le j_{SE}/2\) で包絡する。

### real-coordinate norm とQ011o boundの再発行

real coefficient frameのbijectivityを認証したうえで、解析normはcomplex modulus block-sup normの
real fixed locusへのrestrictionを用いる。

\[
\lVert(s,e)\rVert_{\mathcal X_{\mathbb R}}
=\max\{\lVert s\rVert_\infty,\lVert e\rVert_\infty\},
\qquad s\in S_{\mathbb R},\ e\in E_{\mathbb R}.
\]

full graph coordinateへのreal shearは \((s,e)\mapsto(s+H(e),e)\) で、そのlift／inverse factorは
\(1+h\) である。Q011oのzero-block contributionだけを

\[
186\,v_0(1+r_G)
\longmapsto
186\,v_0(1+r_G)(1+h),
\]

\[
\beta_0(1+r_G)
\longmapsto
\beta_0(1+r_G)(1+h)
\]

へ置換し、他16 blockは変更しない。cross-block cancellationは使わない。

linear mapはreal split上でもupper triangularである。selected conorm \(m_S\) とexternal quotient norm
\(q_E\) はQ011oと同じrestriction boundを使う。zero-block couplingだけを

\[
b_{\mathbb R,0}
\le
\theta_0+(p_{S,0}+q_{E,0})h
\]

で再評価する。ここで \(p_{S,0}\) はzero selected blockのoperator norm upperである。eigenvalue gapだけを
operator boundへ代用しない。

### equivariant cutoff

radiusはQ011oと同じ \(\rho=10^{-11}\) に固定する。selected／external real space上でradial retraction

\[
c_\rho(z)=
\begin{cases}
z,&\lVert z\rVert\le\rho,\\
\rho z/\lVert z\rVert,&\lVert z\rVert>\rho
\end{cases}
\]

を用い、\(C_\rho(s,e)=(c_\rho(s),c_\rho(e))\) とする。real scalar multiplicationだけなので各real
fixed spaceを保ち、core ballでidentity、global Lipschitz upperは`2`とする。Q011oのcomponentwise complex
disk projectionは再利用しない。localized mapがreal spaceからreal spaceへ写りcoreでoriginal mapと一致する
こと、real graph spaceがclosed completeであることだけを確認する。nonlinear derivativeとgraph transformは
未定義のまま残す。

### 登録cap

次を観測前に固定する。

- \(\varepsilon_K\le10^{-8}\)
- selected／external point frame norm upper: 各`20`
- selected actual frame inverse norm upper: `100`
- external actual frame inverse norm upper: `1000`
- selected／external frame perturbation upper: 各`1e-6`
- section norm \(h\le10^{-6}\)
- real dimension: selected／external／total `24 / 2574 / 2598`
- \(K_L^{\mathbb R}\le2600\)、\(K_P^{\mathbb R}\le900\)
- \(K_L^{\mathbb R}\rho\le3\times10^{-8}\)
- \(m_S\ge0.983\)、\(q_E\le0.982\)、\(m_S-q_E\ge10^{-3}\)
- \(q_E/m_S\le0.999\)、\(1/m_S\le1.02\)
- real selected--external coupling upper \(\le10^{-6}\)
- cutoff global Lipschitz upper \(\le2\)、population／density bufferはQ011oと同じthresholdを通過

frame capはcondition numberの最適性を主張するものではなく、固定seed frameが有限でbijectiveであることを
拒否可能にするための登録包絡である。

### validity gate

1. Q011j／Q011k／Q011l／Q011m／Q011o／Q011pのartifact、runner、29 digest、outcome、claim boundaryを直接再現する。
2. \(J_f\)、directed point-product error、\(K_{SS},K_{SE},K_{EE}\) の式とinvolution identityを再現する。
3. deterministic pivot、exact seed、selected／external frame candidate、dual-precision inverse proofを再現する。
4. frameの共役固定性、Neumann invertibility、section identity、`6 + 144 = 150` direct sumを確認する。
5. 17 block、`24 + 2574 = 2598`、real lift／inverse formula、zero lift `186`を再現する。
6. real linear split、coupling formula、radial cutoff、localized map、closed complete graph spaceの型を確認する。
7. 192／256-bit containment、MPFR flag、finite性、strict JSON、4 section digest、result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、real setupを解釈しない。

### hypothesis gate と停止規則

validity通過後、次の5項目を別々に要求する。

1. fixed seedsがinvertibleなselected／external共役固定frameを与え、sectionと合わせてreal direct sumがbijectiveである。
2. frame／section boundとreal coordinate lift／inverseが登録cap内に入る。
3. 同じreal normでselected conormとexternal normがstrictに分離する。
4. selected inverseとreal selected--external couplingが登録cap内に入る。
5. radial cutoff、localized map、real graph Banach spaceがtype-correctで、localization bufferが登録cap内に入る。

全5項目が通る場合だけ
`the repaired fixed-leaf split admits a certified real-frame localized graph-transform setup`
として`accepted`とする。一つでも落ちれば
`the registered symmetrized real frames do not close a real-typed localized graph-transform setup`
として`rejected`とする。これは別seed／real Schur frameまたはinvariant manifold／SSMの不存在を意味しない。

`accepted`なら次のQ011rで、Q011mのanalytic derivative majorantをこのreal normへ変換し、induced nonlinear
graph transformの定義、self-map、contractionを事前登録する。`rejected`なら最初のfailed frame／section／
coordinate／linear／cutoff conditionだけを使い、seed selection、direct real Schur／Riesz frame、block weight、
またはcutoffを一つだけ修正する。`inconclusive`なら最初のprotocol failureだけを修復する。

### 主張境界

本gateは固定17² repaired exact map、fixed-conservation leaf、Q011l selected graph、Q011p zero-block reality、
固定seed real frame、external real section、radius`1e-11` localization setupに限る。componentwise exact frame
entry、frameの最適condition number、nonlinear derivative bound、induced graph transform、self-map／contraction、
fixed graph、exact invariant manifold／SSM、smoothness／一意性、normal attraction、basin、他grid／force／wall、
D3Q27を構成・認証しない。

### Q011q 実行結果

validity `7 / 7`、hypothesis `5 / 5`を通過し、
`the repaired fixed-leaf split admits a certified real-frame localized graph-transform setup`
として`accepted`とした。

Q011j--Q011pの6 artifactと29 digestはすべて直接再現した。Q011pのdirected conjugation enclosureに、
binary64 point productをexact dyadicへ戻した誤差とQ011l graph radiusを加え、

\[
\varepsilon_K
=\varepsilon_J+\varepsilon_f+j_{SE}r_G
=5.066101711744531\times10^{-10}
\]

を得た。固定seed pool `[I+K_c, i(I-K_c)]` のtwo-pass MGS pivotはselected `6`列、external `144`列を
決定的に選び、256-bit proofと192-bit containmentの双方でframe inverseを認証した。

- \(\varepsilon_f\): `1.0274789924034183e-14`
- selected seed norm／point-frame norm／actual inverse／perturbation:
  `2 / 2.6049885677674496 / 1.1494585872526437 / 1.0132203423489061e-9`
- external seed norm／point-frame norm／actual inverse／perturbation:
  `2 / 5.267401433754149 / 1.5755497300774828 / 1.0132203423489061e-9`
- canonical section norm \(h\): `2.533719458312505e-10`
- zero-block real dimension: `6 + 144 = 150`
- fixed-leaf real dimension: `24 + 2574 = 2598`
- \(K_L^{\mathbb R} / K_P^{\mathbb R} / K_L^{\mathbb R}\rho\):
  `2577.187820884975 / 891.1458398501893 / 2.577187820884975e-8`
- \(m_S / q_E / (m_S-q_E) / (q_E/m_S)\):
  `0.9837709559259398 / 0.9817098561324995 / 0.002061099793440198 / 0.9979048987154736`
- selected inverse／real coupling:
  `1.0164967708960113 / 2.080001889821235e-8`
- localized population／density floor:
  `0.027775882541472084 / 0.999999768052464`
- input／conjugation／frame／setup／result digest:
  `c9e57c60fe678901c5502bf163d7317c06fedb35322e8591e741c330969829b5` /
  `583a28e1453b75700d0674bf090c4f8c0652d7538f84bef7c8ea7e09415db54e` /
  `1210f4d2c85d4a0cad9978531b297b5e493bac5f8d54d5eafa6ee7a5a68a6d7b` /
  `ec52daadd80261b9e94672beb979fd5f01e4f1c4bc0e63090a0cccbb90cda26b` /
  `274ddd32b50000c953c623285993ba533651a720c6dc79ae693a0e24a3f623ae`
- runner／artifact newline-normalized SHA-256:
  `83031650f7ecd54adb048a74ace2df96068317531aeb84fb57b9f797b9e33f67` /
  `776be2af80fdbb867fd72eb3c0bdfe82ca30f5fa50bc9436818df5c7f87e676d`

これでQ011oで失敗したzero-blockの標準共役typingを、明示real frameとcanonical external sectionを持つ
別座標として修復した。Q011oの履歴上のvalid `rejected`は変更しない。radial cutoffは両real fixed spaceを
保つが、このgateではnonlinear derivative majorantをreal normへ輸送しておらず、induced graph transformも
定義していない。従ってself-map、contraction、fixed graph、exact invariant manifold／SSMは未認証である。

停止規則どおり、次はQ011rを事前登録し、Q011mのanalytic derivative majorantをQ011qのreal normへ移し、
localized nonlinear graph transformの定義、self-map、contractionだけを独立に判定する。

## Q011r: real-norm nonlinear graph transform — 事前登録

### 問い

Q011mのanalytic $D^2\Phi/D^3\Phi$ boundをQ011qのreal fixed-leaf coordinate normへ厳密に輸送し、
radial cutoffで局所化した写像が、明示したcomplete real graph space上でwell-definedなgraph transformを与え、
self-mapかつstrict contractionになる有限radiusを認証できるか。

本gateはQ011qで未定義だった**非線形graph transformそのもの**だけを扱う。acceptedでも、localized mapの
fixed graphをoriginal mapのforward-invariant core germへ移す評価、smoothness、SSM uniqueness、normal
attraction、basinは次の独立gateへ残す。

### 封印入力

次の2 artifactを直接照合する。Q011qのnested sealだけでQ011mの直接照合を代用しない。

- Q011m artifact／runner newline-normalized SHA-256:
  `b76b0ec1a1436aa3c2b48fcc29485e60e03675bf9a1f4f85ac3106d30687da3f` /
  `0cdc6ec9697d25bea3b28cf90f01f3f639062b3c04a64c4a88e6bd7221163150`
- Q011m input／derivative／coefficient／majorant／result digest:
  `dd30ead5c7c6081502bc34a6163ce64321dd4f9a339c7f24959dfc76891591cb` /
  `0b8f345fdf2bda5b95f2c1624920968f1ad499f4d5e765c0b8305e2045ac7e3a` /
  `1d708042f97c8c42164b07ff7104a68bdef95c14faf90dcb0171749d92b8a514` /
  `bf7144f407dd3e6aabf2161bf3d8c48dbb2e6c89a48cde9cfccf1cff60455e00` /
  `f47a1a4c1712fcff129c3840d7e64dfe1bbbe4bdacc049e28be6f868dbfc9cd4`
- Q011q artifact／runner newline-normalized SHA-256:
  `776be2af80fdbb867fd72eb3c0bdfe82ca30f5fa50bc9436818df5c7f87e676d` /
  `83031650f7ecd54adb048a74ace2df96068317531aeb84fb57b9f797b9e33f67`
- Q011q input／conjugation／frame／setup／result digest:
  `c9e57c60fe678901c5502bf163d7317c06fedb35322e8591e741c330969829b5` /
  `583a28e1453b75700d0674bf090c4f8c0652d7538f84bef7c8ea7e09415db54e` /
  `1210f4d2c85d4a0cad9978531b297b5e493bac5f8d54d5eafa6ee7a5a68a6d7b` /
  `ec52daadd80261b9e94672beb979fd5f01e4f1c4bc0e63090a0cccbb90cda26b` /
  `274ddd32b50000c953c623285993ba533651a720c6dc79ae693a0e24a3f623ae`

両artifactの`accepted`、theorem consequence、claim boundaryを再現する。Q011mのexact conserved-moment
identitiesにより、二次・三次非線形出力がfixed conservation leafに属することも直接確認する。

### analytic derivative boundのreal coordinateへの輸送

Q011qのreal coordinate synthesis／analysisを $L_{\mathbb R},P_{\mathbb R}$ とし、

\[
\lVert L_{\mathbb R}\rVert\le K_L,
\qquad
\lVert P_{\mathbb R}\rVert\le K_P
\]

を同じcomplex-modulus block-sup normのreal restrictionで用いる。Q011mのphysical population
infinity-norm boundを $M_2,M_3$ とし、coordinate map

\[
F_{\mathbb R}(z)=A_{\mathbb R}z+N_{\mathbb R}(z)
\]

について

\[
\mu_2=K_P M_2 K_L^2,
\qquad
\mu_3=K_P M_3 K_L^3
\]

を登録する。normalized forward DFTのanalysis constant `1`、inverse DFTのblock-sum synthesis、Q011mの
streaming／filter nonexpansivityをこの式の根拠とし、未包絡のbinary64 normを使わない。

exact rootで $N_{\mathbb R}(0)=0$、$DN_{\mathbb R}(0)=0$ であることを再現する。radius $\rho$ で
$K_L\rho\le10^{-4}$なら、Taylorの積分形から

\[
\sup_{\lVert z\rVert\le\rho}\lVert N_{\mathbb R}(z)\rVert
\le n_\rho:=\frac12\mu_2\rho^2,
\qquad
\sup_{\lVert z\rVert\le\rho}\lVert DN_{\mathbb R}(z)\rVert
\le\mu_2\rho
\]

を得る。transported $\mu_3$ は独立provenanceとして保存するが、このself-map／contraction boundを
見かけ上鋭くするためには使わない。

### radial cutoff後のglobal nonlinear bound

Q011qと同じblockwise radial retraction $C_\rho$ を各candidate radiusで再発行し、

\[
N_\rho=N_{\mathbb R}\circ C_\rho
\]

とする。$C_\rho$ は両real fixed spaceを保ち、global Lipschitz upper `2`である。従って

\[
\lVert N_\rho\rVert_\infty\le n_\rho,
\qquad
\operatorname{Lip}(N_\rho)\le
\delta_\rho:=2\mu_2\rho
\]

を用いる。amplitude boundへcutoff Lipschitz factor `2`を重ねて掛けず、difference boundには必ず掛ける。

### complete global bounded graph space

Q011qのlocal graphを無証明に延長する代わりに、最初から

\[
\mathscr G_{\rho,1}
=\left\{
\psi:S_{\mathbb R}\to E_{\mathbb R}:
\psi(0)=0,
\sup_s\lVert\psi(s)\rVert\le\rho,
\operatorname{Lip}(\psi)\le1
\right\}
\]

を定義する。metricはglobal uniform metric

\[
d_\infty(\psi,\varphi)=
\sup_s\lVert\psi(s)-\varphi(s)\rVert
\]

とする。boundednessによりmetricは有限で、uniform limitがorigin、height、Lipschitz条件を保つためclosed
completeである。各 $\psi$ のselected radius-$\rho$ ballへのrestrictionはQ011qのlocal graph spaceに入る。
Q011qのradial extensionのLipschitz定数を暗黙に`1`へ改善しない。

### base inverseとgraph transformの定義

Q011qのreal upper-triangular linear splitを

\[
A_{\mathbb R}=
\begin{pmatrix}S&B\\0&E\end{pmatrix},
\qquad
m=m(S),\quad q=\lVert E\rVert,\quad b=\lVert B\rVert,
\quad \alpha=\lVert S^{-1}\rVert\le1/m
\]

とする。各 $\psi\in\mathscr G_{\rho,1}$ について

\[
P_\psi(s)=
Ss+B\psi(s)+(N_\rho)_S(s,\psi(s))
\]

を定義する。

\[
d_\rho:=m-b-\delta_\rho>0,
\qquad
u_\rho:=\alpha(b+\delta_\rho)<1
\]

なら、任意のbase output $u$ に対する

\[
s=S^{-1}\{u-B\psi(s)-(N_\rho)_S(s,\psi(s))\}
\]

はstrict contractionであり、$P_\psi$ はglobal bijection、
$\operatorname{Lip}(P_\psi^{-1})\le1/d_\rho$ である。有限次元性だけでsurjectivityを推測せず、
このfixed-point inverseを明示する。

graph transformを

\[
(\mathcal T_\rho\psi)(u)=
E\psi(P_\psi^{-1}u)
+(N_\rho)_E\left(P_\psi^{-1}u,
\psi(P_\psi^{-1}u)\right)
\]

と固定する。origin固定、real typing、domain／codomainを監査する。

### self-mapとcontraction majorant

height、slope、uniform contractionをそれぞれ

\[
h_\rho=q+\frac{n_\rho}{\rho}
=q+\frac12\mu_2\rho,
\]

\[
\ell_\rho=
\frac{q+\delta_\rho}{d_\rho},
\]

\[
\kappa_\rho=
(q+\delta_\rho)
\left(1+\frac{b+\delta_\rho}{d_\rho}\right)
=\frac{m(q+\delta_\rho)}{d_\rho}
\]

で包絡する。self-mapには $h_\rho\le1$、$\ell_\rho\le1$ を要求する。

uniform contractionでは、同じoutput $u$ のpreimage差を

\[
\lVert P_\psi^{-1}u-P_\varphi^{-1}u\rVert
\le\frac{b+\delta_\rho}{d_\rho}
d_\infty(\psi,\varphi)
\]

で評価し、$\kappa_\rho<1$ を要求する。eigenvalue gap、Q011pのRiccati contraction、Q007系列の
normal-fiber contractionをこの式へ代入しない。

### radius campaignと登録cap

candidate radiusを昇順に

\[
10^{-18},3\!\times\!10^{-18},10^{-17},3\!\times\!10^{-17},
10^{-16},3\!\times\!10^{-16},10^{-15},3\!\times\!10^{-15},
10^{-14},3\!\times\!10^{-14},10^{-13},3\!\times\!10^{-13},
10^{-12},3\!\times\!10^{-12},10^{-11}
\]

に固定し、全条件を満たす最大candidateを選ぶ。candidate間の連続最適化や事後のradius追加は行わない。
最低受理radiusは`1e-16`とする。selected candidateで次をすべて要求する。

- $\mu_2\le10^{12}$、$\mu_3\le10^{17}$
- $K_L\rho\le10^{-4}$、population／density bufferはQ011m thresholdを通過
- $\delta_\rho\le10^{-3}$
- base inverse utilization $u_\rho\le10^{-2}$
- height ratio $h_\rho\le0.99$
- graph slope upper $\ell_\rho\le0.999$
- uniform graph-transform contraction $\kappa_\rho\le0.99$
- 最初のより大きいcandidateが失敗する場合、その最初のfailed conditionを保存

全式はexact `Fraction`で計算する。各majorantがnondecreasing、$d_\rho$がnonincreasingであることを
代数的に確認し、最大passing candidateの選択を再現可能にする。

### validity gate

1. Q011m／Q011qのartifact、runner、10 digest、outcome、theorem consequence、claim boundaryを直接再現する。
2. physical $M_2,M_3$、real $K_L,K_P$、fixed-leaf conserved-moment identityから
   $\mu_2,\mu_3$ の輸送式をexactに再現する。
3. $N(0)=DN(0)=0$、Taylor amplitude／derivative、radial cutoff後の $n_\rho,\delta_\rho$ を再現する。
4. global bounded graph spaceのreal typing、finite uniform metric、closed completenessを確認する。
5. base fixed-point inverse、$d_\rho,u_\rho$、graph transformのdomain／codomainを式どおり再現する。
6. 15 radiusについてheight、slope、contraction、domain、bufferをexactに全列挙し、monotonicityを確認する。
7. finite性、strict JSON、input／transport／radius／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、graph transformの成否を解釈しない。

### hypothesis gateと停止規則

validity通過後、次の5項目を別々に要求する。

1. transported $\mu_2,\mu_3$ が登録cap内で、少なくとも一つのcandidateがderivative domainとbufferを通る。
2. 最大passing candidateが`1e-16`以上で、$\delta_\rho,u_\rho,h_\rho$ の登録capを通る。
3. base mapがglobal bijectionとして定義され、inverse Lipschitz boundが有限である。
4. graph transformが $\mathscr G_{\rho,1}$ のself-mapで、slope upperが`0.999`以下である。
5. uniform metric contraction upperが`0.99`以下である。

全5項目が通る場合だけ
`the registered real localized graph transform is a strict contraction at a certified finite radius`
として`accepted`とする。一つでも落ちれば
`the transported Q011m majorant does not certify the Q011q nonlinear graph transform on the registered radius grid`
として`rejected`とする。rejectedはgraph transformやinvariant manifold／SSMの不存在を意味せず、最初の
failed radius conditionだけを使ってsectorwise derivative transport、block weight、cutoff、またはradius gridの
うち一つを次gateで変更する。

`accepted`なら次のQ011sで、localized fixed graphのcore restrictionとoriginal exact mapの一致、selected
base imageのinner-ball containmentを事前登録し、nonzero original-map invariant graph germへ移せるかを判定する。
`inconclusive`なら最初のseal／transport／typing／inverse／serialization failureだけを修復する。

### 主張境界

本gateは固定17² repaired exact map、fixed-conservation leaf、Q011q real split、Q011m derivative domain、
登録15 radius、radially localized map、global bounded Lipschitz graph spaceに限る。selected radiusの最適性、
original mapのinvariant manifold／SSM、$C^1$以上のsmoothness、spectral quotient uniqueness、normal
attraction、basin、長時間trajectory、他grid／force／wall、D3Q27を構成・認証しない。

### Q011r 実行結果

validity `7 / 7`、hypothesis `5 / 5`を通過し、
`the registered real localized graph transform is a strict contraction at a certified finite radius`
として`accepted`とした。

Q011m／Q011qの2 artifact、runner、10 digest、outcome、theorem consequence、claim boundaryを直接再現した。
Q011mのfixed-leaf conserved-moment identityを使ってnonlinear outputがreal coordinate analysisのdomainに
入ることを確認し、

\[
\mu_2=K_P M_2 K_L^2,
\qquad
\mu_3=K_P M_3 K_L^3
\]

をexact `Fraction`で評価した。

- transported \(\mu_2\): `855561732369.8289`
- transported \(\mu_3\): `5.96467973853591e16`
- registered radius count／passing count: `15 / 6`
- selected radius: `3e-16`
- first failed larger radius: `1e-15`
- first failed larger conditions:
  `localized_nonlinear_lipschitz_fits_cap / graph_slope_fits_cap`

selected radiusでは

- physical state radius: `7.73156346265492e-13`
- nonlinear amplitude $n_\rho$: `3.85002779566423e-20`
- localized nonlinear Lipschitz \(\delta_\rho\): `0.0005133370394218973`
- base conorm $d_\rho$: `0.9832575980864989`
- base inverse utilization $u_\rho$: `0.0005218265861057217`
- base inverse Lipschitz upper: `1.0170274828753758`
- height ratio $h_\rho$: `0.981838190392355`
- graph slope \(\ell_\rho\): `0.9989479817734533`
- uniform contraction \(\kappa_\rho\): `0.9827360109495584`
- population／density floor: `0.027775908312577136 / 0.9999999999924095`

となり、すべての登録capを通った。passing setは登録候補の先頭6個とexactに一致し、全majorantの
monotonicityも通過した。第三微分boundはtransport provenanceとして保存したが、self-map／contractionを
事後に鋭く見せる項としては使用していない。

- input／transport／graph／radius／result digest:
  `7e9fa7b147ede559cffd117b7a6b8592d2939774f9821494759bbf3d634badd2` /
  `3b8fba9cd370521880be3d4b77a9e2fc715e67ac22dc78e631f96e0d71317191` /
  `77f2ac35d83726d0868ab08dd7648aee26bed7b00a40fb1405df1e1f162e023b` /
  `8d33d01931c42730b18778c674282e6870224336cca72f66e81b447178d32d79` /
  `b0520673f844d3f94a735c27800ff40d025a9437b01899e3d400b3c3fe0661ea`
- runner／artifact newline-normalized SHA-256:
  `8169e2fc7d5f7dccdc424bba31f37d4c03e6a669ab2e3f04d6289f03240b6d09` /
  `2d45e3c64965ee1e8bc47f1a7d75070fbeabbcb2711a62b1711da92878a58e11`

これによりradially localized mapには登録graph space内で一意なbounded Lipschitz fixed graphが存在する。
ただし、original mapとlocalized mapが一致するのはcutoff core内だけであり、fixed graphのcore restrictionと
そのselected base imageが同時にcoreへ留まることはまだ示していない。従ってoriginal-map local invariant
manifold／SSM、$C^1$以上のsmoothness、normal attraction、basinは未認証である。

停止規則どおり、次はQ011sを事前登録し、selected operator upper、fixed-graph height／slope、nonlinear
amplitudeからinner base radiusを構成し、そのgraph patchとone-step imageがcutoff identity regionに留まるか
だけを判定する。

## Q011s: original-map invariant Lipschitz core — 事前登録

### 問い

Q011rが構成したlocalized mapの一意なbounded Lipschitz fixed graphについて、入力graph patchとそのone-step
imageがともにradial cutoffのidentity coreへ留まるinner base radiusを認証し、original repaired exact mapの
fixed-conservation leaf上のforward-invariant Lipschitz graph patchへ移せるか。

本gateはlocalized fixed graphからoriginal mapへの**core transfer**だけを扱う。$C^1$ smoothness、originでの
tangency、SSMとしてのspectral-quotient uniqueness、normal attraction、basinは判定しない。

### 封印入力

selected operator upperをQ011rのnested sealから推測せず、次の4 artifactを直接照合する。

- Q011k artifact／runner newline-normalized SHA-256:
  `8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a` /
  `d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07`
- Q011k input／root／block／proof／result digest:
  `f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2` /
  `f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc` /
  `7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8` /
  `1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4` /
  `2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e`
- Q011l artifact／runner newline-normalized SHA-256:
  `2878d8ebaaedc29990700ccac25b78185e0b6139dd371521f14602caf4514c0a` /
  `59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7`
- Q011l input／graph／pair／homological／result digest:
  `1810f989a0328521e8b6d6ccbc2153cb9a945bb2c129c70d7b25a0c227fc7011` /
  `a7d0f320fa7391c506f42853a94ede66fc73e81b004dfccda144028082cb8db3` /
  `694cc2955bcef05df13ad30582f46f84bb627aaa7b336b5278e9b5139e29d377` /
  `14d67f1d915aa3bd6bc34117562da4908e19036943e60fb638eddf6a42b20915` /
  `c372aa5962a7f3d0c83a126303a9e36e4f0830d113f9c49b922d03beb2f09a45`
- Q011q artifact／runner newline-normalized SHA-256:
  `776be2af80fdbb867fd72eb3c0bdfe82ca30f5fa50bc9436818df5c7f87e676d` /
  `83031650f7ecd54adb048a74ace2df96068317531aeb84fb57b9f797b9e33f67`
- Q011q input／conjugation／frame／setup／result digest:
  `c9e57c60fe678901c5502bf163d7317c06fedb35322e8591e741c330969829b5` /
  `583a28e1453b75700d0674bf090c4f8c0652d7538f84bef7c8ea7e09415db54e` /
  `1210f4d2c85d4a0cad9978531b297b5e493bac5f8d54d5eafa6ee7a5a68a6d7b` /
  `ec52daadd80261b9e94672beb979fd5f01e4f1c4bc0e63090a0cccbb90cda26b` /
  `274ddd32b50000c953c623285993ba533651a720c6dc79ae693a0e24a3f623ae`
- Q011r artifact／runner newline-normalized SHA-256:
  `2d45e3c64965ee1e8bc47f1a7d75070fbeabbcb2711a62b1711da92878a58e11` /
  `8169e2fc7d5f7dccdc424bba31f37d4c03e6a669ab2e3f04d6289f03240b6d09`
- Q011r input／transport／graph／radius／result digest:
  `7e9fa7b147ede559cffd117b7a6b8592d2939774f9821494759bbf3d634badd2` /
  `3b8fba9cd370521880be3d4b77a9e2fc715e67ac22dc78e631f96e0d71317191` /
  `77f2ac35d83726d0868ab08dd7648aee26bed7b00a40fb1405df1e1f162e023b` /
  `8d33d01931c42730b18778c674282e6870224336cca72f66e81b447178d32d79` /
  `b0520673f844d3f94a735c27800ff40d025a9437b01899e3d400b3c3fe0661ea`

4 artifactの`accepted`、theorem consequence、claim boundaryを再現する。Q011rからselected radius
$\rho_*$、fixed-graph slope upper $\ell_*$、coordinate second derivative $\mu_2$、Q011qからreal coupling
$b$とphysical lift $K_L$を直接取り出す。

### selected linear operator upperの再構成

Q011kのexact dyadic center、Q011lのselected index／graph radius／same-norm residualを再構成する。
selected block $n\in\{0,1,16\}$ について、各selected centerのexact rational modulus upperを列挙し、

\[
p_{S,n}
=\max_{j\in I_{S,n}}|\lambda_{n,j}|_{\rm upper}
+\theta_n(1+r_{G,n})
\]

とする。global selected operator upperは

\[
p_S=\max_{n\in\{0,1,16\}}p_{S,n}
\]

とする。全24 selected centerを数え、block `1 / 16`のexact conjugacy、Q011oと同じ
complex absolute row-sum norm、Q011q real restrictionであることを確認する。eigenvalue modulusだけ、selected
conorm lower、external normをoperator upperの代用にしない。Q011qのzero-block real shearはselected diagonal
block $S$を変更せず、couplingだけをQ011qのreal bound $b$へ置き換える。

### localized fixed graphのrefined slope

Q011rのcomplete graph spaceでBanach fixed pointを $\psi_*$ とする。Q011r graph transformは任意の入力graphを
slope upper $\ell_*$ 以下へ写すため、fixed-point identityから

\[
\psi_*(0)=0,
\qquad
\operatorname{Lip}(\psi_*)\le\ell_*<1,
\qquad
\lVert\psi_*(s)\rVert\le\ell_*\lVert s\rVert
\]

を使う。global height cap $\rho_*$だけでlocal heightを評価せず、origin固定とrefined slopeを明示的に使う。
componentwise fixed graphは構成しない。

### core patchとoriginal mapへのtransfer

scale candidatesを

\[
1,\frac12,\frac14,\frac18,\frac1{16},\frac1{32},
\frac1{64},\frac1{128},\frac1{256},\frac1{512},\frac1{1024}
\]

に固定し、$r=\sigma\rho_*$ とする。graph patchを

\[
\mathcal M_r
=\{(s,\psi_*(s)):\lVert s\rVert\le r\}
\]

と定義する。$\ell_*<1$なので、各入力はfull coordinate normで$r\le\rho_*$に入り、Q011q radial cutoffは
identityである。従って入力上でlocalized map $F_{\rho_*}$ とoriginal coordinate map $F$ はexactに一致する。

selected image $u=P_{\psi_*}(s)$ には、cutoff factorを重ねず、core Taylor boundを用いて

\[
\lVert u\rVert
\le
\left(p_S+b\ell_*+\frac12\mu_2 r\right)r
=c_r r
\]

を登録する。fixed-graph invarianceからexternal imageは $\psi_*(u)$ であり、

\[
\lVert\psi_*(u)\rVert
\le\ell_*c_r r.
\]

$c_r\le1$ならfull imageもradius $r$のcore内にあり、

\[
F(\mathcal M_r)=F_{\rho_*}(\mathcal M_r)
\subseteq\mathcal M_r
\]

が従う。同じ包含を帰納して、全forward iterateがoriginal mapとlocalized mapで一致しcoreに留まることを
記録する。backward invarianceやpatchへのonto性は主張しない。

### physical fixed-leaf graph patch

Q011qのreal coordinate liftを $L_{\mathbb R}$、exact repaired rootを $x_*$ とし、

\[
\mathcal W_r
=x_*+L_{\mathbb R}\mathcal M_r
\]

とする。Q011q coordinate bijectivityとQ011m conserved-moment identityから、これはfixed conservation leaf内の
24-real-dimensional Lipschitz graph patchである。input／output physical displacementを

\[
K_L r,
\qquad
K_L c_r r
\]

で包絡し、population／density floorを再評価する。

### 登録cap

11 scaleをexact `Fraction`で全列挙し、全条件を満たす最大$r$を選ぶ。selected core radiusは少なくとも
$\rho_*/16$を要求する。candidate間の最適化や事後追加は行わない。

- selected center record count: `24`、selected blocks: `0 / 1 / 16`
- global selected operator upper $p_S\le0.993$
- fixed graph slope upper $\ell_*\le0.999$
- input／output physical displacement upper: 各`1e-11`
- core selected-image ratio $c_r\le0.999$
- external image ratio $\ell_*c_r\le0.999$
- population floor `>=0.02`、density floor `>=0.99`
- selected core radius $r\ge\rho_*/16$

$c_r$とphysical displacementは$r$に対してnondecreasing、population／density floorはnonincreasingであることを
exactに確認する。full radiusが通っても、$\rho_*$より大きいradiusやradius最適性は主張しない。

### validity gate

1. Q011k／Q011l／Q011q／Q011rのartifact、runner、20 digest、outcome、claim boundaryを直接再現する。
2. Q011k／Q011lから全24 selected modulus upper、same-norm residual、3 block operator upperを再構成する。
3. Q011q real shearがselected diagonalを保ち、real coupling $b$だけがcore boundへ入ることを確認する。
4. Q011r fixed graphのorigin、height、refined slopeとlocalized invarianceを再現する。
5. cutoff identity、original/localized equality、selected/external image bound、one-step core containmentを再現する。
6. 11 scaleのexact record、monotonicity、最大passing candidate、最初のlarger failureを再現する。
7. finite性、strict JSON、input／linear／core／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、original-map graph patchを解釈しない。

### hypothesis gateと停止規則

validity通過後、次の5項目を別々に要求する。

1. 全24 selected centerから得たsame-norm $p_S$が`0.993`以下である。
2. Q011r fixed graphのradius、origin、refined slopeがcore transferへ使用可能である。
3. 最大passing core radiusが$\rho_*/16$以上で、input graph patchがcutoff identity coreとphysical bufferに入る。
4. $c_r\le0.999$、$\ell_*c_r\le0.999$で、one-step full imageが同じcoreとbufferに入る。
5. exact original mapが24-real-dimensional Lipschitz graph patchをforward invariantに保つ。

全5項目が通る場合だけ
`the original repaired exact map has a certified forward-invariant Lipschitz graph patch on the fixed conservation leaf`
として`accepted`とする。一つでも落ちれば
`the Q011r localized fixed graph does not remain in the cutoff core on the registered inner-radius grid`
として`rejected`とする。rejectedはoriginal invariant manifold／SSMの不存在を意味せず、最初のfailed
operator／slope／core／buffer conditionだけを次gateで修正する。

`accepted`なら次のQ011tで、fixed graphの$C^1$ graph-transform space、origin derivative、selected tangent、
spectral quotient条件を事前登録し、Lipschitz graph patchをsmooth invariant manifold／SSM claimへ強化できるか
を判定する。`inconclusive`なら最初のseal／linear reconstruction／core formula／serialization failureだけを
修復する。

### 主張境界

本gateは固定17² repaired exact map、fixed-conservation leaf、Q011r localized fixed graph、登録11 inner scales、
forward-invariant Lipschitz graph patchに限る。backward invariance、patchへのonto性、$C^1$以上のsmoothness、
origin tangency、SSM／spectral quotient uniqueness、normal attraction、basin、他grid／force／wall、D3Q27を
構成・認証しない。

### Q011s 実行結果

Q011k／Q011l／Q011q／Q011rの4 artifact、4 runner、20 digestを直接封印し、validity `7 / 7`を通過した。
全24 selected centerからsame-norm operator upperを再構成し、

\[
(p_{S,0},p_{S,1},p_{S,16})
=
(0.9920954876550455,\,
0.9920954684013225,\,
0.9920954684013225)
\]

を得た。global witnessはblock `0`で、登録cap \(p_S\le0.993\)を通過した。blocks `1 / 16`はexact
conjugateで同じupperを持つ。Q011q real shearがselected diagonalを保つことと、real coupling
\(b=2.080001889821235\times10^{-8}\)を別に使うことも再現した。

Q011r fixed graphのrefined slope

\[
\ell_*=0.9989479817734533
\]

とorigin固定を使い、11個の登録scaleをexact `Fraction`で全評価した。`11 / 11` candidateが通過し、最大の
\(\sigma=1\)、\(r=\rho_*=3\times10^{-16}\)を選んだ。このとき

\[
c_r=0.9922238426930379,
\qquad
\ell_*c_r=0.9911800051257107
\]

であり、input graph patchとone-step full imageはともに同じcutoff identity coreへ留まる。input／output
physical displacement upperは

\[
7.731563462654924\times10^{-13},
\qquad
7.671441608940559\times10^{-13}
\]

で、output population／density floorは
`0.02777590831258315 / 0.9999999999924637`だった。

hypothesis `5 / 5`を通過し、

`the original repaired exact map has a certified forward-invariant Lipschitz graph patch on the fixed conservation leaf`

として`accepted`とした。original mapとlocalized mapはpatch上でexactに一致し、one-step inclusionを帰納して
全forward iterateがcoreに留まる。graph patchはfixed conservation leaf上の24-real-dimensional Lipschitz
graphである。

- input／linear／graph／core／result digest:
  `4808619d977f8d14c4f8b454e846558ad047337e4343c6b9bef791e2c2b99af5` /
  `6a657463b847ce242346aea8b582f1f4e108b0abb0935e270a5c03c1ceb3cc36` /
  `b9837d31b26bced4243457e3357a93c8d546883390104f1b43d5e182e92f98a7` /
  `ab837deb8459678d4fce223e06d03cc8e6f4d391ff35bad191392a923825e622` /
  `3e01d86f279bc6c5a2f0769a9728a98e3e49fa749be15a2c6c6e0f32132ca270`
- runner／artifact newline-normalized SHA-256:
  `beeeb6699b5c3a7e7636b2c7afd6036bc6959213e81339f39961c325d9347367` /
  `d7399671504cc513aecc491210108c31365c63a74864ecf04e629b3d1348bc52`

これはforward-invariant Lipschitz graph patchの認証であり、backward invariance、patchへのonto性、
\(C^1\)以上のsmoothness、origin tangency、spectral-quotient SSM uniqueness、normal attraction、basin、
\(\rho_*\)より大きいradiusの最適性は認証していない。

停止規則どおり、次はQ011tを事前登録し、\(C^1\) graph-transform space、origin derivative equation、
selected tangency、spectral quotientを同じfixed-leaf real normで判定する。

## Q011t: C1-localized tangent graph patch — 事前登録

### 問い

Q011qのreal fixed-leaf coordinate上にscalar \(C^1\) localizationを新たに定義し、Q011mのanalytic derivative
boundを用いたgraph transformとderivative-fiber transformを同時にstrict contractionにできるか。そのfixed
graphのinner patchをoriginal repaired exact mapへ移し、originでselected real spectral subspaceに接する
\(C^1\) forward-invariant graph patchを認証できるか。

Q011rのradial retractionは境界で\(C^1\)ではないため、そのLipschitz fixed graphが自動的にsmoothであるとは
仮定しない。本gateは別の\(C^1\)-localized mapからoriginal-map \(C^1\) graph patchを構成する。Q011s graphとの
集合としての一致や、spectral-quotient SSM uniquenessは別判定とする。

### 封印入力

次の5 artifactを直接照合し、nested sealだけで代用しない。

- Q011k artifact／runner newline-normalized SHA-256:
  `8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a` /
  `d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07`
- Q011k input／root／block／proof／result digest:
  `f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2` /
  `f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc` /
  `7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8` /
  `1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4` /
  `2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e`
- Q011m artifact／runner newline-normalized SHA-256:
  `b76b0ec1a1436aa3c2b48fcc29485e60e03675bf9a1f4f85ac3106d30687da3f` /
  `0cdc6ec9697d25bea3b28cf90f01f3f639062b3c04a64c4a88e6bd7221163150`
- Q011m input／derivative／coefficient／majorant／result digest:
  `dd30ead5c7c6081502bc34a6163ce64321dd4f9a339c7f24959dfc76891591cb` /
  `0b8f345fdf2bda5b95f2c1624920968f1ad499f4d5e765c0b8305e2045ac7e3a` /
  `1d708042f97c8c42164b07ff7104a68bdef95c14faf90dcb0171749d92b8a514` /
  `bf7144f407dd3e6aabf2161bf3d8c48dbb2e6c89a48cde9cfccf1cff60455e00` /
  `f47a1a4c1712fcff129c3840d7e64dfe1bbbe4bdacc049e28be6f868dbfc9cd4`
- Q011q artifact／runner newline-normalized SHA-256:
  `776be2af80fdbb867fd72eb3c0bdfe82ca30f5fa50bc9436818df5c7f87e676d` /
  `83031650f7ecd54adb048a74ace2df96068317531aeb84fb57b9f797b9e33f67`
- Q011q input／conjugation／frame／setup／result digest:
  `c9e57c60fe678901c5502bf163d7317c06fedb35322e8591e741c330969829b5` /
  `583a28e1453b75700d0674bf090c4f8c0652d7538f84bef7c8ea7e09415db54e` /
  `1210f4d2c85d4a0cad9978531b297b5e493bac5f8d54d5eafa6ee7a5a68a6d7b` /
  `ec52daadd80261b9e94672beb979fd5f01e4f1c4bc0e63090a0cccbb90cda26b` /
  `274ddd32b50000c953c623285993ba533651a720c6dc79ae693a0e24a3f623ae`
- Q011r artifact／runner newline-normalized SHA-256:
  `2d45e3c64965ee1e8bc47f1a7d75070fbeabbcb2711a62b1711da92878a58e11` /
  `8169e2fc7d5f7dccdc424bba31f37d4c03e6a669ab2e3f04d6289f03240b6d09`
- Q011r input／transport／graph／radius／result digest:
  `7e9fa7b147ede559cffd117b7a6b8592d2939774f9821494759bbf3d634badd2` /
  `3b8fba9cd370521880be3d4b77a9e2fc715e67ac22dc78e631f96e0d71317191` /
  `77f2ac35d83726d0868ab08dd7648aee26bed7b00a40fb1405df1e1f162e023b` /
  `8d33d01931c42730b18778c674282e6870224336cca72f66e81b447178d32d79` /
  `b0520673f844d3f94a735c27800ff40d025a9437b01899e3d400b3c3fe0661ea`
- Q011s artifact／runner newline-normalized SHA-256:
  `d7399671504cc513aecc491210108c31365c63a74864ecf04e629b3d1348bc52` /
  `beeeb6699b5c3a7e7636b2c7afd6036bc6959213e81339f39961c325d9347367`
- Q011s input／linear／graph／core／result digest:
  `4808619d977f8d14c4f8b454e846558ad047337e4343c6b9bef791e2c2b99af5` /
  `6a657463b847ce242346aea8b582f1f4e108b0abb0935e270a5c03c1ceb3cc36` /
  `b9837d31b26bced4243457e3357a93c8d546883390104f1b43d5e182e92f98a7` /
  `ab837deb8459678d4fce223e06d03cc8e6f4d391ff35bad191392a923825e622` /
  `3e01d86f279bc6c5a2f0769a9728a98e3e49fa749be15a2c6c6e0f32132ca270`

5 artifactの`accepted`、theorem consequence、claim boundaryを再現する。Q011rから
\(\mu_2,m,q,b,\alpha,\rho_*\)、Q011sから\(p_S\)とphysical／root bufferを直接取り出す。

### scalar C1 localization

Q011q real fixed spaceを2598個のcomplex-coordinate slotの共役固定部分空間として扱い、そのglobal
complex-modulus block-sup normを使う。scale \(r\)ごとに

\[
t_r(z)=\sum_{j=1}^{2598}
\left(\frac{|z_j|}{2r}\right)^{16}
\]

とし、

\[
\chi(t)=
\begin{cases}
1,&t\le1,\\
1-3y^2+2y^3,\quad y=(t-1)/3,&1<t<4,\\
0,&t\ge4
\end{cases}
\]

および

\[
C_r^{(1)}(z)=\chi(t_r(z))z
\]

を定義する。\(\chi\)はendpoint derivativeが0の\(C^1\) scalar bumpで、
\(0\le\chi\le1\)、\(|\chi'|\le1/2\)をexactに確認する。scalar multiplicationと全slotの対称和により、
selected／external real fixed spacesとconjugacyを保つ。

\[
\frac{2598}{2^{16}}<1
\]

なので\(\|z\|\le r\)ではidentityである。support上は\(\|z\|<4r\)であり、
\(2598^{1/16}\le2\)、\(t^{15/16}\le4\)を用いて

\[
\|DC_r^{(1)}(z)\|\le129
\]

を登録する。componentwise complex disk projectionやQ011rのnonsmooth radial retractionは使わない。

### C1-localized nonlinear majorant

\[
N_r^{(1)}(z)=N(C_r^{(1)}z)
\]

とする。Q011mの\(N(0)=DN(0)=0\)とQ011rのreal-norm \(\mu_2\)から、

\[
n_r=8\mu_2r^2,
\qquad
\delta_r=516\mu_2r
\]

をglobal amplitude／derivative upperとして登録する。前者はsupport radius \(4r\)、後者は
\(\|DC_r^{(1)}\|\le129\)を一度ずつ使う。cutoff factorを重複適用しない。

### C1 graph transformとderivative fiber

全selected real space上の\(C^1\) graph

\[
\psi:S_{\mathbb R}\to E_{\mathbb R},
\qquad
\psi(0)=0,
\qquad
\sup\|\psi\|\le r,
\qquad
\sup\|D\psi\|\le1
\]

を\(C_b^1\) normで完備化する。Q011rと同じupper-triangular linear splitを用い、

\[
d_r=m-b-\delta_r,
\qquad
u_r=\alpha(b+\delta_r),
\qquad
h_r=q+8\mu_2r
\]

とする。base inverseはglobal fixed-point inverseと\(C^1\) inverse function theoremを合成する。
graph-transform derivativeは

\[
D(\mathcal T_r\psi)(u)
=
\left[D_sg+D_eg\,D\psi(s)\right]
\left[D_sf+D_ef\,D\psi(s)\right]^{-1},
\qquad
s=P_\psi^{-1}(u)
\]

で定義する。self-map slope、base-graph contraction、derivative-fiber contractionを

\[
\ell_r=\frac{q+\delta_r}{d_r},
\qquad
\kappa_r=\frac{m(q+\delta_r)}{d_r},
\]

\[
\chi_r
=
\frac{q+\delta_r}{d_r}
+\frac{(q+\delta_r)(b+\delta_r)}{d_r^2}
\]

で包絡する。C0 graph transformのcontractionと、各base graph上のuniform fiber contractionを
fiber-contraction theoremで合成し、\(C^1\) fixed graphを得る。direct \(C^1\)-norm contractionを仮定しない。

originでは\(DN(0)=0\)かつlower-left linear blockが0なので、derivative fiberは\(H=0\)を固定する。
\(\chi_r<1\)によるfiber fixed pointの一意性から

\[
D\psi_*(0)=0
\]

を結論し、physical tangentをQ011q lift of selected real spectral subspaceとして記録する。

### 登録scaleとoriginal-map transfer

\[
r_j=2^{-j}\rho_*,
\qquad
j=6,7,\ldots,16
\]

の11候補をexact `Fraction`で全列挙し、全条件を満たす最大\(r_j\)を選ぶ。fixed graphのrefined slope
\(\ell_{r_j}\)を使い、original coreでは

\[
c_j=p_S+b\ell_{r_j}+\frac12\mu_2r_j
\]

を再評価する。\(c_j\le1\)ならradius-\(r_j\) patchとその像はsmooth cutoffのidentity coreへ入り、
original mapと\(C^1\)-localized mapが一致する。physical support \(4K_Lr_j\)、input／output displacement、
population／density floorを別々に記録する。

### rigorous spectral-quotient diagnostic

Q011kの2598 eigencenterとBauer--Fike radiusからselected 24／external 2574のmodulus intervalを全再構成する。
selected spectral-radius enclosureを\([\rho_S^-,\rho_S^+]\)、external minimum-modulus enclosureを
\([\rho_E^-,\rho_E^+]\)とする。

- sufficient upper quotient:
  最小の\(L_+\)で\((\rho_S^+)^{L_++1}<\rho_E^-\)
- excluded lower quotient:
  \((\rho_S^-)^{L_-} \ge \rho_E^+\)からactual quotientが\(L_-\)以下でないことを示す

actual quotientを含む整数bracket、boundary ratios、witnessをexact rational powersで記録する。
登録capはbracket width `<=1`、conservative \(L_+\le90\)とする。Q011kが直接認証したexternal
nonresonanceはdegree `2`だけなので、degrees `3..L_+`をmissingとして全列挙する。従って本gateでは
spectral-quotient SSM uniquenessを主張しない。

### 登録cap

- coordinate slot count: `2598`、selected／external real dimension: `24 / 2574`
- smooth-cutoff identity ratio: \(2598/2^{16}<1\)
- smooth-cutoff support factor／derivative upper: `4 / 129`
- localized derivative upper \(\delta_r\le10^{-3}\)
- base inverse utilization \(u_r\le10^{-2}\)
- height ratio \(h_r\le0.99\)
- \(C^1\) graph slope \(\ell_r\le0.999\)
- C0 graph contraction \(\kappa_r\le0.99\)
- derivative-fiber contraction \(\chi_r\le0.9995\)
- support physical displacement \(4K_Lr\le10^{-11}\)
- original selected／external image ratio: each `<=0.999`
- population floor `>=0.02`、density floor `>=0.99`
- selected scale \(r/\rho_*\ge1/4096\)
- spectral quotient bracket width `<=1`、conservative upper `<=90`

### validity gate

1. Q011k／Q011m／Q011q／Q011r／Q011sのartifact、runner、25 digest、outcome、claim boundaryを直接再現する。
2. \(t_r,\chi,C_r^{(1)}\)の\(C^1\) typing、identity、support、real conjugacy、derivative `129` boundを再現する。
3. Q011m／Q011rから\(n_r,\delta_r\)を同じreal normで再現する。
4. \(C_b^1\) graph space、global \(C^1\) base inverse、graph derivative formula、fiber theoremの型を確認する。
5. 11 scaleのexact records、monotonicity、最大passing candidate、最初のlarger failureを再現する。
6. selected candidateのorigin derivative `0`、selected tangency、original/core equality、forward invarianceを再現する。
7. 2598 modulus interval、quotient bracket、boundary powers、degree-evidence inventoryを再現する。
8. finite性、strict JSON、input／cutoff／graph／radius／spectral／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、\(C^1\) graph patchを解釈しない。

### hypothesis gateと停止規則

validity通過後、次の6項目を別々に要求する。

1. scalar cutoffが両real spacesを保つglobal \(C^1\) localizationで、support／derivative cap内に入る。
2. 最大passing scaleでbase inverse、height、slope、C0 contractionが全capを通る。
3. derivative-fiber contractionが`0.9995`以下で、fiber theoremが\(C^1\) fixed graphを与える。
4. origin derivativeが0で、graph tangentがselected real spectral subspaceに一致する。
5. inner patchと像がidentity core／physical bufferへ入り、original exact mapでforward invariantである。
6. spectral quotientのrigorous bracketが登録幅／upper cap内に入り、missing degreeを残したままSSM uniquenessを
   主張していない。

全6項目が通る場合だけ
`the original repaired exact map has a certified C1 forward-invariant graph patch tangent to the selected real spectral subspace`
として`accepted`とする。一つでも落ちれば
`the registered C1 localization does not certify a tangent original-map graph patch`
として`rejected`とする。rejectedは\(C^1\) manifoldの不存在を意味せず、最初のcutoff／derivative／fiber／
core conditionだけを修正する。

`accepted`なら次のQ011uで、conservative quotientまでのhigher-smoothness localizationとdegrees
`3..L_+`のexternal nonresonance／homological evidenceを事前登録し、SSM uniquenessへ進めるか判定する。
`inconclusive`なら最初のseal／typing／formula／serialization failureだけを修復する。

### 主張境界

本gateは固定17² repaired exact map、fixed-conservation leaf、Q011q real coordinate、登録\(C^1\) scalar
localization、11 scales、24-real-dimensional forward-invariant \(C^1\) graph patchとorigin tangencyに限る。
Q011s fixed graphとの一致、backward invariance、patchへのonto性、\(C^2\)以上のsmoothness、
spectral-quotient SSM uniqueness、normal attraction、basin、optimal radius、他grid／force／wall、D3Q27を
構成・認証しない。

### Q011t 実行結果

5 direct artifact／25 digest、scalar \(C^1\) cutoff、\(C_b^1\) graph／derivative fiber、11 exact scale、
original-map transfer、2598 modulus interval、strict serializationのvalidity `8 / 8`を通過した。

- outcome: `accepted`
- hypothesis gates: `6 / 6` passed
- selected scale／radius: `1/256 / 1.171875e-18`
- first failed larger radius: `2.34375e-18`
- selected \(\delta_r/u_r/h_r\):
  `0.0005173474850423809 / 0.0005259031911287972 / 0.9817178770237405`
- selected \(\ell_r/\kappa_r/\chi_r\):
  `0.9989561349826355 / 0.9827440318399493 / 0.9994817656326567`
- original selected／external image ratio:
  `0.9920960097390545 / 0.991060395420621`
- spectral-radius／external-minimum enclosures:
  `[0.9920950744174255, 0.9921085054987441] / [0.4900847455855686, 0.4900855234175915]`
- rigorous spectral-quotient bracket: `[89,90]`
- directly certified／missing external nonresonance degrees: `{2} / {3,...,90}`

従ってoriginal repaired exact mapにはfixed conservation leaf上の24-real-dimensional forward-invariant
\(C^1\) graph patchがあり、originでselected real spectral subspaceに接する。ただしこれはQ011s graphとの
一致を示さず、\(C^2\)以上、degrees 3--90のexternal nonresonance、spectral-quotient SSM uniqueness、
normal attraction、basinも示さない。停止規則どおり、次はQ011uでhigher-smoothness localizationと
missing degrees 3--90のevidenceを事前登録する。

## Q011u: C91 localization and modulus-only degree-90 nonresonance — 事前登録

### 問い

Q011tのspectral-quotient upper `90`に対し、original repaired exact mapのanalyticity、登録した
\(C^{91}\) scalar localization、全selected／external eigendiscのrational log-modulusを用いて、degrees
3--90のexternal nonresonanceを組合せ完全に認証できるか。認証できる場合に限り、nonresonant spectral
subspace theoremからanalytic invariant manifoldと\(C^{91}\)-class uniquenessを結論できるか。

Q011tが与えた\(C^1\) graph patchを自動的に\(C^{91}\)へupgradeしたとは仮定しない。本gateで得る可能性が
あるhigher-smooth manifoldは、theoremが与える別のlocal germである。Q011t graphとの一致には、両者が同じ
uniqueness classに属する追加証明が必要である。

### 封印入力

次の4 artifactを直接照合し、nested sealだけで代用しない。

- Q011j artifact／runner newline-normalized SHA-256:
  `74a2e084137699739c14d980b05676e14e6802b4018b3893d3d05270850c2c5a` /
  `23a7a3a272264be3eb5330b2456192bd797aa968c4f795e2cbe8e337fc8fe4b5`
- Q011j input／coordinate／oracle／proof／result digest:
  `a183f4830c757b58122132cf64111fd5375636affdb6c0b31e1cd90e89085799` /
  `adaef353b8b64509334794c6014dc8b88e81ca2b776c3b65bd4d50911ae9452b` /
  `177468a48f667ddd922ed4b979d3e7e5d4cc0ed3afffe27a34651060da8e0f5f` /
  `1080fcea24358422514bba7fb9881928269c853cb4d12b0282e63840c56124c0` /
  `ddad5beca9693eeab726382ac864d01a27b749d579c2ec8f12dd9f8c499db934`
- Q011k artifact／runner newline-normalized SHA-256:
  `8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a` /
  `d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07`
- Q011k input／root／block／proof／result digest:
  `f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2` /
  `f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc` /
  `7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8` /
  `1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4` /
  `2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e`
- Q011m artifact／runner newline-normalized SHA-256:
  `b76b0ec1a1436aa3c2b48fcc29485e60e03675bf9a1f4f85ac3106d30687da3f` /
  `0cdc6ec9697d25bea3b28cf90f01f3f639062b3c04a64c4a88e6bd7221163150`
- Q011m input／derivative／coefficient／majorant／result digest:
  `dd30ead5c7c6081502bc34a6163ce64321dd4f9a339c7f24959dfc76891591cb` /
  `0b8f345fdf2bda5b95f2c1624920968f1ad499f4d5e765c0b8305e2045ac7e3a` /
  `1d708042f97c8c42164b07ff7104a68bdef95c14faf90dcb0171749d92b8a514` /
  `bf7144f407dd3e6aabf2161bf3d8c48dbb2e6c89a48cde9cfccf1cff60455e00` /
  `f47a1a4c1712fcff129c3840d7e64dfe1bbbe4bdacc049e28be6f868dbfc9cd4`
- Q011t artifact／runner newline-normalized SHA-256:
  `7848a915f384a4b51c93fa8201bf357b01cedcec52590defacd15ba22bf99fe2` /
  `b6eff63f29a4274502923a31b98fd774b89d1f21512c5e181c124f493efc8f10`
- Q011t input／cutoff／graph／radius／spectral／result digest:
  `79864489c522a7d50e7534091c283167de3b11d9af58365164b7084095a972eb` /
  `5c194baab4c8be74cba91c398037839c6b313f80123416819cc6aedf7bf027d2` /
  `6d7e09295d3b60d07d4abe9d658fea506752e20300e87e8d1c4158f5f0772bec` /
  `ba1cf6a77e95a52cba33d360632bfae0967a4d8b947daf04761dbfbd7926fcb9` /
  `d899cf7872d69b5adf75cddc9c0dafe42930ff53130099a8bdb5b7cb1b04559c` /
  `ac1019fd526cd4f21caddfb27d4cd8e0c4f7b312a742b84dbc3b3605ee827231`

Q007i rational-log algorithmのsource newline-normalized SHA-256
`22209c56184eff9556db13b553cb89644eea11ffd77a3af69d0316a747118294`
も直接封印する。Q011jのexact fixed point／map identity、Q011kのstrict stable invertible split、Q011mの
analytic density-positive map、Q011tのreal selected tangentとquotient bracketを再現する。

### C91 scalar localization

\(p=91\)とし、normalizing constant

\[
c_p=\frac{(2p+1)!}{(p!)^2}
\]

および

\[
S_p(y)=c_p\int_0^y u^p(1-u)^p\,du
=c_p\sum_{k=0}^{p}
\frac{(-1)^k\binom pk}{p+k+1}y^{p+k+1}
\]

をexact rational polynomialとして構成する。Q011tと同じ\(t_r(z)\)を用い、transition上で

\[
\chi_{91}(t)=1-S_{91}((t-1)/3)
\]

とする。\(S_p'(y)=c_py^p(1-y)^p\)なので、\(S_p(0)=0\)、\(S_p(1)=1\)、endpoint derivatives
1--91が0、\(0\le S_p\le1\)をexact combinatoricsで確認する。従ってpiecewise constant extensionは
\(C^{91}\)で、radius \(r\) ball上のidentity、radius \(4r\) ball内のsupport、conjugacy／selected／external
real-space preservationを持つ。高階derivativeのquantitative graph-transform capは本gateでは主張しない。

### exact modulus compression

Q011kの全2598 eigencenterとblockwise Bauer--Fike radiusからmodulus intervalを再構成する。selected 24
intervalをoverlap連結成分でmergeし、4 type、multiplicity `8 / 4 / 4 / 8`になることを要求する。external
2574 intervalもoverlap連結成分へmergeし、登録count `186`を要求する。mergeはinterval unionの連結成分を
取るだけであり、gapを埋めたりcenterを平均したりしない。

各selected typeの積について、type multiplicityの上限は使わない。同じeigenvalueの反復を許すTaylor
monomialを完全被覆するため、degree \(d\)のcount tuple

\[
(n_1,n_2,n_3,n_4),
\qquad
n_1+n_2+n_3+n_4=d
\]

を全列挙する。

### rational log enclosureと完全列挙

Q007iと同じ

- atanh series terms: `96`
- internal／final outward decimal grid: `110 / 60`
- maximum endpoint tail: `<=1e-90`

を固定し、selected product modulusをlog intervalのMinkowski sumとして評価する。external merged intervalも
logへ単調輸送し、binary searchで全overlapを数える。

degrees 3--90の88 degreeについて

\[
\sum_{d=3}^{90}\binom{d+3}{3}=3{,}049{,}486
\]

aggregateを全列挙する。sign／degeneracyまで展開したmonomial countのcontrol値は

\[
\sum_{d=3}^{90}\binom{d+5}{5}=927{,}048{,}276
\]

とする。各degreeのaggregate count、expanded count、overlap count、最小非overlap log gap、最初のoverlap
witnessを記録する。zero overlapの場合だけdegrees 3--90 external nonresonanceを認証する。interval overlapは
actual resonanceを意味せず、modulus-only certificateの失敗だけを意味する。

### degree-91 tail

Q011tのexact enclosureから

\[
(\rho_S^+)^{91}<\rho_E^-
\]

を直接再評価する。さらに\(\rho_S^+<1\)から全degree \(d\ge91\)のproduct modulusがexternal minimumより
小さいことを帰納する。tail ratio capは`<=0.999`とする。degree 2はQ011kの300 phase-sensitive pair
certificateをそのまま使う。

### design-only pilotの扱い

事前登録前のbinary64設計pilotではselected／external merge count `4 / 186`を得たが、degrees 3--90に
modulus overlapが観測された。このpilotは成功判定、overlap count、witness、gapには使わない。exact rational
log auditがzero overlapを示さなければ、本gateは予定どおりmodulus-only routeを棄却する。

### validity gate

1. Q011j／Q011k／Q011m／Q011tのartifact、runner、21 digest、outcome、claim boundaryとQ007i log sourceを直接再現する。
2. 92 coefficientの\(S_{91}\) polynomial、normalization、endpoint flatness、\(C^{91}\) real typingをexactに再現する。
3. 2598 modulus interval、selected `24 -> 4`、external `2574 -> 186` compressionを再現する。
4. 96-term rational log、110／60-digit outward grid、tail boundを再現する。
5. degrees 3--90の88 records、3,049,486 aggregate、927,048,276 expanded countを完全再現する。
6. overlap／nonoverlap classification、first witness、per-degree sum、record digestを再現する。
7. Q011k degree-2 evidenceとdegree-91 exact tailを再現する。
8. finite性、strict JSON、input／cutoff／spectrum／log／enumeration／tail／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、overlapもnonresonanceも解釈しない。

### hypothesis gateと停止規則

validity通過後、次を別々に判定する。

1. scalar localizationがoriginal mapとorigin近傍で一致する\(C^{91}\) real localizationである。
2. selected／external modulus compressionが登録countとstrict interval gapsを持つ。
3. degrees 3--90の全3,049,486 aggregateについてexternal merged intervalとのoverlapが0である。
4. zero-overlap aggregateのglobal minimum rational log gapが`>=1e-12`である。
5. degree 2 certificate、degrees 3--90 certificate、degree-91 tail、analytic local-diffeomorphism assumptionsが揃う。

全5項目が通る場合だけ
`the repaired exact map satisfies the registered C91 spectral-subspace nonresonance certificate`
として`accepted`とし、analytic local invariant manifoldの存在と\(C^{91}\)-class uniquenessをtheorem consequenceへ
記録する。

validityは通るが一つでもmodulus overlapがあれば
`the C91 localization and degree-91 tail are certified, but modulus-only nonresonance through degree 90 is obstructed`
として`rejected`とする。これはactual resonance、analytic manifoldの不存在、Q011t graphの非滑らかさを意味しない。
最初のoverlapをQ011vのphase-sensitive output-sector product auditへ渡す。

`inconclusive`なら最初のseal／polynomial／compression／log／count／tail／serialization failureだけを修復する。

### 主張境界

本gateは固定17² repaired exact map、fixed conservation leaf、登録\(C^{91}\) scalar localization、Q011k
eigendisc modulus、degrees 3--90のmodulus-only aggregate、degree-91 tailに限る。complex phase、Fourier output
sector、phase-sensitive product disk、homological inverse norm、Q011t graphとの一致、explicit higher-smoothness
radius、normal attraction、basin、他grid／force／wall、D3Q27を構成・認証しない。

### Q011u 実行結果

Q011j／Q011k／Q011m／Q011tの4 artifact、runner、21 digestとQ007i rational-log sourceを直接照合し、
validity `8 / 8`を通過した。登録したbeta polynomialは92個のexact coefficientを持ち、
\(S_{91}(0)=0\)、\(S_{91}(1)=1\)、derivatives 1--91の両endpoint flatnessをexact combinatoricsで再現した。
従ってQ011tと同じscalar power \(t_r\)を用いるcutoffは、origin近傍でoriginal mapと一致する
\(C^{91}\) real localizationである。ただしhigh-derivative graph-transform capやQ011t graphとの一致は
主張していない。

全2598 eigendisc modulus intervalを再構成し、selected `24 -> 4`、multiplicity `8 / 4 / 4 / 8`、
external `2574 -> 186`のstrict overlap-component compressionを得た。Q007iの96-term atanh seriesと
110／60-digit outward gridで全190 componentをlogへ輸送し、maximum endpoint tailは
`1.538017643004299e-92`で登録上限`1e-90`を通過した。

degrees 3--90について、登録した

\[
3{,}049{,}486
\]

aggregateと`927,048,276` expanded-product controlを完全列挙した。結果は

- overlap aggregate: `423,729`
- nonoverlap aggregate: `2,625,757`
- first overlap: degree `3`、selected-type counts `[0,1,1,1]`、external group `183`
- degree 3／90 overlap count: `1 / 2`
- global minimum nonoverlap log gap: `2.593371508729764e-9`

だった。minimum nonoverlap gap自体は`1e-12`より大きいが、zero-overlap gateを満たさないため
nonresonance certificateには使えない。一方、Q011kの300 quadratic pairは再現し、

\[
(\rho_S^+)^{91}/\rho_E^-=0.9922327356143813\le0.999
\]

なのでdegree 91以降のtailは独立に認証した。

hypothesisは`2 / 5`だけが通過し、
`the C91 localization and degree-91 tail are certified, but modulus-only nonresonance through degree 90 is obstructed`
としてvalid `rejected`とした。これはactual complex resonance、analytic invariant manifoldの不存在、
Q011t graphの非滑らかさを意味しない。

- input／cutoff／spectrum／log／enumeration／tail／result digest:
  `ba768da7be5663c607a24fa4a399bae06a8d8b4128a45ab9bb2b57f8a12461f4` /
  `55a374a5d91d2c88e5e34be2173f9861ee14915daaee55efd8848f0cd7ebaf94` /
  `a514c3a13142d379886c56b08109f28b69aee4cbcef2d4c5c9bed8d29182e89d` /
  `10f9aa954446e1e7d8095488ef82abc48fcc99fde3ddabd93a1a188b17ea51b5` /
  `5c94deb8acd69b1346e6d46af829804b401027ecea48caf7e5ce2d9b22d6631c` /
  `307ca2762bb5aecb626983acb8d38eb5728e2a8eb9e64769cc0b632b40da66c6` /
  `b005bb622e7f3abad98a1ef6875af289fa2dccdc16911faf11e7ee04b822722c`
- runner／artifact newline-normalized SHA-256:
  `fa3c7c01355c0b3c19b58618fe97edc5863dc2d0fa02c4f810ddbc57053a419e` /
  `4e0a74cffaeb6781b85621362d4463ac8d9ab98ee14bcf3b5764642b5a15d5e4`

停止規則どおり、次はQ011vで最初のoverlap witnessから始め、Fourier output sector、complex phase、
phase-sensitive product diskを使って、modulus overlapのどれが真のhomological obstruction候補として残るかを
事前登録して判定する。

## Q011v: degree-3 phase-sensitive output-sector product disks — 事前登録

### 問い

Q011uでdegree 3に残った唯一のmodulus-overlap aggregateについて、selected eigendiscのindexed triple、
Fourier output sector、exact complex center、Bauer--Fike radiusを復元し、全sector-compatible external
eigendiscからstrictに分離できるか。Q011uがmodulusだけで分離した残り19 aggregateと合成し、degree-3
external nonresonance全体を認証できるか。

本gateはdegrees 4--90へ結果を外挿しない。Q011uの423,729 overlapを一括解消したとも、Q011t graphの
higher smoothnessやSSM uniquenessを示したとも解釈しない。

### 封印入力

次の4 artifactを直接照合し、Q011uのnested sealだけで代用しない。

- Q011j artifact／runner newline-normalized SHA-256:
  `74a2e084137699739c14d980b05676e14e6802b4018b3893d3d05270850c2c5a` /
  `23a7a3a272264be3eb5330b2456192bd797aa968c4f795e2cbe8e337fc8fe4b5`
- Q011j input／coordinate／oracle／proof／result digest:
  `a183f4830c757b58122132cf64111fd5375636affdb6c0b31e1cd90e89085799` /
  `adaef353b8b64509334794c6014dc8b88e81ca2b776c3b65bd4d50911ae9452b` /
  `177468a48f667ddd922ed4b979d3e7e5d4cc0ed3afffe27a34651060da8e0f5f` /
  `1080fcea24358422514bba7fb9881928269c853cb4d12b0282e63840c56124c0` /
  `ddad5beca9693eeab726382ac864d01a27b749d579c2ec8f12dd9f8c499db934`
- Q011k artifact／runner newline-normalized SHA-256:
  `8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a` /
  `d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07`
- Q011k input／root／block／proof／result digest:
  `f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2` /
  `f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc` /
  `7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8` /
  `1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4` /
  `2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e`
- Q011m artifact／runner newline-normalized SHA-256:
  `b76b0ec1a1436aa3c2b48fcc29485e60e03675bf9a1f4f85ac3106d30687da3f` /
  `0cdc6ec9697d25bea3b28cf90f01f3f639062b3c04a64c4a88e6bd7221163150`
- Q011m input／derivative／coefficient／majorant／result digest:
  `dd30ead5c7c6081502bc34a6163ce64321dd4f9a339c7f24959dfc76891591cb` /
  `0b8f345fdf2bda5b95f2c1624920968f1ad499f4d5e765c0b8305e2045ac7e3a` /
  `1d708042f97c8c42164b07ff7104a68bdef95c14faf90dcb0171749d92b8a514` /
  `bf7144f407dd3e6aabf2161bf3d8c48dbb2e6c89a48cde9cfccf1cff60455e00` /
  `f47a1a4c1712fcff129c3840d7e64dfe1bbbe4bdacc049e28be6f868dbfc9cd4`
- Q011u artifact／runner newline-normalized SHA-256:
  `4e0a74cffaeb6781b85621362d4463ac8d9ab98ee14bcf3b5764642b5a15d5e4` /
  `fa3c7c01355c0b3c19b58618fe97edc5863dc2d0fa02c4f810ddbc57053a419e`
- Q011u input／cutoff／spectrum／log／enumeration／tail／result digest:
  `ba768da7be5663c607a24fa4a399bae06a8d8b4128a45ab9bb2b57f8a12461f4` /
  `55a374a5d91d2c88e5e34be2173f9861ee14915daaee55efd8848f0cd7ebaf94` /
  `a514c3a13142d379886c56b08109f28b69aee4cbcef2d4c5c9bed8d29182e89d` /
  `10f9aa954446e1e7d8095488ef82abc48fcc99fde3ddabd93a1a188b17ea51b5` /
  `5c94deb8acd69b1346e6d46af829804b401027ecea48caf7e5ce2d9b22d6631c` /
  `307ca2762bb5aecb626983acb8d38eb5728e2a8eb9e64769cc0b632b40da66c6` /
  `b005bb622e7f3abad98a1ef6875af289fa2dccdc16911faf11e7ee04b822722c`

exact eigencenter reconstructionとcomplex modulus enclosureに使うQ011l／Q011o runner sourceも直接封印する。

- Q011l source SHA-256:
  `59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7`
- Q011o source SHA-256:
  `60d9c445dace16d114e46263f2b47fe2db993b894337cdd462f204da09543f1f`

direct digest countは`22`とする。

### degree-3 modulus inventoryの再現

Q011uのdegree-3 recordを直接再現する。

- modulus-type aggregate count: \(\binom63=20\)
- expanded-product control count: \(\binom85=56\)
- modulus-separated aggregate count: `19`
- modulus-overlap aggregate count: `1`
- sole count tuple: `[0,1,1,1]`
- sole overlapping external component: `183`
- external component 183 source eigendisc count: `8`

selected modulus groups 1／2／3のsource eigendisc countは`4 / 4 / 8`なので、sole aggregateのindexed
triple countは

\[
4\times4\times8=128
\]

である。group membershipはQ011kの`block=center` identifierまで照合し、multiplicityをeigenvalueの反復上限とは
解釈しない。本witnessは各group countが1なので、128 Cartesian tripleが全monomial choiceを被覆する。

### Fourier output-sector filter

repaired forcingとexact fixed pointはx-independentであり、collision linearization／higher derivativeはx-local、
streaming、filter、repairはx-translation equivariantである。従ってselected input block
\(b_1,b_2,b_3\in\{0,1,16\}\)のcubic output blockは

\[
b_{\mathrm{out}}=(b_1+b_2+b_3)\bmod17
\]

である。128 tripleの登録sector histogramは

`0:32 / 1:28 / 2:16 / 3:4 / 14:4 / 15:16 / 16:28`

とする。external component 183のblock histogramは`0:4 / 2:2 / 15:2`である。従ってsector-compatible
target comparison countは

\[
32\times4+16\times2+16\times2=192
\]

となる。sectorが一致しないtargetとの比較をnonresonance evidenceへ数えず、sector-compatible 192比較だけを
exactに評価する。

### phase-sensitive product disk

selected source discを\(D(c_i,r_i)\)、exact rational center modulus upperを\(u_i\ge|c_i|\)とする。
triple productを

\[
C=c_1c_2c_3,
\qquad
R=\prod_{i=1}^3(u_i+r_i)-\prod_{i=1}^3u_i
\]

で囲み、\(D(c_1,r_1)D(c_2,r_2)D(c_3,r_3)\subset D(C,R)\)をtriangle inequalityで
exactに確認する。external target \(D(c_e,r_e)\)に対して

\[
\Delta^- = |C-c_e|^- - R-r_e
\]

をexact rational lower boundとして計算する。\(\Delta^->0\)ならcomplex product discはtarget discから分離する。
同時にindividual product modulus intervalも計算し、192比較を

1. individual modulusだけで分離
2. modulusはoverlapするがcomplex phaseで分離
3. complex product disc overlapが残る

へ重複なく分類する。成功にはcategory 3が0であることを要求する。phase-sensitive追加情報を実際に監査した
ことを示すため、category 2が1件以上あることも要求する。

### design-only pilotの扱い

事前登録前のexact-rational設計pilotでは、128 triple／192 sector-compatible comparisonを得て、64比較が
individual modulusで、残る128比較がcomplex phaseで分離し、minimum complex separationは約`0.2015`だった。
このpilotは証明record、exact margin、witness、digestには使わない。pilotを踏まえ、独立監査のregistered
minimum complex-separation capを`>=0.1`とする。

### validity gate

1. Q011j／Q011k／Q011m／Q011uのartifact、runner、22 digest、outcome、claim boundaryとQ011l／Q011o sourceを直接再現する。
2. Q011u degree-3の20 aggregate、19 modulus separation、sole `[0,1,1,1]` witness、external group 183を再現する。
3. selected group membership `4 / 4 / 8`、128 indexed triple、external target 8をQ011k centersから再構成する。
4. x-Fourier sum law、registered sector histograms、192 compatible comparison countを再現する。
5. product center、product radius、individual modulus、complex distance lowerのexact formulaを192比較すべてで再現する。
6. comparison partition、minimum margin、first record、full comparison digestを再現する。
7. finite性、strict JSON、input／inventory／sector／product／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、degree-3 nonresonanceもresonanceも解釈しない。

### hypothesis gateと停止規則

validity通過後、次を別々に判定する。

1. x-translation equivarianceからcubic output-sector sum lawがexactに成り立つ。
2. 20 modulus aggregateとsole-overlap 128 triple／192 compatible comparisonがdegree 3を完全被覆する。
3. 全192比較がindividual modulusまたはcomplex phaseでstrictに分離し、complex product-disc overlapが0である。
4. 全comparisonのminimum complex separation lowerが`>=0.1`である。
5. modulus-overlapからcomplex phaseで新たに分離したcomparisonが1件以上ある。

全5項目が通る場合だけ
`degree-3 external nonresonance is certified by modulus separation plus Fourier-sector phase-sensitive elimination of the sole overlap aggregate`
として`accepted`とする。この場合、Q011k degree 2、Q011v degree 3、Q011u degree 91+をevidence inventoryへ
記録し、missing rangeをdegrees 4--90へ更新する。

validityは通るがcomplex product-disc overlapが1件以上残れば
`the sole degree-3 modulus aggregate retains a phase-sensitive product-disc overlap`
として`rejected`とする。これはactual resonanceではなく、registered disc enclosureでは分離できないことだけを意味する。

`accepted`ならQ011wでdegree 4の2 modulus-overlap aggregateへ同じsector／phase auditを拡張する。
`rejected`ならQ011wで最初のremaining product-disc overlapだけを高精度center enclosureまたはfull homological
operatorへ送る。`inconclusive`なら最初のseal／inventory／sector／product／serialization failureだけを修復する。

### 主張境界

本gateは固定17² repaired exact map、fixed conservation leaf、degree 3、Q011u sole modulus-overlap aggregate、
Q011k eigendisc、x-Fourier output sector、registered product-disc formulaに限る。degrees 4--90、all-order
nonresonance、Q011t graphとの一致、\(C^2\)以上のgraph smoothness、SSM existence／uniqueness、explicit radius、
normal attraction、basin、他grid／force／wall、D3Q27を構成・認証しない。

### Q011v 実行結果

Q011j／Q011k／Q011m／Q011uの4 artifact、runner、22 digest、outcome、claim boundaryとQ011l／Q011o
sourceを直接照合し、validity `7 / 7`を通過した。Q011u degree-3 recordの20 aggregate、19 modulus
separation、sole `[0,1,1,1]` overlap、external group 183を再現した。selected source group size
`4 / 4 / 8`から128 indexed tripleを構成し、sector histogram

`0:32 / 1:28 / 2:16 / 3:4 / 14:4 / 15:16 / 16:28`

を得た。external group 183のtarget histogramは`0:4 / 2:2 / 15:2`であり、x-Fourier sum lawで残る
sector-compatible comparisonは`192`だった。

全128 product discと192 target comparisonをexact rational arithmeticで再構成した。comparison partitionは

- individual modulus separation: `64`
- complex phase separation: `128`
- unresolved product-disc overlap: `0`

だった。minimum complex separation lowerは`0.20153632779642386`で登録cap`0.1`を通過した。minimum witnessは
selected triple
`block=16;center=150 / block=0;center=148 / block=1;center=148`
とtarget `block=0;center=139`である。

hypothesis `5 / 5`を通過し、
`degree-3 external nonresonance is certified by modulus separation plus Fourier-sector phase-sensitive elimination of the sole overlap aggregate`
として`accepted`とした。従ってevidence inventoryはdegree 2／3をcertified、degree 91以降をtail-certified、
missing rangeをdegrees 4--90とする。

- inventory／sector-record／product-comparison digest:
  `8a0e025230faade977fcf04be45441f74cf32368089dabb3ddacce4e0349fc5b` /
  `3e372ba3750c06c2a4d48003e6c45bc96fd404cf76511412de9147de92bb2467` /
  `dbb690b311e5ff065295c6e5ae42e46da05259c94e9e1a90b8d8c96a952c2a89`
- input／inventory／sector／product／result digest:
  `10153049ce3cc7f50aa5a57ca6f4e8f92556bbefb3980e1d4c7dd61164aab470` /
  `591e6261238ac2253b0e0f11aaa13ce8a0c78948780633ea890a824ea9c5ccba` /
  `8988ade3f1fc974423040a2fe168904eb6610897f281e681387da7e3e2d3e919` /
  `a93737bcf662b154fcbea83905d733628e1ae397f4f70265d811e7ce657665db` /
  `1a2a83c6ae0d6f512a48f5f6d20e869abd0b69126504adbf5ba50054e1b749fc`
- runner／artifact newline-normalized SHA-256:
  `f9e7b0ffb353bc9f462616b42943860ecc4431b15176be7ca405c894d4d4a8cd` /
  `639afa89ccecadb428c4cb1c16a60ad7f788cc4786cdbb0ac2a5e681744bc663`

これはdegree 3だけのcertificateである。degrees 4--90、all-order nonresonance、Q011t graphとの一致、
higher graph smoothness、SSM existence／uniqueness、normal attraction、basinは未認証である。停止規則どおり、
次はQ011wでdegree 4に残る2 modulus-overlap aggregateへ同じsector／phase auditを拡張する。

## Q011w: degree-4 phase-sensitive output-sector product disks — 事前登録

### 問い

Q011uでdegree 4に残った2個のmodulus-overlap aggregateについて、selected eigendiscの可換多重指数
monomial、Fourier output sector、exact complex center、Bauer--Fike radiusを復元し、全sector-compatible
external eigendiscからstrictに分離できるか。Q011uがmodulusだけで分離した残り33 aggregateと合成し、
degree-4 external nonresonance全体を認証できるか。

本gateはdegrees 5--90へ結果を外挿しない。Q011uの全overlapを一括解消したとも、Q011t graphの
higher smoothnessやSSM uniquenessを示したとも解釈しない。

### 封印入力

計算で直接使うQ011k／Q011u／Q011vの3 artifactを直接照合する。

- Q011k artifact／runner newline-normalized SHA-256:
  `8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a` /
  `d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07`
- Q011k input／root／block／proof／result digest:
  `f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2` /
  `f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc` /
  `7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8` /
  `1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4` /
  `2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e`
- Q011u artifact／runner newline-normalized SHA-256:
  `4e0a74cffaeb6781b85621362d4463ac8d9ab98ee14bcf3b5764642b5a15d5e4` /
  `fa3c7c01355c0b3c19b58618fe97edc5863dc2d0fa02c4f810ddbc57053a419e`
- Q011u input／cutoff／spectrum／log／enumeration／tail／result digest:
  `ba768da7be5663c607a24fa4a399bae06a8d8b4128a45ab9bb2b57f8a12461f4` /
  `55a374a5d91d2c88e5e34be2173f9861ee14915daaee55efd8848f0cd7ebaf94` /
  `a514c3a13142d379886c56b08109f28b69aee4cbcef2d4c5c9bed8d29182e89d` /
  `10f9aa954446e1e7d8095488ef82abc48fcc99fde3ddabd93a1a188b17ea51b5` /
  `5c94deb8acd69b1346e6d46af829804b401027ecea48caf7e5ce2d9b22d6631c` /
  `307ca2762bb5aecb626983acb8d38eb5728e2a8eb9e64769cc0b632b40da66c6` /
  `b005bb622e7f3abad98a1ef6875af289fa2dccdc16911faf11e7ee04b822722c`
- Q011v artifact／runner newline-normalized SHA-256:
  `639afa89ccecadb428c4cb1c16a60ad7f788cc4786cdbb0ac2a5e681744bc663` /
  `f9e7b0ffb353bc9f462616b42943860ecc4431b15176be7ca405c894d4d4a8cd`
- Q011v input／inventory／sector／product／result digest:
  `10153049ce3cc7f50aa5a57ca6f4e8f92556bbefb3980e1d4c7dd61164aab470` /
  `591e6261238ac2253b0e0f11aaa13ce8a0c78948780633ea890a824ea9c5ccba` /
  `8988ade3f1fc974423040a2fe168904eb6610897f281e681387da7e3e2d3e919` /
  `a93737bcf662b154fcbea83905d733628e1ae397f4f70265d811e7ce657665db` /
  `1a2a83c6ae0d6f512a48f5f6d20e869abd0b69126504adbf5ba50054e1b749fc`

exact eigencenter reconstructionとcomplex modulus enclosureに使うQ011l／Q011o sourceも、Q011v artifactに
記録された値へ直接照合する。

- Q011l source SHA-256:
  `59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7`
- Q011o source SHA-256:
  `60d9c445dace16d114e46263f2b47fe2db993b894337cdd462f204da09543f1f`

direct digest countは`17`とする。

### degree-4 modulus inventoryの再現

Q011uのdegree-4 recordと全overlapを直接再現する。

- modulus-type aggregate count: \(\binom73=35\)
- expanded-product control count: \(\binom95=126\)
- modulus-separated aggregate count: `33`
- modulus-overlap aggregate count: `2`
- overlap count tuple: `[0,0,0,4]`、`[0,0,1,3]`
- overlapping external component: いずれも`183`
- external component 183 source eigendisc count: `8`

selected modulus group sizeは`8 / 4 / 4 / 8`である。polynomial monomialはordered tupleではなく可換な
coordinate multi-indexなので、同一groupから\(n\)個を選ぶときはcombination with replacementを使う。
従ってindexed monomial countは

\[
\binom{8+4-1}{4}=330
\]

および

\[
\binom41\binom{8+3-1}{3}=4\times120=480
\]

で、合計`810`とする。source identifierは座標slotを表し、同一identifierの反復はその座標の高べきである。
group中の固有値multiplicityを反復上限とは解釈しない。これにより2 aggregate内のdegree-4 monomialを重複なく
完全被覆する。

### Fourier output-sector filter

x-translation equivarianceから4入力のoutput blockは

\[
b_{\mathrm{out}}=(b_1+b_2+b_3+b_4)\bmod17
\]

である。`[0,0,0,4]`の330 monomialに対するsector histogramは

`0:84 / 1:64 / 2:38 / 3:16 / 4:5 / 13:5 / 14:16 / 15:38 / 16:64`

とし、`[0,0,1,3]`の480 monomialでは

`0:124 / 1:100 / 2:54 / 3:20 / 4:4 / 13:4 / 14:20 / 15:54 / 16:100`

とする。external component 183のtarget histogramは`0:4 / 2:2 / 15:2`なので、
sector-compatible comparison countは`488 + 712 = 1200`である。一致しないsectorとの比較を
nonresonance evidenceへ数えない。

### phase-sensitive product disk

degree-4 source discを\(D(c_i,r_i)\)、exact rational center modulus upperを\(u_i\ge|c_i|\)とする。

\[
C=\prod_{i=1}^{4}c_i,
\qquad
R=\prod_{i=1}^{4}(u_i+r_i)-\prod_{i=1}^{4}u_i
\]

によりproductを囲む。sector-compatible external target \(D(c_e,r_e)\)に対して

\[
\Delta^- = |C-c_e|^- - R-r_e
\]

をexact rational lower boundとして計算する。1200比較を

1. individual modulusだけで分離
2. modulusはoverlapするがcomplex phaseで分離
3. complex product disc overlapが残る

へ重複なく分類する。category 3が0であることと、category 2が1件以上あることを成功条件にする。

### exact recordの逐次封印

degree 4ではexact rational numerator／denominatorが長いため、全810 productと1200 comparisonの巨大な
fraction recordをartifactへ重複保存しない。各exact recordをkey-sorted compact JSONへ直し、
8-byte big-endian record lengthとUTF-8 payloadを順にSHA-256へ投入するframed-record digestで、順序、
境界、全exact値を封印する。artifactには全source／target／sector／classificationのcompact record、
exact digest、minimum marginのexact witnessを保存する。validity testではrunnerを再実行し、全exact digestを
再現する。これは計算を省略する圧縮ではなく、artifact serializationだけの圧縮である。

### design-only pilotの扱い

事前登録前のexact-rational設計pilotでは、810 monomial／1200 compatible comparisonを得た。
`[0,0,0,4]`は`348 modulus / 140 phase / 0 unresolved`、
`[0,0,1,3]`は`88 modulus / 624 phase / 0 unresolved`で、全体は
`436 / 764 / 0`だった。minimum complex separation lowerは約`0.0040573`だった。
このpilotは証明record、exact witness、digestには使わない。pilotを踏まえ、registered minimum
complex-separation thresholdを`>=0.002`、すなわち`1/500`とする。

### validity gate

1. Q011k／Q011u／Q011vのartifact、runner、17 digest、outcome、claim boundaryとQ011l／Q011o sourceを再現する。
2. Q011u degree-4の35 aggregate、33 modulus separation、2 overlap tupleとexternal group 183を再現する。
3. group membership、330／480可換多重指数monomial、external target 8をQ011k centersから再構成する。
4. x-Fourier sum law、登録sector histogram、488／712／1200 compatible comparison countを再現する。
5. product center、radius、individual modulus、complex distance lowerを全810 product／1200比較でexactに再現する。
6. comparison partition、minimum margin、first unresolved、framed exact-record digestを再現する。
7. compact recordのfinite性、strict JSON、input／inventory／sector／product／result digest、provenanceを再現する。

一つでも落ちれば`inconclusive`とし、degree-4 nonresonanceもresonanceも解釈しない。

### hypothesis gateと停止規則

validity通過後、次を別々に判定する。

1. x-translation equivarianceからquartic output-sector sum lawがexactに成り立つ。
2. 35 modulus aggregateと2 overlapの810 monomial／1200 comparisonがdegree 4を完全被覆する。
3. 全1200比較がindividual modulusまたはcomplex phaseでstrictに分離し、product-disc overlapが0である。
4. 全comparisonのminimum complex separation lowerが`>=1/500`である。
5. modulus-overlapからcomplex phaseで新たに分離したcomparisonが1件以上ある。

全5項目が通る場合だけ
`degree-4 external nonresonance is certified by modulus separation plus Fourier-sector phase-sensitive elimination of both overlap aggregates`
として`accepted`とする。この場合、certified degreesを2／3／4、tail-certifiedを91以降、missing rangeを
degrees 5--90へ更新する。

validityは通るがcomplex product-disc overlapが1件以上残れば
`at least one degree-4 modulus aggregate retains a phase-sensitive product-disc overlap`
として`rejected`とする。これはactual resonanceではなく、registered enclosureで分離できないことだけを意味する。

`accepted`ならQ011xでdegree 5の2 modulus-overlap aggregateへ進む。`rejected`ならQ011xで最初のremaining
overlapだけをtightened center enclosureまたはfull homological operatorへ送る。`inconclusive`なら最初の
seal／inventory／sector／product／serialization failureだけを修復する。

### 主張境界

本gateは固定17² repaired exact map、fixed conservation leaf、degree 4、Q011uの2 modulus-overlap
aggregate、Q011k eigendisc、x-Fourier output sector、registered product-disc formulaに限る。degrees 5--90、
all-order nonresonance、Q011t graphとの一致、\(C^2\)以上のgraph smoothness、SSM existence／uniqueness、
explicit radius、normal attraction、basin、他grid／force／wall、D3Q27を構成・認証しない。

### Q011w 実行結果

Q011k／Q011u／Q011vの3 artifact、runner、17 digest、outcome、claim boundaryとQ011l／Q011o sourceを
直接照合し、validity `7 / 7`を通過した。Q011u degree-4 recordの35 aggregate、33 modulus separation、
2 overlap `[0,0,0,4]`／`[0,0,1,3]`、両方のexternal group 183を再現した。

selected group size `8 / 4 / 4 / 8`からcombination with replacementで`330 / 480`、合計810の可換
coordinate monomialを重複なく列挙した。aggregate別sector histogramは

- `[0,0,0,4]`:
  `0:84 / 1:64 / 2:38 / 3:16 / 4:5 / 13:5 / 14:16 / 15:38 / 16:64`
- `[0,0,1,3]`:
  `0:124 / 1:100 / 2:54 / 3:20 / 4:4 / 13:4 / 14:20 / 15:54 / 16:100`

で、external group 183の`0:4 / 2:2 / 15:2`と合わせたsector-compatible comparisonは
`488 / 712`、合計`1200`だった。

全810 product discと1200 comparisonをexact rational arithmeticで再構成した。comparison partitionは

- `[0,0,0,4]`: `348 modulus / 140 phase / 0 unresolved`
- `[0,0,1,3]`: `88 modulus / 624 phase / 0 unresolved`
- total: `436 modulus / 764 phase / 0 unresolved`

だった。minimum complex separation lowerは`0.004057305895234305`で、登録threshold `1/500`を通過した。
minimum witnessはsource
`block=0;center=144`の3乗と`block=0;center=145`、target `block=0;center=137`である。

巨大なexact fraction列は、各canonical JSON recordを8-byte big-endian lengthでframingした逐次SHA-256へ
封印した。product／comparison framed digestは
`87afe07ba51448f4827854908fe5c6fde851ee0ce919ec107e8fd2a50d36d3f7` /
`d3ca632166e3c2c69b947837056b5b6e416baf8160da4958dfd11e8f5d3d125c`である。

hypothesis `5 / 5`を通過し、
`degree-4 external nonresonance is certified by modulus separation plus Fourier-sector phase-sensitive elimination of both overlap aggregates`
として`accepted`とした。従ってcertified degreesは2／3／4、degree 91以降はtail-certified、missing rangeは
degrees 5--90となる。

- inventory／sector／compact-product digest:
  `12fd69ae0d7f290ae7d575ef85448c84b43b21157cb35e991a32cd2a075b0243` /
  `bc38352978cafd86b8b9d4b1524997108f1adf96555072bf862e00efc9a03397` /
  `cbfcc669e638be0211d0ac11e038b2885259deda1f0a9598ab18368f1e3d5ed6`
- input／inventory／sector／product／result digest:
  `ed3eea9c2a0f5c07de59dbddb0579b2dbb36e15409c3372729efc1e0d65c7a8d` /
  `51c97d78b13ba2d9e787f833fe0f3c805848723710096da566f569c2fd301416` /
  `369ef47a86630f84d96033539d3a7a7e94b34a45a95a15cef6bde71174eaa455` /
  `182672f831dd715402b4f52ab9aa2628ff9eba09a3c4a8de07d32a10bf736476` /
  `4681053a49eb583faa30d94d44e39d0ebfb1d00091ad7447ae086f21fd5d94d3`
- runner／artifact newline-normalized SHA-256:
  `288a12d72f90f6df1f79a8e5f02d527d317f9a4a9828ebbcdf0cc58008b56247` /
  `6e0b0a166b6a5f4f915cf6ba4a46c699a26c63faf92dc92388502a2244fe0b9c`

これはdegree 4だけのcertificateである。degrees 5--90、all-order nonresonance、Q011t graphとの一致、
higher graph smoothness、SSM existence／uniqueness、normal attraction、basinは未認証である。停止規則どおり、
次はQ011xでdegree 5に残る2 modulus-overlap aggregateへ同じ監査を拡張する。

## Q011x: degree-5 phase-sensitive output-sector product disks — 事前登録

### 問い

Q011uでdegree 5に残った2 modulus-overlap aggregateを可換coordinate monomialへ展開し、indexed
individual modulus、Fourier output sector、exact complex product discを順に適用して全external eigendiscから
strictに分離できるか。Q011uがmodulus aggregateだけで分離した残り54件と合成し、degree-5 external
nonresonance全体を認証できるか。

本gateはdegrees 6--90へ外挿せず、all-order nonresonance、higher graph smoothness、SSM uniquenessを主張しない。

### 封印入力

Q011k／Q011u／Q011v／Q011wの4 artifactを直接照合する。

- Q011k artifact／runner newline-normalized SHA-256:
  `8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a` /
  `d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07`
- Q011k input／root／block／proof／result digest:
  `f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2` /
  `f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc` /
  `7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8` /
  `1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4` /
  `2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e`
- Q011u artifact／runner newline-normalized SHA-256:
  `4e0a74cffaeb6781b85621362d4463ac8d9ab98ee14bcf3b5764642b5a15d5e4` /
  `fa3c7c01355c0b3c19b58618fe97edc5863dc2d0fa02c4f810ddbc57053a419e`
- Q011u input／cutoff／spectrum／log／enumeration／tail／result digest:
  `ba768da7be5663c607a24fa4a399bae06a8d8b4128a45ab9bb2b57f8a12461f4` /
  `55a374a5d91d2c88e5e34be2173f9861ee14915daaee55efd8848f0cd7ebaf94` /
  `a514c3a13142d379886c56b08109f28b69aee4cbcef2d4c5c9bed8d29182e89d` /
  `10f9aa954446e1e7d8095488ef82abc48fcc99fde3ddabd93a1a188b17ea51b5` /
  `5c94deb8acd69b1346e6d46af829804b401027ecea48caf7e5ce2d9b22d6631c` /
  `307ca2762bb5aecb626983acb8d38eb5728e2a8eb9e64769cc0b632b40da66c6` /
  `b005bb622e7f3abad98a1ef6875af289fa2dccdc16911faf11e7ee04b822722c`
- Q011v artifact／runner newline-normalized SHA-256:
  `639afa89ccecadb428c4cb1c16a60ad7f788cc4786cdbb0ac2a5e681744bc663` /
  `f9e7b0ffb353bc9f462616b42943860ecc4431b15176be7ca405c894d4d4a8cd`
- Q011v input／inventory／sector／product／result digest:
  `10153049ce3cc7f50aa5a57ca6f4e8f92556bbefb3980e1d4c7dd61164aab470` /
  `591e6261238ac2253b0e0f11aaa13ce8a0c78948780633ea890a824ea9c5ccba` /
  `8988ade3f1fc974423040a2fe168904eb6610897f281e681387da7e3e2d3e919` /
  `a93737bcf662b154fcbea83905d733628e1ae397f4f70265d811e7ce657665db` /
  `1a2a83c6ae0d6f512a48f5f6d20e869abd0b69126504adbf5ba50054e1b749fc`
- Q011w artifact／runner newline-normalized SHA-256:
  `6e0b0a166b6a5f4f915cf6ba4a46c699a26c63faf92dc92388502a2244fe0b9c` /
  `288a12d72f90f6df1f79a8e5f02d527d317f9a4a9828ebbcdf0cc58008b56247`
- Q011w input／inventory／sector／product／result digest:
  `ed3eea9c2a0f5c07de59dbddb0579b2dbb36e15409c3372729efc1e0d65c7a8d` /
  `51c97d78b13ba2d9e787f833fe0f3c805848723710096da566f569c2fd301416` /
  `369ef47a86630f84d96033539d3a7a7e94b34a45a95a15cef6bde71174eaa455` /
  `182672f831dd715402b4f52ab9aa2628ff9eba09a3c4a8de07d32a10bf736476` /
  `4681053a49eb583faa30d94d44e39d0ebfb1d00091ad7447ae086f21fd5d94d3`

Q011l／Q011o helper sourceも直接照合する。

- Q011l source SHA-256:
  `59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7`
- Q011o source SHA-256:
  `60d9c445dace16d114e46263f2b47fe2db993b894337cdd462f204da09543f1f`

direct digest countは`22`とする。

### degree-5 modulus inventoryと可換monomial

Q011u degree-5 recordを全tupleについて再現する。

- modulus-type aggregate count: \(\binom83=56\)
- expanded-product control count: \(\binom{10}5=252\)
- modulus-separated／overlap aggregate: `54 / 2`
- overlap 0: `[0,3,1,1]`、external group `178`
- overlap 1: `[0,4,1,0]`、external group `177`

selected group size `8 / 4 / 4 / 8`にcombination with replacementを適用する。monomial countは

\[
\binom{4+3-1}{3}\binom41\binom81=20\times4\times8=640
\]

および

\[
\binom{4+4-1}{4}\binom41=35\times4=140
\]

で、合計`780`とする。ordered tupleは使わず、座標高べきを含むdegree-5 multi-indexを各1回だけ列挙する。

### Fourier output-sector filter

\[
b_{\mathrm{out}}=(b_1+b_2+b_3+b_4+b_5)\bmod17
\]

を使う。aggregate別monomial sector histogramを

- `[0,3,1,1]`:
  `0:96 / 1:92 / 2:80 / 3:60 / 4:32 / 5:8 / 12:8 / 13:32 / 14:60 / 15:80 / 16:92`
- `[0,4,1,0]`:
  `0:18 / 1:17 / 2:16 / 3:13 / 4:10 / 5:5 / 12:5 / 13:10 / 14:13 / 15:16 / 16:17`

とする。external group 178は4 target、histogram `2:2 / 15:2`で、compatible comparisonは`320`。
external group 177は8 target、histogram `0:4 / 3:2 / 14:2`で、compatible comparisonは`124`。
合計`444`だけをexactに比較する。

### indexed modulusとphase-sensitive product disk

各degree-5 monomialについて

\[
C=\prod_{i=1}^{5}c_i,
\qquad
R=\prod_{i=1}^{5}(u_i+r_i)-\prod_{i=1}^{5}u_i
\]

をexactに構成し、

\[
\Delta^- = |C-c_e|^- - R-r_e
\]

を評価する。comparisonをindividual indexed modulus separation、complex phase separation、unresolved
product-disc overlapへ分割する。category 3が0、category 2が1件以上であることを要求する。merged modulus
aggregateがoverlapしていても、その全indexed monomialがindividual modulusで分離すれば正当な解消と数える。

exact product 780件／comparison 444件はQ011wと同じ8-byte length-framed canonical JSONの逐次SHA-256へ
封印し、artifactにはcompact recordとexact minimum witnessを保存する。

### design-only pilotの扱い

事前登録前のexact-rational pilotでは、

- `[0,3,1,1]`／group 178: `320 modulus / 0 phase / 0 unresolved`
- `[0,4,1,0]`／group 177: `52 modulus / 72 phase / 0 unresolved`
- total: `372 modulus / 72 phase / 0 unresolved`

だった。global minimum complex separation lowerは約`0.1992163`、phase-only minimumは約`0.5682244`だった。
pilotは証明digestやexact witnessへ使わない。registered minimum thresholdを`>=0.1`とする。

### validity gate

1. Q011k／Q011u／Q011v／Q011w artifact、runner、22 digest、outcome、claim boundaryとQ011l／Q011o sourceを再現する。
2. degree-5の56 aggregate、54 separation、2 overlap tuple／external groupを全log intervalから再現する。
3. group membership、640／140可換monomial、external target `4 / 8`を再構成する。
4. quintic wave-sum law、sector histogram、`320 / 124 / 444` comparisonを再現する。
5. 全780 productと444 comparisonのcenter、radius、modulus、complex distance lowerをexactに再現する。
6. partition、minimum witness、first unresolved、framed exact-record digestを再現する。
7. compact strict JSON、section／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とする。

### hypothesis gateと停止規則

1. quintic Fourier sum lawがexactに成り立つ。
2. 56 aggregateと2 overlap内の780 monomial／444 comparisonがdegree 5を完全被覆する。
3. unresolved product-disc overlapが0である。
4. global minimum complex separation lowerが`>=0.1`である。
5. complex phase separationが1件以上ある。

全5項目が通る場合だけ
`degree-5 external nonresonance is certified by indexed modulus refinement and Fourier-sector phase-sensitive product disks for both overlap aggregates`
として`accepted`とする。certified degreesを2／3／4／5、tail-certifiedを91以降、missing rangeを
degrees 6--90へ更新する。

unresolvedが残れば
`at least one degree-5 modulus aggregate retains a phase-sensitive product-disc overlap`
として`rejected`とする。actual resonanceの証明とは解釈しない。

`accepted`ならQ011yでdegree 6の3 modulus-overlap aggregateへ進む。`rejected`なら最初のunresolvedだけを
tightened enclosureまたはfull homological operatorへ送る。`inconclusive`なら最初のvalidity failureだけを修復する。

### 主張境界

本gateは固定17² repaired exact map、fixed conservation leaf、degree 5、Q011uの2 overlap aggregate、
Q011k eigendisc、x-Fourier sector、registered product-disc formulaに限る。degrees 6--90、all-order
nonresonance、Q011t graphとの一致、\(C^2\)以上のgraph smoothness、SSM existence／uniqueness、explicit radius、
normal attraction、basin、他grid／force／wall、D3Q27を構成・認証しない。

### Q011x 実行結果

Q011k／Q011u／Q011v／Q011wの4 artifact、runner、22 digest、outcome、claim boundaryとQ011l／Q011o
sourceを照合し、validity `7 / 7`を通過した。degree 5の56 modulus aggregate、54 separation、
`[0,3,1,1]`／external 178と`[0,4,1,0]`／external 177の2 overlapを再現した。

selected group size `8 / 4 / 4 / 8`から`640 / 140`、合計780の可換monomialを列挙した。external
target countはgroup 178が4、group 177が8で、quintic Fourier sum lawによりcompatible comparisonは
`320 / 124`、合計`444`だった。

全780 product discと444 comparisonをexactに評価し、

- `[0,3,1,1]`／group 178: `320 modulus / 0 phase / 0 unresolved`
- `[0,4,1,0]`／group 177: `52 modulus / 72 phase / 0 unresolved`
- total: `372 modulus / 72 phase / 0 unresolved`

を得た。global minimum complex separation lowerは`0.19921630498069512`で、登録threshold `0.1`を通過した。
minimum witnessは
`(block=16;center=150)^3 × block=0;center=148 × block=1;center=149`
とtarget `block=15;center=148`で、individual modulus separationだった。phase-only minimumは
`0.5682244044808002`で、target `block=0;center=130`だった。

product／comparison framed digestは
`c8bf3fa77eea40b0f2384a543cb56d6b2f1b1f714b72cee7d3fd664648f4967f` /
`ae94f63d4b8ea7217e60c39c2aed7626436f0b136c7baabffba76bb1a410e62a`である。

hypothesis `5 / 5`を通過し、
`degree-5 external nonresonance is certified by indexed modulus refinement and Fourier-sector phase-sensitive product disks for both overlap aggregates`
として`accepted`とした。certified degreesは2／3／4／5、degree 91以降はtail-certified、missing rangeは
degrees 6--90となる。

- inventory／sector／compact-product digest:
  `077f1ca07017b0f2b21c79ab069a38804b198b1bb4db7bace1b4a572f1a528d5` /
  `6ef11f94af7e07675c2664da98b3df7fce241bbbf40007869c86e0c0fa3d704c` /
  `44ef544447a7ea792bef4119fa40c6fe897f8fad2cc59aa1f0a56e3bbafcf2ad`
- input／inventory／sector／product／result digest:
  `9d13fa470f4c0bd8efa13868af90c6931025d7f3007e600c66af05bd0037a7ed` /
  `717c4eadbd0e5f160a87de8846968933b8c5fbe604d769f215b6dcc65dacc955` /
  `d31b7ea3cfcd7eca9d936cded13a1dc316e64dc2fc088bda745ea927d15ce52c` /
  `add9d07725802c5fba84b68a207d5adc6f3f405a152a22f88059259f9a255222` /
  `608bb3a7aee34a833e7980dbd18f4a3e641426966352126833f298e282437b31`
- runner／artifact newline-normalized SHA-256:
  `62712392faca2c154883edd93792f81e60ff975f6da16010aa3190ee44657a18` /
  `11ef4d47f60840c4bc05c4056024e2af14b8339a8983b65dcb878bd355cfc328`

これはdegree 5だけのcertificateである。degrees 6--90、all-order nonresonance、higher graph smoothness、
SSM existence／uniqueness、normal attraction、basinは未認証である。停止規則どおり、次はQ011yでdegree 6の
3 modulus-overlap aggregateへ進む。

## Q011y: transformed-residual eigendisc refinement — 事前登録

### 問い

Q011yのdegree-6 design pilotでは、Q011kのblock-uniform Bauer--Fike radiusを使うと3 overlap aggregate中
`[0,2,2,2]`／external group 178に144 product-disc overlapが残り、minimum marginは約`-3.30e-6`だった。
これはactual resonanceではなく、block 0 radius `1.3038e-5`が積に4回入るenclosure obstructionである。

Q011kがすでに証明したinvertible approximate eigenvector matrix \(V\)、diagonal center matrix \(D\)、
family residual \(E=AV-VD\)から、transformed residual

\[
\theta=\|V^{-1}\|_\infty\|E\|_\infty
\]

を直接使うcontained eigendiscを認証できるか。そのrefined discで最初のdegree-6 obstruction witnessをstrictに
分離できるか。

本gateはdegree-6全体を認証しない。linear eigendisc inclusionの精密化と最初のwitness clearanceだけを扱う。

### 数学的根拠

\(V\)が可逆なら

\[
V^{-1}AV=D+F,
\qquad
F=V^{-1}(AV-VD)
\]

であり、

\[
\|F\|_\infty\le
\|V^{-1}\|_\infty\|AV-VD\|_\infty\le\theta.
\]

従ってGershgorin inclusionを\(D+F\)へ適用すると、任意の固有値は少なくとも一つの
\(D(d_j,\theta)\)に入る。これは[Bauer--Fikeの原論文](http://eudml.org/doc/131452)のexclusion argumentと
同じ相似変換である。Q011lは同じexact quantityを`transformed_perturbation_upper = beta * family_residual`
として既に再構成し、Riccati graphとquadratic homological inverseに使用している。

Q011kの旧半径

\[
r_{\mathrm{old}}
=\|V\|_\infty\|V^{-1}\|_\infty^2\|E\|_\infty
=\bigl(\|V\|_\infty\|V^{-1}\|_\infty\bigr)\theta
\]

もvalidなsupersetである。従って\(\|V\|_\infty\|V^{-1}\|_\infty\ge1\)をexactに確認すれば、
同じcenterのrefined discは旧discに包含され、Q011k以降の旧certificateを弱めない。

### 封印入力

Q011k／Q011l／Q011u／Q011xの4 artifactを直接照合する。

- Q011k artifact／runner newline-normalized SHA-256:
  `8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a` /
  `d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07`
- Q011k input／root／block／proof／result digest:
  `f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2` /
  `f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc` /
  `7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8` /
  `1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4` /
  `2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e`
- Q011l artifact／runner newline-normalized SHA-256:
  `2878d8ebaaedc29990700ccac25b78185e0b6139dd371521f14602caf4514c0a` /
  `59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7`
- Q011l input／graph／pair／homological／result digest:
  `1810f989a0328521e8b6d6ccbc2153cb9a945bb2c129c70d7b25a0c227fc7011` /
  `a7d0f320fa7391c506f42853a94ede66fc73e81b004dfccda144028082cb8db3` /
  `694cc2955bcef05df13ad30582f46f84bb627aaa7b336b5278e9b5139e29d377` /
  `14d67f1d915aa3bd6bc34117562da4908e19036943e60fb638eddf6a42b20915` /
  `c372aa5962a7f3d0c83a126303a9e36e4f0830d113f9c49b922d03beb2f09a45`
- Q011u artifact／runner newline-normalized SHA-256:
  `4e0a74cffaeb6781b85621362d4463ac8d9ab98ee14bcf3b5764642b5a15d5e4` /
  `fa3c7c01355c0b3c19b58618fe97edc5863dc2d0fa02c4f810ddbc57053a419e`
- Q011u input／cutoff／spectrum／log／enumeration／tail／result digest:
  `ba768da7be5663c607a24fa4a399bae06a8d8b4128a45ab9bb2b57f8a12461f4` /
  `55a374a5d91d2c88e5e34be2173f9861ee14915daaee55efd8848f0cd7ebaf94` /
  `a514c3a13142d379886c56b08109f28b69aee4cbcef2d4c5c9bed8d29182e89d` /
  `10f9aa954446e1e7d8095488ef82abc48fcc99fde3ddabd93a1a188b17ea51b5` /
  `5c94deb8acd69b1346e6d46af829804b401027ecea48caf7e5ce2d9b22d6631c` /
  `307ca2762bb5aecb626983acb8d38eb5728e2a8eb9e64769cc0b632b40da66c6` /
  `b005bb622e7f3abad98a1ef6875af289fa2dccdc16911faf11e7ee04b822722c`
- Q011x artifact／runner newline-normalized SHA-256:
  `11ef4d47f60840c4bc05c4056024e2af14b8339a8983b65dcb878bd355cfc328` /
  `62712392faca2c154883edd93792f81e60ff975f6da16010aa3190ee44657a18`
- Q011x input／inventory／sector／product／result digest:
  `9d13fa470f4c0bd8efa13868af90c6931025d7f3007e600c66af05bd0037a7ed` /
  `717c4eadbd0e5f160a87de8846968933b8c5fbe604d769f215b6dcc65dacc955` /
  `d31b7ea3cfcd7eca9d936cded13a1dc316e64dc2fc088bda745ea927d15ce52c` /
  `add9d07725802c5fba84b68a207d5adc6f3f405a152a22f88059259f9a255222` /
  `608bb3a7aee34a833e7980dbd18f4a3e641426966352126833f298e282437b31`

complex modulus lower／upperに使うQ011o sourceも直接封印する。

- Q011o source SHA-256:
  `60d9c445dace16d114e46263f2b47fe2db993b894337cdd462f204da09543f1f`

direct digest countは`22`とする。

### registered refined radii

9 representative blockについて、Q011k primary proofのexact \(\beta\)、family residual、vector norm、旧半径を
読み、\(\theta=\beta\|E\|_\infty\)を再構成する。blocks 9--16はexact conjugacyでtransportする。
design-only exact pilot値は次のとおりである。

| representative block | old radius | refined \(\theta\) | old／new |
|---:|---:|---:|---:|
| 0 | `1.3038143644301623e-5` | `2.0299911997564775e-8` | `642.28` |
| 1 | `3.9292231700426665e-7` | `1.0615797998969425e-9` | `370.13` |
| 2 | `5.230382477700401e-7` | `1.223952119991868e-9` | `427.34` |
| 3 | `6.921161201925137e-7` | `1.4069946614862016e-9` | `491.91` |
| 4 | `7.85981566123045e-4` | `4.7369170150175137e-8` | `16592.68` |
| 5 | `2.7378963980438355e-4` | `2.7932109133679385e-8` | `9801.97` |
| 6 | `5.438442399537979e-7` | `1.2439307104566969e-9` | `437.20` |
| 7 | `4.555634685122818e-7` | `1.137780728280521e-9` | `400.40` |
| 8 | `3.8891601146814717e-7` | `1.0510867368940072e-9` | `370.01` |

pilotを踏まえ、次を登録する。

- maximum refined radius: `<=5e-8`
- minimum old／new improvement ratio: `>=300`
- maximum refined eigenvalue-disc modulus upper: `<=0.9921`
- first degree-6 witness refined separation lower: `>=4e-5`

pilot exact値はmaximum refined radius `4.7369170150175137e-8`、minimum ratio `370.0132`、
maximum modulus upper `0.9920954876550118`、witness margin `4.72250069801592e-5`だった。
pilot値は証明digestへ使わず、独立runnerが全exact valueを再構成する。

### first degree-6 witness

Q011yへ送る最初のold-disc obstructionを固定する。

- overlap tuple: `[0,2,2,2]`
- source:
  `(block=16;center=151)^2 × (block=0;center=149)^2 × block=0;center=146 × block=0;center=147`
- output block: `15`
- target: `block=15;center=148`
- old product／target combined radius: 約`5.06026e-5`
- center distance: 約`4.73051e-5`
- old margin: 約`-3.29756e-6`

refined radiiで同じproduct centerとtriangle-inequality product radiusをexactに再計算する。ここでmarginが正でも、
残る143 old-overlap comparisonやdegree-6全体を本gateでは認証しない。

### validity gate

1. Q011k／Q011l／Q011u／Q011x artifact、runner、22 digest、outcome、claim boundaryとQ011o sourceを再現する。
2. 9 representativeのexact \(\beta\)、residual、vector norm、旧半径とQ011l thetaを再現する。
3. \(V^{-1}AV=D+V^{-1}(AV-VD)\)とinduced infinity norm／Gershgorin inclusionの有限次元前提を確認する。
4. 17 blockへのconjugate transport、2598 center、refined discの旧disc containmentを再現する。
5. refined stability、selected／external component containment、旧certificate preservationを再現する。
6. fixed degree-6 witnessのcenter、product radius、target radius、marginをexactに再現する。
7. finite strict JSON、input／radius／containment／witness／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、refined eigendiscもdegree-6 clearanceも主張しない。

### hypothesis gateと停止規則

1. transformed-residual eigendisc inclusionがexact norm boundから成り立つ。
2. maximum refined radius `<=5e-8`かつminimum improvement ratio `>=300`である。
3. 全2598 refined discのmodulus upper `<=0.9921<1`である。
4. 全refined discが対応するQ011k discに包含され、selected／external splitと既存結論を弱めない。
5. fixed degree-6 witness marginが`>=4e-5`である。

全5項目が通る場合だけ
`the Q011k eigenvalue families admit contained transformed-residual eigendiscs that clear the first degree-six enclosure obstruction`
として`accepted`とする。

witness marginが正にならなければ
`the transformed-residual eigendiscs do not clear the first degree-six enclosure obstruction`
として`rejected`とする。actual resonanceとは解釈しない。

`accepted`ならQ011zで3 degree-6 overlap aggregateの全sector-compatible monomialをrefined discで監査する。
`rejected`ならrow-wise transformed Gershgorinまたはtargeted interval eigenpairへ進む。`inconclusive`なら最初の
validity failureだけを修復する。

### 主張境界

本gateは固定17² repaired exact map、fixed conservation leaf、Q011k approximate eigendecomposition family、
transformed-residual eigendisc、fixed degree-6 witnessに限る。degree-6全体、degrees 7--90、all-order
nonresonance、Q011t graphとのhigher-order一致、SSM existence／uniqueness、normal attraction、basin、
他grid／force／wall、D3Q27を認証しない。Q011kの既存コミットやartifactは変更しない。

### Q011y 実行結果

Q011k／Q011l／Q011u／Q011x artifact、runner、22 digest、outcome、claim boundaryとQ011o sourceを照合し、
validity `7 / 7`を通過した。9 representative blockのinverse certificate、\(\beta\)、family residual、vector norm、
旧半径をexactに再構成し、Q011lの\(\theta=\beta\|AV-VD\|_\infty\)と全17 blockで一致した。

相似変換後の残差にinduced infinity normとGershgorin inclusionを適用して、半径\(\theta\)のunionがspectrumを
含むことを確認した。旧半径とのexact関係

\[
r_{\mathrm{old}}=\bigl(\|V\|_\infty\beta\bigr)\theta
\]

と\(\|V\|_\infty\beta\ge1\)から、全2598 refined discが対応する旧Q011k discに包含される。

- maximum refined radius: `4.7369170150175137e-8 <= 5e-8`
- minimum old／new ratio: `370.0132423109111 >= 300`
- eigendisc／selected／external count: `2598 / 24 / 2574`
- maximum refined modulus upper: `0.9920954876550118 <= 0.9921 < 1`
- old-disc containment failure: `0`

固定した`[0,2,2,2]`／external group 178の最初のwitnessでは、旧margin
`-3.2975560108425774e-6`がrefined margin `4.72250069801592e-5`へ改善し、登録下限`4e-5`を通過した。
hypothesis `5 / 5`を通過し、
`the Q011k eigenvalue families admit contained transformed-residual eigendiscs that clear the first degree-six enclosure obstruction`
として`accepted`とした。

- framed eigendisc digest:
  `7421634849c0f732045e576793863f758a09bddf6ab70205bfbd3aca45f9f18b`
- input／theorem／radius／containment／witness／result digest:
  `a31fe1606f7be3931567ec63bbad3037d38a9a57eef43f73d7b8f9afc7523c03` /
  `f3b9518fe67e85f0e701c4e6a97eac95db188ce85f813e358ddc0ecf85ba1ad5` /
  `70919d4697068d7500609551a17325533e83f40bb2e309f5e98b3313a6a93ee5` /
  `54e13cb993a0b99bc2d85dcf687d470cebe5692b4d10ab03865115230c53712c` /
  `933d2841e5501bd48827ead0ea836fb54ebca7f42e36f8bc6228c3f7dcfaaa4b` /
  `51d83bad9b0c2188c05b147f0075b5e7f05f3dea0dd291e0c282e9236914bff8`
- runner／artifact newline-normalized SHA-256:
  `0017ea849f518c69ce93a36db349bd8b18246b678fef9a54a48ae5f6f1acd187` /
  `2886708898f634b3ff85587f3f4b9257d35e14f25b4e3b4524fd01f4c12a254a`

これはlinear eigendisc refinementと最初の1 comparisonだけのcertificateである。degree 6全体、残る6955
comparison、degrees 7--90、higher graph smoothness、SSM existence／uniqueness、normal attraction、basinは
未認証である。停止規則どおり、次はQ011zで3 overlap aggregateの全6956 sector-compatible comparisonを監査する。

## Q011z: degree-6 uniform refined-envelope indexed-modulus audit — 事前登録

### 問い

Q011uでdegree 6に残った3 modulus-overlap aggregateについて、Q011yのtransformed-residual eigendiscを
block-independentな有理半径へ外向きに丸め、全可換coordinate monomialとFourier-sector-compatible external
targetをexact indexed modulusだけで分離できるか。

Q011uのdegree-6 inventoryは

- aggregate: `84 = 81 old-modulus-separated + 3 overlap`
- expanded product control: `462`
- overlap:
  - `[0,2,1,3]`／external group `178`
  - `[0,2,2,2]`／external group `178`
  - `[0,3,1,2]`／external group `177`

である。Q011zは3 overlapを個別indexへ展開し、Q011uの81 separationと合わせてdegree 6全体を判定する。

### uniform refined envelope

Q011yは全17 blockでtransformed-residual半径

\[
\theta_b=\beta_b\|A_bV_b-V_bD_b\|_\infty
\]

を認証し、\(\max_b\theta_b=4.7369170150175137\times10^{-8}\)を得た。Q011zでは

\[
\rho=\frac{1}{20{,}000{,}000}=5\times10^{-8}
\]

を固定し、全centerに\(D(c_j,\rho)\)を使う。従って

\[
D(c_j,\theta_b)\subset D(c_j,\rho).
\]

さらに全Q011k旧半径が\(\rho\)より大きいことをexactに確認し、uniform discも旧discに包含する。この丸めは
Q011y円板より大きいが、巨大な\(\theta_b\)分母をproductごとに掛けずに済み、証明計算を小さい固定分母で行える。

### 封印入力

Q011k／Q011u／Q011x／Q011yの4 artifactを直接照合する。

- Q011k artifact／runner newline-normalized SHA-256:
  `8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a` /
  `d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07`
- Q011k input／root／block／proof／result digest:
  `f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2` /
  `f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc` /
  `7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8` /
  `1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4` /
  `2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e`
- Q011u artifact／runner newline-normalized SHA-256:
  `4e0a74cffaeb6781b85621362d4463ac8d9ab98ee14bcf3b5764642b5a15d5e4` /
  `fa3c7c01355c0b3c19b58618fe97edc5863dc2d0fa02c4f810ddbc57053a419e`
- Q011u input／cutoff／spectrum／log／enumeration／tail／result digest:
  `ba768da7be5663c607a24fa4a399bae06a8d8b4128a45ab9bb2b57f8a12461f4` /
  `55a374a5d91d2c88e5e34be2173f9861ee14915daaee55efd8848f0cd7ebaf94` /
  `a514c3a13142d379886c56b08109f28b69aee4cbcef2d4c5c9bed8d29182e89d` /
  `10f9aa954446e1e7d8095488ef82abc48fcc99fde3ddabd93a1a188b17ea51b5` /
  `5c94deb8acd69b1346e6d46af829804b401027ecea48caf7e5ce2d9b22d6631c` /
  `307ca2762bb5aecb626983acb8d38eb5728e2a8eb9e64769cc0b632b40da66c6` /
  `b005bb622e7f3abad98a1ef6875af289fa2dccdc16911faf11e7ee04b822722c`
- Q011x artifact／runner newline-normalized SHA-256:
  `11ef4d47f60840c4bc05c4056024e2af14b8339a8983b65dcb878bd355cfc328` /
  `62712392faca2c154883edd93792f81e60ff975f6da16010aa3190ee44657a18`
- Q011x input／inventory／sector／product／result digest:
  `9d13fa470f4c0bd8efa13868af90c6931025d7f3007e600c66af05bd0037a7ed` /
  `717c4eadbd0e5f160a87de8846968933b8c5fbe604d769f215b6dcc65dacc955` /
  `d31b7ea3cfcd7eca9d936cded13a1dc316e64dc2fc088bda745ea927d15ce52c` /
  `add9d07725802c5fba84b68a207d5adc6f3f405a152a22f88059259f9a255222` /
  `608bb3a7aee34a833e7980dbd18f4a3e641426966352126833f298e282437b31`
- Q011y artifact／runner newline-normalized SHA-256:
  `2886708898f634b3ff85587f3f4b9257d35e14f25b4e3b4524fd01f4c12a254a` /
  `0017ea849f518c69ce93a36db349bd8b18246b678fef9a54a48ae5f6f1acd187`
- Q011y input／theorem／radius／containment／witness／result digest:
  `a31fe1606f7be3931567ec63bbad3037d38a9a57eef43f73d7b8f9afc7523c03` /
  `f3b9518fe67e85f0e701c4e6a97eac95db188ce85f813e358ddc0ecf85ba1ad5` /
  `70919d4697068d7500609551a17325533e83f40bb2e309f5e98b3313a6a93ee5` /
  `54e13cb993a0b99bc2d85dcf687d470cebe5692b4d10ab03865115230c53712c` /
  `933d2841e5501bd48827ead0ea836fb54ebca7f42e36f8bc6228c3f7dcfaaa4b` /
  `51d83bad9b0c2188c05b147f0075b5e7f05f3dea0dd291e0c282e9236914bff8`

direct digest countは`23`とする。center modulus再構成に使うQ011l／Q011o sourceも、それぞれ
`59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7` /
`60d9c445dace16d114e46263f2b47fe2db993b894337cdd462f204da09543f1f`
へ直接封印する。

### monomialとFourier sector

selected modulus group sizeは`8 / 4 / 4 / 8`である。combination with replacementにより、3 aggregateの
可換monomial数は

\[
4800,\qquad3600,\qquad2880,\qquad\text{total }11280
\]

となる。monomialのwave block histogramを次へ固定する。

- `[0,2,1,3]`:
  `0:820 / 1:760 / 2:600 / 3:380 / 4:178 / 5:60 / 6:12 / 11:12 / 12:60 / 13:178 / 14:380 / 15:600 / 16:760`
- `[0,2,2,2]`:
  `0:628 / 1:560 / 2:459 / 3:278 / 4:138 / 5:42 / 6:9 / 11:9 / 12:42 / 13:138 / 14:278 / 15:459 / 16:560`
- `[0,3,1,2]`:
  `0:420 / 1:404 / 2:348 / 3:260 / 4:150 / 5:56 / 6:12 / 11:12 / 12:56 / 13:150 / 14:260 / 15:348 / 16:404`

external group 178は4 targetでsector `2:2 / 15:2`、group 177は8 targetでsector
`0:4 / 3:2 / 14:2`である。exact Fourier law

\[
b_{\mathrm{out}}=(b_1+b_2+b_3+b_4+b_5+b_6)\bmod17
\]

からcompatible comparisonを`2400 / 1836 / 2720`、合計`6956`へ固定する。

### indexed modulus product enclosure

各source centerについてQ011oからexact rational

\[
\ell_i\le|c_i|\le u_i
\]

を得る。uniform disc productはcenter \(C=\prod_i c_i\)と

\[
R=\prod_{i=1}^{6}(u_i+\rho)-\prod_{i=1}^{6}u_i
\]

を持つ円板に含まれる。また

\[
\prod_i\ell_i\le|C|\le\prod_i u_i
\]

なので、product modulus intervalを

\[
I_p=\left[
\max\left(0,\prod_i\ell_i-R\right),
\prod_i u_i+R
\right]
\]

とする。target \(e\)には

\[
I_e=[\max(0,\ell_e-\rho),u_e+\rho]
\]

を使う。\(I_p\cap I_e=\varnothing\)ならcomplex phaseを計算せずstrict nonresonanceが従う。

### design-only pilotの開示

事前登録用のexact-rational pilotでは、uniform \(\rho=5\times10^{-8}\)でも3 aggregateの全6956比較が
individual modulusで分離した。aggregate別minimum gapは

- `[0,2,1,3]`: `1.6311010454743865e-5`
- `[0,2,2,2]`: `4.6970543553274824e-5`
- `[0,3,1,2]`: `6.7565223274027445e-6`

だった。global witnessは

`(block=16;center=151)^3 × block=0;center=149 × (block=0;center=147)^2`

対target `block=14;center=143`である。登録minimum gapは`5e-6`とする。pilotのexact valueや一時計算を
proof digestへ流用せず、独立runnerがinventory、全monomial、全comparison、minimum witnessを再構成する。

### validity gate

1. Q011k／Q011u／Q011x／Q011y artifact、runner、23 digest、outcome、claim boundaryとQ011l／Q011o sourceを再現する。
2. degree-6の84 aggregate、462 expanded control、81 separation、3 overlap tuple／external groupを再現する。
3. Q011yの全\(\theta_b\le\rho\)、全Q011k旧半径\(\ge\rho\)、source／target refined modulus intervalを再現する。
4. group membership、11280 monomial、wave histogram、`4 / 4 / 8` target entry（12 unique）、6956 compatible comparisonを再現する。
5. 全product radius、center-modulus product interval、target interval、strict gap、framed exact-record digestを再現する。
6. Q011uの81 separationと3 full indexed auditが84 aggregateを重複なく被覆することを再現する。
7. finite strict JSON、input／inventory／sector／product／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、degree-6 nonresonanceを主張しない。

### hypothesis gateと停止規則

1. uniform \(\rho\)-discが全Q011y spectral enclosureを含み、全Q011k旧discに含まれる。
2. 84 aggregate、11280 monomial、6956 comparisonがdegree 6を完全被覆する。
3. 6956 comparisonすべてがindividual modulus separationで、unresolvedが0である。
4. global minimum exact modulus gapが`>=5e-6`である。
5. Q011uの81 old separationと3 refined full auditからdegree-6 external nonresonanceが従う。

全5項目が通る場合だけ
`degree-6 external nonresonance is certified by a contained uniform transformed-residual envelope and exact Fourier-sector indexed-modulus products`
として`accepted`とする。certified degreesを2／3／4／5／6、tail-certifiedを91以降、missing rangeを
degrees 7--90へ更新する。

1件でもinterval overlapが残れば
`at least one degree-6 refined indexed-modulus product remains inseparable from an external target`
として`rejected`とする。actual resonanceとは解釈せず、最初のoverlapだけをexact complex phaseへ送る。

`accepted`ならQ011aaでdegree 7へ進む。`rejected`ならQ011aaで最初のremaining productだけをphase-sensitive
complex discへ送る。`inconclusive`なら最初のvalidity failureだけを修復する。

### 主張境界

本gateは固定17² repaired exact map、fixed conservation leaf、degree 6、Q011uの3 overlap aggregate、
Q011y transformed-residual enclosure、uniform \(\rho\)-disc、x-Fourier sector、indexed modulus product formulaに
限る。degrees 7--90、all-order nonresonance、Q011t graphとのhigher-order一致、\(C^2\)以上のgraph smoothness、
SSM existence／uniqueness、normal attraction、basin、他grid／force／wall、D3Q27を認証しない。

### Q011z 実行結果

Q011k／Q011u／Q011x／Q011y artifact、runner、23 direct digest、outcome、claim boundaryと
Q011l／Q011o sourceを照合し、validity `7 / 7`を通過した。degree-6 inventoryは
`84 aggregate / 462 expanded control / 81 old-separated / 3 overlap`で事前登録どおりだった。

一様半径\(\rho=5\times10^{-8}\)について、全17 blockで
\(\theta_b\le\rho\le r_{\mathrm{old},b}\)をexactに確認した。積へ現れる28 identifierのuniform modulus
intervalも再構成した。最大\(\theta_b\)は`4.7369170150175137e-8`、最小旧半径は
`3.8891601146814717e-7`だった。

3 overlapの`4800 / 3600 / 2880` monomial、合計`11280`を列挙し、Fourier sectorで
`2400 / 1836 / 2720`、合計`6956` comparisonへ絞った。全比較がindividual modulusで分離し、
unresolvedは`0`だった。aggregate別minimum exact gapは

- `1.6311010454743865e-5`
- `4.6970543553274824e-5`
- `6.7565223274027445e-6`

で、global minimumは登録下限`5e-6`を通過した。minimum witnessは
`(block=16;center=151)^3 × block=0;center=149 × (block=0;center=147)^2`
対target `block=14;center=143`で、`product_below_target`だった。

hypothesis `5 / 5`を通過し、
`degree-6 external nonresonance is certified by a contained uniform transformed-residual envelope and exact Fourier-sector indexed-modulus products`
として`accepted`とした。certified degreesは2／3／4／5／6、tail-certifiedは91以降、missing rangeは
degrees 7--90へ更新した。

- monomial／compatible-pair framed digest:
  `2115b6f7affd09687908eb6dc6193d20701167102dbfdf138359091799e06d70` /
  `aa30254a73d854d1d654e749abd863b11a4d87a624593c436397eb77880a411f`
- exact-product／comparison framed digest:
  `b9cc4cbab096815f81c15ffeae3b7e78accb0ff68fd15ee6c93549c85e1c2dfd` /
  `6a61466b0efc2a170d3d43d43b5cc899f1aae198870abc98e80640f543c39ea0`
- input／inventory／sector／product／result digest:
  `394728b15820900b642776843b96b7383b31fec27bede2274d97ee9c635054bb` /
  `46248ce31e7e04039eb9eb1788d42f04d19dd949b026a921e61812ab3d37e8cc` /
  `b172439520fa25bba82fa936564ebc0ae51763a57006cb279d1e3fe9f0ed0a3c` /
  `148acb302034412498638201703eee8722f90afa093adcf6215094170e4a8c1e` /
  `a695e5c632e6dda8114377f33824ca6b234ebadae7c25d6b8aa1c3d3774c4aff`
- runner／artifact newline-normalized SHA-256:
  `6e6d7327e4b85b307098203fe882434bf77f3920a1da7323b1c89d118df3ae87` /
  `bd435ceea3795475f6b17619e13626ba936f8fcbd15da749a39a4e2b034a4e23`

この結果はdegree 6だけのcertificateであり、degrees 7--90、all-order nonresonance、Q011t graphとの
higher-order一致、\(C^2\)以上のsmoothness、SSM existence／uniqueness、normal attraction、basinは
未認証である。停止規則どおり、次はQ011aaでdegree 7を監査する。

## Q011aa: degree-7 uniform refined-envelope indexed-modulus audit — 事前登録

### 問い

Q011uでdegree 7に残った5 modulus-overlap aggregateについて、Q011yからQ011zへ継承したuniform
transformed-residual envelopeを使い、全可換coordinate monomialとFourier-sector-compatible external
targetをexact indexed modulusだけで分離できるか。

Q011uのdegree-7 inventoryは

- aggregate: `120 = 115 old-modulus-separated + 5 overlap`
- expanded product control: `792`
- overlap:
  - `[0,1,1,5]` / external group `178`
  - `[0,1,2,4]` / external group `178`
  - `[0,2,0,5]` / external group `177`
  - `[0,2,1,4]` / external group `177`
  - `[0,2,2,3]` / external group `177`

である。Q011aaは5 overlapを個別indexへ展開し、Q011uの115 separationと合わせてdegree 7全体を判定する。

### uniform refined envelope

Q011zと同じ

\[
\rho=\frac{1}{20{,}000{,}000}=5\times10^{-8}
\]

を固定する。Q011yが認証した全17 blockのtransformed-residual半径は
\(\theta_b\le\rho\)、全Q011k旧半径は\(r_{\mathrm{old},b}\ge\rho\)である。従って

\[
D(c_j,\theta_b)\subseteq D(c_j,\rho)\subseteq D(c_j,r_{\mathrm{old},b})
\]

を保つ。5 overlapで正のmultiplicityを持つselected groupは1／2／3だけなので、16 selected identifierと
12 unique external target、合計28 identifierのcenter-modulus intervalを再構成する。

### sealed input

Q011zで直接照合したQ011k／Q011u／Q011x／Q011yのartifact、runner、23 digest、outcome、
claim boundaryとQ011l／Q011o sourceを同じ固定値で再照合する。さらにQ011zを直接封印する。

- Q011z artifact／runner newline-normalized SHA-256:
  `bd435ceea3795475f6b17619e13626ba936f8fcbd15da749a39a4e2b034a4e23` /
  `6e6d7327e4b85b307098203fe882434bf77f3920a1da7323b1c89d118df3ae87`
- Q011z input／inventory／sector／product／result digest:
  `394728b15820900b642776843b96b7383b31fec27bede2274d97ee9c635054bb` /
  `46248ce31e7e04039eb9eb1788d42f04d19dd949b026a921e61812ab3d37e8cc` /
  `b172439520fa25bba82fa936564ebc0ae51763a57006cb279d1e3fe9f0ed0a3c` /
  `148acb302034412498638201703eee8722f90afa093adcf6215094170e4a8c1e` /
  `a695e5c632e6dda8114377f33824ca6b234ebadae7c25d6b8aa1c3d3774c4aff`

direct digest countは`28`とする。

### monomialとFourier sector

selected modulus group sizeは`8 / 4 / 4 / 8`である。combination with replacementによる5 aggregateの
可換monomial数を

\[
12672,\qquad13200,\qquad7920,\qquad13200,\qquad12000,
\qquad\text{total }58992
\]

へ固定する。monomialのoutput wave histogramは次とする。

- `[0,1,1,5]`:
  `0:2192 / 1:2008 / 2:1520 / 3:944 / 4:488 / 5:204 / 6:64 / 7:12 / 10:12 / 11:64 / 12:204 / 13:488 / 14:944 / 15:1520 / 16:2008`
- `[0,1,2,4]`:
  `0:2320 / 1:2138 / 2:1588 / 3:982 / 4:480 / 5:190 / 6:52 / 7:10 / 10:10 / 11:52 / 12:190 / 13:480 / 14:982 / 15:1588 / 16:2138`
- `[0,2,0,5]`:
  `0:1240 / 1:1144 / 2:944 / 3:644 / 4:356 / 5:174 / 6:60 / 7:18 / 10:18 / 11:60 / 12:174 / 13:356 / 14:644 / 15:944 / 16:1144`
- `[0,2,1,4]`:
  `0:2120 / 1:1975 / 2:1590 / 3:1065 / 4:572 / 5:245 / 6:78 / 7:15 / 10:15 / 11:78 / 12:245 / 13:572 / 14:1065 / 15:1590 / 16:1975`
- `[0,2,2,3]`:
  `0:1952 / 1:1808 / 2:1452 / 3:966 / 4:512 / 5:214 / 6:60 / 7:12 / 10:12 / 11:60 / 12:214 / 13:512 / 14:966 / 15:1452 / 16:1808`

external group 178は4 targetでsector `2:2 / 15:2`、group 177は8 targetで
sector `0:4 / 3:2 / 14:2`である。exact Fourier law

\[
b_{\mathrm{out}}=(b_1+\cdots+b_7)\bmod17
\]

によりcompatible comparisonを`6080 / 6352 / 7536 / 12740 / 11672`、合計`44380`へ固定する。
compatible monomialは`16878`、incompatible monomialは`42114`である。

### indexed modulus product enclosure

各source centerについてexact rational \(\ell_i\le|c_i|\le u_i\)を再構成する。degree 7のuniform
disc productを

\[
R=\prod_{i=1}^{7}(u_i+\rho)-\prod_{i=1}^{7}u_i,
\qquad
I_p=\left[
\max\left(0,\prod_i\ell_i-R\right),
\prod_i u_i+R
\right]
\]

とし、target \(e\)には

\[
I_e=[\max(0,\ell_e-\rho),u_e+\rho]
\]

を使う。\(I_p\cap I_e=\varnothing\)ならcomplex phaseを計算せずstrict nonresonanceが従う。

### design-only pilotの開示

事前登録用のexact-rational pilotでは、全44380 comparisonがindividual modulusで分離し、
unresolvedは0だった。relation countはproduct below target `30764`、target below product `13616`である。
aggregate別minimum gapは

- `[0,1,1,5]`: `1.6371355291399596e-5`
- `[0,1,2,4]`: `4.681636472938023e-5`
- `[0,2,0,5]`: `5.608507807101488e-5`
- `[0,2,1,4]`: `6.603546614599508e-6`
- `[0,2,2,3]`: `7.004874435925448e-5`

だった。global witnessは

`(block=16;center=151)^2 × block=16;center=152 × (block=0;center=147)^4`

対target `block=14;center=143`で、relationは`product_below_target`である。登録minimum gapは`5e-6`とする。
pilotのexact value、一時計算、stream digestはproof artifactへ流用せず、独立runnerがinventory、全monomial、
全comparison、minimum witnessを再構成する。

### validity gate

1. Q011k／Q011u／Q011x／Q011y／Q011z artifact、runner、28 digest、outcome、claim boundaryとQ011l／Q011o sourceを再現する。
2. degree-7の120 aggregate、792 expanded control、115 separation、5 overlap tuple／external groupを再現する。
3. 全\(\theta_b\le\rho\le r_{\mathrm{old},b}\)と28 relevant refined modulus intervalを再現する。
4. group membership、58992 monomial、wave histogram、target histogram、44380 compatible comparisonを再現する。
5. 全product radius、center-modulus product interval、target interval、strict gap、framed exact-record digestを再現する。
6. Q011uの115 separationと5 full indexed auditが120 aggregateを重複なく被覆することを再現する。
7. finite strict JSON、input／inventory／sector／product／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、degree-7 nonresonanceを主張しない。

### hypothesis gateと停止規則

1. uniform \(\rho\)-discが全Q011y spectral enclosureを含み、全Q011k旧discに含まれる。
2. 120 aggregate、58992 monomial、44380 comparisonがdegree 7を完全被覆する。
3. 44380 comparisonすべてがindividual modulus separationで、unresolvedが0である。
4. global minimum exact modulus gapが`>=5e-6`である。
5. Q011uの115 old separationと5 refined full auditからdegree-7 external nonresonanceが従う。

全5項目が通る場合だけ
`degree-7 external nonresonance is certified by the contained uniform transformed-residual envelope and exact Fourier-sector indexed-modulus products`
として`accepted`とする。certified degreesを2／3／4／5／6／7、tail-certifiedを91以降、missing rangeを
degrees 8--90へ更新する。

1件でもinterval overlapが残れば
`at least one degree-7 refined indexed-modulus product remains inseparable from an external target`
として`rejected`とする。actual resonanceとは解釈せず、最初のoverlapだけをexact complex phaseへ送る。

`accepted`ならQ011abでdegree 8へ進む。`rejected`ならQ011abで最初のremaining productだけを
phase-sensitive complex discへ送る。`inconclusive`なら最初のvalidity failureだけを修復する。

### 主張境界

本gateは固定17² repaired exact map、fixed conservation leaf、degree 7、Q011uの5 overlap aggregate、
Q011y transformed-residual enclosure、uniform \(\rho\)-disc、x-Fourier sector、indexed modulus product
formulaに限る。degrees 8--90、all-order nonresonance、Q011t graphとのhigher-order一致、\(C^2\)以上の
graph smoothness、SSM existence／uniqueness、normal attraction、basin、他grid／force／wall、D3Q27を認証しない。

### Q011aa 実行結果

Q011k／Q011u／Q011x／Q011y／Q011z artifact、runner、28 direct digest、outcome、claim boundaryと
Q011l／Q011o sourceを照合し、validity `7 / 7`を通過した。degree-7 inventoryは
`120 aggregate / 792 expanded control / 115 old-separated / 5 overlap`で事前登録どおりだった。

一様\(\rho=5\times10^{-8}\)円板の包含と28 relevant identifierを再構成した。5 overlapの
`12672 / 13200 / 7920 / 13200 / 12000` monomial、合計`58992`を列挙し、Fourier sectorで
`6080 / 6352 / 7536 / 12740 / 11672`、合計`44380` comparisonへ絞った。

全44380 comparisonがindividual modulusで分離し、unresolvedは`0`だった。relation countは
product below target `30764`、target below product `13616`である。aggregate別minimum exact gapは

- `1.6371355291399596e-5`
- `4.681636472938023e-5`
- `5.608507807101488e-5`
- `6.603546614599508e-6`
- `7.004874435925448e-5`

で、global minimumは登録下限`5e-6`を通過した。minimum witnessは
`(block=16;center=151)^2 × block=16;center=152 × (block=0;center=147)^4`
対target `block=14;center=143`で、`product_below_target`だった。

hypothesis `5 / 5`を通過し、
`degree-7 external nonresonance is certified by the contained uniform transformed-residual envelope and exact Fourier-sector indexed-modulus products`
として`accepted`とした。certified degreesは2／3／4／5／6／7、tail-certifiedは91以降、missing rangeは
degrees 8--90へ更新した。

- monomial／compatible-pair framed digest:
  `5e2a0d986b63eb77a4f67ae2c79c0f1ed6acb3531317f530bf82b95ebb45c43b` /
  `36bb54954525bf0867d5fdf31523bd20bd72971acbbd6d5135f7e70523d403c1`
- exact-product／comparison framed digest:
  `ff476eaf7cb575058d7a43002ce56e4f7e5bd733c52347832237f4b8d4c2f0a3` /
  `348a32179485b1f5766787262ea163d36f951eb76bc049070a8d3c0074844c73`
- input／inventory／sector／product／result digest:
  `9d460085b29b9a3e094bc6ed19fd94908a0f9d5507f5c1901b0f8b5e7da3cb76` /
  `c7c6d89542c1b8d563e091530b2bd07aadbd2e4eedf5db3be7b86a9d68b97a65` /
  `4c70de8129596fa631392014f44514290906efa9d2000bf865a9a8700f65d080` /
  `ca37525b63f7e906b352dd86bf0b16b79954b88fd7b6066f880f8b00e474b7fb` /
  `c136c7e2963ef5700a1d1c969ea67f7463db390f6141427a517092ac9e0b44e4`
- runner／artifact newline-normalized SHA-256:
  `d5db6eb414ebc0479fbf91e62b9a3618c675556aa80df2e693a39171ee838c70` /
  `f9485e0dc57b2cf55de6867627893eca2defd45fbf1d64a1654d6cab0efcdf85`

この結果はdegree 7だけのcertificateであり、degrees 8--90、all-order nonresonance、higher graph
smoothness、SSM existence／uniqueness、normal attraction、basinは未認証である。停止規則どおり、
次はQ011abでdegree 8を監査する。

## Q011ab: degree-8 uniform refined-envelope indexed-modulus audit — 事前登録

### 問い

Q011uでdegree 8に残った7 modulus-overlap aggregateについて、uniform transformed-residual envelopeを
external group 167まで拡張し、全可換coordinate monomialとFourier-sector-compatible targetをexact
indexed modulusだけで分離できるか。

Q011uのdegree-8 inventoryは

- aggregate: `165 = 158 old-modulus-separated + 7 overlap`
- expanded product control: `1287`
- overlap／external group:
  - `[0,0,0,8] / 178`
  - `[0,0,1,7] / 178`
  - `[0,0,2,6] / 178`
  - `[0,1,0,7] / 177`
  - `[0,1,1,6] / 177`
  - `[0,1,2,5] / 177`
  - `[0,8,0,0] / 167`

である。Q011abは7 overlapを個別indexへ展開し、Q011uの158 separationと合わせてdegree 8全体を判定する。

### uniform refined envelopeと新external group

半径はQ011z／Q011aaと同じ

\[
\rho=\frac{1}{20{,}000{,}000}=5\times10^{-8}
\]

とする。全blockで\(\theta_b\le\rho\le r_{\mathrm{old},b}\)を再確認する。selected group 1／2／3の
16 identifierに加え、external group 178／177／167の`4 / 8 / 8` identifierを使う。3 external groupは
互いにdisjointなので、unique externalは`20`、relevant identifierは`36`である。group 167のsector
histogramは`0:4 / 4:2 / 13:2`である。

### sealed input

Q011aaで直接照合したQ011k／Q011u／Q011x／Q011y／Q011zのartifact、runner、28 digest、outcome、
claim boundaryとQ011l／Q011o sourceを同じ固定値で再照合し、Q011aaも直接封印する。

- Q011aa artifact／runner newline-normalized SHA-256:
  `f9485e0dc57b2cf55de6867627893eca2defd45fbf1d64a1654d6cab0efcdf85` /
  `d5db6eb414ebc0479fbf91e62b9a3618c675556aa80df2e693a39171ee838c70`
- Q011aa input／inventory／sector／product／result digest:
  `9d460085b29b9a3e094bc6ed19fd94908a0f9d5507f5c1901b0f8b5e7da3cb76` /
  `c7c6d89542c1b8d563e091530b2bd07aadbd2e4eedf5db3be7b86a9d68b97a65` /
  `4c70de8129596fa631392014f44514290906efa9d2000bf865a9a8700f65d080` /
  `ca37525b63f7e906b352dd86bf0b16b79954b88fd7b6066f880f8b00e474b7fb` /
  `c136c7e2963ef5700a1d1c969ea67f7463db390f6141427a517092ac9e0b44e4`

direct digest countは`33`とする。

### monomialとFourier sector

selected modulus group size`8 / 4 / 4 / 8`から、7 aggregateの可換monomial数を

\[
6435,\ 13728,\ 17160,\ 13728,\ 27456,\ 31680,\ 165,
\qquad\text{total }110352
\]

へ固定する。output wave histogramは次とする。

- `[0,0,0,8]`:
  `0:1001 / 1:896 / 2:706 / 3:496 / 4:316 / 5:176 / 6:86 / 7:32 / 8:9 / 9:9 / 10:32 / 11:86 / 12:176 / 13:316 / 14:496 / 15:706 / 16:896`
- `[0,0,1,7]`:
  `0:2212 / 1:2012 / 2:1552 / 3:1052 / 4:628 / 5:324 / 6:138 / 7:44 / 8:8 / 9:8 / 10:44 / 11:138 / 12:324 / 13:628 / 14:1052 / 15:1552 / 16:2012`
- `[0,0,2,6]`:
  `0:2840 / 1:2580 / 2:1992 / 3:1308 / 4:743 / 5:354 / 6:138 / 7:38 / 8:7 / 9:7 / 10:38 / 11:138 / 12:354 / 13:743 / 14:1308 / 15:1992 / 16:2580`
- `[0,1,0,7]`:
  `0:2072 / 1:1952 / 2:1552 / 3:1072 / 4:664 / 5:352 / 6:164 / 7:56 / 8:16 / 9:16 / 10:56 / 11:164 / 12:352 / 13:664 / 14:1072 / 15:1552 / 16:1952`
- `[0,1,1,6]`:
  `0:4360 / 1:4040 / 2:3184 / 3:2136 / 4:1238 / 5:612 / 6:248 / 7:76 / 8:14 / 9:14 / 10:76 / 11:248 / 12:612 / 13:1238 / 14:2136 / 15:3184 / 16:4040`
- `[0,1,2,5]`:
  `0:5152 / 1:4768 / 2:3720 / 3:2456 / 4:1372 / 5:632 / 6:240 / 7:64 / 8:12 / 9:12 / 10:64 / 11:240 / 12:632 / 13:1372 / 14:2456 / 15:3720 / 16:4768`
- `[0,8,0,0]`:
  `0:25 / 2:24 / 4:21 / 6:16 / 8:9 / 9:9 / 11:16 / 13:21 / 15:24`

external group 178のsectorは`2:2 / 15:2`、177は`0:4 / 3:2 / 14:2`、167は
`0:4 / 4:2 / 13:2`である。exact Fourier law

\[
b_{\mathrm{out}}=(b_1+\cdots+b_8)\bmod17
\]

によりcompatible comparisonを`2824 / 6208 / 7968 / 12576 / 25984 / 30432 / 184`、
合計`86176`へ固定する。compatible／incompatible monomialは`31479 / 78873`である。

### indexed modulus product enclosure

各source centerのexact rational modulus区間から

\[
R=\prod_{i=1}^{8}(u_i+\rho)-\prod_{i=1}^{8}u_i,
\qquad
I_p=\left[\max\left(0,\prod_i\ell_i-R\right),\prod_i u_i+R\right]
\]

を作り、target \(I_e=[\max(0,\ell_e-\rho),u_e+\rho]\)と比較する。

### design-only pilotの開示

事前登録用のexact-rational pilotでは全86176 comparisonがindividual modulusで分離し、unresolvedは0だった。
relation countはproduct below target `64568`、target below product `21608`である。aggregate別minimum gapは

- `[0,0,0,8]`: `8.038671735506002e-5`
- `[0,0,1,7]`: `1.6431705364740245e-5`
- `[0,0,2,6]`: `4.666218064574062e-5`
- `[0,1,0,7]`: `5.614493817136191e-5`
- `[0,1,1,6]`: `6.450587884958278e-6`
- `[0,1,2,5]`: `6.989577904616183e-5`
- `[0,8,0,0]`: `7.650184466921042e-4`

だった。global witnessは

`block=16;center=151 × block=16;center=152 × (block=0;center=147)^5 × block=16;center=149`

対target `block=14;center=143`で、relationは`product_below_target`である。登録minimum gapは`5e-6`とする。
pilotの一時計算とstream digestはproofへ流用せず、独立runnerが全recordを再構成する。

### validity gate

1. Q011k／Q011u／Q011x／Q011y／Q011z／Q011aa artifact、runner、33 digest、outcome、claim boundaryとQ011l／Q011o sourceを再現する。
2. degree-8の165 aggregate、1287 expanded control、158 separation、7 overlap tuple／external groupを再現する。
3. 全\(\theta_b\le\rho\le r_{\mathrm{old},b}\)と36 relevant modulus intervalを再現する。
4. group membership、110352 monomial、wave／target histogram、86176 compatible comparisonを再現する。
5. 全product interval、target interval、strict gap、framed exact-record digestを再現する。
6. Q011uの158 separationと7 full indexed auditが165 aggregateを重複なく被覆することを再現する。
7. finite strict JSON、input／inventory／sector／product／result digest、runner provenanceを再現する。

一つでも落ちれば`inconclusive`とし、degree-8 nonresonanceを主張しない。

### hypothesis gateと停止規則

1. uniform \(\rho\)-discが全Q011y enclosureを含み、全Q011k旧discに含まれる。
2. 165 aggregate、110352 monomial、86176 comparisonがdegree 8を完全被覆する。
3. 全86176 comparisonがindividual modulus separationで、unresolvedが0である。
4. global minimum exact modulus gapが`>=5e-6`である。
5. Q011uの158 old separationと7 refined full auditからdegree-8 external nonresonanceが従う。

全5項目が通る場合だけ
`degree-8 external nonresonance is certified by the contained uniform transformed-residual envelope and exact Fourier-sector indexed-modulus products`
として`accepted`とする。certified degreesを2--8、tail-certifiedを91以降、missing rangeをdegrees 9--90へ更新する。

1件でもinterval overlapが残れば
`at least one degree-8 refined indexed-modulus product remains inseparable from an external target`
として`rejected`とし、最初のoverlapだけをexact complex phaseへ送る。

`accepted`ならQ011acでdegree 9へ進む。`rejected`ならQ011acで最初のremaining productをphase-sensitive
complex discへ送る。`inconclusive`なら最初のvalidity failureだけを修復する。

### 主張境界

本gateは固定17² repaired exact map、fixed conservation leaf、degree 8、Q011uの7 overlap aggregate、
Q011y transformed-residual enclosure、uniform \(\rho\)-disc、x-Fourier sector、indexed modulus product
formulaに限る。degrees 9--90、all-order nonresonance、higher graph smoothness、SSM existence／uniqueness、
normal attraction、basin、他grid／force／wall、D3Q27を認証しない。

### Q011ab 実行結果

6 artifact、runner、33 direct digest、outcome、claim boundaryとQ011l／Q011o sourceを照合し、
validity `7 / 7`を通過した。degree-8 inventoryは
`165 aggregate / 1287 expanded control / 158 old-separated / 7 overlap`で事前登録どおりだった。

external group 167を加えた36 relevant identifierのuniform envelopeを再構成し、Q011aaの既存28 recordが
exactに保存されることを確認した。`110352` monomialを列挙し、Fourier sectorで`86176` comparisonへ
絞った。全比較がindividual modulusで分離し、unresolvedは`0`だった。relation countはproduct below
target `64568`、target below product `21608`である。

aggregate別minimum exact gapは

- `8.038671735506002e-5`
- `1.6431705364740245e-5`
- `4.666218064574062e-5`
- `5.614493817136191e-5`
- `6.450587884958278e-6`
- `6.989577904616183e-5`
- `7.650184466921042e-4`

で、global minimumは登録下限`5e-6`を通過した。minimum witnessは
`block=16;center=151 × block=16;center=152 × (block=0;center=147)^5 × block=16;center=149`
対target `block=14;center=143`だった。

hypothesis `5 / 5`を通過し、
`degree-8 external nonresonance is certified by the contained uniform transformed-residual envelope and exact Fourier-sector indexed-modulus products`
として`accepted`とした。certified degreesは2--8、tail-certifiedは91以降、missing rangeはdegrees 9--90である。

- monomial／compatible-pair framed digest:
  `d9f73a519d424484597bd7a17496ba0315f87c1bd7e8116c0bb588469c90e1e4` /
  `c1145c61b8e044d445fd4c56108d685e28af2a15bb6e88ac4912b8c632f8f6ad`
- exact-product／comparison framed digest:
  `127f856813ba1910b35d367880e021e6ffbc42b9bb33ae4789ebfd35cac907ff` /
  `3b1df1e1a54a1e9c27c5f3c829b6ca119669c53a9249fee109c407b0da4d1e0f`
- input／inventory／sector／product／result digest:
  `cbb93d239d4f23ec2ca3fb4dd2bb1bdc89af5756c5f2918ccb303c3442f233d9` /
  `dd22f821362306d7c7bf9513a8f990253134f989a997ec5fb2677b6a1b9ad967` /
  `3d523a17677d993113d9d17a515485db00759e490514bdbe287c6927c6525c9f` /
  `c12cee86ac5e4a9aa56a9e86996eb40756c3d327a9838aba5443b67a42177663` /
  `73c7d110f06596d5b03eead1d2b36b5975a2ca0b451c1c0b4ee13c1d4bb3f949`
- runner／artifact newline-normalized SHA-256:
  `dc4511ea76419b065c5de7b84d02e040b98f50c31e863b6232afdfaedf0f677b` /
  `18a6e146d0d24af9e9bab22f45668bec6c5bc25efcdb05faee2a7228e1870a98`

この結果はdegree 8だけのcertificateであり、degrees 9--90、all-order nonresonance、higher graph
smoothness、SSM existence／uniqueness、normal attraction、basinは未認証である。停止規則どおり、
次はQ011acでdegree 9を監査する。

## Q012: D3Q27 へ移してよいか

D2Q9 で次を全て満たして初めて進む。

- branch/cluster tracking
- Q005 sector-aware nonresonance
- fixed-leaf nonzero-mode quadratic residual order
- same-initial repaired-MPFR all-iterate forward shadowing（Q007ap拡大tube通過）
- representation fidelityとnatural-sparse multi-step equivalence（Q011g／Q011h通過）
- mandatory sparse baselineに勝つTT候補が出た場合のみTT-cross independent validation
- positivity/conservation
- sparse baselineを含むcost report（Q010通過、固定TT-SVD path棄却）

D3Q27 の最初の問いは、D1Q3 tensor-product construction が quadrature、moment、
\(z\)-independent limit、回転等方性を同時に満たすかである。
