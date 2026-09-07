# Q012f1: 二次入力の実構造と三次solve精度の分離

## 2026-09-07 事前登録

Q012fは全三格子の計算と独立性検証を完了したが、33³/65³のH3共役対称性と65³の
272件のsolve残差を落とした。元結果`bd4514e`と全閾値を固定し、二つの原因候補を調べる。
同じ104実座標、26波数、奇数格子17³/33³/65³、四階filter付きmap
`omega=1.5, eta=.02, power=2`、固定保存量葉を保持する。

### 診断対象の固定

三格子共通のtriple集合を、次の和集合とその共役閉包で一意に決める。

1. 封印Q012fの65³で`passed=false`となった全272 ordinal。
2. Q012fの固定replay 16 ordinal。
3. 三格子のforcing/H3/R3共役診断の最大誤差monomialが属するblock triple。

共役写像は波数反転・acoustic±交換・shear平面保持から作る。各caseの選択理由と集合digestを
保存する。これは失敗機構の診断集合であり、全82,160 triple/格子の再検証とは呼ばない。
成功へ進む際には次の独立gateで全三格子・全三次係数を改めて検証する。

### 入力に関する二条件

全二次係数をfreshに再構築し、Q012fの12配列hashと三格子とも一致させる。
`raw`はこれを変更せず用いる。`paired`は別の診断入力であり、Taylor fiberに

```text
H2p = (H2 + J conjugate(H2))/2
G2p = (G2 + J conjugate(G2))/2
```

を適用する。Jは入力共役partnerと、G2の出力acoustic±交換を含む。
mapから得る二次forcing・linear frame・Lambdaは変更しない。元artifactを上書きしない。
paired入力のraw pair jet・実R2・評価器のcacheを同じfiberから再構築し、古いjetを流用しない。
共役投影の冪等性、partner involution、Fourier selection、元入力の不変性を検証する。
全3,081 pair/格子で元方程式に対する外部・full残差、固定葉・graph gaugeを再評価する。
診断入力を作れたことと、これらの数値基準を通ることは別に判定する。

### 同じ行列・右辺に対する三条件

- `svd`: 元のQ012fと同じ例外時のみ代替を持つSVD。元の数値不合格を保持する。
- `sylvester`: 同じ丸め済みA/D/Fに対する独立な構造化Sylvester solve。
- `refined`: Sylvester解から始め、128-bit MPCで`A X-X D+F`を評価し、
  その残差をfloat64 Sylvester法で解いて補正する。固定3回とし、通過した時だけ早期停止しない。

高精度化するのは丸め済み入力の残差積和であり、LBM symbolや固有空間そのものの厳密化ではない。
各回のfloat64／128-bit残差と補正normを保存する。元rank・condition基準は共通で、
外部相対残差`1e-10`、full-population相対残差`1e-9`、構造`5e-12`、
Taylor fiber-wise共役誤差`1e-8`を変更しない。元不収束時代替の結果と診断用solverを混同しない。

選択全triple×三格子×二入力×三solverを計算する。A/Dは両入力で同一hash、
同じ入力のFは三solverで同一hashであることを要求する。input effectとsolver effectを分け、
pairedによる右辺変更量・同solverの応答変更量、同入力のsolver間変更量を保存する。

### 独立検証

1. 既知の非対角複素解でSylvester法と補正を検証する。特異・悪条件の元rank gateを
   高精度残差だけで通さない。MP128/192で同じfloat入力の残差を比較する。
2. Q012fの元入力の選択全recordをfreshに再現し、元の失敗数と理由を一致させる。
3. raw/pairedそれぞれで全192,920 monomialの三次forcingを構築する。rawは封印配列hashと一致。
   各格子でQ012fと同じ8方向を独立物理式と比較し、相対誤差`1e-8`以下を要求する。
   H3 solveはこの独立forcingの生成に用いない。
4. 固定16 replay ordinalとその共役閉包を別プロセスで再計算する。全二次入力をfreshに構築し、
   各入力・solverの行列・forcing・解のhashと全数値診断を一致させる。全診断集合の再実行とは呼ばない。
5. このreplay集合のrefined解について128/192-bit残差の相対差を
   `norm(R128-R192)/max(1e-14,norm(F)) <= 1e-24`で確認する。
   これは区間包含や存在証明ではなく、より高精度での数値照合である。
6. 全選択行を保存し、件数・全判定・共役閉包・最大値を保存行から再集計する。

### 判定と次の問い

source/input seal、既知解、選択coverage、元record再現、独立forcing、有限性、
別プロセス照合、128/192-bit照合をvalidityとする。次を科学的仮説として別々に判定する。

- H1: raw入力のrefined solveが元65³の全272残差不合格を元基準内へ戻す。
- H2: raw/refinedでは33³/65³それぞれにH3共役不合格が残る一方、paired/refinedは
  元の最大誤差対を含む選択全共役fiberを通す。入力とsolverの必要性を区別する。
- H3: paired入力の全二次pairと、paired/refinedの選択全三次solve・実構造が元基準を通る。

validityが通り3仮説も通れば診断範囲でaccepted、validity通過で仮説不合格ならrejected、
validity不通過ならinconclusiveとする。個別armやgridの成功を総合成功へ読み替えない。
acceptedなら次はQ012f2で候補の全三格子・全三次係数を検証する。rejectedなら残った機構を
全失敗familyで調べ、単一ordinalごとの無期限監査へ細分化しない。Q012gは全数通過まで保留する。
三次評価器・有限振幅改善・SSM存在・grid-uniform半径・TT優位性はこの診断では認証しない。
