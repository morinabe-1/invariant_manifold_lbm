# Q012c1: leading viscosityを保つD3Q27 damping修正 — 事前登録 2026-09-07

Q012cの無変更BGKに対する`passed / rejected`を保持し、104実座標の候補を変えずに
高波数減衰を加えた**別の写像**を比較する。元のBGKの多様体構築に成功したとは扱わない。
Q012cの小波数shear interactionの悪条件化まで減衰修正で直るとは仮定しない。

## 入力と登録domain

Q012c artifactの改行正規化SHA-256は
`3dc9da853cbea183546d5646916e50828faaa89156ca217d16e1b6dc68cf886d`、result digestは
`79a17890a273ca26ab297a8c98a0fe550b8eae1fedc74f3a2452c836f39b3863`。
source seals、validity全8項目、`rejected`、viable family 0を照合する。
Q012c入力checkerも実行する。履歴全trajectoryの再実行とは呼ばない。

- odd `N=(17,33,65)`、omega `(1.0,1.2,1.5,1.8)`。
- `n in {-1,0,1}^3 \ {0}`の全26波数、hydrodynamic 4次元、計104実座標。
- `delta M=delta Px=delta Py=delta Pz=0`。zero-wave correctionは23次元kineticのみ。
- 各`N,omega`で無変更BGKを1回、各filterのeta `(0.01,0.02,0.05,0.1)`を計算する。
  baseline 12条件、修正96条件、合計108条件。各条件は3,081 block pair／5,460 product列。
- baselineの全pairはQ012c shell=3の保存値と照合する。同じpoint frame・計算順で
  cycleの数値が一致することを要求する。旧condition／残差失敗を消さない。

## 二つのfilterと数学的な差

周期shiftを`T_(j,+/-)`とし、populationごとに作用する

\[
 D=\frac14\sum_{j=1}^3(2I-T_{j,+}-T_{j,-}),\qquad
 s(k)=\sum_{j=1}^3\sin^2(k_j/2)
\]

を用いる。比較する写像は`Phi_(eta,p)=(I-eta D^p) Phi_BGK`であり、

\[
 \mu_{\eta,p}(k)=1-\eta s(k)^p,\qquad p=1,2.
\]

`p=1`をLaplacian型、`p=2`をbiharmonic（四階）型と呼ぶ。登録etaでは
`mu>=0.7 / 0.1 > 0`で、eigenvector／spectral projectorは変わらず、各固有値がmu倍される。
`mu(0)=1`、signed axis permutationに対して不変であり、全4保存量を数学的に保つ。
axis Nyquistの`lambda=-1`は`-(1-eta)`になる。

`s(k)=|k|^2/4+O(|k|^4)`から、同じomegaで

\[
 \nu_{p=1}=\nu_{BGK}+\eta/4,\qquad
 \nu_{p=2}=\nu_{BGK},\qquad \nu_{BGK}=(1/\omega-1/2)/3.
\]

四階型の追加減衰は先頭次数が`eta |k|^4/16`である。
正の実scalar multiplierなのでacousticの位相速度は変わらない。
この小波数展開は有限kで無変更BGKと同一であることを意味しない。
Laplacian型は粘性変化を測る対照であり、**元のleading viscosityを保つ主候補としては選ばない**。

Laplacian型は登録etaでconvex stencilだが、四階型には負のstencil重みがある。
四階型を全状態でpositivity-preservingとは呼ばない。
そのstencil l1 normは登録範囲で`1+15 eta/4`。一様正平衡に対する小摂動の安全域と、
有限sampleのpositivityを区別する。元のover-relaxed BGK自体も全状態のpositivityを保証しない。

## 代数・写像・hydrodynamicsの検証

- `eta=0`のfilterはbitwise identityとし、元mapを変更しない。
- 非立方`(3,5,7)`上のlinear filterをFFT multiplierと比較する。
  seed `2026090707`、各filter×4 eta、relative誤差 `<=5e-13`。
- mean／4保存moment、streamingとの可換性、48立方操作との共変性、z独立D2Q9 liftとの
  可換性を `<=5e-12`で確認する。D2側の同型stencilは独立に2軸で評価する。
- impulseからstencil係数和1、p=1でnegative係数なし、p=2でnegative係数あり、
  p=2のl1 norm `1+15 eta/4`を `<=5e-13`で確認する。
- `5^3`、seed `2026090708`の平衡population摂動`1e-4`から、各filter×4 eta×4 omegaで
  32 stepを実行する。全iterate finite・positive、site平均保存量drift `<=2e-13`。
  これは固定sampleであり全振幅や無限時間の保証ではない。
- Q012bと同じ4 ray、small radius `(0.04,0.02,0.01,0.005)`で両shear減衰とacoustic対を確認する。
  最小radiusで各filterの上記`nu_eff`にrelative誤差 `<=1e-4`、acoustic速度に`<=1e-5`。
  四階型の追加減衰`-log(mu)/|k|^4`は`eta/16`へrelative誤差 `<=1e-4`。
  cancellationを避ける追加減衰評価は`-log1p(-eta*s^p)`を用いる。
- 3 axis Nyquist × 2 filter × 4 eta × 4 omegaで直接symbolの`-(1-eta)`を確認する。
- 独立physical mixed finite differenceで新map Hessianを確認する。
  seed `2026090709`、`3^3`、omega=1.2、各filter×4 eta、step `(1e-3,5e-4,2.5e-4)`、
  最小stepのrelative誤差 `<=1e-5`。新Hessianはoutput波数のmu倍であり、
  input波数のmuをforcingへ誤って掛けないことを負の対照で検出する。

## 全二次operatorと全格子normal ordering

Q012cのshear 2次元block、Sym²、graph gauge、正規化、閾値を維持する。
各pairについて、input dynamicsを`mu_i`／`mu_j`倍、external dynamicsとforcingを
**outputの`mu_(i+j)`倍**する。基底・projector・zero-wave leafは変えない。
旧operatorの単なる定数倍ではないので、全pairで新たにfull SVDとsolveを行う。

- 数値rank threshold `100 eps max(shape) sigma_max`。
- condition `<=1e8`、forcing-relative solve残差 `<=1e-10`。
- graph gauge／zero-wave moment `<=5e-12 max(1,||H||)`。
- singular-compatibleも非共鳴gateは通さない。
- local／global-l2 response、rank／condition失敗とresidual-only失敗を分けて保存する。
- 全離散波数のorbit inventoryはQ012cと同じ。固有値と各restrictionのnormをmu倍し、
  selected最小modulusとexternal最大modulusを再比較する。
  normal gap `>1e-10`、external最大 `<1-1e-12`、selected全て`0<|lambda|<1`、
  projector norm `<=100`、scaled local Schur sep `>=0.02`。
- `N=17,omega=1.2,eta=0.05,p=2`では全波数の直接eig／full-grid計算と
  scaled-orbit結果を `<=5e-12`で比較する。

無変更BGKと同じsolverを使う。今回、残差上限の変更、post-hocなiterative refinement、
悪条件pairの除外、selected座標の削減はしない。必要なsolve精度改善は別gateとして登録する。

## 判定・保存・次の問い

入力seal、全108条件・全pair、baseline再現、構造・独立対照、finite JSONをvalidity gateとする。
失敗時は`inconclusive`。有効な計算では各family（filter,eta,omega）を、全3格子の
coefficient／normal／map／hydrodynamic gateで判定する。

四階型に全gateを通すfamilyがあれば`accepted`とし、**最小eta、次いで最小omega**で選ぶ。
なければ`rejected`とし、Laplacian型だけの通過を元粘性保持の成功へ読み替えない。
通過後は選んだfamilyを3格子で独立に再実行し、Q012dでその**修正map**のdense quadratic W/Rを構築する。
通過familyがなくても、登録した`eta=0.05,p=2,omega=1.2`を3格子で再実行して証拠を照合する。
この再実行は全108条件の再実行ではなく、選択候補／固定対照の独立再現検証である。

全pairは各条件のJSON tableへ分けて保存し、manifestからshaとresult digestで参照する。
途中のtableだけでは完了扱いせず、全coverageを満たしたmanifestで判定する。
manifest: `research/artifacts/q012c1_d3q27_damping.json`。
pair tables: `research/artifacts/q012c1_d3q27_damping/`。
helper: `research/d3q27_damping.py`、runner: `research/q012c1_d3q27_damping.py`。

これは3格子上の有限次・有限sample prequalificationであり、3D SSMの存在・一意性、
ball全体のpositivity、normal attraction、TT優位性、無変更BGKの縮約を認証しない。
