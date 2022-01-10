import requests
from bs4 import BeautifulSoup
import time
import write_csv as wc

#url = "https://ramendb.supleks.jp/search?page=51&order=point&station-id=0&tags=3"

def get_ramendb():
  ramendb_url_pre = "https://ramendb.supleks.jp/search?page="
  ramendb_url_suf = "&order=point&station-id=0&tags="
  tag_jiro = "3"
  #tag_ie = "2"

  # スクレイピング対象の URL にリクエストを送り HTML を取得する
  #res = requests.get(url)

  # レスポンスの HTML から BeautifulSoup オブジェクトを作る
  #soup = BeautifulSoup(res.text, 'html.parser')

  # title タグの文字列を取得する
  #store_list = soup.select("#searched h4 a")

  #next_button = soup.select(".pages .next")
  #print(len(next_button))

  store_exist_flg = True
  page_num = 1

  # 店のリスト
  store_info_list = []

  while store_exist_flg:



    # urlを作成
    url = ramendb_url_pre + str(page_num) + ramendb_url_suf + tag_jiro

    # スクレイピング対象の URL にリクエストを送り HTML を取得する
    res = requests.get(url)

    # レスポンスの HTML から BeautifulSoup オブジェクトを作る
    soup = BeautifulSoup(res.text, 'html.parser')

    # 次へボタンがあるかどうかを判定する。
    next_button = soup.select(".pages .next")
    # 店がなければ終わる。
    if len(next_button) == 0:
      print("おみせないよ")
      store_exist_flg = False
      continue

    if page_num > 2:
      print("おわりだよ")
      store_exist_flg = False
      continue

    # 店のリストを作成する
    store_list = soup.select("#searched .info")

    # リストを回して店情報を取得する。
    for store in store_list:

      # データの入れ物を作成
      store_info = []

      # 店名、URL
      print(store.h4.text, store.h4.a.get("href"))
      # 点数
      print(store.select_one(".point-val").text)
      print("-------------")

      store_info.append(store.h4.text)
      store_info.append("https://ramendb.supleks.jp" + store.h4.a.get("href"))
      store_info.append(store.select_one(".point-val").text)

      store_info_list.append(store_info)

    page_num += 1

    # サーバーへの優しさ
    time.sleep(1)

  print("■■■■■■■■■■■■■■■■■■")
  print(store_info_list)

  wc.write_csv(store_info_list)

if __name__ == "__main__":
  get_ramendb()
