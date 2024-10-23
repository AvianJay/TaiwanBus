import os
import sys
import requests
import zlib
import xml.etree.ElementTree as et
import aiosqlite
import json
import asyncio

def update_database():
    baseurl = requests.get("https://files.bus.yahoo.com/bustracker/data/dataurl_tcc.txt").text
    r = requests.get(baseurl + "dat_tcc_zh.gz")
    open("bus.sqlite","wb").write(zlib.decompress(r.content))

async def fetch_route(id: int):
    async with aiosqlite.connect('bus.sqlite') as db:
        async with db.execute("SELECT * FROM routes WHERE route_key = ?", (id,)) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result

async def fetch_route_byname(name: str):
    async with aiosqlite.connect('bus.sqlite') as db:
        async with db.execute("SELECT * FROM routes WHERE route_name = ?", (name,)) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result

async def fetch_paths(id: int):
    async with aiosqlite.connect('bus.sqlite') as db:
        async with db.execute("SELECT * FROM paths WHERE route_key = ?", (id,)) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result

async def fetch_stops_by_route(route_key: int):
    async with aiosqlite.connect('bus.sqlite') as db:
        async with db.execute("SELECT * FROM stops WHERE route_key = ?", (route_key,)) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result

def getbus(id):
    r = requests.get(f"https://busserver.bus.yahoo.com/api/route/{id}")
    d = zlib.decompress(r.content).decode()
    x = et.XML(d)
    j = []
    for e in x:
        t = {}
        for a in e.items():
            t[a[0]] = a[1]
        t["bus"] = []
        for ec in e:
            b = {}
            for a in ec.items():
                b[a[0]] = a[1]
            t["bus"].append(b)
        j.append(t)
    return j

async def get_complete_bus_info(route_key):
    route_info = await fetch_route(route_key)
    paths = await fetch_paths(route_key)
    stops = await fetch_stops_by_route(route_key)

    buses = getbus(route_key)

    result = {}

    for path in paths:
        path_id = path['path_id']
        path_name = path['path_name']

        path_stops = []
        for stop in stops:
            if path_id == stop["path_id"]:
                stop_id = str(stop['stop_id'])
                matching_buses = [bus for bus in buses if bus['id'] == stop_id]

                if matching_buses:
                    bus_info = matching_buses[0] 
                    stop.update({
                        "sec": int(bus_info["sec"]),
                        "msg": bus_info["msg"],
                        "t": bus_info["t"],
                        "lon": bus_info["lon"],
                        "lat": bus_info["lat"],
                        "bus": bus_info["bus"]
                    })

                path_stops.append(stop)

        # join every data
        result[path_id] = {
            "route_key": route_key,
            "name": path_name,
            "stops": path_stops
        }

    for path_id, path_data in result.items():
        # 將 stops 依據 sequence 欄位排序
        path_data['stops'] = sorted(path_data['stops'], key=lambda x: x['sequence'])

    return result

def format_bus_info(json_data):
    result = ""
    
    for path_id, path_data in json_data.items():
        route_name = path_data["name"]
        result += f"{route_name}\n"
        
        stops = path_data["stops"]
        for i, stop in enumerate(stops):
            stop_name = stop["stop_name"].strip()  # 去除可能的空白字符
            msg = stop["msg"]
            sec = stop["sec"]
            buses = stop["bus"]

            # 判斷是否顯示msg或剩餘時間
            if msg:
                stop_info = f"{stop_name} {msg}\n"
            elif sec and int(sec) > 0:
                minutes = int(sec) // 60
                seconds = int(sec) % 60
                stop_info = f"{stop_name} 還有{minutes}分{seconds}秒\n"
            else:
                stop_info = f"{stop_name} 即將進站\n"

            # 添加公車資訊
            if buses:
                for bus in buses:
                    bus_id = bus["id"]
                    bus_full = "滿" if bus["full"] == "1" else "未滿"
                    stop_info += f" │  └── {bus_id} {bus_full}\n"
            
            # 使用適當的分隔符顯示站點結構
            if i == len(stops) - 1:
                result += f"└{stop_info}"
            else:
                result += f"├{stop_info}"

    return result




tr = asyncio.run(get_complete_bus_info(304030))
fr = format_bus_info(tr)
print(fr)
