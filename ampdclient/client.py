import asyncio


# Constants for pause / resume
PAUSE_ON = 1
PAUSE_OFF = 0

CONSUME_ON = 1
CONSUME_OFF = 0

RANDOM_ON = 1
RANDOM_OFF = 0


def parse_lines_to_dict(lines):
    """
    Parse a list of message into a dictionnary.
    Used for command like status and stats.

    :param lines: an array of string where each item has the following format
    'name: value'
    :return: a dictionary with the names (as keys) and values found in the
    lines.
    """
    res = {k: v.strip() for k, v in (m.split(':', 1) for m in lines)}
    return res


def parse_to_dicts(lines, containers):
    """
    Parses a list of lines into tuples places in the given containers.

    The lists of lines has the following format

    token1: tval1
    key1: val11
    key2: val12
    token1: tval2
    key1: val21
    key2: val22



    :param lines:
    :param containers: a dictionary { token : array_instance}
    :return:
    """

    pairs = [(a, b.strip()) for a, b in (m.split(':', 1) for m in lines)]
    item = {}
    kind, name = None, None
    for j in range(0, len(pairs)):
        if pairs[j][0] in containers.keys():
            if j != 0:
                containers[kind].append((name, item))
            item = {}
            kind = pairs[j][0]
            name = pairs[j][1]
        else:
            item[pairs[j][0]] = pairs[j][1]
    if kind is not None:
        containers[kind].append((name, item))

    return containers


def parse_playlist(lines):
    files = []
    containers = {'file': files}

    parse_to_dicts(lines, containers)

    return files


def parse_lsinfo(lines):
    dirs = []
    files = []
    playlists = []
    containers = {'directory': dirs,
                  'file': files,
                  'playlist': playlists}

    parse_to_dicts(lines, containers)

    return dirs, files, playlists


def _format_range(start, end):
    """
    Build string for format specification.
    used by many commands, like delete, load, etc...
    :param start:
    :param end:
    :return: the string to be used for range in the command
    """
    if start is None:
        return ''
    if end is None:
        return str(start)+':'
    return str(start)+':'+str(end)


class MpdCommandException(Exception):

    def __init__(self, message, error, line, command, msg):

        super(Exception, self).__init__(message)

        # error num
        self.error = error
        # line of the error in the command list
        self.line = line
        self.command = command
        # Error message.
        self.msg = msg


class MpdClientProtocol(asyncio.StreamReaderProtocol):

    def __init__(self, host=None, port=None, timeout=10, loop=None):

        self.host = host
        self.port = port
        self.timeout = timeout

        self._protocol_version = None
        self.cb_onchange = None

        self.loop = loop
        stream_reader = asyncio.StreamReader(loop=loop)
        super().__init__(stream_reader, self.client_connected, loop)

        self._responses = asyncio.Queue(loop=loop)
        self._cmds = asyncio.Queue(loop=loop)

        self.f_closed = asyncio.Future(loop=loop)
        self.f_stopped = asyncio.Future(loop=loop)

    @property
    def protocol_version(self):
        return self._protocol_version

    @asyncio.coroutine
    def command(self, cmd):
        """
        Send an arbitrary command to mpd.
        This method raises a MpdCommandException if mpd returned a error.

        Example: `client.command(b'play')`

        :param cmd:The command must be a string. If it does not end with
        `\n`, one will be added.
        :return:
        """
        cmd = cmd.encode(encoding='UTF-8')
        if cmd[-1] != b'\n':
            # make sure the command ends with \n, otherwise the client will
            # block
            cmd += b'\n'
        yield from self._cmds.put(cmd)
        resp = yield from self._get_response()
        return resp

    @asyncio.coroutine
    def status(self):
        lines = yield from self.command('status')
        # TODO: used named tuple for status info
        return parse_lines_to_dict(lines)

    @asyncio.coroutine
    def stats(self):
        lines = yield from self.command('stats')
        # TODO: used named tuple for stats info
        return parse_lines_to_dict(lines)

    @asyncio.coroutine
    def clearerror(self):
        """
        Clears the current error message in status.
        This is also accomplished by any command that starts playback.

        :return: True
        """
        yield from self.command('clearerror')
        return True

    @asyncio.coroutine
    def lsinfo(self, path):
        """
        list information.

        :param path:
        :return: a tuple (dirs, files, playlists) corresponding to the
        content of the path.
        dirs, files, playlists are arrays of tuples (path, info) where path
        is the path, relative to the music directory, of the item and info is
        a dictionnary of meta-data for this item.

        """
        resp = yield from self.command('lsinfo "' + path + '"')
        # TODO: improve return format, array of tuples of dict...
        return parse_lsinfo(resp)

    @asyncio.coroutine
    def close(self):
        try:
            yield from self.command('close')
        except MpdCommandException:
            pass
        yield from self.f_stopped

    # Playlist

    def playlistid(self, track_id=None):
        """
        Get information about track(s) in the play queue.

        :param track_id: optional, specifies a single track to display info for.
        If `pos` id not given or `None`, the info for all tracks is returned.

        :return: an array of tuples `(uri, attrs)` where `uri` is the uri of
        the track and `attrs` is a dictionary with all attributes for the track.
        The only attributes guaranteed to be in `attrs` are `Id` and `Pos`.
        """
        track_id = '' if track_id is None else track_id
        lines = yield from self.command('playlistid {}'.format(track_id))
        return parse_playlist(lines)

    def playlistinfo(self, pos=None):
        """
        Get information about track(s) in the play queue.

        :param pos: optional, specifies the position of a single track to get
        info for. If `pos` id not given or `None`, the info for all tracks is
        returned.
        :return: an array of tuples `(uri, attrs)` where `uri` is the uri of
        the track and `attrs` is a dictionary with all attributes for the track.
        The only attributes guaranteed to be in `attrs` are `Id` and `Pos`.
        """
        pos = '' if pos is None else pos
        lines = yield from self.command('playlistinfo {}'.format(pos))
        return parse_playlist(lines)

    def playlistinfo_range(self, start, end=None):
        """
        Get information about track(s) in the play queue.

        :param start: start of the range of the tracks.
        :param end: optional, end of the range. If end is not given, info for
        all tracks from start to the end of the play queue will be returned.
        :return: an array of tuples `(uri, attrs)` where `uri` is the uri of
        the track and `attrs` is a dictionary with all attributes for the track.
        The only attributes guaranteed to be in `attrs` are `Id` and `Pos`.
        """
        track_range = _format_range(start, end)
        lines = yield from self.command('playlistinfo {}'.format(track_range))
        return parse_playlist(lines)

    def load(self, playlist, start=None, end=None):
        """
        Loads the playlist into the play queue.

        :param playlist: it can either
        * the name (without the .m3u suffix)of a stored playlist managed by
        mpd (and hence stored inside the configured playlist directory)
        * or the path, relative to the music directory, of a user playlist
        * an uri to a remote playlist

        In these last two cases, supported playlist formats depend on the
        enabled playlist plugins.
        :param start: start of the range.
        :param end: optional, end of the range. If end is not given, all tracks
        from start to the end of the playlist queue will be added.

        :return:
        """
        track_range = _format_range(start, end)
        yield from self.command('load "{}" {}'.format(playlist, track_range))
        return True

    # Play queue control

    def add(self, uri):
        """
        Adds the track(s) to the playlist.

        :param uri: uri to directory, a single file or a network stream
        File and directory uri are relative to the root of mpd's music
        directory (and must not start with `/`).
        If uri is a directory, all tracks are added recursively. Uri to
        directories must NOT end with '/'.
        When connecting locally (with the socket interface), a 'file://' uri
        can be used to add local files outside the music directory.

        :return: True is the add succeeded, raises an MpdCommandException
        otherwise.
        """
        yield from self.command('add "{}"'.format(uri))
        return True

    def addid(self, uri):
        """
        Adds a track to the playlist (non-recursive) and returns the song id.

        For example:
        `trackid = client.addid( "foo.mp3")`

        :param uri: an uri to a single file or an URL to a network stream.


        :return: the song id in the play queue if the operation succeeded,
        raises an MpdCommandException otherwise.
        """
        resp = yield from self.command('addid "{}"'.format(uri))
        # format : ['Id: 854']
        track_id = resp[0].split(':')[1].strip()
        return track_id

    @asyncio.coroutine
    def clear(self):
        """
        Clears the current play queue.

        :return: True
        """
        yield from self.command('clear')
        return True

    def delete_pos(self, pos):
        """
        Removes track(s) in the playlist.

        If start and end are both given and not None, removes all tracks
        between start and end (not included).
        If only start is given, the track at this position is removed.

        :param pos: index of the track to be removed.
        :return:
        """
        yield from self.command('delete {}'.format(pos))
        return True

    def delete_range(self, start, end=None):
        """
        Removes track(s) in the playlist.

        Removes all tracks between start and end (not included).

        :param start: start of the range of the tracks to be removed.
        :param end: optional,end of the range of the tracks to be removed. If
        end is not given, all tracks from start to the end of the playlist
        will be removed.
        :return:
        """
        track_range = _format_range(start, end)
        yield from self.command('delete {}'.format(track_range))
        return True

    def deleteid(self, track_id):
        """
        Deletes the song `track_id` from the play queue.

        :param track_id: the id of a song in the play queue
        """
        yield from self.command('deleteid {}'.format(track_id))
        return True

    # Controlling playback : pause, next, previous, stop,

    @asyncio.coroutine
    def pause(self, state):
        """
        Pause/resumes playing.
        As the automatic pausing (with no argument) is decrecated in mpd's
        protocole, the state argument is mandatory.
        Returns True or raise an `MpdCommandException`

        :param state: PAUSE_ON or PAUSE_OFF
        :return:
        """
        resp = yield from self.command('pause '+str(state))
        return True

    @asyncio.coroutine
    def next(self):
        """
        Plays next track in the playlist.
        If the end of the playlist is reached, stops playing.
        """
        resp = yield from self.command('next')
        return True

    @asyncio.coroutine
    def previous(self):
        """
        Plays previous track in the playlist.
        If the beginning of the playlist is reached, stay on the first track
        and keeps playing.
        """
        resp = yield from self.command('previous')
        return True

    @asyncio.coroutine
    def play(self, songpos=None):
        """
        Begins playing the playlist at song number `songpos`. If songpos is
        not given, starts playing at current position in the playlist.

        TODO: implement songpos !

        :param songpos: position in the playlist to start playing.
        An `MpdCommandException` will be raised if this index is invalid
        (out of range).
        """
        # TODO: implement songpos !
        if songpos is None:
            resp = yield from self.command('play')
        return True

    @asyncio.coroutine
    def stop(self):
        """
        Stops playback.
        """
        resp = yield from self.command('stop')
        return True

    @asyncio.coroutine
    def consume(self, consume_mode):
        """
        Sets consume mode to consume_mode, should be CONSUME_ON or CONSUME_OFF.
        When consume is activated, each song played is removed from playlist.

        :param consume_mode: consume mode.
        """
        resp = yield from self.command('consume {}'.format(consume_mode))
        return True

    @asyncio.coroutine
    def crossfade(self, seconds):
        """
        Sets crossfading between songs.

        :param seconds: length of the cross-fading
        """
        resp = yield from self.command('crossfade {}'.format(seconds))
        return True

    @asyncio.coroutine
    def random(self, random_mode):
        """
        Sets random mode to random_mode, should be RANDOM_ON or RANDOM_OFF.

        :param random_mode: random mode.
        """
        resp = yield from self.command('random {}'.format(random_mode))
        return True

    @asyncio.coroutine
    def _run(self):

        # first, wait for welcome message
        yield from self._welcome_msg()

        while not self.f_closed.done():

            yield from self._send_cmd(b'idle\n')

            f_resp = asyncio.async(self._read_response())
            f_cmd = asyncio.async(self._cmds.get())

            done, pending = yield from \
                asyncio.wait([f_resp, f_cmd, self.f_closed],
                             return_when=asyncio.FIRST_COMPLETED)

            if self.f_closed in done:
                # The socked has be been closed, cancel pending tasks
                f_cmd.cancel()
                f_resp.cancel()
                break

            if f_resp in done:
                # got a notification from our idle wait
                if self.cb_onchange is not None:
                    msg = f_resp.result()
                    self.cb_onchange(msg)

            if f_cmd in done:

                yield from self._send_cmd(b'noidle\n')
                yield from f_resp

                cmd = f_cmd.result()
                yield from self._send_cmd(cmd)
                response = yield from self._read_response()
                yield from self._responses.put(response)
            else:
                f_cmd.cancel()
        self.f_stopped.set_result(True)

    @asyncio.coroutine
    def _welcome_msg(self):
        while True:
            line = yield from self.reader.readline()
            print(line)
            if line.startswith(b'OK MPD'):
                self._protocol_version = line[7:-1]
                break

    @asyncio.coroutine
    def _send_cmd(self, cmd):
        self.writer.write(cmd)
        yield from self.writer.drain()

    @asyncio.coroutine
    def _read_response(self):

        message = []
        while not self.f_closed.done():
            line = yield from self.reader.readline()
            if line == b'':
                if self.reader.at_eof():
                    # When at eof, readline returns empty lines indefinitely.
                    break
            elif line.startswith(b'OK'):
                break
            elif line.startswith(b'ACK'):
                message.append(line[:-1].decode(encoding='UTF-8'))
                break
            else:
                message.append(line[:-1].decode(encoding='UTF-8'))

        return message

    @asyncio.coroutine
    def _get_response(self):
        """
        Get the response from the response queue and raise an Exception if
        mpd returned an error or failure.
        :return:
        """
        resp = yield from self._responses.get()
        if len(resp) == 1:
            line = resp[0]
            if line.startswith('ACK'):
                i = line.index('@')
                error = line[5:i]
                l = line[i+1:line.index(']')]
                command = line[line.index('{')+1:line.index('}')]
                msg = line[line.index('}')+1:]
                raise MpdCommandException(line, error, l, command, msg)
        return resp

    def client_connected(self, reader, writer):
        # Callback from StreamReaderProtocol
        self.reader = reader
        self.writer = writer
        # Start the task that handles incoming messages.
        self.worker = asyncio.async(self._run(), loop=self.loop)

        # FIXME : be careful, any exception in self.worker would be invisible
        # without this callback !
        self.worker.add_done_callback(self.on_worker)

    def on_worker(self, future):
        print('on worker {}'.format(future))

    def connection_lost(self, exc):
        # When the connection is closed, signal closing,will still need to
        # cancel the prnding task in _run for a clean stop.
        self.f_closed.set_result(True)
        pass


@asyncio.coroutine
def connect(host, port, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    transport, protocol = yield from loop.create_connection(
        lambda: MpdClientProtocol(), host, port)

    return protocol
