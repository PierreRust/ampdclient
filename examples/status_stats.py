import asyncio
import sys
import ampdclient


# This script demonstrates the status and stats commands.
# It can be called on with the host as argument:
#    `python status_stats.py 127.0.0.1
#
# If no argument is given, DEFAULT_HOST will be used instead.

# MPD host
DEFAULT_HOST = '127.0.0.1'


def onchange(message):
    print('Message received ' + str(message))


@asyncio.coroutine
def start(host):
    mpd_client = yield from ampdclient.connect(host, 6600)
    mpd_client.cb_onchange = onchange

    print('status')
    status = yield from mpd_client.status()
    print('Status {} '.format(status))

    print('stats')
    stats = yield from mpd_client.stats()
    print('Stats {} '.format(stats))

    yield from mpd_client.close()


def main(argv):
    if len(argv) == 2:
        host = argv[0]
    else:
        host = DEFAULT_HOST

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start(host))


if __name__ == "__main__":
    main(sys.argv[1:])
