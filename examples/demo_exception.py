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
        resp = yield from mpd_client.command('foobar')
        # This will never be displayed:
        print('No Mpd client Exception : {}'.format(resp))

    except ampdclient.MpdCommandException as e:
        print('Mpd client Exception : {}'.format(e))

    # the error should be displayed
    # but it does not seem to be true for all errors
    status = yield from mpd_client.status()
    print('Status: {}'.format(status))

    yield from mpd_client.clearerror()

    status = yield from mpd_client.status()
    print('Status: {}'.format(status))

    yield from mpd_client.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(start())
