import asyncio
import ampdclient


MPD_HOST = '192.168.1.5'
MPD_PORT = 6600


def onchange(message):
    print('Message received ' + str(message))


@asyncio.coroutine
def start():
    mpd_client = yield from ampdclient.connect(MPD_HOST, MPD_PORT)
    mpd_client.cb_onchange = onchange

    resp = yield from mpd_client.lsinfo('nas-samba')
    print('Response {}'.format(resp))

    yield from asyncio.sleep(1)

    resp = yield from mpd_client.lsinfo('nas-samba/testpl')
    print('Response {}'.format(resp))

    yield from asyncio.sleep(1)

    resp = yield from mpd_client.lsinfo('nas-samba/Albums/Alternative '
                                        'Rock/Arcade Fire/2004 - '
                                        'Funeral')
    print('Response {}'.format(resp))

    yield from mpd_client.stop()

loop = asyncio.get_event_loop()
loop.run_until_complete(start())
