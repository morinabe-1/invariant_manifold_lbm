# TT parameterized invariant-manifold LBM

このリポジトリは、既存の `tci` 系統とは独立した研究プロジェクトである。完全な
LBM 1-step 写像

\[
\Phi:\mathbb{R}^{N}\to\mathbb{R}^{N}
\]

に対して、埋込み \(W\) と縮約写像 \(R\) を

\[
\Phi(W(a))=W(R(a))
\]

から同時に構成し、多変数係数を tensor train (TT) で圧縮することを目的とする。
最初の対象は周期境界・無外力・BGK の D2Q9、最終的な拡張先は D3Q27 である。

## 現時点の判定

研究方向は Go である。ただし Q005 により、Q004b cutoff をそのまま使う2次元
isotropic low-wave set は、標準的な nonresonant・normally-attracting SSM 候補として
棄却された。これは研究計画全体の棄却ではなく、最初の reduced set の反証である。
Q006s では非線形に不変な \(y\)-independent stripe 上の coefficient solver を
有限格子オラクルとして受理した。Q006r では diagonal shear orbit を加えた16実座標
候補の coefficient closure は通過したが、near-Nyquist 外部モードにより有限格子の
linear normal-dominance は棄却された。Q006n では登録した全20条件でこの負の gap を
再現した一方、3個の高解像度条件が別の small-wave coefficient condition gate を落とした。
従って封印した clean-obstruction 仮説の判定は `inconclusive` である。Q006c は
second-harmonic near resonance が真の \(N^{-2}\) spectral separationを持ち、
local-amplitude response は \(O(N)\)、global-\(\ell_2\) response は \(O(1)\) となる
二重の scaling を支持した。Q006f の保存的checkerboard filterは全algebra・coefficient
gateを通したが、登録20 family全てがnormal-gap gateを落とし、viable pairは0だった。
Q006gは、フィルタ後の律速となった対角第一shell内のshear/acoustic gapが符号付きで
\(N^{-4}\)となり、scalar filterでは順序も指数も変えられないことを確認した。Q006hは
diagonal acousticも含む24実座標cluster-complete familyを100条件で監査し、6 familyを
viableと判定した。事前登録した規則で \((\eta,\omega)=(0.01,1.5)\) を選択し、Q006iで
\(17^2\) 上のfull 2D dense quadratic chartを構築した。構成・独立Hessian・残差次数・
shadowingのgateは通過したが、100-step global conservation driftが登録上限 \(10^{-12}\) に
対して \(2.72850\times10^{-12}\) となったため、Q006iは単一gateで`rejected`と固定する。
linear／quadratic chartでほぼ同じdriftであることから、次は閾値を変更せず、Q006jで
保存量の集約とfloat64写像の各stageに分解して発生源を診断した。補償和でもdriftを再現し、
collisionとfilterへ分解できたが、一様fixed-leaf projectionが登録上限を通らなかったため、
Q006jは`structural or unresolved conservation defect`として`rejected`である。次はQ006kで
この投影失敗がfloat64分散補正の不完全な実現に由来するかを監査した。全6,400 stepで
intended／realized moment correctionが不一致となり、固定3-population controlは保存上限を
通過したため、Q006kは診断範囲で`accepted`である。ただし固定site依存は採用せず、次のQ006lで
collision／filter各stageの状態共変anchor correctionがtranslation／C4と保存を同時に満たすかを
監査した。登録64 trajectoryでは保存・generator equivariance・anchor uniquenessを全て通過し、
Q006lは有限軌道上で`accepted`となった。ただし一様平衡ではanchorが289重に縮退するため、Q006mで
unique-anchor classのequivariant differentiability obstructionを監査した。一様状態はtranslationで
不変だが周期site作用には固定点がなく、全8本のgap ladderも縮退へ向かったため、Q006mは
`accepted`である。従ってQ006lのunique-anchor correctionは局所production mapへ採用しない。次の
Q006oでは、anchor-freeな一様smooth correctionと、写像を変更しない明示的forward-error budgetを
比較した。標準写像は全19,200 component-stepで登録budgetを通過し、一様projectionは改善率とexact
realizationをともに落としたため、Q006oはunmodified map policyを`accepted`とした。Q006pでは、
旧 \(10^{-12}\) 判定を保持したoriginal columnがglobal conservationだけを失敗し、同じ64 trajectoryの
policy columnは全8 gateを通過した。従ってQ006pは条件付きchart continuationを`accepted`としたが、
同一データの再利用に限る。Q006qでは別seed・振幅・horizonの128 trajectory、16,000 step、
48,000 component checkを行い、違反0、最大utilization `0.5`で独立holdoutを通過した。次のQ007aで
3次homological operatorの全2,600 unordered tripleをprequalificationし、singular block 0、最大condition
`10821.8`で通過した。Q007bでは全cubic forcing・係数を構築し、独立3次微分、homological equation、
fixed-leaf、共役、C4を全て通過した。held-out残差は次数`3 → 4`、100-step shadowingも全方向で改善したが、
amplitude `0.01`のcubic/quadratic残差比が32方向中9方向で登録上限`0.10`を超え、最大`0.228691`と
なった。このためQ007bは有効な性能棄却として固定し、quarticへ進まず、独立holdoutで有効半径を局在化する。
Q007b1では別seedの64方向で半径`0.004`の最大残差比`0.0780063`、失敗0を得て、別32方向の
100-step shadowingも全gateを通過した。chart Jacobianの正規化最小特異値は半径`0.01`まで`1.0`以上で、
fold signatureは見つからなかった。従って半径`0.004`の有限sampleだけを`accepted`とした。Q007cでは
全17,550 order-4 homological blockを列挙し、singular block 0、最大condition `34673.9`でoperator-only
prequalificationを通過した。これは四次forcingや係数の正しさをまだ示さないため、次はQ007c1で
解析的4階微分、forcing assembly、全係数、残差次数`4 → 5`、半径`0.01`の改善を独立に判定した。
全validityと1-step残差gateは通過したが、100-step shadowingの1方向でfinal absolute比`1.37153`、
maximum relative比`0.891419`が上限`0.8`を超えたため、Q007c1は有効な性能棄却として固定する。
Q007c2では係数を変えず、別seedの64方向で振幅・horizon依存を監査した。半径`0.01`・10 stepと
半径`0.004`・100 stepは全3 shadow比が`0.8`以下となり、有限sampleの有効shadow領域を局在化した。
一方、半径`0.01`・100 stepではfinal absolute比が`0.850582`となったため、Q007c1の長時間・大振幅
棄却は変更しない。Q008aでは固定した四次Fourier coefficientを自然なsparse-fiber baselineと
4つのflat／D1Q3 TT-SVDへ同じ格納・忠実度規則で比較した。全忠実度gateは通過したが、最良TTでも
格納実スカラー数は`11.2397`倍、serialized bytesは`10.8600`倍となったため、この4 tensorizationの
圧縮仮説を棄却した。Q008cではwave／branch factorizationと3-bit wave QTTの4候補も全忠実度gateを
通過したが、最良候補でも自然なsparse-fiberの`14.1366`倍の格納実スカラー、`13.6592`倍の
serialized bytesを要した。このため固定Q007c1係数に対するTT-SVD圧縮経路を閉じ、TT-crossへ進まない。
Q007dでは固定保存量葉上の解析的full-map Jacobian、quartic chart tangent、Euclidean projector、
matrix-free normal SVDを独立検証し、全7 validity gateを通過した。しかし平衡点でも
`gamma_10=2.59222`、半径`0.004 / 0.01`の全32方向でも`gamma_10>1`となったため、登録した
Euclidean projected normal-dominance仮説を有効に棄却した。Q007eでは平衡点Fourier blockだけから
Riesz／Stein metricを固定し、全8 validity gateを通過した。adapted `gamma_1 / gamma_10`は
`0.998806 / 0.979633`となったため、平衡点prequalificationを`accepted`とした。これはQ007dの棄却を
変更せず、Euclidean nonnormal amplificationを計量依存性として切り分けた結果である。Q007fでは同じ
metricを再調整せずQ007dの33 starting pointへ適用し、全7 validity gateを通過した。半径
`0.004 / 0.01`の最大adapted `gamma_10`は`0.980286 / 0.981561`、failure countはともに0だったため、
登録した10-step有限sample仮説を`accepted`とした。次は、これをball全体や存在定理へ読み替えず、
Q007gでは非共鳴不変多様体定理と定量的a posteriori proofのreadinessを監査し、全6 validity gateを
通過した。必要spectral quotientは\(L=89\)である一方、既存の次数2--4監査はFourier selection ruleに
沿うsector-aware float64条件であり、固定した定理のfull-spectrum条件を直接認証していない。さらに
Banach関数norm、rigorous inverse、defect／variation／tail／roundoff majorantも未構築なので、結果は
有効な`not_ready`とした。これはcandidate manifoldの不存在やQ007fの棄却ではない。Q007hでは
`Fraction`端点、Machin／Taylor区間、Neumann inverse bound、Bauer--Fike inclusionを全288非零blockへ
適用した。線形5仮説はすべて通り、selected radius upper、normal-gap lower、degree-90 tail upperは
`0.9920954673554354 / 0.00206112115963712 / 0.998942202264331`となった。しかし独立preconditionerが作る
C4-related modulus endpoint差`2.32993e-11`が登録validity閾値`1e-12`を超えたため、Q007hは規則どおり
`inconclusive`とした。次はQ007h1でC4 orbit代表のpreconditionerを厳密なpopulation permutationにより
輸送した。全289 C4 symbol edge、輸送した\(\epsilon\)／\(\beta\)／radius、conjugate／C4 modulus endpointは
有理数としてexact 0差となり、10 validity gateと5 hypothesis gateを全通過した。selected radius upper、
normal-gap lower、degree-90 tail upperは`0.9920954673554099 / 0.0020611211596580 / 0.9989422022620159`で、
`registered symmetry-equivariant linear spectral split and degree-90 tail certified`として`accepted`とした。
Q007iでは72代表のproof digestを全て再現し、selected 6 diskを4 modulus型へ、external spectrumを643
representative diskへ包含した。96項の有理log enclosureで次数2--89の全2,919,730 aggregate、展開時
869,107,778 productを検査し、overlap 0、最小log-gap lower `6.912230841407495e-10`を得た。従って
`registered direct external nonresonance through degree 89 certified`として`accepted`とした。
Q007gのmap structureとQ007h1の線形・tail認証を合わせ、Cabré--Fontich--de la Llave Theorem 1.2から、
固定17²・固定保存量葉上でselected 24実次元spectral subspaceへ接する局所解析的不変多様体の存在と、
同じ接空間を持つ\(C^{90}\) locally invariant manifoldとしての局所一意性を結論する。ただしこれは定性的な
局所定理で、explicit radius、登録した数値quartic chartとの厳密同定、finite-ball normal attraction、
grid-uniform性を与えない。従ってspectral manifoldの存在は認証済みだが、保存済みの数値chartは引き続き
**candidate numerical chart** と呼ぶ。Q007jではQ006iの係数hashを再現し、axis／diagonalの6 branchに対する
right／left 12個の正規化固有対を有理Krawczyk boxで認証した。maximum utilization／interval contractionは
`3.453560282251993e-5 / 7.431317256896775e-9`、Q007h1 selected discへの対応は`6 / 6`で衝突0だった。
C4／共役で全24 modeへ輸送したexact root enclosureと登録centerの最大component correction upperはright
`1.153401559605646e-15`、biorthogonal-left `2.9617269241843315e-15`である。従って
`registered selected eigencoordinates rigorously bridge to the theorem spectral subspace`として`accepted`とした。
Q007kではこの24 mode boxからexact quadratic forcingを作り、zero-wave 36、internal graph-gauge 108、external
156の全300 homological system（3,024 complex unknown）を140桁外向き有理区間で認証した。300/300でstrict
Krawczyk inclusionが通り、maximum utilization／interval contraction／registered-center correction upperは
`3.871467353051258e-6 / 2.262806292583543e-11 / 4.012059355448033e-12`だった。さらに \(ME=0\) と
\(MA(0)=M\)をentrywise exactに検証し、36 zero-wave productの1からのminimum separation lower
`0.015746583653469235`、108 graph-gauge inclusionを得た。従って
`registered Q006i quadratic coefficients identify the theorem-manifold graph-gauge quadratic jet`として
`accepted`とした。これでlinear coordinateとquadratic jetの同定は済んだが、cubic／quartic jetとexplicit
radiusはまだ認証していない。

- 奇数幅の有限周期 D2Q9 で物理的に \(|\lambda|=1\) となるのは、通常 \(k=0\) の
  質量と二成分運動量の3モードである。
- 偶数幅では \((\pi,0),(0,\pi)\) に \(\lambda=-1\) の Nyquist checkerboard mode が
  加わる。このため主構築は奇数格子に限定し、偶数格子は parity regression と障害解析に
  使う。
- 非零低波数の shear/acoustic modes は正粘性により \(|\lambda|<1\) である。
  Q004b は個別ラベルの全域一意性ではなく、\(k=0\) から連続化した3次元 invariant
  cluster が有効な最大低波数域 \(|k|\le k_c\) を求める。
- 非零波数 chart は最初に全質量・全運動量を固定した葉
  \(\delta M=\delta P_x=\delta P_y=0\) 上で構築する。\(k+(-k)=0\) が作る
  zero-wave-number 補正は、保存モーメントを持たない kinetic 成分だけを許す。
- strict-center の一様 equilibrium family は、保存量葉を横切る別の解析解付き
  オラクルである。homological equation、gauge、残差次数、TT 表現の検証に使う。

## 完了した数値ゲート

### Strict-center dense oracle

\(3^2\) 奇数周期格子の一様 equilibrium family では、線形チャートの不変性残差
\(O(\lVert a\rVert^2)\) が二次補正により \(O(\lVert a\rVert^3)\) へ改善した。
観測次数は `1.9969` と `2.9969` である。64方向、解析 Hessian、
finite-difference step sweep、homological residual を別々に検証している。

### Q004b branch/cluster tracking

\(\omega=1.0,1.2,1.5,1.8\) と path angle \(0,\pi/8,\pi/4\) の連続 \(k\)-path で、
simple eigenvalue 域は左右固有ベクトル、衝突・縮退域は ordered-Schur subspace を
追跡する。次表は事前登録した閾値を通る最後の sampled \(k\)、すなわち \(k_c\) の
経験的下限である。各 path では隣の最初の不合格点も transition bracket として保存する。

| \(\omega\) | validated \(k_c\) range |
|---:|---:|
| 1.0 | 0.763–0.988 |
| 1.2 | 0.925–1.188 |
| 1.5 | 1.163–1.388 |
| 1.8 | 1.375–1.450 |

path reversal と90度回転の最大 principal angle はともに `4.5e-8` 未満である。
\(\omega=1.2\) の \(17^2,33^2\) では strict unit mode が3個、診断用
\(16^2,32^2\) では5個であり、
直接評価した \(A(\pi,0),A(0,\pi)\) にも \(-1\) mode が各1個現れた。全波数域で
個別ラベルを一意にする旧仮説は棄却した。ここで得た \(k_c\) は閾値依存の経験的境界で、
多様体の存在定理ではない。

### Manufactured nonidentity oracle

安定な複素共役対、非零 \(R_2\)、mean-like/second-harmonic complement、可制御な
二次共鳴を持つ5状態写像を追加した。非直交 similarity transform により左右基底の
正規化と左右不変性も独立に検証する。一般 real-block homological solver は既知の
\(H\) と \(R_2\) を相対誤差 \(2\times10^{-15}\) 未満で回収し、共鳴へ近づくと
condition number が約 `5.10` から `1.74e4` へ増大し、厳密共鳴を
rank deficiency として拒否した。これは solver と LBM branch-classification error を
切り分ける algebraic oracle であり、D2Q9 candidate manifold の存在証拠ではない。

### Q005 sector-aware nonresonance

Q004b の方向別最小 cutoff、奇数格子 \(N=9,17,33,65\)、
\(\omega=1.0,1.2,1.5,1.8\) の16条件を監査した。最小非空 isotropic shell は全条件で、
直交 acoustic 対の積が対角 shear と数値 rank threshold 内で一致した。
二次 forcing の左 nullspace 射影は最大 \(9.97\times10^{-16}\) なので方程式は
compatible だが、係数は非一意で strict nonresonance は失敗する。

登録 radial band の境界でも14条件に external resonance witness があり、14条件で
near-Nyquist excluded mode が finite-grid normal-attraction 必要条件を破った。
一方、spectral split 自体は最小 Schur separation 0.4846、最大 projector norm 1.8387、
最大 residual \(3.09\times10^{-14}\) で解像されている。従ってこの失敗を
branch-classification error とは扱わない。

修正案のうち cutoff 縮小は、最小 shell 自体が共鳴するため棄却した。mode追加は
resonant/near-resonant closure の再監査待ちである。\(y\)-independent stripe は
有限格子 solver oracle として全16条件で nonsingular だった。代表
\(N=17,\omega=1.2\) の
second-harmonic block は \(\sigma_{\min}=1.9335\times10^{-2}\)、
condition number 96.02 である。ただし conditioning は概ね \(N^2\) で悪化するため、
grid-uniform な manifold claim は置かない。

### Q006s fixed-leaf stripe quadratic oracle

\(N_x=17,\omega=1.2\) の \(1\times17\) stripe で、正波数側の shear と2本の
acoustic mode を共役制約付き実6座標へ変換した。全質量・全運動量を固定し、
二次出力を \(k=0,\pm2k\) に制限する sector-aware Sylvester solve を実装した。
Fourier selection rule の予測どおり \(R_2=0\) で、非零の zero-wave kinetic 補正
\(\lVert\widehat H_0\rVert_F=0.6630\) と second harmonics
\(\lVert\widehat H_{\pm2}\rVert_F=2.0938\) を得た。

- 36列の solver assembly:
  \(\sigma_{\min}=1.9335\times10^{-2}\)、\(\kappa_2=96.0205\)
- homological relative residual: \(4.57\times10^{-15}\)
- graph gauge / fixed-leaf Hessian residual:
  \(1.47\times10^{-16}\) / \(9.03\times10^{-16}\)
- Richardson finite-difference Hessian discrepancy: \(4.29\times10^{-11}\)
- 未使用 seed の64方向での residual order:
  linear `2.000000–2.000020`、quadratic `3.000000–3.000219`
- \(\lVert a\rVert=0.01\) での最大方向別 quadratic/linear residual ratio: `0.05672`
- 32方向・100 step の quadratic 最大 absolute / perturbation-relative error:
  `1.873e-6` / `3.927e-4`
- quadratic/linear の最大 shadow error 比: `0.01691`
- \(1\times17\) と \(y\) 方向へ複製した \(17^2\) の1 step 差: `0.0`

最大振幅0.01までの登録サンプル campaign は全 gate を通過し、最小 population も
`0.02706` だった。一方、非ゲート stress の \(\lVert a\rVert=0.1\) では最大方向別
残差比が `0.6009` まで悪化した。また projected-coordinate drift は quadratic
`1.283e-6`、linear `5.006e-7` で改善していない。これは登録判定を変えないが、
支持された局所スケールと座標力学には追加検証・改善が必要である。半径0.01の
Euclidean ball 全体に対する一様保証ではない。

厳密に不変なのは ambient な \(y\)-independent stripe 部分空間であり、受理した
quadratic chart はその中の局所的な有限次近似である。full 2D、grid-uniform、
存在・一意性、normal attraction の主張には拡張しない。

### Q006r mode-added closure audit

\(N=17,\omega=1.2\) の固定保存量葉で、axial first-shell hydrodynamic modes に
diagonal shear の C4・複素共役 orbit を加えた16実座標候補を監査した。全136個の
unordered input Schur-block pair について、斜交 Riesz projector で external forcing を
抽出し、正規化済み Kronecker／symmetric-product homological operator を SVD した。

- 元の diagonal resonance:
  `compatible_nonunique`、\(\sigma_{\min}=5.10\times10^{-16}\)
- diagonal shear を internalize した external block:
  \(\sigma_{\min}=0.130569\)、condition number `13.8414`
- terminal numerical singular / near-singular block: `0 / 0`
- terminal maximum condition number: `1894.292`
- maximum Schur/projector/C4/conjugacy/fixed-leaf residual:
  \(4.07\times10^{-15}\)
- mode addition: `0`、terminal real dimension: `16`

従って coefficient-solvability gate は通過した。一方、selected の最小 modulus
`0.9699501` に対して、\((0,-8)\) の near-Nyquist excluded mode は `0.9830465` で、
normal-dominance gap は `-0.0130964` だった。local Sylvester separation `0.130569` と
selected Riesz projector norm `1.52896` は通過しており、棄却理由は normal gap に
局在する。この結果は **coefficient-solvable finite-grid candidate** の受理に留め、
full 2D Q006 には進めない。

### Q006n near-Nyquist refinement audit

同じ16実座標 family を odd grid \(N=9,17,33,65,129\) と
\(\omega=1.0,1.2,1.5,1.8\) の全20条件で再監査した。各条件で136個の unordered
input block pair を固定し、mode addition は行っていない。study validity、全 pair
列挙、構造残差、solve residual、direct Nyquist anchor は通過した。

- \(N\ge17\) の normal gap が負: `16 / 16`
- 同条件の最悪 excluded mode が axial near-Nyquist: `16 / 16`
- coefficient + blockwise projector gate 通過: `13 / 16`
- viable \(\omega\): `0`
- maximum structural / solve residual:
  \(2.65\times10^{-14}\) / \(1.14\times10^{-13}\)
- maximum external condition number: \(2.42\times10^7\)（登録上限 \(10^8\) 未満）

全 \(\omega\) で \(N^2g_N\) は負の有限値へ近づき、例えば \(N=129\) では
\(-5.7548,-3.8373,-1.9190,-0.63975\) だった。これは登録した有限 ladder 上での
near-Nyquist scaling evidence であり、全 odd grid に対する定理ではない。

clean obstruction 判定を止めたのは \((65,1.8),(129,1.5),(129,1.8)\) の3条件である。
numerically singular block はなく、materially forced near condition が \(10^4\) を
超えた。代表 witness は axial acoustic self-product から \((\pm2,0),(0,\pm2)\) を作る
second harmonic と、axial shear × diagonal shear から \((\pm2,\pm1)\) 型を作る block
である。従って Q006n を事後的に成功へ変更せず、**normal gap と coefficient scaling の
混合障害**として記録する。

### Q006c small-wave coefficient-scaling audit

odd grid \(N=17,33,65,129,257\)、全4 \(\omega\)、全136 pairのcompleteness screenを
維持し、acoustic self second-harmonic 8 pairと axial-shear × diagonal-shear 8 pairを
詳細監査した。固定fit window \(N=33,65,129,257\) に対する8本の
（2 orbit × 4 \(\omega\)）fitは、全て登録窓を通過した。

| metric | observed slope range |
|---|---:|
| \(\sigma_{\min}\) | `-2.04791 … -1.98123` |
| eigenvalue detuning | `-2.04823 … -1.99309` |
| condition number | `1.97607 … 2.04818` |
| forcing norm | `0.00257 … 0.00833` |
| weakest-direction forcing \(\beta\) | `-0.99574 … -0.98548` |
| local-amplitude response | `0.95557 … 1.05216` |
| global-\(\ell_2\) response | `-0.04443 … 0.05216` |

study validityと全scaling gateは通過し、判定は
`genuine weakly-forced small-k resonance supported` である。\(N=257\) で
materially forced near witnessは56件に増えたが、全て登録2 orbit内で、新規classは0だった。
最大target conditionは `1.826e5`、全pair最大は `3.807e8` である。後者は旧 \(10^8\)
ceilingを超えるため、Q006cの受理はQ006nのcoefficient gateを遡及的に通すものではない。

global-\(\ell_2\) coefficient \(\lVert x\rVert/N\) が有限ladder上boundedでも、固定した
local Fourier amplitudeに対する \(\lVert x\rVert\) は \(O(N)\) に増える。従って
near resonanceを座標artifactとして消去せず、normal-gap障害とともに変更モデルの
baselineへ残す。これは有限4点fitであり、漸近定理ではない。

### Q006f conservative checkerboard-filter audit

BGK step後に5点convex filterを加える変更モデルを、\(5\)個の\(\eta\)、全4 \(\omega\)、
odd grid \(N=17,33,65,129,257\) の100条件で封印監査した。filter algebra、全136 pair、
16 target、残差、condition、Q006c scaling、low-wave distortionの各gateは有効に評価できた。

- study validity: `passed`
- scientific outcome: `rejected`
- viable family: `0 / 20`
- coefficient gate通過: `20 / 20`
- 正のraw normal gapを持つfamily: `11 / 20`
- 最大の5-grid minimum normal gap: `9.5571e-9`（閾値 `1e-6`）
- maximum all-pair condition: `7.4421e8`（閾値 `1e9`）
- maximum structural / solve residual: `6.6025e-14 / 1.7609e-13`

filterはNyquist checkerboard anchorを厳密に \(-(1-\eta)\) へ移し、Q006cのresponseを
悪化させなかった。しかしNyquistを十分に減衰したfamilyでは、global bottleneckが同じ
\((\pm1,\pm1)\) sectorのselected shearとexcluded acousticへ移った。正の11 familyで
観測した5-grid gap slopeは `-4.0284 … -4.0052` であり、絶対gapは\(N^{-4}\)程度に
閉じる。これはQ006fの事前登録判定を変更する根拠ではなく、Q006gで独立に検証する
post-hoc診断である。Q006fは標準BGKのQ006nを変更せず、filtered full Q006も開始しない。

### Q006g diagonal low-wave tangency audit

対角C4 orbit、7 odd grids \(N=33,\ldots,2049\)、全5 \(\eta\)、全4 \(\omega\) の
140条件・560 waveをsymbol levelで独立監査した。direct eigensystemと
\(\lambda_{\eta,j}=\chi_\eta\lambda_{0,j}\) の二経路が一致し、全20 familyが固定した
符号、2種の4次slope、\(N^4|g|\) plateau gateを通過した。

- outcome: `same-sector hydrodynamic fourth-order tangency confirmed`
- family fit: `20 / 20`
- absolute-gap slope: `-4.00088 … -3.99980`
- relative-gap slope: `-4.00092 … -4.00007`
- maximum \(N^4|g|\) relative spread: `0.001804`
- maximum eigensystem / matching residual: `1.3344e-15 / 4.3673e-15`
- maximum scalar-gap identity error: `5.0034e-15`

符号は全fit gridと全\(\eta\)で、\(\omega=1.0\) が負、\(1.2,1.5,1.8\) が正だった。
代表 \((\eta,\omega)=(0.02,1.2)\) では \(N=2049\) で
\(g=2.3658\times10^{-12}\)、\(N^4g=41.7005\) である。従ってQ006fの唯一の失敗を
数値誤分類やNyquist残留へ転嫁できない。ただしこれは対角sectorの有限ladder診断であり、
Q006fの棄却、\(10^{-6}\) threshold、full-chart保留を変更しない。

### Q006h first-shell cluster-complete filtered-family audit

第一Chebyshev shellの8 waveそれぞれでshearと2 acoustic modeを全て選んだ24実座標familyを、
5 \(\eta\)・4 \(\omega\)・5 odd gridの100条件、各300 unordered pairで監査した。全validity
gateが通り、20 family中6 familyが全spectral/coefficient/scaling gateを通過した。
事前登録したlexicographic ruleにより \((\eta,\omega)=(0.01,1.5)\) を選択した。

- study outcome: `accepted`
- classification: `cluster-complete filtered finite-ladder prequalification passed`
- selected five-grid minimum normal gap: `6.93869e-5`（閾値 `1e-6`）
- selected maximum external condition: `5.95817e8`（上限 `1e9`）
- selected maximum target response ratio: `0.964773`（上限 `1.10`）
- selected maximum structural/fixed-leaf/solve residual: `8.3841e-14`
- selected material witness: `40`（旧2 class各16、diagonal acoustic self 8）

新しい8 witnessは \(N=257\) で対角acousticの自己相互作用から
\((\pm2,\pm2)\) second harmonicを作るnear-singular blockであり、全件を独立classとして
保存した。登録外class自体を失敗にしない事前規則に従い、condition ceilingと残差で判定した。
一方、選択familyのnormal gapは \(N=257\) で最小となり、最大conditionも解像度とともに
増大している。従ってこれは変更写像・有限5-gridのprequalificationであり、all-grid theorem、
grid-uniform chart、非線形normal attraction、存在・一意性の証明ではない。

### Q006i filtered full-2D dense quadratic chart

Q006hが選んだ \((N,\eta,\omega)=(17,0.01,1.5)\) を固定し、第一Chebyshev shellの
24実座標、300 unordered pairについて、selected-output graph gaugeと非自明な \(R_2\) を
含むdense quadratic chartを構築した。全validity gateは通過したが、登録した仮説gateのうち
global conservationだけが失敗したため、結果は`rejected`である。

- classification: `Q006i local chart hypothesis rejected`
- sector count: zero/internal/external = `36 / 108 / 156`
- numerical singular block: `0`
- maximum operator condition: `1.45139e4`
- maximum solve residual: `1.08638e-14`
- homological relative residual: `2.35301e-15`
- independent Hessian maximum relative discrepancy: `9.06933e-10`
- linear residual slope range: `1.99982 ... 2.00026`
- quadratic residual slope range: `2.99973 ... 3.00028`
- maximum quadratic/linear residual ratio: `0.00658935`
- quadratic 100-step maximum state error: `1.51151e-7`
- quadratic/linear shadow-error ratio: `0.00512138`
- maximum global conservation drift: `2.72850e-12`（上限 `1e-12`）

二次補正は登録方向で残差を2次から3次へ改善し、shadowingも大幅に改善した。一方、失敗した
保存gateを結果後に緩めてacceptedへ変更しない。linear／quadraticの保存driftがほぼ同じため、
Q006jではchart係数ではなく、通常和による測定、collision、streaming、filterのfloat64演算を
分離して監査する。Q006iは固定変更写像・単一grid・有限方向の数値結果であり、真の不変多様体の
存在・一意性やall-grid主張ではない。

### Q006j float64 global-conservation drift source audit

Q006iと同じlinear／quadratic各32、合計64 trajectoryを100 step追跡し、NumPy通常和、
`math.fsum`、Neumaier補償和を比較した。全validity gateは通り、Q006iの最大driftを厳密に
再現したが、登録した一様fixed-leaf projection controlが保存上限を落とした。

- classification: `structural or unresolved conservation defect`
- NumPy maximum drift: `2.7284963e-12`
- `math.fsum` / Neumaier maximum drift: `2.7285042e-12 / 2.7285042e-12`
- maximum `math.fsum`–Neumaier component difference: `0`
- maximum NumPy–`math.fsum` measurement difference: `1.13687e-13`
- streaming drift / stage reconstruction error: `0 / 0`
- collision maximum one-step / cumulative norm: `5.68691e-14 / 2.67164e-12`
- filter maximum one-step / cumulative norm: `5.68451e-14 / 5.11595e-13`
- projected-control maximum drift: `2.16005e-12`（上限 `1e-12`）
- maximum single projection norm: `1.67297e-15`

従ってQ006iの超過は通常和だけの測定artifactではなく、float64 stateへ蓄積したmass-dominated
driftである。streamingは原因から除外でき、collisionが主寄与、filterが副寄与である。ただし、
一様投影が失敗したため、登録範囲ではbounded roundoffとして制御できたとは判定しない。
分散した補正が各populationのULPに対して小さすぎた可能性はQ006jだけでは未証明であり、Q006kで
実現補正量と診断用localized correctionを比較する。Q006iの棄却と \(10^{-12}\) 上限は維持する。

### Q006k fixed-leaf projection representability audit

Q006jと同じ64 trajectoryを100 step追跡し、standard、一様分散、固定site \((0,0)\) の
\((q_0,q_1,q_2)\) localized controlを比較した。Q006jのstandard／uniform driftを誤差0で再現し、
全validity・hypothesis gateを通過した。

- classification: `uniform projection representability failure localized`
- standard / uniform maximum drift: `2.7285042e-12 / 2.1600519e-12`
- nonzero uniform realization-error step: `6400 / 6400`
- maximum uniform global correction error: `5.71253e-14`
- changed population count: `0 ... 2601`、mean `1563.04 / 2601`
- ULP ratio: minimum `4.80200e-20`、median-of-medians `1.57478`、maximum `1.81584`
- localized maximum drift: `1.51150e-16`
- localized maximum correction norm: `5.92925e-14`
- localized / standard maximum state difference: `1.03852e-13`
- 3-population moment matrix condition / solve residual: `3.73205 / 0`

一様補正はstepによって全entryが丸め落ちする一方、平均では約60%のentryが変化し、ULP比の中央値は
1を超えた。従って「全補正がsub-ULP」とは結論せず、**分散したfloat64加算がintended global
moment correctionを正確に実現しない**と限定する。同じmoment correctionを3 populationへ
局在化すると登録保存上限を大幅に通過したが、固定siteと固定populationはtranslation／C4 symmetryを
壊す。このcontrolは原因診断だけに使い、Q006i／Q006jの判定、本番写像、chartへ採用しない。

### Q006l stagewise state-covariant conservative arithmetic

collision後とfilter後のraw stateごとに \(q_0\) 最大siteを選び、minimum-norm conserved-moment
right inverseでglobal residualを一回補正した。standard／Q006k fixed controlを誤差0で再現し、
64 trajectory × 100 step × 2 stageの全anchorとtranslation／C4 generatorを監査した。

- classification: `covariant anchor correction controls registered drift`
- covariant maximum drift: `1.1368684e-13`（上限 `1e-12`）
- minimum anchor gap: collision `1.63489e-9`、filter `1.24669e-9`
- anchor covariance failure: `0`
- translation / C4 equivariance error: `0 / 0`
- right-inverse condition / residual: `1.2247449 / 2.22045e-16`
- maximum single-stage correction norm: `1.89632e-14`
- covariant / standard maximum state difference: `1.15577e-13`
- minimum population: `0.0275271`

これは登録軌道が全stepでunique-anchor gapを持つ範囲の算術結果である。補正はglobal residualと
`argmax`に依存し、anchor switchで非滑らかになる。特に基準一様平衡では全siteがtieとなるため、
このままparameterization mapの近傍写像として採用したり、Q006iを再判定したりしない。Q006mで
translation-equivariant unique-site selectorが一様平衡へ連続・微分可能に延長できるかを判定した。

### Q006m equivariant unique-anchor obstruction

\(17^2\) のuniform equilibriumと周期translation群を直接列挙し、Q006lのunique-site selectorが
平衡へequivariantに延長できるかを監査した。固定点矛盾は有限群作用だけから得られ、振幅縮小は
その近傍で \(q_0\) top-two gapがtieへ向かうことを確認する補助診断である。

- classification: `equivariant unique-anchor obstruction confirmed`
- uniform \(q_0\) maximum multiplicity / gap: `289 / 0`
- translation generator fixed-site count: `0 / 0`
- uniform translation invariance error: `0`
- row-major anchor covariance failure: `2 / 2`
- registered records: `384` direction-amplitude、`768` signed state、`1536` stage observation
- failed gap ladder: `0 / 8`
- maximum smallest/largest-amplitude gap ratio: `1.0052062e-5`（上限 `1e-4`）
- minimum population: `0.0275189`

一様状態 \(f_*\) は全translation \(T_g\) で固定される。一方、非自明なgenerator \(g\) が固定する
siteはないので、unique-site selector \(s\) のequivarianceは
\(s(f_*)=s(T_gf_*)=g\cdot s(f_*)\) という不可能な条件を要求する。これはunique-site selector classを
排除するが、anchor-freeなequivariant arithmetic全体を排除しない。Q006lの有限軌道acceptedと
Q006i／Q006jのrejected判定も変更しない。

### Q006o anchor-free arithmetic policy

Q006jのunmodified standard mapとuniform minimum-norm projectionを同じ64 trajectory × 100 stepで
再実行した。初期stateのcomponent scale \(S_c=\sum_{x,q}|C_{cq}f_{0,x,q}|\) から、観測driftへfitせず
\(B_c(t)=2t\,\operatorname{spacing}(S_c)\) を登録した。係数2はcollisionとfilterの2 conservation-sensitive
stageに対応する。

- classification: `unmodified equivariant map with registered forward-error budget preferred`
- component-budget check / violation: `19200 / 0`
- maximum utilization: `0.5`
- maximum final component budget: `1.1368684e-11`（上限 `1.2e-11`）
- streaming / independent-sum error: `0 / 0`
- standard / uniform maximum drift: `2.7285042e-12 / 2.1600519e-12`
- uniform improvement factor: `1.2631660`（選択下限 `2`）
- uniform exact remaining-drift step: `0 / 6400`
- maximum uniform remaining local drift: `5.7125343e-14`
- minimum population: `0.0275271`

従ってuniform projectionは採用せず、smooth・translation／C4-equivariantな標準写像を変更しない。
ただしこのbudgetは登録有限trajectoryのoperational policyであり、任意state・任意horizonのroundoff
定理ではない。Q006i／Q006jの旧 \(10^{-12}\) gateとrejected判定は変更せず、Q006pでは旧判定と新policyを
並記してchart continuationの可否を判定した。

### Q006p dual-reporting integration

Q006iとQ006oをsealed runnerから再実行し、grid、model、seed、amplitude、horizonと64方向を照合した。
Q006iの既存8 gateをoriginal columnとして変更せず保存し、別のpolicy columnではglobal conservationだけを
Q006oのcomponentwise ULP budgetへ置き換えた。

- classification: `dual reporting supports unmodified-map chart continuation`
- direction alignment record / maximum error: `64 / 0`
- Q006i original / Q006o `math.fsum` drift:
  `2.7284963e-12 / 2.7285042e-12`
- cross-measurement drift difference: `7.8275683e-18`
- original failed gate: `1`（`global_conservation`）
- policy failed gate: `0`
- Q006o budget violation / maximum utilization: `0 / 0.5`
- maximum final component budget: `1.1368684e-11`

original columnのQ006i `rejected`は変更していない。policy columnだけが、同じ64 trajectoryについて
unmodified mapを使う次段階を支持する。独立性のないintegration結果なので、Q006qではseed `20260811`・
amplitude `0.005`・200 stepと、seed `20260812`・amplitude `0.02`・50 stepをholdoutとして使い、
予算式を変更せずに再判定する。

### Q006q independent forward-error holdout

Q006oの係数2、component scale、`numpy.spacing`、`math.fsum`／Neumaier測定を変更せず、Q006pまでに
使っていない2 scenarioを全列挙した。

- classification: `independent holdout supports registered forward-error policy`
- trajectory / step / component check: `128 / 16000 / 48000`
- budget violation: `0`
- aggregate maximum utilization: `0.5`
- maximum final component budget: `2.2737368e-11`（上限 `2.4e-11`）
- long-horizon maximum drift / minimum population:
  `5.4569682e-12 / 0.0276566`
- large-amplitude maximum drift / minimum population:
  `1.3642421e-12 / 0.0273224`
- stage-map / streaming / independent-sum error: `0 / 0 / 0`

この結果で、登録した有限軌道についてQ006oの算術policyを独立に支持した。ただし任意state・任意horizonの
roundoff定理ではなく、amplitude `0.02`でのchart invarianceも主張しない。次数継続はまずQ007aで3次の
全homological blockが一意に解ける条件を満たすか調べ、通過した場合だけcubic coefficientを構築する。

### Q007a cubic homological-family prequalification

Q006iと同じ24 complex modeについて、order-2 control 300 pairとorder-3全2,600 unordered tripleを
artifact入力なしで組み立てた。zero-wave kinetic、internal selected、external blockを同一SVD規則で
判定した。

- classification: `order-three homological family prequalified on registered grid`
- order-2 sector count: `36 / 108 / 156`
- order-2 minimum singular / maximum condition:
  `1.5502436e-4 / 14513.9305`（Q006iを誤差0で再現）
- order-3 sector count: `108 / 1044 / 1448`
- order-3 singular / near-resonant block: `0 / 24`
- order-3 minimum singular / maximum condition:
  `2.0787973e-4 / 10821.8148`（ceiling `1e9`）
- conjugate multiplier / singular-value relative error:
  `2.91520e-16 / 2.84703e-15`
- output wave count / C4・conjugacy count failure: `49 / 0 / 0`

これは登録有限grid上のoperator-only判定であり、cubic forcingや係数をまだ計算していない。Q007bでは
解析的3次微分を独立有限差分で照合し、全係数solve、fixed-leaf／共役／C4、held-out残差次数`3 → 4`、
100-step shadowing改善を別gateとして判定する。

### Q007b cubic coefficient and residual continuation

Q006iのquadratic chartから全2,600 cubic forcingを解析的に構成し、symmetric complex Fourier-fiberで
\(T\) と \(K\) を保存した。物理空間の \(2601\times24^3\) dense tensorはmaterializeしていない。

- classification: `cubic continuation does not improve the registered chart`
- validity gates: `7 / 7` passed
- independent third-derivative maximum best relative error: `3.36571e-6`
- maximum solve / homological residual: `7.50719e-13 / 7.50742e-13`
- coefficient conjugacy / C4 chart / C4 reduced error:
  `1.94246e-13 / 2.03769e-14 / 1.19346e-15`
- quadratic residual slope range: `2.9994581 – 3.0005016`
- cubic residual slope range: `3.9993071 – 4.0003672`
- amplitude `0.01` residual-ratio maximum / failed directions: `0.2286914 / 9 of 32`
- 100-step maximum-absolute / final-absolute / relative shadow-ratio maximum:
  `0.1509163 / 0.1097002 / 0.1310869`
- cubic forward-error component checks / violations / maximum utilization:
  `9,600 / 0 / 0.5`

従って3次係数や次数改善は検証されたが、登録振幅`0.01`で要求した全方向10倍改善は支持されない。
同じ32方向では残差比の最大値がamplitude `0.00125 / 0.0025 / 0.005 / 0.0075 / 0.01`に対して
`0.02859 / 0.05717 / 0.11435 / 0.17152 / 0.22869`とほぼ線形に増えた。次はこの観測をcalibrationに
限定し、新seedで半径`0.004`を検証する。Q006iの旧rejectionは変更せず、quartic continuationも保留する。

### Q007b1 independent cubic-radius and immersion audit

Q007bの方向をcalibrationに限定し、seed `20260818 / 20260819 / 20260820`でradius、shadowing、解析
chart Jacobianを独立に検証した。

- classification: `registered cubic improvement radius localized without fold signature`
- validity / hypothesis gates: `5 / 5`, `6 / 6` passed
- quadratic / cubic / residual-ratio slope range:
  `2.999754–3.000373 / 3.999374–4.000278 / 0.999438–1.000311`
- radius `0.004` maximum residual ratio / failed directions: `0.0780063 / 0 of 64`
- radius `0.01` maximum residual ratio / failed directions: `0.1950024 / 16 of 64`
- analytic Jacobian maximum best relative error: `1.46388e-10`
- radial minimum normalized singular value / maximum condition: `1.0 / 1.76763`
- shadow maximum-absolute / final-absolute / maximum-relative ratio:
  `0.0440221 / 0.0300889 / 0.0362175`
- cubic budget component checks / violations / maximum utilization:
  `9,600 / 0 / 0.5`

near-resonant 24 tripleのchart寄与率は残差比と負相関`-0.57894`で、上位残差quartileへのenrichmentも
`0.47235`だった。これに対し全cubic／quadratic chart補正比は残差比と`0.96076`のSpearman相関を示した。
従って登録sampleではnear-resonant subsetやfoldより有限次数の全体的な曲率が主要indicatorである。これは
半径`0.004`のball全体やinjectivityを保証せず、Q007bの半径`0.01`棄却も変更しない。

### Q007c quartic homological-family prequalification

Q006iと同じ24 complex modeについて、order-2／order-3 controlをartifact入力なしで再現した上で、
全17,550 unordered order-4 tupleを同じsector SVD規則で監査した。

- classification: `order-four homological family prequalified on registered grid`
- validity / hypothesis gates: `6 / 6`, `2 / 2` passed
- order-2 control sector / singular: `36 / 108 / 156`, `0`
- order-3 control sector / singular / near-resonant: `108 / 1044 / 1448`, `0 / 24`
- order-4 sector count: `846 / 4536 / 12168`
- order-4 singular / near-resonant block: `0 / 8`
- order-4 minimum singular / maximum condition:
  `6.4857065e-5 / 34673.9156`（ceiling `1e9`）
- minimum rank margin: `1.4431597e8`
- permutation multiplicity sum / values: `331776 / 1, 4, 6, 12, 24`
- conjugate multiplier / singular-value relative error:
  `3.57125e-16 / 3.01907e-15`
- fixed-leaf invariance maximum / C4・conjugacy count failure:
  `1.22778e-16 / 0 / 0`

従って登録有限gridでは四次homological familyに代数的障害は見つからなかった。ただしこれはoperator-only
判定であり、四次forcing／coefficient、5次残差、半径延長、shadowing、grid-uniformな存在・一意性を
主張しない。Q007c1では解析的な四次Faà di Bruno forcingを独立有限差分と照合してから全係数を解く。

### Q007c1 quartic coefficient and sampled-radius continuation

全17,550 quartic forcing／coefficientをsymmetric complex Fourier-fiberで構築し、写像の4階微分と
cubic defectの4階差分を独立に照合した。物理空間のfull dense quartic tensorはmaterializeしていない。

- classification: `quartic continuation does not restore registered radius`
- validity / hypothesis gates: `8 / 8`, `3 / 4` passed
- map fourth-derivative maximum best relative error: `3.09632e-5`
- assembled-forcing maximum best relative error: `3.95799e-4`
- maximum solve / homological residual: `1.00060e-12 / 9.53058e-13`
- maximum coefficient conjugacy / C4 error:
  `1.67664e-13 / 4.65140e-12`
- cubic / quartic residual slope range:
  `3.999714–4.000289 / 4.999739–5.000472`
- amplitude `0.01` maximum quartic/cubic residual ratio: `0.439147`
- amplitude `0.01` maximum quartic/quadratic residual ratio: `0.0927052`
- 100-step maximum-absolute / final-absolute / maximum-relative shadow ratio:
  `0.746449 / 1.371531 / 0.891419`
- shadow ratio failure counts: `0 / 1 / 1` of 32
- quartic budget component checks / violations / maximum utilization:
  `9,600 / 0 / 0.5`

従って四次係数と残差次数`4 → 5`は検証され、半径`0.01`の1-step残差も全32方向で登録上限を通った。
一方、shadow方向14ではmaximum absolute error自体は改善したが、step 15以降にinstantaneous error比が
`0.8`を超え、step 100の絶対誤差が`5.21953e-9 → 7.15874e-9`となった。このためQ007c1の100-step
性能仮説は棄却する。次はこの方向をcalibrationだけに使い、別seedで短時間・小振幅の有効領域を検証する。

### Q007c2 quartic shadow amplitude-horizon localization

Q007c1の全5係数hashを固定したまま、別seed `20260826`の64方向、amplitude
`0.004 / 0.007 / 0.01`、100 stepを一度ずつ実行し、horizon `10 / 25 / 50 / 100`のprefixを比較した。

- classification: `quartic shadowing domain localized on independent directions`
- validity / hypothesis gates: `4 / 4`, `3 / 3` passed
- Q007c1方向14 control maximum relative error: `0`
- direction norm error / prior exact duplicate count: `2.22045e-16 / 0`
- trajectory / chart-step / quartic budget-component count: `384 / 38,400 / 57,600`
- budget violations / maximum utilization / maximum final budget:
  `0 / 0.5 / 1.13687e-11`

| amplitude | horizon | max-absolute比 | final-absolute比 | max-relative比 | failure count |
|---:|---:|---:|---:|---:|---:|
| 0.004 | 100 | 0.220812 | 0.339679 | 0.270315 | 0 / 0 / 0 |
| 0.007 | 100 | 0.386433 | 0.594921 | 0.473050 | 0 / 0 / 0 |
| 0.010 | 10 | 0.466920 | 0.483935 | 0.461063 | 0 / 0 / 0 |
| 0.010 | 100 | 0.552063 | 0.850582 | 0.675784 | 0 / 2 / 0 |

従って、事前登録した短時間・大振幅と長時間・小振幅の2 operating pointは独立方向で通過した。
ただしこれは64方向上の有限sample claimであり、ball全体、他horizon、grid-uniform family、存在・一意性、
TT優位性を示さない。半径`0.01`・100 stepの境界失敗もそのまま保存する。

## TT 格納量の解釈

Phase 0 の \(81\times3\times3\times3\) 二次 coefficient tensor の比較は次の通りである。

| 表現 | stored scalar/value count |
|---|---:|
| box-dense | 2187 |
| full Hessian | 1053 |
| symmetric quadratic | 810 |
| natural fiber-sparse | 567 + 7 multi-indices |
| scalar-sparse | 468 + 468 multi-indices |
| TT cores | 657 + ranks/shapes |

657 は **TT core stored scalars** であり、TT gauge 自由度を除いた独立自由度数ではない。
TT の相対再構成誤差は `3.01e-15` だが、自然な fiber-sparse 表現より大きいため、
現段階で TT の圧縮優位性はない。今後も Fourier selection rule に基づく sparse
表現を必須 baseline とし、値数、index metadata、serialized bytes、評価時間、
rounding時間、不変性残差を分けて比較する。TT がこの baseline に勝たない場合は、
その tensorization を不適切と判定する。

### Q008a local Fourier coefficient TT storage prequalification

Q007c1のdegree `2 / 3 / 4` local complex Fourier chart係数をordered dense oracleへ展開し、
`flat-q-first / flat-q-last / d1q3-q-first / d1q3-q-last`をrelative discarded-Frobenius budget
`1e-13`で比較した。物理空間の \(2601\times24^d\) tensorはmaterializeしていない。

- classification: `registered TT tensorizations do not beat natural quartic sparse-fiber storage`
- validity / hypothesis gates: `4 / 4`, `0 / 1` passed
- maximum dense-vs-sparse action error: `2.44532e-14`
- maximum TT reconstruction / action error: `1.06011e-13 / 2.07996e-13`
- degree-4 natural sparse-fiber: `315,900` stored real scalars / `2,615,734` NPZ bytes
- degree-4 best TT: `3,550,626` stored real scalars / `28,406,852` NPZ bytes
- TT/sparse scalar / byte ratio: `11.2397 / 10.8600`
- degree-4 flat-q-last ranks: `[1, 24, 300, 216, 9, 1]`
- diagnostic median action time sparse / fastest TT: `0.603 / 2.783` ms per sample

従って4候補は係数を高精度に再現するが、自然なFourier sparse-fiberより格納量が約1桁大きく、
評価もこの環境では約4.6倍遅かった。timingはacceptanceに使っていない。Q008bのfull-chart／rolloutと
Q009 TT-crossはこの4候補について開始しない。Q008cでは、Q008aで未計算の`24=8 wave×3 branch`分解と
wave indexの3-bit QTTだけを新しい事前登録候補として試す。

### Q008c wave-branch / wave-QTT storage prequalification

Q008aのflat-q-lastを完全一致controlとして再構築した上で、入力modeを`24=8 wave×3 branch`へ分ける
tuple-major／factor-majorと、waveを3 bitへ分けるtuple-major／scale-interleaved QTTをdegree `2 / 3 / 4`
で比較した。任意の24次元方向は分割軸上のrank-one vectorとは限らないため、各元座標に属する小軸を
同じfeature tensorで結ぶ一般tensor-network contractionでTT作用を評価した。

- classification: `registered wave-factorized TTs do not beat natural quartic sparse-fiber storage`
- validity / hypothesis gates: `5 / 5`, `0 / 1` passed
- maximum candidate mapping action error: `1.34278e-15`
- maximum TT reconstruction / action error: `1.49155e-13 / 6.62433e-13`
- degree-4 natural sparse-fiber: `315,900` stored real scalars / `2,615,734` NPZ bytes
- degree-4 best wave-branch TT: `4,465,748` stored real scalars / `35,728,884` NPZ bytes
- best TT/sparse scalar / byte ratio: `14.1366 / 13.6592`
- degree-4 best wave-QTT: `8,121,540` stored real scalars / `64,977,332` NPZ bytes
- diagnostic median action time sparse / best registered candidate: `0.573 / 22.349` ms per sample

全12候補は再構成・作用・serializationを通過しているため、これは忠実度不良ではなく有効なstorage棄却で
ある。明示的なwave構造もflat-q-lastより改善せず、QTTはさらに大きかった。この結論は登録した有限degree・
grid・係数・4配置に限り、TT一般の不可能性は主張しない。次は圧縮候補を追加せず、未検証だった有限半径の
normal-attraction診断へ戻る。

## 再現

Python 3.11 以上を使う。`q004b`、`q005`、`q006s`、`q006r`、`q006n`、`q006c`、`q006f`、
`q006g`、`q006h`、`q006i`、`q006j`、`q006k`、`q006l`、`q006m`、`q006o`、`q006p`、
`q006q`、`q007a`、`q007b`、`q007b1`、`q007c`、`q007c1`、`q007c2`、`q007d`、`q007e`、`q007f`、`q007g`、`q008a`、`q008c` は
登録条件を実行するため、CLI の `--omega` は baseline study にだけ適用される。

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m ttim_lbm --study baseline --omega 1.2 --output research/artifacts/d2q9_baseline.json
python -m ttim_lbm --study q004b --output research/artifacts/q004b_and_manufactured.json
python -m ttim_lbm --study q005 --output research/artifacts/q005_nonresonance.json
python -m ttim_lbm --study q006s --output research/artifacts/q006s_stripe.json
python -m ttim_lbm --study q006r --output research/artifacts/q006r_mode_closure.json
python -m ttim_lbm --study q006n --output research/artifacts/q006n_normal_refinement.json
python -m ttim_lbm --study q006c --output research/artifacts/q006c_coefficient_scaling.json
python -m ttim_lbm --study q006f --output research/artifacts/q006f_checkerboard_filter.json
python -m ttim_lbm --study q006g --output research/artifacts/q006g_low_wave_tangency.json
python -m ttim_lbm --study q006h --output research/artifacts/q006h_cluster_complete.json
python -m ttim_lbm --study q006i --output research/artifacts/q006i_full2d_quadratic.json
python -m ttim_lbm --study q006j --output research/artifacts/q006j_conservation_drift.json
python -m ttim_lbm --study q006k --output research/artifacts/q006k_projection_representability.json
python -m ttim_lbm --study q006l --output research/artifacts/q006l_covariant_correction.json
python -m ttim_lbm --study q006m --output research/artifacts/q006m_anchor_obstruction.json
python -m ttim_lbm --study q006o --output research/artifacts/q006o_forward_error_budget.json
python -m ttim_lbm --study q006p --output research/artifacts/q006p_dual_reporting.json
python -m ttim_lbm --study q006q --output research/artifacts/q006q_forward_error_holdout.json
python -m ttim_lbm --study q007a --output research/artifacts/q007a_cubic_prequalification.json
python -m ttim_lbm --study q007b --output research/artifacts/q007b_cubic_continuation.json
python -m ttim_lbm --study q007b1 --output research/artifacts/q007b1_cubic_radius.json
python -m ttim_lbm --study q007c --output research/artifacts/q007c_quartic_prequalification.json
python -m ttim_lbm --study q007c1 --output research/artifacts/q007c1_quartic_continuation.json
python -m ttim_lbm --study q007c2 --output research/artifacts/q007c2_quartic_shadow_radius.json
python -m ttim_lbm --study q007d --output research/artifacts/q007d_normal_cocycle.json
python -m ttim_lbm --study q007e --output research/artifacts/q007e_adapted_metric.json
python -m ttim_lbm --study q007f --output research/artifacts/q007f_adapted_finite_cocycle.json
python -m ttim_lbm --study q007g --output research/artifacts/q007g_theorem_readiness.json
python -m ttim_lbm --study q007h --output research/artifacts/q007h_rational_spectrum.json
python -m ttim_lbm --study q007h1 --output research/artifacts/q007h1_equivariant_spectrum.json
python -m ttim_lbm --study q007i --output research/artifacts/q007i_direct_nonresonance.json
python -m research.q007j_eigencoordinate_bridge --output research/artifacts/q007j_eigencoordinate_bridge.json
python -m research.q007k_quadratic_jet_bridge --output research/artifacts/q007k_quadratic_jet_bridge.json
python -m ttim_lbm --study q008a --output research/artifacts/q008a_tt_storage_prequalification.json
python -m ttim_lbm --study q008c --output research/artifacts/q008c_wave_qtt_prequalification.json
```

保存済み結果:

- [`research/artifacts/d2q9_baseline.json`](research/artifacts/d2q9_baseline.json)
- [`research/artifacts/q004b_and_manufactured.json`](research/artifacts/q004b_and_manufactured.json)
- [`research/artifacts/q005_nonresonance.json`](research/artifacts/q005_nonresonance.json)
- [`research/artifacts/q006s_stripe.json`](research/artifacts/q006s_stripe.json)
- [`research/artifacts/q006r_mode_closure.json`](research/artifacts/q006r_mode_closure.json)
- [`research/artifacts/q006n_normal_refinement.json`](research/artifacts/q006n_normal_refinement.json)
- [`research/artifacts/q006c_coefficient_scaling.json`](research/artifacts/q006c_coefficient_scaling.json)
- [`research/artifacts/q006f_checkerboard_filter.json`](research/artifacts/q006f_checkerboard_filter.json)
- [`research/artifacts/q006g_low_wave_tangency.json`](research/artifacts/q006g_low_wave_tangency.json)
- [`research/artifacts/q006h_cluster_complete.json`](research/artifacts/q006h_cluster_complete.json)
- [`research/artifacts/q006i_full2d_quadratic.json`](research/artifacts/q006i_full2d_quadratic.json)
- [`research/artifacts/q006j_conservation_drift.json`](research/artifacts/q006j_conservation_drift.json)
- [`research/artifacts/q006k_projection_representability.json`](research/artifacts/q006k_projection_representability.json)
- [`research/artifacts/q006l_covariant_correction.json`](research/artifacts/q006l_covariant_correction.json)
- [`research/artifacts/q006m_anchor_obstruction.json`](research/artifacts/q006m_anchor_obstruction.json)
- [`research/artifacts/q006o_forward_error_budget.json`](research/artifacts/q006o_forward_error_budget.json)
- [`research/artifacts/q006p_dual_reporting.json`](research/artifacts/q006p_dual_reporting.json)
- [`research/artifacts/q006q_forward_error_holdout.json`](research/artifacts/q006q_forward_error_holdout.json)
- [`research/artifacts/q007a_cubic_prequalification.json`](research/artifacts/q007a_cubic_prequalification.json)
- [`research/artifacts/q007b_cubic_continuation.json`](research/artifacts/q007b_cubic_continuation.json)
- [`research/artifacts/q007b1_cubic_radius.json`](research/artifacts/q007b1_cubic_radius.json)
- [`research/artifacts/q007c_quartic_prequalification.json`](research/artifacts/q007c_quartic_prequalification.json)
- [`research/artifacts/q007c1_quartic_continuation.json`](research/artifacts/q007c1_quartic_continuation.json)
- [`research/artifacts/q007c2_quartic_shadow_radius.json`](research/artifacts/q007c2_quartic_shadow_radius.json)
- [`research/artifacts/q007d_normal_cocycle.json`](research/artifacts/q007d_normal_cocycle.json)
- [`research/artifacts/q007e_adapted_metric.json`](research/artifacts/q007e_adapted_metric.json)
- [`research/artifacts/q007f_adapted_finite_cocycle.json`](research/artifacts/q007f_adapted_finite_cocycle.json)
- [`research/artifacts/q007g_theorem_readiness.json`](research/artifacts/q007g_theorem_readiness.json)
- [`research/artifacts/q007h_rational_spectrum.json`](research/artifacts/q007h_rational_spectrum.json)
- [`research/artifacts/q007h1_equivariant_spectrum.json`](research/artifacts/q007h1_equivariant_spectrum.json)
- [`research/artifacts/q007i_direct_nonresonance.json`](research/artifacts/q007i_direct_nonresonance.json)
- [`research/artifacts/q007j_eigencoordinate_bridge.json`](research/artifacts/q007j_eigencoordinate_bridge.json)
- [`research/artifacts/q007k_quadratic_jet_bridge.json`](research/artifacts/q007k_quadratic_jet_bridge.json)
- [`research/artifacts/q008a_tt_storage_prequalification.json`](research/artifacts/q008a_tt_storage_prequalification.json)
- [`research/artifacts/q008c_wave_qtt_prequalification.json`](research/artifacts/q008c_wave_qtt_prequalification.json)

## 文書

- [`docs/LITERATURE_REVIEW.md`](docs/LITERATURE_REVIEW.md): 一次文献と主張範囲
- [`docs/DESIGN.md`](docs/DESIGN.md): 数理・ソフトウェア・検証設計
- [`research/RESEARCH_LOG.md`](research/RESEARCH_LOG.md): 問い、仮説、棄却、改善の記録
- [`research/NEXT_QUESTIONS.md`](research/NEXT_QUESTIONS.md): 次の反証ゲート

## 実装の境界

現在実装済み:

- D2Q9 equilibrium、BGK collision、periodic streaming、厳密な線形化
- Fourier symbol、odd/even spectrum audit、Nyquist direct audit
- moment-based low-\(k\) classification
- simple-branch / ordered-Schur cluster continuation、path reversal、90度回転
- 固定保存量葉への線形射影
- identity-center と general real-block の dense quadratic homological solver
- manufactured nonidentity/resonance oracle
- Fourier-index arithmetic、sector SVD、fixed-leaf zero-mode restriction
- Q005 radial-band normal-dominance/resonance campaign と stripe finite-grid audit
- Q006s fixed-leaf stripe quadratic chart、sector Sylvester solve、residual/shadow campaign
- Q006r full Schur-block pair audit、Riesz external projection、response-cluster closure
- Q006n odd-grid/relaxation refinement、normal-gap/Nyquist anchor、全 pair coefficient audit
- Q006c full pair completeness、target operator/SVD/forcing/response、固定window scaling fit
- Q006f conservative filter algebra、100条件のspectral/coefficient/scaling audit
- Q006g 140条件のdiagonal shear/acoustic \(N^{-4}\) tangency audit
- Q006h 24実座標cluster-complete family、100条件・300 pairのfiltered prequalification
- Q006i 24実座標full-2D dense quadratic chart、非自明な \(R_2\)、独立Hessian・残差・shadow audit
- Q006j 3種の保存量集約、collision/streaming/filter分解、一様fixed-leaf projection control
- Q006k 一様projectionのULP／実現誤差、固定3-population localized diagnostic
- Q006l collision/filter stagewise covariant correction、translation／C4・unique-anchor audit
- Q006m uniform-equilibrium tie、translation固定点矛盾、8本のanchor-gap ladder
- Q006o standard-map componentwise ULP budget、uniform projection policy比較
- Q006p Q006i original-threshold／forward-error-policy dual-reporting、64方向の完全照合
- Q006q 2 independent scenario、128 trajectory・48,000 component forward-error holdout
- Q007a 全2,600 cubic homological block、order-2 reproduction、共役／C4 count closure
- Q007b 全2,600 cubic forcing／coefficient、独立3次微分、残差次数、100-step shadowing
- Q007b1 独立finite-radius／analytic Jacobian／immersion／near-resonance診断
- Q007c 全17,550 quartic homological block、order-2／3 control、共役／C4 count closure
- Q007c1 全17,550 quartic forcing／coefficient、独立4階微分・forcing、残差・shadow audit
- Q007c2 独立64方向のquartic shadow amplitude／horizon localization、forward-error budget
- Q007d 解析的full-map／quartic-chart Jacobian、fixed-leaf Euclidean projector、10-step normal cocycle
- Q007e 289 Fourier blockのRiesz invariant split、Stein metric、実往復、adapted matrix-free SVD
- Q007f fixed metric／varying quartic tangent、複素共役Jacobian／adjoint、33点の10-step adapted cocycle
- Q007g 固定定理の構造仮定、\(L=89\) spectral quotient、sector／full-spectrum証拠差分、proof-object inventory
- Q007h 288非零blockの有理区間Neumann／Bauer--Fike audit、全5線形仮説通過、C4 validity棄却
- Q007h1 72 C4代表からのexact preconditioner輸送、線形split／可逆性／normal gap／degree-90 tail認証
- Q007i 4 selected modulus型と643 external diskの有理log区間、次数2--89のdirect nonresonance認証
- Q007j 12有理Krawczyk固有対、6 selected-disc対応、全24 modeのright／biorthogonal-left輸送認証
- Q007k exact quadratic forcing／保存恒等式、全300 graph-gauge homological systemの有理Krawczyk認証
- Q008a degree 2／3／4 local Fourier係数、4 TT配置、sparse格納・忠実度・timing診断
- Q008c wave／branch・3-bit wave QTTの4配置、一般TT作用、格納・忠実度・timing診断
- 二次多項式チャートの output-block TT-SVD と sparse storage baselines

未実装・未通過:

- 認証済みspectral manifoldと登録数値chartのcubic／quartic jet同定、explicit local radius
- TT-cross、境界条件、外力、D3Q27

Q007iにより固定17² map・固定保存量葉に対する定性的な局所解析的不変多様体の存在と\(C^{90}\)一意性を、
Q007jにより登録数値eigencoordinatesと厳密selected subspaceの対応を、Q007kにより登録Q006i二次係数と
定理多様体のgraph-gauge quadratic jetの対応を認証した。次のゲートはQ007lであり、2,600 cubic tripleだけを
区間化してQ007bの数値三次jetを同定する。quartic係数とexplicit radiusは後続の独立gateとする。
