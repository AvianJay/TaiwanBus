# My code is shit.
# Main file for TaiwanBus.
import os
import sys
import requests
import zlib
import xml.etree.ElementTree as et
import aiosqlite
import json
import asyncio
import argparse
import taiwanbus.exceptions
from pathlib import Path

home = os.path.join(Path.home(), ".taiwanbus")
if not os.path.exists(home):
    os.mkdir(home)
current = os.path.join(home, "bus_tcc.sqlite")


def update_database(path=home, info=False):
    local = {"tcc": 0, "tpe": 0, "twn": 0}
    version_path = os.path.join(home, "version.json")
    if os.path.exists(version_path):
        local = json.loads(open(version_path, "r").read())
    if info:
        print("取得台中版本資訊...")
    baseurl = requests.get(
        "https://files.bus.yahoo.com/bustracker/data/dataurl_tcc.txt"
    ).text
    if local["tcc"] < int(baseurl.split("/")[-2]):
        if info:
            print("下載台中版資料庫...")
        r = requests.get(baseurl + "dat_tcc_zh.gz")
        if info:
            print("正在解壓縮...")
        open(os.path.join(path, "bus_tcc.sqlite"), "wb").write(
            zlib.decompress(r.content)
        )
        local["tcc"] = int(baseurl.split("/")[-2])
    if info:
        print("取得台北版本資訊...")
    baseurl = requests.get(
        "https://files.bus.yahoo.com/bustracker/data/dataurl_tpe.txt"
    ).text
    if local["tpe"] < int(baseurl.split("/")[-2]):
        if info:
            print("下載台北版資料庫...")
        r = requests.get(baseurl + "dat_tpe_zh.gz")
        if info:
            print("正在解壓縮...")
        open(os.path.join(home, "bus_tpe.sqlite"), "wb").write(
            zlib.decompress(r.content)
        )
        local["tpe"] = int(baseurl.split("/")[-2])
    if info:
        print("取得全台版本資訊...")
    baseurl = requests.get(
        "https://files.bus.yahoo.com/bustracker/data/dataurl.txt"
    ).text
    if local["twn"] < int(baseurl.split("/")[-2]):
        if info:
            print("下載全台版資料庫（無站點資訊）...")
        r = requests.get(baseurl + "dat_twn_zh.gz")
        if info:
            print("正在解壓縮...")
        open(os.path.join(home, "bus_twn.sqlite"), "wb").write(
            zlib.decompress(r.content)
        )
        local["twn"] = int(baseurl.split("/")[-2])
    open(version_path, "w").write(json.dumps(local))


def checkdb(database_directory=home):

    file_paths = [
        os.path.join(database_directory, "bus_tcc.sqlite"),
        os.path.join(database_directory, "bus_tpe.sqlite"),
        os.path.join(database_directory, "bus_twn.sqlite"),
    ]

    if not any(os.path.exists(path) for path in file_paths):
        raise taiwanbus.exceptions.DatabaseNotFoundError(
            "Cannot find database")


async def fetch_route(id: int):
    async with aiosqlite.connect(current) as db:
        async with db.execute(
            "SELECT * FROM routes WHERE route_key = ?", (id, )
        ) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result


async def fetch_routes_byname(name: str):
    checkdb()
    async with aiosqlite.connect(current) as db:
        async with db.execute(
            "SELECT * FROM routes WHERE route_name LIKE ?",
                ('%' + name + '%', )
        ) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result


async def fetch_stops_byname(name: str):
    checkdb()
    async with aiosqlite.connect(current) as db:
        async with db.execute(
            "SELECT * FROM stops WHERE stop_name LIKE ?", ('%' + name + '%', )
        ) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result


async def fetch_stop(id: int):
    checkdb()
    async with aiosqlite.connect(current) as db:
        async with db.execute(
            "SELECT * FROM stops WHERE stop_id = ?", (id, )
        ) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result


async def fetch_paths(id: int):
    async with aiosqlite.connect(current) as db:
        async with db.execute(
            "SELECT * FROM paths WHERE route_key = ?", (id, )
        ) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result


async def fetch_path_by_stop(id: int):
    stop = await fetch_stop(id)
    pathid = stop[0]["path_id"]
    async with aiosqlite.connect(current) as db:
        async with db.execute(
            "SELECT * FROM paths WHERE route_key = ? and path_id = ?",
            (stop[0]["route_key"], pathid, )
        ) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result


async def fetch_stops_by_route(route_key: int):
    async with aiosqlite.connect(current) as db:
        async with db.execute(
            "SELECT * FROM stops WHERE route_key = ?", (route_key, )
        ) as cursor:
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
    # route_info = await fetch_route(route_key)
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
        result[path_id] = {
            "route_key": route_key,
            "name": path_name,
            "stops": path_stops
        }

    for path_id, path_data in result.items():
        path_data['stops'] = sorted(
            path_data['stops'],
            key=lambda x: x['sequence'])

    return result


def format_bus_info(json_data):
    result = ""

    for path_id, path_data in json_data.items():
        route_name = path_data["name"]
        result += f"{route_name}\n"
        
        stops = path_data["stops"]
        for i, stop in enumerate(stops):
            stop_name = stop["stop_name"].strip()
            msg = stop["msg"]
            sec = stop["sec"]
            buses = stop["bus"]

            if msg:
                stop_info = f"{stop_name} {msg}\n"
            elif sec and int(sec) > 0:
                minutes = int(sec) // 60
                seconds = int(sec) % 60
                stop_info = f"{stop_name} 還有{minutes}分{seconds}秒\n"
            else:
                stop_info = f"{stop_name} 進站中\n"

            # 添加公車資訊
            if buses:
                for bus in buses:
                    bus_id = bus["id"]
                    bus_full = "已滿" if bus["full"] == "1" else "未滿"
                    stop_info += f" │  └── {bus_id} {bus_full}\n"
            
            # 使用適當的分隔符顯示站點結構
            if i == len(stops) - 1:
                result += f" └──{stop_info}"
            else:
                result += f" ├──{stop_info}"

    return result


def main():
    parser = argparse.ArgumentParser(description="TaiwanBus")
    subparsers = parser.add_subparsers(
        dest="cmd",
    )
    # parser_updatedb = subparsers.add_parser("updatedb", help="更新公車資料庫")
    subparsers.add_parser("updatedb", help="更新公車資料庫")
    parser_showroute = subparsers.add_parser("showroute", help="顯示公車路線狀態")
    parser_searchroute = subparsers.add_parser("searchroute", help="查詢路線")
    parser_searchstop = subparsers.add_parser("searchstop", help="查詢站點")
    parser_showroute.add_argument("routeid", help="路線ID", type=int)
    parser_searchroute.add_argument("routename", help="路線名", type=str)
    parser_searchstop.add_argument("stopname", help="站點名", type=str)
    args = parser.parse_args()

    try:
        if args.cmd == "updatedb":
            print("正在更新資料庫...")
            update_database(info=True)
            print("資料庫更新成功。")

        elif args.cmd == "showroute":
            data = asyncio.run(get_complete_bus_info(args.routeid))
            print(format_bus_info(data))

        elif args.cmd == "searchroute":
            rs = asyncio.run(fetch_routes_byname(args.routename))
            for r in rs:
                print(r["route_key"], r["route_name"], r["description"])

        elif args.cmd == "searchstop":
            stops = asyncio.run(fetch_stops_byname(args.stopname))
            for stop in stops:
                route = asyncio.run(fetch_route(stop["route_key"]))[0]
                paths = asyncio.run(fetch_paths(stop["route_key"]))
                cpath = None
                for p in paths:
                    if stop["path_id"] == p["path_id"]:
                        cpath = p
                print(
                    f"{route['provider']} "
                    f"{route['route_name']}[{route['route_key']}] "
                    f"{cpath['path_name']}[{cpath['path_id']}] "
                    f"{stop['stop_name']}[{stop['stop_id']}]"
                )

        else:
            print("使用", sys.argv[0], "來取得幫助。")

    except Exception as e:
        print("錯誤！")
        print(e)
