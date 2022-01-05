import folium
import pandas as pd

def main():
  make_map()

def make_map():
  latitude = 35.710063
  longtude = 139.8107
  name = "東京スカイツリー"
  url = "https://www.tokyo-skytree.jp/"

  latitude2 = 36.710063
  longtude2 = 138.8107
  name2 = "ここはどこかな"
  url2 = "https://google.com"

  new_label = make_name_css(name, url)
  new_label2 = make_name_css(name2, url2)

  map = folium.Map(location=[latitude, longtude], zoom_start=18)

  folium.Marker(location=[latitude, longtude],
                popup=new_label,
                icon=folium.Icon(icon="bell", icon_color="#ffff00", color="purple")
                ).add_to(map)

  folium.Marker(location=[latitude2, longtude2],
                popup=new_label2,
                icon=folium.Icon(
      icon="star", icon_color="#ffff00", color="red")
  ).add_to(map)

  #別のLayerを作成
  #folium.TileLayer('openstreetmap').add_to(map)

  #Layerをmy_mapへ追加
  folium.LayerControl().add_to(map)

  map.save("map/map.html")

def make_name_css(name, url):
  popup_label = "<span style='white-space: nowrap'>" + name + "</span>" + "</br>" + \
                "<a href='" + url + "' target='_blank'> サイト </a>"
  return popup_label

if __name__ == "__main__":
  main()
