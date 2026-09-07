# Q012b: 3D hydrodynamic clusterとNyquist parity — 事前登録 2026-09-07

Q012a `9987eed`のD3Q27 BGK symbolを用い、4次元hydrodynamic clusterを`k=0`から
追跡する。二つのshear branchが縮退しても、その2次元部分空間を判定単位とする。
局所Fourier blockの分離を、異なる波数間のnormal dominanceやSSM存在と混同しない。

## 入力

Q012a artifactの改行正規化SHA-256
`b26c6dfde65b24f424fcadffe9c9c75f4236171242e819921e6e0d06cf5ba327`、
result digest`385e0e55211c24f99b8dd4b5591862b5c83295f5199beb286f0db56bbce4801b`、
helper／runner hash、`accepted`、全7 auditを照合する。
前提のD2Q9状態もQ012aのprerequisite checkerで再照合する。

## 連続pathと判定

- omega `(1.0,1.2,1.5,1.8)`。
- rayはaxis `(1,0,0)`、face diagonal `(1,1,0)/sqrt(2)`、body diagonal
  `(1,1,1)/sqrt(3)`、一般方向`(1,2,3)/sqrt(14)`。
- radial gridは`0,0.0125,...,1.8`（145点）。最初に失敗した点でpathを止める。
- `k=0`ではeigenvalue 1の4次元clusterを選ぶ。次点では前の4固有値の集合との
  minimum-distance assignmentで候補集合を得てordered complex Schurで部分空間を構築する。
  分離不能な固有値を恣意的に切らない。内部permutationは同一clusterとして扱う。
- per-pointの閾値: equilibrium tangentへのminimum alignment `>=0.75`、
  前点とのmaximum principal angle `<=0.20 rad`、external eigenvalue gap `>=0.05`、
  Schur Sylvester operatorの最小特異値`>=0.02`、spectral projector norm`<=100`、
  invariance／idempotency／commutator residual`<=1e-12`。
- shearは非零kで4固有値のうちimaginary partの絶対値が小さい2個を候補とし、
  acoustic対とのgap`>1e-8`がある場合だけordered Schur subspaceを作る。
  transverse momentum planeへのminimum alignment`>=0.75`、densityとlongitudinal
  momentum leakage（momentum Frobenius normで規格化）の各値`<=0.25`を要求する。
  shear内部のlabel、固有値一致、個別固有ベクトルの一致は要求しない。
- path reversalはaccepted endpointのclusterから逆行し、forwardとのorthogonal projector差
  `<=1e-10`を全点で確認する。x/y交換とcyclic axis permutationで別pathを実行し、
  輸送した4次元projectorおよび定義済みshear projectorとの差`<=1e-10`も確認する。
- 各rayの最後のpassと最初のfailをbracketで報告する。全16 pathに非自明なprefix
  `k_last_pass>=0.5`を要求する。上端1.8までpassの場合は右打切りと記録する。
  全rayの最小cutoffはsample-based radial boundであり、sphere全体の証明や厳密最大値ではない。

## small-k、parity、grid projection

small-k radius`(0.04,0.02,0.01,0.005)`を同じ4 ray・4 omegaで評価する。
二つのshearについて`-log|lambda|/|k|^2`が`nu=(1/omega-1/2)/3`へ収束し、
最小radiusのrelative誤差`<=0.01`を要求する。acoustic対の`|arg(lambda)|/|k|`は
`1/sqrt(3)`にrelative誤差`<=0.01`で一致することを確認する。各値と誤差列を記録する。

奇数`17^3,33^3`、偶数`16^3,32^3`の全離散波数を監査する。Q012aの立方対称性と
共役関係により、`sort(min(i,N-i))`のorbit代表へ集約して27次固有値を計算し、
orbit multiplicityでfull-grid countを復元する。4³／5³では別にfull-grid brute forceを
実行し、同じ結果となることを確かめる。全orbitのmultiplicity合計が`N^3`であることが必須。

unit tolerance`1e-10`で、odd strict-unit count=4、even=7を仮説とする。
全gridで`k=0`の4個は`lambda=+1`、evenでは3本のaxis Nyquistに各1個の`lambda=-1`を期待する。
`A(pi,0,0), A(0,pi,0), A(0,0,pi)`をomega全4値で直接評価する。
unit分類境界に`[0.1 tol,10 tol]`距離の固有値があれば数値的に未解決と記録する。
even Nyquistは構築候補に含めない。低波数候補はodd gridの4 ray全体の最小cutoff以内とし、
離散波数数と線形real-coordinate次元を数えるだけで、非線形閉包・外部非共鳴は次のQ012cへ渡す。

## 成功条件と境界

入力seal・登録coverage・finite JSONはvalidity gate。これを満たさない場合は`inconclusive`。
有効な計算でprefix／reversal／symmetry／small-k／parityの仮説を満たさなければ`rejected`とする。
全gate通過時にのみ`accepted`。runnerは`research/q012b_d3q27_spectral.py`、
helperは`research/d3q27_spectra.py`、成果物は`research/artifacts/q012b_d3q27_spectral.json`。

次はQ012cで104実座標までのfirst-shell候補を含め、固定4保存量葉上のFourier-compatible
quadratic operator、normal ordering、second-harmonic resonanceを調べる。
Q012bだけでは3DのSSM存在・一意性、通常吸引、非零波数W/R、TT優位性を認証しない。
