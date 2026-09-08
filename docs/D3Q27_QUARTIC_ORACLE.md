# Q012h1: 四次operator・forcingの人工オラクル — 事前登録 2026-09-08

## 問い・親・主張範囲

Q012h0を`1348b8a`で構造censusとして受理した。四次は全104座標について1,663,740 block組・5,160,610列/格子である。
次に、**四次の対称積・Taylor正規化・非自明な内部力学を含むforcingとhomological solveを、既知解から独立検証できるか**を問う。
この文書をcommitしてから新規helper/runnerを実装する。判定は未実行・未確定。

- 親は[Q012h0 manifest](../research/artifacts/q012h0_d3q27_quartic_census.json)、正規化SHA256は
  `4c7c20a6dbde1aa8c9e7317a7b7750c000d81e429759af51ddfebc836064a0d8`。
  両child・source・先行Q012g3もQ012h0の全再監査で開始前後に確認する。
- 先行scientific source、Q012h0の4固定source、`src/ttim_lbm`、既存係数・判定は変更しない。
- 本問は人工代数オラクルであり、D3Q27の実四次forcing・全数rank・実測RSS・有限振幅改善ではない。
  後続の実LBM問題は17³/33³/65³、全26波数・78 block・104座標、`omega=1.5, eta=.02, power=2`のまま保持する。
  人工例の小さい座標数を原問題の置換に使わない。
- 保存量は質量と3運動量を固定する葉。人工写像にも恒等力学の4保存座標を追加し、chartはそれらを0に固定する。
  center-slow構築や保存座標の追加による共鳴回避には切り替えない。

## 四次の式と二つの表現

摂動chartと内部力学をraw対称微分で
`K(a)=Va+H2[a²]/2!+H3[a³]/3!+H4[a⁴]/4!`、
`R(a)=Lambda*a+G2[a²]/2!+G3[a³]/3!+G4[a⁴]/4!` と書く。
`A=D Phi, B=D² Phi, C=D³ Phi, D=D⁴ Phi`は平衡での微分、`W=f*+K`である。

合成の混合微分を集合分割で数えると、区別された4引数の各項の係数は1で、同一引数にしたときの係数は重複数になる。
この一般則は[Hardy (2006), Combinatorics of Partial Derivatives](https://arxiv.org/abs/math/0601149)に基づく。
以下はその一般則を本研究のraw微分規約へ適用して導出した候補式であり、本問の独立オラクルで検証する。

```text
F4[u,u,u,u] = 4 B[Vu,H3[u³]] + 3 B[H2[u²],H2[u²]]
               + 6 C[Vu,Vu,H2[u²]] + D[Vu,Vu,Vu,Vu]
               - 4 H2[Lambda*u,G3[u³]] - 3 H2[G2[u²],G2[u²]]
               - 6 H3[Lambda*u,Lambda*u,G2[u²]]

A H4 - H4 (Lambda tensor Lambda tensor Lambda tensor Lambda) + F4 - V G4 = 0
```

区別された4引数では、順に1+3分割の4項、2+2分割の3項、2+1+1分割の6項、全1+1+1の1項。
後半のcompositionも4/3/6項である。対角式だけから全混合微分の正しさを推論せず、全混合columnで照合する。
内積の複素共役をこの多重線形微分へ入れない。graph gaugeは選択左射影`L H_d=0`で固定し、`G4=L F4`を検証する。

一般の不変性方程式と係数構築の設定は[既存の文献整理](LITERATURE_REVIEW.md)を保持する。
本問の代数的一致は、外部非共鳴や正則性を仮定する存在定理の適用を意味しない。

## H1: 四次対称積と列正規化の全人工inventory

人工blockをb=0,1,2,3とし、次元`(s0,s1,s2,s3)`は`{1,2}^4`の全16通り。
各通りで4 blockからの全35 unordered四つ組を使う。全5重複patternを保持し、一部のpatternを省略しない。

- `a_b=3/5+b/40`、1次元blockの力学は`[a_b]`。
- 2次元blockは`S_b J_b S_b^-1`、`S_b=[[1,b+1],[0,1]]`、
  `J_b=[[a_b,-(b+1)/40],[(b+1)/40,a_b]]`。非正規で、安定複素共役対を持つ。
- 全積は第1入力index最速。重複block内の対称軌道から直交列Sを作り、
  `D4=S.T @ kron(Lambda4,kron(Lambda3,kron(Lambda2,Lambda1))) @ S`へ制限する。
- 別方式は有理数のmonomial辞書へ各blockの線形写像を直接代入する。Kronecker積・S構築関数を使わない。
  無正規化monomialから軌道多重度の平方根で表現変換し、D4全entryと一致を要求する。
- Sの直交性、対称部分空間の不変性、全unique入力column、全相異なる入力slot permutationを検証する。
  raw微分からTaylor columnへの係数は`sqrt(軌道多重度)/product_b(m_b!)`。
  実際の多項式代入の係数と比較し、全columnへ一律1/24を掛ける実装を負の対照で拒否する。

外部次元p=23,27を各inventoryに適用し、**全1,120人工operator case・4,482対称入力列**を保存する。
最大列数16、最大operator寸法432を含む。これは実LBMの全1,663,740組/格子の代用ではない。

## H2: 既知の非線形chartと内部力学からの全forcing照合

人工selected座標xは8次元、上の2次元blockを4個使う。p=23,27の各外部座標yについて、次の有理係数を固定する。
indexは0始まり、`ell(x)=sum_i((i+1)*x_i)/8`、`m(x)=sum_i((-1)^i*x_i)/8`。

```text
h_z(x) = sum_{d=2..4} [ (z+1)/32 * ell(x)^d + (-1)^z/64 * m(x)^d ] / d!
R_i(x) = (Lambda*x)_i
           + sum_{d=2..4} [ (-1)^i/32 * ell(x)^d + (i+1)/64 * m(x)^d ] / d!
e = y-h(x), E(e)=sum_z(e_z)/(p+1)
U_i(x,e) = (i+1)/128 * [ell(x)*E + E^2 + ell(x)^2*E]
T_z(x,e) = (z+1)/128 * [2*ell(x)*E - E^2 + 3*ell(x)^2*E]
A_ext = -diag(1/5 + z/(10*p)) + superdiag(1/100)
Phi(x,y,c) = (R(x)+U(x,e), h(R(x))+A_ext*e+T(x,e), c)
W(a) = (a,h(a),0), c in R^4
```

`e=0`でU=T=0なので、これは既知の非零H2/H3/H4とG2/G3/G4を持ち、`Phi(W(a))=W(R(a))`が代数的に成り立つ。
U/Tを設けるのは、単純な三角写像ではB(V,H3)・B(H2,H2)・C(V,V,H2)が消えてしまうためである。
全7 forcing項群それぞれの非零係数を確認する。消える項群があればその対照は不成立と記録し、十分なcoverageとみなさない。

- 主方式は混合Fréchet微分と上記集合分割式からF4を作る。
- 独立workerは`fractions.Fraction`（複素数は実虚の有理数対）で既知多項式を直接合成し、次数4までの全係数を抽出する。
  forcing式・対称化・Kronecker kernelを呼ばず、入力recipeも独立に構築する。有限差分fitは使わない。
- 全`i<=j<=k<=l`の330列/場合でF4、既知H4、G4、full homological式を照合する。
  H2/H3/G2/G3も既知の全monomial係数と照合し、既知解を入力にした自己整合だけでforcingを通さない。
- real表示と、各blockの`S_b @ [[1,1],[-i,i]]`で作る複素固有対表示の両方を使う。
  左基底は厳密な逆行列で構築し、`LV=I`と元real係数への往復、共役partnerを全件検証する。
  p=23,27×2表示の全4場合・四次1,320列。保存量4座標の全chart/forcing係数は厳密に0。
- 整数/有理数同士の係数照合は完全一致。float64へ変換する比較では、相手のFrobenius normを基準に
  `norm(diff)/max(1,norm(reference)) <= 5e-12`。全係数と、非零を確認した各項群のノルムを保存する。
- 各forcing項群の削除、composition符号の反転、G2/G3の省略、複素多重線形項への不要な共役を負の対照とする。
  各変異について少なくとも一つのexact係数の相違を要求する。検出できない変異を成功扱いしない。

## H3: 既知解・near resonance・特異問題

H1全1,120 caseに対して上記A_extを使い、`X_known[row,col]=(row+1)/32 + 1j*(col+1)/32`とする。
丸め済み行列D4について`F=X_known@D4-A_ext@X_known`を作り、既存のKronecker型SVD解法と
Sylvester＋固定3回refinementの両方式を検証する。D4の誤りをこの既知解構成だけで見逃さないようH1を必須にする。

- 既知解scaled誤差`1e-10`、外部relative残差`1e-10`、full式`1e-9`、構造/gauge`5e-12`を上限とする。
- relative残差分母は`max(1e-14,norm(F))`。丸め済みA/D/F/Xの残差は独立整数/有理数演算でも評価する。
  残差積和の丸めと方程式の誤りを区別し、float64残差だけでexactな式の不合格を認定しない。
- rank thresholdは`100*eps*operator_dimension*sigma_max`、condition上限`1e8`。
  gesvdへの変更は既存規則どおり例外時のみ。正常終了した数学的不合格をbackend変更で救済しない。
- 負の対照は`A=diag(.5+gap,.125), D=[.5]`。
  `(gap,F)=(0,[[0],[1]])`はsingular compatible、`(0,[[1],[0]])`はsingular incompatible、
  `(2^-36,[[1],[1]])`はnonsingular ill-conditionedとして区別する。
  特異compatibleを一意なH4として通さない。

## 実行の妥当性・保存・次の行動

source/親封印、全case・全column coverage、finite、左右正規化、非零対照のcoverage、
実在する別processのPID/exit/source、保存後全内容再計算をvalidityとする。
H1は全対称積・正規化、H2は全既知写像forcing・実複素表示、H3は全既知解と負の共鳴対照。
validity通過かつ全仮説成立で人工オラクルをaccepted、不成立はrejected、欠測/例外/封印変化はinconclusive。
失敗したpattern・表示・外部次元を削除して受理しない。

新規helper/runner/専用テスト、各caseの入力・全行列/係数・診断、独立worker、最終manifestを排他的に保存する。
全科学的recordを独立方式と照合し、保存後は全entry・集計・判定を再計算する。旧artifactを上書きしない。
新しいsourceは正式実行前にcommitして封印する。数値結果を見て閾値や人工recipeを変更する場合は、
元結果を保持して新しい診断/修正ゲートを登録する。

本問の後は実LBMの四次forcing・operatorと資源pilotを別登録する。
そこで全104座標のlower-order入力を保持し、streaming/filterとorthonormal FFTの次数別係数、
zero-wave kinetic補正、実際のrank/condition、lower-order入力・作業配列・保存を含むRSS/時間/diskを測る。
pilotのcase選択と資源上限は実行前に固定し、pilot成功を全数solve・四次残差改善へ一般化しない。
最終的な全三格子の四次chart、元振幅域の改善、SSM存在、3D疎/TT実費用、物理benchmarkは依然として未完了である。

## 実装進捗 2026-09-08 — 部品テストのみ、正式判定は未実行

上記の事前登録はcommit `a345ec7`で固定した。以下はその後の実装検査で、登録条件や対象を変更しない。

- H1部品：全16 inventory×35四つ組の対称積を、独立Fraction monomial代入と全entry照合した。
  全5重複pattern・slot permutation・Taylor係数を検査した。外部次元23/27を合わせた登録件数は1,120組・4,482列。
- H2部品：実/複素×外部次元23/27の全4場合、各330四次列を独立Fraction多項式合成と完全照合した。
  全二〜四次H/G、全係数の実表示への往復、7項群の非零coverage、保存量、項の欠落・符号・共役の負の対照も検査した。
- H3部品：全5重複pattern×外部次元23/27と1次元block例の11正例を検査した。最大operator寸法432を含む。
  既存SVDと固定3回refinement、独立exact残差、3種類の特異/悪条件対照を検査した。
  外部残差1e-10とfull式1e-9は別条件であり、未refineのSylvester結果は診断のみとする。

再現コマンド（新規118テスト、警告error化、88.68秒で通過）：

```sh
python -m pytest -q -W error tests/test_d3q27_quartic_operator.py tests/test_d3q27_quartic_jets.py tests/test_d3q27_quartic_fraction.py tests/test_d3q27_quartic_solve.py
```

実装は `research/d3q27_quartic_{operator,reference,jets,fraction,solve}.py`。先行scientific sourceとQ012h0固定sourceは変更していない。
検証評価は **Share with caveats（部品検証に限定）**。全1,120 caseの正式solve、独立workerの実PID/exit/source、
全行列・係数の排他的保存と保存後全entry再監査は未実行であり、**Q012h1のaccepted判定はまだ出していない**。
これらを正式runnerに接続し、sourceをcommit・封印してから登録済みの全数実行へ進む。

## 実行器の実装検証 2026-09-08 — 正式実行前

`research/q012h1_d3q27_quartic_oracle.py`に、全1,120 case・4,482列と全4 forcing case・1,320列の実行/保存/監査を接続した。
primary/workerのZIPはそれぞれ2,247/1,127 entryを必須にする。圧縮は格納形式であり、数学的な自由度の削減ではない。
入力行列、実homological行列、全解・残差・exact proof、軌道basisとTaylor係数、全forcing項群・既知係数を保持する。
独立workerはFraction forcing合成と明示的行列組立を使い、primaryの丸め済み数値解をGMP残差で検査する。
source commit、事前登録prefix、Q012h0全再監査、実PID/exit/stdout、保存後全entry再構築を結び付ける。
既存出力や部分実行を上書きせず、例外時はfailure markerを残す。科学的な不合格を削除して受理しない。

追加129件と既存118件、計247テストが警告error化で通過した（149.26秒）。
再封印改変・末尾entry・空/部分coverage・偽worker・source変更・pickle拒否を含む。Q012h0のfresh再監査も通過した。
これは実装検証であり、正式な科学的判定はまだ未実行である。

sourceのcommit・封印後に実行するコマンド：

```sh
python -u -W error -m research.q012h1_d3q27_quartic_oracle
python -u -W error -m research.q012h1_d3q27_quartic_oracle --audit-only
```

監査は保存record/配列の全再計算を含むため、集計だけの読出しより時間を要する。
再計算には封印した数値libraryのversionも照合する。異なるversionでの再現性は別途評価し、この実行へ混ぜない。

## 正式結果 2026-09-08

source commit `d91cc3755cc4f7c42177943ef9b12e42cd45af17`の15ファイルを固定し、登録内容を変更せず全数実行した。
primary PID 34492と独立worker PID 36808の実際の終了code 0を確認した。
全保存entryの再計算後、全8 validityとH1/H2/H3が成立し、manifestは **passed / accepted**。
さらに別CLIでも全record/配列・集計・判定を再構築し、exit 0で同じ結果を確認した。

- H1：全1,120 operator case・4,482対称列。全inventory、重複pattern、slot permutation、Taylor正規化を保持した。
- H2：実/複素×外部次元23/27の全4場合・1,320四次列。全二〜四次H/Gと7項群を独立Fraction合成で照合した。
- H3：全1,120既知解問題と3種類の特異/悪条件対照を検証した。正常終了した不合格をbackend変更で救済していない。

全正例はnonsingular practical、最大operator寸法432、最大条件数505.62993230613523。SVD fallbackは0件だった。
最大既知解scaled誤差はSVDが7.342935551580036e-14、固定3回refinementが6.956833564147589e-15。
exact相対残差の表示用最大値は、外部/fullともSVDが5.8716611829721615e-15、refinedが9.091296385596169e-17。
ここで合否は有理数の二乗norm条件を用い、表示用の平方根へ丸めた値だけでは判定していない。

保存物：

- [正式manifest](../research/artifacts/q012h1_d3q27_quartic_oracle.json)：正規化ファイルSHA256
  `fb70d3b9f8e75505b337c7eaf75db084b3fcce733170069069af8284acd66682`。
- [primary archive](../research/artifacts/q012h1_d3q27_quartic_oracle_primary.zip)：2,247 entry、22,983,998 bytes、バイナリSHA256
  `e56c550c87dc5566d9657d5dcbcbe69e69cd3f62fc1c2c44b20464a056ed3d26`。
- [独立worker archive](../research/artifacts/q012h1_d3q27_quartic_oracle_worker.zip)：1,127 entry、3,522,387 bytes、バイナリSHA256
  `6cc4d2c544d03c79fe0b51666b97923615e8c31b20178d1512796530ae9848ef`。

これらのZIPサイズは圧縮後の実格納量であり、数学的な独立自由度・TT格納量・実LBM全数solveのRSSではない。
事前の部品/保存/実行器247テスト（149.26秒）と、正式run内の部品118テスト（86.19秒）が通過した。
実行/再監査コマンドは直前節のとおり。再実行には別の`--output`を指定し、既存の保存物を上書きしない。

検証評価は **Ready to share（人工代数オラクルに限定）**。実LBMの全四次forcing・rank/condition・chart・資源pilotは未完了。
次に全104座標のlower-order入力と三格子を保持して実LBMの構築/資源pilotを別登録する。
元Q012gの3次数不合格・81半減不達・37悪化は未修復で、D3Q27 SSM存在・連続振幅域・TT優位性も未認証である。
