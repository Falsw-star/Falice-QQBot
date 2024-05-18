import time
try:
    import thread #type: ignore
except ImportError:
    import _thread as thread

from adapters import adapter_satori as adapter
from matcher import match
from logger import log, save

log("正在启动适配器线程...","DEBUG")
thread.start_new_thread(adapter.run, ())

#编辑该区域导入模块
from plugins import echo
echo.loads()

from matcher import PLUGINLIST
log(PLUGINLIST,"DEBUG")

#主时钟
log("启动主时钟...","DEBUG")
while True:
    if adapter.STATUS ==False:
        log("等待主开关开启...","DEBUG")
    elif adapter.STATUS == True:
        for msg in adapter.MASSAGE_LIST:
            thread.start_new_thread(save,(msg,))
            thread.start_new_thread(match,(msg,))

            adapter.MASSAGE_LIST.remove(msg)
    time.sleep(1)