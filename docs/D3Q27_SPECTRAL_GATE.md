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

## Q012b結果（2026-09-07）

事前登録`fbc39fb`の全validity／hypothesis gateを通過し、`passed / accepted`となった。
保存artifactとsourceの照合・数値cycle再計算を含むD3Q27、D2Q9、manufactured oracleの
100テストが通過した（66.77 s）。変更した3 Pythonファイルのruff検査も通過した。
4 ray × 4 omegaのaccepted sampleは合計1,577点で、全経路に`|k|>=0.5`のprefixが得られた。
以下は各方向の「最後のpass / 最初のfail」である。

| omega | axis | face diagonal | body diagonal | generic |
|---|---|---|---|---|
| 1.0 | 0.7625 / 0.7750 | 0.9875 / 1.0000 | 1.1125 / 1.1250 | 0.9250 / 0.9375 |
| 1.2 | 0.9250 / 0.9375 | 1.1875 / 1.2000 | 1.3375 / 1.3500 | 1.1125 / 1.1250 |
| 1.5 | 1.1625 / 1.1750 | 1.3875 / 1.4000 | 1.5375 / 1.5500 | 1.3750 / 1.3875 |
| 1.8 | 1.3750 / 1.3875 | 1.4500 / 1.4625 | 1.4000 / 1.4125 | 1.4750 / 1.4875 |

全16本で最初の失敗は`equilibrium_alignment < 0.75`であり、固有値衝突でも
Schur分離限界でもなかった。従ってこれは登録した物理的近接条件付きのsample cutoffであり、
kinetic clusterからの数学的分離が失われる最大波数を求めた結果ではない。
未計算の方向・sample間・cutoff以遠については判定しない。

accepted sampleの最小external eigenvalue gapは`0.163049`、最小Schur Sylvester sepは
`0.0969025`、最大spectral projector normは`3.54964`だった。
path reversalの4次元／shear projector差は本実装でともに`0`、独立に回転したpathとの差は
最大`7.02353e-15 / 5.27221e-13`だった。shear内部の固有vectorやlabel一致は要求していない。
small-k最小radius`0.005`の最大relative誤差は、二つのshear減衰率で`2.05835e-6`、
acoustic速度で`6.81589e-7`となった。

| grid（omega=1.2） | orbit代表数 | 復元した全波数数 | strict unit count | 最大nonunit modulus |
|---|---:|---:|---:|---:|
| 16³ | 165 | 4,096 | 7 | 0.9829145254 |
| 17³ | 165 | 4,913 | 4 | 0.9848604492 |
| 32³ | 969 | 32,768 | 7 | 0.9957193806 |
| 33³ | 969 | 35,937 | 4 | 0.9959747092 |

分類境界にある固有値は0個。4³／5³のbrute-force対照とも一致し、3軸×4 omegaの直接評価で
各axis Nyquistに`lambda=-1`が1個ずつ得られた。偶数格子の3個の追加center方向を除外側へ
隠さず、主たる非零波数構築は奇数格子上の固定4保存量葉へ限定する。

4 rayの最小cutoffを半径としたodd-grid inventoryは、omega順に17³で
`32 / 80 / 122 / 202`波数、33³で`256 / 460 / 948 / 1574`波数だった。
これは4倍すれば実座標次元になる候補数であり、全候補の採用を意味しない。
Q012cではより小さなfirst-shellから、異なる波数間のnormal orderingと
Fourier-compatible quadratic operatorを独立に検査する。

[成果物](../research/artifacts/q012b_d3q27_spectral.json)の改行正規化SHA-256:
`53753f2d2344d5ec308a7498875703f0c89ae8d184ade1d8f19377ffbc10b870`。
result digest:
`b26abf59676f6689216f9143068d7a06dfad432faf7c723e9ab4b3fec3fa632d`。
runner／spectral helper SHA-256:
`e8562b2cf1955aeaf7faed84665d91ea02fcb8997143e454c59c7d7cc7dd624a` /
`355498c6ca5d2d3ba655fc64dddd6d853d3ad4cd7e87979bfba752a688df27a7`。

再現コマンド:

```powershell
python -m pytest tests/test_d3q27_foundation.py tests/test_d3q27_spectral.py tests/test_d2q9.py tests/test_manufactured.py -q
python -m research.q012b_d3q27_spectral --output research/artifacts/q012b_d3q27_spectral.json
```
