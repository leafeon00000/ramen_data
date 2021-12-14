import pandas as pd
import folium
from folium.features import CustomIcon
from folium.plugins import MarkerCluster
import json

class MakeRamenMap() :
  """
  ラーメン情報のCSVからマッピングするクラス。
  """

  def __init__(self, ramen_type):
    """
    コンストラクタ　変数を設定する。

    Parameters
    ----------
    ramen_type : String
      ラーメンの種類を指定する
        "2" : 家系  "3" : 二郎系
    """

    # 変数宣言
    self.ramen_type = ramen_type
    self.csv_path = "./csv/ramendb_data.csv"

  def make_ramen_map(self):
    """
    ラーメンマップを作成する。
    全体の流れを指定。
    """

    # CSVを読み取り、必要な情報を引き出す。
    shop_info_list_df = self.get_ramen_info()

    # 店舗情報リストから地図にマッピングする。
    self.make_map(shop_info_list_df)

  def get_ramen_info(self):
    """
    CSVからデータを取得する。
    """
    csv_path = self.csv_path

    """
    読み込みデータ
    1:系列店名称 2:正式名称 3:URL 4:レート 5:住所都道府県 6:住所市区町村 7:住所その他 8:緯度 9:経度 10:公式サイト 11:facebook 12:twitter 13:instagram
    """
    df = pd.read_csv(
        csv_path,
        encoding="utf-8",
        usecols=[
          "shop_name",
          "shop_name_official",
          "ramendb_url",
          "rating_value",
          "addr_region",
          "addr_local",
          "street_addr",
          "latitude",
          "longitude",
          "official_site", "facebook", "twitter", "instagram"
          ]
    )

    # TODO : フィルターが効かないのであとで検証する。
    #df2 = df[df["rating_value"] < 98].fillna("")
    df2 = df.fillna("")

    return df2

  def make_map(self, df):
    """
    データフレームから地図を作成する。

    Parameters
    ----------
    df : DataFrame
      ラーメン店舗情報リストのデータフレーム
    """

    # Map生成
    ramen_map = folium.Map(
      location=[35.690921, 139.700258],
      zoom_start=12
    )

    # ピンが密集していたらまとめる設定
    #ramen_map = MarkerCluster().add_to(ramen_map)

    for row in df.itertuples():
      """
      print(row[0], row[1], row[2], row[3],
            row[4], row[5], row[6], row[7], float(row[8]), float(row[9]))
      """

      if row[8] == "" or row[9] == "":
        continue

      #if float(row[4]) < 98:
        #break

      popup_label = self.make_popup(row[2], row[3], str(
          round(row[4])), row[10], row[11], row[12], row[13])

      c_icon = self.make_custom_icon(row[1], row[4])

      folium.Marker(
          location=[float(row[8]), float(row[9])],
          popup=popup_label,
          tooltip="【" + str(round(row[4])) + "】" + row[2],
          icon=c_icon
      ).add_to(ramen_map)

    ramen_map.save("./map/ramen_map.html")

  def make_popup(self, shop_name, url, rating_value, official_site, facebook, twitter, instagram):
    """
    popupを作成する。

    Parameters
    ----------
    shop_name : String
      店舗の正式名称
    url : String
      ラーメンDBのURL
    rating_value : float
      点数
    official_site : String
      公式サイトのURL
    facebook : String
      facebookのURL
    twitter : String
      twitterのURL
    instagram : String
      instagramのURL

    Returns
    -------
    popup : String
      ポップアップに表示させるHTML
    """

    links = ""

    if not official_site == "":
      links += "<a href='" + official_site + \
          "' target='_blank' rel='noopener noreferrer'> 公式 </a>"
    if not facebook == "":
      links += "<a href='" + facebook + "' target='_blank' rel='noopener noreferrer'><img src='../icon/facebook.png'> </a>"
    if not twitter == "":
      links += "<a href='" + twitter + \
          "' target='_blank' rel='noopener noreferrer''><img src='../icon/twitter.png'> </a>"
    if not instagram == "":
      links += "<a href='" + instagram + \
          "' target='_blank' rel='noopener noreferrer''><img src='../icon/instagram.png'> </a>"

    popup = "<span style='white-space: nowrap'>" + \
        shop_name + "</span>" + "</br>" + \
        "<span style='white-space: nowrap'><a href='" + url + "' target='_blank'> ラーメンDB </a> " + rating_value + "点 </span>" + \
        "</br>" + links

    return popup


  def make_custom_icon(self, shop_name, rating_value):
    """
    カスタムアイコンを作成する。

    Parameters
    ----------
    shop_name : String
      店舗の正式名称
    rating_value : float
      点数

    Returns
    -------
    icon : folium.map.Icon
      アイコンオブジェクト
    """

    icon = ""
    icon_obj = ""
    pin_color = ""

    # 店舗ごとにアイコンを設定する。
    if shop_name == "ラーメン二郎":
      icon = CustomIcon(
          icon_image="./icon/jiro.png",
          icon_size=(50, 50),
          icon_anchor=(30, 30)
      )
      # 二郎直系の店は特殊アイコン
      return icon

    elif shop_name == "ジャンクガレッジ":
      icon_obj = "plus"
    elif shop_name == "ラーメン大":
      icon_obj = "stop"
    elif shop_name == "優勝軒":
      icon_obj = "star"
    elif shop_name == "ラーメン豚山":
      icon_obj = "chevron-up"
    else:
      icon_obj = "map-marker"

    """
    ピンのカラー
      ※メモ：ピンの色は以下の色からしか選択できない
      [‘red’, ‘blue’, ‘green’, ‘purple’, ‘orange’, ‘darkred’,
      ’lightred’, ‘beige’, ‘darkblue’, ‘darkgreen’, ‘cadetblue’,
      ‘darkpurple’, ‘white’, ‘pink’, ‘lightblue’, ‘lightgreen’,
      ‘gray’, ‘black’, ‘lightgray’]

    if rating_value > 95.0:
      pin_color = "darkred"
    elif rating_value > 90.0:
      pin_color = "red"
    elif rating_value > 85.0:
      pin_color = "lightred"
    elif rating_value > 80.0:
      pin_color = "orange"
    elif rating_value > 75.0:
      pin_color = "beige"
    else:
      pin_color = "lightgray"
    """

    # 点数ごとにピンの色を変更する。
    if rating_value > 95.0:
      pin_color = "darkred"
    elif rating_value > 90.0:
      pin_color = "red"
    elif rating_value > 85.0:
      pin_color = "orange"
    elif rating_value > 80.0:
      pin_color = "green"
    elif rating_value > 75.0:
      pin_color = "darkgreen"
    elif rating_value == 0:
      pin_color = "gray"
    else:
      pin_color = "cadetblue"

    icon=folium.Icon(
        icon=icon_obj,
        icon_color=self.judge_icon_color(),
        color=pin_color,
        prefix="glyphicon"
    )

    return icon

  def judge_icon_color(self):
    """
    アイコンのカラーを決定する。

    Returns
    -------
    color : String
      アイコンの色
    """

    icon_color = ""

    if self.ramen_type == "2":
      # 家系の場合
      icon_color = "red"
    elif self.ramen_type == "3":
      # 二郎系の場合
      icon_color = "#ffff00" # 黄色
    else:
      # その他
      icon_color = "lightgray"

    return icon_color


if __name__ == "__main__":
  mm = MakeRamenMap("3")
  mm.make_ramen_map()
