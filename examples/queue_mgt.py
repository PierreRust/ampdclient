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


def print_pl(playlist_content):

    for item in playlist_content:

        print('item {} - {}'.format(item[1]['Id'], item[0]))


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

    playqueue_content = yield from mpd_client.playlistid()
    print_pl(playqueue_content)

    # Removes first track in the play queue
    yield from mpd_client.delete_pos(0)

    playqueue_content = yield from mpd_client.playlistid()
    print_pl(playqueue_content)

    # Removes tracks with index 2, 3 and 4 in the play queue
    yield from mpd_client.delete_range(2, 5)

    playqueue_content = yield from mpd_client.playlistid()
    print_pl(playqueue_content)

    # Removes all tracks from index 5 to the end of the play queue
    yield from mpd_client.delete_range(5)

    playqueue_content = yield from mpd_client.playlistid()
    print_pl(playqueue_content)

    # Display info for the first track in the play queue
    track_id = playqueue_content[0][1]['Id']
    print('Track id: {}'.format(track_id))
    playqueue_content = yield from mpd_client.playlistid(track_id)
    print_pl(playqueue_content)

    # Remove the first track in the play queue, by id
    yield from mpd_client.deleteid(track_id)
    try:
        playqueue_content = yield from mpd_client.playlistid(track_id)
    except ampdclient.MpdCommandException as e:
        if e.command == 'playlistid':
            print("OK, track {} was removed from the play queue".
                  format(track_id))

    playqueue_content = yield from mpd_client.playlistid()
    print_pl(playqueue_content)

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
