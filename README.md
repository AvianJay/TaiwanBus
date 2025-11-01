# TaiwanBus
台灣公車，全台皆可使用
# 前置作業
## 從pip下載/更新
```shell
pip install TaiwanBus -U
```
## 從儲存庫安裝
```shell
# 複製儲存庫
git clone https://github.com/AvianJay/TaiwanBus

# 進入資料夾
cd TaiwanBus

# 安裝
pip install .
```
## 更新公車資料庫
```shell
taiwanbus updatedb
```
# 用法
## 終端機
```
usage: taiwanbus [-h] [-p PROVIDER]
          {updatedb,showroute,searchroute,searchstop} ...

TaiwanBus

positional arguments:
   {updatedb,showroute,searchroute,searchstop}
       updatedb            更新公車資料庫
       showroute           顯示公車路線狀態
       searchroute         查詢路線
       searchstop          查詢站點

options:
   -h, --help            show this help message and exit
   -p PROVIDER, --provider PROVIDER
                             資料庫
```
## Python
```python
# 引入依賴庫
from taiwanbus.session import BusSession
from taiwanbus import api

# 更新資料庫
api.update_database()

# 地區資料庫
# 全台（無站點資料，無法查詢單一車站）：twn
# 台中：tcc
# 台北：tpe
# 取得路線
bus = BusSession("304030", api.Provider.TWN)  # 綠3, 全台

# 更新資訊
bus.update()

# 取得資訊
bus.get_info()

# 取得站點
bus.get_stop(...)

# 模擬功能
bus.start_simulate()
bus.get_simulated_info()
```
# taiwanbus.api
## update_database_dir(path: str) -> bool
更新資料庫的路徑，返回資料夾是否可使用。
## update_provider(provider: taiwanbus.api.Provider) -> None
更新使用的地區。
## check_database_update(path: str=None) -> dict
檢查資料庫的更新，返回字典。
範例：
```
{
    "twn": None,  # 沒有更新
    "tcc": 442,  # 有更新，版本號為 442
    "tpe": 442
}
```
## update_database(path: str=None, info: bool=False)
path: 路徑，若未指定將使用預先設定的。
info: 是否記錄更新到控制台
## fetch_route(id: int) -> list
從資料庫取得路線，不包含線上資訊。
<!-- -# 我應該直接返回 list 的第一個的，因為也只有一個 -->
## fetch_all_routes() -> list
從資料庫取得所有路線，不包含線上資訊。
## fetch_routes_by_name(name: str) -> list
使用關鍵字搜尋路線，不包含線上資訊。
## fetch_stop(id: int) -> list
**只適用於 tcc 跟 tpe 資料庫**
從資料庫取得站點資訊，不包含線上資訊。
<!-- -# 我應該直接返回 list 的第一個的，因為也只有一個 -->
## fetch_stops_by_name(name: str) -> list
**只適用於 tcc 跟 tpe 資料庫**
使用關鍵字搜尋站點，不包含線上資訊。
## fetch_paths(id: int) -> list
id 為路線 id
從資料庫取得路線的方向，不包含線上資訊。
## fetch_path_by_stop(id: int) -> list
使用站點id取得路線方向資訊，不包含線上資訊。
## fetch_stops_by_route(route_key: int) -> list
使用路線id取得所有站點，若使用 twn 資料庫將會線上取得站點。
## fetch_stops_nearby(lat: float, lon: float, radius: int = 100) -> list
lat, lan: 座標
radius: 距離（公尺）
取得指定座標內距離的站點，不包含線上資訊。
## getbus(id) -> list
線上取得路線資訊，不包含資料庫的東西。
## get_complete_bus_info(route_key) -> dict
使用路線id取得整個路線的資訊，包含所有資訊。
## format_bus_info(json_data: dict) -> str
將 get_complete_bus_info 返回的字典格式成可視化文字。
# Termux/Discord
項目已移至[AvianJay/TaiwanBus-Utils](https://github.com/AvianJay/TaiwanBus-Utils)。
# Credit
API by Yahoo!<br>
(謝謝Yahoo 沒有你就不會有這個)
