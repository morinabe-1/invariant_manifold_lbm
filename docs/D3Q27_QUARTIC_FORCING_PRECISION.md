# Q012h2a: 四次forcingの算術精度診断 — 事前登録 2026-09-08

## 問いと固定入力

Q012h2 H1では全三格子・5,478列の計算と保存後再計算が完了したが、元の相対差gateに514列が不合格だった。
**不合格は算術精度に起因するか。全対象で、同じTaylor入力から形成した四次forcingを独立に一致させられるか**を問う。
本書をcommitしてから新しい高精度forcingを実装・評価する。旧7 sourceと数値結果は変更しない。

- 親H1 manifest: `research/artifacts/q012h2_d3q27_quartic_forcing.json`、ファイルSHA256
  `b2ec4ed701a677c6ddbca1016b45c3de3d4861ee9c20d98592bfb262e3d58df6`。
- 全列再集計: `research/artifacts/q012h2_d3q27_quartic_forcing_diagnostics.json`、ファイルSHA256
  `6f6c72eef1f8d93f6083ae0e88ce52a205daacad880e163df46bb913600004a3`。
- S0の698組・1,826対称列/格子、N=17,33,65、全78 block・104座標を全て保持する。
  既存のfresh/paired二次入力と全192,920三次fiberを使用し、各格子で入力の全hashと基底・Lambdaの一致を監査する。
- `omega=1.5, eta=.02, power=2`、固定保存量葉、shear平面、Fourier規約、7項formulaを変えない。
  元不合格182/174/158列、特に17³のfloor以上の8列も全て残す。微小値を0へ射影しない。

## 登録した計算方式

1. **旧binary64方式の再現**。旧sourceと保存物の全entryを再監査し、全514不合格と元の列別値を再現する。
2. **全算術をGMP 128/192 bitで評価する主方式**。丸め済みのV, Lambda, H2/H3, G2/G3を、各complex成分の
   binary64値を正確に表す数へ変換する。Taylorからrawへの整数factor、moment和、B/C/D、7項合成を当該精度で行う。
   途中でbinary64のmoment contractionへ戻さない。全lower-order配列を保持し、GMPへの変換はtuple単位でよい。
3. **GMP 128/192 bitの独立方式**。4 labelled nilpotent変数へ元Taylor単項式を直接代入し、
   逆密度級数とW3(R3)を合成する。主方式の7項kernel・raw-factor変換・moment contractionを呼ばない。
4. **moment形成だけを変更する診断arm**。VおよびH2/H3のraw momentを、元Taylor値と整数factorから192 bitで形成し、
   moment vectorを一度だけcomplex128へ丸める。残りの主方式のB/C/D・合成・位相/filter計算はbinary64のままにする。
   このarmが全算術高精度方式と一致するかで、moment形成だけによる説明を検査する。一致を事前に仮定しない。

全算術GMP方式では、整数速度と格子サイズ、保存されたbinary64のweight/omega/etaを入力とする。
weightを別の有理数へ置換せず、Nの平方根・pi・位相・filterは指定精度で計算する。
Lambdaとlower-order係数を高精度で再solve・再分類しない。厳密symbolや真の多様体を計算するという意味ではなく、
**丸め済みlower-order係数を固定した式の形成精度**を比較する。
moment-only armは元binary64の位相/filter/factorを保ち、全GMPとの差から他の算術段階の寄与も残す。

## 保存・検証・判定

- 主・独立方式を実在する別processで行い、128 bitと192 bitを全698組/格子で評価する。
  両精度の全F4、collision/composition、主方式の7項、moment-only arm、全元列との誤差・判定を保存する。
  高精度値はその有限二進値を損失なく復元できる形式で保存し、complex128への丸め後の値も別に保存する。
- 両方式の192 bit F4、およびcomplex128化したF4に、元の
  `norm(diff)/max(1e-14,norm(reference)) <= 1e-8`を全列で要求する。
  各方式の128→192 bit相対差は同じfloorで`1e-10`以内を要求する。精度一致を厳密誤差boundとは呼ばない。
- moment-only arm対192 bit主方式も元の`1e-8`で全列比較する。
  これが不達なら「moment形成だけが原因」という仮説は棄却し、全精度armの結果と分離する。
- 旧H1の固定20物理照合列/格子について、高精度から丸めたF4と保存済みの物理格子結果を、全off-wave漏れ込みで
  同じ`1e-8`以内に照合する。元の5変異（FFT factor、streaming、filter、G2、G3）の非零検出例も全格子で維持する。
- 有理数でmomentが厳密0の人工入力と、0ではない微小momentを持つ人工入力を別に設け、
  微小値の強制0化、raw factorial、複素共役混入、入力外内部座標の欠落、末尾列/成分の改変を検査する。
- 全入力/親/source、全列coverage・finite、全保存値と判定の再構築、実PID/exitをvalidityとする。
  新sourceは正式実行前にcommitする。旧H1 source・artifactと元の不合格は上書きしない。

資源条件は各grid/route開始時RAM>=4 GiB・disk>=6 GiB、peak working set/private commit各3 GiB、
各grid/route実時間4時間、本診断の新規保存物合計2 GiB。3格子を同時に保持せず、格子・方式を順に実行する。
2精度・入力監査・保存・再読を含めて測定する。超過/欠測では部分結果を保存してinconclusiveとし、対象や閾値を変えない。

全列独立一致と精度安定性、物理照合、validityを満たせた場合にのみ、高精度形成F4をQ012h2のH2への候補入力とする。
moment-only仮説の成否は別に報告する。旧binary64 H1の不合格を受理へ書き換えない。
H2の実operator解、solveを含む資源pilot、全四次chart、元振幅の改善、SSM存在、自然疎表現とTTの費用比較、
物理benchmark・force/wallは引き続き未完了である。

## 実装検証 2026-09-08 — 正式計算前

七項方式・独立nilpotent多項式方式をGMP 128/192 bitで実装した。
元のbinary64係数を正確に取り込み、整数raw factorを高精度化の後に掛ける。
独立方式は元Taylor単項式と逆密度級数から合成し、主方式のmoment・raw factor・七項kernelを呼ばない。
内部生成先は全104座標のまま。人工入力だけを小さくし、実入力loader・S0の698組/格子は変更しない。

保存形式は有限二進数の符号付き整数仮数と2の指数であり、両精度の全成分を損失なく復元する。
complex128への丸め後の配列、主方式の七項、moment-only armも別に保存する。
各方式を別の実processで実行し、全entryを保存後に再計算する。別CLIでは入力からfreshに再構築する。
元H1の全entry・全514不合格と固定20物理列/格子も再監査する。
5変異の照合先は元H1に封印された非零witnessとし、新結果から都合のよい例を選び直さない。

新規68テスト、先行H1の実装・全列診断・実artifactの81テスト、計149件が警告error化で通過した（43.56秒）。
人工の全126混合組×両精度、全16対称列、厳密ゼロと`2^-80`の非零moment、raw factor前後の丸め差、
入力外内部座標、複素双線形性、末尾成分改変、精度・coverage・偽PID/異常exit・資源不足の保持を検査した。
Ruff・format・compileも通過した。これらは部品検証であり、実LBMのQ012h2a合格ではない。

正式計算は新しい7 sourceをcommitしてから行う。元の事前登録60行と旧source/保存物は変更しない。
再現コマンド（repository root、新規出力先を使用）:

```powershell
python -m pytest tests/test_d3q27_quartic_mp.py tests/test_q012h2a_d3q27_quartic_precision.py -q -W error
python -m research.q012h2a_d3q27_quartic_precision --output research/replays/q012h2a_d3q27_quartic_precision.json
python -m research.q012h2a_d3q27_quartic_precision --output research/replays/q012h2a_d3q27_quartic_precision.json --audit-only
```

`validate-data`の判定は部品検証に限るShare with caveats。実全列の一致、moment-only仮説、
Q012h2 H2/H3と研究全体の未完了事項は、実行結果が得られるまで受理しない。

## 初回の開始資源条件による停止 2026-09-08

source `c007e72bbc3c43f44c80e3addcb7e5d9f093a9f0`をcommit/push後、正式CLIを起動した。
main PID 28148は、前段S0のread-only再監査child PID 27704の開始資源チェックで停止し、実exit 1を確認した。
console上の原因は`registered starting RAM/disk minimum unavailable`。
子processの開始時counterは旧監査器から取得できず、失敗recordの`resources=[]`を後の測定で埋めない。
新しいGMP forcingは0組・0列で、ZIPも未生成。Q012h2aは`inconclusive`、H2/H3は未評価のまま。

停止後の別probeではavailable RAMが4,174,069,760 bytes（約3.89 GiB）、次のprobeで4,157,419,520 bytesだった。
必要な4,294,967,296 bytesを下回っている。後者のdisk空きは14,487,965,696 bytesで6 GiBを上回った。
これは停止後の外側観測であり、失敗したchild開始瞬間の不足量を示す記録ではない。
他のprocessの終了・資源閾値・BLAS環境・対象caseの変更は行わない。

保存した[初回停止record](../research/artifacts/q012h2a_d3q27_quartic_precision_failure.json)は537 bytes、file SHA256は
`9c696615aef6936ca364a326fbfc88aad5320a09650615a5a40cfe25a0034998`。
元source/不合格の上書きや、資源が足りないままでの再起動は行わない。

再試行に向け、外側CLIにも親監査前の測定付きpreflightを加え、例外後の外側観測をchild-start証拠と別に記録する。
同じ診断名の`_attempt02`等の出力では、先の停止recordも含めた全保存量を2 GiB上限へ集計する。
これは実行・記録の補強であり、数値4 moduleは`c007e72`から不変であることをテストで照合する。
追加5件を含む新規73件と先行H1の81件、計154回帰テストが43.58秒で通過した。Ruff・format・compileも通過した。
開始RAMの回復を確認後、新しい出力名で全三格子・全対象を再実行する。初回recordはそのまま保持する。
`validate-data`での実験の評価はNeeds revision（前段監査未完了・開始時測定欠落）。数値仮説の棄却や受理ではない。

## RAM回復後の再実行と正規化順序の修正 2026-09-08

ユーザーによるRAM解放後、source `95a002e3a932cff18935c54e54361a6f1dc3d2c0`のまま、
`_attempt02`を別の出力先として起動した。mainの開始available RAMは5,979,512,832 bytesで4 GiB以上だった。
前段の全S0・旧H1保存値のfresh再監査を通過し、旧514不合格も全列で再現した。
新17³ primary（PID 36488）は全698組・1,826列の128/192 bit値を保存し、全entryの再計算を通過した。
一方worker（PID 14312）は7組・25列の保存後、8組目の保存前検証で停止した。main PID 30092の実exit 1を確認した。
全診断のmanifestは未生成で、Q012h2aは引き続き`inconclusive`。主方式だけの完了を独立一致へ昇格させない。

停止原因は`saved F4 collision/composition identity differs`だった。
worker開始RAMは5,994,995,712 bytes、diskは14,515,384,320 bytesで、全記録の資源条件を満たしていた。
主方式の全保存後再計算までの実時間は79.68秒、主・workerの記録の最大working setは488,902,656 bytes、
最大private commitは1,783,062,528 bytes。今回はRAM不足ではなく、正規化と丸め順序の実装不整合である。

停止tupleはordinal 7の`(0,0,77,77)`、該当する対称column 1は座標`(0,1,103,103)`、軌道因子は`sqrt(2)`。
元独立方式はrawの差を取ってから軌道因子を掛け、保存するcollision/compositionには各々因子を掛けていた。
有限精度では`fl(s*fl(C-D))`と`fl(fl(s*C)-fl(s*D))`は一般に同一ではない。
同じ全lower-order入力を再構築して、128 bitで22成分、192 bitで21成分の差を再現した。
その最大列相対差はそれぞれ`3.166529495572177e-39`と`1.183372315342952e-58`だった。
これは元の相対誤差gateの不合格ではなく、保存値間のビット単位の恒等式チェックとの不整合である。

修正は独立方式のblock正規化だけに限定し、**正規化したcollisionとcompositionから保存F4を定義する**。
raw nilpotent展開・moment・元Taylor入力・collision/compositionの値、主方式・moment-only armは変更しない。
検証側の厳密一致条件、`1e-8/1e-10`、floor、対象、資源条件も変更しない。旧sourceはGit履歴に残す。
歴史的な資源修正`95a002e`が`c007e72`の数値4 moduleを変更していなかったことを、両commit間の検査として保持する。
今回の修正についても、独立方式のgroup関数以外が`95a002e`と同一であることを別に検査する。

同じ不整合は非単位軌道因子を持つ人工入力の3パターンでも再現した（修正前3不合格・1通過）。
修正後はこれらと128/192 bitの旧順序との差、反復blockの全保存payloadを含む関連14検査が通過した。
全件再実行前に回帰検証とsourceのcommitを行う。次の出力名は`_attempt03`とし、途中のprimaryを流用しない。

保存物は初回537 bytesに加えて今回の5ファイル36,992,495 bytesで、計36,993,032 bytesを保持した。
以後も再試行を含む診断全体の2 GiB集計へ含める。以下のfile SHA256を回帰テストへ固定する。

| attempt02保存物のsuffix | file SHA256 |
|---|---|
| `_failure.json` | `9e7debac708bd8a8c707fb42111a0b5da43fc40bb2f3c96d74165849ffa8ef54` |
| `_n17_primary.json` | `340913c9769a57d123fe51226abacf7fca98454baca73b888ed312f059101758` |
| `_n17_primary.zip` | `04ba4f0bdf68898aaa0bd9008e4f4dc614ed051103d3dca08a6601b420471da6` |
| `_n17_worker_failure.json` | `4bd9ec19e938ad3f6a65a151d2753e6684e828fcc9efc1bdaf0f32f9cda9481d` |
| `_n17_worker.zip` | `b82d3e63d9abb94293ef5eb8901d04c8974b677206c9db4b5841611f41d87b9f` |

`validate-data`による評価はNeeds revision（全三格子の独立方式未完了）。修正の部品検証と正式実験の判定を分離する。
高精度forcing候補、moment-only説明、H2/H3、四次chartと元振幅の改善はまだ受理しない。

修正後の全精度対照82件、停止artifactと実停止tupleの再構築4件、先行H1の81件、
計**167テスト**が警告error化で通過した（67.32秒）。部分archiveの全entryも再読・検証した。
これは実装と停止原因の検証であり、未実行のattempt03の合格を意味しない。

## attempt03の主計算結果 2026-09-08

正規化順序を修正したsource `3ec22a16ac357e9f23017e25f8fc1d02b4b07fd5`をcommitしてから全対象を再実行した。
main PID 33868の実exit 0を確認した。三格子×698組・**全5,478列**の二方式・二精度を保存し、
各方式で全entryを再計算した。最終manifestを再読して全列の診断・集計・判定が再構築できることも確認した。
別CLIによる全入力・全entryのfresh再監査、および保存値を分数として扱う独立な合否確認は続けて実行する。

| 格子 | 192 bit二方式の最大相対差 | 128→192 bit最大差（両方式） | moment-only最大差 | 物理照合最大差（漏れ込み） |
|---|---:|---:|---:|---:|
| 17³ | 9.09417e-57 | 1.66661e-37 | 4.54395e-15 | 2.48075e-15 |
| 33³ | 3.65991e-56 | 6.88525e-37 | 2.86024e-14 | 6.08569e-15 |
| 65³ | 2.14332e-55 | 3.01519e-36 | 1.11033e-13 | 1.29112e-14 |

全列で登録した各上限を満たした。192 bit F4をcomplex128へ丸めた後の二方式の差は、全三格子で厳密に0だった。
旧182/174/158列の不合格は全件保持・再現した。固定20物理列/格子、全5変異/格子も通過している。
moment-onlyの一致は、この**固定入力・全pilot・登録精度条件**では元primaryのmoment形成だけの変更で十分だったことを支持する。
他の演算の丸め誤差がゼロ、一般の格子・係数でもこれだけが原因、という結論にはしない。

正式6 process（17³ primary/worker: 36720/20748、33³: 28136/10844、65³: 16216/33856）の実exit 0を取得した。
新precision計算の最大peak working setは549,367,808 bytes、最大peak private commitは1,842,696,192 bytes、
最長grid/routeは65³ workerの127.511秒で、各登録上限以内だった。全入力監査・保存・再読を含む。
これはforcing診断のみの測定であり、H2 solveや全四次chartの資源条件の通過とは呼ばない。

[主計算manifest](../research/artifacts/q012h2a_d3q27_quartic_precision_attempt03.json)のfile SHA256は
`e6a853b2176857e217570b26947096ea3325a55095815cdc9527a1b6c50d0189`。
attempt03の13保存物は177,827,201 bytes、初回・attempt02を含む正式計算終了時の全19保存物は214,820,233 bytesだった。
正式run内の算術・実行器82テストは13.50秒で通過した。事前167回帰テストと区別する。

主計算の判定は`validity=passed, high_precision_forcing_candidate=true, moment_only_explanation_passed=true`。
旧binary64 H1は`false`、Q012h2全体・H2・solveを含むH3は`not_evaluated`を維持する。
ここで一致したのは丸め済みTaylor入力の式であり、厳密symbol、真の多様体、精度に関する厳密誤差boundではない。

保存値の追加監査ではGMPのcodec・normを呼ばず、有限二進値をPythonのFractionへ直接復元し、
全5,478列のcollision/composition/F4について合計219,120組のnorm二乗比を分数演算で確認した。
二方式一致、両方式の精度安定性、moment-only、旧値との全8比較、丸め後比較、旧不合格集合を含む。
合否には分数として正確な登録decimal閾値を使い、表示用相対差の照合だけにrelative `3e-15`を用いた。
元514不合格のcolumn集合を維持し、末尾成分・複素成分・floor直上直下・偽合否を検出する対照も通過した。
保存値監査17件を加えた計**184テスト**が警告error化で通過した（247.52秒）。別CLIのfresh再構築とは区別する。
さらに全147,906複素population成分を直接比較し、丸め後一致がnorm二乗のアンダーフローによる見かけではないことを確認した。
この追加1テストも通過した（9.53秒）。検証済みの異なるテストは計185件（保存値監査18件＋先行167件）となる。

## attempt03の最終検証と後続 2026-09-08

別CLI main PID 29016による全入力・全entryのfresh再構築が完了し、実exit 0を確認した。
再監査の6 process（17³: 27932/10076、33³: 28792/5100、65³: 37984/28396）も全て実exit 0だった。
全三格子の入力・二精度・全column・保存判定が再現され、主計算と同じ二つの候補/説明flagがtrueとなった。
新precisionの生成・再監査12 processに限った最大working setは552,452,096 bytes、
最大private commitは1,846,317,056 bytes。前段S0/旧H1の別processを含むrun全体のpeakとは区別する。

[別CLI監査receipt](../research/artifacts/q012h2a_d3q27_quartic_precision_attempt03_fresh_audit.json)には、
実行時に観測したmain PID/exitとCLIの最終出力を保存した。file SHA256は
`e781d8760b0da4b61412f01767f72b52391f2acda6542fa034808ef042d93aa4`、6,036 bytes。
receiptを含む全20保存物は214,826,269 bytes。childの元測定値214,820,233 bytesは保存前の値のまま保持する。
receiptの実process・判定・OS peakを照合する追加1テストも通過した（2.41秒）。検証済みテストは計186件となった。

`validate-data`の評価は**Share with caveats（固定された丸め済み入力の算術診断に限定）**。
高精度形成F4を後続H2の候補入力として受理し、moment-only説明も本登録範囲では支持する。
旧binary64 H1の不合格とQ012gの3次数不合格・81半減不達・37悪化は未修復のまま残す。

次は[既存のH2/H3事前登録](D3Q27_QUARTIC_PILOT.md)に従い、
このmanifestの**192 bit primary F4をcomplex128へ丸めた保存値**を入力に実operatorを求解する。
moment-onlyの一致から、求解入力を別armへ自動で差し替えたり、精度・condition条件を緩めたりしない。
全104座標・三格子・698組/格子・最大432寸法を保ち、SVD/Sylvester-refinement・外部/full残差・gauge・保存量・共役・
求解を含む実資源を検証する。今回のforcing診断だけでH2/H3、全四次chart、SSM存在、TT実費用の優位を受理しない。
