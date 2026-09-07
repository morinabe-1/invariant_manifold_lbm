# Q012e: 二次chartの有理式tailと有限時間の使用範囲

## 2026-09-07 事前登録

Q012d1のP3 vector精度2%条件の棄却を保持する。P3の閾値を変更せず、必要だった
四次項とその先の有理式tailを分離し、同じ二次W/Rの使用範囲を有限sampleで調べる。
Q012d/Q012d1のsource、artifact、104実座標・全26波数、17³、
`omega=1.5, eta=.02, power=2`、4保存量固定葉を変更しない。
方向別の四次合成項は、四次の不変多様体係数W4/R4ではない。

### 1. 独立な有理式分解

単位方向uに対し、`v=Vu, h=H[u,u]/2, l=Lambda u, q=G[u,u]/2` とする。
局所momentを `Mv=(r,j1), Mh=(s,j2)` とし、
`Q(j,k)=w*(4.5*(c.j)*(c.k)-1.5*j.k)` と書く。

```text
a2 = Q(j1,j1)
a3 = 2 Q(j1,j2) - r a2
a4 = Q(j2,j2) - 2 r Q(j1,j2) + (r^2-s) a2
rho(t) = 1 + r t + s t^2
tail_local(t) = -t^5 * (r a4 + s a3 + t s a4) / rho(t)
```

これは二次経路のequilibrium非線形部から次数4までを引いた厳密な有理式である。
omega倍、streaming、filterの順で作用させてtailを得る。密度因子をstreaming後に
移動しない。Q012d1の独立微分式も再利用し、full-map差分から係数をfitしない。

本体の不変性欠陥には
`t^3*(C3-H[l,q]) + t^4*(C4-H[q,q]/2) + tail` が現れる。
さらに浮動小数で構成した係数の `d0 + t*d1 + t^2*d2` を明示的に足す。
`d0=Phi(f*)-f*`, `d1=Av-Vl`, `d2=Ah+B[v,v]/2-h(l)-Vq`。
実数代数の恒等式と浮動小数の一致を区別し、予測と直接full-map欠陥の差が
`100*eps*max(1, norm(Phi W), norm(W R), norm(prediction))` 以下か判定する。
次数3のみ、次数4まで、tail込みの誤差・各項norm・符号付きGramを保存する。
rho非正値の場合は式を評価せずdomain failureとして残す。大振幅での正値性失敗を
係数実装の失敗とは混同しない。非有限演算や予期しない例外はvalidity failureである。

### 2. 固定sampleと有限時間比較

- calibration: seed `2026090717` の正規乱数8方向を104次元単位球面に正規化。
- holdout: 独立seed `2026090718` の同じ方法による8方向。
- 両groupとも全方向・両符号・振幅 `(.008, .032, .128, .512, 1, 2, 4)`。
  合計224 case。新しい結果を見て方向・振幅を除外、追加、選別しない。
- 各caseで1-step分解と64-step rolloutを行う。途中の失敗もstep番号・理由・
  それまでのtraceを保存する。失敗後の架空の64-step結果は作らない。
- full mapと二次縮約は同一初期状態 `f0=W2(a0)` から開始する。
- linear baselineも同一f0から `f* + A^n(f0-f*)` とする。これは全空間の
  線形化oracleであり、104座標の安価な実装との費用比較ではない。
  Q012dの異なる初期chart同士の比率とは比較指標を区別する。
- 全iterateでpopulation L2誤差、density/momentumの誤差、正値、密度の下限、
  最大Mach数、保存量driftを記録する。Machは `norm(j)/rho/sqrt(1/3)`。
  physical誤差の分母は背景全体ではなく初期摂動norm。
- macro normは `sqrt(norm(delta rho)^2 + 3*norm(delta j)^2)` とする。
  初期macro normが丸め床以下なら比率を未解決とし、成功扱いしない。
- full/二次再構成のpopulationが非正値、密度が0.5未満、または非有限なら
  そのstepで停止し、そのcaseは使用基準不合格。線形baselineの負のpopulationは
  比較用診断として記録し、二次モデルのadmissionには用いない。

### 3. 使用基準と選択を分ける

工学的な許容値はまだユーザーから指定されていない。以下は研究用の有限時間基準であり、
普遍的な「実用精度」やSSM半径の定義ではない。

各caseの使用基準は、すべてを満たすこととする。

1. 全65 iterateのfull/二次再構成が正値かつ密度0.5以上で、64 stepを完遂。
2. 最大population L2誤差 / 初期population摂動norm が0.1以下。
3. 最大macro誤差 / 初期macro摂動norm が0.1以下。
4. 二次モデルの最大population誤差が同一初期linear baselineの0.5倍以下。
5. 初期の1-step本体欠陥 / 初期population摂動norm が0.01以下。
6. full/二次再構成の初期固定葉誤差と保存量drift（global値を計算して17³で割る）が
   各成分5e-13以下。線形baselineのdriftは別に診断する。

calibrationで全16 signed directionが通る振幅の、最小振幅からの連続prefixを選び、
最大登録振幅を `selected_amplitude` として固定する。途中で不合格なら、それより大きい
振幅が偶然通っても採らない。prefixが空ならnullとし、都合のよい方向へ縮小しない。
holdoutの全16 signed direction・選択prefix全振幅で同じ基準を検証する。
holdout失敗後に選択値を下げてacceptedへ変更しない。両groupの全振幅結果を保存する。
最大振幅まで通過しても、それ以上の範囲や連続した球全体へ外挿しない。

### 4. 再現・判定・次の問い

既存全source/artifactのseal、全12係数配列のfresh rebuild一致、224 caseの完全なcoverage、
予期しない非有限値がないことをvalidityとする。別プロセス・fresh chartによって次の4 caseを
1-stepと全rollout traceまで完全再現する（全224 caseの別プロセス再現とは呼ばない）。

```text
calibration direction 0: sign +, amplitude .008
calibration direction 0: sign -, amplitude .512
holdout direction 0: sign +, amplitude .032
holdout direction 0: sign -, amplitude 2
```

全in-domain sampleの有理式分解一致、空でないcalibration prefix、holdoutのprefix通過を
科学的仮説とする。大振幅の不合格自体は、使用範囲を調べるこの仮説の棄却ではない。
validity不通過はinconclusive、validity通過で仮説が不通過ならrejectedとする。
選択は上の使用基準だけで決め、次数別予測の相対誤差を新たな選択条件に追加しない。

許容振幅の律速が三次不変性欠陥なら、次は全104座標の三次homological preflightと
W3/R3構築を検討する。tailや密度が律速ならその機構を先に調べる。いずれの場合も
SSM存在・連続球での保証・grid-uniform半径・長時間精度は未認証のまま残す。
TT評価へ進む際にはFourier sparse表現を必須baselineとする。
