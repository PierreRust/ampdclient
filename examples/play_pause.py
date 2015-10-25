import asyncio

import ampdclient


def onchange(message):
    print('Message received ' + str(message))


@asyncio.coroutine
def start():
    mpd_client = yield from ampdclient.connect('192.168.1.12', 6600)
    mpd_client.cb_onchange = onchange

    yield from asyncio.sleep(5)
    print('Pausing')
    yield from mpd_client.pause(ampdclient.PAUSE_ON)
    resp = yield from mpd_client.status()
    print('Response {}'.format(resp))

    yield from asyncio.sleep(5)
    print('Resume playing')
    yield from mpd_client.pause(ampdclient.PAUSE_OFF)
    resp = yield from mpd_client.status()
    print('Response {}'.format(resp))

    # If you pass anything else than PAUSE_OFF / PAUSE_ON (i.e. 0 or 1) an
    # exception is raised.
    try:
        yield from mpd_client.pause(5)
    except ampdclient.MpdCommandException as e:
        print('Exception for wrong pause argument: {}'.format(e))

    yield from mpd_client.stop()


loop = asyncio.get_event_loop()
loop.run_until_complete(start())
loop.run_forever()
