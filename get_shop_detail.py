import requests
from bs4 import BeautifulSoup

url = "https://ramendb.supleks.jp/s/4738.html"

# スクレイピング対象の URL にリクエストを送り HTML を取得する
res = requests.get(url)

# レスポンスの HTML から BeautifulSoup オブジェクトを作る
soup = BeautifulSoup(res.text, 'html.parser')

# 店名
shop_name = soup.select_one(".shop-name .shopname").text
# 店舗名
branch_name = soup.select_one(".shop-name .branch").text

# データテーブル
data_table = soup.select_one("#data-table")

# 正式名称
official_name = data_table.find("span", itemprop="name").text

# 住所
address = data_table.find("span", itemprop="address").text

# TEL
tel = data_table.find("td", itemprop="telephone").text

# 営業時間
opening_hours = data_table.find(text="営業時間").parent.parent.find("td").text

# 定休日
regular_holiday = "なし"
if not data_table.find(text="定休日") is None:
  regular_holiday = data_table.find(text="定休日").parent.parent.find("td").text

# 最寄駅
nearest_station = "なし"
if not data_table.find(text="最寄り駅") is None:
  nearest_station = data_table.find(
      text="最寄り駅").parent.parent.select_one("td div").text

# メニュー
menu = data_table.select_one(
    "#shop-data-menu .more").text.replace("元に戻す", "")

# 備考
note = data_table.select_one("#shop-data-note .more").text.replace("元に戻す", "")

print(menu)
