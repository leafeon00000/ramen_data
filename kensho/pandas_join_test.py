import pandas as pd

db_csv_path = "./kensho/csv/ramendb_jiro_data.csv"
tblg_csv_path = "./kensho/csv/tabelog_jiro_data.csv"

df_db = pd.read_csv(
    db_csv_path,
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

df_tblg = pd.read_csv(
    tblg_csv_path,
    encoding="utf-8",
    usecols=[
        "id_tabe",
        "tabelog_url_tabe",
        "rating_value_tabe"
    ]
)

print(df_tblg)

m_df = pd.merge(
    df_db,
    df_tblg,
    left_on="id",
    right_on="id_tabe",
    how='left'
)

print(m_df)
