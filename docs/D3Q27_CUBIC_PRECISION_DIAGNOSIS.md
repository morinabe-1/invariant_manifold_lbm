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

## 2026-09-07 封印結果: passed / rejected

事前登録`cbbceca`の規則から共役閉包324 triple/格子を得た。三格子972 triple、
二入力×三solverの5,832 armをすべて計算した。validity10項目は通過したが、H1/H2/H3は
全て不合格だった。元Q012fと今回Q012f1の棄却を保持し、Q012f2の全三次再検証はまだ開始しない。

### 65³の全324組における比較

| 入力 | solver | solve不合格 | 最大float64外部残差 | 最大128-bit外部残差 | H3最大scaled共役誤差 |
|---|---|---:|---:|---:|---:|
| raw | SVD | 272 | 1.08311e-9 | 1.07727e-9 | 5.39076e-6 |
| paired | SVD | 270 | 1.07282e-9 | 1.07634e-9 | 5.39073e-6 |
| raw | Sylvester | 278 | 1.54150e-9 | 1.54942e-9 | 3.86831e-6 |
| paired | Sylvester | 278 | 1.55806e-9 | 1.55388e-9 | 3.86832e-6 |
| raw | refined | 20 | 1.33578e-10 | 3.24517e-11 | 3.32858e-8 |
| paired | refined | 17 | 1.16995e-10 | 3.07901e-11 | 8.80803e-11 |

外部残差上限は`1e-10`、共役誤差上限は`1e-8`のまま。solverをSylvesterへ置き換えるだけでは
十分でなく、128-bit残差を使う固定3回の補正でsolve誤差が大きく減った。
それでもrawの20件、pairedの17件は元float64残差gateを落とした。この37 armは32個の
異なるtripleに属し、全てshear/shear/shearである。refinedの全件がfull残差`1e-9`と
構造基準を通り、残ったsolve不合格は外部float64残差だけだった。
raw/refinedの20件は元272失敗に含まれるため、H1の「全件修復」は棄却する。

共役対称化だけではH3の大きい誤差はほぼ変わらない。精度補正後にはrawの`3.32858e-8`から
pairedの`8.80803e-11`へ減る。65³のこの診断では入力の実構造とsolve精度の双方が効いている。
ただし、その影響を全波数・全次数・別のmapへ一般化しない。

### 格子依存と仮説の棄却理由

17³/33³では両入力・全solverが選択全324組のsolve基準を通った。
17³のH3最大共役誤差はraw/refined `1.38091e-11`、paired/refined `5.06254e-13`。
33³ではraw/SVDの`7.88162e-8`がraw/refinedだけで`5.10031e-10`へ減り、基準を通った。
paired/refinedでは`3.48116e-12`だった。従って「raw/refinedでは33³/65³の両方で
共役不合格が残る」としたH2は棄却される。65³での入力誤差の影響まで否定した結果ではない。

paired入力の全9,243二次pairは元方程式・固定葉・graph gaugeを通った。
二次外部残差の最大値は17³/33³/65³で`4.32497e-13 / 2.94257e-12 / 2.27536e-11`。
H2の相対変更量は`4.68333e-13 / 6.18419e-12 / 1.02115e-10`で、元の入力配列は変更していない。
paired/refinedの共役gateも三格子で通ったが、65³の17 solve残差失敗があるためH3も棄却する。

### 独立性と残る数値上の問題

raw/paired×三格子の全1,157,520三次forcing monomialを構築した。rawの全配列hashはQ012fと一致。
各条件8方向、計48方向の独立物理forcing比較は全通過し、pairedの最大相対誤差は
17³/33³/65³で`3.99021e-15 / 1.01795e-14 / 2.80199e-14`だった。
raw/pairedでA/Dは同一、同一入力の三solverでFも同一であることを保存した。

別プロセスでは共役閉包32 triple/格子、計96 triple・576 armの全二次再構築・数値・配列hashが一致。
refinedの192件の128/192-bit残差照合も通過した。全972 tripleの別プロセス再実行ではない。
新規33・既存関連268テスト、ruff、compileallは通過した。

同じ丸め済みA/D/Fと同じrefined解を128-bitで再評価すると、65³の両入力・全324組の
外部残差が`1e-10`以内になる。これはfloat64残差の積和での打消しも影響する証拠だが、
128-bit数値照合だけで厳密な包含や真のLBM係数の誤差を認証したとはいわない。
元のfloat64 gateを事後的に128-bit判定へ置き換えて合格扱いしない。

### 次問 Q012f1a（未事前登録）

残差評価そのものの丸めと、保存した係数の真の方程式誤差を切り分ける。
65³の選択全324組・両入力のrefined解を固定し、そのfloat64行列・解を二進有理数へ
厳密に写して残差を計算する。37 arm／32 tripleの不合格を成功対とまとめて調べる。
必要なら残差normの二乗で比較し、平方根丸めや閾値緩和を避ける。
これは元mapの厳密symbolや非共鳴・SSM存在の認証とは区別する。
評価方法を修正する候補は別gateとして事前登録し、Q012f/Q012f1の元判定を保持する。
Q012f2の全三次preflightとQ012g評価器は、この診断を経るまで保留する。

### Seals

textはnewline-normalized SHA-256、gzipはraw byte SHA-256。

- helper: `1ab54c33c02be15cbe666d866fad2004d4aa2189bac97f381ea9f7bc9b82e1e0`
- runner: `89542c265eb476955a34708ecc0d6841bd0be8fbcb57b205fab5a626ce40819d`
- main artifact: `5bc0db745c8846196feec53bcbacddc069b8b257e5bcb89503b7b41e44c403a7`
- cycle digest: `2137462ad6c2a67c6310dfc428b9c92ae06db85129b23c2c21adae715206c5f1`
- selection digest: `bac3236df15f0e1f6128e3f75c742982777680696cffc0695ab1243dccf24c8b`
- replay artifact: `a8ebe503de90093706c41368e30afbc9d899f0f94b4c2b0b67891e19d24df960`
- replay evidence digest: `37c33c7559b81adadcee112512ab564376a89225a8737c009a1a714698dd7592`
- 17³ gzip (342,976 bytes): `26f31f9d756376a79e2c1c6da7da23f898089a139256aac24962ed3326093a08`
- 33³ gzip (348,764 bytes): `61deea7a7259134a4020cff70ef38cc995dc06e0d23548a023bc20f79135c255`
- 65³ gzip (362,274 bytes): `2ffe761a16ac5a23c2aaa6c6ad55eca65dbd2161a7016feef3aa13921bf8a806`

各324行の展開record digest:

- 17³: `70f0cb700febf23fa0385a847f644851b88e1087f41d16e93051b2e2924a4102`
- 33³: `f1f9aac49270a97fcdda75791fee3bc6966fd3409b8a4eccfd3d4c640e323033`
- 65³: `503d7fc69215cb5a11e8b8cb0d2361452d95678aeea3ba2bed0bd43017e94c03`
