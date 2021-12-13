import requests
from bs4 import BeautifulSoup
import time
import write_csv as wc
import json
import pandas as pd
import traceback
import logging
import datetime

class GetRamenDb() :
  """
  ラーメンデータベースからラーメン屋情報を取得するクラス。
  """

  def __init__(self, tag, test_mode):
    """
    コンストラクタ　変数を設定する

    Parameters
    ----------
    tag : String
      "2" : 家系  "3" : 二郎系
    test_mode : boolian
      テストモードにするか否か True:する False:しない
    """

    # 変数宣言
    self.test_mode = test_mode
    self.tag = tag
    self.csv_path = "./csv/ramendb_data.csv"
    self.error_log_path = "./log/error_log.log"

    # エラーログ出力レベルの設定
    logging.basicConfig(filename="./log/error.log", level=logging.ERROR)

  def get_shop_list(self):
    """
    ラーメンデータベースのページから店一覧を取得する。
    """

    ramendb_url_pre = "https://ramendb.supleks.jp/search?page="
    ramendb_url_suf = "&order=point&station-id=0&tags="
    tag = self.tag

    # 変数宣言等
    store_exist_flg = True
    page_num = 1
    cnt = 1

    while store_exist_flg:

      # 店のリスト
      store_info_list = []

      # urlを作成
      url = ramendb_url_pre + str(page_num) + ramendb_url_suf + tag

      # スクレイピング対象の URL にリクエストを送り HTML を取得する
      res = requests.get(url)

      # レスポンスの HTML から BeautifulSoup オブジェクトを作る
      soup = BeautifulSoup(res.text, 'html.parser')

      # 次へボタンがあるかどうかを判定する。
      next_button = soup.select(".pages .next")
      # 店がなければ終わる。
      if len(next_button) == 0:
        print("最後のページです。")
        store_exist_flg = False
        break

      # テストモードの場合、2ページ目の１店舗目を取得して終わる
      if page_num > 3 and self.test_mode:
        print("テストモードのため終了します。")
        store_exist_flg = False
        break

      # 店のリストを作成する
      store_list = soup.select("#searched .info")

      # リストを回して店情報を取得する。
      for i, store in enumerate(store_list):

        # なぜかbs4でランキングを取得すると21件取得されるので、21件目以降はBreak。
        if i >= 20:
          break

        # 店舗ごとのURLを作成する
        url = "https://ramendb.supleks.jp" + store.h4.a.get("href")

        # 詳細を取得し、リストに格納する
        store_info_list.append(self.get_shop_detail(cnt, url))

        # ID用のカウントを1つ増やす。
        cnt += 1

      # 1ページごとにCSVに書き出していく。
      self.write_csv(store_info_list, page_num)

      page_num += 1

      # サーバーへの優しさ
      time.sleep(1)

  def get_shop_detail(self, cnt, url):
    """
    店舗ページより店舗の詳細情報を取得する。

    Parameters
    ----------
    cnt : int
      店舗数のカウント
    url : String
      店舗の詳細ページのURL(ex:https://ramendb.supleks.jp/s/4738.html)

    Returns
    -------
    shop_info : list of String
      店舗情報

    Exception
    ---------
    スクレイピング失敗時
    """

    try:

      # スクレイピング対象の URL にリクエストを送り HTML を取得する
      res_d = requests.get(url)

      # レスポンスの HTML から BeautifulSoup オブジェクトを作る
      soup_d = BeautifulSoup(res_d.text, 'html.parser')

      # JSON-LDから情報を取得する。
      detail_info = soup_d.find("script", type="application/ld+json").text
      js = json.loads(detail_info)

      # データテーブルを取得する
      data_table = soup_d.select_one("#data-table")

      # ランキング情報を取得
      ranking_table = soup_d.select_one(".key-value")

      # 店舗情報の入れ物
      shop_info = []

      print("店舗情報取得: " + str(cnt) + ". " + js["name"])

      # 店舗情報を取得していく
      shop_info.append(cnt)  # ID
      shop_info.append(soup_d.select_one(".shop-name .shopname").text)  # 店名
      shop_info.append("" if soup_d.select_one(
          ".shop-name .branch") is None else soup_d.select_one(".shop-name .branch").text)  # 店舗名
      shop_info.append(js["name"])  # 正式名称
      shop_info.append(js["alternateName"])  # 店かな名
      shop_info.append(url)  # URL
      shop_info.append(soup_d.select_one("#point").select_one(
          ".int").text + soup_d.select_one("#point").select_one(".float").text)  # 点数
      shop_info.append(ranking_table.select_one(
          "tr", text="レビュー件数").select_one("span").text)  # レビュー数
      if "address" in js:
        shop_info.append(js["address"]["addressRegion"])  # 住所（都道府県）
        shop_info.append(js["address"]["addressLocality"])  # 住所（市区町村）
        shop_info.append(js["address"]["streetAddress"])  # 住所（その他）
      else:
        # 外国の場合は住所がデータテーブルにのみ記入されている場合がある。
        shop_info.append(data_table.find(text="住所").parent.parent.find("span").text)
        shop_info.append("")
        shop_info.append("")
      shop_info.append(js["geo"]["latitude"])  # 緯度
      shop_info.append(js["geo"]["longitude"])  # 経度
      shop_info.append("" if data_table.find("td", itemprop="telephone")
                        is None else data_table.find("td", itemprop="telephone").text)  # TEL
      shop_info.append("" if data_table.find(
          text="営業時間") is None else data_table.find(
          text="営業時間").parent.parent.find("td").text)  # 営業時間
      shop_info.append("" if data_table.find(
          text="定休日") is None else data_table.find(
          text="定休日").parent.parent.find("td").text)  # 定休日
      shop_info.append("" if data_table.find(
          text="最寄り駅") is None else data_table.find(
          text="最寄り駅").parent.parent.select_one("td div").text)  # 最寄駅
      shop_info.append("" if data_table.select_one(
          "#shop-data-menu .more") is None else data_table.select_one(
          "#shop-data-menu .more").text.replace("元に戻す", ""))  # メニュー
      shop_info.append("" if data_table.select_one(
          "#shop-data-note .more") is None else data_table.select_one(
          "#shop-data-note .more").text.replace("元に戻す", ""))  # 備考
      # 外部リンク
      if data_table.select_one("#links") is None:
        shop_info += ["", "", "", ""]
      else:
        links = data_table.select_one("#links") # 外部リンク欄を取得

        shop_info.append("" if links.find(text="公式サイト") is None else links.find(text="公式サイト").parent.parent.get("href"))  # 公式サイト
        shop_info.append("" if links.select_one(".facebook") is None else links.select_one(".facebook").get("href"))  #FaceBook
        shop_info.append("" if links.select_one(".twitter") is None else links.select_one(".twitter").get("href")) # Twitter
        shop_info.append("" if links.select_one(".instagram") is None else links.select_one(".instagram").get("href"))  # Instagram

      #print(shop_info)

    except:
      # スクレイピング 失敗時
      print("【" + js["name"] + "】で情報取得失敗。")
      traceback.print_exc()

      # エラーログ出力
      dt_now = datetime.datetime.now()
      logging.error(str(dt_now) + " 【" +
                    js["name"] + "】で情報取得失敗。 \r\n " + traceback.format_exc())

    # サーバーへの優しさ
    time.sleep(1)

    return shop_info

  def write_csv(self, data, page_num):
    """
    店舗情報リストをCSVファイルに出力する。
    CSVのファイルパスはinitにて指定

    Parameters
    ----------
    data : list of String
      店舗情報
    page_num : int
      ページ数（１ページ目かどうかの判断に用いる。）
    """
    header = ["id", "shop_name", "shop_name_branch", "shop_name_official", "shop_name_kana", "ramendb_url", "rating_value", "rating_cnt", "addr_region", "addr_local",
              "street_addr", "latitude", "longitude", "tel", "opening_hors", "regular_holiday", "nearest_station", "menu", "memo", "official_site", "facebook", "twitter", "instagram"]

    df = pd.DataFrame(data, columns=header)



    if page_num == 1:
      # １ページ目のみヘッダーを出力する。
      # CSVファイルを出力
      df.to_csv(self.csv_path, index=False, encoding="utf-8")
    else:
      # 2ページ目以降は追記モードにする。
      df.to_csv(self.csv_path, index=False, header=False, encoding="utf-8", mode="a")

if __name__ == "__main__":
  grd = GetRamenDb("3", False)
  grd.get_shop_list()
