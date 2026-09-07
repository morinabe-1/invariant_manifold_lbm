# Q012g: 封印した三次fiberの実座標W/R評価 — 事前登録 2026-09-07

Q012f2はcommit `284fb30`で全三格子・全246,480組のpreflightと保存後監査を完了した。
本問は、保存された三次Taylor係数を実座標のW/Rとして正しく評価でき、二次モデルに対して
欠陥次数と登録した有限振幅での1-step精度が改善するかを検証する。
存在定理や連続球の保証ではなく、candidate invariant manifoldの三次jetの数値検証である。

## 入力の封印と固定する範囲

- Q012f2 main normalized SHA256:
  `65a0046d2b54c1192a84fbce481da0e804364cf62566d2e9c18204e372158ec1`。
- scientific result digest:
  `ca64e1235a4dc94a4736bc051f9bbd780835a77d3ed0718bf886f93064c1ef7f`。
- 全source seal、11 validity gate、2仮説、全三格子のresult/record/fiber archiveのhash、
  全array metadata、972組の独立replayを照合する。元Q012f/Q012f1の棄却を保持する。
- 奇数格子`17³, 33³, 65³`、四階filter付きmap `omega=1.5, eta=.02, power=2`。
  無変更BGKや別filterへ変更しない。
- 26第一shell波数、二重shear平面を含む全104実座標、質量・3運動量固定葉を保持する。
  非零波数の候補をstrict centerと呼ばず、中心座標も追加しない。
- 二次入力はQ012f2と同じpaired H2/G2をfreshに再構築して全配列・全3,081 pairを照合する。
  三次は各格子の全192,920 Taylor columnを保存NPZから読む。三次solveの別の解へ交換しない。
- H3を再投影・共役平均・立方対称平均してから合格させない。sourceや旧artifactは編集しない。

## 評価する写像と表現

`z=T a`は封印した104×104の実座標化を用いる。104複素slotは共役制約を持ち、208独立実座標ではない。
FFTは`norm=ortho`、物理基底は`exp(i k.x)/sqrt(N³)`。以下のh/gは既にTaylor係数である。

\[
 W_2(a)=f_*+Va+h_2(a),\quad R_2(a)=\Lambda a+g_2(a),
\]
\[
 W_3(a)=W_2(a)+h_3(a),\quad R_3(a)=R_2(a)+g_3(a).
\]

`h3(a)`は全`i<=j<=k`の保存fiberに`z_i z_j z_k`を掛け、出力波数ごとに集約する。
追加の`1/6`や対称化multiplicityを掛けない。`g3`も同じ規約で、第一shellの出力slotへ集約してT*で戻す。
第一shell外のreduced fiberがexactにゼロであることを全件確認してから、その既知のゼロ支持を評価時に省略してよい。
小さい非零係数を閾値で落とすこと、TT近似、104⁴のdense real R3や巨大なphysical W3の生成は行わない。

自然Fourier sparse-fiberの集約評価を本体とし、別の正負波数の手動実座標化と直接単項式和を対照とする。
虚部は実場へ変換する前に測り、`||imag|| <= 1e-9 max(1,||real||)`を満たす場合だけreal部分を利用する。
違反を無条件のreal化で修復しない。保存係数のhash、支持、shape/dtypeと使用した配列を記録する。

## 既知の非自明な人工写像

4実座標aと3外部座標bについて、Bを次の二つの2×2 blockの直和とする。

```text
[[ .64, -.48], [ .48, .64]]    [[ .42, .56], [-.56, .42]]
```

複素安定固有対の絶対値は`.8, .7`。`S=diag(.2,.25,.3)`とし、zero-based添字で

```text
r2 = .01 * (a0*a1, a1*a2, a2*a3, a3*a0)
r3 = (.03*a0^3, -.02*a1*a2*a3, .01*a0^2*a2, .015*a0*a1*a3)
h2 = .02 * (a0*a1, a1*a2, a2*a3)
h3 = .01 * (a0^3 + 2*a0*a1*a2 - a1*a3^2,
             a0^2*a2 + a1*a2*a3, a2^3 - a0*a1^2)
Rstar(a) = B*a + r2(a) + r3(a)
h(a) = h2(a) + h3(a)
Wstar(a) = (a, h(a))
Phistar(a,b) = (Rstar(a), S*(b-h(a)) + h(Rstar(a)))
```

この写像の既知の不変graphを、明示的なreal多項式と共役複素slotのsparse評価で比較する。
seed `2026090723`の4次元正規乱数8単位方向、振幅`.1`で、W/Rと不変性欠陥を
`1e-12 max(1,||reference||)`以内に要求する。非自明なr2/r3を省略しない。
固定した評価点`a=(.08,-.06,.04,-.02)`でr3を省いた縮約、またはh3を2倍にしたgraphは、
それぞれ正しいPhistarに対して欠陥normが`1e-10`を超えなければ対照不成立とする。
一般の非対角homological solverの検証は既存Q012fの人工対照で保持し、本問は評価器を独立に検証する。

## 実LBMでの表現・構造・独立物理式

各格子で以下を行う。相対誤差の分母は特記がなければ`max(1e-14,||reference||)`。

1. seed `2026090723`の104次元Gaussian 8単位方向で、本体と独立単項式和のh3/g3を比較し、
   相対誤差`<=1e-10`を要求する。二次項も封印したpair-loop／real G2評価と同じ基準で照合する。
2. 同じ8方向と104座標軸で、三次項の`p(-a)=-p(a)`、`p(2a)=8p(a)`を
   `1e-12 max(1,||reference||)`以内で検証する。ゼロ、形の不正、非実入力、NaN/Inf、
   archive改変・欠落をunit testで確認し、黙って修正または補完しない。
3. 8方向のh3を物理場へ戻し、虚部、`L h3=0`のgraph gauge、4保存momentのzero-wave制約を確認する。
   gauge/momentは`<=1e-9 max(1,||h3||)`。zero waveを保存量の生成とは呼ばない。
4. 同じ8方向で、独立な物理空間微分から三次forcing F3を作り、保存forcingのcontractionと
   相対誤差`<=1e-8`で照合する。さらに
   `A h3(a) - h3(Lambda a) + F3(a) - V g3(a)=0`をF3 norm基準で`<=1e-9`と要求する。
   F3は二次Rとのcompositionを含む。これを単なるD³Phi(V,V,V)と混同しない。
5. seed `2026090726`の104次元4単位方向、全48立方対称操作でh3/g3の共変性を比較する。
   物理格子・populationの回転を独立対照とし、相対誤差`<=1e-8`を要求する。3格子で576比較。

## 欠陥次数と有限振幅

主たる欠陥は完全な非線形mapによる`D_d(a)=Phi(W_d(a))-W_d(R_d(a))`、`d=2,3`である。
係数方程式や方向微分だけからこの量を推定しない。両モデルは同じpaired二次項を共有する。
各モデル自身のWで欠陥を測るので、これは同一物理初期状態のtrajectory比較ではない。

- 次数: seed `2026090724`の64個の104次元Gaussian単位方向を固定し、全3格子で同じ方向を使う。
  `t=(.008,.004,.002,.001)`の全768 direction-amplitude caseで二次・三次の完全map欠陥を保存する。
- 全64方向/格子でlog-log傾きが二次`[2.9,3.1]`、三次`[3.9,4.1]`、
  最小振幅の三次/二次欠陥比が`<=.1`であることを要求する。
- fitに使う全欠陥が`100*eps*max(1,||f_*||2)`を超えることを要求する。
  generic方向を事後に除外しない。未解像があれば次数は未確定で、総合判定はinconclusiveとする。
- axis/face/body代表波数`(1,0,0),(1,1,0),(1,1,1)`の各8実座標軸、計24特殊方向も同じladderで保存する。
  3格子で288 case。退化方向のfloor以下の傾きはnullとし、次数の証拠にしない。genericと混ぜない。
- 有限振幅holdout: 独立seed `2026090725`の32単位方向、`t=(.008,.032)`、全3格子で192 case。
  各caseの三次/二次欠陥比`<=.5`を要求し、全caseでW、Phi(W)、W(R)がfiniteかつpopulation positiveであることを要求する。
  欠陥がfloor以下なら比を成功の証拠にせず未解像として残す。振幅や方向を事後に差し替えない。
- 有限振幅caseのWとW(R)の固定葉誤差、Phi(W)とWの保存量差を4成分別に計算する。
  site平均の最大絶対値`<=5e-13`を要求し、global sumの値も別に保存する。浮動小数点の厳密保存とは呼ばない。

振幅tは`||a||2=t`という縮約座標のEuclidean normである。Fourier基底はglobal-l2正規化だが、
非直交なspectral frameを含むため、tをそのまま`||W(a)-f_*||2`と同一視しない。
物理perturbation norm・最大局所密度偏差・最小populationも保存する。
Q012eの17³・二次モデルの有限sample受理を、三次モデルや33³/65³へ流用しない。
この1-step検証は長時間shadowing、任意初期状態の縮約、連続球の使用半径を認証しない。

## 費用、独立再現、保存

格子と方向を逐次処理し、全方向の巨大physical fieldを同時に保持しない。
全caseのmetrics、比較fieldのhash、共役/実変換誤差、失敗index、全timing sampleを保存する。
保存入力を上書きしない。新しいhelper/runnerは実装検証後に固定し、実験途中で編集しない。

費用は記述的測定で、合格条件にはしない。seed `2026090727`の8単位方向・振幅`.008`を用い、
W2/W3のphysical再構成、R2/R3の実縮約1-step、Phi(W3(a))のfull-map 1-stepを別々に測る。
各格子・各methodを3回warmup後、8方向を11巡し、巡回ごとにmethod順を正順/逆順へ交替する。
全raw wall sampleと中央値を保存し、hash/normの検証費はtimed callの外に置く。
入力再構築・NPZ読み込み・評価器準備のoffline時間、coefficientsとsparse indexのメモリbytes、
serialized bytesを分離する。TT core格納スカラー数や独立自由度の数とは呼ばない。
TTとの比較はまだ行わず、自然Fourier sparseを必須baselineとして後続へ渡す。

別processは全二次入力をfreshに再構築し、同じ封印三次fiberから、各格子の最初の8次数方向×4振幅と
最初の8有限振幅方向×2振幅を再計算する。計144 caseについて二次/三次の全数値・field hashを一致させる。
これは全caseや全三次solveの独立再実行ではない。再現workerと主計算のphysical campaignは同時実行しない。
time、PID、出力名の一致は数値再現の条件にせず、sourceと科学的recordを一致させる。

## 判定と次の行動

封印入力、人工写像の正しい評価と負の対照、全登録coverage、finiteな保存証拠、読み戻し、
144 caseの独立再現をvalidityとする。未実行やNaNをゼロで埋めて通過させない。

- H1: 三格子の独立評価・realification・homogeneity・graph gauge/固定葉が通る。
- H2: 全48立方操作の共変性が通る。
- H3: 全三格子の独立物理forcingと三次homological identityが通る。
- H4: 全generic方向の次数`3 → 4`と最小振幅の欠陥比が通る。
- H5: 登録した有限振幅holdout全192 caseで欠陥半減・正値・保存の基準が通る。

validityまたはgeneric/holdoutの解像性が不十分ならinconclusive、validityと解像性が通り仮説不合格ならrejected、
全て通過ならacceptedとする。依存する評価を安全に実行できない場合は未実行範囲と原因を明記する。
個別の構造・次数・性能の成否を保持し、一つの失敗を隠すために総合成功へ読み替えない。
受理後は共通初期状態からの三次縮約trajectoryと使用領域を次問とし、存在認証とTT費用優位性は別に残す。
棄却なら失敗family/方向と次数別項を分析し、閾値や旧結果を上書きせず次の実験を登録する。

実装予定: `research/d3q27_cubic_chart.py`、`research/q012g_d3q27_cubic_chart.py`。
本書のcommit前には新規評価器や未登録の振幅探索を実行しない。

## 実装・事前検証 2026-09-07

事前登録commit `b5f5543`の後、上記二つのmoduleを実装した。登録条件に変更はない。
実験開始前に固定するnormalized SHA256は次の通り。

- `d3q27_cubic_chart.py`: `e830cb88bf48b05adac868e7ca71ad5576d3f7f9cf1eb451a9475e452b7ddc37`
- `q012g_d3q27_cubic_chart.py`: `01c114dce30d7793729c8ae2563bc57d6ae41b3101a0c9295d689fec7be68ff3`

新規90テストと既存Q012f2実装31テスト、計121件が通過した（172.49秒）。
人工写像の8方向は最大不変性欠陥`2.866236503153378e-17`。
R3省略対照の欠陥`1.5667750445071706e-5`、H3倍掛け対照の欠陥`4.873334711633402e-6`で、両方成立した。
全104軸の合成fiberの次数・実座標化、入力異常、archiveの破損／欠落、再現行の改変、未解像の判定をテストした。
特殊方向ラベルの保存前後の型不一致を修正してから全テストを再実行した。Ruff、format、compileallも通過した。
全三格子の実archiveはshape・全支持・全array hashとbyte sealを確認したが、この読込み試験は実LBMの評価結果ではない。
旧11 validity／2仮説、source chain、全972組の保存replayも変更なしと照合した。

実行順（別process、同時実行しない）:

```powershell
python -m research.q012g_d3q27_cubic_chart --worker-output research/artifacts/q012g_d3q27_cubic_chart_replay.json
python -m research.q012g_d3q27_cubic_chart --output research/artifacts/q012g_d3q27_cubic_chart.json --replay research/artifacts/q012g_d3q27_cubic_chart_replay.json
```

各実行は格子ごとのJSONも保存し、全内容を読戻して照合する。既存の全結果・部分結果は上書きしない。
全fieldを保存するのではなく、登録した全metricsと比較fieldのshape/dtype/byte/hashを保存する。
caseまたは診断phaseで例外が出た場合は失敗位置・得られた有限の部分recordを保持し、欠落を合格扱いしない。
格子JSONの読戻し成否は親resultの`roundtrip_passed`にも付記するため、その付記だけは子JSONの中には含まれない。
実LBMの三次次数、有限振幅での改善、対称性・物理三次式の本検証はまだ未実行であり、Q012gは未判定である。

## 独立workerの完了・主計算の開始 2026-09-07

commit `0e682d7`で実装を固定後、独立workerが三格子×48 caseを完了した（PID 33368、exit 0）。
helper/runnerのsealは上記と同一で、全144 caseはfiniteかつ登録floor以上に解像した。
保存後の10テスト（35.35秒）が全行・全4保存量成分・比・正値・解像性・全metadataを検証した。
これで主計算によるfreshな144 caseの一致が証明されたとはしない。以下は各格子の登録方向の一部の結果である。

| 格子 | 次数gate（最初の8方向） | 有限振幅の総合gate | holdoutの最大三次/二次欠陥比 |
|---|---|---|---|
| 17³ | 8/8 | 16/16 | 0.3478045642 |
| 33³ | 8/8 | 8/16 | 1.087274049 |
| 65³ | 8/8 | 0/16 | 5.166501261 |

33³は`.032`の全8方向が半減基準不達で、うち3方向は二次より悪化した。
65³は半減基準不達15/16、保存量数値gate不達16/16で、`.032`の全8方向が二次より悪化した。
holdout全48 caseは正値だが、それだけで他の失敗を打ち消さない。
全144 caseのsite平均保存量誤差最大`5.445078958095503e-13`は上限`5e-13`を超えた。
この超過に対する丸めと他の誤差の寄与は未診断である。欠陥比不達と区別し、元の数値・判定を保持する。

worker normalized SHA256:
`84e4d6f9ce241b0eab4a6eda380dbf242a83c084e4fc4bc872291bb48ef56891`。
evidence digest:
`677211d3055d0bce7b1a0f6bf16e28280ea2302a1c13c270a30f329ffac13085`。
格子JSONのnormalized SHA256は17³ `74dfdf7a9d427e6f2c9ae7316572eaf1dcc3c3cfa1e38ac098b2bd59a188bb02`、
33³ `a0af8cf77012646a1bcf5ba0d208c030b1eb0880152291f1c4b9f01fd32aa1e4`、
65³ `767134aba2402bc6e7d776a0b7914bf36c57201663431768d6f4d2019d236801`。

主計算を2026-09-07 22:00:47 JSTに開始した（PID 29360、handle 89608）。
全登録方向・48対称操作・物理三次式・費用とworkerの再現照合はまだ進行中である。
H5には既に反例があるが、未完了のvalidityや解像性を仮定して総合判定を先取りしない。
sourceを変えず、現在のhandle／processを確認しながら全登録範囲を完了する。
