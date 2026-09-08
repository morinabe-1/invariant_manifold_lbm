# Q012h0: 四次構築の全数構造・格納量census — 事前登録 2026-09-08

## 問いと固定範囲

Q012g3をcommit `db0622b`で全960 caseについて受理した。これは失敗の診断であり、元Q012gの棄却は保持する。
次の四次補正を構築する前に、**全104座標を保持した四次homological問題の規模を、独立した数え上げで確定できるか**を調べる。
本書をcommitしてから新しい実装と正式censusを開始する。

- `N=17,33,65`、`omega=1.5, eta=.02, power=2`、固定質量・3運動量の葉を保持する。
- 全26第一shell波数と、各波数のshear平面（2次元）・acoustic±（各1次元）、計78 block・104座標を使う。
- shear平面を個別固有ベクトルへ分割せず、波数・座標・次数を削減しない。
- Q012g3 mainのnormalized SHA256は `40d5bbbee9a3a6c4c4330062a1eada7422567e478f2ae06b2c9851e409423a91`。
- Q012g3 scientific source digestは `c7001e41d3ef7541d5f2c863a7fba714f95b0dc7a78f434555fdcf3f09f5e38a`。
- 先行scientific sourceと`src/ttim_lbm`を編集しない。lower-order係数を作り直したり修正したりしない。

この問は次元・support・格納量のcensusであり、四次forcing、四次解、rank、condition、残差、有限振幅改善の評価ではない。
開始条件は上記最終親の封印・受理と現在の先行sourceの一致。係数値を使わないcensusなので、lower-order物理場の再計算は行わない。
各格子のpaired spectral frameは既存関数でfreshに構築し、元のframe監査と78 blockのinventoryを確認する。

## 全数計算と独立性

1. 主方式は78 blockからのunordered degree-d tupleを逐次列挙する。比較用にd=2,3、主対象d=4を全数実行する。
   全tupleを巨大なPython listへ蓄積しない。tuple中のblock bの重複数をm_b、次元をs_bとし、対称入力column数を
   `q = product_b binom(s_b + m_b - 1, m_b)` とする。
2. 生の出力波数和とqのjoint histogramを全件保存する。別processの独立方式はblockごとの有限生成関数を次数dまで積み、
   `(次数, 波数和, q)`の係数を動的計画法で求める。tuple列挙関数を呼ばず、全joint histogramの整数一致を要求する。
3. さらに104個の個別coordinateの生成関数 `product_i (1 - t*x^k_i)^(-1)` を次数dまで展開する。
   この方式はshearの対称column数を使わない。各波数のmonomial数が主方式のq重み付き和と一致することを要求する。
4. 全block tuple数は `binom(78+d-1,d)`、全coordinate monomial数は `binom(104+d-1,d)` と照合する。
   d=2,3では既存の3,081/82,160 blockと5,460/192,920 columnにも照合する。
5. 3格子それぞれでcanonical wave写像の衝突がないことを全supportについて確認する。
   k=0は固定葉の23次元kinetic、選択波数の外部補空間は23次元、選択外は27次元として別集計する。
   各sectorで `operator_dimension = external_dimension*q` のhistogramを保存する。
   これはoperatorの寸法であり、数値rankや非共鳴の証明ではない。

小さな人工block集合では、全coordinate monomialの直接列挙、block列挙、二種類の生成関数を全件照合する。
全重複pattern（1+1+1+1, 2+1+1, 2+2, 3+1, 4）、複数波数、1/2/3次元のblockを含める。
負の次元、不正degree、入力重複key、不正波数、欠落/改変histogramを拒否する。

## 格納量と費用の指標

以下は**uncompressed array payload**であり、RSS・実ディスク使用量・独立自由度・実行時間ではない。
数値型はcomplex128=16 bytes、float64=8 bytes、int64=8 bytesとして、実際のNumPy dtype itemsizeとも一致を確認する。

- 自然Fourier sparseの全columnについて、入力index d個、波数index3個、H_dの27複素成分、F_dの27複素成分、G_dの4複素成分を保持する既存型layout。
  共役partnerも格納し、選択外でゼロとなるGの格納も含む。これを最小実装可能量とは呼ばない。
- 同じlayoutを65,536 columnごとのchunkへ分けた場合の最大chunk payloadとchunk数。
  chunk化は全保持データ量を減らさない。保持全量と作業中chunk量を混同しない。
- H/F/Gの各内訳、全三格子保持量を分離する。圧縮率は仮定しない。
- 物理空間のreal ordered dense W_d: `27*N^3*104^d` float64 scalars。
  対称dense W_d: `27*N^3*binom(104+d-1,d)` float64 scalars。
  Fourier sparseとは座標表示とreal/complex型が違うことを明記し、同じスカラー個数として比較しない。
- 最大operatorの単一complex行列payload、および全数の `sum operator_dimension^2` と `sum operator_dimension^3`。
  後二者はdense行列格納量とdense factorizationの規模指標であり、実測timeの外挿ではない。

Python object、配列管理・一時複製、LAPACK workspace、lower-order入力、保存ledger、圧縮・ファイルheader、OSの費用はこのpayloadに含まれない。
従ってpayloadが小さくても実行可能とは判定しない。実RSS・実時間・disk peakは、後続の実operator/forcing pilotで測る。
TTの実core、rounding、評価費用はこの問では測定せず、圧縮優位を主張しない。自然Fourier sparseは後続でも必須baselineとする。

## 保存・判定・次の行動

新しいhelper/runner、専用テスト、全joint histogram・三格子のsector集計・格納量のJSONを保存する。
独立processのPID、exit code、source sealと全科学的countを保存し、主方式との整数一致を要求する。
入力・新旧sourceは開始前後に封印照合し、既存出力を上書きしない。保存後は全内容を再読し、集計・判断を再計算する。

validityは入力/source・fresh frame監査・全coverage・finite・独立process・保存後一致。
H1は全joint block histogramの一致、H2は全coordinate生成関数との一致、H3は全三格子のsupport非aliasとsector/寸法/byteの内部整合。
validity通過でH1–H3全成立ならこの**構造census**をaccepted、validity通過で仮説不成立ならrejected、欠測・封印変化・例外などでvalidity不通過ならinconclusiveとする。
丸め誤差の許容値を整数countに導入しない。失敗したsectorやblockを削除して成立させない。

受理後は全規模を保持した四次homological operatorとforcingの人工オラクル・実operator pilotを登録する。
資源を満たすために小さいgrid/少ない座標だけへ問題を置換せず、必要ならchunk処理やstructured solveを別案として検証する。
四次solve、共役・固定葉・独立forcing、W4/R4の残差次数と元振幅範囲の改善、SSM存在、3D sparse/TT費用、物理benchmarkは未完了である。

## 実装前オラクルの進捗 — 2026-09-08

`research/d3q27_quartic_census.py`と専用テストを追加した。これは正式censusの前提テストであり、
**Q012h0の受理ではない**。全78 block・104座標の正式実行器、別processでの全数照合、
三格子のfresh frame、保存後監査はまだ接続していない。新しい正式artifactも作成していない。

- 小さな1/2/3次元block集合について、次数1〜4のblock列挙と二種類の生成関数を、
  個別座標monomialの直接列挙と全件照合した。四次の全5重複patternを含む。
- 生成関数から列挙関数・対称column kernelを呼ぶと失敗する対照を追加した。
  個別座標方式は二項係数関数も呼ばない。これは呼出し経路の分離であり、別process実行の代用ではない。
- 未コミット草稿にあったiteratorの消費によるsector分類の不一致とinventory復元の二重走査を修正した。
  元草稿は保全元に残したままである。
- 不正な波数・degree・重複key・bool/floatの整数欄・欠落/改変histogramを検査した。
  全体の個数が一致しても、波数の改変は独立histogram照合で検出できることを確認した。
- D3Q27用sector集計では、選択波数が非零・canonicalで、各波数の選択座標数が4であることを要求した。
  小さな入力集合でzero/selected/outsideの23/23/27分類とalias検出を確認した。
- 格納量はNumPy配列の実dtype/nbytesと照合した。Python整数への正規化で機械整数のoverflowを避け、
  大整数の集計も検査した。返却値の`full_solver_resource_feasibility`は`None`のままである。

新規127テストは0.37秒で通過した。既存D3Q27二次・基礎の43テストを含む計170テストも
警告をerror化して通過した（104.01秒）。Ruff・整形・compileallが通過し、先行Q012g3の
artifact/source sealは冒頭の固定値と一致した。

```powershell
python -m pytest -q -W error tests/test_d3q27_quartic_census.py tests/test_d3q27_quadratic.py tests/test_d3q27_foundation.py
```

次は、このhelperを独立worker・主列挙・排他的保存・全内容の再読監査へ接続してから、
登録した全規模のcensusを実行する。原問題の四次係数や実行可能性を、この小オラクルの成功から推論しない。

## 正式結果 — 2026-09-08

`6e87dec`でrunnerと37テストを追加し、既存127対照と合わせて164件が通過した後に正式実行した。
本節より前の事前登録・中間記録は変更していない。全7 validityとH1–H3が成立し、
**Q012h0の構造censusは `passed / accepted`**。元Q012gの棄却と未修復の悪化例は保持する。

main（PID 16132）と独立worker（PID 36920）の終了code 0を取得し、保存後の別process再監査もexit 0で一致した。
全3格子のpaired frameをfreshに再構築し、全78 block・104座標を確認した。
波数和の数え上げは格子に依存しないため各方式で一度実行し、各格子へのcanonical写像・sector・格納量を別々に監査した。
各格子の数値homological行列を構築したという意味ではない。

### 件数・全coverage

| 次数 | unordered block組/格子 | 対称入力列/格子 | 出力波数 | joint bin | 登録疎配列量/格子（bytes） |
|---|---:|---:|---:|---:|---:|
| 2 | 3,081 | 5,460 | 125 | 393 | 5,285,280 |
| 3 | 82,160 | 192,920 | 343 | 1,922 | 188,289,920 |
| 4 | 1,663,740 | 5,160,610 | 729 | 5,739 | 5,078,040,240 |

全joint binがblock列挙と独立block生成関数で一致し、q重み付き波数別列数が個別座標生成関数と一致した。
三格子とも二〜四次の全supportでaliasなし。四次sectorの内訳も三格子で同じだった。

| 四次の出力sector | 外部次元 | block組 | 対称入力列 |
|---|---:|---:|---:|
| zero-wave kinetic | 23 | 19,746 | 61,844 |
| 選択波数の外部補空間 | 23 | 353,160 | 1,107,840 |
| 選択外の波数 | 27 | 1,290,834 | 3,990,926 |

zero-wave行は固定保存量葉のkinetic補正用であり、保存モーメント方向を4個追加したものではない。
ただし、係数の保存モーメントがゼロであることの数値検証は、実際の四次構築で別途必要である。

### 格納量・規模指標と限界

四次の登録疎配列量は1格子5,078,040,240 bytes（約4.7293 GiB）、三格子15,234,120,720 bytes（約14.1879 GiB）。
1列984 bytesの内訳は入力index 32、波数index 24、H4 432、F4 432、G4 64 bytes。
G4がゼロになる選択外の列や共役partnerも含む既存layoutであり、最小格納量・独立自由度ではない。

- H4とF4はそれぞれ2,229,383,520 bytes/格子、G4は330,279,040 bytes/格子。
- 65,536列chunkは79個/格子、最大chunk配列量64,487,424 bytes（61.5 MiB）。全保持量は減らない。
- 最大homological行列の寸法は432、単一complex128行列payloadは2,985,984 bytes（約2.848 MiB）。
- 全blockの`sum n²`は17,288,159,170、`sum n³`は3,348,122,120,590/格子。
  全行列・factorizationの規模指標であり、実測RSS・処理時間の予測には使わない。

参考として、物理空間real W4だけを保持する場合の配列量は次のとおり。上のFourier complex H/F/G等のlayoutとは
表現・数値型・保存する対象が異なり、同じスカラー数や実装間の実メモリ比較として扱わない。

| 格子 | ordered dense W4（bytes） | 対称dense W4（bytes） |
|---|---:|---:|
| 17³ | 124,146,326,274,048 | 5,476,480,616,880 |
| 33³ | 908,090,072,727,552 | 40,058,677,779,120 |
| 65³ | 6,939,483,992,064,000 | 306,122,224,590,000 |

記録された`census_wall_seconds`は主列挙10.2757秒、生成関数方式5.8540秒で、fresh frame・集計・開始前後の封印照合を含む。
保存・全再監査を含む全campaign時間でも、係数solveの時間でもない。ソルバー実行可能性欄は全件`null`で保持した。

### 保存と再現

正式sourceは`6e87dec`時点の4ファイルで固定した。先行Q012g3のinput/source sealも冒頭の固定値から不変。
以下は正規化SHA256（textのCRLF/LF差を除く）であり、JSON内部sealとは別である。

- [最終manifest](../research/artifacts/q012h0_d3q27_quartic_census.json):
  `4c7c20a6dbde1aa8c9e7317a7b7750c000d81e429759af51ddfebc836064a0d8`
- [全主列挙](../research/artifacts/q012h0_d3q27_quartic_census_primary.json):
  `15896d87310f64ecaf5cff30e5b6a5e38f44f9b1ea3a5d9fdfc9944fc9699be8`
- [独立生成関数worker](../research/artifacts/q012h0_d3q27_quartic_census_worker.json):
  `8b83a9c6be10352f86351ba47527916647242a50acb9d0262e7b5df8175fe406`

正式保存データの全内容監査:

```powershell
python -W error -m research.q012h0_d3q27_quartic_census --audit-only
python -m pytest -q -W error tests/test_q012h0_d3q27_census_artifact.py tests/test_q012h0_d3q27_quartic_census.py tests/test_d3q27_quartic_census.py
```

新しい実行は、既存ファイルのない出力先を明示する。PID・時刻等でfile sealは変わるため、科学的再現は全histogramとscope/sourceで確認する。

```powershell
python -W error -m research.q012h0_d3q27_quartic_census --output research/replays/q012h0_quartic_census.json
python -W error -m research.q012h0_d3q27_quartic_census --audit-only --output research/replays/q012h0_quartic_census.json
```

### 検証評価と次の問い

`validate-data`のQAでは、全母集団・二種類の数え上げ粒度・全bin照合・非alias・sector和・dtypeとbyte・
固定保存量葉・自然Fourier sparse baselineの一致を点検した。図は使わず、上の表で件数とbytesを明示する。
総合評価は **Ready to share（この構造censusの範囲に限定）**。未実行・欠測による共有blockerはない。
追加17テストでは、二〜四次の全個別座標monomialを生成関数・対称column kernelなしに直接列挙し、
両保存方式の全波数別件数と一致した。各格子・次数の全sector/payloadを再計算し、再封印した親の件数・判定・PID・
余分な成功主張の改変を全再監査で拒否した。正式出力を別processで再監査する検査も含む。
既存164テストを含む計181件が警告error化で通過した（242.31秒）。Ruff・整形・差分チェックも通過した。
独立自由度・実RSS・実時間・rank・condition・四次不変性残差・TTの圧縮優位性は未検証である。
資源面の含意は「1.66百万block問題を全数保持する構築設計が必要」までであり、現在の機械で解けるという結論ではない。

次は全規模を保持した四次homological operator/forcingの人工オラクルと実測pilotを登録する。
演算子寸法が432以下であることから非共鳴・安定な解法を推論せず、lower-order入力、作業配列、保存を含む実費用を測る。
小さい格子や少ない座標だけへ原問題を置換しない。四次chartの構築と元振幅範囲の改善、3D SSM存在、物理benchmark、疎/TT費用比較は未完了である。
