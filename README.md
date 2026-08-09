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
Q010ではこの停止判断を独立holdout cost campaignで再検証した。TTに有利にdense-oracle生成費用を除外しても、
最速TTのonline中央値はsparseの`4.9709`倍で、全8候補の最良offline／online timeがsparseの最悪値を
strictに上回った。従って固定8 TT-SVD候補にはnatural sparse-fiberに対する有限break-evenがない。
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
`accepted`とした。Q007lではQ007bの2,600 cubic tripleを同じ証明鎖へ接続し、zero-wave 108、internal
graph-gauge 1,044、external 1,448の全system（26,532 complex unknown）を140桁外向き有理区間で認証した。
2,600/2,600でstrict Krawczyk inclusionが通り、maximum utilization／interval contraction／
registered-center correction upperは
`2.2077918755524963e-5 / 1.4873927720660498e-11 / 2.2540660753247895e-8`だった。
zero-wave productの1からのminimum separation lowerは`0.031245322922837878`で、108 fixed-leaf解と
1,044 graph-gauge inclusionも構造的に確認した。従って
`registered Q007b cubic coefficients identify the theorem-manifold graph-gauge cubic jet`として
`accepted`とした。Q007mではQ007c1の17,550 quartic quartetを同じ証明鎖へ接続し、zero-wave 846、
internal graph-gauge 4,536、external 12,168の全system（171,558 complex unknown）を140桁外向き
有理区間で認証した。17,550/17,550でstrict Krawczyk inclusionが通り、maximum utilization／interval
contraction／registered-center correction upperは
`9.230907576183161e-5 / 5.4768769188623044e-11 / 9.431388896713633e-5`だった。zero-wave productの
1からのminimum separation lowerは`0.031245212410182764`で、846 fixed-leaf解と4,536 graph-gauge
inclusionも構造的に確認した。従って
`registered Q007c1 quartic coefficients identify the theorem-manifold graph-gauge quartic jet`として
`accepted`とした。これでlinear coordinateからquartic jetまでの同定は済んだが、Q007c1の有限振幅
directional-shadowing棄却は変更しない。Q007nではFourier-population Wiener \(\ell^1\) norm、
D2Q9非線形majorant、全次数homological inverseの有理上界を固定し、quartic jetを中心とするBanach収縮を
全119候補で監査した。最大pass modal radiusは`1e-75`、含まれるreal Euclidean ballの半径下限は
`3.470110468942836e-75`、収縮上界は`0.449393612526706`である。従って固定17²・固定保存量葉上の
explicit local existence radiusを`accepted`とした。ただしこの極小値は
\(C_L=1.5620130640618827\times10^{71}\)というadjugate inverse boundの粗さに支配され、実用半径、
finite-ball normal attraction、grid-uniform性を示さない。Q007oではQ007nのgap、majorant、119候補を
固定したまま、selected projectorのexact external complementでinternal inverseを再評価した。旧119レコードは
完全一致し、total inverse upperは`2.746444556852928e13`、最大pass modal radiusは`1e-18`へ改善した。
Q007acではnonselected-output 630 discに対する位相付きgap \(10^{-7}\)を監査したが、登録した
対称nominal discがQ007nの\(\sigma\)を`1.6653345369377348e-16`超え、さらに4個の位相比較がfailしたため
`inconclusive`で停止した。診断上の半径`1e-16`は定理主張へ採用していない。
Q007adではこの失敗を固定したfollow-upとしてoriginal asymmetric discsとgap
\(2.1\times10^{-8}\)を再登録し、287,929比較を全通過した。external inverseがQ007o internal
inverseを下回ったため、固定17²・固定葉のanalytic existence radiusを`1e-16`へ改善した。
Q007aeでは同じgapをselected-outputの12 point centersへ適用し、internal inverseを
`1.6818752065691547e9`へ下げた。totalは再びQ007ad external inverseに支配され、
10進候補上のanalytic radiusは`1e-16`のままである。
Q007afではQ007n scalar majorantから`1e-15` candidateに許されるinverseを
`173791195571 pass / 173791195572 fail`とexactに挟んだ。必要external gapは
`2.546402442702229e-8`より大きくなければならないが、Q007adの封印witness一対が許す
sqrt-upper gapは`2.4028364427409988e-8`に留まる。従って同じoriginal-disc
certificate familyでは次の10進radiusへ届かないというnegative obstructionを`accepted`とした。
これは真のanalytic radiusの上限ではなく、別norm・wave-sum・blockwise certificateを排除しない。
Q007agではQ007aeの`1e-16` chart radiusと対応するcorrection boundだけをQ007p／Q007s
majorantへ伝播し、固定9×99格子上で
\(r=9\times10^{-17}\)、\(\zeta=5\times10^{-11}\)を認証した。これはQ007s比でbase 100倍、
normal 10倍である。ただしQ007t／Q007uのexact positivityとQ007v--Q007abの
binary64／MPFR／repair／shadowing certificateは旧Q007s tubeに封印されたままである。
Q007ahでは同じ新tubeのWiener upperをexactに再利用し、population lower
`0.027777777633364167`とdensity lower`0.9999999998555864`を得た。従ってfull-mapの
入力／出力時刻では全iterateのstrict positivityを認証したが、内部stageと有限精度帰納はまだ拡張しない。
Q007aiではexact equilibrium／collision／streaming／filterへ拡張し、最悪stage lower
`0.027777777320468006`を認証した。これでexact stagewise positivityは新tubeへ移ったが、
Q007ajではcurrent binary64演算も一段だけ囲い、最悪stage lower
`0.02777777714596806`を認証した。一方、roundoff re-entry upperはbase／normal marginの
`35399902.97837664 / 38.16743540245316`倍で、all-iterate binary64帰納は`not_certified`である。
Q007akではこのfailureをexactに4因子へ分解し、ideal-binary最小十分precisionを
base／normal／joint=`79 / 59 / 79` bitsと認証した。Q007alでは既存MPFR-85 backendの
全283,296 operation traceをnew tube上へ再適用し、一段stage包囲とbase／normal誤差予算を
認証した。Q007amではQ007yのdistributed dyadic repairを同じnew tubeへ適用し、fixed-leaf
closureと修復込みbase／normal一段予算の共存を認証した。ただしQ007ag exact invarianceとの
自己写像合成、all-iterate induction、initialization、same-initial shadowingはまだ主張しない。
Q007pではQ007o当時の半径`1e-18`を固定し、全289 Fourier blockをexternal coordinate normで
厳密に覆った。
登録tube \(\|a\|_1\le10^{-19}\)、\(\|z\|_*\le10^{-20}\)に対し、base forward invariance、
one-step normal contraction、tangentに対するstrict normal dominationを全て認証した。ただしこれは固定17²・
固定保存量葉・固定external-coordinate normの極小tubeだけの結果であり、Euclidean contraction、
より大きいtube、global basin、grid-uniform性は示さない。Q007qでは同じtube-state Wiener upper
\(x_*=3.075728140408179\times10^{-19}\)をexactに再利用し、
\(p_*=1/36-x_*>0\)、\(d_*=1-x_*>0\)を認証した。従って登録tube内の全9 populationとdensityは
full one-step mapの入力／出力時刻で全iterateにわたりstrict positiveである。Q007rではexact
equilibrium evaluation、BGK collision、periodic streaming、five-point filterの各出力へ範囲を拡張し、
全stageでstrict positivityを認証した。ただしIEEE-754の各中間演算に対するroundoff enclosure、
entropy、maximum principleは示さない。Q007sではQ007pと同じmajorantを9×99のexact rational候補へ
適用し、\(r=9\times10^{-19}\)、\(\zeta=5\times10^{-12}\)のregistered tubeを認証した。ただし
Q007s単独ではQ007q／Q007rのpositivityを新tubeへ拡張しない。Q007tでfull-map入力／出力時刻の
population／density positivityを別途認証し、Q007uで同じ拡大tubeのexact equilibrium／collision／
streaming／filter各段階にもstrict positivityを拡張した。Q007vでは現行binary64実装のone-step
stage positivityも認証したが、roundoff error upperはQ007sのstrict re-entry marginに収まらず、
全iterateへのroundoff-robust帰納は`not_certified`である。Q007wでは同じenclosureを
ideal binary \(p=53,\ldots,128\)へ拡張し、sufficient thresholdを\(p_*=85\) bitsと決めた。
Q007xでは`gmpy2 2.3.1`／`MPFR 4.2.2`の
85-bit backendがQ007wの全登録演算と一段boundを再現することを認証した。一方、componentwise
input encoding、非一様collision、filterがglobal保存量をexactには保たないため、固定保存量葉上の
all-iterate帰納は`not_certified`のままである。Q007yでは対角4 populationの\(2^{-90}\)格子を使う
分散保存補正を構成し、4 probeのencoding／post-filter保存量をexactに回復した。補正は登録tube全体で
well-definedでnormal marginも通るが、粗いrepair-aware Wiener boundはbase marginを2.326倍使用するため、
all-iterate帰納はなお`not_certified`である。Q007zではselected baseが軸・対角の8非零波数だけから
成ることを使い、balanced repairの一様quotientをexactに除いた。repairのbase寄与上界は
\(1.9216710236250915\times10^{-26}\)、総base利用率は`0.8213071928437413`となり、
normal側とともにstrictに通過した。従って、登録tube内のrepair済みMPFR-85状態から開始する条件下で、
fixed leaf、tube re-entry、stage positivityを全iterateへ帰納できる。Q007aaではこの条件付き初期値を
exact state側へ接続し、\(r_0=8.9998\times10^{-19}\)、
\(\zeta_0=4.999999999\times10^{-12}\)のcoordinate interiorを事前登録した。encoding、repair、
graph \(W(a)\) のbase移動を含む増分は両inward marginの`0.56524 / 0.59604`だけを使用し、
repair直後のQ007s tube membershipからQ007zの全iterate帰納へ接続できる。
Q007abではさらに、平衡点で固定したselected／external eigencoordinate直和normでexact mapの
tube-wide Lipschitz upperを\(0.9920954948836456<1\)と認証した。Q007aaの初期誤差とQ007zの
一段local defectを幾何級数で合成し、同じexact initial stateから始めるrepaired MPFR-85軌道との
sampling-time Wiener誤差を全非負iterateで\(8.529800645544777\times10^{-18}\)以下に抑えた。
Q007an--Q007apではこの有限精度証明鎖をQ007agの拡大tubeへ移した。Q007anでrepaired mapの
全iterate tube帰納、Q007aoでstrict inner exact-state setからの初期化を認証し、Q007apで
fixed-coordinate Lipschitz upper \(0.9920957426381974<1\)と初期／一段欠陥を合成した。
その結果、同じexact initial stateからのsampling-time Wiener誤差を全非負iterateで
\(8.803831096064757\times10^{-18}\)以下に抑え、propagated-tube finite-precision chainを閉じた。
Q011aでは次に、一様非零平均body forceをperiodic filtered BGKへ加える前提を監査した。各stepの
exact global momentum incrementが\(867\,2^{-40}>0\)で、boundary／drag／repair sinkがないため、
このforced mapにはfixed pointが存在しない。従って非零平均periodic Newton solveは開始せず、
zero-mean forcingとwall-bounded flowを別問題として扱う。
Q011bでは零平均cosine force \(F_x(y)=3\,2^{-24}\cos(2\pi y/17)\)へ切り替え、固定mass／momentum葉上の
x-independent fixed pointを二つのNewton startから同一解として数値的に解いた。全17個の
\(k_x\) block、合計2598 fixed-leaf eigenvalueを監査し、spectral radius
`0.9920954673551019`、\(\min\sigma(I-J)=0.00649328212134047\)でstable prequalificationを通過した。
Q011cではQ006h first-shell 24-mode subspaceを9点のforce-amplitude pathでordered-Schur clusterとして
追跡した。全cluster分離・projector・Sylvester・normal-dominance診断は登録閾値を通ったが、Q011b
終点のcondition-number再現差が\(7.05\times10^{-12}>10^{-12}\)となり、共役な
\(k_x=1,16\) witnessも交換したため、事前登録どおり`inconclusive`とした。forced slow clusterの
科学的選択や不変多様体はまだ主張しない。Q011c1では全17 blockのJacobian差からFrobenius--Weyl
摂動区間を作り、交換が同じ共役orbit`{1,16}`内に限られ、全resolvent metric変化が区間内である
ことを確認した。これは失敗原因の局在化であり、Q011cの判定は変更していない。Q011c2では元の9点の
中間に8個の未使用amplitudeを置き、全8点でSylvester familyと2598 spectrumを評価する再発行gateを
通過したため、この有限数値範囲ではforced candidate spectral clusterをselectedとする。Q011dでは
このselected clusterの全300 quadratic external blockと5 sector actionを通し、数値的external
nonresonance／solvabilityをprequalifiedとした。Q011eでは案Aの固定保存量葉上で解析Hessianと
dense \(W_2/R_2\)を構築し、homological／graph-gauge／保存則／実座標化の検査を通した。一方、登録した
小振幅窓ではquadratic residualが`1e-13`以上となる点が各方向1点しかなく、slope-eligible方向が
`0 / 32`だったため、Q011e自体は`rejected`である。二次チャートの構築成功と三次残差次数の未確認を
分け、閾値を緩めず独立seed・拡大振幅窓のQ011e1を別gateとして実行した。Q011e1では32/32方向が
eligibleとなり、linear／quadraticのprimary・上位4点secondary slopeが全て登録区間を通ったため
`accepted`とした。これはQ011eの再採点ではなく、有限独立窓で残差次数を確認した新しい結果である。
Q011fでは別seedの160初期値を64 step追跡した。誤差次数、quadratic改善、64-step相対誤差、positivity、
保存則は通ったが、direction 4のhorizon 1・2でquadratic errorのfit点が3個しかなく、登録要求
`224 / 224`に対して`222 / 224`だったため`rejected`とした。Q011f1では同じ方向・閾値を固定し、
未使用振幅`4.8e-4`だけを追加した独立再発行を行った。全224 fitがeligibleとなり、linear／quadratic
slope、全checkpoint改善、64-step相対誤差、positivity、保存則を通過したため`accepted`とした。
Q011f自体の棄却は変更していない。Q011gではこのforced (W_2/R_2)をnatural Fourier-sparseと
6個のuncapped TT-SVD bundleで比較した。3個のoutput-last TTは現在環境のonline作用時間で勝ったが、
最小TTでもsparseの約5倍の格納量だったためjoint winnerは0で、TT優位性を`rejected`とした。
Q011hでは未使用24方向×3振幅のnatural sparse経路とdense経路を64 reduced stepまで
独立更新し、9,360 common-input actionと4,680 state、576 checkpoint defectを全て登録閾値内で
一致させた。従ってこの固定係数のnatural Fourier-sparse chart同値性を`accepted`とした。
Q011iではQ011b waveformのbinary64値をexact dyadicとして再監査し、その和が
\(-71/2^{78}\ne0\)であるためraw exact-real mapにはglobal momentum obstructionが残ることを確認した。
reflection pairのmidpoint丸めと登録ULP search、exact-moment source allocationによりlocal／global
保存ledgerが厳密に0となる別のrepaired mapを一意に構成した。validity `6 / 6`、hypothesis `4 / 4`を
通過し、repaired fixed pointと全17 spectrum blockはQ011b数値baselineとbitwise同一だったため
`accepted`とした。Q011bの数値結果は変更せず、Q011e--Q011hのraw-map coefficientも修復mapへ移さない。
Q011jではsite 0の3 populationをexactに消去する150次元affine fixed-leaf chartを構成し、
exact rational nonlinear map／Jacobian enclosureと256／384-bit外向きMPFRを用いたKrawczyk証明を行った。
登録10半径のうち5候補が通り、最大の自由座標半径`1e-8`で収縮上限`0.199756943`、包含利用率
`0.199757034`を得た。従ってrepaired mapのx-independent fixed pointの存在と同box内局所一意性を
`accepted`とした。Q011kでは収縮証明からexact root半径を`1.13014e-15`へ絞り、17 Fourier blockの
256／384-bit Bauer--Fike enclosureを構成した。全2598 eigenvalue discが`0.992108506`以下、
selected／external countが`24 / 2574`、normal modulus gapが`0.002047690`、300 quadratic productの
external distance lowerが`1.79373e-4`となり`accepted`とした。Q011lではQ011k eigencoordinateの
selected invariant graphをexactに囲み、非対角symmetric-product couplingを含む5 sectorのquadratic
homological inverseを認証した。最大coordinate inverse boundは`5178.30`、ambient-output lift後は
`3.326e6`であり`accepted`とした。raw Q011b exact map、repaired quadratic coefficient、forced SSMは
未認証である。

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

### Q010 sealed TT-SVD representation cost and break-even

Q008a／Q008cの固定8候補をfresh TT-SVDで再構築し、seed `20260901`の独立16方向でnatural
sparse-fiber、ordered-dense coefficient oracle、8 TTのoffline preparationとlocal quartic actionを
測定した。full model／coefficient生成とordered-dense materializationは全methodの共通入力として除外し、
TT側の費用を意図的に過小評価した。

- classification:
  `sealed TT-SVD path is cost-dominated by natural quartic sparse-fiber`
- validity / hypothesis gates: `6 / 6` passed、`5 / 5` passed
- holdout direction hash／prior exact duplicate count:
  `ed625949a32c1cbf6cb7f00e0a4cca5e05675481159b29c61db59c769890609b / 0`
- sparse offline min／median／max:
  `20.9392 / 20.9547 / 21.6592 ms`
- fastest TT offline min／median／max（`flat-q-last`）:
  `1.3654306 / 1.3732766 / 1.3768735 s`
- sparse online min／median／max:
  `0.5805375 / 0.58298125 / 0.61728125 ms per sample`
- fastest TT online min／median／max（`flat-q-last`）:
  `2.85776875 / 2.89795 / 3.0604 ms per sample`
- fastest TT median slowdown／best-case envelope slowdown:
  `4.9709145877333105 / 4.629605629524629`
- sparse stored real scalars／raw bytes／NPZ bytes:
  `315900 / 2614950 / 2615734`
- best TT core stored real scalars／raw bytes／NPZ bytes:
  `3550626 / 28405096 / 28406852`
- best TT/sparse ratios:
  `11.2397151 / 10.8625771 / 10.8599926`
- maximum reconstruction／action／block-checksum relative error:
  `1.4915466e-13 / 6.6372433e-13 / 4.6567547e-14`
- input／result digest:
  `566d3ce0569736c140dae7c4f19d36223957e5ad2b25abc4b9d6a012558d0841` /
  `79545f0cbf14a53fef52d46bc44cbb8586efb95e1b6645d7c8cc00b45ceed6dc`
- runner SHA-256:
  `c6e99082a3418d604f7d09687685cf5e6ab9efe341ea36153123bb8ad4b26b4e`
- artifact newline-normalized SHA-256:
  `2885a029ecfe2c17aebe3b05b305caebd927d78476971e4ab186455d0ee30b7f`

全8候補で\(B_m^->B_s^+\)かつ\(t_m^->t_s^+\)となり、登録campaignの全\(N\ge0\)で
best-case TT cost lineがworst-case sparse cost lineを上回った。flat系TTはordered-dense coefficient
oracleには約120--144 actionでmedian time break-evenを持つが、これはfull dense LBMではなく、必須
sparse baselineにも格納量にも勝たない。従って固定Q007c1係数のTT-SVD／Q009経路を閉じる。
この有限CPU campaignからTT一般、TT-cross、別tensorization／grid、GPU、full rolloutの不可能性は
主張しない。

### Q007n quartic-centered explicit local radius

Q007h1／Q007iの全次数external separationとQ007j--Q007mのexact jet boxを固定入力とし、24 complex
modal coordinateの\(\ell^1\) ballでparameterization equationをBanach収縮へ書き直した。full stateには
Fourier-population Wiener \(\ell^1\) normを使い、D2Q9非線形部を
\((21/2)x^2/(1-x)\)で抑えた。非正規なselected-output blockには個別external eigenvectorを仮定せず、
12次bordered行列のdeterminant／adjugate boundを使った。

- classification: `registered quartic-centered contraction gives an explicit fixed-leaf local radius`
- validity / hypothesis gates: `5 / 5`, `4 / 4` passed
- registered modal-radius candidates / passing candidates: `119 / 46`
- largest passing modal \(\ell^1\) radius: `1e-75`
- previous larger candidate: `1e-74`（fail）
- contained real-coordinate Euclidean radius lower: `3.470110468942836e-75`
- finite-degree absolute spectral-gap lower: `1.611328085325626e-10`
- maximum \(S_\infty\)／bordered-entry upper: `6.025984057925574 / 1.6509200830138158`
- pair homological inverse upper \(C_L\): `1.5620130640618827e71`
- contraction upper at `1e-75 / 1e-74`: `0.449393612526706 / 4.49393612526706`
- correction radius \(\tau=2Y\) at `1e-75`: `1.620396579477627e-295`

入力の有理boundを80桁10進格子へ必ず外向きに丸めた後、全候補の符号とpass/failを`Fraction`で判定した。
選択候補と直前のfail候補については完全なbase-16有理数もartifactへ保存している。従って固定17²・固定保存量葉で
explicit analytic \(W,R\)の存在を初めて数値半径付きで認証した。ただし`1e-75`は最適半径ではなく、
対角化不要だが極端に粗い\(\delta^{-6}\) adjugate boundの結果である。Q007c1の有限振幅性能棄却を変更せず、
forward invariance、positivity、finite-ball normal attraction、grid-uniform性はまだ認証しない。

### Q007o exact external-complement resolvent refinement

Q007nの12次bordered adjugate全逆行列を、graph-gauge右辺に必要な6次元external complementのinverseへ
置き換えた。Q007jのexact selected \(V,L\)から\(Q=I-VL^*\)を作り、axial／diagonalの2代表で
\(U=QE\)の6列がexternal complementを張ることを有理interval Neumann boundで認証した。
external eigenvalueの個別一意性は使わず、C4で全8 selected waveへ輸送した。

- classification:
  `exact external-complement resolvent strictly sharpens the registered explicit radius`
- validity / hypothesis gates: `6 / 6`, `4 / 4` passed
- Q007n old 119 candidate records reproduced exactly: `true`
- maximum coordinate inverse defect:
  `3.724809047388777e-13`（登録上限`1e-8`）
- maximum external representation perturbation \(\gamma\):
  `1.1339793519314153e-14`
- working internal pair inverse upper:
  `2.1920952274236575e11`
- unchanged external-output inverse upper／new total inverse upper:
  `2.746444556852928e13 / 2.746444556852928e13`
- registered inverse-upper reduction factor:
  `5.687400680142434e57`
- registered／passing radius count: `119 / 103`
- largest passing modal \(\ell^1\) radius／previous fail:
  `1e-18 / 1e-17`
- selected／previous contraction upper:
  `0.07901564138003579 / 0.7901564138003603`
- correction radius \(\tau\)／radii margin at `1e-18`:
  `2.8490986842816327e-68 / 1.199425982247287e-68`
- contained real-coordinate Euclidean radius lower:
  `3.470110468942836e-18`

従ってQ007nのexistence結論を保ったまま、同じ固定17²・固定保存量葉で登録半径を57桁改善した。ただし
`1e-18`も最適半径ではなく、位相を捨てた全次数gapとQ007nのexternal-output Bauer--Fike／Neumann upperを
維持した保守値である。Q007c1の有限振幅性能棄却、forward invariance、positivity、
finite-ball normal attraction、grid-uniform性、continuum limitは変更・認証しない。

### Q007ac phase-aware external-output resolvent refinement

Q007oのexternal-output upperを支配するmodulus-only gapの代わりに、Q007h1のcomplex eigenvalue
discと全selected productを比較した。Q007iと同じ291万9730 modulus aggregateを先にscreenし、
log-gapが`1e-6`未満のaggregateだけをacoustic signごとに完全展開した。Fourier wave-sum restrictionは
使わず、全productを70 nonselected C4 representativeの630 target discと比較した。

- classification: `registered Q007ac phase-aware audit invalid`
- validity／hypothesis gates: `5 / 6`, `4 / 5` passed
- target phase gap: `1e-7`
- safe／dangerous aggregate: `2,918,904 / 826`
- dangerous expanded product／exact disc comparison: `108,273 / 287,929`
- selected nominal-disc containment: pass
- nominal disc within Q007n working \(\sigma\): fail
- required product-factor inflation over Q007n \(\sigma\):
  `1.6653345369377348e-16`
- failed phase comparison: `4`
- minimum-distance witness:
  degree `71`、counts `(24,38,2,7)`、acoustic split `(12,12,1,1)`、
  external `wave=(-7,-7); eigenvalue_index=6`
- witness certified complex distance lower: `2.4028360293239852e-8`
- phase-comparison digest:
  `5039563c60ab57b85b683b324506049535372847b1a5adef3362da2b16a954ab`

従って事前登録した停止規則どおり`inconclusive`とし、external inverseもexistence radiusも更新しない。
診断としてgapが通ったと仮定すれば、external inverseは`4.425423249246816e10`、total inverseは
Q007o internal upper `2.1920952274236575e11`に支配され、改善率`125.28856057411295`、
最大pass候補`1e-16`となる。しかしvalidityとphase hypothesisが落ちたため、これらはcounterfactualであり
認証値ではない。この停止を受けたQ007adでselected discを再中心化せず、critical external gapから
新しい閾値を事前登録した。Q007ac自体の`1e-7`結果はinvalidのままであり、Q007p--Q007abの
tube／MPFR結論も変更しない。

### Q007ad original-asymmetric-disc critical phase certificate

Q007acのinvalid／`inconclusive`結果を封印入力として保持し、Q007h1の6 selected discsを
共役化・実軸化・再中心化せずに直接使用した。Q007n \(\beta_*\)とQ007o internal inverseから

\[
\delta_{\rm crit}
=81\beta_*/C_{\rm int}^{\rm Q007o}
=2.0188097642308912\times10^{-8}
\]

を先に導き、targetを \(\delta_{\rm ad}=2.1\times10^{-8}\)へ固定した。このgateはQ007acの
失敗witnessを見た後のfollow-up certificateであり、独立な探索仮説ではない。

- classification:
  `original asymmetric discs certify the critical external-output phase gap`
- validity／hypothesis gates: `6 / 6`、`5 / 5` passed
- original selected disc／target disc: `6 / 630`
- Q007n \(\sigma\)からのminimum selected-disc slack:
  `7.672593033162951e-81`
- Q007ac screen exact reproduction: pass
- aggregate／dangerous aggregate: `2,919,730 / 826`
- dangerous expanded product／exact comparison:
  `108,273 / 287,929`
- failed phase comparison: `0`
- minimum witness:
  degree `71`、counts `(24,38,2,7)`、acoustic split `(12,12,1,1)`、
  external `wave=(-7,-7);eigenvalue_index=6`
- certified complex distance lower: `2.4028364427409988e-8`
- phase-comparison digest:
  `086516b273f30d7c94c276399c16f8a6433bd90e3dc03fb740d2ab45754e4a37`

80桁working external inverseは`2.107344404403246e11`で、Q007o internal upper
`2.1920952274236575e11`より小さい。従ってnew totalはinternal-limitedとなり、Q007o totalからの
改善率は`125.28856057411295`、固定119候補での最大passは`1e-16`、直前の
`1e-15`はfailした。これにより固定17²・固定保存量葉・固定modal／Wiener normに対する
Q007i manifoldのexplicit analytic existence radiusを`1e-16`として認証する。

ただし \(2.1\times10^{-8}\) の最適性、Fourier wave-sumによるsharp化、Q007o internal／zero-wave
inverseの改善、grid-uniform性、finite-ball normal attraction、global basinは示さない。特に
Q007p--Q007abのtube、positivity、MPFR、forward-shadowing結論は再走査しておらず、従来の
`1e-18`設定を変更しない。analytic radiusと有限tube radiusを混同しない。

### Q007ae phase-aware selected-output internal resolvent

Q007o internal upperを支配したglobal modulus gapの元witnessはdegree `51`、
counts `(1,19,27,4)`、nonselected output
`wave=(-2,-2);eigenvalue_index=(8,7)`だった。これをselected-output internal blockへ
一様適用する保守性を外すため、Q007o axial／diagonal representativeのexternal coordinate
point centers 6個ずつ、計12個だけを位相付きで比較した。target gapは探索せず、Q007adと同じ
\(2.1\times10^{-8}\)を固定した。

- classification:
  `phase-aware selected-output centers remove the internal resolvent bottleneck`
- validity／hypothesis gates: `6 / 6`、`5 / 5` passed
- selected-output point center: `12`、target radius `0`
- aggregate／dangerous aggregate: `2,919,730 / 81`
- dangerous expanded product／comparison: `15,773 / 19,870`
- failed comparison: `0`
- minimum witness:
  degree `63`、counts `(1,39,17,6)`、acoustic split `(0,1,3,14)`、
  target `selected_output_wave=1,0;external_index=6`
- certified complex distance lower:
  `5.228929928706603e-4`
- maximum critical gap／target ratio:
  `5.691119055000859e-9 / 3.6899597068782164`
- axial／diagonal working internal upper:
  `1.0192745414727758e9 / 1.6818752065691547e9`
- phase／selected-center certificate digest:
  `4aea091076179e7ef8eb14c9c4828b41d6af3ef25665e5b2dbbf562acf692b3b` /
  `3cc524ebb82c3e375bf35d456f96be11fa5d124728873046ed59a7032a2058d7`

新internal upperはzero-wave upper`6.2060607588672085e9`より小さい。new totalはQ007ad
external upper`2.107344404403246e11`に一致し、直前totalからの改善率は
`1.0402168828423712`だった。固定radius scanでは`1e-16`が最大pass、
`1e-15`がfailのままであり、より大きい10進半径は認証していない。

targetはQ007o identity \(A_kU_k=U_kD_k+Q_kR_k\)の\(D_k\) point centerであるため、
Q007h1 Bauer--Fike radiusを加えず、target residualは既存\(\gamma_k\)としてinternal inverseの
分母から差し引いた。Fourier wave-sumを使わない全product \(\times\) 12 centersのsuperset
certificateである。次のanalytic bottleneckはQ007ad nonselected-output external inverseである。
Q007p--Q007abのtube定数は変更しない。

### Q007af sealed external phase-disc radius-step obstruction

Q007ae後に残ったexternal inverseを同じQ007ad original-disc family内でsharp化する価値があるかを、
新しいphase gapの探索前に判定した。Q007nの`1e-15` candidateへpair inverseだけを入れ、
exact integer bisectionを \([1,10^{13}]\)から44回行った。

- classification:
  `sealed external phase-disc family cannot certify the 1e-15 radius step`
- validity／hypothesis gates: `6 / 6`、`5 / 5` passed
- maximum passing／minimum failing integer inverse:
  `173791195571 / 173791195572`
- passing／failing contraction \(Z\):
  `0.4999999999994811 / 0.5000000000023581`
- passing／failing radii margin:
  `9.35528407264837e-68 / -4.2513570828920896e-67`
- necessary external gap lower:
  `2.546402442702229e-8`
- sealed witness allowable gap upper:
  `2.4028364427409988e-8`
- witness／required ratio、absolute shortfall:
  `0.9436200666659436 / 1.4356599996123017e-9`
- optimistic external inverse floor／failing-endpoint ratio:
  `1.841749679890231e11 / 1.059748552755201`
- integer-bisection digest:
  `24b0e993f676082579158cfeddfe74009161d72412bf228f715baa396246c31b`

positive domainではQ007n derivative majorant \(D(C)\)が非減少で
\(Z(C)=CD(C)\)がstrictに増加し、domainを外れればbuffer gateがfailする。従ってfailing端点以上の
inverseは全てfailする。external formula \(C_{\rm ext}^{\rm raw}=81\beta_*/\delta\)から、passには
\(\delta>81\beta_*/173791195572\)が必要である。

反証にはQ007adのdegree `71`、counts `(24,38,2,7)`、
external `wave=(-7,-7);eigenvalue_index=6`を固定した。center distanceの平方を保存centerから
exact再構成し、100桁`isqrt` enclosureの上端からproduct uncertaintyとexternal radiusを
差し引いた。必要gapでのexact squared marginは`-7.109332998428586e-17`で、thresholdの
外向き丸めを行わなくてもfailする。従って全287,929 comparisonを別gapで再探索する前に、
同じcertificate familyの停止条件が成立した。

この結論はQ007ad gapが真に最適、または真のanalytic radiusが`1e-15`未満だという主張ではない。
Q007n scalar majorant、Q007ad original asymmetric discs、Q007ad norm formulaを同時に固定した
場合だけのobstructionである。Q007aeの`1e-16 pass / 1e-15 fail`と
Q007p--Q007abのtube／MPFR constantsは変更しない。次は同じgapのmicro-sharpeningではなく、
認証済み`1e-16` chart domainを使う下流tube再監査を別gateにする。

### Q007ag Q007ae analytic radiusのfinite-tube伝播

Q007aeで認証したanalytic radius \(\rho=10^{-16}\)と対応する
\(\tau=2.186110822784426\times10^{-60}\)だけをQ007p／Q007s majorantへ代入し、
Q007sのbase gridをexactに100倍、normal gridを不変にした9×99候補を全評価した。

- classification:
  `Q007ae analytic radius enlarges the registered external-coordinate tube`
- validity／hypothesis gates: `6 / 6`、`5 / 5` passed
- Q007s old candidates／passing candidates: `891 / 676` exact reproduction
- Q007ae radius records: `119 / 119` exact reproduction
- new candidates／passing candidates: `891 / 757`
- selected base／normal radius:
  `9e-17 / 5e-11`
- Q007s selectedからのimprovement: `100 / 10`
- selected state Wiener upper: `1.4441361143956586e-10`
- base image／strict forward margin:
  `8.995021185299983e-17 / 4.978814700017615e-20`
- normal contraction／tangent conorm／domination ratio:
  `0.9817100978829438 / 0.9837709569923392 / 0.9979051433722989`
- first larger normal `6e-11`のbase forward margin:
  `-2.4132428529856413e-19`（このgateだけfail）
- input／candidate／result digest:
  `262cbeccacf858bd798de06f363635f15c78ff3d361b44bdd5850aeb90679613` /
  `a7a6a8f605339b0e8ffd16a5d3190967cb7329771d322f8edc0a53bc4b45e408` /
  `6f52c6f1cfa618ca881439504f1bd5b46e45eb245670f1a2c6341669aa024f43`
- runner／artifact SHA-256:
  `bafd9a56d2d2ceb94acb709609bd710c9fff0f6c0bf543202fa411b9456fb6e0` /
  `5783df74abb4b6ec7d658fd7e3dd272cf100cd134783c31863d643fcd17d4200`

選択点は全6 candidate gateをstrictに通り、selected base sliceのより大きいnormal候補は全て
failした。従って固定scaled grid上では両tube半径が拡大した。ただしbase grid上端を選んだだけなので、
continuous optimumやmaximum tubeを意味しない。Euclidean／grid-uniform attraction、global basin、
continuum limitも示さない。Q007t／Q007uのpopulation／stagewise positivityと
Q007v--Q007abの有限精度certificateは旧tubeに封印され、新tubeへは自動的に移らない。

### Q007ah Q007ag tubeのfull-map population positivity

Q007ag selected tubeのexact Wiener state upper
\(x_{\rm ag}=1.4441361143956586\times10^{-10}\)を再利用した。Q007agをfresh replayし、旧Q007t
population oracleもexact replayした上で、D2Q9 weight tableと289-wave Fourier triangle boundを
独立に再構成した。

- classification:
  `registered Q007ag propagated tube lies in the strictly positive population cone at every full-map iterate`
- validity／hypothesis gates: `6 / 6`、`3 / 3` passed
- selected base／normal radius: `9e-17 / 5e-11`
- tube population deviation upper: `1.4441361143956586e-10`
- population lower／upper:
  `0.027777777633364167 / 0.44444444458885807`
- density lower: `0.9999999998555864`
- D2Q9 weight multiplicities／minimum: `1 / 4 / 4`、`1/36`
- Fourier wave count: `289`
- input／result digest:
  `6d7bd69b5c90ff7dbabd5193a4536809f4b79eef36a41fb288ab7caec44321b4` /
  `caea5280667e909f17922260ef0d78998b6a8b374cd048b4b3e526185f040921`
- runner／artifact SHA-256:
  `f29a974f0219af1767140e977775aa95dcf22b41a36de7a97bb553d540968d27` /
  `cab5ecc090b794a21a21fded8e5c503eca40be2bbc6502767c29844ba8209fa9`

Q007ag forward invarianceにより、同じlower boundをfull one-step mapの全入力／出力時刻へ帰納できる。
一方、equilibrium evaluation、BGK collision、streaming、filterの内部stageはこのgateの対象外である。
entropy、maximum principle、IEEE-754 roundoff、Q007v--Q007ab有限精度帰納も示さない。

### Q007ai Q007ag tubeのexact stagewise positivity

Q007ahのexact state upperをQ007uと同じD2Q9 stage majorantへ代入した。Q007ah／Q007uをfresh replayし、
現行D2Q9／checkerboard-filter sourceをSHA固定して、linear operator、nonlinear remainder、17² periodic
streaming、five-point convex filterを再構成した。

- classification:
  `registered Q007ag propagated tube is population-positive at every exact BGK, streaming, and filter stage`
- validity／hypothesis gates: `6 / 6`、`5 / 5` passed
- equilibrium／collision induced \(\ell^1\) norm: `13/6 / 19/6`
- equilibrium／collision nonlinear constant: `7 / 21/2`
- equilibrium deviation／population lower:
  `3.1289615826504644e-10 / 0.02777777746488162`
- collision deviation／population lower:
  `4.5730976977760583e-10 / 0.027777777320468006`
- streaming／filter population lower:
  `0.027777777320468006 / 0.027777777320468006`
- streaming bijections／convex filter／wrapped composition: pass
- input／result digest:
  `0dff47e8b0ed6e9b87cb73e6dea20192088495b51283c57b9d58630b7344c6a3` /
  `c101313957c738ccee9fd3d7f1ed36b77c6f3dad4e1130651f5be4d8757ef18a`
- runner／artifact SHA-256:
  `3235b2dc31445e5912f2aaf7fc080e8295035801ade9b27d3f683d34da61173d` /
  `3ce5fa6358eaa6f3a64f93fe773e3fbc1990abfb83886aad1a4ade9c82425804`

Q007ag forward invarianceにより、同じ4 stage lowerをexact mapの全iterateへ再適用できる。ただし
NumPy／IEEE-754の中間演算は囲っておらず、binary64 one-step enclosureとroundoff-robust tube re-entryは
別問題である。entropy、monotonicity、maximum principle、finite-precision all-iterate帰納も示さない。

### Q007aj Q007ag tubeのcurrent binary64 one-step enclosure

Q007ag／Q007ai／Q007vを封印し、Q007vのFraction-based paired interval engine、binary64 model、固定
operation schedule、current D2Q9／filter sourceを新しいstate upperへそのまま適用した。Q007vの旧tube
mixed resultもfresh replayし、one-step stage positivityとbase／normal re-entryを独立に判定した。

- classification:
  `binary64 one-step stages remain positive, but the registered Q007ag tube is not certified roundoff-invariant`
- validity gates: `7 / 7` passed
- hypothesis gates: `5 / 7` passed
  - equilibrium／collision／streaming／filter／one-step positivity: pass
  - base／normal roundoff re-entry: fail / fail
- input state Wiener upper: `1.4441361143956586e-10`
- binary64 equilibrium／collision／streaming／filter population lower:
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

従って、Q007ag component box内のexact real stateをcorrectly rounded binary64へencodeした入力について、
登録current NumPy演算順序のequilibrium／collision／streaming／filterは一段ならstrict positiveである。
しかし固定worst-case error upperは両strict marginを超えるため、この結論を全iterateへ帰納しない。
これは実際のtube escapeや反例ではなく、現行enclosureの再入認証失敗である。Q007akではmargin、analysis
norm、Wiener lifting、local roundoff accumulationを分離してbottleneckを決める。

### Q007ak Q007ag roundoff re-entry obstructionの因子分解

Q007aj／Q007wを封印し、binary64 utilizationを
\(U_X=K_X\,289\,E_{53}/m_X\)へexactに分解した。さらにQ007wと同じideal-binary evaluatorを
53--128 bitの全76整数候補へ適用し、base、normal、jointのfirst-pass boundaryを別々に決めた。

- classification:
  `registered factor audit isolates base re-entry as the dominant Q007ag binary64 obstruction`
- validity／hypothesis gates: `7 / 7`、`7 / 7` passed
- binary64 base／normal utilization: `35399902.97837664 / 38.16743540245316`
- maximum local component-error sum at the strict boundary:
  - base: `1.1403927055836785e-22`
  - normal: `1.0577024814278182e-16`
- maximum analysis factor at the strict boundary:
  - base: `4.26748121347461e-08`
  - normal: `0.7838393109965568`
- maximum wave-lifting factor at the strict boundary:
  - base: `8.163864182806664e-06`
  - normal: `7.5718998919540965`
- unit-wave counterfactual base／normal utilization:
  `122491.01376600914 / 0.13206725052751958`
- minimal sufficient ideal precision base／normal／joint: `79 / 59 / 79` bits
- boundary utilization:
  - base `p=78 / 79`: `1.049142142753718 / 0.5226851687280066`
  - normal `p=58 / 59`: `1.1922608315359098 / 0.5970734654373829`
- input／candidate／result digest:
  `333ce7e6b4537947808a369f1c218c2d930a11df4b826994df0947fa42489d46` /
  `eacc824a8f0fc891971c210883d05f7178e4fe5848ab3b2432dc94adf289e567` /
  `a4d10df4c1d6edd83488115d501af21ad6727dd6321e159e37b2b0e434858644`
- runner／artifact SHA-256:
  `c8bb3f7a84d19d9ab2794d9a1c27334ecd53e62dabce7862343b51ef30cd29b1` /
  `aae6b560125cd29dad5b87bf20e9806ae26a5b1b6ae2ee9c055580042561cf7c`

従って固定enclosureではbase coordinateが支配的である。wave factorを反実仮想的に289から1へ下げてもbaseは
約12.2万倍超過する一方、normalは通る。ideal 79 bitは固定operation model内の十分条件であり、必要条件、
actual trajectory threshold、MPFR-85実装証明ではない。Q007alでは既存MPFR-85 backendをnew tube上の
一段stage／error-budgetだけに対して再監査した。結果は次節に固定し、fixed-leaf closureと
repairは分離したまま残す。

### Q007al propagated-tube concrete MPFR-85 bridge

Q007ak／Q007x artifactとrunnerを封印し、既存`gmpy2 2.3.1`／MPFR `4.2.2`の
85-bit backendを変更せずnew Q007ag component box上へ再適用した。Q007ak stored cycle、
Q007x mixed cycle、fresh 85-bit ideal candidate、4 exact probeのconcrete campaignをそれぞれ再現した。

- classification:
  `registered MPFR-85 backend realizes the Q007ag one-step arithmetic and complement-coordinate error budgets`
- validity／hypothesis gates: `8 / 8`、`5 / 5` passed
- precision／rounding: `85 / RoundToNearest`
- probes／operation traces: `4 / 70,824 per probe / 283,296 total`
- trace mismatch／operation-domain failure: `0 / 0`
- post-filter component-error sum／Wiener error upper:
  `9.365881800643092e-25 / 2.7067398403858536e-22`
- base error／strict margin／utilization:
  `4.08902913525762e-22 / 4.978814700017615e-20 / 0.008212856636827946`
- normal error／strict margin／utilization:
  `8.097790464783468e-21 / 9.144951058528087e-13 / 8.8549303467643e-09`
- maximum concrete stage-bound utilization: `0.15250294771440714`
- minimum observed concrete stage population: `0.027777777777759027`
- conservation: encoding `fail` / collision `fail` / streaming `pass` / filter `fail` / full step `fail`
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

従って固定MPFR-85 implementationはnew tubeの一段算術budgetを実現する。しかしこの結論は
ideal exact-map outputに対する誤差予算とfinite probe stage checkであり、丸め後stateがfixed leafに
属することを示さない。actual tube re-entry、all-iterate invariance、repair、same-initial shadowingは
未認証である。次はQ007amでnew-tube repairを独立に判定する。

### Q007am propagated-tube distributed fixed-leaf repair

Q007al／Q007y artifactとrunnerを封印し、Q007yと同一の\(h=2^{-90}\) diagonal dyadic repairを
Q007ag component boxへ変更せず再適用した。4 exact probeではinput encoding後とpost-filter後の
\((M,P_x,P_y)=(289,0,0)\)をexactに回復し、tube-wideではbinade／integer-lattice／parity条件と
coarse Wiener triangle boundをexact rationalで監査した。

- classification:
  `distributed MPFR-85 repair restores the Q007ag fixed leaf and fits both registered one-step budgets`
- validity／hypothesis gates: `8 / 8`、`7 / 7` passed
- input repair \(\ell^1\) upper／maximum site correction:
  `1.2452407121655381e-23 / 4.362085261510107e-26`
- raw／repair／total post-filter Wiener upper:
  `2.7067398403858536e-22 / 4.959477728036884e-22 / 7.666217568422737e-22`
- repaired／raw Wiener ratio: `2.8322698229209555`
- repair-aware base error／strict margin／utilization:
  `1.1581233824834727e-21 / 4.978814700017615e-20 / 0.02326102601246388`
- repair-aware normal error／strict margin／utilization:
  `2.2935127565743277e-20 / 9.144951058528087e-13 / 2.5079552005207522e-08`
- input／probe／finite-result／result digest:
  `f1a0dfd0b90cf354e9847cb076058fd241ab813a90bdee0bfdbafa9dfee17de5` /
  `a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329` /
  `905b65f13ee01711f3b083a0bd93e44b32d0fc5201007fad77e99de03063ab6d` /
  `2217172b48bf86b987a316c9b8c14db6aaeceb3e50f304fa7fefb021c2fd5bd2`
- runner／artifact newline-normalized SHA-256:
  `a0bdebc150c4c3ad055e1840b98196dee95bf967c417d17097f7a35579f2aa16` /
  `3b1b6f3c839cec572d0279f41c158dfafa09088e5f8ee1c3eab84f5bd279b781`

従ってnew tubeではfixed-leaf repair feasibilityと両一段誤差予算が同時に成立する。finite probeは
実装回帰でありtube sampling proofではなく、coarse boundはcenter cancellation、spatial phase、
Q007z selected-wave boundを使わない。この結果だけではrepaired MPFR-85 mapのtube self-mapや
all-iterate invarianceにならないため、次はQ007anでexact Q007ag invariance、stage positivity、
repair-aware budgetを明示的に合成する。

### Q007an repaired MPFR-85 fixed-leaf tube induction

Q007ag／Q007ai／Q007al／Q007amのartifactとrunnerを封印してfresh replayし、85-bit raw mapと
Q007y row-major repairの合成

\[
\widetilde\Psi_{85}=\mathcal R\circ\widetilde\Phi_{85}
\]

をQ007ag fixed-leaf tubeの自己写像としてexact rationalで監査した。Q007agのstrict interior marginから
Q007amの修復込みcoordinate errorを引いても、base／normalの両方にstrict headroomが残る。

- classification:
  `coarse repair certificate closes the Q007ag repaired MPFR-85 fixed-leaf tube induction`
- validity／hypothesis gates: `7 / 7`、`7 / 7` passed
- exact base／normal strict margin:
  `4.978814700017615e-20 / 9.144951058528087e-13`
- repair-aware base／normal error:
  `1.1581233824834727e-21 / 2.2935127565743277e-20`
- repaired-map base／normal headroom:
  `4.863002361769267e-20 / 9.144950829176811e-13`
- exact／MPFR-85 minimum internal-stage population lower:
  `0.027777777320468006 / 0.027777777145968227`
- repaired diagonal population lower: `0.015625`
- input／composition／result digest:
  `7d93718b4e8375ea3983c37042d0aaedc98f4a16a329687afa69f75511e29657` /
  `7ce1bde2ddc99ace52610c1a814a65dada1711baf048ec5410241ce497f809d7` /
  `80bae2065ec27d22c7e5a392f764e422ef57d521e0848d6c9eae3e0ed07e8bf7`
- runner／artifact newline-normalized SHA-256:
  `bacf2eca47348ebbb5f5fbfe739f3239ebdb49eedc0d615efc144eb113b5f1bf` /
  `dd28dc89f2096252db80e2ad7461ebdf71bb757e879b8657df01da766849ebdb`

従って、すでにcomponentwise MPFR-85へencode・repairされ、Q007ag tube内にあるfixed-leaf stateを
初期条件とすれば、sampling-timeの保存量とtube membership、および各stepの全内部stage positivityを
数学的帰納で全iterateへ延長できる。4 probeは実装回帰でありtube sampling proofではなく、帰納は
tube-wide exact-rational boundだけを使う。任意exact stateのinitial encoding／repairがこの初期集合へ
入ることとsame-initial shadowingは未認証であり、次はQ007aoでinitialization interiorを独立に判定する。

### Q007ao propagated-tube exact-state initialization interior

Q007ag／Q007am／Q007anのartifactとrunnerを封印し、Q007anをtransitive upstreamごとfresh replayした。
Q007aaの登録内側半径をQ007agのtube拡大率（base 100倍、normal 10倍）で写したexact-state set

\[
\lVert a\rVert_1\le8.9998\times10^{-17},\qquad
\lVert z\rVert_*\le4.999999999\times10^{-11}
\]

に対し、componentwise MPFR-85 encodingとQ007y row-major repair後のbase shift、direct external error、
graph shiftをexact rationalで評価した。

- classification:
  registered propagated-tube exact-state interior survives MPFR-85 encoding and repair
- validity／hypothesis gates: 7 / 7、6 / 6 passed
- base／normal inward margin: 2e-21 / 1e-20
- raw／repair／total input Wiener upper:
  7.470474916829075e-24 / 1.2452407121655381e-23 / 1.9922882038484456e-23
- base increment／headroom／margin utilization:
  3.009718329710275e-23 / 1.969902816702897e-21 / 0.015048591648551374
- direct external／graph-shift／total normal increment:
  5.960355768038905e-22 / 9.362725402249564e-36 / 5.960355768038998e-22
- normal headroom／margin utilization:
  9.4039644231961e-21 / 0.05960355768038998
- tight base／normal initialization radius:
  8.99999699028167e-17 / 4.9999999999403966e-11
- input／bound／result digest:
  4793702239a7bc6252b71b5fff43cc68e78dcad1d1b9446db94544b85270deb3 /
  b747e0a635cf4d747728fd5447e613b62a0b951813634f8a98c9e80a17f3308a /
  6c2a41f2ff2d610d8f542cb132a50a678298098245063d54bcd2a38b6e6a8360
- runner／artifact newline-normalized SHA-256:
  2cd4c852c2855b93efaeb618bc3b1cb488885375c69f11e2c7624f0ea84614f7 /
  c6262043848a479b90634fc8aa82dbd02bfcaea4bcb3467d240b956fd7602b8f

従って登録inner setのexact fixed-leaf stateは、encoding・input repair後にQ007ag repaired tubeへstrictに
入り、Q007anと合成してsampling-time fixed leaf／tube membershipと全内部stage positivityを全iterateへ
帰納できる。このcoarse boundはcenter cancellation、spatial phase、Q007zを使わない。任意Q007ag
boundary state、arbitrary exact physical state、same-initial shadowing／trajectory errorは未認証であり、
次はQ007apでshadowingだけを独立に判定する。

### Q007ap propagated-tube same-initial all-iterate forward shadowing

Q007ab／Q007ag／Q007am／Q007aoのartifactとrunnerを封印し、Q007abとQ007aoをfresh replayした。
Q007ao replayではQ007anと全transitive upstreamも再現した。平衡点で固定したselected／external
eigencoordinate直和normを変えず、Q007agのstate radiusとnonlinear derivativeだけを代入して
exact-map Lipschitz boundを再構成した。Q007aoのinitial defectではgraph-relative membership用の
graph shiftをtrajectory errorへ二重加算せず、Q007amのtube-wide一段local defectと幾何級数で合成した。

- classification:
  `propagated-tube fixed-coordinate contraction certifies all-iterate MPFR-85 forward shadowing`
- validity／hypothesis gates: `7 / 7`、`6 / 6` passed
- linear／nonlinear／full Lipschitz upper:
  `0.9920954673554099 / 2.7528278762500916e-7 / 0.9920957426381974`
- contraction gap: `0.007904257361802534`
- initial／one-step coordinate defect upper:
  `6.261327601009932e-22 / 2.4093250948226748e-20`
- stationary／uniform coordinate error upper:
  `3.0481359405954845e-18 / 3.0481359405954845e-18`
- uniform physical Wiener error upper／tube-radius ratio:
  `8.803831096064757e-18 / 6.096261293035372e-8`
- registered relative／absolute accuracy threshold:
  `1e-6 / 1.4441361143956587e-16`
- input／recurrence／result digest:
  `06692ce9d11691d2a45cd57220ea3e5e201b5c2beb2d0b55776a60f15456830f` /
  `108cb6d50ecaa2d9ad50c02777f6c0bb03a979903849149e30f686c8004fc1ce` /
  `1ee4dc09badbba0264ccc05317ba87de68557d5df148cb7085b158097d17a910`
- runner／artifact newline-normalized SHA-256:
  `095bd3cf728e916d937df22bf9e6773698801064213cd679af52d39719f94d3d` /
  `3b35ad0c3f8979f295214ae16c7be09f6a1047b2779f9eeabe3dabec759e49f0`

従って、Q007ao inner exact-state setの同じstateから始めるexact軌道とsealed repaired MPFR-85軌道の
sampling-time forward errorは、全非負iterateで上の一様Wiener bound内に留まる。これはbi-infinite
shadowing lemma、backward error、内部stage間距離、componentwise相対誤差、任意Q007ag boundary
initialization、他grid／MPFR build、性能、grid-uniform／continuum結果ではない。Q009 TT-crossは
Q008c／Q010により保留したままとし、次はQ011 boundary／forcingまたは別norm certificateを
新しいgateとして事前登録する。

### Q011a nonzero-mean periodic forcing fixed-point obstruction

odd periodic \(17^2\)、\(\omega=3/2\)、\(\eta=1/100\)のfiltered BGK mapへ、collision後に
state-independent source

\[
S_q(F)=3w_q(c_q\cdot F),\qquad F=(3\,2^{-40},0)
\]

を各siteで加えた。D2Q9 source moment、10 positive probe、source derivative、rest reference
Fourier symbolを独立に監査した。

- classification:
  `nonzero-mean periodic body force is incompatible with a fixed point of the registered conservative map`
- validity／hypothesis gates: `6 / 6`、`4 / 4` passed
- exact per-step global momentum increment／population-l1 residual lower:
  `867*2^-40 / 867*2^-40`（float `7.885319064371288e-10`）
- source moment residual: `0.0`
- maximum finite state／compensated global ledger error:
  `1.3877787807814457e-17 / 1.2032042029375134e-14`
- maximum best forced／unforced derivative discrepancy:
  `5.062223386808321e-14`
- rest reference strict unit-circle count／largest nonunit modulus:
  `3 / 0.9920954673551`
- minimum rest forced-output population:
  `0.027777777777550403`
- source／probe／result digest:
  `75fd3fe1050b39a333f483375969a67c79ab9ec75009a2048359d0f0dabb7492` /
  `43d0b722ba63a45ccf6b5a41cffaef387448fcc2cd9324538887fd3169571001` /
  `9b1f0c1516a365481c72617957b30424a7873136d221bd164b6d0617c4c3d958`
- runner／artifact newline-normalized SHA-256:
  `41e45565066fd4c96c2ae927bc8cc6a1218377f67b711f6cc312ecbf0d1c68de` /
  `31c427660b10771af7756c249408606578a9b7a02d756bc77b918b56e7a5b14a`

exact collisionはlocal momentumを、periodic streamingとpopulation-wise filterはglobal momentumを
保存するため、fixed point仮定は上のstrict positive incrementと矛盾する。rest Jacobianがunforced
symbolと一致することはsource微分0のreference-state診断であり、restはforced fixed pointではない。
finite-precision bitwise fixed point、Guo／EDM精度、zero-mean forcing、drag、Poiseuille／Couette、
forced manifoldは主張しない。次はQ011bでzero-mean single-wave periodic forcingを事前登録する。

### Q011b zero-mean periodic forced fixed point and full fixed-leaf spectrum

Q011aと同じodd periodic \(17^2\)、\(\omega=3/2\)、\(\eta=1/100\)のmapに

\[
F_x(y)=3\,2^{-24}\cos(2\pi y/17),\qquad
S_q(y)=3w_qc_{qx}F_x(y)
\]

をcollision後に加えた。全mass \(289\)、全momentum 0の葉を153×150 orthonormal nullspace basisで
表し、x-independent stripe fixed pointをzero coordinateとrest linear responseの二初期値から解いた。
任意状態BGK Jacobian、full-grid action、x-Fourier block actionを独立に照合した。

- classification:
  `zero-mean single-wave periodic forcing yields a numerically resolved stable fixed-leaf fixed point`
- validity／hypothesis gates: `6 / 6`、`4 / 4` passed
- Newton accepted steps（zero／linear-response start）: `2 / 1`
- maximum terminal projected／full／component residual:
  `3.4838391155252677e-16 / 4.088062755440557e-16 / 1.6653345369377348e-16`
- two-solution absolute／forced-departure-relative distance:
  `7.901660672580398e-16 / 2.444328466505941e-11`
- minimum population／density: `0.027775908313351423 / 0.9999999999999997`
- first-harmonic \(j_x\) amplitude／registered force amplitude:
  `2.202356130540601e-05 / 1.7881393432617188e-07`
- departure Fourier leakage outside \(k_y=0,\pm1,\pm2\):
  `9.755400055442727e-12`
- unrestricted \(k_x=0\) unit count／fixed-leaf eigenvalue count:
  `3 / 2598`
- maximum fixed-leaf eigenvalue modulus（\(k_x\) index）:
  `0.9920954673551019 (0)`
- minimum \(\sigma_{\min}(I-J)\)／maximum \(\kappa_2(I-J)\):
  `0.00649328212134047 / 360.53472657220163`
- maximum Schur reconstruction／unitarity／conjugate-spectrum Hausdorff／block-action error:
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

このaccepted結果はfloating-point Newton／Schurによる単一grid・単一amplitudeのnumerical
prequalificationである。rigorous existence／uniqueness、basin、forced slow-subspace selection、
nonresonance、normal attraction、forced invariant manifold、他grid／amplitude、wall boundaryは
主張しない。次はQ011cでこのfixed pointのcandidate slow spectral clusterと外部gapを事前登録する。

### Q011c forced slow spectral-cluster continuation

Q006hのfirst-shell 8 wave × 3 hydrodynamic modeを、Q011b forceの
\(t=j/8\), \(j=0,\ldots,8\)に沿って追跡した。\(k_x=0,1,16\) blockでselected complex
dimensionを`6 / 9 / 9`に固定し、個別固有ベクトルではなくordered complex Schur range、
Riesz projector、cluster eigenvalue setを比較した。forward／backward fixed-point path、
unforced-targetからのdirect endpoint control、共役block closureも独立に監査した。

- outcome／classification: `inconclusive / registered forced spectral-cluster audit is invalid`
- validity gate: `5 / 6` passed；raw cluster／checkpoint hypothesis diagnostics: all passed
- maximum forward/backward state distance:
  `3.2722439815434854e-15`
- maximum adjacent angle／minimum reference alignment:
  `1.0421788015551248e-05 / 0.9999999965243628`
- minimum selected/excluded eigenvalue separation／maximum projector 2-norm:
  `0.023905378580598713 / 1.5115930042152532`
- minimum checkpoint Sylvester separation:
  `0.019362054767979874`
- minimum global modulus normal gap／maximum full fixed-leaf radius:
  `0.002061121154971146 / 0.9920954673551043`
- endpoint state distance／relative distance from Q011b stored state:
  `3.2437399411382716e-15 / 1.0034303173230714e-10`
- endpoint radius／minimum-resolvent-singular-value absolute difference:
  `1.6653345369377348e-15 / 1.231653667943533e-16`
- endpoint maximum-condition absolute difference:
  `7.048583938740194e-12`（登録上限`1e-12`）
- Q011b stored／continued minimum-singular and maximum-condition witness:
  `16 / 1`（共役blockの交換）
- input／path／spectrum／result digest:
  `7d8d4a593dc29a715c995e237890da4de17314c4feffabe10111b289120435ee` /
  `06254ea5569d8b0c8c5369477c82ea685284aec9970574c46c24fea749280b92` /
  `5b1e79280b752268248f5150dd12c73a96719cb20d86cbd34fb3ff1e1b8b472c` /
  `4b41c4e7bda3a45f1ece871c183d321bed637d255053e22a82e7000dd83f5751`
- runner／artifact newline-normalized SHA-256:
  `10222da26fe14b97cd9565c517838d3a03e21f19e605d4a60cb2461e011d1d13` /
  `dbb562dd3628dc7589219baa94ae6791e084847f302c69dbcdc328b94ac6d2b3`

唯一のvalidity failureは、許容された微小なstate差に対してpointwise worst-indexとcondition numberを
absolute `1e-12`で一致させる再現規則に局在した。閾値を観測後に緩めず、Q011cの
`inconclusive`判定と全raw診断を保存する。次は、封印済みQ011cを入力として共役orbit単位の
set-valued witnessとstate-to-spectrum感度を事前登録する修復監査を行う。これを通すまではQ011dの
external nonresonanceやforced invariant manifold構築へ進まない。

### Q011c1 conjugacy-orbit endpoint localization

Q011cのstored／continued endpointを再構築し、各17 blockで
\(A_k=I-J_k\)のfull SVDを実行した。実測差へ

\[
d_k=\|A_k^c-A_k^s\|_F+
64\epsilon_{\rm mach}\max(1,\|A_k^s\|_F,\|A_k^c\|_F)
\]

を加えた保守的Weyl区間で、continued \(\sigma_{\min}\)、\(\sigma_{\max}\)、\(\kappa_2\)を
全blockについて囲んだ。

- classification:
  `the Q011c endpoint failure is localized to perturbation-consistent conjugate-witness tie instability`
- validity／hypothesis gates: `5 / 5`、`4 / 4` passed
- maximum resolvent Frobenius difference／registered bound:
  `4.2352782748696136e-14 / 2.9468087840500247e-13`
- maximum minimum／maximum singular-value bound utilization:
  `0.0009382376259671139 / 0.010647618003265125`
- minimum-singular／maximum-condition winning-orbit separation margin:
  `2.694725883406468e-10 / 0.5844815558106689`
- maximum stored／continued SVD reconstruction residual:
  `2.889692747875842e-15 / 2.94286841789878e-15`
- maximum stored／continued SVD unitarity residual:
  `2.5479952376461563e-14 / 2.480871382499916e-14`
- maximum stored／continued matrix-conjugacy residual:
  `6.570605272701854e-16 / 6.577836273397531e-16`
- input／metric／enclosure／result digest:
  `e9ea01348fe839dd745c3ccb7cf2e622bec3c0a4f080a1ab1c62a92a02ced064` /
  `fca5a81f3fc47e24a6f17578065adb527d892400d5d88c8eb18cf7089e234a9e` /
  `7a6cd761f88b328c2ffa74de5b9fb7952f454b86a99630d6266973e8fa6fea20` /
  `ad8b47548ebc04595246301864314502158e686520197377b3a33d30db1d4f86`
- runner／artifact newline-normalized SHA-256:
  `1f777dc50c6748cb8d8a64d643822b55733ac247b5de7d08b119d628b63c52a6` /
  `939baa85fa4db1efaf701985d81665f863e5f77f6ec2c95cfc2bacf004c0c45c`

stored／continuedのradius winnerは`{0}`、minimum-singular／maximum-condition winnerは
ともに`{1,16}`で、個別witnessだけが`16 -> 1`へ交換した。Q011c1はこの失敗を説明したが、
同じ観測データを使うlocalizationであるためQ011cを再採点しない。次は共役orbit意味論を最初から
固定し、未使用のheld-out force-amplitude nodesを加えたQ011c2を通してからQ011dへ進む。

### Q011c2 held-out forced spectral-cluster reissue

Q011cのtraining node \(t=j/8\)の間に、未使用の
\(t=(2j+1)/16\), \(j=0,\ldots,7\)を置いた。17-node forward／backward fixed-point pathで
clusterを追跡し、training state／cluster、direct endpoint、Q011b stored canonical endpointをcontrol
として再現した。8 held-out node全てで3 blockの明示的Sylvester SVDと全2598 fixed-leaf
eigenvalueを評価した。

- classification:
  `the forced first-shell cluster passes a conjugacy-orbit reissue with eight held-out amplitude nodes`
- validity／hypothesis gates: `7 / 7`、`5 / 5` passed
- maximum forward/backward／training state distance:
  `5.037082596836928e-15 / 4.318359172954769e-15`
- endpoint absolute／relative distance:
  `9.417935011590327e-16 / 2.913378288239695e-11`
- minimum population／density:
  `0.027775908313351423 / 0.9999999999999997`
- maximum adjacent／training／canonical principal angle:
  `5.2108940113403335e-06 / 1.8103036342337398e-13 / 8.532131573213541e-14`
- minimum external separation／maximum projector 2-norm:
  `0.02390537858060371 / 1.5115930042152512`
- minimum held-out Sylvester separation:
  `0.019362054855570406`
- minimum held-out normal gap／maximum held-out fixed-leaf radius:
  `0.0020611211556098574 / 0.9920954673551043`
- endpoint resolvent difference／registered perturbation bound:
  `1.1428197375089487e-14 / 2.639179006344862e-13`
- endpoint minimum-singular／maximum-condition orbit margin:
  `2.6953366361742725e-10 / 0.5844815592084842`
- input／path／holdout-spectrum／endpoint／result digest:
  `de4b0c4d38d0efcff9c7db4bbef66ba6d081a6703c732dbd7116a294020459f2` /
  `36be8801af32ae178e91e049b2640ed4bb058107abdf2df2af8860930c53c27d` /
  `d7319399578d3755ee0679122dec5e6b6d3454e394295bd62886920d104b0d72` /
  `8c78791883b82f4a964d0c102006d9295b7b96733e77dea93249f30dc427b6a8` /
  `8c23b985d69ffaa980e752e5d262184c0a6d466681d9d44fa4f0e9101df02b0c`
- runner／artifact newline-normalized SHA-256:
  `87bdfc1ed20e6e68e4a395d36399adbab19e82809c626ecefa65a342ce42b9d2` /
  `c1794ca72eebd60c4bc097278495218e9e2d2e84bdacd0f478e510a80fcba42a`

Q011c2はQ011cを再採点せず、新しいholdoutを持つ別gateとしてacceptedである。従って単一17²
grid・登録force・17 amplitude nodeのbinary64 prequalificationとしてcandidate forced clusterを
選択する。continuous-amplitude theorem、rigorous projector／SVD enclosure、individual mode label、
external nonresonance、forced invariant manifold、nonlinear normal attractionは未認証である。
次はQ011dでquadratic external nonresonanceとforced homological operatorを事前登録する。

### Q011d forced quadratic external homological-family prequalification

Q011b stored forced endpointでQ011c2のselected clusterを直接ordered-Schur分解し、
\(R_1=\operatorname{diag}(T_{s,0},T_{s,1},T_{s,16})\in\mathbb C^{24\times24}\)と、
output sector \(k_x=0,1,16,2,15\)のexternal quotientを構成した。24 selected coordinateの
unordered quadratic pair全300個をsector count `102 / 54 / 54 / 45 / 45`へ分解し、
300×300 symmetric-product action \(K\)を明示的にassemblyした。

各固有値積 \(\mu_{ij}\)について
\(H_{ij}=A_{e,k}-\mu_{ij}I\)のfull singular spectrum、rank、spectral distance、
condition number、登録複素RHSのdirect solveを全300 blockで評価した。さらにSchur基底の
nonnormal couplingを保持した
\(\mathcal H_k(X)=A_{e,k}X-XK_k\)を、5 sector × 4 RHSで検査した。

- classification:
  `the forced quadratic external homological family is numerically nonresonant and solvable`
- validity／hypothesis gates: `7 / 7`、`5 / 5` passed
- maximum structural／conjugate-spectrum residual:
  `7.35746952368904e-14 / 1.3286214932264194e-14`
- selected minimum／external maximum eigenvalue modulus:
  `0.983770956987517 / 0.981709835832543`
- global normal gap／full fixed-leaf radius／spectral quotient:
  `0.0020611211549740327 / 0.9920954673551019 / 1.128181043680419`
- sector leakage／maximum action error／maximum product-spectrum error:
  `0.0 / 2.4215004011706513e-16 / 0.0`
- minimum block singular value／spectral distance:
  `0.0001550243474275936 / 0.00019318395013023792`
- maximum block condition／direct-solve residual:
  `15018.139810898925 / 3.0754729793416724e-15`
- maximum conjugate-sector scalar discrepancy:
  `2.0227681201111162e-11`
- 20 sector-probe maximum residual／response amplification:
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

全300 blockはfull rankで、最小特異値と最小spectral distanceは登録floor `1e-5`を通過した。
sector-wide probeも通過したため、canonical endpointのcomplete quadratic external spectrumと
登録有限RHSに対してoperator familyをprequalifiedとする。ただしprobeはrigorous inverse-norm
upper boundではない。forced-map Hessian、quadratic forcing、\(W_2\)、\(R_2\)、homological residual、
independent derivative、invariance residual order、forced SSM existence／uniqueness、nonlinear
normal attractionは未認証である。次はQ011eでdense forced quadratic chartを観測前に事前登録する。

### Q011e dense forced quadratic fixed-leaf chart

Q011b stored endpointとQ011d selected clusterを固定し、案Aの
\(\delta M=\delta P_x=\delta P_y=0\)葉上でforced-map解析Hessianを構成した。ordered-Schurの
invariant external complementを使って全300 unordered pairを5 output sectorへ分け、dense
\(W_2\)と\(R_2\)を解いた。さらにcomplex chartをdeterministic real QR basisへ移し、forced map
そのものの独立mixed finite differenceと一段不変性残差を評価した。

- classification:
  `the forced fixed-leaf quadratic chart is constructed, but the registered residual-order window is underresolved`
- validity／hypothesis gates: `7 / 7` passed、`5 / 6` passed
- maximum complex structural／real linear invariance residual:
  `7.35746952368904e-14 / 8.341890217669523e-15`
- analytic forcing／\(W_2\)／\(R_2\) Frobenius norm:
  `6.834040875959414 / 14.084081139824606 / 0.5789086833342865`
- maximum sector solve／full homological／pairwise homological residual:
  `8.463492700134046e-16 / 1.2377387705494087e-14 / 1.3875757356771478e-14`
- graph-gauge／zero-\(k_x\) conserved-moment residual:
  `2.028243962507091e-15 / 8.28412455635593e-15`
- forcing／\(W_2\) Fourier leakage:
  `4.5884705629714995e-15 / 2.903640423048552e-15`
- independent Hessian maximum discrepancy／coarse-to-fine change:
  `1.2602687807695985e-9 / 3.254644954471969e-7`
- residual slope eligible／degenerate directions: `0 / 32`、`32 / 32`
- linear／quadratic residual fit-point count per direction: `5 / 1`
- maximum largest-amplitude quadratic／linear residual ratio:
  `8.954201113852774e-5`
- minimum chart-or-mapped population／maximum conservation drift:
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

構造・Hessian・homological・実座標化の全gateは通り、有限binary64 dense quadratic chartは
構築できた。しかし登録noise floor `1e-13`に対してquadratic residualの有効点が各方向1点しかなく、
三次slopeは測定できなかった。従ってQ011eのbinary outcomeは再採点せず`rejected`とし、
`dense_forced_quadratic_chart_is_constructed=true`と
`registered_residual_order_is_confirmed=false`を同時に記録する。forced SSM existence／uniqueness、
uniform Taylor remainder、nonlinear normal attraction、basin、他grid／force／wall boundaryは未認証である。
次は同じnoise floorとslope閾値を保った独立拡大振幅窓をQ011e1として事前登録する。

### Q011e1 independent enlarged residual-window reissue

Q011e chartの6 array hashと全construction thresholdをfreshに再現したうえで、未使用seed
`20260825`の32 unit directionと振幅
`1.6e-4 / 3.2e-4 / 6.4e-4 / 1.28e-3 / 2.56e-3`を評価した。Q011eと同じnoise floor、
slope interval、最低eligible方向数を維持し、5点primary fitとbridge点を除く上位4点secondary fitを
比較した。

- classification:
  `the independent enlarged window resolves second- and third-order forced chart residuals`
- validity／hypothesis gates: `5 / 5`、`6 / 6` passed
- slope-eligible／degenerate directions: `32 / 32`、`0 / 32`
- linear primary slope range:
  `1.9999592141961493 -- 2.0000652994279995`
- linear secondary slope range:
  `1.9999478838445748 -- 2.000083440834926`
- quadratic primary slope range:
  `2.9998586349153378 -- 3.000154889315294`
- quadratic secondary slope range:
  `2.999908289307265 -- 3.000145181102861`
- maximum linear／quadratic primary-secondary slope difference:
  `1.8141406926464043e-5 / 1.7126610593187763e-4`
- maximum largest-amplitude quadratic／linear residual ratio:
  `0.0013091448869808333`
- minimum chart/reduced/mapped population／maximum conservation drift:
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

独立拡大窓ではlinear chartの二次、quadratic chartの三次が32方向全てで解像され、上位4点fitにも
安定だった。Q011eの元小振幅窓と`rejected` outcomeは変更しない。これは単一17² forced endpoint、
32方向、5振幅のbinary64一段holdoutであり、uniform Taylor remainder、continuous-amplitude family、
forced SSM existence／uniqueness、nonlinear normal attraction、basinは未認証である。次はQ011fで
独立multi-step shadowing windowを事前登録する。

### Q011f independent multi-step forced-chart shadowing window

Q011e1とQ011eのoutcomeを封印し、Q011e chartを同じ6 array hashで再構築した。未使用seed
`20260826`の32方向、Q011e1と同じ5振幅から、linear／quadratic各160 full orbitとreduced-lift orbitを
64 step追跡した。全10,240 stepでerror、positivity、conservation、coordinate normを保存し、7 horizonの
1,120 checkpointでstate hashと振幅slopeを評価した。

- classification:
  `the forced quadratic chart fails the registered finite shadowing window`
- validity／hypothesis gates: `6 / 6` passed、`5 / 6` passed
- slope-eligible／degenerate direction-horizon fits:
  `222 / 224`、`2 / 224`
- degenerate witnesses:
  direction `4`、horizon `1 / 2`、linear／quadratic fit points `5 / 3`
- witness quadratic errors at amplitudes `1.6e-4 / 3.2e-4`:
  horizon 1 `1.1752258806252989e-13 / 9.402263023336189e-13`、
  horizon 2 `1.1463003790416861e-13 / 9.171105405464717e-13`
- eligible linear／quadratic slope range:
  `1.9999216343019504 -- 2.000128344576816` /
  `2.999096737571295 -- 3.000265091846932`
- maximum checkpoint quadratic／linear error ratio:
  `0.002547526388856511`
- maximum horizon-64 quadratic error／initial amplitude:
  `1.1019505895816554e-6`
- minimum full-or-lifted population／maximum conservation drift:
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

失敗は長時間shadowing劣化ではない。唯一落ちたgateは`224 / 224` eligibilityで、direction 4の最初の
2 horizonでは第2振幅のquadratic errorが登録floor `1e-12`を僅かに下回り、高振幅側3点しかfitに
残らなかった。他222 fitの次数と、全checkpoint改善、64-step相対誤差、positivity、保存則は通った。
それでもQ011fを合格へ読み替えない。次はfloorを下げず、未使用amplitudeを追加する独立再発行gateを
事前登録してからQ011gへ進む。

### Q011f1 held-out-amplitude multi-step reissue

Q011f artifactと二つのdegenerate witnessを封印し、同じseed `20260826`の32方向へ未使用振幅
`4.8e-4`のlinear／quadratic trajectoryだけを追加した。元5振幅の保存済みerrorと合わせた6点fitを
行い、noise floor `1e-12`、7 horizon、全slope／performance thresholdを変更せず再評価した。

- classification:
  `the forced quadratic chart passes a held-out-amplitude 64-step shadowing reissue`
- validity／hypothesis gates: `6 / 6` passed、`6 / 6` passed
- slope-eligible／degenerate direction-horizon fits:
  `224 / 224`、`0 / 224`
- merged linear／quadratic slope range:
  `1.9999204011998797 -- 2.000130424734462` /
  `2.9992217798368643 -- 3.00027147080911`
- repaired direction `4`、horizon `1 / 2`のquadratic fit-point count:
  `4 / 4`
- repaired quadratic slopes at horizon `1 / 2`:
  `3.000037106494855 / 3.0000355600774475`
- held-out quadratic errors at horizon `1 / 2`:
  `3.1730810288365184e-12 / 3.0952409781368448e-12`
- maximum merged checkpoint quadratic／linear error ratio:
  `0.002547526388856511`
- maximum merged horizon-64 quadratic error／initial amplitude:
  `1.1019505895816554e-6`
- minimum merged full-or-lifted population／maximum conservation drift:
  `0.027704572566416702 / 1.8214860035899544e-12`
- held-out-only maximum checkpoint ratio／horizon-64 relative error:
  `0.00047765951440299786 / 3.8740640529751134e-8`
- direction SHA-256:
  `4d0bef57236d4f70a8a8f422b1bdfa39cd5737c88401c2441decdd98d886d2f9`
- input／chart-reconstruction／heldout-trajectory／merged-fit／result digest:
  `101adcdc6fc2d40dc984e6ba900d234b913f7c78aa34381a08d0a77aa9e23000` /
  `ba50ee295551dae970d33e1bba735ac0502987aef0f4a82987f2998ae884f732` /
  `243c41522a9eb7d7b78b2031bdbe8f55eb23b447e8d84162b1aae2f53b651829` /
  `2e3fcee7bebec5c82f2fbd2b78ddac8c44401fd0681ad5d9feb60c7257a8326e` /
  `484580786b6c535856f0693b14c58815462e1de979759057dc3b402d475bcbc7`
- runner／artifact newline-normalized SHA-256:
  `eab2d63a075f2c43b4c6adfaa7941e9c23bf85a351427057130f68945346ce62` /
  `79ddb64e0965b5b87b7ad68c6dc8698efdd2281540c798ed27f355747d265bc1`

追加点により、元witnessのquadratic fit maskは
`[false, false, true, true, true, true]`となり、両fitが4点で解像された。これはQ011fの棄却を
再採点せず、同じ有限shadowing hypothesisを独立データで再発行した結果である。6振幅、32方向、
64 step、7 horizonのbinary64観測を越えるall-time shadowing、uniform remainder、basin、normal
attraction、forced SSM existence／uniqueness、他grid／force／wall boundaryは主張しない。次は
natural Fourier-sparse baselineを必須比較対象としてQ011gのTT-SVD費用・精度gateを事前登録する。

### Q011g forced quadratic Fourier-sparse／TT-SVD representation audit

Q011f1とQ011eを封印し、native complex (W_2/R_2)、complex-to-real map、real chartを一度だけ
fresh再構築した。300 unordered pairをoutput sector `0 / 1 / 16 / 2 / 15`へ
`102 / 54 / 54 / 45 / 45`と分け、同じ構造射影済みordered-dense tensorからnatural sparseと
6個のTT-SVD bundleを生成した。TT-SVD toleranceは`1e-13`、rank capは置いていない。

- classification:
  `registered TT-SVD bundles do not beat the natural Fourier-sparse forced-quadratic baseline`
- validity／hypothesis gates: `6 / 6` passed、`1 / 4` passed
- storage／robust-timing／joint winner count: `0 / 3 / 0`
- robust timing winners:
  `flat-output-last / fourier-output-last / d1q3-output-last`
- natural sparse stored real scalars／raw／in-memory／NPZ bytes:
  `94,968 / 760,644 / 761,995 / 762,188`
- best-storage TT (`fourier-output-first`) corresponding values:
  `474,050 / 3,792,544 / 3,795,218 / 3,795,586`
- best TT／sparse scalar／raw／memory／NPZ ratio:
  `4.99168140847443 / 4.98596452479741 / 4.98063373119246 / 4.97985536376852`
- sparse offline median／best TT offline median:
  `2.7488 ms / 401.5353 ms`
- sparse online median／fastest TT online median (`flat-output-last`):
  `0.7321 ms / 0.47460625 ms per joint action`
- fastest TT online ratio／its stored-scalar ratio:
  `0.6482806310613304 / 15.2224538792014`
- maximum TT reconstruction／joint-action／realification error:
  `2.41559062578165e-14 / 3.84139374578316e-14 / 3.82602037711869e-14`
- natural projection loss (W_2/R_2):
  `3.33475349414364e-15 / 0`
- natural-vs-dense action／one-step defect relative difference:
  `3.23695449081624e-16 / 4.16928788077864e-9`
- maximum TT-vs-sparse one-step defect relative difference:
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

全6候補は係数忠実度と一段不変性残差保存を通過したため、棄却原因は近似精度ではなく格納量である。
onlineだけならoutput-last配置に明確な利点があるが、最速候補のcore格納scalarはsparseの約15.2倍で、
事前登録した同一候補によるstorage＋timeのjoint採択条件を満たさない。従ってこの固定係数ではnatural
Fourier-sparseを採用し、TT-crossを開始しない。これはTT一般、別tensorization、GPU、他grid、full rolloutの
不可能性を主張せず、Q011e--Q011f1のoutcomeも変更しない。

### Q011h natural Fourier-sparse 64-step chart equivalence

Q011g artifactとTT-cross非許可を封印し、natural Fourier-fiber係数だけを持つruntimeと
ordered-dense real Hessian oracleを分離した。seed `20260906`の未使用24方向と、既存campaignで
未使用の振幅`4.0e-4 / 9.6e-4 / 2.4e-3`から72縮約軌道を別々に64 step更新した。

- classification:
  `the natural Fourier-sparse chart reproduces the dense forced quadratic reduced trajectory through 64 steps`
- validity／hypothesis gates: `5 / 5` passed、`4 / 4` passed
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

sparse runtimeはbase／tangent／reduced linear map／coordinate map／pair／sector／fiberだけを所有し、
dense quadratic fieldを持たない。全stepで両経路を独立更新したため、natural sparseを今後の
forced quadratic chart実装baselineとする。ただしfull LBM orbitを64 step進めたわけではなく、
Q011f／Q011f1のshadowing outcome、all-time equivalence、forced SSMの存在・一意性、normal attraction、
basinは追加認証しない。Q011gのTT棄却を変更せず、TT-crossを開始しない。

### Q011i exact-dyadic zero-mean forcing compatibility repair

Q011bのbinary64 cosine waveformとsourceをexact dyadic arithmeticで再監査した。raw waveformの和は
\(-71/2^{78}\)、raw global x-momentum sourceはnonzeroであり、exact-real mapとしてはfixed pointと
両立しない。登録済みのreflection midpoint丸めと2,056候補のULP searchはpair `(3,14)`の
`+7 ULP`を選び、exact sum 0のwaveformを一意に得た。各siteではaxis／diagonal source amplitudeを
最大1 ULPだけ調整し、保存したbinary64 source entryそのものについてmass／x-momentum／y-momentumの
local ledgerとglobal ledgerをexactに閉じた。

- classification:
  `the exact-dyadic zero-mean repair preserves the numerical forced fixed-point and linear-spectrum baseline`
- validity／hypothesis gates: `6 / 6` passed、`4 / 4` passed
- raw exact waveform sum／global x-momentum source:
  `-71 / 2^78` / `-267 / 2^80`
- repaired waveform selected pair／shift／changed entries:
  `(3,14) / +7 ULP / 11`
- waveform maximum-component／relative-ℓ2／Fourier-leakage perturbation:
  `1.4558378780933287e-22 / 3.9903677672599853e-16 / 2.661531424982623e-16`
- source maximum selected shift／maximum-component／relative-ℓ2 perturbation:
  `1 ULP / 4.963083675318166e-23 / 4.0883745079611583e-16`
- repaired waveform／source SHA-256:
  `025d6122db8e0d3512224ce4a2af82d57b5728ce0c7450425436218dd561bcbf` /
  `24bb558464cce4ac154b3f2574bd1fe816d11d58c9365e8312f12b0a389df490`
- two-start／repaired-vs-Q011b state ℓ2 distance: `0 / 0`
- representative repaired／sealed Q011b stripe-state SHA-256:
  `612ef4aca91a5c0100286988e0e7979342a9046c3c78fe60ee59ca4e232a7613`
- maximum block-matrix relative perturbation／spectrum Hausdorff distance: `0 / 0`
- spectral radius／minimum σmin(I-J)／maximum condition(I-J):
  `0.9920954673551019 / 0.00649328212134047 / 360.53472657220163`
- input／repair／fixed-point／spectrum／result digest:
  `81a1dc3f9fe934d8e9391dbfe6b80701d68c04b7db954da2f62e92b581dd5b51` /
  `910a82fa1485ce8ad6b488c5bb71ad0c8bcb12b98b6202ebc3805caa8f4a3239` /
  `3adfbcfc7d5e9c3396bbfb60b8d10dce6ff080b90097b82f40b4c057b8518f1e` /
  `5e63b9cc22a662238391dc83b8de1a81eb259af25b3ad2335e481bb0cf83466d` /
  `ac94658b95d2ae1f190fab57af3bd80dbf50a4addd37f6bb7bee27d6aa1d2398`
- runner／artifact newline-normalized SHA-256:
  `2cec0472422ba02bb925e8c90336000058def7c36303479a4037405f873b9b88` /
  `1c8b11a3ae47895a79639a5cfe901ec936fbdde8d10273c56c1578b9a88780ea`

修復量は小さく、現在のbinary64演算ではfixed pointとlinear blocksにbitwiseな変化を生じなかったが、
exact-real mapの保存則compatibilityはraw sourceと異なる。従ってQ011bのnumerical `accepted`は維持し、
Q011e--Q011hのraw-map coefficient、残差次数、shadowingを修復mapへ自動移植しない。Q011i単独では
区間存在・局所一意性を主張せず、その証明は後続Q011jで独立に行った。rigorous spectrum、forced SSM、
normal attractionは引き続き未認証である。

### Q011j repaired fixed-point interval Krawczyk proof

site-major stripe stateのsite 0、velocity `(0,0)/(1,0)/(0,1)`をpivotとし、残る150 populationを
自由座標にした。pivot moment matrixのdeterminantはexact 1、liftはshape `153 x 150`、rank `150`、
infinity operator norm `186`である。Q011i stateのfree entryをexact dyadic centerとし、3 pivotだけを
mass／momentum `(17,0,0)`へexactに戻した。最大pivot補正は`1.1032841307212493e-15`だった。

nonlinear equilibrium、collision、repaired source、periodic streaming、stripe filterを`Fraction`で
構成し、analytic Jacobian enclosureもexact rationalで評価した。dense preconditioner積だけを
256 bit／384 bitの外向きMPFRで独立に計算した。

- classification:
  `the repaired periodic forcing admits a locally unique exact fixed-leaf fixed point in the registered rational box`
- validity／hypothesis gates: `6 / 6` passed、`4 / 4` passed
- registered／passing radius count: `10 / 5`
- selected free-coordinate radius／first failed radius: `1e-8 / 1e-7`
- selected ambient-component radius upper: `1.86e-6`
- selected-box population／density lower:
  `0.02777589831335142 / 0.9999944000000008`
- exact-center reduced residual maximum: `2.2024432251775355e-16`
- exact-vs-binary64 map／independent-Jacobian relative discrepancy:
  `1.994466096750315e-16 / 1.4468366996163912e-16`
- point Jacobian condition／preconditioner infinity norm:
  `1672.0533600047117 / 714.5779769798695`
- 256-bit inverse-defect／center-correction upper:
  `2.0361209046326675e-13 / 9.043895266505443e-16`
- selected 256-bit contraction／Krawczyk utilization upper:
  `0.1997569427734526 / 0.19975703321240526`
- 384-bit upper: 256-bit upper以下、selected radius bitwise一致
- coordinate／lifted-center／preconditioner SHA-256:
  `508f175fc7d1d62d253b5e34877a25fded6f4d207ef26f281a01d10eb5571ed8` /
  `c85cddc2072cb2e86d1a73024da97828d4a7f21f10b631c86a5d9ee0297c72dd` /
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

`q<1`かつKrawczyk imageがbox interiorに入るため、Banach／Krawczyk argumentによりexact repaired
stripe mapのfixed pointが存在し、同じbox内で一意である。x-independent replicationによりfull
17² periodic mapにもfixed pointを与える。ただしlocal uniquenessをglobal uniquenessやbasinへ拡張せず、
Q011b raw exact map、Q011e--Q011h coefficient、区間spectrum、forced SSM、normal attractionを認証しない。
後続Q011kではQ011j box内の一意なexact rootを収縮不等式で再局在化し、その点のspectrumを別gateで認証した。

### Q011k repaired fixed-point interval spectrum and selected／external split

Q011jのNewton-like mapについて、selected box全体の収縮上限とcenter correctionから

\[
\|x_\ast-x_0\|_\infty\le\frac{\|CG(x_0)\|_\infty}{1-q}
\]

をexact rationalで評価した。root coordinate radius upperは`1.1301435463682045e-15`、affine lift後の
population component radius upperは`2.1020669962448604e-13`である。この導出box上でzero blockを
150次元exact affine fixed-leaf coordinate、16 nonzero x-wave blockを各153次元population coordinateとし、
合計2598次元を17 blockへexactに分解した。

Q007hと同じMachin／Taylor trigonometric enclosure、Q011jのexact equilibrium derivative、
256／384-bit directed MPFRを用い、9代表blockのapproximate eigendecompositionからBauer--Fike discを
構成した。残る8 blockはexact conjugacyでtransportした。Q011c2 endpoint eigenvalue setはblockごとの
selected cluster識別にだけ使い、cluster内部の個別branch labelは要求していない。

- classification:
  `the exact repaired fixed point has a rigorously stable and quadratically nonresonant selected/external spectral split`
- validity／hypothesis gates: `7 / 7` passed、`5 / 5` passed
- root coordinate／ambient component radius upper:
  `1.1301435463682045e-15 / 2.1020669962448604e-13`
- root-box population／density lower:
  `0.027775908313350292 / 0.999999999999368`
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

従ってQ011c2でdesignateした24-dimensional selected clusterと2574-dimensional external spectrumは
exact repaired fixed pointで交換せず、全fixed-leaf spectrumはstrictly stableである。またselected
eigenvalueの全300 quadratic productは対応output sectorのexternal spectrumから分離する。ただしこれは
eigenvalue-level nonresonanceであり、Q011c2のcontinuous-amplitude continuation、nonnormal Sylvester／
homological inverse bound、Q011e--Q011h raw-map coefficientの移植、forced SSM、nonlinear normal attractionを
認証しない。次はQ011lでrepaired split上のinterval homological inverseを別gateにする。

### Q011l repaired invariant graph and quadratic homological inverse

Q011kのbinary64 eigenvector matrixをexact dyadic pointとし、認証済みinverse norm upper
\(\beta_n\)とfamily residual upper \(r_n\)から

\[
V_n^{-1}A_n(x_\ast)V_n=\widehat\Lambda_n+F_n,
\qquad
\lVert F_n\rVert_\infty\le\theta_n:=\beta_n r_n
\]

をexact `Fraction`で導いた。selectedを持つblock `0 / 1 / 16`では、selected／external diagonal
center間Sylvester inverseをbaseとしてRiccati mapを閉じ、一意なselected invariant graphを認証した。
graph triangularization後のselected dynamicsとexternal quotientは各center diagonalから
\(\eta_n=\theta_n(1+r_n^G)\)以内にある。

全空間resolventへの置換は使っていない。実際、pair
`[11, 19, 33, 43, 56, 64, 76, 86]`の8件ではQ011k product discがoutput selected discと
重なる。これらも除外せず、external quotient上で扱った。

24 selected座標のunscaled symmetric monomial `i <= j`をQ011dと同じ順で使い、selected dynamicsの
非対角perturbationを

\[
\lVert K(S)-K(\widehat\Lambda)\rVert_\infty
\le 2L\eta_S+\eta_S^2
\]

で包んだ。各sectorのfull operator
\(\mathcal H_q(Z)=E_qZ-ZK_q(S)\)をdiagonal product operatorのperturbationとして評価し、
全5 sectorでNeumann quotientがstrictly 1未満であることをexact rational arithmeticで示した。

- classification:
  `the exact repaired selected/external split has a rigorously bounded quadratic homological inverse in the registered quotient norm`
- validity／hypothesis gates: `7 / 7` passed、`5 / 5` passed
- unsafe full-space pair count／indices:
  `8 / [11, 19, 33, 43, 56, 64, 76, 86]`
- maximum graph radius／self-map utilization／contraction upper:
  `1.6628540517032178e-6 / 0.5000016628554342 / 1.662856816786815e-6`
- minimum selected-graph identification margin lower:
  `0.02390537645745014`
- symmetric-product action perturbation upper:
  `4.9954323399005556e-8`
- sector pair counts／external comparisons:
  `102 / 54 / 54 / 45 / 45 / 44010`
- minimum base homological distance／witness:
  `0.00019318395012417515 / sector 0, pair 173, external center 143`
- maximum Neumann quotient／coordinate inverse／ambient-output inverse upper:
  `0.0003636651445795734 / 5178.2966276547 / 3325900.503434659`
- exact base-pair／Q011k-pair／sector digest:
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

従ってQ011kのeigenvalue-level nonresonanceは、登録quotient normにおけるnonnormal full-sector
homological inverseへ持ち上がった。ただしrepaired mapのquadratic jet／coefficient自体はまだ構成していない。
Q011e--Q011hのraw-map coefficient、higher-order nonresonance、forced SSM存在・一意性、nonlinear normal
attraction、basinへは広げない。次はQ011mでrepaired quadratic jetとcoefficient／residual majorantを
別gateとして事前登録する。

### Q011m repaired exact quadratic jet and cubic-defect majorant

Q011j--Q011lのexact recordを単純有理envelopeへ包含した後、repaired exact mapのlocal equilibriumを
exact `Fraction`で二階・三階微分した。population-to-moment row sum `(9, 6, 6)`、BGK factor `3/2`、
streaming／filter norm `<=1`を合成し、登録domain `U <= 1e-4`で

\[
\lVert D^2\Phi\rVert_{\infty,\mathrm{bil}}\le144.5474473239429<145,
\qquad
\lVert D^3\Phi\rVert_{\infty,\mathrm{tri}}\le3910.210477654001<4000
\]

を得た。mixed-partial symmetry、D2Q9 quadrature、全二階／三階forcingのglobal conserved moment zeroも
exactに列挙した。Q011e--Q011hのraw-map Hessian／coefficientは入力に使っていない。

Q011lの5 sector inverseからgraph-gauge quadratic coefficient \(Z\) の一意解をimplicitに定義し、
componentwise arrayを保存せず、登録式から

- \(K_T=2450.0048392\)
- \(K_F=435182969.1274978\)
- \(K_Z=2.772324401167342\times10^{17}\)
- \(K_P=23064697363.75738\)
- \(K_S=1.24\)

を認証した。8個の事前登録radiusをexactに評価した結果、最大passing radiusは`1e-11`だった。この点で
`U=2.7747744060065423e-5`、`A_R/r=1.4706469736375738`、
`D=1.738847670176358e-5`、`D/U=0.6266627176653649`である。次の`3e-11`はdomain、defect、
utilizationの3条件で失敗した。

- classification:
  `the repaired exact map admits a unique graph-gauge quadratic jet with the registered coefficient and cubic-defect majorants`
- validity／hypothesis gates: `7 / 7` passed、`5 / 5` passed
- exact-root population radius／population floor／density floor:
  `2.1020669962448604e-13 / 0.027775908313350292 / 0.999999999999368`
- center／enclosed-root momentum component upper:
  `2.202356130560565e-5 / 2.2023562566845846e-5`
- selected radius／passing count／first failed larger radius:
  `1e-11 / 7 / 3e-11`
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

従ってrepaired mapのquadratic jetと有限radiusのuniform cubic defectまでは認証した。ただしfinite defectを
exact invarianceへ読み替えず、componentwise coefficient、exact invariant manifold／SSM、smoothness、
normal attraction、basinはまだ主張しない。次はQ011nでa posteriori correctionを独立gateにする。

### Q007p exact-manifold finite-tube normal attraction

Q007oのanalytic radius \(\rho=10^{-18}\)とcorrection radius \(\tau\)を固定し、exact graph-gauge manifoldの周囲に
\(r=10^{-19}\)、\(\zeta=10^{-20}\)のtubeを事前登録した。zero waveではfixed-leaf kinetic population
\(\ell^1\)、8 selected waveではQ007oの6次元external coordinate、残る280 waveではQ007h1のtransported
full eigencoordinateを使い、block-sum external norm \(\|\cdot\|_*\)を構成した。

- classification:
  `registered fixed-leaf tube is uniformly normally attracting in the external-coordinate norm`
- validity / hypothesis gates: `6 / 6`, `4 / 4` passed
- nonselected／selected C4 representatives: `70 / 2`
- reproduced wave blocks／external complex dimension: `289 / 2574`
- Q007h1 proof-digest mismatch／Q007o selected-certificate mismatch: `0 / 0`
- maximum full-coordinate defect: `9.306827894107678e-15`（登録上限`1e-8`）
- linear external contraction \(q_0\): `0.981709835832552`
- conversion bounds \(K_s/K_a/K_L\):
  `2.888267212368763 / 29.917136268364473 / 1.5106842091904618`
- tube state Wiener upper \(x_*\): `3.075728140408179e-19`
- base-image modal upper \(a_*\): `9.920954673554099e-20`
- base forward-invariance margin \(r-a_*\): `7.904532644590156e-22`
- normal fiber contraction \(q_*\): `0.9817098358325526`
- tangent conorm lower \(m_T\): `0.9837709569923394`
- domination ratio \(\Gamma_*=q_*/m_T\): `0.9979048769989224`
- registered domination-cap margin \(0.999-\Gamma_*\): `0.0010951230010776572`

従って登録tube全体でbaseとnormal fiberがforward invariantであり、normal fiberはone stepで一様に収縮し、
tangentよりstrictに速く収縮する。Q007fの有限33点・10-step観測とは異なり、これはexact manifoldのfull
registered tubeに対する解析的majorantである。ただし\(\|\cdot\|_*\)は固定Fourier external-coordinate normで
ありEuclidean normではない。Q007dのEuclidean棄却、Q007c1の有限振幅性能棄却、positivity、より大きいtube、
global basin、grid-uniform性、continuum limitは変更・認証しない。

### Q007q registered-tube population positivity

Q007pで認証した同じ固定tubeに対し、D2Q9 rest equilibrium
\(f_i^*=w_i\)とFourier--Wiener triangle inequalityを用いた。全289 Fourier phaseのmodulusが1であるため、

\[
\max_{x,i}|\delta f_i(x)|
\le \max_i\sum_k|\widehat{\delta f}_{k,i}|
\le \|\delta f\|_{\mathrm W}
\le x_*.
\]

Q007pのexact tube-state upper \(x_*=3.075728140408179\times10^{-19}\)と
\(\min_i w_i=1/36\)、\(\sum_iw_i=1\)から、exact rational boundとして

\[
p_*=\frac1{36}-x_*>0,\qquad d_*=1-x_*>0
\]

を得た。Q007pのforward invarianceにより、このlower boundは初期状態だけでなく
full-map sampling時刻 \(n=0,1,2,\ldots\) の全iterateへ帰納的に適用される。

- classification:
  `registered Q007p tube lies in the strictly positive population cone at every full-map iterate`
- validity / hypothesis gates: `5 / 5`, `3 / 3` passed
- exact D2Q9 weight multiplicity: `1 / 4 / 4`
- Fourier wave count: `289`
- tube-state Wiener upper \(x_*\): `3.075728140408179e-19`
- population lower: exact \(1/36-x_*>0\)
- density lower: exact \(1-x_*>0\)

これはfixed 17²、fixed conservation leaf、registered Q007p tubeのreal stateについて、
full one-step mapの入力／出力時刻だけを扱うQ007q単独の結論である。内部stageは次のQ007rで別途扱う。
entropy、monotonicity、maximum principle、より大きいtube、global basin、grid-uniform性、
continuum limitは認証しない。Q007c1とQ007dの既存棄却も変更しない。

### Q007r exact stagewise population positivity

Q007qと同じ\(x_*\)を固定し、D2Q9 moment map \(M\)、rest-equilibrium tangent \(E\)、
BGK collision linearization \(C=(1-\omega)I+\omega EM\)をexact rational arithmeticで再構成した。
population-summed Fourier--Wiener \(\ell^1\)誘導normと非線形majorantは

\[
\|EM\|_1=\frac{13}{6},\qquad
\|C\|_1=\frac{19}{6},\qquad
\|N_{\mathrm{eq}}\|_{\mathrm W}\le7\frac{x_*^2}{1-x_*}.
\]

従ってequilibrium evaluationとpost-collisionのdeviation upperは

\[
e_*=\frac{13}{6}x_*+7\frac{x_*^2}{1-x_*},
\qquad
c_*=\frac{19}{6}x_*+\frac{21}{2}\frac{x_*^2}{1-x_*}
\]

であり、それぞれ`6.66407763755105e-19`、`9.73980577795923e-19`だった。
どちらもminimum rest population \(1/36\)よりstrictに小さい。さらにperiodic streamingは9個の
population-wise permutation、登録filterは
\(99/100\)と4個の\(1/400\)からなる凸結合であるため、post-collision lowerを保持する。

- classification:
  `registered Q007p tube is population-positive at every exact BGK, streaming, and filter stage`
- validity / hypothesis gates: `6 / 6`, `5 / 5` passed
- equilibrium／collision linear norm: `13/6 / 19/6`
- equilibrium／collision nonlinear constant: `7 / 21/2`
- streaming periodic permutations: `9 / 9`
- filter coefficient sum／minimum: `1 / 1/400`
- equilibrium／post-collision deviation upper:
  `6.66407763755105e-19 / 9.73980577795923e-19`

Q007pのforward invarianceにより、同じstage boundは全one-step iterateへ適用される。これはexact
mathematical mapのequilibrium evaluation、collision output、streaming output、filter outputに対する結論である。
NumPy／IEEE-754の全中間加算・除算を外向き区間で囲った結果ではなく、entropy、monotonicity、
maximum principle、より大きいtube、global basin、grid-uniform性、continuum limitも認証しない。

### Q007s registered-grid finite-tube enlargement

Q007pのmap、固定保存量葉、exact graph-gauge manifold、external-coordinate norm、analytic majorantを
変更せず、base radius 9点とnormal radius 99点のCartesian product全891候補を`Fraction`で評価した。
候補は枝刈りせず、passing candidateのbase radiusを先に、次にnormal radiusを最大化する事前登録済み
辞書式規則を適用した。

- classification:
  `registered exact-manifold tube enlarged on the fixed rational candidate grid`
- validity / hypothesis gates: `6 / 6`, `5 / 5` passed
- registered／passing candidates: `891 / 676`
- selected base／normal radius:
  `9e-19 / 5e-12`
- Q007pからのbase／normal improvement factor:
  `9 / 500000000`
- tube-state Wiener upper \(x_*\): `1.44413385700551e-11`
- base-image modal upper \(a_*\): `8.9950210818665e-19`
- base forward-invariance margin \(r-a_*\): `4.97891813350137e-22`
- normal contraction／tangent conorm／domination ratio:
  `0.9817098620375503 / 0.9837709569923394 / 0.9979049036362179`
- selected sliceの次候補: \(\zeta=6\times10^{-12}\)、base forward invarianceでfail
- canonical candidate digest:
  `91fcc70355acfc4b7163c951227188960ef275408b06a678d45d5e4ec4c85300`

従って固定17²・固定保存量葉・同じexact manifold・同じexternal-coordinate normについて、選択した
registered tubeのforward invariance、一様one-step normal contraction、strict normal dominationを認証した。
これは9×99有限格子上の辞書式選択であり、連続最適化、最大可能tube、Euclidean／grid-uniform attraction、
global basin、continuum limitを意味しない。Q007q／Q007rのpopulation positivity certificateは旧Q007p tubeに
封印されたままで、Q007sの結果から新しいtubeへ自動拡張はしない。full-map positivityは次のQ007tで
独立に扱う。

### Q007t larger-tube full-map population positivity

Q007s selected tubeのexact state upper \(x_*=1.44413385700551\times10^{-11}\)を再利用し、Q007pから
transitiveに固定されたFourier--Wiener normとD2Q9 weight tableを再構成した。全289 Fourier phaseの
modulusが1であるため、各site・populationのdeviationは\(x_*\)以下である。

- classification:
  `registered Q007s larger tube lies in the strictly positive population cone at every full-map iterate`
- validity / hypothesis gates: `5 / 5`, `3 / 3` passed
- selected base／normal radius: `9e-19 / 5e-12`
- Fourier wave／D2Q9 population count: `289 / 9`
- tube-state Wiener upper \(x_*\): `1.44413385700551e-11`
- population lower: exact \(1/36-x_*>0\)、float `0.02777777776333644`
- density lower: exact \(1-x_*>0\)、float `0.9999999999855587`

Q007sのforward invarianceにより、同じlower boundはfull one-step mapの入力／出力時刻
\(n=0,1,2,\ldots\)へ帰納的に適用される。これはequilibrium evaluation、BGK collision、
periodic streaming、filter outputのstagewise positivityをまだ認証しない。Q007rのstagewise
certificateは旧Q007p tubeに封印されたままであり、次の独立gateで扱う。

### Q007u larger-tube exact stagewise population positivity

Q007tのexact \(x_*=1.44413385700551\times10^{-11}\)とQ007s forward invarianceを固定し、
D2Q9 moment map、rest-equilibrium tangent、BGK collision linearization、非線形convolution
majorant、streaming permutation、five-point convex filterをexact arithmeticから再構成した。

- classification:
  `registered Q007s larger tube is population-positive at every exact BGK, streaming, and filter stage`
- validity / hypothesis gates: `6 / 6`, `5 / 5` passed
- equilibrium／collision induced \(\ell^1\) norm: `13/6 / 19/6`
- equilibrium／collision nonlinear constant: `7 / 21/2`
- equilibrium deviation upper／population lower:
  `3.12895669032459e-11 / 0.02777777774648821`
- collision deviation upper／population lower:
  `4.5730905474030926e-11 / 0.02777777773204687`
- streaming／filter population lower:
  `0.02777777773204687 / 0.02777777773204687`
- runner SHA-256:
  `56fc99f1f381e97e70710c7da0cee8d1262d0c10190cf617316f822d1eb29014`
- artifact newline-normalized SHA-256:
  `b568fc304fd939121dd52543f316cb571ae6f4be4f4f664c68fe1c749b566c55`

従って固定17²・固定保存量葉・Q007s selected tube内の全real stateについて、exact mathematical
mapのequilibrium evaluation、BGK collision output、periodic streaming output、five-point filter
outputで全9 populationがstrict positiveであり、同じboundを全iterateへ再適用できる。これは全ての
NumPy／IEEE-754中間演算のroundoff enclosure、entropy、monotonicity、maximum principle、連続最適tube、
global basin、grid-uniform性、continuum limitを認証しない。

### Q007v binary64 stage-roundoff enclosure

Q007u／Q007sと現行`d2q9.py`／`checkerboard_filter.py`のsource SHAを固定し、
\(u=2^{-53}\)、subnormal fallback \(h=2^{-1075}\)のpaired exact-target／forward-error intervalを
全input rounding、reduction、乗除算、実装定数へ伝播した。一段のstage positivityと、Q007s tubeへの
roundoff-robust re-entryは別判定である。

- classification:
  `binary64 one-step stages remain positive, but the registered Q007s tube is not certified roundoff-invariant`
- validity gates: `7 / 7` passed
- hypothesis gates: `5 / 6` passed
- one-step／robust-reentry outcome: `accepted / not_certified`
- equilibrium lower／maximum component error:
  `0.027777777759726004 / 7.154770604839416e-16`
- post-collision lower／maximum component error:
  `0.02777777771459676 / 1.2459169501537343e-15`
- post-filter lower／maximum component error:
  `0.027777777714596753 / 1.3501237168549712e-15`
- registered Wiener roundoff upper:
  `1.1666869562204168e-12`
- base／normal coordinate error upper:
  `1.7624955618306674e-12 / 3.490393265176959e-11`
- base／normal strict margin:
  `4.978918133501365e-22 / 9.145068981224883e-14`
- base／normal margin utilization:
  `3.539916734062091e9 / 381.6694299783683`
- runner SHA-256:
  `a0d3cea0fcae8a627f4a96db56d46727589411b2557e2aa91433569576a0575c`
- artifact newline-normalized SHA-256:
  `c4c1c45941a6f6ac302691efd8e795e431f6acc1fa4f4629cb0c7a0afac3c0a5`

従って、Q007s exact tube内のreal stateを正しくbinary64へ丸めた入力に対する一段のequilibrium／
collision／streaming／filter outputはstrict positiveである。しかし登録worst-case errorはbaseとnormalの
両re-entry marginを超えるため、この一段結論を同じtube上で全iterateへ帰納しない。これは実際のtube
escapeの反例ではなく、現certificateがroundoff-robust invarianceを示さないという否定的判定である。

### Q007w ideal binary precision threshold

Q007vのcomponent box、operation count、source SHA、DFT係数、analysis norm、strict marginを固定したまま、
total significand bits \(p=53,\ldots,128\)の76候補をexact ties-to-even arithmeticで全評価した。
\(p=53\)ではQ007vの全constant、population target/error record、stage summary、re-entry quantityを
exactに再現している。

- classification:
  `registered ideal binary precision threshold restores roundoff-robust Q007s tube re-entry`
- validity / hypothesis gates: `7 / 7`, `6 / 6` passed
- candidate／passing count: `76 / 44`
- selected sufficient precision: `85 significand bits`
- 84-bit Wiener error／base utilization:
  `5.360999559126826e-22 / 1.6266138872531641`
- 85-bit Wiener error／base utilization:
  `2.706739822688458e-22 / 0.8212685966874661`
- 85-bit base／normal coordinate error:
  `4.089029108522444e-22 / 8.097790411837928e-21`
- 85-bit normal margin utilization:
  `8.854816107415864e-8`
- candidate digest:
  `440a08dc36990d3e34edf1886fd7e47eacb4766c4a42352022897fd79dbb3ce2`
- runner SHA-256:
  `86dcc0a507e24216775650d5467d0ebf6e90eac0865190d0d5186e08afb7eac8`
- artifact newline-normalized SHA-256:
  `bac362d9dca4a681387b986a5f5802278ef61a1a3bcf1a0f8577c7f3ab0a07af`

従って、固定worst-case enclosureに対するideal binary arithmeticでは85 bitsが最初のsufficient
re-entry precisionであり、84 bitsではbase marginだけがfailする。これはnecessary thresholdではなく、
NumPy／MPFR／decimal／hardwareなどの実装済みbackend、正しいrounding mode、trajectory、性能を
認証しない。Q007vのbinary64 `not_certified`は変更しない。

### Q007x concrete MPFR-85 backend and fixed-leaf closure

`gmpy2==2.3.1`、`MPFR 4.2.2`、85 significand bits、nearest-even、
`emin=-1105`、`emax=1024`、gradual subnormalを固定した。4個のexact rational
fixed-leaf probeについて、constant construction、input encoding、collision、streaming、filterの
全primitive operationをexact dyadic ratioへ戻し、Q007wのinteger rounding oracleと照合した。

- classification:
  `MPFR-85 realizes the Q007w one-step arithmetic bound but not the fixed conservation leaf`
- validity / hypothesis gates: `8 / 8` passed、`2 / 6` passed
- trace: `70,824 / probe`、`283,296 total`、mismatch `0`
- all stage error-bound maximum utilization: `0.15250294804773457`
- operation semantics／one-step Q007w bound: `pass / pass`
- encoding／collision／streaming／filter exact conservation:
  `fail / fail / pass / fail`
- rounded-weight partition defect:
  `6.462348535570529e-27`
- rounded-filter partition-of-unity defect:
  `8.077935669463161e-27`
- rest-grid encoding／filter mass defect:
  `1.8676187267798828e-24 / 8.404284270509473e-24`
- probe／trace／result digest:
  `a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329` /
  `49ce9b304b4b6a07fdf7d7baed6c9118a97c5a08e489e3aa5eacde28662c2351` /
  `12cb83a87895d50523c909ad314b9ad155ac507af73e05f1b28cfb2a65328c7d`
- backend／runner SHA-256:
  `25ad43629e2487c5c062920cbb5319dac4e8fbded339dc856548bfab7f18a0dc` /
  `de16e86ab365e6e64b15fd62ebdb442a54e05d4e4e529ae1e018299983d7491b`
- artifact newline-normalized SHA-256:
  `20ba483c4c627de015673a2f8873cc020a5c1a43ee48c7715121a00330e13566`

従って、Q007wのideal 85-bit complement-coordinate error boundはconcrete MPFR backendへ接続できる。
しかしQ007sの定理はexact fixed mass／momentum leaf上の結果であり、componentwise encoding時点で
中心保存方向に非零誤差が生じる。finite probeはこの障害を検出する診断であり、保存補正なしに
Q007wのre-entryを全iterateへ帰納しない。Q007wのideal threshold、Q007uのexact stage positivity、
Q007sのexact fixed-leaf invarianceは変更しない。

### Q007y distributed dyadic conservation repair

Q007x backendを変更せず、componentwise encoding直後とpost-filter直後にglobal保存量補正を加えた。
対角population \(q=5,6,7,8\) の共通MPFR格子 \(h=2^{-90}\) 上で整数Hadamard系を解き、
各総unitを289 siteへrow-majorに均等配分する。補正前後をexact rationalへ戻し、全加算のexactness、
same-binade、positivityを検査した。

- classification:
  `distributed MPFR-85 repair restores the registered fixed-leaf probes but not the Q007w tube-wide base budget`
- validity / hypothesis gates: `8 / 8` passed、`5 / 7` passed
- repaired conservation: `input 4 / 4 exact`、`post-filter 4 / 4 exact`
- MPFR repair additions: `9,248 / 9,248 exact, same-binade, positive`
- maximum finite component-bound utilization: `0.15776531320758136`
- raw／repair／total Wiener error upper:
  `2.706739822688458e-22 / 4.959477689155467e-22 / 7.666217511843926e-22`
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

従って保存補正の有限実装とtube-wide algebraic定義は成功したが、Q007wの既存Wiener triangle boundへ
補正normを単純加算するだけではbase re-entryを認証できない。この否定結果は、repair後にexactに消える
global conserved center成分やbalanced配置のFourier phaseを利用していない。次はbackend／repairを固定し、
selected projectorへ直接通すprojector-aware error boundを別gateで評価する。

### Q007z selected-wave repair certificate

Q007pが封印するselected base waveは軸4点と対角4点の計8非零波数であり、\(k=0\)を含まない。
Q007yのbalanced distributionを\(n=289s+r\)と書くと、一様quotient \(s\) は各selected waveの
normalized DFTでexactに消える。prefixとcomplementのtriangle boundから、各対角populationの
selected-wave振幅はtotal unitに依存せず

\[
|\widehat c_q(k)|\le\frac{144}{289}2^{-90}
\]

となる。8 wavesと全289 remaindersをexact integer phase histogramで全走査し、Q007pの軸／対角
left-operator normを別々に適用した。

- classification:
  `selected-wave certificate closes the repaired MPFR-85 fixed-leaf tube induction`
- validity / hypothesis gates: `6 / 6` passed、`7 / 7` passed
- exact phase／balanced-distribution cases: `2,312 / 4,624`
- selected wave set: `2 C4 orbits / 8 nonzero waves / k=0 excluded`
- repair base-coordinate error upper: `1.9216710236250915e-26`
- raw／repaired base-coordinate error:
  `4.089029108522444e-22 / 4.0892212756248066e-22`
- base margin／headroom／utilization:
  `4.978918133501365e-22 / 8.896968578765586e-23 / 0.8213071928437413` (`pass`)
- unchanged normal utilization: `2.507922842743146e-7` (`pass`)
- selected／phase／result digest:
  `ea5d303e4333638447d70ef8ec6692599948260657e7cb51c133b8c3c5d20b90` /
  `f0da04edcc58edd6b96b2869ee67c79cc44b020278545bc52d03a142c0fa4a83` /
  `62262fe2cfb0bf361e5b79aaf89c8ba319ad1df046bf59aff56be8b7a54d4054`
- runner SHA-256:
  `0e2b3aebdc30d6a441178e3ac05fe417ab66673885a52ac9da801bd787dd8f79`
- artifact newline-normalized SHA-256:
  `b1ca382a76e874c18b804c7614ff8ad1ded3a5d0b9dda583facf6641b24f0c53`

これにより、`already encoded, repaired MPFR-85 state`が登録Q007s tube内にあることを初期条件として、
sampling timeのexact保存量、tube membership、equilibrium／collision／streaming／filter／repairの
strict positivityを全iterateへ帰納する。任意のexact stateの初期encodingやtrajectory shadowingは
別問題として残す。Q007yの`not_certified`は、意図的に粗いphysical-\(\ell^1\) estimatorの判定として
変更しない。

### Q007aa exact-state encoding initialization interior

Q007zの帰納は、すでにencoding／repair済みの状態がQ007s tube内にあることを仮定していた。
Q007aaではexact fixed-leaf state

\[
x=W(a)+Uz,\qquad
\|a\|_1\le r_0,\qquad \|z\|_*\le\zeta_0
\]

に対し、事前登録した

\[
r_0=8.9998\times10^{-19},\qquad
\zeta_0=4.999999999\times10^{-12}
\]

からcomponentwise MPFR-85 encodingとQ007y repairを行う。raw／repair physical Wiener errorに加え、
selected base shiftでgraph \(W(a)\) が移動する項も

\[
\epsilon_z=K_a\left(E_W+d_H(r)\epsilon_a\right)
\]

としてexact rationalで課金した。

- classification:
  `registered exact-state interior survives MPFR-85 encoding and repair`
- validity / hypothesis gates: `6 / 6` passed、`6 / 6` passed
- registered initial base／normal radii:
  `8.9998e-19 / 4.999999999e-12`
- raw／repair／total input Wiener upper:
  `7.470474908090484e-24 / 1.2452407101265335e-23 / 1.992288200935582e-23`
- raw／repair／total base increment:
  `1.1285528478805861e-23 / 1.9216710236250915e-26 / 1.1304745189042113e-23`
- base inward margin／headroom／utilization:
  `2e-23 / 8.69525481095789e-24 / 0.5652372594521056`
- \(d_H(r)\)／direct external／graph-shift／total normal increment:
  `1.0403913489904792e-16 / 5.96035575932445e-22 / 3.5186618281273335e-38 / 5.960355759324451e-22`
- normal inward margin／headroom／utilization:
  `1e-21 / 4.03964424067555e-22 / 0.596035575932445`
- tight base／normal initialization radii:
  `8.99988695254811e-19 / 4.999999999403964e-12`
- input／result digest:
  `71ca5b7b6ec65d0aee8e6486da73c4e532ce9e4721e8ae59edd7c664757fb8c7` /
  `9ccdfa40693489d0161521724c10f452626bb6066712ad6d0ba8c15d53fed5bc`
- runner SHA-256:
  `a7a6334fdb157ec317f65fca2475bf3b03775af88ea6d68eec2c02c5ba74188e`
- artifact newline-normalized SHA-256:
  `cf6a0566b91e9b034d2c93290302182fe8b4a0bf0f7e7bbbbb232f3d4a12ee64`

従って、上記exact coordinate interiorから開始すれば、initial encoding／repair後のbase／normal座標は
Q007s tubeへstrictに入り、その後はQ007zによりexact fixed leaf、tube membership、全MPFR stageの
positivityを全iterateへ帰納できる。任意のQ007s boundary stateやexact軌道とのshadowing精度は
まだ主張しない。

### Q007ab fixed-coordinate all-iterate forward shadowing

Q007aaのexact initial stateから始めるexact軌道と、その同じ状態をMPFR-85へencodingしてQ007y repairを
適用した軌道を比較する。graph-relative normal coordinateではなく、平衡点で固定した線形座標

\[
\mathcal Cx=(Lx,JQx),\qquad
\|\mathcal Cx\|_\oplus=\|Lx\|_1+\|JQx\|_*
\]

を用いた。Q007sのlinear／nonlinear majorantから

\[
L_\oplus
=\max(q_s,q_0)+(K_L+K_a)d_N(R_T)\max(c_V,K_s)
\]

をexact rationalで構成し、Q007aaのinitial defect \(d_0\)とQ007zのone-step local defect
\(\epsilon_{\rm step}\)に対して

\[
d_{n+1}\le L_\oplus d_n+\epsilon_{\rm step}
\]

を閉じた。

- classification:
  `fixed-coordinate contraction certifies all-iterate MPFR-85 forward shadowing`
- validity / hypothesis gates: `6 / 6` passed、`6 / 6` passed
- linear contraction／nonlinear Lipschitz increment／full Lipschitz upper:
  `0.9920954673554099 / 2.7528235726518938e-8 / 0.9920954948836456`
- contraction gap:
  `0.007904505116354432`
- initial／one-step coordinate error upper:
  `6.073403211214871e-22 / 2.3344049524038155e-20`
- uniform all-iterate coordinate／physical Wiener error upper:
  `2.9532588290365307e-18 / 8.529800645544777e-18`
- physical error／Q007s tube-state-radius ratio:
  `5.90651663221288e-7`（登録閾値 `1e-6` を通過）
- input／result digest:
  `83c98750b8a18aa98cae710fad0a4d2fa139428d791a085bdd086e39e435225f` /
  `268a5e2098011561c3bc521c845e6eb804692713502fbbd54c3b3106b8f9c014`
- runner SHA-256:
  `4958e1aa5140bdbd1a32ce074c77ce2739636a34f7da2531c792ec165401c01a`
- artifact newline-normalized SHA-256:
  `3770e53e5fd169ea8ba16a568a1a1a3052afdd95d2779ba630c7ba7113bdc7ae`

従って、Q007aaの登録interiorに属するexact stateごとに、同じ状態から初期化したsealed repaired
MPFR-85軌道のsampling-time forward errorは上の一様Wiener bound内に全iterateで留まる。これは
bi-infinite shadowing lemma、backward error、intermediate-stage距離、componentwise相対誤差、
任意のQ007s boundary initialization、他grid／MPFR buildの結果ではない。

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
python -m research.q007l_cubic_jet_bridge --output research/artifacts/q007l_cubic_jet_bridge.json
python -m research.q007m_quartic_jet_bridge --output research/artifacts/q007m_quartic_jet_bridge.json
python -m research.q007n_explicit_local_radius --output research/artifacts/q007n_explicit_local_radius.json
python -m research.q007o_external_complement_radius --output research/artifacts/q007o_external_complement_radius.json
python -m research.q007p_finite_tube_attraction --output research/artifacts/q007p_finite_tube_attraction.json
python -m research.q007q_population_positivity --output research/artifacts/q007q_population_positivity.json
python -m research.q007r_stagewise_positivity --output research/artifacts/q007r_stagewise_positivity.json
python -m research.q007s_finite_tube_enlargement --output research/artifacts/q007s_finite_tube_enlargement.json
python -m research.q007t_larger_tube_population_positivity --output research/artifacts/q007t_larger_tube_population_positivity.json
python -m research.q007u_larger_tube_stagewise_positivity --output research/artifacts/q007u_larger_tube_stagewise_positivity.json
python -m research.q007v_binary64_stage_enclosure --output research/artifacts/q007v_binary64_stage_enclosure.json
python -m research.q007w_ideal_precision_threshold --output research/artifacts/q007w_ideal_precision_threshold.json
python -m research.q007x_mpfr_fixed_leaf --output research/artifacts/q007x_mpfr_fixed_leaf.json
python -m research.q007y_distributed_conservation_repair --output research/artifacts/q007y_distributed_conservation_repair.json
python -m research.q007z_selected_wave_repair --output research/artifacts/q007z_selected_wave_repair.json
python -m research.q007aa_initialization_interior --output research/artifacts/q007aa_initialization_interior.json
python -m research.q007ab_forward_shadowing --output research/artifacts/q007ab_forward_shadowing.json
python -m research.q007ac_phase_aware_resolvent --output research/artifacts/q007ac_phase_aware_resolvent.json
python -m research.q007ad_asymmetric_phase_resolvent --output research/artifacts/q007ad_asymmetric_phase_resolvent.json
python -m research.q007ae_internal_phase_resolvent --output research/artifacts/q007ae_internal_phase_resolvent.json
python -m research.q007af_radius_step_obstruction --output research/artifacts/q007af_radius_step_obstruction.json
python -m research.q007ag_tube_radius_propagation --output research/artifacts/q007ag_tube_radius_propagation.json
python -m research.q007ah_propagated_tube_population_positivity --output research/artifacts/q007ah_propagated_tube_population_positivity.json
python -m research.q007ai_propagated_tube_stagewise_positivity --output research/artifacts/q007ai_propagated_tube_stagewise_positivity.json
python -m research.q007aj_propagated_tube_binary64_enclosure --output research/artifacts/q007aj_propagated_tube_binary64_enclosure.json
python -m research.q007ak_reentry_factor_audit --output research/artifacts/q007ak_reentry_factor_audit.json
python -m research.q007al_propagated_tube_mpfr85_bridge --output research/artifacts/q007al_propagated_tube_mpfr85_bridge.json
python -m research.q007am_propagated_tube_distributed_repair --output research/artifacts/q007am_propagated_tube_distributed_repair.json
python -m research.q007an_repaired_tube_induction --output research/artifacts/q007an_repaired_tube_induction.json
python -m research.q007ao_initialization_interior --output research/artifacts/q007ao_initialization_interior.json
python -m research.q007ap_forward_shadowing --output research/artifacts/q007ap_forward_shadowing.json
python -m research.q011a_periodic_forcing_compatibility --output research/artifacts/q011a_periodic_forcing_compatibility.json
python -m research.q011b_zero_mean_forced_fixed_point --output research/artifacts/q011b_zero_mean_forced_fixed_point.json
python -m research.q011c_forced_spectral_cluster --output research/artifacts/q011c_forced_spectral_cluster.json
python -m research.q011c1_endpoint_localization --output research/artifacts/q011c1_endpoint_localization.json
python -m research.q011c2_heldout_cluster_reissue --output research/artifacts/q011c2_heldout_cluster_reissue.json
python -m research.q011d_forced_quadratic_homological --output research/artifacts/q011d_forced_quadratic_homological.json
python -m research.q011e_forced_quadratic_chart --output research/artifacts/q011e_forced_quadratic_chart.json
python -m research.q011e1_enlarged_residual_window --output research/artifacts/q011e1_enlarged_residual_window.json
python -m research.q011f_multistep_shadowing --output research/artifacts/q011f_multistep_shadowing.json
python -m research.q011f1_heldout_amplitude_reissue --output research/artifacts/q011f1_heldout_amplitude_reissue.json
python -m research.q011g_forced_representation_audit --output research/artifacts/q011g_forced_representation_audit.json
python -m research.q011h_sparse_chart_equivalence --output research/artifacts/q011h_sparse_chart_equivalence.json
python -m research.q011i_exact_zero_mean_repair --output research/artifacts/q011i_exact_zero_mean_repair.json
python -m research.q011j_interval_fixed_point --output research/artifacts/q011j_interval_fixed_point.json
python -m research.q011k_interval_spectral_split --output research/artifacts/q011k_interval_spectral_split.json
python -m research.q011l_interval_homological_inverse --output research/artifacts/q011l_interval_homological_inverse.json
python -m research.q011m_quadratic_jet_majorant --output research/artifacts/q011m_quadratic_jet_majorant.json
python -m ttim_lbm --study q008a --output research/artifacts/q008a_tt_storage_prequalification.json
python -m ttim_lbm --study q008c --output research/artifacts/q008c_wave_qtt_prequalification.json
python -m research.q010_representation_cost --output research/artifacts/q010_representation_cost.json
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
- [`research/artifacts/q007l_cubic_jet_bridge.json`](research/artifacts/q007l_cubic_jet_bridge.json)
- [`research/artifacts/q007m_quartic_jet_bridge.json`](research/artifacts/q007m_quartic_jet_bridge.json)
- [`research/artifacts/q007n_explicit_local_radius.json`](research/artifacts/q007n_explicit_local_radius.json)
- [`research/artifacts/q007o_external_complement_radius.json`](research/artifacts/q007o_external_complement_radius.json)
- [`research/artifacts/q007p_finite_tube_attraction.json`](research/artifacts/q007p_finite_tube_attraction.json)
- [`research/artifacts/q007q_population_positivity.json`](research/artifacts/q007q_population_positivity.json)
- [`research/artifacts/q007r_stagewise_positivity.json`](research/artifacts/q007r_stagewise_positivity.json)
- [`research/artifacts/q007s_finite_tube_enlargement.json`](research/artifacts/q007s_finite_tube_enlargement.json)
- [`research/artifacts/q007t_larger_tube_population_positivity.json`](research/artifacts/q007t_larger_tube_population_positivity.json)
- [`research/artifacts/q007u_larger_tube_stagewise_positivity.json`](research/artifacts/q007u_larger_tube_stagewise_positivity.json)
- [`research/artifacts/q007v_binary64_stage_enclosure.json`](research/artifacts/q007v_binary64_stage_enclosure.json)
- [`research/artifacts/q007w_ideal_precision_threshold.json`](research/artifacts/q007w_ideal_precision_threshold.json)
- [`research/artifacts/q007x_mpfr_fixed_leaf.json`](research/artifacts/q007x_mpfr_fixed_leaf.json)
- [`research/artifacts/q007y_distributed_conservation_repair.json`](research/artifacts/q007y_distributed_conservation_repair.json)
- [`research/artifacts/q007z_selected_wave_repair.json`](research/artifacts/q007z_selected_wave_repair.json)
- [`research/artifacts/q007aa_initialization_interior.json`](research/artifacts/q007aa_initialization_interior.json)
- [`research/artifacts/q007ab_forward_shadowing.json`](research/artifacts/q007ab_forward_shadowing.json)
- [`research/artifacts/q007ac_phase_aware_resolvent.json`](research/artifacts/q007ac_phase_aware_resolvent.json)
- [`research/artifacts/q007ad_asymmetric_phase_resolvent.json`](research/artifacts/q007ad_asymmetric_phase_resolvent.json)
- [`research/artifacts/q007ae_internal_phase_resolvent.json`](research/artifacts/q007ae_internal_phase_resolvent.json)
- [`research/artifacts/q007af_radius_step_obstruction.json`](research/artifacts/q007af_radius_step_obstruction.json)
- [`research/artifacts/q007ag_tube_radius_propagation.json`](research/artifacts/q007ag_tube_radius_propagation.json)
- [`research/artifacts/q007ah_propagated_tube_population_positivity.json`](research/artifacts/q007ah_propagated_tube_population_positivity.json)
- [`research/artifacts/q007ai_propagated_tube_stagewise_positivity.json`](research/artifacts/q007ai_propagated_tube_stagewise_positivity.json)
- [`research/artifacts/q007aj_propagated_tube_binary64_enclosure.json`](research/artifacts/q007aj_propagated_tube_binary64_enclosure.json)
- [`research/artifacts/q007ak_reentry_factor_audit.json`](research/artifacts/q007ak_reentry_factor_audit.json)
- [`research/artifacts/q007al_propagated_tube_mpfr85_bridge.json`](research/artifacts/q007al_propagated_tube_mpfr85_bridge.json)
- [`research/artifacts/q007am_propagated_tube_distributed_repair.json`](research/artifacts/q007am_propagated_tube_distributed_repair.json)
- [`research/artifacts/q007an_repaired_tube_induction.json`](research/artifacts/q007an_repaired_tube_induction.json)
- [`research/artifacts/q007ao_initialization_interior.json`](research/artifacts/q007ao_initialization_interior.json)
- [`research/artifacts/q007ap_forward_shadowing.json`](research/artifacts/q007ap_forward_shadowing.json)
- [`research/artifacts/q011a_periodic_forcing_compatibility.json`](research/artifacts/q011a_periodic_forcing_compatibility.json)
- [`research/artifacts/q011b_zero_mean_forced_fixed_point.json`](research/artifacts/q011b_zero_mean_forced_fixed_point.json)
- [`research/artifacts/q011c_forced_spectral_cluster.json`](research/artifacts/q011c_forced_spectral_cluster.json)
- [`research/artifacts/q011c1_endpoint_localization.json`](research/artifacts/q011c1_endpoint_localization.json)
- [`research/artifacts/q011c2_heldout_cluster_reissue.json`](research/artifacts/q011c2_heldout_cluster_reissue.json)
- [`research/artifacts/q011d_forced_quadratic_homological.json`](research/artifacts/q011d_forced_quadratic_homological.json)
- [`research/artifacts/q011e_forced_quadratic_chart.json`](research/artifacts/q011e_forced_quadratic_chart.json)
- [`research/artifacts/q011e1_enlarged_residual_window.json`](research/artifacts/q011e1_enlarged_residual_window.json)
- [`research/artifacts/q011f_multistep_shadowing.json`](research/artifacts/q011f_multistep_shadowing.json)
- [`research/artifacts/q011f1_heldout_amplitude_reissue.json`](research/artifacts/q011f1_heldout_amplitude_reissue.json)
- [`research/artifacts/q011g_forced_representation_audit.json`](research/artifacts/q011g_forced_representation_audit.json)
- [`research/artifacts/q011h_sparse_chart_equivalence.json`](research/artifacts/q011h_sparse_chart_equivalence.json)
- [`research/artifacts/q011i_exact_zero_mean_repair.json`](research/artifacts/q011i_exact_zero_mean_repair.json)
- [`research/artifacts/q011j_interval_fixed_point.json`](research/artifacts/q011j_interval_fixed_point.json)
- [`research/artifacts/q011k_interval_spectral_split.json`](research/artifacts/q011k_interval_spectral_split.json)
- [`research/artifacts/q011l_interval_homological_inverse.json`](research/artifacts/q011l_interval_homological_inverse.json)
- [`research/artifacts/q011m_quadratic_jet_majorant.json`](research/artifacts/q011m_quadratic_jet_majorant.json)
- [`research/artifacts/q008a_tt_storage_prequalification.json`](research/artifacts/q008a_tt_storage_prequalification.json)
- [`research/artifacts/q008c_wave_qtt_prequalification.json`](research/artifacts/q008c_wave_qtt_prequalification.json)
- [`research/artifacts/q010_representation_cost.json`](research/artifacts/q010_representation_cost.json)

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
- Q007l exact cubic forcing／保存選択則、全2,600 graph-gauge homological systemの有理Krawczyk認証
- Q007m exact quartic forcing／保存選択則、全17,550 graph-gauge homological systemの有理Krawczyk認証
- Q007n Wiener \(\ell^1\) majorant、全次数homological inverse、quartic-centered explicit-radius収縮認証
- Q007o exact external-complement resolvent、旧119判定再現、explicit-radius upperの厳密改善
- Q007p 全289 blockのexternal-coordinate norm、有限tubeのforward invariance／normal contraction／domination認証
- Q007q Q007p tubeのexact Wiener bound、D2Q9 population／densityのfull-map時刻でのstrict positivity認証
- Q007r exact equilibrium／BGK／streaming／convex-filter stageの全iterate strict positivity認証
- Q007s 9×99 exact rational候補の全評価、base／normal両半径を拡大したregistered tubeの認証
- Q007t Q007s tubeのexact Wiener bound、full-map時刻でのpopulation／density strict positivity認証
- Q007u Q007s tubeのexact equilibrium／BGK／streaming／convex-filter stageでの全iterate strict positivity認証
- Q007v 現行binary64演算のpaired roundoff enclosure、一段stage positivity認証、robust re-entry棄却
- Q007w ideal binary 53--128 bit全候補、85-bit最小sufficient robust re-entry threshold認証
- Q007x concrete MPFR-85全演算trace／Fraction stage oracle、fixed-leaf closure棄却
- Q007y 対角dyadic保存補正のfinite／tube-wide定義認証、normal budget認証、base budget棄却
- Q007z balanced repairのselected-wave Fourier認証、条件付きMPFR-85 all-iterate tube帰納
- Q007aa exact-state coordinate interiorからMPFR-85 encoding／repair後のQ007s tube membership認証
- Q007ab fixed eigencoordinate contractionによるsame-initial MPFR-85 all-iterate forward-error認証
- Q007ac 全291万9730 modulus aggregate／287,929位相比較、登録nominal-disc条件とgap反例によるinvalid stop
- Q007ad original asymmetric 6 discs／287,929位相比較によるcritical external gapと`1e-16` analytic radius認証
- Q007ae selected-output 12 point centers／19,870位相比較によるinternal resolvent bottleneck除去
- Q007af `1e-15` inverse thresholdのexact bracketとsealed Q007ad witnessによる
  external-disc certificate family obstruction
- Q007ag Q007ae `1e-16` radius／correctionのQ007p majorantへの伝播、9×99候補上の
  base 100倍／normal 10倍tube認証
- Q007ah Q007ag tubeのexact Wiener bound、full-map時刻でのpopulation／density strict positivity認証
- Q007ai Q007ag tubeのexact equilibrium／BGK／streaming／convex-filter全iterate strict positivity認証
- Q007aj Q007ag tubeのcurrent binary64 paired enclosure、一段stage positivity認証、base／normal re-entry棄却
- Q007ak Q007aj re-entry failureの4因子分解、base／normal／joint ideal threshold `79 / 59 / 79`認証
- Q007al Q007ag tubeのconcrete MPFR-85全演算trace、一段stage／complement-error budget認証、
  fixed-leaf closure未認証
- Q007am Q007ag tubeのdistributed MPFR-85 fixed-leaf repair、tube-wide well-definedness、
  repair-aware base／normal一段budget認証
- Q007an Q007ag tubeのrepaired MPFR-85自己写像、fixed-leaf保存、全iterate stage positivityの
  条件付き数学的帰納
- Q007ao 登録strict inner exact-state setのMPFR-85 encoding／input repair後のQ007ag tube包含と
  Q007anへのinitialization接続
- Q007ap Q007ag tube上のfixed-coordinate収縮、initial／local defectの幾何級数合成、
  same-initial repaired-MPFR-85 all-iterate forward-error認証
- Q011a nonzero-mean periodic sourceのexact global momentum ledger、fixed-point obstruction、
  non-fixed rest reference-spectrum診断
- Q011b zero-mean single-wave periodic sourceのfixed-leaf Newton fixed point、全x-Fourier
  block spectrum、resolvent isolation診断
- Q011c 9-node force-amplitude pathのordered-Schur 24-mode cluster、Riesz／Sylvester／
  global normal-dominance診断、endpoint reproduction failureの局在化
- Q011c1 34 full SVD、共役orbit extrema、Frobenius--Weyl区間によるQ011c endpoint
  witness交換の摂動整合的局在化
- Q011c2 17-node cluster path、8 held-out midpointの24 Sylvester operator／全spectrum、
  共役orbit endpoint semanticsによるcandidate forced cluster選択
- Q011d forced endpointの300 quadratic external block完全SVD／direct solve、5 sectorの
  symmetric-product spectrumと20 nonnormal Sylvester probeによるoperator-family prequalification
- Q011e／Q011e1 forced fixed-leaf dense quadratic chart、analytic Hessian、homological residual、
  independent enlarged-window residual-order reissue
- Q011f／Q011f1 64-step forced-chart shadowing campaign、early-horizon解像失敗とheld-out-amplitude再発行
- Q011g natural Fourier-sparse baselineと6 uncapped TT-SVD bundleのfidelity／storage／timing比較
- Q011h dense／natural-sparse経路の64-step reduced-chart／checkpoint-defect同値性
- Q011i raw binary64 forcingのexact-dyadic obstruction、reflection-symmetric exact-zero-sum waveform、
  exact local／global moment source、Q011b fixed-point／spectrum numerical bridge
- Q011j exact affine fixed-leaf coordinate、exact rational map／Jacobian enclosure、
  dual-precision outward Krawczyk fixed-point existence／local-uniqueness proof
- Q011k contraction-derived exact-root enclosure、17-block dual-precision Bauer--Fike spectrum、
  rigorous 24／2574 selected-external split、300 quadratic-product spectral nonresonance
- Q011l exact eigencoordinate invariant graph、8 full-space overlap obstruction、unscaled symmetric-product
  perturbation、5-sector rigorous quadratic homological inverse bound
- Q008a degree 2／3／4 local Fourier係数、4 TT配置、sparse格納・忠実度・timing診断
- Q008c wave／branch・3-bit wave QTTの4配置、一般TT作用、格納・忠実度・timing診断
- Q010 固定8 TT-SVD候補の独立offline／online cost envelope、sparse-baseline break-even棄却
- 二次多項式チャートの output-block TT-SVD と sparse storage baselines

未実装・未通過:

- 連続最適化、Euclidean／grid-uniform normal attraction、global basin
- Q007afが排除していないwave-sum／blockwise／別norm external certificate、
  Q007ag新tubeのarbitrary boundary-state initialization
- repaired exact mapのquadratic jet／coefficientとQ011l inverseを合成したresidual majorant
- TT-cross（固定Q007c1／Q011g係数では保留）、forced SSM存在・一意性／normal-attraction認証、境界条件、
  Poiseuille／Couette、D3Q27

Q007iにより固定17² map・固定保存量葉に対する定性的な局所解析的不変多様体の存在と\(C^{90}\)一意性を、
Q007jにより登録数値eigencoordinatesと厳密selected subspaceの対応を、Q007kにより登録Q006i二次係数と
定理多様体のgraph-gauge quadratic jetの対応を、Q007lにより登録Q007b三次係数とgraph-gauge cubic jetの
対応を、Q007mにより登録Q007c1四次係数とgraph-gauge quartic jetの対応を認証した。Q007nでは同じ
定理多様体についてmodal radius`1e-75`のexplicit local existenceを認証し、Q007oではgapとmajorantを
変えずにexact external complementを使って`1e-18`へ改善した。Q007pではそのexact manifoldについて
\(r=10^{-19}\)、\(\zeta=10^{-20}\)の登録tubeをexternal-coordinate normで一様normal-attractingと認証した。
Q007qでは同じtubeをfull-map時刻でstrict positive population cone内に含むことを認証した。
Q007rではexact mapのequilibrium／collision／streaming／filter stageへ正値性を拡張した。
Q007sでは同じ解析的majorantを9×99有限格子へ適用し、\(r=9\times10^{-19}\)、
\(\zeta=5\times10^{-12}\)のregistered tubeへ拡大した。Q007tではそのtubeをfull-map時刻でstrict
positive population cone内に含むことを認証し、Q007uではexact equilibrium／collision／streaming／
filter各段階へ同じ結論を拡張した。Q007vでは現行binary64実装の一段stage positivityまで認証したが、
roundoff error upperがQ007sのbase／normal strict marginを超えるため、同じtube上の全iterateへは
帰納しない。Q007wでは同じenclosureをideal binary precisionへ拡張し、85 bitsを最小sufficient
thresholdと認証した。Q007xではfixed MPFR-85 backendの全演算がideal modelと一致し、一段stage errorが
Q007w bound内にあることを認証したが、componentwise encoding／collision／filterがexact fixed leafを
保たないためall-iterate invarianceは認証しない。Q007yでは対角dyadic repairがfinite probeと登録tubeの
algebraic条件でexact fixed leafを回復すること、およびnormal budgetを認証したが、粗いWiener triangle
boundのbase utilizationが2.326となるため、そのestimatorではall-iterate invarianceを認証しない。
Q007zではbalanced repairのuniform quotientが8 selected非零波数でexactに消えることを使い、
base utilizationを0.821307へ戻した。従って、repair済みMPFR-85 stateが登録tube内にあるという
初期条件のもとでall-iterate invarianceとstage positivityを認証する。Q007aaでは事前登録した
exact coordinate interiorからのinitial encoding／repairがその初期条件を満たすことを、
graph shiftを含むexact rational boundで認証した。Q007abでは固定線形eigencoordinate normで
exact mapのQ007s tube-wide contractionを認証し、initial／local MPFR defectからsame-initial
sampling-time forward errorを全iterateで一様に抑えた。Q007c1の有限振幅性能棄却とQ007dの
Euclidean棄却を変更せず、任意Q007s boundary state、bi-infinite shadowing、連続最適性、
grid-uniform性へは主張を広げない。
Q007agではQ007aeのanalytic radiusとcorrectionだけを同じmajorantへ伝播し、固定scaled grid上で
\(r=9\times10^{-17}\)、\(\zeta=5\times10^{-11}\)まで拡大した。ただしこの新tubeには
Q007t--Q007abのpositivity／有限精度結論を自動的には移していない。Q007ahでは新tubeを
full-map時刻のstrict positive population coneへ含め、Q007aiではexact内部stageへ拡張した。Q007ajでは
current binary64の一段stage positivityまで移したが、base／normal roundoff re-entryがともにfailするため、
all-iterate finite-precision結論はまだ移していない。Q007akではこの失敗を4因子へ分解し、同じideal
operation family内のjoint sufficient thresholdを79 bitsと決めた。Q007alでimplemented MPFR-85の一段
stage包囲とcomplement-coordinate誤差予算をnew tubeへ移し、Q007amでdistributed repairによる
fixed-leaf closureと修復込み一段予算も認証した。Q007anでは両結果をexact Q007ag invarianceと合成し、
already-repaired MPFR-85 stateを条件とするrepaired-map自己写像とall-iterate inductionを認証した。
Q007aoでは登録strict inner exact-state setからのcomponentwise encoding／input repairがその条件を
満たすことを認証した。Q007apでは固定線形eigencoordinate normの収縮を新tube上で再評価し、
Q007ao初期誤差とQ007am一段local defectを幾何級数へ合成した。従って登録inner exact-state setからの
same-initial sampling-time forward shadowingまで新tubeへ移した。arbitrary Q007ag boundary-state
initialization、bi-infinite shadowing、内部stage間距離、他grid／MPFR buildへは主張を広げない。
Q011aでは一様非零平均sourceのexact global momentum ledgerを閉じ、sinkのないperiodic mapでは
fixed pointが不可能と認証した。rest reference Jacobianはsource微分0によりunforced symbolと一致するが、
forced fixed-point stabilityとは解釈しない。Q011bでは零平均single-wave sourceへ切り替え、
固定保存量葉上のpositive fixed pointを二Newton startから同一解として解き、全x-Fourier fixed-leaf
spectrumが登録radius／resolvent gateを通ることを確認した。Q011cでは24-mode clusterの全raw
separation／normal-dominance診断が通ったが、continued endpointとQ011b artifactのcondition-number
再現差および共役witness交換によりvalidity 5/6、`inconclusive`となった。従ってforced clusterを
selectedとはまだ扱わない。Q011c1では全metric変化をJacobian perturbation区間で囲み、extremal
orbitが`{1,16}`のまま個別witnessだけ交換したことを認証したが、Q011cは再採点していない。
Q011c2では8 held-out midpointを含む別の再発行gateを通し、この有限範囲でcandidate forced spectral
clusterをselectedとした。Q011dではそのcanonical endpointにおける全300 quadratic external blockと
5 sector actionを通し、数値的external nonresonance／solvabilityをprequalifiedとした。実Hessian、
quadratic chart、residual orderはこの段階では未実装だった。Q011eでは実Hessianとdense quadratic chartを
構築し、全homological／構造gateを通したが、登録振幅窓のquadratic residualはnoise floor上に各方向1点
しかなく、residual order gateだけを棄却した。従ってforced dense chartは構築済みだが、三次残差次数、
normal attraction、不変多様体の存在・一意性、wall-bounded flowは未認証である。Q011e1では別seedの
32方向と16倍まで拡大した振幅窓で二次／三次残差を全方向に解像し、primary／secondary fitを全通過した。
ただし有限一段holdoutであり、Q011e自体の判定や上記未認証事項は変更しない。Q011fの64-step
campaignでは長時間性能gateを全て通したが、early horizonの2 fitがnoise floor上に3点しかなく、
eligibility gateだけを棄却した。Q011f1では未使用振幅`4.8e-4`だけを追加した独立再発行により
全224 fitを解像し、同じ有限multi-step shadowing gateを通過した。Q011fは棄却のままであり、
all-time shadowing、uniform remainder、basin、normal attraction、forced SSM存在・一意性は未認証である。
Q011gではforced (W_2/R_2)の6 TT-SVD bundleが全忠実度gateを通ったが、格納量でnatural
Fourier-sparseに勝つ候補は0だった。現在環境でonline時間に勝つ3候補は記録したもののjoint winnerはなく、
この固定係数に対するTT-SVD／TT-cross rolloutは停止する。
Q011hでは新規72初期値のdense／natural-sparse reduced trajectoryを別々に64 step更新し、
9,360 action、4,680 lifted state、576 checkpoint defectを全て登録閾値内で一致させた。
従ってnatural sparseをforced quadratic chartの実装baselineとするが、full-state 64-step orbit、
all-time equivalence、forced SSM存在・一意性、normal attractionは未認証である。
Q011iではQ011b raw waveform／sourceのexact dyadic global-momentum obstructionを再現し、登録した
reflection／ULP searchでexact-zero-sum waveformとexact local／global-moment sourceを構成した。
修復後の二Newton start、fixed point、17 block spectrumはQ011b numerical baselineとbitwise同一だった。
ただしraw mapとrepaired mapは数学的に別であり、Q011e--Q011h coefficientは移植していない。
Q011jではrepaired mapの150次元exact affine fixed-leaf residualを構成し、登録半径`1e-8`の
Krawczyk boxでfixed pointの存在と局所一意性を認証した。x-independent replicationによりfull 17²
periodic mapへも同じ結論を移した。Q011kではその収縮証明からexact rootを半径`1.13014e-15`へ絞り、
全2598 fixed-leaf eigenvalueのstrict stability、Q011c2-designated `24 / 2574` split、全300 selected
quadratic productのexternal spectral nonresonanceを認証した。nonnormal homological inverse、forced SSM、
normal attractionはこの段階では未認証だった。Q011lではQ011k eigencoordinate上のselected invariant graphを
Riccati contractionで認証し、8件のselected-overlap pairを除外せずexternal quotientへ移した。さらに
unscaled symmetric-product couplingを含む5 sectorのquadratic homological inverse normをexact rational
Neumann boundで認証した。Q011mではrepaired map自身のanalytic \(D^2/D^3\) を合成し、5 sectorのunique
graph-gauge quadratic jet、係数majorant、最大登録半径`1e-11`でのuniform cubic defectを認証した。
componentwise coefficient、exact invariant manifold／forced SSM、smoothness、normal attractionは未認証である。
