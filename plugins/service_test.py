from logger import log
from matcher import plugin_registry, load_trigger

def main():
    log("servicetest")

def loads():
    plugin_registry(name="servicetest", status=False)
    load_trigger(name="servicetest", type="services", func=main, trigger="test")