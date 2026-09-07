# Q012f: 全104座標の三次homological preflight

## 2026-09-07 事前登録

Q012eで最初に不合格となった振幅.128は、絶対精度・正値性ではなく、同一初期線形化に
対する半減基準を30/32 caseで落とした。そこで全104座標の三次方程式を調べる。
Q012d/Q012d1の棄却とQ012eの限定的受理を保持し、振幅閾値や二次係数を変更しない。
このpreflightの成功は、三次chartの有限振幅改善やSSM存在を保証しない。

### 範囲と入力

- 四階filter付き修正map `omega=1.5, eta=.02, power=2` を固定。
- 奇数格子 `17³, 33³, 65³`、全26第一shell波数・104実座標を保持。
- 各格子で同じ方法により全二次W2/R2をfreshに再構築する。17³は封印済み12配列と
  全hash一致を要求し、33³/65³では元二次solve基準・coverage・paired frameを再検証する。
- 全質量・3運動量を固定。zero-wave外部空間は23次元kinetic部分空間。
- 78個の入力block（各波数でshear平面2次元、acoustic±各1次元）から、
  各格子82,160 unordered block triple、192,920対称monomial columnを評価する。
  三格子で246,480 triple、578,760 column。内部shear固有ベクトルへ分裂させない。

### 三次右辺と正規化

`W(a)=f*+Va+H[a,a]/2`, `R(a)=Lambda a+G[a,a]/2` と書く。
H/Gは既存二次Taylor配列をraw対称二次微分へ戻したものとする。
三次のraw forcingは

```text
F3[u,v,w] = B[Vu,H[v,w]] + B[Vv,H[u,w]] + B[Vw,H[u,v]]
            + C[Vu,Vv,Vw]
            - H[Lambda u,G[v,w]] - H[Lambda v,G[u,w]] - H[Lambda w,G[u,v]]
```

とする。`B=D²Phi`, `C=D³Phi`。局所equilibriumの非線形部分を
`Q(j,j)/rho` とすると、Cのlocal部分は
`-2*(r_u Q(j_v,j_w)+r_v Q(j_u,j_w)+r_w Q(j_u,j_v))` である。
omega倍・streaming・filterは局所微分項の後に作用させる。
H/Gとのcomposition項に余分なstreamingやfilterを重ねない。
orthonormal FFTのためB(V,H)の積には`N^(-3/2)`、3つの線形場の積には`N^(-3)`を含める。
HとG自体に既に含まれる`N^(-3/2)`を二重計上しない。

3 blockが異なる場合はKronecker積、同一blockが2つならそのSym²、3つならSym³へ
直交基底Sで制限する。入力の第1indexを最速とする。対称化誤差を数値で記録する。
raw三次微分をTaylor fiberへ戻す係数は、block重複の階乗の逆数とS列の重複度を
組み合わせる。最終的に全`i<=j<=k`を一度ずつ覆うことを照合する。

### 方程式と判定

出力波数は3入力波数の和。選択外・選択内の外部補空間・zero-wave固定葉を区別し、
外部方程式 `A_ext H3 - H3 Lambda_product + F3_ext = 0` を解く。
選択出力の内部forcingはR3候補へ投影し、`P_selected H3=0`を保つ。

次の数値基準を変更せず全tripleへ適用する。

- rank threshold: `100*eps*operator_dimension*sigma_max`。
- condition number上限`1e8`、外部solve relative残差上限`1e-10`。
- full-population homological relative残差上限`1e-9`。
- input symmetric-subspace invariance、外部部分空間、graph gauge、zero-waveの
  H3/forcing保存momentのscaled誤差上限`5e-12`。
- numerical singular compatible／incompatible、ill-conditioned、残差失敗を分ける。
  singular compatibleを一意な係数solveとして通さない。
- SVDは既存の例外時だけのgesvd代替を使う。正常終了した数学的不合格を別backendで救済しない。

最小detuning、最小特異値、弱い左部分空間へのforcing射影、応答normも保存する。
これらを使って真の共鳴と断定せず、数値的非共鳴・悪条件化・右辺整合性を切り分ける。
三格子共通のprequalificationは全格子・全tripleの通過を必要とする。
17³だけの成功を三格子共通成功へ読み替えない。

### 独立性・実構造・coverage

1. 非対角複素安定blockの既知三次解で、Kronecker／Sym²／Sym³の積とsolveを検証する。
   singular compatible／incompatible・near-resonanceの負の対照も置く。
2. 各格子でseed `2026090719` の8個の104次元単位方向を使い、全fiberの三次forcingを
   contractionする。これを物理空間で別に計算した
   `B(Vu,H[u,u]/2)+C[Vu,Vu,Vu]/6-H[Lambda u,G[u,u]/2]` と比較する。
   relative誤差`1e-8`以下。full-map差分fitをforcingの生成に用いない。
3. 全monomialの共役partnerを照合する。forcing、H3、R3の各fiberの差を
   `max(1,norm(fiber))`で割った最大値を記録し、`1e-8`以下を要求する。
   小さい虚部を捨ててから検証しない。R3出力のacoustic±交換を含める。
4. 別プロセスで全二次係数を再構築し、各格子で固定16 tripleの行列・forcing・解のhashと
   全診断を一致させる。ordinal 0と82159、およびseed `2026090720` で
   `1..82158`から重複なし抽出した14 ordinalを採る。計48 tripleであり、全数再現とは呼ばない。
5. 全tripleの結果を順序付き圧縮JSONLに保存し、summaryの件数・最大値・最悪例・判定を
   保存行から再計算する。バイナリhashと展開した科学的record列のdigestを別に持つ。
   圧縮は保存形式だけの変更であり、数値精度やcolumnを削減しない。

全forcing/H3/R3 fiberは実構造・全coverage・方向別検証のために一時的に構成する。
このpreflightでは実座標R3の104⁴ dense配列や物理空間の巨大W3配列を作らない。
通過後のQ012gで評価器・保存形式・残差次数・有限振幅・費用を別途検証する。
Fourier selection ruleによる疎表現を必須baselineとし、TTの優位性は仮定しない。

### 総合判定と次の行動

seal、二次入力再構築、全coverage、有限性、独立forcing、48 triple再現をvalidityとする。
数学的solve不合格は残りのtripleを省略する理由としない。予期しない実行障害は保存し、
未実行を明示してinconclusiveにする。数値的失敗を隠してpartial成功へ変更しない。

validity通過かつ全三格子の三次solve・実構造が通ればaccepted、validity通過でいずれかを
落とせばrejected、validity不通過ならinconclusiveとする。grid依存性を別に示し、
棄却なら最初の未解決機構を分析する。受理でも、三次W/Rの評価器・有限振幅改善・
SSM存在・grid-uniform半径は未検証のまま次の研究課題へ渡す。

## 2026-09-07 封印結果: passed / rejected

事前登録commitは`9480e24`。全三格子・全246,480 triple・578,760対称columnの計算が
完了した。全8 validity gateを通過した一方、三格子共通のsolveと実構造の両仮説を落とした。
17³だけの通過で全体を受理せず、Q012gの三次chart評価器へ直進しない。

### 全数結果

| 診断 | 17³ | 33³ | 65³ |
|---|---:|---:|---:|
| 完了triple | 82,160 | 82,160 | 82,160 |
| rank・condition基準の不合格 | 0 | 0 | 0 |
| solve総合不合格 | 0 | 0 | 272 |
| 最大condition number | 39,414.9040 | 500,430.0734 | 7,246,918.3126 |
| 最小特異値 | 6.98843e-5 | 5.50737e-6 | 3.80275e-7 |
| 最大外部solve相対残差 | 6.36578e-12 | 7.03068e-11 | 1.08311e-9 |
| 最大raw三次応答norm | 2,700.4657 | 22,509.4451 | 176,601.8718 |
| H3最大scaled共役誤差 | 1.86685e-9 | 7.88162e-8 | 5.39076e-6 |
| 全実構造gate | pass | fail | fail |
| 独立forcingの最大相対誤差 | 6.58278e-13 | 8.18163e-12 | 1.20345e-10 |
| 例外時だけのSVD代替件数 | 0 | 0 | 2 |

応答normはorthonormal Fourier・global-l2座標でのraw三次微分行列のnormである。
局所振幅基準やTaylor fiberそのもののnormではない。既存solverから継承したrecord名
`response_local_norm`には各行の`response_normalization`でこの規約を明記した。
gridごとに異なる波数・operatorを比較しているため、この3値だけから漸近指数を認証しない。

全246,480件のstatusは`nonsingular_practical`だが、これは数値rankとconditionのみの判定。
最終`passed`にはsolve残差・full-population残差・構造・backendの別gateを要求する。
従ってこのstatusで65³の272件を通過扱いしてはならない。

65³の272件は全て外部solve相対残差`1e-10`を超えた。内訳はshear/shear/shearが264件、
shear/acoustic+/acoustic-が8件で、rank・condition・構造の不合格はない。
ordinal `55031, 62968, 63622`の3件はfull-population残差`1e-9`も超えた。
最初の不合格はordinal `897`、入力波数`(-1,-1,-1), (-1,0,0), (0,0,1)`のshear三つ、
出力波数`(-2,-1,0)`、operator 216×216である。condition `1.64143e6`、
forcing norm `.322362`、応答norm `126505.171`、残差 `6.66064e-10`だった。
弱い左部分空間へのforcing射影は`.214249`であり、悪条件方向のforcingがゼロとはいえない。

65³のordinal `45729, 55289`だけが元gesddの`SVD did not converge`例外を生じた。
既存の例外時gesvd代替で両方通過した。factor再構成誤差`3.88520e-15`、左右直交誤差
`3.23142e-14 / 3.31750e-14`も登録上限内だった。上記272件は全て元gesddが正常終了した
ケースであり、これらに事後的なbackend切替を適用していない。

### 実構造の失敗と独立性

forcingとR3の全fiber共役gateは三格子で通った。H3だけが33³/65³で上限`1e-8`を超えた。
最大誤差の入力monomialと共役partner（0-based complex coordinate）はそれぞれ
33³で`[53,60,92] / [8,40,49]`、65³で`[36,44,53] / [49,56,64]`である。
全partnerのcoverage・反対出力波数を確認し、小さい虚部を捨てる前のfiberで判定した。

unchanged二次H2のaggregate共役誤差は17³/33³/65³で
`9.36665e-13 / 1.23684e-11 / 2.04230e-10`だった。これはH3のfiber-wise尺度とは異なる。
元二次評価器は物理場を実部に戻す一方、今回の係数forcingは保存された複素H2を用いる。
独立物理forcingとのずれは全24方向で上限`1e-8`以内だが、この比較はH3実構造の代わりにはならない。
入力共役誤差の増幅と、大きい解を持つ方程式での浮動小数点打消しは原因候補であり、
現時点でどちらか一つが原因と確定したわけではない。

既知の非対角複素安定block・全4対称積patternで、製造した三次解と独立Sylvester solveが一致。
特異compatible／incompatible・ill-conditionedの負の対照も正しく不合格となった。
各格子8方向の104座標をすべて用いる独立物理forcing比較は通過した。
別プロセスでは全二次係数をfreshに構築し、固定16 triple/格子の行列・forcing・解のhashと
全recordが一致した。これは48 tripleの独立再現であり、全246,480 tripleの再実行ではない。
テストでは全保存行のrank・condition・残差・判定・最大値を再計算し、別途freshな二次係数と
各格子のordinal 0・最悪condition・最初の不合格を再計算した。

全三次fiberは構築時に照合したが、保存するのは配列metadata hashと全診断recordである。
三次評価器・三次残差の次数4・有限振幅改善・存在定理はまだ検証していない。
物理空間の巨大W3や104⁴の実R3は確保しておらず、TTの優位性も主張しない。

### 保存と再現

全診断は各格子82,160行のlossless gzip JSONLとして保存し、展開後の順序・全数値一致を確認した。
workerを含む入力chain、固定保存量葉、全104座標を保った。関連既存230テストと新規38テスト、
ruff・compileallは通過した。再現コマンドは[STATUS](../research/STATUS.md)に記載する。
封印artifactを上書きせず、別の`research/replays/`へ出力する。cycleにはworker metadataが入るため、
再実行時はsource hash・配列hash・全科学的recordを照合し、cycle全体の一致を要求しない。

newline-normalized SHA-256（gzipはraw byte SHA-256）:

- cubic helper: `bf9ce50926b1a75a5f33d01302b2af48b4e173b1d39b08f97a0bdaa336ffca70`
- runner: `06ac8d9ccd0382714b4f4c70c763ddeb1d3e65b3fea4da1f7f595113b3bab94c`
- main artifact: `d3b778ed339c9629dbac57264291aceb32c795a1e6d12e3becb20cf333c57089`
- cycle digest: `42208f4a8a6c7d585273ae8d925a6d966cc68e568f08a835ab7f941a41668b34`
- replay artifact: `5e54cfb8ef545748417f26dda3b954b5b43ce63faa5504127fc1619a30d09aa8`
- replay evidence digest: `086e3ad397b2ef90d3f37aed38909cfcbadf0b4b87367ede6db87f0a47e7bdcc`
- 17³ gzip (9,309,054 bytes): `f2b42c98554ca482c7e6c07c8d168fbcbc033b6421bf4398be43ac597d5565f6`
- 33³ gzip (9,306,440 bytes): `9fc10e6e384f9adf906f3f989e47e5f22d04a3e989a3f628c6d0273a0147afd7`
- 65³ gzip (9,324,427 bytes): `7444d66a8acf411635fef32bd11e1f91ec423fb1a8f970ffe0c2ceebb5138298`

展開record列digest（canonical JSON行と改行を順にhash）:

- 17³: `276f146328627d286f23523974676c5d2fb4b1eae15c2f2bd1bbdcf368bbedf2`
- 33³: `e2dc02bde2272b17d8f1ba11ab99b19a470d5064b1c21c3aecf2cb095387734e`
- 65³: `9b9f21d9f72602df0a341d5afd3890918536ad8da4d8011915b54fe9b96d0d70`

### 次問 Q012f1

入力の共役誤差とsolver精度を分ける診断を事前登録する。元入力／明示的実構造の入力と、
元SVD／独立高精度または構造化Sylvester solveを区別し、元272件の失敗分類と固定共役最悪対・
成功対を覆う。入力を変更する候補では二次方程式・固定葉・独立forcingを改めて検証する。
単一ordinalずつの監査へ細分化し続けず、機構を切り分けた後の候補は全三格子で再検証する。
これはまだ診断案であり、修正実装の受理ではない。元Q012fの棄却と閾値は保持する。
