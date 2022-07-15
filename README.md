# BigQuery (SQL) もくもく会
## スコープ
- SQLをとりあえず触ってみる
- DWH製品に触れてみる 
## スコープ外
- DWHとは（業務DBと何が違うの？）
- 運用におけるナレッジ
- DDL系の話　などなど
- （別途勉強会あるのでそっちでよろしく）

## SQLに慣れよう
### SQLて何よ？
- (一言で)データを操作や定義することに特化した言語
- 宣言型言語（対義語：手続型言語）
- SQLはDBMS向けの標準規格言語であはあるものの、商品によって方言はある。製品仕様を必ず調べよう

## サブ言語
- データ定義言語（DDL）
  - CREATE, ALTER, DROP, ...
- データ操作言語（DML）
  - SELECT,....
<br>

__使うだけ__ に特化するのであれば、まずは後者だけ覚えよう

## 最初はこの12個だけでも調べて

1. SELCT : どんなカラム が必要？
2. FROM : どこのテーブル（ビュー）を使うの？
3. WHERE : 条件しぼる？（フィルターする？）
4. GROUP BY : グループ集計しよう
5. ORDER BY : 並び替える？
6. HAVING : GROUP BY後のWHEREと同じ機能
7. JOIN ON : テーブル同士を特定のキーで結合したい
8. WITH句 : クエリ分を見やすくするように、サブクエリは分割しよう
9. LIMIT : 一部だけ表示をしぼりたい（非推奨）
10. DISTINCT : ユニークな値のみ抽出
11. 各種集計指示 : COUNT(), AVG(), SUM()など
12. CASE文 : Excelでいうところのif文

- その他にも色々ありますが（窓関数とか）、適宜公式ドキュメント をググりましょう
- 本日は上記のうち、特に大切なものをご紹介

## BigQueryにアクセスしよう
- 画面で説明。BigQueryコンソロール画面に移動してください [リンク](https://console.cloud.google.com/bigquery?hl=ja)
- 注意：スキャン量に応じて課金されます
- LIMITを入れたからといって、課金は節約されません！（超大事）

## サンプルデータ
- 練習用の公開opendata : `bigquery-public-data.covid19_open_data.covid19_open_data`
- コロナの各国推移データ
- new_confirmed : 新規感染者
- new_deceased : 死亡者数
- country_code : JPが日本
- location_key : 都道府県を表す。JP_13=> TOKYO

## SELECTとFROMを理解しょう
- SELECTのあとに必要なカラム、FROMはデータのソースを定義するだけ（簡単！！）
```sql
SELECT
    col1  -- みたいカラムの名前
    col2,
    col3,
FROM
    `bigquery-public-data.covid19_open_data.covid19_open_data`  -- 参照先のテーブル
```
- 例えば
```sql
SELECT
  date,
  country_code,
  country_name,
  location_key,
  new_confirmed,
  new_deceased,
FROM
  `bigquery-public-data.covid19_open_data.covid19_open_data`
```

- 全てのカラム を持ってきたければ*で引っ張れる。
- ただし、SQLの可読性を損なう + 無駄なカラムのために課金消費するのは嫌。__非推奨！！__
```sql
SELECT
   *
FROM
  `bigquery-public-data.covid19_open_data.covid19_open_data`
```
- ついでに、LIMIT 10を最後にいれると、１０レコードのい表示になる

## WHERE と ORDER BY
- 日本だけのデータが欲しい
- 日付で並び替えたい

```sql
SELECT
  date,
  country_code,
  country_name,
  location_key,
  new_confirmed,
  new_deceased,
FROM
  `bigquery-public-data.covid19_open_data.covid19_open_data`
WHERE
  country_code = "JP"  -- 日本のデータだけとってきて
ORDER BY 
  date DESC  -- dateで並び替え（DESCいれると、降順）
```
## 集計してみよう（SUM）
- 2022-01-01の新規感染者について
- 都道府県の new_confirmed の合計が 日本全体の数値と一致しているか確認していよう
- まず、これを実行してみてください
- 
```sql
SELECT
  date,
  country_code,
  location_key,
  new_confirmed,
FROM
  `bigquery-public-data.covid19_open_data.covid19_open_data`
WHERE
    country_code = "JP"
  AND
    date = "2022-01-01"
ORDER BY 
  location_key
```
- 上を実行すると、location_keyに日本全体と、都道府県が混ざっていることがわかる
- 日本全体 465件を都道府県の合計で再現できるか確認してみる

```sql
SELECT
  SUM(new_confirmed) AS sum_cnt,  -- これが見たいもの
  AVG(new_confirmed) AS avg_cnt,  -- ついでに平均みよう
  COUNT(new_confirmed) AS record_cnt,  -- ついでにレコードの数みよう
FROM
  `bigquery-public-data.covid19_open_data.covid19_open_data`
WHERE
    country_code = "JP"
  AND
    date = "2022-01-01"
  AND
    location_key <> "JP"
```

## GROUP BY
- 2021年の都道府県ごとの平均感染者数を集計しよう
- グループごとの集計はGROUP BYがおすすめ

```sql
SELECT
  location_key, -- group by のキー
  AVG(new_confirmed) AS avg_new_confirmed,  -- 平均計算
FROM
  `bigquery-public-data.covid19_open_data.covid19_open_data`
WHERE
    country_code = "JP"
  AND
    EXTRACT(YEAR FROM date) = 2021  -- 2021年に絞る
  AND
    location_key <> "JP"  -- 日本全体のレコードは除く
GROUP BY
  location_key
ORDER BY
  avg_new_confirmed DESC  -- 平均感染者数が多い順にソート
```

- ついでに、`HAVING`について
- `GROUP BY`した結果に対して、さらにフィルターしたいときに使う

```sql
SELECT
  location_key, -- group by のキー
  AVG(new_confirmed) AS avg_new_confirmed,  -- 平均計算
FROM
  `bigquery-public-data.covid19_open_data.covid19_open_data`
WHERE
    country_code = "JP"
  AND
    EXTRACT(YEAR FROM date) = 2021  -- 2021年に絞る
  AND
    location_key <> "JP"  -- 日本全体のレコードは除く
GROUP BY
  location_key
HAVING
  avg_new_confirmed > 60  -- 60以上のレコードにフィルター
ORDER BY
  avg_new_confirmed DESC  -- 平均感染者数が多い順にソート
```

## WITH句
- サブクエリ（FROMの中に、さらにSELECT文を書くようなもの）は第三者にとって非常に読みにくい。
- WITH句を積極的に活用しましょう
- (以下はあまり意味のないwith句ですが、練習として)

```sql
-- 東京のみの感染者推移テーブルを一時的に作って、それを利用する
WITH tokyo_table AS (
  SELECT
    date,
    SUM(new_confirmed) AS tokyo_new_confirmed
  FROM
    `bigquery-public-data.covid19_open_data.covid19_open_data`
  WHERE
    country_code = "JP"
  AND
    location_key = "JP_13"  -- これが東京
  GROUP BY
    date
)

SELECT
  date,
  tokyo_new_confirmed
FROM
  tokyo_table
ORDER BY 
  date DESC
```

## JOIN
- table と tableをキーを基に、マージしよう
- tokyo_table : 東京のみの感染者推移
- japan_table : 日本全体の感染者推移
- 両テーブルをマージして、推移を比較したい
```sql

WITH tokyo_table AS (
  SELECT
    date,
    SUM(new_confirmed) AS tokyo_new_confirmed
  FROM
    `bigquery-public-data.covid19_open_data.covid19_open_data`
  WHERE
    country_code = "JP"
  AND
    location_key = "JP_13"
  GROUP BY
    date
)
,japan_table AS (
  SELECT
    date,
    SUM(new_confirmed) AS japan_new_confirmed
  FROM
    `bigquery-public-data.covid19_open_data.covid19_open_data`
  WHERE
    country_code = "JP"
  AND
    location_key = "JP"
  GROUP BY
    date
)

-- ここからマージ
SELECT
  j.date,
  t.tokyo_new_confirmed,
  j.japan_new_confirmed
FROM
  japan_table j　 -- japan_tableをjとした
LEFT JOIN
  tokyo_table t
ON
  j.date = t.date
WHERE
  j.date <= DATE_ADD(CURRENT_DATE, INTERVAL -2 DAY) -- 直近のデータはないっぽいので、２日前までのデータにする
ORDER BY 
  j.date DESC
```

## SQLの心の中
- 実行の順番（製品にもよる）
- FROM -> ON -> JOIN -> WHERE -> GROUP BY -> HAVING -> SELECT -> DISTINCT -> ORDER BY -> LIMIT
- 要するに、、、
- LIMITがあれば大丈夫！ではない。課金はあくあでスキャン量に依存する。LIMITはスキャンが終わってから実行される
- 本当のBIGDATAはパーティション（クラスター、index）がついてるので、かならずwhereでパーティションを指定してクエリを投げる（課金爆死する）

## view
- 適当なデータセットの下に、viewを作ってみよう
- viewはデータを物理的に複製しているのではなく、SQLクエリを保存しているようなもの
- viewを見るたびに、クエリ実行される
- tableの作成かviewの構築かは、スキャン量と利用頻度等を勘案しながら考えよう

## スケジュールクエリでテーブルを自動定期更新(便利機能)
- クエリを定期的に実行して、テーブルを上書き or 追加することお簡単

## 実務的には、
### チーム内で必ずルールを決めよう
- コーディング規約
- 特に、命名規約の徹底はしよう（スネークケース）
  - prefixで`raw_`(生データ)、`dwh_`(データウェアハウス)、`dtm_`(データマート)を識別する命名規則は本当におすすめ！是非やろう
    - raw : データソースのコピー（例外は個人情報などはハッシュ化・匿名化しておく）
    - dtm : アプリケーションと一対一対応したもの。例えば、tableauで分析する直前のデータなど。BIツールで複雑な前処理は事故の元なのでNG!!
    - dwh : raw -> dtmの構築の過程において、「あれ？この中間データ他でも必要なんじゃない？」と思ったときに外だしする中間データ。組織がどんどんBQを使い込むと良い感じのdwhが増えてくる
- table viewはsandbox以外、必ずドキュエントを書こう（どこに？フォーマットは？検索できることが大事）
- パーティション（クラスター）の設定・利用ルール
- 当然機微情報の管理なども！

### 一方でどんどん遊ぼう
- データをアップロードしたり
- 他のオープンデータで練習したり
- PythonとBQを繋げてみたり などなど

## 慣れてきたら効率的なクエリを書く
- [公式ドキュメント](https://cloud.google.com/bigquery/docs/best-practices-costs)を読んでみよう
  - SELECT *を避ける
    - 無駄なカラムのためにスキャン料金が発生するのはバカらしい
    - *は可読性を損ねる
  - パーティション(クラスター)を積極的に使う
    - 本当にデータが大きくなってきたとき、パーティション設定しないクエリは料金的に死ぬ
    - テーブルを作るときにパーティションがあるクエリしか受け付けないようにする防御策はある
  - テーブルを非正規化する
    - 意外かもしれませんが、BGの場合、非正規化しておいた方が効率的なクエリが実行できることが多々ある
    - 非正規化されたデータはJOINが必要ないので(列志向DBの特徴かと)
  - JOINする前にデータの量を減らす
  - クエリのキャッシュを有効利用する　などなど

## おまけ
### UDF(ユーザー定義関数)
- BigQueryはUDFという関数を作ることができる
- さらに、以下のようにGCSにjavascriptのライブラリーを格納することによって、javascriptのライブラリーを使用することもできる
- ご参考１：ymym3412さん [SQLで始める自然言語処理](https://ymym3412.hatenablog.com/entry/2020/12/24/001923)
- ご参考２：浅見 [BigQuery で統計処理を完結させる](https://lab.mo-t.com/blog/bigquery-udf)
