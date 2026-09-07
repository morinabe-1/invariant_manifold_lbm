# Q012d: D3Q27 104実座標のquadratic W/R — 事前登録 2026-09-07

前turnのQ012c1aは全条件計算・独立再現・保存・commitまで完了したためprogressである。
本問は、受理したcandidate spectral subspaceに接する二次jetを、実座標のW/Rとして構築し、
full-grid非線形写像で不変性欠陥の次数改善と有限sampleのtrajectory精度を確認できるか。
SSMの存在・一意性・正の半径・非線形normal attractionをこのgateでは認証しない。

## 入力と対象

Q012c1aのartifact SHA
`b254057450e1deaaa2cd2791fa4547455e27a76352c99b5923e5de2a9434ddbe`、result digest
`f652b5b9d6c0f3fc151d4de6927f36445d518f4cff993cdbbfc5b1a848f6587e`、全helper／runner seal、
validity全11項目、selected family、選択した3 tableとindependent replayを照合する。
Q012c1aのinput checkerも実行するが、全履歴のtrajectory再実行とは呼ばない。

- 本構築は`N=17`、`omega=1.5, eta=.02, p=2`。
- 写像は`Phi=(I-eta D^2) Phi_BGK`、`D=1/4 sum_j(2I-Tj+-Tj-)`。無変更BGKではない。
- 26個の`n in {-1,0,1}^3 \ {0}`を全て含む。各波数のshear平面2＋acoustic2、104実座標。
- 全質量・3運動量固定葉。k=0の補正は23次元kineticのみ。中心座標は追加しない。
- mや波数集合を縮めて通過させず、全3,081 block pair・5,460 symmetric product列を解く。
- 凍結したD2Q9・Q012a/b/c/c1/c1aのsourceを変更せず、新しいresearch moduleを用いる。

## Fourier正規化・実座標・二次方程式

FFTは`norm=ortho`。物理場は`exp(i k.x)/sqrt(N^3)`を基底とする。
二次forcingはsymbol-local値を`sqrt(N^3)`で割る。この係数を有限差分で独立に検証する。
正の波数代表は「最初の非零成分が正」の13波数とし、各4複素座標を
`z=(a_cos+i a_sin)/sqrt(2)`で実座標化する。負側は共役基底を用い、acoustic +/-の対応を入れ替える。
104×104変換Tと逆T*を明示し、`T* T=I`、実場への復元、左右双対性を検証する。
shear平面は2次元のまま扱い、個別固有ベクトルを一意と仮定しない。

\[
 W(a)=f_*+Va+\tfrac12H[a,a],\qquad
 R(a)=\Lambda a+\tfrac12G[a,a],\qquad LH=0.
\]

各Fourier sectorでは
`A H - H(Sym^2 Lambda) + B(V,V) - V G = 0`、`G=L B(V,V)`を使う。
outputのmuをAとBへ、inputのmuをそれぞれのLambdaへ掛ける。
Q012c1aと同じrank閾値、condition `<=1e8`、forcing-relative solve残差`<=1e-10`、
graph gauge・zero conserved moment`<=5e-12 max(1,||H||)`を維持する。
SVD代替は不収束時だけ。残差失敗への代替・iterative refinement・閾値変更はしない。

同一2次元shear blockのSym²とblock間の二重和を区別し、Taylorの1/2を保つ。
全5460個のcomplex monomialについてoutput waveと27 populationのdense fiberを保存する。
Rの二次項は104×104×104の実Hessianにも変換し、Fourier側の評価と照合する。
全物理空間の巨大W2配列は不要だが、係数の削除・TT近似は行わない。

## 構造・独立対照

- 全26 frameの不変性・双対性・共役対応・実Lambdaのimaginary leakageを`<=5e-12`で検証する。
- 全pairのgauge／zero moment、実Hessianの対称性、Fourier coefficientsの共役整合を確認する。
  二次係数の共役・realification relative誤差は`<=1e-9`。
- TによるFourier評価とdense real R2評価、pair-loopと集約fiber評価をseed `2026090713`の
  8実方向で比較し、relative誤差`<=1e-10`を要求する。
- 実GのFrobenius norm `>1e-6`、zero-wave kinetic coefficient norm `>1e-8`を確認する。
  mean generationを保存momentの生成と呼ばない。
- physical-space analytic HessianとFourier forcing、homological identityを8方向対で比較する。
  前者relative誤差`<=1e-10`、後者`<=1e-9`。
- 同じ8方向対でfull nonlinear mapのmixed finite differenceを
  h`(.01,.005,.0025)`、seed `2026090714`で評価し、最小hのrelative誤差`<=1e-5`を要求する。
- 48立方対称操作×seed `2026090715`の4方向で、線形・二次WおよびRの共変性を
  relative誤差`<=1e-9`で比較する。実際のpopulation／格子rotationを独立対照とする。

## 残差次数

seed `2026090711`の64個の独立なGaussian実方向を座標l2 norm=1に正規化し、
振幅`(.008,.004,.002,.001)`で線形chart/Rlinearと二次chart/Rquadraticの欠陥を測る。
全64方向でlog-log傾きが線形`[1.9,2.1]`、二次`[2.9,3.1]`、
最小振幅の二次欠陥が線形欠陥の`<=.1`であることを要求する。
次数fitに用いる各欠陥が`100 eps max(1,||f_*||2)`より大きいことを要求し、
floorに埋もれたgeneric方向を無断で落とさず、該当したらその判定を未解決とする。

axis／face／body代表の純mode各8実方向、計24特殊方向も保存するが、
退化方向で残差が丸めfloorに入った場合は傾きを次数の証拠としない。
generic方向のうち最初の8本でGを落とした対照も評価し、二次残差が残ることを
傾き`[1.9,2.1]`で確認する。R2をゼロとして済ませないための負の対照である。

## 有限trajectory・保存・正値sample

seed `2026090712`の16方向×振幅`(.008,.004,.002)`、64 step。
線形chartと二次chartは、それぞれ同じa0から自身のWでfull trajectoryを初期化する。
各chartの縮約trajectoryと対応するfull trajectoryを比較する（別初期化であることを記録）。
全48ケースで二次chartの最大／最終state誤差が線形chartの`<=.5`を要求する。
full stateとchart再構成の全iterateがfinite・population positiveであることを確認し、
初期値からの全4保存量のsite平均driftを`<=5e-13`とする。global driftも別に記録する。
この有限sampleの許容誤差を、浮動小数点mapの厳密保存やball全体の正値性へ一般化しない。

## 判定・保存・次の問い

入力seal、全coverage、finiteな証拠をvalidityとし、構造、独立Hessian、残差次数、
負の対照、48操作、trajectory／positivity／保存を別hypothesis gateとして保存する。
validity失敗はinconclusive、計算が有効でhypothesis失敗ならrejected、全通過ならaccepted。
各gateの成否を隠すために方向・振幅・保存量定義を事後変更しない。

全係数はNPZに保存し、manifestでfile SHAと各arrayの形・dtype・byte hashを参照する。
独立にchartを再構築して主要array hashを一致検証し、保存trajectory監査と区別する。
manifest: `research/artifacts/q012d_d3q27_quadratic_chart.json`。
coefficient archive: `research/artifacts/q012d_d3q27_quadratic_chart.npz`。
helper: `research/d3q27_chart.py`、runner: `research/q012d_d3q27_quadratic_chart.py`。

通過後は有限次jetと実用振幅／高次・存在認証の差を評価し、自然Fourier sparse表現を
必須baselineとして3D TT費用評価へ進む。失敗時は原因を特定して別gateを登録する。
