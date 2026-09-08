# TT parameterized invariant-manifold LBM

格子ボルツマン法（LBM）の不変多様体に基づく縮約モデルを構築し、
Tensor Train（TT）で係数を効率よく表現できるかを検証する研究用リポジトリです。
D2Q9（2次元）で方法を検証し、D3Q27（3次元）へ展開しています。

完全離散の1ステップ写像 $\Phi$ に対して、埋込み $W$ と縮約写像 $R$ を求めます。

$$
\Phi(W(a)) = W(R(a)).
$$

## 現在の到達点（2026-09-08）

- **D2Q9**：固定保存量葉上の二次〜四次モデルを構築。存在・誤差の認証は、指定した格子・写像・局所領域に限定しています。
- **D3Q27**：[三次モデルの欠陥診断（Q012g3）](docs/D3Q27_CUBIC_DEFECT_DIAGNOSIS.md)を完了。元の次数不合格と有限振幅での悪化は未解決です。
- **TT**：検証済みの候補では、自然なFourier疎表現に対する圧縮優位性を確認できていません。疎表現を比較基準として残します。

D3Q27のSSM（スペクトル部分多様体）の存在、連続した実用振幅域、TTの優位性は未認証です。
四次の人工オラクル（Q012h1）を検証済み。[実LBMの四次構築・資源pilot（Q012h2）](docs/D3Q27_QUARTIC_PILOT.md)を事前登録しました。
合格・棄却・未解決の詳細は[研究の到達点](research/STATUS.md)を参照してください。

## 使い始める

Python 3.11以上、Git、Git LFSが必要です。Pythonの仮想環境を用意してから実行してください。
以下のcloneにはGitHubへのSSH認証が必要です。

```sh
git clone git@github.com:morinabe-1/invariant_manifold_lbm.git
cd invariant_manifold_lbm
git lfs install --local
git lfs pull
python -m pip install -e ".[dev]"
python -m pytest tests/test_d2q9.py tests/test_manufactured.py -q
```

上記テストは基本動作の確認用で、全研究ゲートの再検証ではありません。
大容量の係数データ3件はLFS管理です。取得方法と旧コミットIDの対応は[公開・LFS移行ガイド](docs/GITHUB_PUBLICATION.md)にあります。

## 構成

```text
src/ttim_lbm/       基礎実装・不変多様体・TT
research/          実験コード、研究ログ、保存結果
tests/             数値検証・回帰テスト
docs/              理論、設計、個別ゲートの結果
```

## 詳細を読む

- [研究の到達点](research/STATUS.md)：現在の判定と未解決課題
- [設計](docs/DESIGN.md)：数学的な設定と検証方針
- [研究ログ](research/RESEARCH_LOG.md)：実験・失敗・判断の経緯
- [変更前の詳細README](https://github.com/morinabe-1/invariant_manifold_lbm/blob/deeb20248b20a6f8e9b117e7efd1683efb8c7e6d/README.md)：過去の記録と再現コマンド
