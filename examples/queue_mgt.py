import asyncio
import sys
import ampdclient


# This script demonstrates the lsinfo, add, addid and load command.
# It can be called on with the host and the path as argument:
#    `python queue_mgt.py 127.0.0.1 testpl`
#
# If no argument is given, DEFAULT_HOST and DEFAULT_PATH will be used instead.

# MPD host
DEFAULT_HOST = '127.0.0.1'
# directory (relative to the configured music directory) whose files and
# playlists will be loaded in play queue.
DEFAULT_PATH = 'testpl'


def onchange(message):
    print('Message received ' + str(message))


@asyncio.coroutine
def start(host, path):
    mpd_client = yield from ampdclient.connect(host, 6600)
    mpd_client.cb_onchange = onchange

    print('lsinfo')
    dirs, files, playlists = yield from mpd_client.lsinfo(path)

    print('content:\n\tdirs: {} \n\tfiles: {} \n\tplaylists: {}'
          .format(dirs, files, playlists))

    # Add playlists in the play queue
    for p in playlists:
        try:
            yield from mpd_client.load(p[0])
            print('loaded playlist {} '.format(p[0]))
        except ampdclient.MpdCommandException as e:
            # Make sure
            print('Could not load playlist {} \n\t {}'.format(p[0], e))

    # Add files in the play queue
    for f in files:
        try:
            f_id = yield from mpd_client.addid(f[0])
            print('loaded {} - id: {}'.format(f[0], f_id))
        except ampdclient.MpdCommandException as e:

            print('Could not enqueue file {} \n\t {}'.format(f[0], e))

    # Add (recursive) directories in the play queue
    for d in dirs:
        try:
            yield from mpd_client.add(d[0])
            print('Dir added {} '.format(d[0]))

        except ampdclient.MpdCommandException as e:
            print('Could add directory {} \n\t {}'.format(d[0], e))

    # Clear the play queue
    yield from mpd_client.clear()

    yield from mpd_client.close()


def main(argv):
    if len(argv) == 2:
        host = argv[0]
        path = argv[1]
    else:
        host = DEFAULT_HOST
        path = DEFAULT_PATH

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start(host, path))


if __name__ == "__main__":
    main(sys.argv[1:])
