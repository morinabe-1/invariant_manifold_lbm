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

### 33³の完了と登録反例の再現 — 2026-09-08

同じ独立worker PID 27060／handle 51090で33³の全21方向・64 caseが完了し、65³へ進んだ。
全42 profile、元384 field・128欠陥、1,533全vector比較の保存後監査が通過した。
全21方向のchildのSHA・内容・headerをgridと照合し、科学的source digestも封印時と一致した。
H1/H2/H3・Gram・独立照合の不達は0。再構成差の最大は`1.5336496636226352e-14`で、
元floor `1.4882165908113665e-12`以内だった。

33³ gridのnormalized SHA256:
`777559e4ffebb723f3dd5b3c42880bb06ea137711a8babac8f011c1039be0c23`。
grid evidence digest:
`07662bf8c2765e9c8ba631402f941b2b9ad9c782cea664b8a1f1a61e9089977b`。
全21方向childの封印は同gridの`direction_artifacts`へ保存している。

登録holdoutの`.032`全10 caseの元半減不達と、index 2/4/7/16の4悪化を全件再現した。
H2の成立は「元欠陥を再現できた」という意味であり、「三次補正が二次より良い」への読み替えではない。
最悪方向index 16・`.032`では、元比`1.316172134164264`、九次予測比`1.3161721341163626`だった。
元のlegacy保存量・正値性を含むH5 compositeはfalseのまま保持する。

同反例の記述的診断では、二次のC3と三次のC4のnorm比は`33.66509428645966`で、
振幅を掛けたleading同士の比は`1.0772830171667092`だった。これは元比全体の再現ではない。
三次モデルの欠陥予測は、四次まででvector相対誤差`0.4984067518373402`、
六次までで`9.034376519768248e-5`、九次までで約`8.6714e-10`となった。
その三次モデルで、低次数0–3の寄与normは`5.347496454803282e-17`、
有理式の残りnormは`3.807768117565888e-16`、元欠陥normは`1.6989923303657745e-5`である。
純粋なC4だけ、あるいは低次数丸めや有理式の残りだけで、この有限振幅反例を説明しない。
高次数寄与と符号付きGram交差項を保持する。上の値は一件の記述であり、新しい受理gateではない。

33³の追加11テストは全保存物、全holdout合否、独立OLS式、全1,664 Gram集計の`fsum`照合、
最悪方向の欠落、旧H5/P9比/tail/末尾縮約座標の改変検知を含む。
17³の11回帰と合わせて全22件が警告error化で通過した（24.93秒）。Ruff・整形も通過した。
監査済みの途中報告として共有可能だが、対象は17³/33³の計128 caseのみである。
65³、最終worker192 caseの全読戻し・終了、本計算960 caseとの全primary record対応は未完了。
元Q012gの棄却、SSM・連続球・長時間・TT優位性の未認証を保持して同じworkerを継続する。

### 合成の代数的な補足 — 実格子の仮説・sourceは不変

65³の独立計算中に、[三次chartの合成係数](D3Q27_COMPOSITION_IDENTITY.md)を式で整理した。
J0–J9の全20種類の項を、40組の次数選択の列挙と整数で照合した。
別記述の座標多項式の積・直接評価との有理数の厳密一致、表の全行、誤った置換数/二重階乗を含む17テストが通った。
W3にR2を合成しても六次のT(r2,r2,r2)が残り得るため、高次欠陥をG3だけへ帰属させない。
一方で、この恒等式は写像側との差Cnや実反例での各項の支配性を測った結果ではない。
この補足は読解のための検査で、正式177対照・係数・演算・事前登録仮説へ変更はない。

### 65³の登録反例34 — 元の傾き上限超過を保持して再現

同じworkerが保存した一般方向index 34の全4振幅を読み戻した。
2 profile・元24 field・8欠陥・73全vector比較について内部整合、両方式のH1、Gram、独立照合が通過した。
本節はこの一方向の記述であり、65³全体、最終worker192 case、main960 caseの受理ではない。
元H4はfalse、九次予測による元H4判定もfalse、その再現を調べるH3はtrueだった。

| 同じ4振幅での量 | 元Q012g | 九次欠陥予測 |
|---|---:|---:|
| 二次chartの欠陥傾き | 3.030747161234832 | 3.030747445098687 |
| 三次chartの欠陥傾き | 4.103841695537577 | 4.103894349187252 |
| 最小振幅での三次／二次欠陥比 | 0.0801557831453807 | 0.08014626737054589 |

三次傾きの差は`5.2653649674994085e-5`、比の相対差は`0.00011871601101507567`で、元のH3許容差以内だった。
保存されたnormから独立の閉じたOLS式でも傾きを計算し、元fit・予測fitの両方を確認した。
同じ三次chartの切断欠陥D^[4]、D^[5]、D^[6]、D^[9]の傾きは、それぞれ
`3.9999999998584626`、`4.077688458854748`、`4.1038942623554435`、`4.103894349187255`だった。
各切断の全4 normが元floorを上回ることも確認した。
この有限振幅窓での上限超過には五次・六次の寄与が関わり、四次項だけの傾きとは区別できる。
W4/W6/W9を構築した結果ではなく、漸近次数の変更やG3単独への原因帰属でもない。

方向別artifactのnormalized SHA256:
`92061894ea332780273f3866816a1c1fb0784da842223d855e786c811031e1d8`。
[反例34の保存後検査](../tests/test_q012g3_cubic_defect_replay_counterexample34_artifact.py)では、
元H4の成功への書換え、予測H4の書換え、C9・末尾caseの欠落、末尾縮約座標の改変を拒否する。
全104切断Gram norm²の補償和照合も含む追加9テストが通過した（1.88秒）。
17³/33³の22回帰と合成恒等式17件を合わせた全48テストも警告error化で通過した（26.69秒）。
稼働中のsource digestは実行前封印と一致しており、正式177対照へこの保存後検査を追加していない。
元Q012gの棄却を保持し、残りの反例・holdout・最終親保存物の確認へ進む。

### 65³の一般方向subset完了 — 反例51と52を分ける

登録されたworker一般方向0–7、34、51、52の全11方向・44 caseを保存後監査した。
22 profile・元264 field・88欠陥・803全vector比較、全childのSHA/header/body digestを照合した。
このsubsetでは両方式のH1、Gram、独立照合、全11方向のH3が通過した。
元H4の不合格集合は34/51/52と厳密一致し、再現できたから元H4を成功へ変更することはない。
全11方向の元／予測fitを独立OLS式で、全1,144切断Gram norm²を補償和でも確認した。

方向51の元三次傾き`4.102353999806372`に対し、九次予測は`4.10242111001829`だった。
四次までの切断欠陥の傾きは`3.9999999992928137`、五次までで`4.083366963321555`、
六次までで`4.102421242714545`となり、方向34と同様に有限窓での上限超過が再現された。
最小振幅比は元`0.06909250406390506`、予測`0.06908204448486943`で、こちらは基準0.1以内である。

方向52は異なる。元三次傾き`4.01807675597301`、予測`4.018103036707387`は両方とも元区間内だった。
不達は最小振幅`.001`での欠陥比であり、元`0.10292984357429616`、予測`0.10292376971677472`である。
二次chartのC3のnormは`0.336997145213524`、三次chartのC4は`34.74494138429175`だった。
その先頭項同士の比`.001 * ||C4^(3)|| / ||C3^(2)|| = 0.10310158966562488`も0.1を超える。
したがってこの反例を「傾き上限超過」や「五次以上だけが引き起こした比の超過」とは扱わない。
先頭項の比は全欠陥比とは異なり、受理gateの置換や新しい振幅半径の認証には使わない。
符号付きGram交差項を保持した九次予測で元判定を再現し、有理式の残りは別項として監査した、という範囲に限定する。

全11方向のnormalized SHA256は[一般方向subsetの保存後検査](../tests/test_q012g3_cubic_defect_replay_n65_order_artifacts.py)へ封印した。
新たな反例51/52のSHAは、それぞれ
`a2561c03fdd7005f4ced690272337a6d73def933a5ce9702d9e972aaa943fc87`、
`8ed0d85bcddb664b7faaa640bc1339f73cafaccbbf7bdf994aa482028736ba29`。
全方向・fit・Gram・二種類の反例の検査と、反例削除・旧判定／比書換え・末尾case／C9欠落の拒否を含む10テストが通過した（4.08秒）。
既存48件と合わせた全58テストも警告error化で通過した（30.71秒）。Ruff・整形・compileallも通過した。
同じworkerのholdout試験は継続中で、65³全grid・最終親192 caseの全監査と終了、main960 caseは未完了。
稼働中のscientific sourceと正式177対照は封印後から変更していない。

### 独立worker全192 caseの完了 — 2026-09-08

同じPID 27060／handle 51090で全三格子・63方向・192 caseを完了し、最終親の全数保存後監査も通過した。
05:39:40 JST時点でexit 0とprocessの終了を確認した。以後このworker handleをpoll・再起動しない。
126 profile、元1,152 field・384欠陥の同一性、holdout60 caseのexact記録、4,599全vector比較を確認した。
全63方向childと三gridのSHA/header/内容、入力とsourceの実行前後一致、正式177対照（19.67秒）も通過した。
10 validityとH1/H2/H3は全てtrue。ただし判定は`passed / worker_only`であり、main960 caseの受理ではない。
workerの一般132 caseとholdout60 caseを合わせた192 caseであって、全960 caseや全holdout192 caseを独立計算したものではない。

最終親のnormalized SHA256:
`546f99edfe101dccd770dcf559bf3a9394eec84c463c0e2b05895c11430f4628`。
evidence digest:
`06332e8070f549040a49c70a558dd562034ba31d58c0ec47ff46bfca5fbd624b`。
65³ gridのnormalized SHA256:
`4e08f3440d38930b3f35edef5a22b6c5ed93d529ffe73e0922e78b0d7ee89de2`。
同gridのdigest:
`f2bc00c12144f2b84796d548e4d0959a358dd60ca1dc81324681aeb0b1007a0b`。
17³/33³の既報sealは不変で、全方向childのsealは各gridに保存した。

全再構成差の最大は65³・一般方向4・degree3・`.002`のPhi再構成で`4.2263693498373226e-14`だった。
対応する元floorは`4.1140092794350784e-12`であり、他の全case・両degree/armもそれぞれの元floor以内だった。
元一般方向H4の3不合格、holdoutの29半減不達・14悪化を全件再現した。元の棄却は修理・変更していない。
65³のholdoutでは`.008`の9/10 caseと`.032`の10/10 caseが元の半減不達で、`.032`全10 caseが二次より悪い。
index6・`.008`は欠陥比0.37329115を再現して半減するが、旧H5 compositeはfalseを保持した。

最悪例65³・index21・`.032`の元比`5.834017983080117`に対し、九次予測は`5.834017984274533`だった。
先頭項同士の比は`2.4411856684572943`で、全欠陥比の再現ではない。
同じ三次chartの欠陥予測のvector相対誤差は次のとおりだった。

| 欠陥の切断次数 | 元の全vectorに対する相対誤差 |
|---|---:|
| 4 | 0.9169766502506098 |
| 6 | 6.584932657101983e-5 |
| 9 | 約3.28809e-10 |

元三次欠陥normは`1.2423483833504367e-4`、五次以上の寄与normは`1.1392044589355291e-4`で、
四次寄与norm`3.7426941053865025e-5`より大きかった。leading–higherの符号付き交差項は`1.0556511449794793e-9`である。
低次数0–3の寄与norm`9.681631776402514e-17`や有理式の残りnorm`8.963718357636764e-16`だけで、この悪化を説明しない。
また65³・index0・`.008`は先頭項同士の比`0.497894959297805`が半減基準内でも、九次予測比`0.5107470629849643`は基準外となる。
先頭係数のnorm比は記述用に限るという登録方針を、この実例でも確認した。
これらは既存W3の欠陥分解であり、W4/W6/W9の構築、全方向での単一項への原因帰属、連続球の認証ではない。

[最終workerの保存後検査](../tests/test_q012g3_cubic_defect_replay_artifact.py)の12件が通過した（65.54秒）。
fresh入力chain、最終親と全childの再読、全4,992切断Gram集計の補償和、元判定の保持、
最悪方向削除・旧H5／比書換え・C9欠落・末尾座標改変の拒否を含む。
既存58回帰も再実行して通過した（29.35秒）。追加12件と合わせて70件を確認し、Ruff・整形・compileallも通過した。
この結果は独立workerの完了に限定する。本節のcommit後、同じsourceでmain960 caseを開始し、
入力・177対照・worker全readbackの再確認後に実格子へ進み、全primary科学的recordの一致を最後に検査する。

### main960 caseの開始 — 2026-09-08

独立結果をcommit `6faf34e`で保存し、cleanなworktree、全292出力pathの未使用、source digestの一致を確認した。
workerの終了確認後、05:51:00 JSTにPID 35240／handle 31939で次を開始した。

```powershell
python -u -m research.q012g3_d3q27_cubic_defect --output research/artifacts/q012g3_d3q27_cubic_defect.json --replay research/artifacts/q012g3_d3q27_cubic_defect_replay.json
```

起動時の`input_audit`と、実processの生成時刻・引数・生存を確認した。
その後17³への`fresh_grid`を観測した。固定runnerの開始条件である元入力chain・177対照・worker全readbackを通過して実格子へ進んだ。
mainの一般index0–7・32 caseを保存後監査し、対応するworkerの全primary科学的recordと一致することを確認した。
source digest `c7001e41d3ef7541d5f2c863a7fba714f95b0dc7a78f434555fdcf3f09f5e38a`、map・係数・方向・振幅・閾値は不変である。
ここまでの成立はworker部分集合に限り、main960 caseの完了・受理、全primary対応の成立はまだ主張しない。
同じ実行handleを継続確認し、観測timeoutを終了と取り違えず、計算を再起動しない。

### mainの17³全320 caseの保存後監査 — 2026-09-08

同じPID 35240／handle 31939で17³の全96方向を完了した。
一般64方向×4振幅、holdout32方向×2振幅の320 case、192 profile、元1,920 field・640欠陥を全件照合した。
全96方向childのSHA/header/body、登録schedule、旧record、holdout64 caseのexact記録も監査し、H1/H2/H3・Gramが全て通過した。
mainはprimaryのみを計算するため、このgrid内での二方式vector比較数は0である。
その一方、独立workerで計算済みの登録21方向・64 caseに対応する全primary科学的recordの厳密一致を別途確認した。
これは同じ格子のsubset照合であり、全main960 caseを独立方式でも再計算したものではない。

main gridのnormalized SHA256:
`e2edeec5e05da2e1d93694ac0c9c9b58f3b33da64edd022cfb9515b8cb92c43f`。
grid digest:
`c34c5f89177569a8fa9b53088b4b3da639386169aa0e1417fd8cbfa033402ece`。
方向childのsealはこの外部封印済みgridに保存した。scientific source digestは実行前の`c7001e41…`から不変である。

全64一般方向の元／予測傾きを閉じたOLS式で、全4,160切断Gram norm²を補償和で確認した。
元N17のH4は64/64、holdout H5は64/64の成功を維持し、欠陥比の半減判定・悪化判定も全64 holdoutで一致した。
全holdoutのP9 vector相対誤差は元上限`1e-3`以内だった。
傾き差の最大`0.00024180368661497198`は登録上限`.01`以内、最小振幅比の相対差最大`0.0005470464888657247`は1%以内だった。
全640 sampleの再構成差最大は、一般方向10・degree3・`.008`のPhi再構成で`5.7870239958157445e-15`だった。
対応する元floorは`5.502608491768111e-13`で、他の全再構成比較も各caseの元floor以内だった。

[main N17の保存後検査](../tests/test_q012g3_cubic_defect_main_n17_artifact.py)の13件が警告error化で通過した（38.65秒）。
全coverage・全child・worker対応・OLS・Gram・summaryの検査に加え、末尾case/C9欠落、tail・比・exact field・末尾座標改変を拒否した。
既存worker N17の11件と合成恒等式17件も通過した（13.33秒）。計41件を検証し、Ruff・整形・compileallも通過した。
この追加artifact検査は正式177対照に組み込まず、稼働中のsource封印を保持する。
同じmainは33³へ進んでいる。残り33³/65³・全worker対応・終了時入力/source照合・最終親の全監査を終えるまで、Q012g3全体は未判定とする。
元Q012gの棄却は変更せず、この結果を新しい高次chart、SSM存在、連続球・grid-uniform半径やTT優位性へ一般化しない。
