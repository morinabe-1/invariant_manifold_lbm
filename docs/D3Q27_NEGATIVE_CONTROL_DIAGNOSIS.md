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
