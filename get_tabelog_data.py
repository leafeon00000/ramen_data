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

class GetTabelogData():
  """
  食べログからデータを取得する。
  """

  def __init__(self):
    """
    コンストラクタ　変数を設定する

    """

    # 変数宣言
    self.csv_path = "./csv/ramendb_data.csv"
    self.error_log_path = "./log/error_log.log"
    self.CHROMEDRIVER_PATH = "./lib/chromedriver"
    self.TABELOG_URL = "https://tabelog.com/"

    # エラーログ出力レベルの設定
    logging.basicConfig(filename="./log/error.log", level=logging.ERROR)

  def get_tabelog_data(self):
    """
    全体の流れを指定する。
    """

    # CSVからデータを取得
    df = self.get_csv_data()

    # スクレイピング
    self.scrape_tabelog(df)


  def get_csv_data(self):
    """
    CSVファイルを取得する。
    """

    df = pd.read_csv(
        self.csv_path,
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

      if int(shop_info[0]) > 3:
        break

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
        print("一致する名前の店名がありませんでした。 : " + shop_info[2])

      else:
        # 一致する店名があった場合は一番上のリンクから店舗詳細を取得しにいく。
        print("一致する名前の店名がありましたので詳細を取得します。 : " + shop_info[2])

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

        print(target_url)
        print(js["aggregateRating"]["ratingValue"])
        print(js["aggregateRating"]["ratingCount"])

        # サーバーへの優しさ
        time.sleep(1)

    # ドライバーを終了する
    driver.quit()

if __name__ == "__main__":
  gtd = GetTabelogData()
  gtd.get_tabelog_data()
