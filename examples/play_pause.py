import asyncio

import ampdclient


def onchange(message):
    print('Message received ' + str(message))


@asyncio.coroutine
def start():
    mpd_client = yield from ampdclient.connect('192.168.1.12', 6600)
    mpd_client.cb_onchange = onchange

    while True:
        yield from asyncio.sleep(5)
        print('pausing')
        yield from mpd_client.command(b'pause\n')
        resp = yield from mpd_client.command(b'status\n')
        print('Response {}'.format(resp) )

        yield from asyncio.sleep(5)
        print('playing')
        yield from mpd_client.command(b'play\n')
        resp = yield from mpd_client.command(b'status\n')
        print('Response {}'.format(resp) )


loop = asyncio.get_event_loop()
loop.run_until_complete(start())
loop.run_forever()
