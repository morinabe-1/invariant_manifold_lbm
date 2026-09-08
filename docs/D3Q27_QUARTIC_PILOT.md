# Q012h2: 実LBMの四次forcing・operatorと資源pilot — 事前登録 2026-09-08

## 問い・固定範囲・親

Q012h1は人工代数オラクルとして受理した。次は、**実LBMの全lower-order入力から四次の混合forcingを構築でき、
難しいスペクトル条件を含む登録pilotで解・独立照合・資源計測を成立させられるか**を問う。
本書をcommitしてから新しい実装・四次の数値実験を開始する。Q012h2の判定は未実行・未確定。

- `N=17,33,65`、`omega=1.5, eta=.02, power=2`、全26第一shell波数・78 block・104座標を保持する。
  各波数のshear平面は2次元、acoustic±は各1次元。shearを個別固有ベクトルへ分割しない。
- 質量と3運動量を固定した葉を使う。ゼロ波数のkinetic補正は残し、保存モーメントは持たせない。
  center座標の追加、波数の削除、別filter、追加の係数平均・射影による救済は行わない。
- 親は[Q012h1 manifest](../research/artifacts/q012h1_d3q27_quartic_oracle.json)、正規化ファイルSHA256
  `fb70d3b9f8e75505b337c7eaf75db084b3fcce733170069069af8284acd66682`。
  Q012h1の15 source、Q012h0と先行scientific source・artifactを変更しない。
- 二次入力はQ012f2で採用した既存のfresh rebuildとpaired-input処理をそのまま用い、入力監査を通す。
  三次はQ012f2の全192,920 Taylor fiber/格子を、保存済みNPZの全array・checksumと照合して使用する。
  pilotの入力座標だけでlower-orderモデルを再構築することはしない。
- Q012gの3次数不合格・81半減不達・37悪化は未修復のまま残す。本問は元振幅域での改善試験ではない。

## S0: forcingを評価する前に検証対象を固定する

block番号は辞書順の第一shell波数ごとにshear, acoustic+, acoustic−を並べた`0..77`とする。
共役partnerは反対波数へ移り、局所labelを`(0,2,1)`で置換する。tupleは常に昇順に正規化する。

1. 全bについて、`c=(b+1)%78, d=(b+2)%78, e=(b+3)%78`から
   `(b,b,b,b), (b,b,b,c), (b,b,c,c), (b,b,c,d), (b,c,d,e)`を作り、共役closureを取る。
   整数構造の確認値は650組。さらに`(0,3,6,9)`とその共役`(66,69,72,75)`を加え、**652組**を必須seedとする。
   後者は全相異なるshear入力、出力波数`(-4,-3,-1)`、外部次元27・対称列16、operator寸法432を含めるためである。
2. 各格子の全**1,663,740 unordered四つ組**について、filtered blockの固有値の四積と、出力波数の外部sectorの
   固有値との最小距離`delta=min |lambda_ext-product(lambda_input)|`を走査する。
   外部sectorはゼロ波数でkinetic 23次元、第一shellでは選択4次元の補空間23次元、それ以外で27次元。
   filterは既存の`1-eta*(sum(sin(k/2)**2))**power`を用いる。
3. 重複pattern `(4), (3,1), (2,2), (2,1,1), (1,1,1,1)`と出力sector（zero/selected/other）の各非空binから、
   最小の`(binary64 delta, tupleの辞書順ordinal)`を一つ選ぶ。空binは記録し、架空の代表を作らない。
   全3格子の代表・その共役を652 seedへ加えたunionを、全格子で共通に用いる。**上限742組/格子**。
4. 全tupleの距離、全binの件数・最小値とordinal、使用した全block/external行列・固有値、選択理由を保存する。
   主方式はbounded chunkで計算し、独立方式は別のtuple列挙と固有値積の生成で全距離・binを照合する。
   固有値距離の数値照合は絶対誤差`1e-13`以内。選択自体は保存された主方式の全距離から厳密に再構築する。
   near tieによる代表の変化を隠さず、距離は丸め済み行列・binary64評価の診断値であると明記する。
5. 選択実装をcommit・封印してから走査し、全距離の保存後監査を通した選択artifactをcommitする。
   **選択を固定するまで実LBMのF4を評価しない**。後続実装はこの入力と選択sourceを変更しない。

この全数走査は外部共鳴に近い候補を選ぶための固有値距離診断であり、全operatorの最小特異値・rank・条件数の証明ではない。
S0だけの完了をQ012h2の受理、全四次solveの実行可能性、SSM存在として扱わない。

## H1: 全pilot columnの四次forcingを別の代数経路と照合する

Q012h1で検証したraw微分の7項群を、実LBMのB/C/D、H2/H3、G2/G3へ適用する。
対角での式は次のとおりで、実装・照合の対象は全混合columnである。

```text
F4 = 4 B(V,H3) + 3 B(H2,H2) + 6 C(V,V,H2) + D(V,V,V,V)
     - 4 H2(Lambda,G3) - 3 H2(G2,G2) - 6 H3(Lambda,Lambda,G2)
```

- 保存fiberはTaylor monomial係数である。raw微分への変換は添字重複のmultiindex factorialを使い、
  一律2!/3!/4!で変換しない。第1入力index最速の対称積と軌道正規化はQ012h1の規約を保つ。
- 直交FFT規約により、局所B/C/Dへ渡すFourier振幅の積にはそれぞれ`N^-1.5, N^-3, N^-4.5`が掛かる。
  lower-order係数に既に含まれる正規化を再度掛けない。streamingの位相は`exp(-i*k·c_q)`。
- 平衡`rho=1,j=0`の局所Bを`B0(u,v)=w*(9(c·j_u)(c·j_v)-3 j_u·j_v)`とすると、
  `C0=-sum rho_u B0(v,w)`、D0は密度2引数の6選択について`2*sum rho_i rho_j B0(other pair)`。
  複素表示の多重線形式へHermitian共役を入れない。式は独立展開で検証し、自己整合solveだけで正しいと判定しない。
- 独立方式は4個の区別されたnilpotent変数を用い、既存のTaylor monomialを直接代入する。
  局所平衡の逆密度級数と`W3(R3)`を多項式として合成し、4変数の積の係数を抽出する。
  主方式の7項formula・raw factorial変換・対称積kernelは呼ばない。全104座標の内部力学を保持する。
- 主・独立方式の全pilot全columnのF4を、`norm(diff)/max(1e-14,norm(reference)) <= 1e-8`で比較する。
  forcingの7項群のnorm、collisionとcompositionの各寄与、零/非零coverageを保存する。
- さらに各格子で、pilot内の各非空pattern/sector binの辞書順最初のtupleと最大432寸法の必須tupleを対象に、
  最初と最後の対称column（同じなら一つ）を、物理格子上の平衡級数・streaming・差分filter・直交FFTで照合する。
  対象columnを値を見て選び直さず、全出力waveの漏れも含めrelative `1e-8`を要求する。
- FFTの次数factor欠落、streaming符号反転、filter欠落、G2またはG3欠落を負の対照とする。
  各変異に実際の非零検出例を要求し、検出できなければその対照は未成立と記録する。

## H2: 実operatorの全pilot解・構造を検証する

各tupleで実filtered block行列のKronecker積を対称部分空間へ制限し、
`A_ext X-X D4+F_ext=0`を既存SVD方式とSylvester＋固定3回refinementで解く。
条件を変えて数値的な不合格を救済しない。gesvd fallbackは既存の例外時規則のみ。

- rank thresholdは`100*eps*dimension*sigma_max`、実用condition上限`1e8`。
  singular compatible/incompatible、nonsingular ill-conditionedを区別し、一意な実用解として受理しない。
- 両方式の解を保存し、scaled相互差`1e-8`、丸め済み行列の独立GMP残差で外部relative `1e-10`、full式relative `1e-9`を要求する。
  分母は`max(1e-14,norm(F))`。float64残差を併記し、残差積和の丸めと式の不一致を区別する。
- gaugeとゼロ波数の保存モーメントはscaled `5e-12`、共役closureのTaylor H4/G4はrelative `1e-8`を要求する。
  共役平均・追加射影を四次結果へ施さない。G4は選択左基底によるF4の射影と照合する。
- 各operatorの全行列・特異値・解・F4/G4・Taylor fiberを保存し、保存後に全entry・診断・集計を再構築する。

## H3: 資源上限と実測

事前のread-only確認ではRAM約15.7 GiB中の空き約4.8 GiB、Cドライブ空き約13.8 GiBだった。
Q012h0の全四次payload約14.19 GiB/三格子を一括確保・保持する設計にはしない。
以下は原問題を縮小する条件ではなく、全規模構築へ進む前のpilotの運用上限である。

- 格子は17→33→65の順で、独立方式もprocessを順に実行する。全三格子のlower-order配列を同時に保持しない。
  S0距離走査のchunkは高々4096 tuple、F4の作業単位は一つのblock tupleとする。
- 各grid process開始時に利用可能RAM `>=4 GiB`、disk `>=6 GiB`を要求する。
  各processのpeak working set（RSS相当）とpeak private commitの上限をそれぞれ`3 GiB`、
  各grid/routeの実時間を4時間、本問による新規保存物の合計を2 GiBとする。
- lower-orderの再構築・読み込み・全監査、一時コピー、参照計算、保存・再読も当該processの資源計測へ含める。
  OSが管理するpeak値、工程ごとの現在値、各実ファイルbytes、計算/保存/監査の経過時間を分けて記録する。
  配列のnbytesやZIP圧縮量をRSS・独立自由度数と呼ばない。S0だけの測定をF4/全数solveへ流用しない。
- 上限超過、欠測、例外は未完了分と実行済み結果を保持し、inconclusiveとする。既存ファイルは上書き・削除しない。
  他のユーザーファイルの削除、環境の大幅な変更、対象caseの間引きで通過させない。
  上限の変更が必要なら、測定済み失敗を保持した別の資源設計を事前登録する。

## 実行証跡・判定・後続

親Q012h1の全再監査、先行source/入力封印、S0選択の全件監査、新規sourceのcommit、finite、全件coverage、
実在する別processのPID/exit/source、負の対照coverage、保存後全entry再構築をvalidityとする。
実装部品のテストと正式pilotの結果は分離する。sourceは各段階の正式実行前にcommitし、後続から変更しない。
validityが通りH1/H2/H3が全て成立した場合だけQ012h2をaccepted、科学的条件不成立はrejected、欠測はinconclusiveとする。
途中のS0選択artifactは段階結果であり、Q012h2の合格manifestとは区別する。

後続では全**1,663,740組・5,160,610列/格子**の四次chart構築、元Q012gの全振幅試験・反例の改善を検証する。
pilot成功から未計算のrank・RSS・残差改善を推定して合格にしない。D3Q27 SSM存在、連続振幅域、
自然Fourier sparseを必須baselineとするTT実費用比較、物理benchmark・force/wallは引き続き原研究の未完了課題である。
