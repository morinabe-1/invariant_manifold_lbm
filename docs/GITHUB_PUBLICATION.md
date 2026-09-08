# GitHub公開とLFS移行

2026-09-08。これは公開に必要な格納形式とGit履歴の移行記録であり、研究結果の再計算や再判定ではない。

## 取得方法

公開先は <https://github.com/morinabe-1/invariant_manifold_lbm>、ブランチは `main`。
GitとGit LFSをインストールした環境で、次を実行する。

```sh
git clone git@github.com:morinabe-1/invariant_manifold_lbm.git
cd invariant_manifold_lbm
git lfs install --local
git lfs pull
git lfs fsck
```

LFS対象のNPZが約134 byteのテキストになっている場合は、データ本体ではなくLFS pointerである。
研究コードの実行前に `git lfs pull` で本体を取得する。GitHubのソースZIPだけで大容量データが
全て取得できるとは仮定しない。

## 移行範囲と履歴の保全

元ローカルリポジトリのコミット済み `main`、全1,942コミットを、共有オブジェクトやhardlinkに
依存しない別の公開用コピーで移行した。元リポジトリと未コミット作業は変更せず保持した。

- 移行前の先端: `a188867032ba8bda5a502379928d05c1388a30ce`
- 対応するLFS移行後の先端: `1983900531754631d3353faa426a8f1e6e481a4f`
- GitHub側の初期コミット: `a570df45d322cb89384e01618b02b54bdf5ab435`
- 初期コミットを保存した統合コミット: `36cc65575df8759f0ee21ff513b40de6080d2227`

GitHub側の初期コミットには、リポジトリ名だけのREADMEがあった。二つの履歴を通常のmergeで
統合し、詳しい研究READMEを残した。GitHub側の既存コミットを祖先に含むため、強制pushは不要である。

移行によりコミットIDは変わる。[全コミット対応表](GIT_LFS_COMMIT_MAP.csv)は、ヘッダーなしで
各行が `旧40桁SHA,新40桁SHA` の形式である。研究ログや保存済み実験記録にある旧コミットIDは
書き換えていない。この表で公開履歴上の対応先を照合する。著者、committer、日時、メッセージ、
親子関係は、SHAの対応を除いて保持した。

今後の開発は公開用コピー、またはGitHubから取得した新しいcloneで行う。
保全した移行前のローカル `main` を、そのまま公開先へpushしない。

## LFS対象

対象は次の3ファイルだけである。ディレクトリは全て `research/artifacts/`。
他のNPZ、JSON、圧縮JSONL、ソース、保存済み研究結果の内容は変更していない。

| ファイル | 本体のbyte数 | 本体のSHA-256 |
| --- | ---: | --- |
| `q012f2_d3q27_refined_cubic_n17.npz` | 152490290 | `5541b4229f0b8220b8fc6b08ea44287718508e5a682759939846f5754dd21e61` |
| `q012f2_d3q27_refined_cubic_n33.npz` | 153374815 | `e51f7dd54359e32d2743633b14028fdc57883e2c4b2beb8532d8a696a86e3cbc` |
| `q012f2_d3q27_refined_cubic_n65.npz` | 153774786 | `31133a6e46149371ec35c5f5579c2f3ccb50ec50a194be05716238e33f93da2e` |

`.gitattributes`には、この3パスだけのLFS設定を追加した。履歴内でも本体はLFS pointerへ置き換えた。
単に最新コミットから大きなファイルを除外する操作ではない。

## 移行コピーの検証

- 全1,942コミットの対応表を旧・新の全履歴と照合し、欠落・重複がないことを確認した。
- 変更のある1,991 tree pairを再帰的に比較した。履歴上の内容変更は`.gitattributes`と上記3パスだけだった。
- 全コミットの著者、committer、メッセージ、対応後の親コミットを比較し、全て一致した。
- 旧Git blobから直接計算した3本のSHA-256とbyte数が、新LFS pointerの指定と全て一致した。
- LFSから復元した3ファイルのSHA-256も一致し、`git lfs fsck --objects --pointers main`が通過した。
- 移行した`main`から到達可能な通常のGit blobには、100 MiB超のものが残っていなかった。
- 次の関連28テストが、公開用コピーで全て通過した。

```sh
python -m pytest -q -W error tests/test_d3q27_foundation.py tests/test_d3q27_refined_cubic_artifact.py::test_full_coordinate_wave_coverage_and_unprojected_conjugacy tests/test_d3q27_refined_cubic_artifact.py::test_grid_results_match_final_result_and_preserve_cost_scope
```

この検証は格納形式移行の確認であり、研究全体のテストの再実行や、新たな科学的主張の検証ではない。
