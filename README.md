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

## 現時点の結論

「中心多様体」と「空間的な流体の遅い多様体」は同一ではない。

- 奇数幅の有限周期 D2Q9 で厳密に \(|\lambda|=1\) となる物理モードは、通常
  \(k=0\) の質量と二成分運動量の3個である。
- 偶数幅の格子には、さらに \(\lambda=-1\) の Nyquist checkerboard mode が現れる。
  したがって固有値の絶対値だけで中心・遅いモードを選んではならない。
- 非零低波数の shear/acoustic modes は正粘性により \(|\lambda|<1\) であり、
  本命の空間的縮約は slow/spectral invariant manifold として構成する。
- 厳密な3次元中心多様体は、homological equation、gauge、残差次数、TT表現を
  検証するための解析解付きオラクルとして使う。

unit-mode の parity は、保存・Nyquist 構造に加えて、幅3–10、
\(\omega=0.5,1.2,1.8\) の Fourier-block 回帰テストでも確認している。保存 artifact
自体の代表ケースは \(\omega=1.2\) の \(8^2,9^2\) である。

最初の再現可能な D2Q9 実験では、線形チャートの不変性残差
\(O(\lVert a\rVert^2)\) が、二次 homological equation を解くことで
\(O(\lVert a\rVert^3)\) に改善した。観測次数はそれぞれ
`1.9969` と `2.9969` である。同じ二次チャートの polynomial TT は、
相対再構成誤差 `3.01e-15` で box-dense 表現と一致した。ただし、TT の657係数は
box-dense の2187係数より少ない一方、自然な sparse-fiber 表現の567係数より多い。
従って、この一様3変数 oracle は TT の同値性検証には使えるが、自然な疎表現に対する
圧縮優位性は示していない。

さらに低波数の moment-based classifier は、\(k\to0\) 外挿で shear viscosity を
相対誤差 `4.9e-8`、音速を `2.0e-8` で回収した。これは低波数での物理モード同定を
支持するが、固有値衝突を越える branch continuation の検証はまだ残っている。

これは非一様流れの縮約完成を意味しない。次の研究ゲートは、D2Q9 Fourier
ブロック上で物理モーメントを使って低波数の流体枝を追跡し、その実基底に対する
一般の二次 homological equation を解くことである。

## 再現

Python 3.11 以上を使う。

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m ttim_lbm --output research/artifacts/d2q9_baseline.json
```

実験結果は
[`research/artifacts/d2q9_baseline.json`](research/artifacts/d2q9_baseline.json)
に保存される。

## 文書

- [`docs/LITERATURE_REVIEW.md`](docs/LITERATURE_REVIEW.md):
  中心多様体、不変多様体、パラメータ化法、LBM slow manifold、TT/TT-cross の
  一次文献調査
- [`docs/DESIGN.md`](docs/DESIGN.md):
  D2Q9 から D3Q27 までの数理・ソフトウェア・検証設計
- [`research/RESEARCH_LOG.md`](research/RESEARCH_LOG.md):
  問い、仮説、実験、失敗分析、改善を一組にした研究記録
- [`research/NEXT_QUESTIONS.md`](research/NEXT_QUESTIONS.md):
  次に反証する問いと進行ゲート

## 実装の境界

現在のコードは意図的に小さい dense oracle である。

- D2Q9 の equilibrium、BGK collision、periodic streaming
- 一様平衡まわりの厳密な線形化と Fourier symbol
- 低波数 shear/acoustic modes の moment-based classification
- 恒等中心力学に対する二次 homological equation
- 二次多項式チャートの output-block TT-SVD と評価
- 独立したテストと再現可能な研究 artifact

TT-cross、非零波数 slow subspace、境界条件、外力、D3Q27 は設計済みだが、
現段階では未実装である。dense oracle で検証できない機能を先に TT 化しない。
