import asyncio
import sys
import functools
import time

from aioesphomeapi import APIClient, APIConnectionError, DeviceInfo, EntityInfo, EntityState

HOST = "washer.local"
PORT = 6053
RELEVANT_SENSORS = [
    "mpu6050_accel_x",
    # "mpu6050_accel_y",
    # "mpu6050_accel_z"
]


sensor_ids = []
current_tuple = []


class Prompt:
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.q = asyncio.Queue(loop=self.loop)
        self.loop.add_reader(sys.stdin, self.got_input)

    def got_input(self):
        asyncio.ensure_future(self.q.put(sys.stdin.readline()), loop=self.loop)

    async def __call__(self, msg, end="\n", flush=False):
        print(msg, end=end, flush=flush, file=sys.stderr)
        return (await self.q.get()).rstrip("\n")


ms_now = lambda: str(int(time.time() * 1000))


def async_on_state(state: EntityState) -> None:
    global current_tuple, sensor_ids
    try:
        if state.key not in sensor_ids:
            return
        idx = sensor_ids.index(state.key)
        if current_tuple[idx] != None:
            if None not in current_tuple:
                print(",".join([ms_now()] + [str(x) for x in current_tuple]), flush=True)
            current_tuple = [None] * len(RELEVANT_SENSORS)
        current_tuple[idx] = state.state
    except:
        import traceback

        traceback.print_exc()


async def main():
    global sensor_ids, current_tuple
    evloop = asyncio.get_running_loop()
    cli = APIClient(evloop, HOST, PORT, None, client_info="datadump", keepalive=1.0)
    terminating = False

    async def reconnect():
        print("connection failed, reconnecting...", file=sys.stderr)
        try:
            await cli.connect(login=True, on_stop=async_on_stop)
            print("connected!", file=sys.stderr)
            await cli.subscribe_states(async_on_state)
        except:
            print("error reconnecting", file=sys.stderr)
            asyncio.create_task(reconnect())

    async def async_on_stop():
        if terminating:
            return
        asyncio.create_task(reconnect())

    await cli.connect(login=True, on_stop=async_on_stop)
    entities, _ = await cli.list_entities_services()
    sensor_ids = [0] * len(RELEVANT_SENSORS)
    for e in entities:
        idx = RELEVANT_SENSORS.index(e.object_id) if e.object_id in RELEVANT_SENSORS else None
        if idx != None:
            sensor_ids[idx] = e.key
    current_tuple = [None] * len(RELEVANT_SENSORS)
    await cli.subscribe_states(async_on_state)
    prompt = Prompt(evloop)
    await prompt("press enter to stop capturing data")
    terminating = True
    await cli.disconnect()
    await asyncio.sleep(3)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

