import asyncio



def parse_status(messages):
    """
    Parse the status message into a dictionnary.
    :param messages:
    :return:
    """
    res = {k: v.strip() for k, v in (m.split(':', 1) for m in messages)}
    return res


def parse_lsinfo(message):
    dirs = []
    files = []
    playlists = []
    containers = {'directory': dirs,
                  'file': files,
                  'playlist': playlists}

    pairs = [(a, b.strip()) for a, b in (m.split(':', 1) for m in message)]
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

    return dirs, files, playlists



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

    @property
    def protocol_version(self):
        return self._protocol_version

    @asyncio.coroutine
    def command(self, cmd):
        """
        Send a command to mpd.

        :param cmd:
        :return:
        """
        yield from self._cmds.put(cmd)
        resp = yield from self._responses.get()
        return resp

    def status(self):
        resp = yield from self.command(b'status\n')
        return parse_status(resp)

    def lsinfo(self, path):
        resp = yield from self.command(b'lsinfo "' +
                                       path.encode(encoding='UTF-8') +
                                       b'"\n')
        return resp

    @asyncio.coroutine
    def _run(self):

        # first, wait for welcome message
        yield from self._welcome_msg()

        while True:
            print('wait for change')
            yield from self._send_cmd(b'idle\n')

            f_resp = asyncio.async(self._read_response())
            f_cmd = asyncio.async(self._cmds.get())

            done, pending = yield from asyncio.wait([f_resp, f_cmd],
                            return_when=asyncio.FIRST_COMPLETED)

            if f_resp in done:
                # got a notification from our idle wait
                if self.cb_onchange is not None:
                    msg = f_resp.result()
                    self.cb_onchange(msg)

            if f_cmd in done:
                print('noidle')
                yield from self._send_cmd(b'noidle\n')
                yield from f_resp # self._read_response()
                cmd = f_cmd.result()
                print('send cmd {}'.format(cmd))
                yield from self._send_cmd(cmd)
                response = yield from self._read_response()
                print('Response {}'.format(response))
                yield from self._responses.put(response)
            else:
                print('No command')
                f_cmd.cancel()

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
        while True:
            line = yield from self.reader.readline()
            if line.startswith(b'OK'):
                break
            elif line.startswith(b'ACK'):
                print('error ' + line)
                break
            else:
                message.append(line[:-1].decode(encoding='UTF-8'))
        return message

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
        print('LOST')
        pass


@asyncio.coroutine
def connect(host, port, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    transport, protocol = yield from loop.create_connection(
        lambda: MpdClientProtocol(), host, port)

    return protocol
