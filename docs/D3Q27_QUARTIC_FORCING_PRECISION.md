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
