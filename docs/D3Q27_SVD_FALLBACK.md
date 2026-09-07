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
