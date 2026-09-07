# Q012f2: paired/refined候補の全三次preflight

## 2026-09-07 事前登録

Q012f1aは65³の選択324組・二入力の648個の丸め済み外部方程式をexact演算で照合し、
元37件の判定差を残差評価の丸めへ切り分けた。この診断を全三次組へ外挿せず、
Q012f2で同じ修正候補の全数preflightを実行する。元Q012f/Q012f1の棄却は変更しない。

### 固定する対象

- 四階filter付きmap `omega=1.5, eta=.02, power=2`、奇数格子17³/33³/65³。
- 全26第一shell波数・104実座標・78入力block。二重shear平面を個別固有ベクトルへ分裂させない。
- 質量と3運動量を固定した不変葉。zero-wave補正は保存momentを持たないkinetic成分に限る。
- 各格子82,160 block triple・192,920対称monomial column、合計246,480組・578,760列。
- Q012f1の`paired_input`でH2/G2を共役対称化し、全二次方程式・構造を元の閾値で再検証する。
  二次のraw再構築・paired配列・全3,081 pairの監査を封印したQ012f1と一致させる。
- 三次forcing・対称積・波数選択・Taylor係数規約はQ012fを保持する。
- solveはQ012f1のSylvester初期解と、128-bit残差による固定3回の補正をそのまま使う。
  収束した例だけを選ぶ、補正回数をcaseごとに変更する、三次応答を後から共役平均することはしない。

### 全件で保存する判定

元SVDのrank・condition診断を同じ行列でfreshに行い、paired入力に対するSVD参考解も記録する。
これは元raw入力のQ012fの結果とは区別する。既存の例外時だけのgesvd代替を維持し、
正常終了した不合格によるbackend切替は行わない。

- rank threshold `100*eps*operator_dimension*sigma_max`、condition上限`1e8`。
  singular compatible/incompatibleとill-conditionedを、残差の大小だけで通過扱いしない。
- refined解Xの外部残差`A X - X D + F`を、Q012f1aで検証したIEEE754 decodeと整数積で
  **全246,480組**についてexactに評価する。GMP有理数積による独立照合を後述の972組で行う。
- 元float64残差列、R64のexact norm列、exact Rと元分母／exact分母／十進定数の3列を保持する。
  3つのexact gate全てで上限`1e-10`を要求し、元float64 gateを事後に書き換えない。
  二乗normの有理数比較を使う。表示用の近似normを厳密判定へ逆流させない。
- full-population homological残差は、元の計算式と上限`1e-9`を保持する。
  外部射影後のexact残差が小さくても、full方程式の不合格を救済しない。
- symmetric-subspace invariance、external-subspace、graph gauge、zero-waveの
  H3/forcing保存momentのscaled誤差上限は`5e-12`を保持する。
- forcing/H3/R3の全共役fiberを、虚部を捨てる前に上限`1e-8`で判定する。
  内部acoustic±の交換、反対出力波数、全partnerの一対一coverageを確認する。
- R128のcomplex128格納値とexact Rとの差は、exact分母に対して`1e-24`以内を照合する。
  この補助検証を厳密LBM symbolや128-bit全桁の保証と呼ばない。

candidate通過は数値rank・condition、全3 exact外部残差列、full方程式、構造の同時通過とする。
元float64不合格の件数・全ordinalは別に保存する。誤差評価の異なる列を混ぜて集計しない。

### 独立性と前段との一致

1. Q012fの既知の非対角複素三次解・全対称積pattern・特異/near-resonant負の対照、
   Q012f1の固定補正対照、Q012f1aの全10 exact対照を再実行する。
2. 各格子8方向（Q012f seed `2026090719`）で、全forcing fiberのcontractionを独立な
   物理空間式と比較し、相対誤差`1e-8`以内を要求する。封印したQ012f1のpaired全forcing
   配列hashと方向別数値にも一致を要求する。
3. Q012f1の共通選択全324 ordinalを固定して別プロセスで全二次入力からfreshに再構築する。
   三格子で972組。行列・forcing・refined解・応答・固定補正履歴の数値/hashを主計算と一致させる。
   exact演算だけは主計算の整数kernelを使わず、GMP有理数積とする。全proofも一致を要求する。
   これは972組の独立再現であり、全246,480組の別プロセス再実行ではない。
4. 同じ324組/格子の値を元Q012f1のpaired/refined armとも全件照合する。
   65³の全324 exact proofはQ012f1aのpaired行とも一致させる。
5. 全recordを順序付きlossless gzip JSONLへ保存し、元/新gate、件数、極値、失敗familyを
   保存行から再集計する。解の大きさはraw三次微分・orthonormal Fourier global-l2規約を明記する。
6. 全入力triple・出力波数・forcing/H3/R3 Taylor fiberをpickle不要のNPZへ保存し、全entryの
   shape/dtype/bytes/hashとarchive byte hashを照合する。疎fiberで保存し、巨大な物理W3や
   104⁴のdense実R3は作らない。保存係数をQ012gで使う前に評価器を別途検証する。

### 実行・費用・失敗時の扱い

メモリ使用を抑えるため格子を順に処理し、全recordを逐次圧縮保存する。
各格子の保存が完了したらmetadata付き結果を封印する。wall/CPU時間と保存bytesを報告する。
これはpreflightの実費記録であり、TT対sparseやonline評価のbenchmarkではない。

数学的不合格でも残りの組を省略しない。予期しない実行障害なら例外と到達ordinalを保存し、
その格子をincompleteとして残す。未実行組や未完の検証を成功扱いしない。
既存出力を上書きしない。観測timeoutだけで再起動せず、live processは同じhandleで継続確認する。
部分recordを受理せず、別runが必要なら原因と別出力名を明示する。

### 総合判定

封印入力chain、全対照、二次入力の再構築、三格子全coverage、有限性、全数保存/再集計、
全forcingの独立検証、972組の独立GMP再現、元選択armとの一致、R128照合をvalidityとする。

- H1: 全三格子・全246,480組でcandidateのrank/condition・exact外部残差・full方程式・構造が通る。
- H2: 全三格子・全578,760列でforcing/H3/R3の共役実構造が通る。

validity通過かつH1/H2通過ならaccepted、validity通過で仮説不合格ならrejected、
validity不通過ならinconclusiveとする。各格子単独の結果と三格子共通の結果を区別する。
acceptedならQ012gの三次W/R評価器・残差次数・有限振幅比較へ進む。
rejectedなら失敗family全体を分類し、未解決機構を次問にする。
SSM存在、連続球・grid-uniform半径、有限振幅改善、TT費用優位性はこのgateで認証しない。

## 実装と再現

事前登録commitは`44b12a0`。新規31テストで、三格子のordinal 0に対する前段との全数値一致、
整数/GMP kernelの一致、全candidate gate、数学的棄却とcoverage不足の区別、逐次保存の
読み戻し、実行例外・壊れた部分archive・上書き拒否を確認した。
これは全数preflightの結果ではなく、実装開始時の検証である。

次の二つは別processで実行する。主計算は三格子を順に処理し、各格子にresult JSON、
全recordのgzip JSONL、全疎fiberのNPZを保存する。途中で部分fileがある場合も上書きを拒否する。

```powershell
python -m pytest tests/test_d3q27_refined_cubic.py -q
python -m research.q012f2_d3q27_refined_cubic --worker-output research/replays/q012f2_worker.json
python -m research.q012f2_d3q27_refined_cubic --output research/replays/q012f2_refined.json --replay research/replays/q012f2_worker.json
```

source sealと全科学的record/配列hashで再現を照合する。時刻、PID、出力名、wall/CPU時間は
再実行で変わるため、それらを含むfile/cycle digestの一致を数値再現の条件にはしない。
