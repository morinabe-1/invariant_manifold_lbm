# Q012a: D3Q27基礎オラクル — 事前登録 2026-09-07

目的はD2Q9で検証済みのパラメータ化法を3Dへ拡張するための、完全離散写像と独立な
代数オラクルを作ることである。対象は周期・無外力・isothermal BGK、`0 < omega < 2`。
`research/d3q27.py`を実験用実装、`research/q012a_d3q27_foundation.py`を再現runnerとする。
既存D2Q9 packageの証明に用いたsource fingerprintは保ち、3D runnerとhelperを別々にhashする。

## 着手条件と研究順序

NEXT_QUESTIONSのQ012条件を次の証拠に対応させる。`study_gate=passed`だけで
科学的仮説を成功と判定しない。各artifactの内容hash、対応runner、必要な個別判定を照合する。
これは保存済み証拠の整合監査であり、過去の全trajectoryを再実行したという主張ではない。

| Q012条件 | 証拠と限定 |
|---|---|
| branch／cluster | Q004b continuous paths、parity、manufactured oracleがaccepted |
| sector-aware非共鳴 | Q005の元isotropic候補はrejected。Q006hの修正cluster-complete familyはcoefficient／spectralともpass |
| fixed-leaf二次chart | Q006iの旧conservation rejectionを保持し、Q006pのpolicy column全gate、Q006qの独立holdoutを使用 |
| same-initial shadowing | Q007apのrepaired MPFR-85 backend、登録tube、sampling-timeのall-iterate certificate |
| 表現忠実度 | Q011gの忠実度passとTT圧縮rejection、Q011hの72本・64-step sparse／dense同値性 |
| TT-cross | 勝者がないため条件分岐は非該当。TT-crossを開始しない |
| positivity／conservation | Q006p/qとQ011hの明示的有限trajectory gate |
| 費用 | Q010の自然sparse baselineに対する固定8 TT候補のcost rejectionを保持 |

各証拠のmap、grid、norm、precision、振幅範囲は個別のまま保持する。異なる証拠を
単一の3D存在定理や実用半径の証明へ合成しない。Q011np以降のrepaired mapの高次
滑らかさ・degrees 34--90非共鳴は独立した未解決研究として残す。
Q012aの後はQ012b（3D hydrodynamic cluster、二重shear、Nyquist parity）、
Q012c（固定保存量葉の非零波数homological operator）、Q012d（dense quadratic W/R）、
その後に3D sparse／TT費用比較を行う。3D Taylor–Green、force／wallはさらに後とする。
この依存順で、従来の単一witnessごとの直列順序を更新する。

## 定義と数学的な対照

一軸速度`(-1,0,1)`、有理重み`(1/6,2/3,1/6)`の三重積とする。
population順は`(cx,cy,cz)`のlexicographic、`cz`が最速。空間arrayは`(nz,ny,nx,27)`。
`cs2=1/3`。保存量は`(M,Px,Py,Pz)`、非零波数構築ではその4量を固定した葉を使う。

平衡分布はD2Q9と同じ二次isothermal式

\[
 f_q^{eq}=w_q[\rho+3c_q\cdot j+\{9(c_q\cdot j)^2-3j\cdot j\}/(2\rho)]
\]

を採る。1 stepはcollisionの後に`(cz,cy,cx)`だけ周期rollする。
線形symbolは`A(k)=diag(exp(-i k.c)) C`、`C=(1-omega)I+omega E M`。
`M E=I4`を確認し、`k=0`の4保存方向と23 kinetic方向を区別する。

D2Q9埋込み`J`は各`z`平面で
`(J f)_(cx,cy,cz)=w_cz f_(cx,cy)`、逆方向は`cz`についての和を各平面に返す。
`rho>0`の任意のD2Q9状態で`Phi3 J=J Phi2`が成立する。これは
`jz=0`と平衡式の因子化、`z`独立性によるstreamingの可換性から導く。
この同一性は三次元の全てのz独立状態がD2Q9 liftであることを意味しない。

tensor-productの根拠はCoreixas–Chopard–Latt (2019), Sec. VI A,
[arXiv:1904.12948v4](https://arxiv.org/pdf/1904.12948)と
[DOI](https://doi.org/10.1103/PhysRevE.100.033305)を確認した。
以下の有理moment同一性とrank-6反例は本gateで直接計算する。

## 登録検証と閾値

- 有理quadrature: `0 <= ax,ay,az <= 5`の216 monomialを、分散`1/3`の独立Gaussian
  momentsとexact比較する。速度27個の一意性、正重み、sum=1、重みshell
  `(8/27,2/27,1/54,1/216)`と個数`(1,6,12,8)`もexact比較する。
- 等方性: rank 2／4の全tensor成分をGaussian tensorとexact比較する。
  rank 6は負の対照とし、`<cx^6>=1/3`とGaussian値`5/9`の不一致を必ず記録する。
  四次等方性、立方対称性、全次数でのSO(3)等方性を混同しない。
- 平衡moment: seed `2026090701`、grid `(3,5,7)`、rho in `[0.98,1.02]`、
  j各成分in`[-0.01,0.01]`。質量・運動量・pressure tensor
  `rho/3 I + j j^T/rho`の最大absolute誤差`<=5e-15`。
- periodic streaming: 全27方向のimpulse移動を非立方`(3,5,7)`上でbitwise照合。
  random状態の各populationのmultisetが保存されることもbitwise照合。
- BGK／leaf: omega `(1.0,1.2,1.5,1.8)`、grid `3^3,5^3`、seed
  `2026090702`から各2状態、平衡へのpopulation摂動`1e-4`、32 step。
  全状態finite・positive、保存量driftをsite数で割った値`<=2e-13`。
  fixed-leaf projectorのidempotencyと保存momentを`<=5e-14`で確認。
  binary64でのexact conservationやall-iterate positivityは主張しない。
- D2Q9 lift: 非平衡D2Q9状態、nz `(1,3,5)`、上記4 omega、16 step、seed
  `2026090703`。collision／stream／full-map／moments／marginalの可換誤差
  `<=2e-14`。Fourier intertwining `A3(kx,ky,0)J=J A2(kx,ky)`も
  `(0,0),(.37,-.22),(pi,0)`で`<=2e-14`。wrong-z-weight対照は失敗すべき。
- 立方対称性: 48 signed axis permutations全てについてvelocity／weight closureをexactに、
  `3^3`上の非線形写像と一般波数`(.31,-.27,.19)`のsymbol covarianceを`<=2e-14`で確認。
- 線形化: seed `2026090704`、`3^3`上、omega `(1.2,1.5)`、central FD step
  `1e-4,5e-5,2.5e-5`、誤差の二次収束比`[3.5,4.5]`と最小stepのrelative誤差`<=1e-7`。
  physical-space作用とFFT-symbol作用のrelative誤差`<=2e-14`。
- 一様center oracle: 局所27成分、4保存座標、既存のhomological solverでquadratic jetを解く。
  解析Hessianとのrelative誤差`<=1e-12`、`R2`とgauge／homological残差`<=1e-12`。
  odd `3^3`へliftし、固定32方向（seed `2026090705`、`|a_rho|>=0.1`かつ
  `||a_j||>=0.1`の非退化方向）、振幅`1e-2,5e-3,2.5e-3,1.25e-3`で
  linear／quadratic残差slopeが`[1.9,2.1] / [2.9,3.1]`に入ることを確認。

入力不整合・数値不正・登録coverage不足は`inconclusive`、有効な計算で数学的検証が失敗すれば
`rejected`とする。全gate通過時だけ`accepted`。rank-6負の対照は想定したモデル限界を示す。
result digestは数値証拠とgateを覆い、時刻・runtime計測は別に置く。
成果物は`research/artifacts/q012a_d3q27_foundation.json`。
3D非零波数chart、SSM存在・一意性、normal attraction、TT圧縮率はQ012aの結論に含めない。

## Q012a結果（2026-09-07）

前提10 artifactのsealと必要な個別判定を照合し、7監査すべてを通過した。
判定は`passed / accepted`。D2Q9回帰・manufactured oracleと合わせた86テストを通過した。

| 検証 | 結果 |
|---|---|
| 有理quadrature | 216/216一致、rank 2／4等方性exact |
| 平衡moment | 最大absolute誤差 `2.22045e-16` |
| streaming | 27/27 impulse一致、population multiset不変 |
| 保存量／positivity | 16本・512 step、最大site平均drift `3.28955e-15`、最小population `0.00418275` |
| D2Q9 lift | 12本・16 step、最大誤差 `8.88178e-16`、symbol可換誤差 `1.14439e-16` |
| 立方対称性 | 48/48通過（proper rotation 24）、最大map誤差 `2.77556e-16` |
| 線形化 | FD誤差減少比 `4.00000`、FFT照合誤差 `<=4.78831e-16` |
| 4保存座標center oracle | Hessian誤差 `1.04467e-15`、`||R2||=2.15360e-15` |
| 残差次数 | 32方向でlinear `1.99693--2.00396`、quadratic `2.99693--3.00396` |

rank 6の負の対照では、`<cx^6>=1/3`、unit face diagonal方向では`1/2`であり、
Gaussian値`5/9`とも一致しない。従って連続回転の全次数等方性を主張しない。

[成果物](../research/artifacts/q012a_d3q27_foundation.json)の改行正規化SHA-256は
`b26c6dfde65b24f424fcadffe9c9c75f4236171242e819921e6e0d06cf5ba327`、result digestは
`385e0e55211c24f99b8dd4b5591862b5c83295f5199beb286f0db56bbce4801b`。
helper／runner SHA-256は
`4a220aa1f88aaf2b2bdd5ce3fa82dfed3d56b466c545d1385926f7a9e2dcb89a` /
`4b8a87a2e8d7d41f8e56d35cf2e060efb2e3ee7fe3d36723c1b2e68456ffe9fa`。
次はQ012bで4次元hydrodynamic clusterと二重shearを追跡し、Nyquist parityを監査する。
