import asyncio
import ampdclient


MPD_HOST = '192.168.1.12'
MPD_PORT = 6600


def onchange(message):
    print('Message received ' + str(message))


@asyncio.coroutine
def start():
    mpd_client = yield from ampdclient.connect(MPD_HOST, MPD_PORT)
    mpd_client.cb_onchange = onchange

    try:
        resp = yield from mpd_client.command(b'foobar\n')

        # This will never be displayed:
        print('No Mpd client Exception : {}'.format(resp))

    except ampdclient.MpdCommandException as e:
        print('Mpd client Exception : {}'.format(e))

    for i in range(4):
        status = yield from mpd_client.status()
        if status['state'] == 'pause':
            yield from mpd_client.command(b'play\n')
        else:
            yield from mpd_client.command(b'pause\n')
        yield from asyncio.sleep(3)

    mpd_client.stop()


loop = asyncio.get_event_loop()
loop.run_until_complete(start())
