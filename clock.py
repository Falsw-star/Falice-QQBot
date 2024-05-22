import time
try:
    import thread #type: ignore
except ImportError:
    import _thread as thread

from adapters import adapter_satori as adapter
from matcher import match, run_services
from logger import log, save

log("正在启动适配器线程...","DEBUG")
thread.start_new_thread(adapter.run, ())

#编辑该区域导入模块
from plugins import echo
from plugins import trigger_test
trigger_test.loads()
echo.loads()

from matcher import PLUGINLIST
log("插件列表: " + str(PLUGINLIST),"DEBUG")
#展示已经注册的服务
services_list = []
for plugin_key in PLUGINLIST:
    for service_key in PLUGINLIST[plugin_key]["triggers"]["services"]:
        services_list.append(service_key + f"({plugin_key})")
log("已经注册的服务: " + str(services_list), "DEBUG")

#在logs文件夹里生成每个群聊的log，如果你在使用当前版本的Falice，可以打开它。
make_log = False

#主时钟
log("启动主时钟...","DEBUG")
while True:
    if adapter.STATUS ==False:
        log("等待主开关开启...","DEBUG")
    elif adapter.STATUS == True:
        #运行被注册为“service”的插件
        run_services()
        for msg in adapter.MASSAGE_LIST:
            if make_log == True:
                thread.start_new_thread(save,(msg,))
            thread.start_new_thread(match,(msg,))

            adapter.MASSAGE_LIST.remove(msg)
    time.sleep(1)