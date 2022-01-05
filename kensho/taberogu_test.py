from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import json
import time
import re

CHROMEDRIVER_PATH = "./lib/chromedriver"
TABELOG_URL = "https://tabelog.com/"

# https://tabelog.com/tokyo/A1328/A132801/13024745/
shop_name = "ラーメン二郎 ひばりヶ丘駅前店"

# https://tabelog.com/kanagawa/A1410/A141002/14038776/
shop_name = "らぁ麺 飯田商店"

#shop_name = "ラaaaaaaaaaa"

# オプションからヘッドレスモードを設定
option = Options()
option.add_argument('--headless')

# サービスオブジェクトを生成する。
chrome_service = fs.Service(executable_path = CHROMEDRIVER_PATH)
#Chromeを操作するドライバーを生成
driver = webdriver.Chrome(service=chrome_service, options=option)

# 食べログへアクセス
driver.get(TABELOG_URL)

# 明示的な待機
driver.implicitly_wait(20)

# 検索ボックスを特定
elem = driver.find_element(By.ID, "sk")
# 店名を入力して、「Enter」を押す
elem.send_keys(shop_name + Keys.RETURN)

# 明示的な待機
driver.implicitly_wait(20)

# 検索結果から一致する店名があるかどうかを判定する
search_result = driver.find_elements_by_css_selector(".js-rstlist-info.rstlist-info")
if len(search_result) == 0:
  # 一致する店名がない場合は終了
  print("一致する名前の店名がありませんでした。 : " + shop_name)

else:
  # 一致する店名があった場合は一番上のリンクから店舗詳細を取得しにいく。
  print("一致する名前の店名がありましたので詳細を取得します。")

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

  print(js["name"])  # 店舗名
  print(target_url)  # 食べログのURL
  print(js["aggregateRating"]["ratingValue"])  # レート
  print(js["aggregateRating"]["ratingCount"])  # レビュー数
  print(js["geo"]["latitude"])  # 緯度
  print(js["geo"]["longitude"])  # 経度
  print(js["address"]["postalCode"])  # 郵便番号
  print(js["address"]["addressRegion"])  # 住所(都道府県)
  print(js["address"]["addressLocality"])  # 住所(市区町村)
  print(js["address"]["streetAddress"])  # 住所(その他)
  print(js["telephone"])  # 電話番号

  moyori = soup.find(text="最寄り駅：").parent.parent.find("span").text
  print(moyori)  # 最寄駅

  eigyo = soup.select_one(
      "#rst-data-head").select(".rstinfo-table__subject-text")

  for s in eigyo:
    s2 = str(s).replace(
        "<br/>", "\r\n").replace('<p class="rstinfo-table__subject-text">', "").replace("</p>","")
    #s3 = re.sub("<.*>", "", s2)

    print(s2)  # 営業時間情報

  if not soup.select_one(".homepage") is None:
    homepage = soup.select_one(".homepage").find("a").get("href")  # ホームページ
    print(homepage)

  if not soup.find(text="公式アカウント") is None:
    kousiki = soup.find(text="公式アカウント").parent.parent.find("a").get("href")
    print(kousiki)

    #.replace("<br/>", "/r/n")


  # サーバーへの優しさ
  time.sleep(1)

# ドライバーを終了する
driver.quit()
