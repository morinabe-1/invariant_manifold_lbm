# Q012c1a: 不収束時だけのSVD代替 — 事前登録 2026-09-07

Q012c1の`failed / inconclusive`を保持した別プロトコルである。保存した108×108行列は
この実行環境の`gesdd`で3回不収束、診断用`gesvd`ではcondition約36.74で収束した。
この1例を一般的なlibrary bugや数学的共鳴とは呼ばない。
[SciPy公式仕様](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.svd.html)は
両driverを提供し、SVD不収束を`LinAlgError`として報告する。

## 変更する点と固定する点

- Q012c1のmap、3格子、4 omega、2 filter×4 eta、104実座標、108条件を全て維持する。
- 最初に元の`gesdd`を実行し、**SVD不収束の例外が出た場合だけ**、同じ行列を`gesvd`へ渡す。
- 収束したがcondition／solve残差を落としたpairでは切り替えない。iterative refinementや
  行列摂動、座標削減、pair除外、rank／condition／残差閾値の変更をしない。
- 代替時にはSVD再構築relative誤差と左右直交性誤差を各`<=1e-12`で確認する。
  失敗なら数値validity失敗として保存し、条件を合格へ補完しない。
- 元solverで収束したpairの数値metricsは元実装と一致させる。代替driver・元の例外・
  再構築／直交性は別metadataへ保存する。
- Q012cの無変更BGK全12 baseline・全pairは数値完全一致を要求する。
  Q012c1の完了4条件も保存tableと完全一致を要求する。

## backend検証

- Q012c1のartifact／result digest／全helper・runner source／4 table sealを照合し、
  元のinconclusiveを前提として読む。停止行列をbit-preservingに再構築する。
- 保存行列に対する同一組立のbitwise一致と、代替SVDの3回再現を確認する。
  全3回で有限、再構築・左右直交性`<=1e-12`、元のsolve残差`<=1e-10`を要求する。
- seed `2026090710`、complex stable input block `[[.74 exp(.21i),.035i],[0,.68 exp(-.31i)]]`、
  external block `[[.23,.07i],[0,.29]]`、そのSym²上の既知2×3 coefficientを使う。
  元driverと代替driverの双方でrelative coefficient error `<=1e-12`を要求する。
- singular-compatible／incompatible、near-resonant condition上限超過、故意の不正factorを
  対照にし、代替が数学的失敗を通過へ読み替えないことをテストする。
- 元driverが正常に返る場合に代替を呼ばないこと、両driver不収束や不正factorを
  成功扱いしないことを例外注入でテストする。

## 科学ゲートと保存

Q012c1と同じ独立physical map／FFT／Hessian／small-k／全格子対照を再実行する。
全108条件の各3,081 pair・5,460 product列を新たに計算する。部分tableの再利用はせず、
保存値は一致検証にだけ使う。各conditionで代替回数と全pairのdriverを記録する。

validityは入力、backend対照、独立写像対照、108条件coverage、12 baselineと旧4条件の一致、
frame／coefficient構造、有限証拠、選択familyの3格子独立再実行で判定する。
全rank／condition／残差・normal-ordering gateを3格子で満たす四階型familyだけを主候補とし、
最小eta、次いで最小omegaで選ぶ。通過がなければp=2・eta=.05・omega=1.2の固定対照を
3格子再実行する。再現は全108条件の二重実行とは称さない。

backend不収束が解消しても、残差精度やnormal gapの失敗が残ればそのまま`rejected`とする。
全validityを通し主候補があれば`accepted`、validity失敗は`inconclusive`。
元Q012c1の状態を上書きしない。

helper: `research/d3q27_svd_fallback.py`。
runner: `research/q012c1a_d3q27_damping.py`。
manifest: `research/artifacts/q012c1a_d3q27_damping.json`。
全pair table: `research/artifacts/q012c1a_d3q27_damping/`。
Q012dは合格した**修正map**のdense chartとして次に置く。
このゲートも存在・一意性・非線形normal attraction・全状態の正値性・TT優位性を証明しない。

## Q012c1aの結果: passed / accepted

事前登録commit `a20456c`に従い、全108条件・332,748 block pair・589,680 product列を
再計算した。validity全11項目が通過し、3格子共通でjointly viableなfamilyは、
Laplacian対照が4/16、leading viscosityを保つ四階型が9/16だった。
最小eta、次いで最小omegaの規則で、**p=2、eta=0.02、omega=1.5、104実座標**を選んだ。
元のleading viscosityは`nu=1/18`で維持されるが、有限波数の写像は無変更BGKとは異なる。

### 選択候補の3格子検証

| N | normal modulus gap | 最大condition | 最大solve relative残差 | 最大global-l2 coefficient response |
|---:|---:|---:|---:|---:|
| 17 | 0.00384398666 | 11,710.4 | 5.27652e-13 | 63.4169 |
| 33 | 0.00193104909 | 172,745 | 3.63422e-12 | 184.960 |
| 65 | 0.000513792229 | 2,614,033 | 2.62989e-11 | 519.500 |

全3格子の3,081 pairを、frame・全格子spectrumも含めて独立に再計算し、
各conditionの全数値・driver metadataのresult digestが一致した。追加の9,243 pairの
replayであり、全108条件を二重実行したという主張ではない。

SVD代替は全332,748 pair中**1件だけ**で、元Q012c1を止めたLaplacian対照のpairだった。
選択候補の全3格子では代替を使っていない。無変更BGKの12 baseline・全pairと、
Q012c1の完了4条件は旧保存値に完全一致し、元の棄却／判定保留を維持した。

### 不採用とした結果も維持する

全108条件で二次計算gateの不合格は14条件、normal-ordering不合格は24条件だった
（両方を落とした4条件を含む）。jointly prequalifiedは74条件である。
特に、より弱い四階型`eta=0.01, omega=1.8`は17³・33³で通過するが、65³の4 shear pairが
solve残差を落とした。最大残差`2.42506e-10`、そのpairのcondition`7.43326e6`は
condition上限内だったが、残差上限`1e-10`は超えている。正常に収束したため代替を呼ばず、
このfamilyを不採用とした。

また、65³・四階型`omega=1, eta=.05`は11 pairが残差を落とす一方、eta=.01/.02/.1では
二次計算を通す。高波数減衰の増加を、homological operatorの改善の単調性へ読み替えない。
新しいoperatorではinput積とoutputが異なるmuで変わるため、normal gapと二次solve精度は
別々に検証する必要がある。全条件の構造誤差最大は`1.66717e-14`だった。

### 主張の限界とQ012d

選択候補でもglobal-l2 coefficient responseは格子細分化で増大している。またexternalの
one-step operator normは約`2.56 > 1`であり、正の固有値modulus gapから一段のnorm収縮を
結論しない。受理したのは有限3格子の二次prequalificationであり、3D SSMの存在・一意性、
grid-uniformな半径、nonlinear normal attraction、全状態の正値性を示したわけではない。

次はQ012dとして、選択した**修正map**の17³・104実座標dense quadratic W/Rを構築する。
共役Fourier blockの実座標化、非自明なR2、固定4保存量葉、保存momentのないzero-wave kinetic補正、
独立Hessian、残差次数`2 -> 3`、小振幅でのrollout／positivity／保存量を順に検証する。
全物理空間のW2配列を不要に確保せず、Fourier selection ruleに従うdense fiber oracleを用い、
full-gridの非線形写像で欠陥を評価する。TTより前に、この自然な疎表現を必須baselineとして残す。

### 保存と検証

manifestの改行正規化SHA-256:
`b254057450e1deaaa2cd2791fa4547455e27a76352c99b5923e5de2a9434ddbe`。
result digest:
`f652b5b9d6c0f3fc151d4de6927f36445d518f4cff993cdbbfc5b1a848f6587e`。
runner seal:
`7f1e7697a2f13e463c136c7933be9c18d26684bd72a9638fb7e2481b9aeb52c0`。
fallback helper seal:
`17d24e04cd6183e8439456bfb6b659d3c8a83a7b20ace081461f43252d946d76`。

108個のJSON tableは全pairのmetricsとdriverを保持し、manifestから個別SHAとresult digestで
参照する。元Q012c1の4 tableと停止行列は別ディレクトリのまま保存する。
再生成は`research/replays/`へ出力し、封印artifactを上書きしない。

検証は、dampingと元障害の29テスト、backendの12テスト、全保存tableの3テスト、
既存foundation／D2Q9／manufacturedの86テスト、既存spectral／quadraticの33テスト、
計163件が通過した。保存table監査を全108条件の再計算と称していない。
ruffとcompileallも通過した。封印した`src/ttim_lbm`とQ012a/b/c/Q012c1のsourceは変更していない。
