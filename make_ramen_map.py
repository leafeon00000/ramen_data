import pandas as pd
import folium
from folium.features import CustomIcon
from folium.plugins import MarkerCluster
import configparser
import os
import errno

class MakeRamenMap() :
  """
  ラーメン情報のCSVからマッピングするクラス。
  """

  def __init__(self, ramen_type, test_mode):
    """
    コンストラクタ　変数を設定する。

    Parameters
    ----------
    ramen_type : String
      ラーメンの種類を指定する
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

    # 本番モードか検証モードかの設定
    mode = "KENSHO" if test_mode else "HONBAN"

    # 変数宣言
    self.ramen_type = ramen_type
    if self.ramen_type == "2":
      # /_/_/_/_/_/家系_/_/_/_/_/_/
      # ラーメンデータベースから取得したCSVのファイルパス
      self.RAMEN_DB_CSV_PATH = config_ini.get(mode, "IE_RAMENDB_CSV_PATH")
      # 食べログから取得したデータを格納するCSVファイルパス
      self.TABELOG_CSV_PATH = config_ini.get(mode, "IE_TABELOG_CSV_PATH")
      # 作成したマップのファイルのパス
      self.MAP_FAIL_PATH = config_ini.get(mode, "IE_MAP_FAIL_PATH")

    elif self.ramen_type == "3":
      # /_/_/_/_/_/二郎系/_/_/_/_/_/
      # ラーメンデータベースから取得したCSVのファイルパス
      self.RAMEN_DB_CSV_PATH = config_ini.get(mode, "JIRO_RAMENDB_CSV_PATH")
      # 食べログから取得したデータを格納するCSVファイルパス
      self.TABELOG_CSV_PATH = config_ini.get(mode, "JIRO_TABELOG_CSV_PATH")
      # 作成したマップのファイルのパス
      self.MAP_FAIL_PATH = config_ini.get(mode, "JIRO_MAP_FAIL_PATH")


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

    """
    ラーメンデータベース読み込みデータ
    1:id 2:系列店名称 3:正式名称 4:URL 5:レート 6:住所都道府県 7:住所市区町村 8:住所その他 9:緯度 10:経度 11:公式サイト 12:facebook 13:twitter 14:instagram
    """
    df_db = pd.read_csv(
        self.RAMEN_DB_CSV_PATH,
        encoding="utf-8",
        usecols=[
          "id",
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
    #df_db2 = df[df["rating_value"] < 98].fillna("")
    df_db2 = df_db.fillna("")

    """
    食べログ読み込みデータ
    1:id 2:url 3:点数
    """
    df_tblg = pd.read_csv(
        self.TABELOG_CSV_PATH,
        encoding="utf-8",
        usecols=[
            "id_tabe",
            "tabelog_url_tabe",
            "rating_value_tabe"
        ]
    )

    # TODO : フィルターが効かないのであとで検証する。
    #df_tblg = df[df["rating_value"] < 98].fillna("")
    df_tblg2 = df_tblg.fillna("")

    df_m = pd.merge(
        df_db2,
        df_tblg2,
        left_on="id",
        right_on="id_tabe",
        how='left'
    )

    df_m = df_m.fillna({
      "id_tabe" : "",
      "tabelog_url_tabe" : "",
      "rating_value_tabe" : ""
    })

    return df_m

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

    for index, row in df.iterrows():

      """
      print("---------------")
      print(row[0], row[1], row[2], row[3],
            row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14],row[15], row[16])
      """

      # 経度緯度がない場合はスキップ
      if row["latitude"] == "" or row["longitude"] == "":
        continue

      #if float(row[4]) < 90:
        #break

      # 食べログの点数を100換算したものと、ラーメンデータベースの点数の平均値を算出する。
      if row["rating_value_tabe"] == "":
        my_value = row["rating_value"]
      else:
        my_value = (row["rating_value"] + (row["rating_value_tabe"] * 20)) / 2

      print(row["shop_name_official"], row["rating_value"], row["rating_value_tabe"], my_value)

      # クリックした際のラベルを作成する。
      popup_label = self.make_popup(row[2], row[3], str(
          round(row[4], 2)), row[10], row[11], row[12], row[13], row["tabelog_url_tabe"], str(row["rating_value_tabe"]))

      # カスタムアイコンを設定する。
      c_icon = self.make_custom_icon(row[1], my_value)

      # オンマウス時の表示内容を作成する。
      folium.Marker(
          location=[float(row[8]), float(row[9])],
          popup=popup_label,
          tooltip="【" + str(round(my_value)) + "】" + row[2],
          icon=c_icon
      ).add_to(ramen_map)

    #Layerをmy_mapへ追加
    folium.LayerControl().add_to(ramen_map)

    # 地図を保存する
    ramen_map.save(self.MAP_FAIL_PATH)

  def make_popup(self, shop_name, url, rating_value, official_site, facebook, twitter, instagram, tblg_url, tblg_rating_value):
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

    # リンクがある場合に表示される部分を作成する
    links = ""

    if not official_site == "":
      links += "<a href='" + official_site + \
          "' target='_blank' rel='noopener noreferrer'> <img src='../icon/official_icon.png'> </a>"
    if not facebook == "":
      links += "<a href='" + facebook + "' target='_blank' rel='noopener noreferrer'><img src='../icon/facebook.png'> </a>"
    if not twitter == "":
      links += "<a href='" + twitter + \
          "' target='_blank' rel='noopener noreferrer''><img src='../icon/twitter.png'> </a>"
    if not instagram == "":
      links += "<a href='" + instagram + \
          "' target='_blank' rel='noopener noreferrer''><img src='../icon/instagram.png'> </a>"

    # クリックした際に表示されるHTMLを作成する。
    popup = "<span style='white-space: nowrap'>" + \
        shop_name + "</span>" + "</br>" + \
        "<span style='white-space: nowrap'><a href='" + url + \
        "' target='_blank'> <img src='../icon/ramendb.gif'> </a> " + \
        rating_value + "点 </span>" + "</br>"

    # 食べログのURLがある場合
    if not tblg_url == "":
      popup = popup + "<span style='white-space: nowrap'><a href='" + tblg_url + \
          "' target='_blank'> <img src='../icon/tabelog.png'> </a> " + \
          str(tblg_rating_value) + "点 </span>" + "</br>"

    # リンクがある場合のみ実行する処理
    if not len(links) == 0:
      links = "<span style = 'white-space: nowrap' > <img src = '../icon/link_icon.png' > " + links + "</span >"
      popup = popup + links

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

    """
    # 店舗ごとにアイコンを設定する。
    if shop_name == "ラーメン二郎":
      icon = CustomIcon(
          icon_image="./icon/jiro.png",
          icon_size=(50, 50),
          icon_anchor=(30, 30)
      )
      # 二郎直系の店は特殊アイコン
      return icon
    """

    if shop_name == "ジャンクガレッジ":
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
    if rating_value > 80.0:
      pin_color = "darkred"
    elif rating_value > 70.0:
      pin_color = "red"
    elif rating_value > 60.0:
      pin_color = "orange"
    elif rating_value > 50.0:
      pin_color = "green"
    elif rating_value > 40.0:
      pin_color = "darkgreen"
    elif rating_value < 1.0:
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
  mm = MakeRamenMap("3", False)
  mm.make_ramen_map()
