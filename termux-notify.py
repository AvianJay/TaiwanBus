import os
import sys
import time
import twbus
import asyncio
import argparse

async def gettime(route, stopid):
    stop_info = 0
    route_info = await twbus.get_complete_bus_info(route)
    for path_id, path_data in route_info.items():
        if True:
            route_name = path_data["name"]
        
            stops = path_data["stops"]
            for i, stop in enumerate(stops):
                if stop["stop_id"] == stopid:
                    stop_name = stop["stop_name"].strip()  # 去除可能的空白字符
                    msg = stop["msg"]
                    sec = stop["sec"]
                    buses = stop["bus"]

                    # 判斷是否顯示msg或剩餘時間
                    if msg:
                        stop_info = 999999
                    elif sec and int(sec) > 0:
                        stop_info = int(sec)
                    else:
                        stop_info = int(sec)

    return stop_info

async def gettimeformat(route, stopid):
    stop_info = ""
    route_info = await twbus.get_complete_bus_info(route)
    for path_id, path_data in route_info.items():
        if True:
            route_name = path_data["name"]
        
            stops = path_data["stops"]
            for i, stop in enumerate(stops):
                if stop["stop_id"] == stopid:
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
                        stop_info = f"{stop_name} 還有{minutes}分{seconds}秒"
                    else:
                        stop_info = f"{stop_name} 進站中"

                    # 添加公車資訊
                    if buses:
                        for bus in buses:
                            bus_id = bus["id"]
                            bus_full = "已滿" if bus["full"] == "1" else "未滿"
                            stop_info += f" [{bus_id} {bus_full}]"
    return stop_info

def send_notify(msg):
    os.system(f"termux-notification -t 公車 -i termuxtwbus -c \"{msg}\"")

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="TaiwanBus for Termux")
    subparsers = parser.add_subparsers(dest="cmd",
                                       help='可用的指令為: \n' +
                                            'keep, time\n')
    parser_keep = subparsers.add_parser("keep", help="持續發送模式")
    parser_time = subparsers.add_parser("time", help="在快到站的時候發送")
    parser_keep.add_argument("-r", "--routeid", help="公車ID", type=int, dest="routeid", required=True)
    parser_keep.add_argument("-s", "--stopid", help="車站ID", type=int, dest="stopid", required=True)
    parser_keep.add_argument("-t", "--time", help="發送間隔時間", type=int, dest="waittime", required=True)
    parser_time.add_argument("-r", "--routeid", help="公車ID", type=int, dest="routeid", required=True)
    parser_time.add_argument("-s", "--stopid", help="車站ID", type=int, dest="stopid", required=True)
    parser_time.add_argument("-t", "--time", help="當公車在幾秒內到站提醒", type=int, dest="intimenotify", required=True)
    parser_time.add_argument("-c", "--checktime", help="檢查間隔時間", type=int, dest="checktime", required=True)
    args = parser.parse_args()
    if args.cmd == "keep":
        while True:
            msg = asyncio.run(gettimeformat(args.routeid, args.stopid))
            print("got bus", msg)
            send_notify(msg)
            print("sent notify now waiting")
            time.sleep(args.waittime)
    else:
        while True:
            print("remain", asyncio.run(gettime(args.routeid, args.stopid)))
            if args.intimenotify > asyncio.run(gettime(args.routeid, args.stopid)):
                print("send msg")
                msg = asyncio.run(gettimeformat(args.routeid, args.stopid))
                print("got bus", msg)
                send_notify(msg)
            print("waiting")
            time.sleep(args.checktime)
