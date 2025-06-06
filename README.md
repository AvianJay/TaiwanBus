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
import taiwanbus

# 更新資料庫
taiwanbus.update_database()

# 切換地區資料庫
# 全台（無站點資料，無法查詢單一車站）：twn
# 台中：tcc
# 台北：tpe
taiwanbus.update_provider("twn") # 替換 twn 成所需地區

# 取得路線
taiwanbus.get_complete_bus_info("304030") # 綠3
```
# Termux/Discord
項目已移至[AvianJay/TaiwanBus-Utils](https://github.com/AvianJay/TaiwanBus-Utils)。
# Credit
API by Yahoo!<br>
(謝謝Yahoo 沒有你就不會有這個)
