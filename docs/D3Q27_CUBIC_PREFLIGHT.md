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
