# Q012g3: 実LBMの三次欠陥の次数別診断 — 事前登録 2026-09-08

## 問いと開始条件

Q012g1の保存量診断とQ012g2の代数オラクルはそれぞれcommit `97c109c`, `e6ead08`で受理した。
元Q012gのH4は65³のindex 34/51/52で不達、holdoutの欠陥比は81/192 caseで`.5`を超え、
65³・振幅`.032`では全32方向で三次欠陥が二次より大きい。これらの元記録と棄却を保持する。

**問い:** 同じW2/W3の不変性欠陥を、方向別の次数0–9係数と有理式の残りで再構成できるか。
その分解は元の残差次数・有限振幅の欠陥比を再現し、低次数の数値残り、次数間の干渉、
高次の合成項を切り分ける診断として使えるか。
本書をcommitしてから新規helper/runnerを実装する。係数や物理mapを修正してから原因を説明する実験ではない。

前提はQ012gの全結果・元NPZ、Q012g1の全数受理、Q012g2の人工オラクル受理と保存後監査である。
開始前にそれらの封印・source chain・判定を照合し、独立workerを終了してからmainを実行する。
実行中にmap・係数・閾値・方向・振幅を変更しない。失敗・未解像・例外を保存し、0や合格へ置換しない。

## 固定入力と全範囲

- `N=17,33,65`、`omega=1.5, eta=.02, power=2`の同じ四階filter付き修正D3Q27 map。
- 全104実座標、26第一shell、paired H2/G2、元の未投影H3/G3、固定保存量葉。
- 元Q012gの全64一般方向（seed `2026090724`）×振幅`.008,.004,.002,.001`。
- 元Q012gの全32holdout方向（seed `2026090725`）×振幅`.008,.032`。
- 三格子で全960 case。両degree 2/3を比較し、96方向×2 degree×3格子の576組の方向別profileを作る。
- 元の特殊24方向は元fitが未解像のdiagnostic枠であり、本問の次数・holdout仮説には含めない。
  元の288特殊caseとnull fitは保存したままにする。全1,248 caseの再診断とは主張しない。

方向uは元と同じ乱数生成・正規化から再構築し、元のa=t*uと同一であることを要求する。
丸め済みaからa/tで方向を逆算して係数を変えない。
全960 caseを封印されたQ012g `physical_case`でfresh再計算し、元の全recordと厳密一致させる。
続いてW、Phi(W)、W(R)、欠陥を再生成し、元shape/dtype/bytes/hashを全件照合してから診断する。
同じ場を再現できなければ、別の場を使って元反例の原因を説明しない。

入力封印は先行設計書と一致させる。

- Q012g main normalized SHA256:
  `6a201f212b321d8d7b3d4d143306633608c9df4c50c763e05dcd044695002944`
- Q012g1 main normalized SHA256:
  `ca6b15627880cbe390f6a53bc87eb9a6ba0833f1f370c5b9ea2c494625e75000`
- Q012g2 oracle normalized SHA256:
  `493f78e85887821862dbfae135b30c019979369b285db5e114772eb71dd90b03`
- Q012g2 path helper normalized SHA256:
  `a0e2185cfffd1adeb76ec7aae413dce4f5962b8923b1baf1e5588a17d14de9c3`

Q012gの三child・独立worker、Q012f2の三係数NPZ、全source chainも既存の封印を引き継ぐ。
全先行scientific sourceと`src/ttim_lbm`を編集しない。

## 数学的な対象と丸めの扱い

既存chartに対する方向別経路を

```text
W_d(t u) = f* + sum_{i=1}^d t^i v_i
R_d(t u) = sum_{i=1}^d t^i r_i,  d=2,3
```

と表す。v2/v3はTaylor係数を含む寄与であり、追加の`1/2`や`1/6`を掛けない。
埋込みのFourier係数、実座標化、`norm="ortho"`の逆FFTを保持する。
各次数を別々に物理場へ戻した経路と、元の合算後FFTによるWの差も数値診断として保存する。
内部経路r1/r2/r3は元のreal linear、reduced Hessian、G3評価から作る。定数座標は厳密な0を確認する。

局所moment係数は各v_i（v0=f*を含む）へ既存`macroscopic`を作用させた丸め済み値とする。
`rho(t)=sum rho_i t^i`, `j(t)=sum j_i t^i`のrho0を1、j0を0にハードコードしない。
事前の小配列確認でも、一様f*の既存局所運動量計算はx成分`-1.3877787807814457e-17`を返した。
Q012g1のexactな基準運動量0とは異なる集計である。この低次数の丸めを修理・投影せず保存する。

population qごとの、重みを掛ける前の非線形分子を

```text
Q_q(t) = 4.5*(c_q . j(t))^2 - 1.5*(j(t) . j(t))
E_q(t) = w_q * (rho(t) + 3*c_q . j(t) + Q_q(t)/rho(t))
B_q(t) = v_q(t) + omega*(E_q(t)-v_q(t))
```

とする。Qは最高次数2d、rhoは最高次数dである。
primaryはQ012g2の係数除算で`Q/rho`を次数9まで求める。
衝突係数B_nを作ってから、各次数へ元のperiodic streamとreal-space filterを作用させる。
局所densityの積・除算をstreamの外へ移動しない。filterは方向別二階差分の**和の二乗**を保つ。

`W_d(R_d(tu))`の係数は、線形・二次・三次の元monomialへr(t)を直接代入して畳み込みで求める。
最高次数はd²。ゼロの不足次数も明示し、定数は元f*を使う。
写像側との差をC0,…,C9とする。低次数の係数を、理論上消えるはずという理由で0へ置換しない。
この計算は丸め済み入力に基づく形式的な経路展開であって、IEEE写像が解析的であるという主張ではない。

残りは局所分子を全係数のまま

```text
tail_q(t) = omega*w_q * [Q_q(t)-rho(t)*P9_q(t)]/rho(t)
```

として評価し、その後にstream/filterを作用させる。ここでP9_qは非線形商の九次近似である。
分子の低次数の丸め残りも保持する。合成側は有限多項式なので、次数9を超える合成の残りはない。
欠陥近似を`D^[p](t)=sum_{n=0}^p t^n C_n`、有理式の残り込みを`D^[9](t)+T(t)`と区別する。

## 保存する診断値

全profileでv_i、r_i、局所moment、写像側・合成側・C_nの各配列metadata/hashとnormを保存する。
物理場全体を全960 case分蓄積しない。profileはdegreeごとに逐次処理し、worker/mainを同時実行しない。
費用は再生成・診断の追加費用として記録し、元Q012gのtimingやTT費用比較へ混ぜない。

- 各caseの元record・元判定、元field/defectとのhash一致、元のroundoff floor。
- 元W/Rと次数経路の差、合成再構成との差、残り込みのPhi/欠陥再構成差。
- C0–C9の全Gram matrix。低次数0–d、leading(d+1)、それ以降を別に集計する。
- `D^[p]`（p=d+1,…,9）の全norm、実測欠陥との全vector差、残りTのnorm。
- profileのGramから再構成したnorm²と直接vector norm²の差。
  差を`1e-9*max(floor²,直接norm²)`と比較する。負のnorm²を黙って0へclampしない。
- 符号付き交差項`2*t^(m+n)*<C_m,C_n>`を残し、各次数のnormの和だけで原因を説明しない。
- 二次leading C3と三次leading C4のnorm比、有限振幅の次数別寄与は記述用とし、後付けgateにしない。

holdoutの保存量にはQ012g1のinteger exact集計と丸め済みf*のexact基準を用いる。
元float `5e-13`を二進有理数として使い、全192 case・1,152 fieldの集計はQ012g1の保存record/hashと一致させる。
診断fieldや元の物理場へ投影を追加しない。この保存量確認は欠陥比だけのH2と区別する。
一般方向の次数診断へ保存量の追加合格を仮定せず、元recordのlegacy値を保持する。

## 独立workerと人工対照

workerは一般方向`0..7,34,51,52`の11本、holdout方向`0..7,16,21`の10本を全三格子で用いる。
これは元H4の全不合格方向と、holdoutの各格子の最悪方向3/16/21を含む固定部分集合である。
11*4+10*2=64 case/格子、全192 case、126方向別degree profileとなる。
workerはfresh modelと同じ封印入力を用い、元の全record/fieldを再現する。

workerではprimary方式に加えて、以下の別記述の方式でprofileを作る。

1. sparse monomialの経路係数は、各入力の次数の全組合せを列挙して求める。
   primaryの`homogeneous_composition`や経路畳み込みを呼ばない。
2. rhoの逆数係数は、rho0で規格化した一次・二次・三次項の多項係数による有限和で求める。
   primaryの`quotient`や逆数漸化式を呼ばない。
3. 非線形分子はequilibrium Hessianの運動量blockによるbilinear式でも構成する。
   重みを掛ける位置・全j0寄与を含めてprimaryの成分式と照合する。

各v/r、写像側・合成側・C_nを全vectorで比較し、`||差|| <= 1e-10*max(1,||reference||)`を要求する。
workerの両方式とも、192 caseで後述H1の残り込み再構成条件を満たすことを要求する。
worker内primary armの全profile hash・科学的recordをmainの対応部分集合と厳密一致させる。
これにより、全係数場を巨大な中間NPZとして保存せず、別方式との全vector比較とmainとの対応を記録する。
別方式の丸め差を同一hashへ偽装しない。独立照合範囲は192 caseであり、全960 caseではない。

実LBMの前に、非立方の小格子・非零density/運動量定数・複素Fourier経路・反復/重複monomialを含む人工対照を通す。
商の成分式とHessian式、stream/filterの独立なFFT記述、C0を消す対照、誤った三次factorとG3欠落を検査する。
zero density、不正shape/dtype、非有限値、overflow、保存後の末尾方向・成分改変も検知する。
Q012g2の77テストは先行実装の回帰として再実行する。

## 判定基準

validityは親/係数/source封印、元recordとfieldの全件同一性、coverage、finite、人工対照、
全Gram整合、holdout exact保存量照合、独立192 caseの全vector照合とmain対応、全保存後読戻しである。
欠測、元case再現失敗、source変化、独立照合不足があればinconclusiveとする。
次の科学的仮説は互いに分けて判定し、都合のよい次数や方向だけで集計しない。

### H1: 残り込みの再構成

全960 case・両degreeで、次数経路Wと元W、合成再構成と元W(R)、残り込みPhiと元Phi(W)、
残り込み欠陥と元欠陥の各vector差normが元の
`B=100*eps*max(1,||f*||_2)`以内であること。
これは元の解像性floorを使った数値再構成条件であり、微小残差の相対1%精度や存在定理を意味しない。

### H2: holdoutの九次欠陥予測

全192 holdout case・両degreeで、残りを足さない`D^[9]`の実測欠陥に対するvector相対誤差が`1e-3`以内であること。
さらに、その二次/三次norm比の`.5`以下判定と`1`を超える判定が元の欠陥比だけの判定と全件一致すること。
元のH5 composite（positivity・legacy保存量も含む）を再判定したことにはしない。
元の欠陥normが0や未解像なら除外せずH2を不成立とする。

### H3: 元の一般方向のfit再現

全192方向/格子の4振幅で、`D^[9]`による二次/三次のlog–log fitと元fitとの差が各々`.01`以内、
最小振幅の三次/二次norm比の相対差が`1%`以内であること。
元のH4の三条件（二次傾き2.9–3.1、三次傾き3.9–4.1、最小振幅比`.1`以下）の合否も全件一致すること。
予測normが元floor以下ならそのfitを未解像としてnullを保存し、H3を不成立とする。
丸め込み低次数を含む予測であることを明記し、純粋なC4だけで説明できたとは言わない。

validityが通りH1/H2/H3が全て成立ならaccepted、validity通過かついずれか不成立ならrejected。
不達は方向・degree・振幅・成分/比較・次数を列挙し、元の反例と対応させる。
H1不達なら経路再構成・局所moment・collision・stream/filterへ段階的に切り分ける次問へ進む。
H1成立でH2/H3不達なら、次数別項・有理式の残り・丸めの寄与に応じた次問を登録する。
受理しても高次chartを自動構築せず、診断が示す使用範囲と高次化の必要性を次に判断する。

## 主張範囲と実装

新しい不変多様体の存在・一意性、SSM、連続球、長時間trajectory、grid-uniform実用半径は認証しない。
この次数別分解は既存W2/W3の評価であり、W9の構築でもTT優位性の検証でもない。
自然Fourier sparse baselineと元Q012gの棄却は保持する。

実装予定は`research/d3q27_cubic_defect.py`、`research/q012g3_d3q27_cubic_defect.py`と専用テスト。
本書作成時点で新規実装・実LBM診断は未実施。正式実行前に新規sourceを封印し、worker→mainを逐次実行する。

### 実装進捗 2026-09-08 — 実格子の判定ではない

登録commit `8260488`の後に`d3q27_cubic_defect.py`を実装した。
定数項から九次までの写像・合成・欠陥、全Gram、有理式の残りと再構成差を保持する。
independent armは次数全組合せ、逆数の多項係数和、Hessian bilinear式を使い、primaryの合成・商・畳み込みを呼ばない。
population単位の商の計算は、全tensorによる既存商と小配列でbitwise一致を確認した。
full-vector照合はdegree 2/3で36/37比較を行い、末尾C9成分の改変も検出する。
非立方2×3×4局所場、複素共役の2実座標・7³人工chart、非単位density・非零momentum定数、
誤factor・G3欠落・C0削除、不正入力・overflowを含む45テストが通過した。
Q012g2の77回帰テストと合わせた122件は警告error化で全件通過した（17.90秒）。Ruffと整形も通過した。
この時点ではrunner未実装、実格子17³/33³/65³は未実行であり、H1/H2/H3の実LBMでの成立はまだ判定しない。

### 保存記録の監査 2026-09-08 — 実行管理は未実装

`research/d3q27_defect_evidence.py`と専用55テストを追加した。
元と同じ乱数方向から全960 case・worker192 caseのscheduleを作り、元aとの全件一致を検査する。
方向ごとの両degree・全振幅、C0–C9・局所商/残りの全係数metadata、全Gramと交差項、
両armの全vector比較36/37件、元record/field/defectとholdout exact fieldの対応を監査する。
内部経路の小さな係数配列と再構成座標も保存して再計算し、P9 vector誤差の絶対値を追加保存する。
追加は証跡であり、既存helperの係数計算・判定上限・物理mapを変更していない。

元記録のnormを予測欄へ注入する**判定式だけの回帰**では、全192 generic fitの再現条件が通り、
元H4の65³ index 34/51/52の3不合格は不合格のままとなる。
全192 holdoutも元の欠陥比の81不合格・37悪化を保持し、legacy保存量を含む元H5 compositeと分離した。
これはP9による実LBM予測ではない。判定式の検査値を正式artifactや科学的結果へ転用しない。

末尾case・degree・C9比較・tail・cross term・exact field・閾値改変、欠測・重複・順序変更・非有限値を検知する。
一方で、整合したH1不成立や独立vector不一致は記録破損と混同せず、対応gateをfalseに保つ。
負のGram推定norm²も負のまま保存し、Gram validityを不成立にする。
`validate_direction`の成功は保存値の内部整合だけを意味する。
source封印・fresh物理field照合・worker/main対応・全格子coverageと、`direction_gates`のvalidityを別途満たす必要がある。
workerとmainの同一性比較には`primary_record`を用い、独立armの丸め差をprimary hashへ偽装しない。
実行費用はこの科学的比較recordの外側へ保存する。

新規45＋55、先行Q012g2の77、Q012g1 main保存後監査10、全187件が警告error化で通過した（90.54秒）。
Ruff・整形・compileallも通過した。実格子はまだ開始していない。
次は既存の入力/source封印を接続したrunner、fresh物理fieldの診断、例外/途中結果の保存、全数readback、
worker完了後のmain開始を実装・検証し、正式なsource封印を行ってから実行する。

### 実行器と実行前source封印 2026-09-08

`research/q012g3_d3q27_cubic_defect.py`を実装した。初回の実行器34テストは245.51秒で通過した。
7³/9³/11³・2実座標の人工fixtureでworker/mainを全経路実行し、保存物の全方向・末尾case・
tail/係数比較・source・集計・判定・replayの改変を検査した。正式17³/33³/65³の結果ではない。
実データへの開始条件は、元Q012g・Q012g1・Q012g2の封印、Q012f2を含む全入力chain、
Q012g1全192 caseの保存後監査・全GMP replay、Q012g2の全人工値の再計算である。
実行時に既存の小格子/保存監査100件とQ012g2の77件、全177テストも再実行し、終了code・件数・test sourceを保存する。

主方式の全振幅を評価した後に、以後の照合に使わないtail係数の一時配列だけを解放する。
続いて独立方式を作り、v/r・写像・合成・C0–C9の全vector比較を行ってから主方式の大配列を解放する。
独立方式の全振幅では元fieldを再生成・再照合する。演算や係数を変更してメモリを減らす方法ではない。
開始前のavailable physical memoryは約5.57 GiBだった。全caseの物理場を蓄積しない。

正式実行はCLIを使用し、OSが保持する非blocking lockでworker/mainの並行実行を拒否する。
lock fileの存在は生存証拠とせず、process/実行handleを確認する。終了時・例外時のlock解放は別processで検査した。
全出力は新規pathへの排他的書込みとし、既存の全結果・途中結果を上書きしない。
各方向を完了/失敗時に保存し、失敗位置とそれまでの元record・field・係数を保持する。
非有限値は0やnullで埋めず、明示的なexceptional-value tagにする。失敗した方向はvalidityを通さない。
workerとmainの保存物は同じdirectoryに置き、入力とsourceは実行前後・全保存後に再照合する。
mainは独立192 caseの完了、全保存後監査、両方式のH1・全vector比較、別processを満たしてから開始する。
旧方向のscientific primary recordは全て厳密一致させる。費用はその比較recordから分離する。

実行前のnormalized SHA256:

- profile helper: `884339bef18159b1edd2940193e134733f75c28881840c4edebef58ccf0fa005`
- evidence helper: `b283282df457c96116c3aef324c61a29251e7ae4fec1aec04751e945c4517c76`
- runner: `3906850e43cbb67ac9dec44ec3eb4c3ed09d921d0345bacaa0410385d8da7b62`
- 全scientific sourceと対照test sourceのdigest: `c7001e41d3ef7541d5f2c863a7fba714f95b0dc7a78f434555fdcf3f09f5e38a`

最終35＋177、全212件は警告error化で通過した（279.46秒）。Ruff・整形・compileall・CLI helpも通過した。
本節のcommit時点では実格子診断は未開始である。
commit後、独立192 caseを開始し、完了・再読確認後にのみmain960 caseへ進む。

### 独立worker開始と17³の完了 — 2026-09-08

source封印commit `7412b46`の後、02:45:36 JSTにPID 27060／handle 51090で独立workerを開始した。
出力予定は`research/artifacts/q012g3_d3q27_cubic_defect_replay.json`。
実行前の入力・対照を通過して実格子へ進み、17³の全21方向・64 caseを保存した。main960 caseは未開始。
同じprocessの生存とhandleの進行を確認しており、観測timeoutによる再起動や並行した主計算はない。

17³の閉じたgridのnormalized SHA256:
`273ce8b5ee72e9220d935e147d96ba0f412abf7364d8ded5b51fdd2dc4349329`。
grid evidence digest:
`09c0743605aa4ffb85264fafd3eeda8343afc332aa97d41748a8ddba0e0cbb4c`。
全21方向childのSHAは同gridの`direction_artifacts`へ固定し、全件を読み戻して内容とheaderを照合した。

- 42 profile、元384 field・128欠陥metadata、1,533全vector比較を監査した。
- 全11一般方向のH3、全20holdout caseのH2、両degree/armのH1とGram整合が通った。
- 全再構成比較の最大差は`5.722781890795384e-15`、元floorは`5.502608491768111e-13`。
- 一般方向のfitを別記述の閉じた最小二乗式で確認し、全1,664切断norm²を`fsum`でも照合した。
- 元record/field/holdout exact集計の全照合、末尾case・C9比較・tail・exact field・H2/H3改変を含む追加11テストが通った（13.35秒）。

この報告は17³のworker部分集合に限定する。全192 caseの完了/受理やmain960 caseの再現成功ではない。
最終親workerの保存後監査、33³/65³、本計算との全primary record一致は未完了である。
検証手順に沿って途中の成立と未実施部分を分離し、元Q012gの棄却を保持する。
workerを中断・再起動せず、同じhandleを確認しながら残りを継続する。
