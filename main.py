import folium
import pandas as pd

def main():
  make_map()

def make_map():
  latitude = 35.710063
  longtude = 139.8107
  name = "東京スカイツリー"
  url = "https://www.tokyo-skytree.jp/"



  new_label = make_name_css(name, url)

  map = folium.Map(location=[latitude, longtude], zoom_start=18)

  folium.Marker(location=[latitude, longtude],
                popup=new_label,
                icon=folium.Icon(icon="bell", icon_color="#ffff00", color="purple")
                ).add_to(map)

  map.save("map/map.html")

def make_name_css(name, url):
  popup_label = "<span style='white-space: nowrap'>" + name + "</span>" + "</br>" + \
                "<a href='" + url + "' target='_blank'> サイト </a>"
  return popup_label

if __name__ == "__main__":
  main()
