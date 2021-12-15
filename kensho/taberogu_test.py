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

  print(js["name"])
  print(target_url)
  print(js["aggregateRating"]["ratingValue"])
  print(js["aggregateRating"]["ratingCount"])
  print(js["geo"]["latitude"])
  print(js["geo"]["longitude"])
  print(js["name"])
  print(js["address"]["postalCode"])
  print(js["address"]["addressRegion"])
  print(js["address"]["addressLocality"])
  print(js["address"]["streetAddress"])
  print(js["telephone"])

  moyori = soup.find(text="最寄り駅：").parent.parent.find("span").text
  print(moyori)

  eigyo = soup.select_one(
      "#rst-data-head").select(".rstinfo-table__subject-text")

  for s in eigyo:
    s2 = str(s).replace(
        "<br/>", "\r\n").replace('<p class="rstinfo-table__subject-text">', "").replace("</p>","")
    #s3 = re.sub("<.*>", "", s2)

    print(s2)



    #.replace("<br/>", "/r/n")


  # サーバーへの優しさ
  time.sleep(1)

# ドライバーを終了する
driver.quit()
