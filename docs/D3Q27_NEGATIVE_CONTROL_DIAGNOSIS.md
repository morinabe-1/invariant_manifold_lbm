# Q012d1: R2なし対照の有限振幅診断 — 事前登録 2026-09-07

前turnはQ012dの全係数・実験・監査・commitまで完了し、次の診断を決める証拠を得たので
progressである。Q012dはvalidity全通過、R2なし対照の4/8方向だけが傾き上限2.1を超えた。
本問では、これは二次係数の誤りではなく有限振幅での三次以上の寄与かを検証する。
元の`passed / rejected`、振幅、閾値、失敗方向`0,2,4,5`を変更しない。

## 固定入力

- Q012d manifest SHA: `d33ca861d7b51096e09de93550e24d33f0722fc12ac531ff591f56383dd4fea8`
- result digest: `c3d24a465f6d2f1050137c5bc5d4c3e91d5ebb1432a0cfbd72321f297edfa7a0`
- NPZ binary SHA: `0877235be7ec1619c0fcd3e982cb1863bee3fb13a62bd68f082f13e59d1b0d8d`

全source seal、8 validity、7通過hypothesisと唯一の負の対照失敗、全12 NPZ配列を照合する。
Q012dのinput checkerも実行する。17³、omega=1.5、eta=.02、p=2、固定4保存量葉、
26波数・104実座標のまま、全3,081 pairからchartを再構築しNPZのarray hashと一致させる。
先行helper／runner／artifactは変更しない。基礎理論・全先行trajectoryを再実行したとは呼ばない。

## 独立な次数別予測

`W2(a)=f*+Va+H[a,a]/2`、`q(a)=G[a,a]/2`とする。方向uについて
`v=Vu`、`h=H[u,u]/2`、`l=Lambda u`を固定する。

\[
 D_{drop}(a)=\Phi(W_2(a))-W_2(\Lambda a),\qquad
 D_{full}(a)=\Phi(W_2(a))-W_2(\Lambda a+q(a)).
\]

厳密な二次chart compositionの代数は

\[
 D_{drop}(a)=D_{full}(a)+Vq(a)+H[\Lambda a,q(a)]+\tfrac12H[q(a),q(a)].
\]

この恒等式だけでは原因を確定しない。別に、full-map equilibriumの局所式を展開する。
`rho=1+t r+t²s`、`j=t j1+t²j2`として、`r,j1=Mv`、`s,j2=Mh`を用いる。
populationごとに`Q(x,y)=w[4.5(c.x)(c.y)-1.5 x.y]`と置くと、collisionの次数3・4係数は

\[
 C_{3,local}=\omega\{2Q(j_1,j_2)-rQ(j_1,j_1)\},
\]
\[
 C_{4,local}=\omega\{Q(j_2,j_2)-2rQ(j_1,j_2)+(r^2-s)Q(j_1,j_1)\}.
\]

streamと同じ四階filterを適用したものをC3、C4とする。C2は`Vq(u)`であり、
独立な`Ah+B(v,v)/2-H[l,l]/2`とも照合する。
C3はさらに`B(v,h)+D³Phi[v,v,v]/6`と照合する。第三微分項ではrhoとequilibrium Hessianを
**streamより前**に掛ける。stream後のrhoを誤って掛けない。
次数予測`Pj(t)=t²C2+...+t^j Cj`の係数を実測欠陥へfitしない。

## 登録sampleと基準

- 既知8方向：Q012dのseed2026090711の最初の8本。成功4本も含め、元4振幅を全再計算する。
- 独立32方向：seed`2026090716`、Gaussian104座標をl2 norm=1へ正規化する。
- 元のwindow：`(.008,.004,.002,.001)`。
- 新しい漸近診断window：`(.001,.0005,.00025,.000125)`。元判定の置換ではない。
- unionの7振幅×正負2符号×全40方向、計560 signed full-grid sample。
- roundoff floorは元と同じ`100 eps max(1,||f*||2)`。欠陥がfloor以下ならその傾きを
  証拠にせずnullとし、登録した新windowのraw対照で生じれば診断をinconclusiveにする。
  新windowで本体の三次欠陥がfloorに入っても、その傾きを判定対象にしていない。

以下を別gateにする。

1. 既知8方向の元positive振幅のlinear／quadratic／R2なし欠陥・傾き・全判定がQ012dと一致する。
2. 全40方向でC2の独立physical equation relative誤差`<=1e-9`、C3の独立微分式誤差`<=1e-10`、
   C2 norm`>1e-6`。係数がゼロという説明を採らない。
3. 全560 sampleで上記composition恒等式のabsolute誤差`<=roundoff floor`。
4. 元windowの全40方向・正負について、P3のvector-relative誤差`<=.02`、P4は`<=.001`。
   positiveの元8方向で、P3／P4のnorm傾きと実測傾きの差はそれぞれ`<=.01 / .001`、
   両予測が元の失敗4方向を再現する。normだけでなくsigned vector誤差を要求する。
5. 正負のodd part`(D(tu)-D(-tu))/2`をt³で割りC3と比較する。元windowの全160点で
   relative誤差`<=.001`、odd defectはfloorより大きいことを要求する。
6. 新windowの全40方向・正負80本のraw対照傾きが`[1.9,2.1]`、全sampleがfloorより大きいこと。
   最小振幅で`D(tu)/t²`とC2のrelative差`<=.05`を要求する。
7. 全560 sampleのW(a)、Phi(W(a))、W(Lambda a)、W(R(a))がfinite・population positive。
   これは有限sampleだけの確認であり、ballや長時間trajectoryの正値保証ではない。

even part、C2/C3/C4のGram matrix、C3とC2の比・角度、P4のP3に対する改善は診断値として保存し、
事後にgateを追加しない。C2/C3/C4およびcomposition各termのnormとGram matrixを保存し、
元windowの傾き増大を予測項のベクトル干渉まで追えるようにする。

## 判定・保存・独立再実行

入力、40方向×7振幅×2符号のcoverage、有限な証拠、全係数再構築、実験全体の独立再実行digest一致を
validityとする。別プロセスかつfresh chartで40方向の全診断を再実行し、timeなどを除く
科学的cycle digestを比較する。元Q012dの全trajectory再実行ではない。
新windowのraw対照が未解像ならinconclusive、validity不通過もinconclusive、
validity通過かつ上記hypothesis gate失敗ならrejected、全通過なら有限振幅診断としてaccepted。

helper: `research/d3q27_negative_control.py`。
runner: `research/q012d1_d3q27_negative_control.py`。
manifest: `research/artifacts/q012d1_d3q27_negative_control.json`。
全方向・振幅・符号のnorm／Gram／相対誤差とsource sealをJSONへ保存する。
大きなfull-fieldベクトルを全保存する代わりに、固定入力chartと独立全数replayで再現性を確保する。
元chartの全係数NPZは引き続き参照し、新しいTT表現や係数修正を作らない。

通過すればQ012dの棄却を保持したまま、係数修正を要さない有限振幅の対照設計問題として
次の実用振幅・高次／存在認証の差の評価に進める。3DのSSM存在、半径、normal attraction、
grid-uniform性、TT優位性をこの診断の成功条件へ混ぜない。失敗なら該当termを次に調べる。

## 結果 — 2026-09-07

事前登録commitは`7fd705a`。別々のプロセスでfresh chartから560 signed sampleを
それぞれ計算し、科学的experiment全体のdigestが完全一致した。validity全5項目は通過。
ただし、三次予測P3のvector-relative誤差が登録上限2%を超えたため、
Q012d1は`passed / rejected`で固定する。元Q012dも引き続き`passed / rejected`である。

| 検証項目 | 全登録sampleでの結果 | 判定 |
|---|---|---|
| 元8方向の再現 | linear／quadratic／R2なしの元記録、傾き、4失敗方向が全て一致 | 通過 |
| 独立C2／C3 | C2 equation誤差1.61079e-12、C3 derivative式誤差1.92378e-16、最小C2 norm0.00322148 | 通過 |
| chart composition恒等式 | 最大absolute誤差1.92851e-15、floor5.50261e-13 | 通過 |
| 元windowのP3 vector予測 | 最大0.0337647。元window320 signed sample中40点が0.02を超過 | **失敗** |
| 元windowのP4 vector予測 | 最大7.09458e-6、失敗0（上限0.001） | 通過 |
| 元8方向の傾き予測 | P3／P4の最大傾き差0.000480387／2.53949e-7、両者とも元4失敗方向を再現 | 通過 |
| odd partによるC3照合 | 全160点、最大relative誤差1.60817e-5、最小odd norm2.23673e-10 | 通過 |
| 新windowの二次挙動 | 全40方向×正負80本、傾き2.00037857–2.00296911、最小振幅のleading vector差最大0.0141253 | 通過 |
| 有限sampleの正値 | 最小population0.00461236、finite失敗0 | 通過 |

登録hypothesis第4項はP3・P4のvector予測と元傾き再現の**連言**である。
表では内訳を分離したが、第4項全体の失敗を他の通過で取り消さない。
P3失敗は既知5方向・holdout15方向の正負、全て振幅0.008で発生した。
元Q012dで傾きが失敗した4方向とは判定対象も集合も異なる。
最小raw対照欠陥は5.03343e-11で、全てfloorを上回った。新windowでの二次挙動は
元windowの傾き条件を置き換えたものではない。

### 何が説明でき、何が棄却されたか

二次係数が消失していたのではない。全40方向でC2≠0を独立なphysical equationと照合し、
小振幅でD_drop/t²がそのC2へ近づくことを確認した。
C3/C2 norm比は43.5641–113.001であり、振幅0.008では三次寄与を無視できない。
C2・C3のcosineは-0.0132469–0.00976782と小さく、normの増大には両ベクトルの
二乗和が効く。例えば既知方向0ではC3/C2比97.9607、cosine0.00284477、
振幅0.008で三次termのnormが二次termの約0.784倍となる。
傾きの観測値へfitせずに作ったP3だけで、元の傾き上限超過を再現できた。

一方、normの傾き再現はvector自体の高精度な再現を保証しない。
四次寄与を省いたP3は2%のvector誤差条件を落としたが、元windowのP4は全点で通過した。
振幅0.008でP4／P3のvector誤差比は0.000152118–0.000271375であり、
P3から残った誤差は四次termの追加で大幅に減った。これは診断値であり、
事後に追加した受理条件ではない。

ここでC4は**二次Wを非線形mapへ入れた際の方向別の次数4寄与**である。
3Dの四次W/Rや、全104変数の四次多様体係数を構築したわけではない。
今回の証拠は元対照の傾きが有限振幅の高次寄与で説明できることを支持するが、
登録した「P3だけで元window全点2%以内」という強い予測仮説は棄却する。
W/R・map・波数集合・閾値の変更は行っていない。

### 次の主問Q012e

次はP3の閾値を緩める再試行ではなく、必要と判明した四次寄与と残りの有理式termから、
同じ二次chartの実用振幅と高次化の必要性を評価する。
局所非線形項の次数2–4係数をa2,a3,a4、densityを1+rt+st²とすれば、
次数4までを引いた残りは代数的に

\[
 -\frac{t^5\{r a_4+s a_3+t s a_4\}}{1+rt+st^2}
\]

と書ける。この式にstream／filterを適用し、coefficient equationと浮動小数点の誤差を
分離して扱うことが次問の候補である。まだ新しい実用振幅や有効半径を認証していない。
Q012eの基準は別途登録し、単に二次の傾きが見える小領域へ目標を縮めない。
自然Fourier sparse baselineは引き続き必須とし、TT費用評価はこの診断・誤差評価と区別する。

### 保存・検証

全40方向、560 signed sample、280 parity record、係数／compositionのGram matrix、
fitに用いた全norm、符号、元失敗記録を保存した。2プロセスで各々全係数を再構築し、
全数実験のdigest一致を確認した。これは元Q012dの48 trajectoryを再実行したことを意味しない。
新規17テストは全保存記録の再監査、既知1方向とholdout1方向のfresh再実行を含む。
既存関連190テスト、ruff・format check・compileallも通過した。

- manifest SHA: `812cda7e30678029b91f2a2a56f1ec2cc8cad73ba170d42c3c805769f15c5190`
- cycle digest: `a78e8e61b7a5bd185ab579ae4ecc032154229b627a070c18e90a3494ee363075`
- 共通experiment digest: `2a5335ff8462fc04b808b861c13368763f662ab48d089351e1c5d4e820ae129b`
- 独立worker SHA: `ec12a947dfdc34082050b60a32328bafec175ea22ee0f799e8ac846d88519e84`
- helper SHA: `52ba33bbded0dc7b068b26f65181eb3be941beaafcf22bd9db941d23a7226794`
- runner SHA: `878c8d4866a632de7041af62560be8837bc5e34ce08c78f0d15953fad2e25aee`

再実行は同じプロセス内で呼ばず、次の2コマンドで別プロセスを使う。
既存の出力先は上書きしないので、再実行ごとに未使用のパスを選ぶ。

```powershell
python -m pytest tests/test_d3q27_negative_control.py tests/test_d3q27_negative_control_artifact.py -q
python -m research.q012d1_d3q27_negative_control --worker-output research/replays/q012d1_worker.json
python -m research.q012d1_d3q27_negative_control --output research/replays/q012d1_diagnosis.json --replay research/replays/q012d1_worker.json
```
