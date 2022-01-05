from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import json
import time
import pandas as pd
import traceback
import logging
import datetime
import configparser
import os
import errno

class GetTabelogData():
  """
  食べログからデータを取得する。
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

    # 設定ファイルの読み込み
    config_ini = configparser.ConfigParser()
    config_ini_path = "./config/settings.ini"

    # 指定したiniファイルが存在しない場合、エラー発生
    if not os.path.exists(config_ini_path):
      raise FileNotFoundError(errno.ENOENT, os.strerror(
        errno.ENOENT), config_ini_path)

    config_ini.read(config_ini_path, encoding='utf-8')

    mode = "KENSHO" if test_mode else "HONBAN"

    ## 変数宣言 ##
    # ラーメンデータベースから取得したCSVのファイルパス
    self.RAMEN_DB_CSV_PATH = config_ini.get(mode, "RAMEN_DB_CSV_PATH")
    # エラーログファイル格納場所
    self.ERROR_LOG_PATH = config_ini.get(mode, "ERROR_LOG_PATH")
    # Chromeドライバーの配置場所
    self.CHROMEDRIVER_PATH = config_ini.get(mode, "CHROMEDRIVER_PATH")
    # 食べログのURL
    self.TABELOG_URL = config_ini.get(mode, "TABELOG_URL")
    # 食べログから取得したデータを格納するCSVファイルパス
    self.TABELOG_CSV_PATH = config_ini.get(mode, "TABELOG_CSV_PATH")
    # ヘッダーを出力するかどうかのフラグ（CSVファイルを出力する際に最初のページかどうかを判定する。）
    self.top_page_flg = True

    print(self.CHROMEDRIVER_PATH)

    # エラーログ出力レベルの設定
    logging.basicConfig(filename=self.ERROR_LOG_PATH, level=logging.ERROR)


  def get_tabelog_data(self):
    """
    全体の流れを指定する。
    """

    # CSVからデータを取得
    df = self.get_csv_data()

    # スクレイピング、CSV書き込み
    self.scrape_tabelog(df)


  def get_csv_data(self):
    """
    CSVファイルを取得する。
    """

    # ラーメンDBのCSVからIDと公式店名を取得する。
    df = pd.read_csv(
        self.RAMEN_DB_CSV_PATH,
        encoding="utf-8",
        usecols=[
            "id",
            "shop_name_official"
        ]
    )

    return df


  def scrape_tabelog(self, df):
    """
    食べログをスクレイピングする。
    """

    # オプションからヘッドレスモードを設定
    option = Options()
    option.add_argument('--headless')

    # サービスオブジェクトを生成する。
    chrome_service = fs.Service(executable_path=self.CHROMEDRIVER_PATH)
    #Chromeを操作するドライバーを生成
    driver = webdriver.Chrome(service=chrome_service, options=option)

    for shop_info in df.itertuples():

      # 食べログへアクセス
      driver.get(self.TABELOG_URL)

      # 明示的な待機
      driver.implicitly_wait(20)

      # 検索ボックスを特定
      elem = driver.find_element(By.ID, "sk")
      # 店名を入力して、「Enter」を押す
      elem.send_keys(shop_info[2] + Keys.RETURN)

      # 明示的な待機
      driver.implicitly_wait(20)

      # 検索結果から一致する店名があるかどうかを判定する
      search_result = driver.find_elements_by_css_selector(
          ".js-rstlist-info.rstlist-info")

      if len(search_result) == 0:
        # 一致する店名がない場合は終了
        print("一致する名前の店名がありませんでした。 : " +
              str(shop_info[1]) + ". " + shop_info[2])

      else:
        # 一致する店名があった場合は一番上のリンクから店舗詳細を取得しにいく。
        print("一致する名前の店名がありましたので詳細を取得します。 : " + str(shop_info[1]) + ". " + shop_info[2])

        # 店舗情報の入れ物
        tabelog_shop_info = []

        # リンクのURLを取得する。
        target_url = search_result[0].find_element_by_tag_name(
            "a").get_attribute("href")

        # スクレイピング対象の URL にリクエストを送り HTML を取得する
        res = requests.get(target_url)

        # レスポンスの HTML から BeautifulSoup オブジェクトを作る
        soup = BeautifulSoup(res.text, 'html.parser')

        # JSON-LDから情報を取得する。
        detail_info = soup.find("script", type="application/ld+json").text
        js = json.loads(detail_info)

        try:

          # 店舗情報を取得していく。
          tabelog_shop_info.append(str(shop_info[0]))  # ID
          tabelog_shop_info.append(js["name"])  # 店名
          tabelog_shop_info.append(target_url)  # URL
          if js["aggregateRating"] is None:
            # 点数がない場合
            tabelog_shop_info += ["", ""]
          else:
            # 点数がある場合
            tabelog_shop_info.append(js["aggregateRating"]["ratingValue"])  # 点数
            tabelog_shop_info.append(js["aggregateRating"]["ratingCount"])  # レビュー数
          tabelog_shop_info.append(js["address"]["postalCode"])  # 郵便番号
          tabelog_shop_info.append(js["address"]["addressRegion"])  # 住所(都道府県)
          tabelog_shop_info.append(js["address"]["addressLocality"])  # 住所(市区町村)
          tabelog_shop_info.append(js["address"]["streetAddress"])  # 住所(その他)
          tabelog_shop_info.append(str(js["geo"]["latitude"]))  # 緯度
          tabelog_shop_info.append(str(js["geo"]["longitude"]))  # 経度
          tabelog_shop_info.append(js["telephone"])  # TEL
          eigyo = soup.select_one(
              "#rst-data-head").select(".rstinfo-table__subject-text")
          for s in eigyo:
            eigyo_info = str(s).replace("<br/>", "\r\n").replace('<p class="rstinfo-table__subject-text">', "").replace("</p>", "")
          tabelog_shop_info.append(eigyo_info)  # 営業日情報
          tabelog_shop_info.append("" if soup.find(text="最寄り駅：") is None else soup.find(
              text="最寄り駅：").parent.parent.find("span").text)  # 最寄駅

          tabelog_shop_info.append("" if soup.select_one(
              ".homepage") is None else soup.select_one(".homepage").find("a").get("href"))  # ホームページ

          tabelog_shop_info.append("" if soup.find(text="公式アカウント") is None else soup.find(
              text="公式アカウント").parent.parent.find("a").get("href"))  # 公式アカウント

          li = []
          li.append(tabelog_shop_info)


        except:
          # スクレイピング失敗時
          print("【" + js["name"] + "】 で食べログ情報取得失敗。")
          traceback.print_exc()

          # エラーログ出力
          dt_now = datetime.datetime.now()
          logging.error(str(dt_now) + "【" + js["name"] + "】 で食べログ情報取得失敗。\r\n" + traceback.format_exc())

        # CSVに出力する、
        try:
          self.write_csv(li)

        except:

          # CSV出力失敗時
          print("【" + js["name"] + "】 でCSV出力失敗")

          traceback.print_exc()

          # エラーログ出力
          dt_now = datetime.datetime.now()
          logging.error(str(dt_now) + "【" +
                        js["name"] + "】 でCSV出力失敗。\r\n" + traceback.format_exc())

        # サーバーへの優しさ
        time.sleep(1)

    # ドライバーを終了する
    driver.quit()

  def write_csv(self, data):
    """
    食べログから取得した店舗情報をCSVファイルに出力する。
    CSVのファイルパスはinitにて指定

    Parameter
    ---------
    data : list of String
      店舗情報
    """

    header = ["id_tabe", "shop_name_tabe", "tabelog_url_tabe", "rating_value_tabe", "rating_cnt_tabe",
              "post_code_tabe", "addr_region_tabe", "addr_local_tabe", "street_addr_tabe", "latitude_tabe", "longitude_tabe", "tel_tabe", "eigyo_info_tabe", "nearest_station_tabe", "homepage_tabe", "official_account_tabe"]

    df_tabelog = pd.DataFrame(data, columns=header)

    if self.top_page_flg:

      # フラグを変更する。
      self.top_page_flg = False

      # 1ページ目のみヘッダーを出力する。
      # CSVファイルを出力
      df_tabelog.to_csv(self.TABELOG_CSV_PATH, index=False, encoding="utf-8")

    else:
      # 2ページ目以降は追記モードにする。
      df_tabelog.to_csv(self.TABELOG_CSV_PATH, index=False,
                header=False, encoding="utf-8", mode="a")


if __name__ == "__main__":
  gtd = GetTabelogData("3", False)
  gtd.get_tabelog_data()
