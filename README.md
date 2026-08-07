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
viableと判定した。事前登録した規則で \((\eta,\omega)=(0.01,1.5)\) を選択したため、次は
\(17^2\) 上でこの変更写像に固定したfull 2D dense quadratic chartをQ006iで構築する。
stripe を含め、
存在・一意性 gate を通るまでは非零波数の対象を
**candidate spectral subspace / candidate chart** と呼ぶ。

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

## 再現

Python 3.11 以上を使う。`q004b`、`q005`、`q006s`、`q006r`、`q006n`、`q006c`、`q006f`、
`q006g`、`q006h` は
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
- 二次多項式チャートの output-block TT-SVD と sparse storage baselines

未実装・未通過:

- Q006i の \(17^2\)・24実座標filtered full 2D dense quadratic candidate chart
- TT-cross、境界条件、外力、D3Q27

従って次のゲートは、Q006hが選んだ変更写像に対するQ006i dense quadratic chartである。
このoracleを通過するまでTT圧縮へは進まない。
