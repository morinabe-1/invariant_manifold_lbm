# 研究の到達点 — 2026-09-08

Q012h2aの初回正式CLIは、前段S0再監査の開始RAM/ディスク条件で実exit 1となった。新GMP forcingは未生成。
停止後RAMは約3.89 GiBで必要な4 GiB未満。失敗childの開始時counterは未取得で、後の測定による補完はしない。
初回停止recordを保持し、外側の測定付きpreflightと再試行を含む保存量集計を追加した。数値kernelと閾値は不変。
追加検査を含む計154回帰テストとRuff・format・compileが通過した。これは正式数値実験の通過とは別である。
[資源停止の記録](../docs/D3Q27_QUARTIC_FORCING_PRECISION.md#初回の開始資源条件による停止-2026-09-08)を参照。
次はRAM条件の回復を確認後、別の出力名で全対象の正式精度診断を再実行する。H2/H3へはまだ進まない。

Q012h2aの128/192 bit七項方式・独立多項式方式・moment-only armと全件保存後監査を実装した。
新規68件と先行H1の81件、計149回帰テストが通過した。実LBMの全698組/格子の高精度結果はまだ未評価。
[実装検証](../docs/D3Q27_QUARTIC_FORCING_PRECISION.md#実装検証-2026-09-08--正式計算前)を参照。
次はsourceをcommitして、元514不合格を保持した全対象の正式精度診断を実行する。以下の元H1判定は変更しない。

Q012h2 H1は全三格子・2,094 block組・5,478列を計算し、全入力/保存後再計算・mainの実exit 0を確認した。
主・独立F4の相対差1e-8に17³/33³/65³で182/174/158列、計514列が不合格。別の補償和normで全列の判定を再現した。
不合格の506列は参照normがfloor未満だが、17³の8列はfloor以上。小さい値だけの問題とは結論しない。
固定した物理照合60列、全5変異/格子、H1-onlyの資源条件は通過。最大private commit約2.35 GiB、最長route約576.33秒。
別CLIによる全入力/全entry再監査も実exit 0で完了。計212回帰テストが通過したが、H1不合格を保持し、H2 solveへまだ進めない。
[H1結果](../docs/D3Q27_QUARTIC_PILOT.md#h1正式結果-2026-09-08--全件完了独立f4一致は不合格)と
[Q012h2aの事前登録](../docs/D3Q27_QUARTIC_FORCING_PRECISION.md)を参照。次は全対象の128/192 bit算術精度診断。

Q012h2 H1の実LBM四次forcing、独立nilpotent合成、物理FFT/filter照合、実入力loaderと実行器を実装した。
新規66件＋先行131件の計197テストが通過。6座標の全126混合組、560対称積、入力外内部座標、5変異を検証した。
これは部品検証であり、実LBMの全698組/格子の結果とは別である。後続の正式H1の結果は冒頭を参照。
H2 solve・solveを含むH3は未実装/未評価。詳細は[H1実装検証](../docs/D3Q27_QUARTIC_PILOT.md#h1実装検証-2026-09-08--実入力の正式計算前)へ。

Q012h2のS0（検証対象の選択）が正式実行・保存後全件監査・別CLIの全件再監査を通過した。両CLIの実exit 0を確認した。
全三格子の4,991,220 block組を二方式で走査し、全距離の差は最大6.66e-16だった。
三格子共通の698組・1,826対称column/格子を、全104座標と最大432寸法を保って選んだ。
保存されたS0 processの最大working set約219.6 MiB、private commit約1.44 GiB。実H2/H3入力やF4の資源測定ではない。
詳細・near tieの2件・保存物は[Q012h2 S0結果](../docs/D3Q27_QUARTIC_PILOT.md#s0正式結果-2026-09-08--選択のみq012h2全体は未判定)へ。
この後にH1を全件実行したが不合格（冒頭参照）。H2/H3は未実行のまま、H1の算術精度を先に診断する。

Q012h1の四次人工オラクルは、正式実行と別CLIの全件再監査で `passed / accepted`。
全1,120 operator case・4,482列、実/複素×外部次元23/27の全4 forcing case・1,320列を保持し、全8 validityとH1/H2/H3が成立した。
最大operator寸法432、最大条件数505.63。SVD/refinedの最大既知解scaled誤差は約7.34e-14/6.96e-15で、3種類の特異/悪条件対照も通過した。
全entry・行列・係数・判定を再計算し、primary PID 34492、独立worker PID 36808の正常終了を確認した。
事前の実装検証247テストと正式run内の部品118テストも通過した。詳細と保存物は[Q012h1正式結果](../docs/D3Q27_QUARTIC_ORACLE.md#正式結果-2026-09-08)へ。
これは人工代数オラクルの受理であり、実LBMの四次係数・rank/condition・有限振幅改善ではない。
次の[Q012h2: 実LBM四次・資源pilot](../docs/D3Q27_QUARTIC_PILOT.md)では、全104座標・17³/33³/65³と元の失敗caseを保持する。
S0の選択・別process照合・全保存後監査を実装し、起動runtimeの修正後、新規86件＋先行172件、計258テストが通過した。
正式S0の現在の結果は冒頭のとおり。実LBMのF4・solve・資源pilotの合格は主張しない。

Q012h0の正式全数censusと別processの保存後監査が `passed / accepted`。全7 validityとH1–H3が成立した。
全78 block・104座標、次数2/3/4、17³/33³/65³を保持した。四次は1格子あたり1,663,740 block組・5,160,610列、729出力波数。
全個別座標monomialの直接列挙・全sector/payload再計算・親改変拒否を含む181テストが通過した（242.31秒）。
登録した自然Fourier sparse配列の四次保持量は5,078,040,240 bytes/格子（約4.73 GiB）、三格子で約14.19 GiB。
これは係数・forcing等の非圧縮配列payloadであり、実RSS・独立自由度・四次solveの実行可能性ではない。
実LBMの全規模構築と資源pilotはその後の別ゲートとし、全104座標・三格子を保持する。
計算・保存・検証の詳細は[Q012h0結果](../docs/D3Q27_QUARTIC_RESOURCE_CENSUS.md)へ。以下の先行判定は変更しない。

Q012g3のmain全960 caseを完了し、保存後の全件監査で `passed / accepted` を確認した。
全576 profile、元5,760 field・1,920欠陥、全288方向child・三grid・最終親を再読し、全10 validityとH1/H2/H3が通過した。
全192 holdout case・1,152 fieldのexact保存量記録もQ012g1と一致した。一般方向に保存量の追加gateは課していない。
独立worker全192 case・4,599 vector比較の保存後監査と、mainの対応192 caseの全primary科学的record一致も確認した。
元の一般方向3不合格、holdoutの81半減不達・37悪化を全件再現した。元Q012gの `passed / rejected` は保持する。
65³の方向51は傾き、方向52は最小振幅比の超過を再現し、方向34と合わせた旧H4の不合格集合は不変である。
最悪例65³・方向21・`.032`の旧比5.834017983080117を予測5.834017984274533で再現した。悪化は修復していない。
全再構成差の最大は65³・一般方向46・degree3・`.002`のPhi再構成`4.244566574097749e-14`で、元floor`4.1140092794350784e-12`以内だった。
独立OLSで全192 generic fit、補償和で全12,480切断Gram norm²を確認する追加18検査が通過した（169.49秒）。
既存main二格子・反例34・worker65³一般方向の47検査も通過した（73.81秒）。計65件を警告error化で確認し、Ruff・整形・compileallも通過した。
mainの実装・入力・正式177対照は開始時の封印から不変である。元特殊288 caseと未解像null fitは本問の対象外のまま保持した。

main出力は`artifacts/q012g3_d3q27_cubic_defect.json`。11:17 JST時点でPID 35240の不在とhandle 31939の消失を確認した。
元の終了codeや元processによる最終監査のconsole出力は取得できなかったため推測しない。別processで同じ全保存後監査を再実行し、exit 0を確認した。
この旧main handleは再poll・再起動しない。worker PID 27060／handle 51090も終了確認済みである。
この診断から進めたQ012h0の現在の結果は冒頭を参照。高次chartや連続球の実用半径を診断成功で代用しない。

Q012f2は全三格子・全246,480 block triple・578,760 columnで`passed / accepted`。
全104実座標、四階filter付き`eta=.02, omega=1.5`、固定保存量葉、paired入力・固定3回refinementを保持した。
11 validity gate、2仮説、全数保存後監査、972組の独立fresh/GMP照合を全て通過した。
最大exact外部残差は65³の`3.07901e-11`、最大full残差は`1.16995e-10`で、それぞれ元の上限以内。
H3共役誤差最大は17³/33³/65³で`1.11479e-12 / 1.36351e-11 / 8.80803e-11`、全て`1e-8`以内。
元float64列の65³の17件は全て前段と同じ判定差であり、別列のexact計算で全件通過した。
31実装テスト・16artifactテストを再実行して通過した。Q012f2の主計算は正常終了した。
元Q012f/Q012f1の棄却とQ012f1aの限定的受理を保持し、丸め済み方程式の検証を厳密symbolへ一般化しない。
Q012gは全三格子・全1,248 caseを完了して`passed / rejected`と確定した。
12 validity gate、全generic/holdoutの解像性、独立144 caseの一致、53保存後監査テストが通過した。
H1（実評価・固定葉構造）、H2（全48立方対称性）、H3（独立物理三次式）は通過したが、H4/H5は棄却した。
一般方向gateは17³/33³/65³で64/64、64/64、61/64。65³のindex 34/51が三次傾き上限、52が最小振幅比に不達だった。
有限振幅gateは64/64、32/64、0/64。65³の`.032`全32方向で三次欠陥が二次より大きく、最大比5.834018だった。
全holdoutはpositiveだが、65³では両モデルのW葉・W(R)葉の質量成分が全64 caseで上限を超えた。
3運動量・Phi(W)−Wの保存差はholdoutで上限以内。質量葉の集計誤差は後続Q012g1で、欠陥比とは分けて診断した。
特殊24方向/格子のfitは未解像でnullを保持した。全準備配列は三格子×worker/mainの全6組で元fiberと一致した。
主計算PID 29360／handle 89608とworker PID 33368／handle 81813はいずれもexit 0で終了済み。再pollしない。
Q012g1は全三格子・192 caseを完了して`passed / accepted`。8 validity gateとH1が全て通過した。
旧recordと1,152 fieldを同一に再現し、31,104 population和・4,608成分のexactな符号付き分解を全数監査した。
独立GMP workerの全48 case・288 field・1,152成分・12対照もprimary整数方式と厳密一致した。
元超過256成分は65³の両degree・W/W(R)葉の質量であり、exactな場の誤差と総和だけの交換後は全件が元上限以内だった。
全成分の最大は元集計`5.46839381544819e-13`、exact場誤差`8.804966277311955e-17`、総和交換後`2.1195324866078255e-16`。
65³の基準側集計項はsite平均`+5.322701185384562e-13`で、葉の差へ負号付きで現れる主要項だった。
場を投影せず、基準・閾値・振幅・方向・map・係数を変更していない。exact場誤差が厳密に0という結果ではない。
実装71、worker監査10、main監査10、親Q012g監査53、計144テストが通過した（204.00秒）。Ruff・整形・compileallも通過した。
worker PID 12416／handle 41088は00:08:34 JST、primary PID 5024／handle 14558は00:39:06 JSTにexit 0で終了済み。再pollしない。
Q012g1の計算は終了済み。最終親`artifacts/q012g1_d3q27_conservation.json`と三childのSHAを設計書・監査テストへ封印した。
検証範囲は192 holdout caseであり、元Q012g全1,248 caseの保存量再診断・再判定へ一般化しない。
Q012g2の[代数オラクル](../docs/D3Q27_CUBIC_DEFECT_ORACLE.md)は全96人工caseで`passed / accepted`。
6方向・二次／三次の12組・1,824係数、全2,976 case値を別記述のFraction式と照合し、6 validityとH1・全数保存後監査が通過した。
係数比較の最大誤差0、case比較と残りidentityの最大誤差`1.6601845766184287e-19`。有理式の残りは0にしていない。
新規71・保存後6の計77テストが通過した。検査側の分数decoderのkey衝突は回帰テスト付きで修正し、正式artifact/sourceは変更していない。
PID 37164はexit 0で終了済み。
[Q012g3](../docs/D3Q27_CUBIC_DEFECT_DIAGNOSIS.md)では、元の全一般方向・holdoutの960 caseと独立192 caseを事前登録した。
独立側にはH4の34/51/52、holdoutの各格子最悪3/16/21も含める。定数項・低次数の丸めも保持して九次までと有理式の残りを診断する。
H1は元floor以内の再構成、H2はholdoutのvector相対誤差1e-3と比判定、H3は元fit/判定の再現で分ける。
登録commit `8260488`の後に次数別helperを実装し、小格子45件と先行オラクル77件、計122テストが通過した（17.90秒）。
primary/独立方式の全係数比較、非単位density・非零momentum定数、非立方格子、誤factor・G3欠落・C0削除・末尾成分改変を検査した。
続いて保存記録監査55件を追加し、新規100件＋Q012g2の77件＋Q012g1 main監査10件、計187件が通過した（90.54秒）。
元記録のnormを注入した判定式の回帰でも、H4の3不合格、欠陥比81不合格・37悪化を保持した。実次数別予測の成功ではない。
負のGram推定値、独立vector不一致、H1不成立は整合した失敗記録として保持し、validity/科学的gateを分離する。
runnerを実装し、元record/fieldのfresh再生成、holdout exact照合、方向別の排他的保存と全child再読を接続した。
主方式の全振幅診断後にtail用の一時配列を解放してから独立方式を作り、必要な全vectorは比較完了まで保持する。
初回34実行器テストは245.51秒で通過した。別directoryのreplayを開始前に拒否する検査を追加し、35件と先行177件、計212件が279.46秒で通過した。
commit `7412b46`でsourceを封印後、workerを開始した。17³の全21方向・64 case・42 profile・1,533全vector比較が通過した。
元384 field・128欠陥metadataとholdoutのexact集計を照合し、21方向の保存物も全てgridと一致した。
この部分集合でH1/H2/H3・Gram・独立照合の不達は0。再構成差の最大は`5.722781890795384e-15`で、元floor `5.502608491768111e-13`以内。
追加11テストは独立OLS式・1,664 Gram集計・末尾case/係数改変を含み、13.35秒で通過した。
33³の全21方向・64 caseも完了し、全保存後監査、両方式のH1・全vector比較、H2/H3・Gramが通過した。
33³の最大再構成差は`1.5336496636226352e-14`、元floorは`1.4882165908113665e-12`。
登録holdoutの元10件の半減不達・4件の悪化を保持して再現し、最大比`1.316172134164264`の反例も維持した。
33³の追加11テストと17³の回帰11テスト、計22件が24.93秒で通過した。
その後65³の一般11方向・44 case、803全vector比較も監査した。反例34/51は高次寄与を含む傾き上限超過、
反例52は傾きが区間内での最小振幅比超過と分け、元H4の不合格を全件再現した。追加10テストが4.08秒で通過した。
続いて65³全64 case、最終worker192 caseの全監査と正常終了を確認した。
全126 profile、元1,152 field・384欠陥、4,599全vector比較、holdout60 caseのexact記録照合が通過した。
最大再構成差`4.2263693498373226e-14`は対応する元floor`4.1140092794350784e-12`以内で、全H1/H2/H3が成立した。
65³の最悪例index21・`.032`は、元比`5.834017983080117`、予測`5.834017984274533`で、旧H5はfalseを保持した。
四次までの欠陥予測ではvector相対誤差約91.70%、六次まででは`6.58493e-5`、九次まででは約`3.28809e-10`だった。
以上は独立workerの段階の結果である。その後main全960 caseの最終監査と、登録192 caseの全primary対応も完了した（冒頭参照）。
検証済み保存量集計を後続の実LBM監査へ採用する条件も明記した。旧record・旧判定を保持し、新しい高次chartはまだ構築しない。
H4の3方向とH5の欠陥比不達の元記録を、今回の再現成功と分離する。修復の検証は未実施である。
Q012eの登録振幅`.008, .032`の二次モデル有限sample受理と元Q012d/Q012d1の棄却を保持する。
3DのSSM存在・連続球の実用半径やTTの優位性は未認証である。

| 課題 | 到達点と次の行動 |
|---|---|
| 別系統での研究基盤 | `tt_invariant_manifold_lbm`。既存tciから独立。理論整理と詳細設計を保存 |
| D2Q9の縮約 | 固定保存量葉のdense quadraticからquarticまで構築。残差・限定領域でのshadowingを検証 |
| 存在・半径 | Q007系の固定17²・指定map／norm／tubeについて認証。実用半径・grid-uniform性へ一般化しない |
| TT表現 | Q008/Q010、forced系Q011gの登録TT候補は自然Fourier sparse baselineに敗れた。疎表現を採用 |
| repaired mapの高次滑らかさ | Q011no ordinal 149は個別区間分割で改善なし。Q011np位相監査、degrees 34--90は未解決 |
| D3Q27基礎 | Q012a accepted。216有理moment、48立方対称操作、z独立D2Q9 lift、center二次残差次数3 |
| D3Q27スペクトル | Q012b accepted。16 pathのprefix、二重shear平面、odd unit count 4／even 7。全方位・normal attractionの証明ではない |
| D3Q27非零波数preflight | Q012c passed/rejected。36条件・56,844 block pair、jointly viable 0/12 family。104座標・omega=1.2は二次計算のみ3格子通過 |
| 元D3Q27 damping試行 | Q012c1 failed/inconclusiveを保持。4/108条件後に108×108 SVDが不収束 |
| D3Q27 damping修正検証 | Q012c1a accepted。108条件・332,748 pair。例外時SVD代替1件、四階型9/16 familyが3格子で通過。選択eta=.02, omega=1.5 |
| D3Q27二次W/R | Q012d passed/rejected。全3,081 pair・実座標化・独立Hessian・64方向の次数・48 trajectoryは通過。R2なし対照の4方向が傾き上限2.1を超過 |
| D3Q27対照の次数別診断 | Q012d1 passed/rejected。560 sampleを別プロセスで全再現。元振幅域のP3 vector誤差最大3.38%で2%基準を棄却、P4誤差最大7.09e-6。元傾きはC3で再現、小振幅80本の次数は約2 |
| D3Q27有限振幅 | Q012e accepted。224 case・8,416 iterate。選択値.032を独立holdoutで確認。.128は絶対誤差基準内だが半減基準30/32件不達。振幅1以上は初期正値性不合格 |
| D3Q27三次preflight | Q012f passed/rejected。全246,480 triple・578,760 column、17³は通過。33³/65³のH3共役誤差は7.88e-8／5.39e-6で上限1e-8を超過。65³は272件の残差も不合格 |
| D3Q27入力／精度診断 | Q012f1 passed/rejected。5,832 arm、全二次pair・全三次forcingは検証済み。65³のpaired/refined共役誤差8.80803e-11、外部残差は17件不合格。固定96 tripleを別プロセス照合 |
| D3Q27厳密残差診断 | Q012f1a accepted。65³の全648 caseのexact残差を独立整数演算で全数照合。元37件の不合格は残差積和の丸めで説明され、全3種のexact gateは違反0。元判定は保持 |
| D3Q27修正三次preflight | Q012f2 accepted。全246,480組・578,760列のexact残差・full式・共役が通過。独立972組、全行/全fiberの保存後監査も通過。元float64の17件は保持 |
| D3Q27三次W/R | Q012g passed/rejected。全1,248 case、12 validity、独立144 case、53監査テスト通過。H1–H3成立、H4の65³3方向とH5の有限振幅/質量葉が不達 |
| D3Q27保存量診断 | Q012g1 accepted。全192 case・1,152 field・4,608成分、独立48 caseと12対照を監査。元超過256成分を集計誤差へ切り分け。144テスト通過 |
| D3Q27次数別欠陥の代数オラクル | Q012g2 accepted。全96人工case・1,824係数・2,976値、独立Fraction式・全数保存後監査・77テスト通過。実LBMの悪化原因を説明した結果ではない |
| D3Q27次数別欠陥診断 | Q012g3 accepted。全960 case、独立192 caseとの一致、全入力/source・全保存後監査が通過。旧3次数不合格・81半減不達・37悪化を再現し、元の棄却は保持 |
| D3Q27四次構造census | Q012h0 accepted。全104座標・3格子・次数2/3/4の全joint/coordinate histogramが独立processで一致。四次1,663,740 block組・5,160,610列/格子。数値rank・solveの実行可能性は未評価 |
| 次の主課題 | Q012h2 H1の全5,478列で514列の独立一致が不合格。Q012h2aで全対象の算術精度を診断。全104座標・三格子、現行W2/W3と自然Fourier sparseをbaselineに残す |
| さらに必要 | 実用振幅・高次／存在認証、3D sparse／TT費用評価、Taylor–Green、force／wall。有限sampleのrollout／正値／保存はQ012dで検証済み |

Q005の元isotropic候補の棄却、Q006iの元保存量閾値による棄却、TT圧縮の棄却を保持する。
Q012の着手条件は後続の修正候補と個別gateを照合して判定した。詳細な対応は
[Q012a設計](../docs/D3Q27_FOUNDATION.md)にある。高次非共鳴の個別signature監査が
3D基礎代数の唯一の前提である、という直列順序にはしない。
Q012bのcutoffとその限界は[スペクトル検証結果](../docs/D3Q27_SPECTRAL_GATE.md)を参照。
Q012cの共鳴・near-Nyquist・悪条件化の切り分けは
[二次preflight結果](../docs/D3Q27_QUADRATIC_PREFLIGHT.md)を参照。
Q012c1の数値backend障害と保存した行列は[damping結果](../docs/D3Q27_DAMPING_REPAIR.md)を参照。
Q012c1aの独立再計算・選択候補・不採用の残差失敗は
[SVD代替と全条件結果](../docs/D3Q27_SVD_FALLBACK.md)を参照。
Q012dの構築・7仮説通過・負の対照失敗と次の診断は
[実座標quadratic chart結果](../docs/D3Q27_QUADRATIC_CHART.md)に保存した。
Q012d1でのnorm傾きとvector精度の切り分け、独立全数replayは
[負の対照の次数別診断](../docs/D3Q27_NEGATIVE_CONTROL_DIAGNOSIS.md)にある。
Q012eの同一初期状態比較、有限sampleの使用範囲と絶対精度の区別は
[有限振幅結果](../docs/D3Q27_PRACTICAL_AMPLITUDE.md)に保存した。
Q012fの全数coverage、二種類の不合格、例外時SVD代替と再現範囲は
[三次preflight結果](../docs/D3Q27_CUBIC_PREFLIGHT.md)に保存した。
Q012f1の二入力×三solver、残った不合格と残差評価の精度差は
[入力／精度診断](../docs/D3Q27_CUBIC_PRECISION_DIAGNOSIS.md)に保存した。
Q012f1aの元判定・厳密判定の分解、全648件の独立照合と丸め済み方程式への限定は
[厳密残差監査](../docs/D3Q27_EXACT_CUBIC_RESIDUAL.md)に保存した。
Q012f2の全数結果、固定済み実装、保存後監査と限定された主張範囲は
[修正候補の全三次preflight](../docs/D3Q27_REFINED_CUBIC_PREFLIGHT.md)に保存した。
Q012gの実座標評価、人工写像、三格子の次数・有限振幅比較と独立再現範囲は
[三次W/R評価の事前登録](../docs/D3Q27_CUBIC_CHART.md)に保存した。

再現コマンド（repository root）:

```powershell
python -m pytest tests/test_d3q27_foundation.py tests/test_d3q27_spectral.py tests/test_d2q9.py tests/test_manufactured.py -q
python -m research.q012a_d3q27_foundation --output research/replays/q012a_d3q27_foundation.json
python -m research.q012b_d3q27_spectral --output research/replays/q012b_d3q27_spectral.json
python -m pytest tests/test_d3q27_quadratic.py -q
python -m research.q012c_d3q27_preflight --output research/replays/q012c_d3q27_preflight.json
python -m pytest tests/test_d3q27_damping.py tests/test_d3q27_damping_artifact.py tests/test_d3q27_svd_fallback.py tests/test_d3q27_damping_complete.py -q
python -m research.q012c1a_d3q27_damping --output research/replays/q012c1a_d3q27_damping.json
python -m pytest tests/test_d3q27_chart.py tests/test_d3q27_chart_artifact.py -q
python -m research.q012d_d3q27_quadratic_chart --output research/replays/q012d_d3q27_quadratic_chart.json
python -m pytest tests/test_d3q27_negative_control.py tests/test_d3q27_negative_control_artifact.py -q
python -m research.q012d1_d3q27_negative_control --worker-output research/replays/q012d1_worker.json
python -m research.q012d1_d3q27_negative_control --output research/replays/q012d1_diagnosis.json --replay research/replays/q012d1_worker.json
python -m pytest tests/test_d3q27_amplitude.py tests/test_d3q27_amplitude_artifact.py -q
python -m research.q012e_d3q27_amplitude --worker-output research/replays/q012e_worker.json
python -m research.q012e_d3q27_amplitude --output research/replays/q012e_amplitude.json --replay research/replays/q012e_worker.json
python -m pytest tests/test_d3q27_cubic.py tests/test_d3q27_cubic_artifact.py -q
python -m research.q012f_d3q27_cubic_preflight --worker-output research/replays/q012f_worker.json
python -m research.q012f_d3q27_cubic_preflight --output research/replays/q012f_cubic.json --replay research/replays/q012f_worker.json
python -m pytest tests/test_d3q27_cubic_precision.py tests/test_d3q27_cubic_precision_artifact.py -q
python -m research.q012f1_d3q27_cubic_precision --worker-output research/replays/q012f1_worker.json
python -m research.q012f1_d3q27_cubic_precision --output research/replays/q012f1_diagnosis.json --replay research/replays/q012f1_worker.json
python -m pytest tests/test_d3q27_exact_residual.py tests/test_d3q27_exact_residual_artifact.py -q
python -m research.q012f1a_d3q27_exact_residual --prepare-output research/replays/q012f1a_prepared.json
python -m research.q012f1a_d3q27_exact_residual --worker-output research/replays/q012f1a_worker.json --prepared research/replays/q012f1a_prepared.json
python -m research.q012f1a_d3q27_exact_residual --output research/replays/q012f1a_exact.json --prepared research/replays/q012f1a_prepared.json --replay research/replays/q012f1a_worker.json
```

成果物再生成では時刻が変わるためファイル全体hashは変わる。科学的な再現照合では、
helper／runnerのsource hashと数値結果を比較する。Q012e/Q012f/Q012f1のcycleにはworkerのprocess ID・
metadata込みhashが含まれるため、caseごとの数値・係数配列hashを照合する。
Q012fの全tripleはgzip JSONLに保存し、圧縮fileのbyte hashと展開record列のdigestを区別する。
Q012f1も同形式で選択全324組/格子の6 armを保存する。全三次tripleの保存とは区別する。
Q012f1aは65³・二入力の648個の丸め済み行列問題をNPZへ保存し、全entry・archive byte hashを
照合する。時刻・PID・出力名を含むdigestではなく、再現した配列と各caseの有理数proofを比較する。
metadataを含まない旧experimentについては、そのresult digestも使用できる。
封印した既存artifactを上書きしないよう、再実行は別の`research/replays/`へ出力する。
元Q012c1を再実行すると数値障害を記録して終了code 1となる。これは事前登録された
108条件が未達であることを示す意図的な不合格で、例外の隠蔽や部分結果の受理ではない。
