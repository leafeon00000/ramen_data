import configparser

inifile = configparser.SafeConfigParser()
inifile.read('./kensho/config/settings_k.ini')

print('# SECTION1 の設定読み込みa')
print(inifile.get('SECTION1', 'data1'))
print(inifile.get('SECTION1', 'data2'))
print(inifile.get('SECTION1', 'data3'))

print('# SECTION2 の設定読み込みa')
print(inifile.get('SECTION2', 'data1'))
print(inifile.get('SECTION2', 'data2'))
print(inifile.get('SECTION2', 'data3'))

print("---------")
print(inifile.get("HONBAN", "data1"))

print(inifile.get("DEFAULT", "data2"))
