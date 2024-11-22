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
```
usage: taiwanbus [-h] [-p PROVIDER]
          {updatedb,showroute,searchroute,searchstop} ...                                                                    TaiwanBus                                                                                                                           positional arguments:
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
# Termux/Discord
項目已移至[AvianJay/TaiwanBus-Utils](https://github.com/AvianJay/TaiwanBus-Utils)。
# Credit
API by Yahoo!<br>
(因為有秒數所以選這個)
