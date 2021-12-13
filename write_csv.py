import pandas as pd

def write_csv(data):
  header = ["id", "shop_name", "shop_name_branch", "shop_name_official", "shop_name_kana", "ramendb_url", "rating_value", "rating_cnt", "addr_region", "addr_local", "street_addr", "latitude", "longitude", "tel", "opening_hors", "regular_holiday", "nearest_station", "menu", "memo", "official_site", "facebook", "twitter", "instagram"]

  df = pd.DataFrame(data, columns=header)

  # CSV ファイル (employee.csv) として出力
  df.to_csv("./csv/ramendb_data.csv", index=False, encoding="utf-8")
