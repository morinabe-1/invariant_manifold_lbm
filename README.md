# TT parameterized invariant-manifold LBM

このリポジトリは、既存の `tci` 系統とは独立した研究プロジェクトである。完全な
LBM 1-step 写像

\[
\Phi:\mathbb{R}^{N}\to\mathbb{R}^{N}
\]

に対して、埋込み \(W\) と縮約写像 \(R\) を

\[
\Phi(W(a))=W(R(a))
\]

から同時に構成し、多変数係数を tensor train (TT) で圧縮することを目的とする。
最初の対象は周期境界・無外力・BGK の D2Q9、最終的な拡張先は D3Q27 である。

## 現時点の判定

研究方向は Go である。ただし Q005 により、Q004b cutoff をそのまま使う2次元
isotropic low-wave set は、標準的な nonresonant・normally-attracting SSM 候補として
棄却された。これは研究計画全体の棄却ではなく、最初の reduced set の反証である。
次は非線形に不変な \(y\)-independent stripe で coefficient solver を検証する。
stripe を含め、存在・一意性 gate を通るまでは非零波数の対象を
**candidate spectral subspace / candidate chart** と呼ぶ。

- 奇数幅の有限周期 D2Q9 で物理的に \(|\lambda|=1\) となるのは、通常 \(k=0\) の
  質量と二成分運動量の3モードである。
- 偶数幅では \((\pi,0),(0,\pi)\) に \(\lambda=-1\) の Nyquist checkerboard mode が
  加わる。このため主構築は奇数格子に限定し、偶数格子は parity regression と障害解析に
  使う。
- 非零低波数の shear/acoustic modes は正粘性により \(|\lambda|<1\) である。
  Q004b は個別ラベルの全域一意性ではなく、\(k=0\) から連続化した3次元 invariant
  cluster が有効な最大低波数域 \(|k|\le k_c\) を求める。
- 非零波数 chart は最初に全質量・全運動量を固定した葉
  \(\delta M=\delta P_x=\delta P_y=0\) 上で構築する。\(k+(-k)=0\) が作る
  zero-wave-number 補正は、保存モーメントを持たない kinetic 成分だけを許す。
- strict-center の一様 equilibrium family は、保存量葉を横切る別の解析解付き
  オラクルである。homological equation、gauge、残差次数、TT 表現の検証に使う。

## 完了した数値ゲート

### Strict-center dense oracle

\(3^2\) 奇数周期格子の一様 equilibrium family では、線形チャートの不変性残差
\(O(\lVert a\rVert^2)\) が二次補正により \(O(\lVert a\rVert^3)\) へ改善した。
観測次数は `1.9969` と `2.9969` である。64方向、解析 Hessian、
finite-difference step sweep、homological residual を別々に検証している。

### Q004b branch/cluster tracking

\(\omega=1.0,1.2,1.5,1.8\) と path angle \(0,\pi/8,\pi/4\) の連続 \(k\)-path で、
simple eigenvalue 域は左右固有ベクトル、衝突・縮退域は ordered-Schur subspace を
追跡する。次表は事前登録した閾値を通る最後の sampled \(k\)、すなわち \(k_c\) の
経験的下限である。各 path では隣の最初の不合格点も transition bracket として保存する。

| \(\omega\) | validated \(k_c\) range |
|---:|---:|
| 1.0 | 0.763–0.988 |
| 1.2 | 0.925–1.188 |
| 1.5 | 1.163–1.388 |
| 1.8 | 1.375–1.450 |

path reversal と90度回転の最大 principal angle はともに `4.5e-8` 未満である。
\(\omega=1.2\) の \(17^2,33^2\) では strict unit mode が3個、診断用
\(16^2,32^2\) では5個であり、
直接評価した \(A(\pi,0),A(0,\pi)\) にも \(-1\) mode が各1個現れた。全波数域で
個別ラベルを一意にする旧仮説は棄却した。ここで得た \(k_c\) は閾値依存の経験的境界で、
多様体の存在定理ではない。

### Manufactured nonidentity oracle

安定な複素共役対、非零 \(R_2\)、mean-like/second-harmonic complement、可制御な
二次共鳴を持つ5状態写像を追加した。非直交 similarity transform により左右基底の
正規化と左右不変性も独立に検証する。一般 real-block homological solver は既知の
\(H\) と \(R_2\) を相対誤差 \(2\times10^{-15}\) 未満で回収し、共鳴へ近づくと
condition number が約 `5.10` から `1.74e4` へ増大し、厳密共鳴を
rank deficiency として拒否した。これは solver と LBM branch-classification error を
切り分ける algebraic oracle であり、D2Q9 candidate manifold の存在証拠ではない。

### Q005 sector-aware nonresonance

Q004b の方向別最小 cutoff、奇数格子 \(N=9,17,33,65\)、
\(\omega=1.0,1.2,1.5,1.8\) の16条件を監査した。最小非空 isotropic shell は全条件で、
直交 acoustic 対の積が対角 shear と数値 rank threshold 内で一致した。
二次 forcing の左 nullspace 射影は最大 \(9.97\times10^{-16}\) なので方程式は
compatible だが、係数は非一意で strict nonresonance は失敗する。

登録 radial band の境界でも14条件に external resonance witness があり、14条件で
near-Nyquist excluded mode が finite-grid normal-attraction 必要条件を破った。
一方、spectral split 自体は最小 Schur separation 0.4846、最大 projector norm 1.8387、
最大 residual \(3.09\times10^{-14}\) で解像されている。従ってこの失敗を
branch-classification error とは扱わない。

修正案のうち cutoff 縮小は、最小 shell 自体が共鳴するため棄却した。mode追加は
additive closure の再監査待ちである。\(y\)-independent stripe は有限格子 solver
oracle として全16条件で nonsingular だった。代表 \(N=17,\omega=1.2\) の
second-harmonic block は \(\sigma_{\min}=1.9335\times10^{-2}\)、
condition number 96.02 である。ただし conditioning は概ね \(N^2\) で悪化するため、
grid-uniform な manifold claim は置かない。

## TT 格納量の解釈

Phase 0 の \(81\times3\times3\times3\) 二次 coefficient tensor の比較は次の通りである。

| 表現 | stored scalar/value count |
|---|---:|
| box-dense | 2187 |
| full Hessian | 1053 |
| symmetric quadratic | 810 |
| natural fiber-sparse | 567 + 7 multi-indices |
| scalar-sparse | 468 + 468 multi-indices |
| TT cores | 657 + ranks/shapes |

657 は **TT core stored scalars** であり、TT gauge 自由度を除いた独立自由度数ではない。
TT の相対再構成誤差は `3.01e-15` だが、自然な fiber-sparse 表現より大きいため、
現段階で TT の圧縮優位性はない。今後も Fourier selection rule に基づく sparse
表現を必須 baseline とし、値数、index metadata、serialized bytes、評価時間、
rounding時間、不変性残差を分けて比較する。TT がこの baseline に勝たない場合は、
その tensorization を不適切と判定する。

## 再現

Python 3.11 以上を使う。`q004b` study は事前登録した4個の \(\omega\) をまとめて
実行するため、CLI の `--omega` は baseline study にだけ適用される。

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m ttim_lbm --study baseline --omega 1.2 --output research/artifacts/d2q9_baseline.json
python -m ttim_lbm --study q004b --output research/artifacts/q004b_and_manufactured.json
python -m ttim_lbm --study q005 --output research/artifacts/q005_nonresonance.json
```

保存済み結果:

- [research/artifacts/q005_nonresonance.json](research/artifacts/q005_nonresonance.json)

- [`research/artifacts/d2q9_baseline.json`](research/artifacts/d2q9_baseline.json)
- [`research/artifacts/q004b_and_manufactured.json`](research/artifacts/q004b_and_manufactured.json)

## 文書

- [`docs/LITERATURE_REVIEW.md`](docs/LITERATURE_REVIEW.md): 一次文献と主張範囲
- [`docs/DESIGN.md`](docs/DESIGN.md): 数理・ソフトウェア・検証設計
- [`research/RESEARCH_LOG.md`](research/RESEARCH_LOG.md): 問い、仮説、棄却、改善の記録
- [`research/NEXT_QUESTIONS.md`](research/NEXT_QUESTIONS.md): 次の反証ゲート

## 実装の境界

現在実装済み:

- D2Q9 equilibrium、BGK collision、periodic streaming、厳密な線形化
- Fourier symbol、odd/even spectrum audit、Nyquist direct audit
- moment-based low-\(k\) classification
- simple-branch / ordered-Schur cluster continuation、path reversal、90度回転
- 固定保存量葉への線形射影
- identity-center と general real-block の dense quadratic homological solver
- manufactured nonidentity/resonance oracle
- Fourier-index arithmetic、sector SVD、fixed-leaf zero-mode restriction
- Q005 radial-band normal-dominance/resonance campaign と stripe finite-grid audit
- 二次多項式チャートの output-block TT-SVD と sparse storage baselines

未実装・未通過:

- Q006s の fixed-leaf stripe dense quadratic chart と residual-order gate
- mode-added full 2D candidate の additive closure、nonresonance、normal attraction
- TT-cross、境界条件、外力、D3Q27

従って次のゲートは Q006s であり、full 2D Q006 や TT-cross へはまだ進まない。
