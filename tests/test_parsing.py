import unittest
import ampdclient.client as c


# Test for parsing functions


class TestStatusParsing(unittest.TestCase):

    def test_parse_status(self):

        msg = ['1:a', '2: b', '3: c ']
        res = c.parse_lines_to_dict(msg)

        self.assertIn('1', res)
        self.assertIn('2', res)
        self.assertIn('3', res)

        self.assertEqual('a', res['1'])
        self.assertEqual('b', res['2'])
        self.assertEqual('c', res['3'])

    def test_parse_status2(self):

        msg = ['1:a:b:c']
        res = c.parse_lines_to_dict(msg)

        self.assertIn('1', res)

        self.assertEqual('a:b:c', res['1'])


class TestLsInfoParsing(unittest.TestCase):

    def test_parse_root_dir(self):

        resp = ['directory: nas-samba/A Classer',
                'Last-Modified: 2015-06-11T16:25:16Z',
                'directory: nas-samba/Albums',
                'Last-Modified: 2015-06-17T10:46:05Z',
                'directory: nas-samba/Compilations',
                'Last-Modified: 2015-06-03T18:56:30Z',
                'directory: nas-samba/Enfants',
                'Last-Modified: 2014-12-28T20:38:30Z',
                'directory: nas-samba/Import',
                'Last-Modified: 2015-05-30T07:19:11Z',
                'directory: nas-samba/Non-Album',
                'Last-Modified: 2014-07-25T23:55:13Z',
                'directory: nas-samba/Playlists',
                'Last-Modified: 2015-09-02T20:23:14Z',
                'directory: nas-samba/Soundtracks',
                'Last-Modified: 2014-11-28T19:24:58Z',
                'directory: nas-samba/testpl',
                'Last-Modified: 2015-09-07T20:06:24Z'
                ]
        dirs, files, playlists = c.parse_lsinfo(resp)

        self.assertEqual(0, len(playlists))
        self.assertEqual(0, len(files))

        dir2 = dirs[2]
        self.assertEqual(dir2[0], 'nas-samba/Compilations')
        attrs = dir2[1]
        self.assertEqual(attrs['Last-Modified'], '2015-06-03T18:56:30Z')

        self.assertEqual(9, len(dirs))

    def test_parse_empty_dir(self):

        resp = []
        dirs, files, playlists = c.parse_lsinfo(resp)

        self.assertEqual(0, len(playlists))
        self.assertEqual(0, len(files))
        self.assertEqual(0, len(dirs))

    def test_parse_playlist_dir(self):

        resp = ['playlist: nas-samba/testpl/FranceInter.m3u\n',
                'Last-Modified: 2015-09-02T16:32:30Z\n',
                'playlist: nas-samba/testpl/RadioFranceInter.pls\n',
                'Last-Modified: 2015-09-02T16:34:26Z\n',
                'playlist: nas-samba/testpl/TestVlc.xspf\n',
                'Last-Modified: 2015-09-02T20:24:14Z\n',
                'playlist: nas-samba/testpl/FranceInterPl.xspf\n',
                'Last-Modified: 2015-09-02T20:28:33Z\n'
                ]

        dirs, files, playlists = c.parse_lsinfo(resp)

        self.assertEqual(4, len(playlists))
        self.assertEqual(0, len(files))
        self.assertEqual(0, len(dirs))

    def test_parse_album_dir(self):

        resp = ['file: nas-samba/Albums/Alternative Rock/Arcade Fire/2004 -'
                ' Funeral/01-Neighborhood #1 (Tunnels).mp3',
                'Last-Modified: 2014-12-28T23:19:15Z',
                'Time: 288',
                'Artist: Arcade Fire',
                'AlbumArtist: Arcade Fire',
                'ArtistSort: Arcade Fire',
                'AlbumArtistSort: Arcade Fire',
                'AlbumArtistSort: Arcade Fire',
                'AlbumArtistSort: Arcade Fire',
                'AlbumArtistSort: Arcade Fire',
                'AlbumArtistSort: Arcade Fire',
                'AlbumArtistSort: Arcade Fire',
                'AlbumArtistSort: Arcade Fire',
                'AlbumArtistSort: Arcade Fire',
                'Title: Neighborhood #1 (Tunnels)',
                'Album: Funeral',
                'Track: 1/10',
                'Date: 2005-02-28',
                'Genre: Alternative Rock',
                'Disc: 1/1',
                'AlbumArtistSort: Arcade Fire',
                'MUSICBRAINZ_ALBUMARTISTID: 52074ba6-e495-4ef3-'
                '9bb4-0703888a9f68',
                'MUSICBRAINZ_ALBUMID: 0bce5b2f-adbe-35fb-8065-43f531427737',
                'MUSICBRAINZ_ARTISTID: 52074ba6-e495-4ef3-9bb4-0703888a9f68',
                'MUSICBRAINZ_TRACKID: e6d80ec5-85b3-4900-8e52-f83e9bf16852',

                'file: nas-samba/Albums/Alternative Rock/Arcade Fire/2004 - '
                'Funeral/02-Neighborhood #2 (Laïka).mp3',
                'Last-Modified: 2014-12-28T23:19:15Z',
                'Time: 212',
                'Artist: Arcade Fire',
                'AlbumArtist: Arcade Fire',
                'ArtistSort: Arcade Fire',
                'AlbumArtistSort: Arcade Fire',
                'AlbumArtistSort: Arcade Fire',
                'AlbumArtistSort: Arcade Fire',
                'AlbumArtistSort: Arcade Fire',
                'AlbumArtistSort: Arcade Fire',
                'AlbumArtistSort: Arcade Fire',
                'AlbumArtistSort: Arcade Fire',
                'AlbumArtistSort: Arcade Fire',
                'Title: Neighborhood #2 (Laïka)',
                'Album: Funeral',
                'Track: 2/10',
                'Date: 2005-02-28',
                'Genre: Alternative Rock',
                'Disc: 1/1',
                'AlbumArtistSort: Arcade Fire',
                'MUSICBRAINZ_ALBUMARTISTID: 52074ba6-e495-4ef3-'
                '9bb4-0703888a9f68',
                'MUSICBRAINZ_ALBUMID: 0bce5b2f-adbe-35fb-8065-43f531427737',
                'MUSICBRAINZ_ARTISTID: 52074ba6-e495-4ef3-9bb4-0703888a9f68',
                'MUSICBRAINZ_TRACKID: c05048f1-47f6-4532-8d98-75ca80fa1792',
                ]

        dirs, files, playlists = c.parse_lsinfo(resp)

        self.assertEqual(0, len(playlists))
        self.assertEqual(2, len(files))
        self.assertEqual(0, len(dirs))

        f1 = files[0][1]
        self.assertEqual('nas-samba/Albums/Alternative Rock/Arcade Fire/2004 -'
                ' Funeral/01-Neighborhood #1 (Tunnels).mp3', files[0][0])
        self.assertEqual('Arcade Fire', f1['AlbumArtist'])
        self.assertEqual('Funeral', f1['Album'])
        self.assertEqual('Neighborhood #1 (Tunnels)', f1['Title'])

class TestPlaylistParsing(unittest.TestCase):

    def test_parsepl(self):

        lines = ['file: http://audio.scdn.arkena.com/11008/franceinter'
                 '-midfi128.mp3',
                 'Name: France Inter',
                 'Time: 0',
                 'Pos: 0',
                 'Id: 1019',

                 'file: http://www.rdl.de:8000/rdl',
                 'Title: Radio Dreyeckland Livestream',
                 'Pos: 1',
                 'Id: 1020',

                 'file: http://audio.scdn.arkena.com/11008/franceinter'
                 '-midfi128.mp3',
                 'Title: France Inter 128b',
                 'Pos: 2',
                 'Id: 1024',

                 'file: testpl/Sunday Bloody Sunday.mp3',
                 'Last-Modified: 2015-10-26T20:47:22Z',
                 'Artist: U2',
                 'AlbumArtist: Compil Classic Rock',
                 'ArtistSort: U2',
                 'Title: Sunday Bloody Sunday',
                 'Album: Compil Classic Rock',
                 'Track: 5/0',
                 'Date: 0000',
                 'Genre: Non-Album',
                 'Disc: 0/0',
                 'MUSICBRAINZ_ARTISTID: a3cb23fc-acd3-4ce0-8f36-1e5aa6a18432',
                 'MUSICBRAINZ_TRACKID: f9fd2d50-c830-4a8a-9a2c-6ae86dbe0d2d',
                 'Time: 279',
                 'Pos: 3',
                 'Id: 1025',

                 'file: testpl/Dalida/Bambino.mp3',
                 'Last-Modified: 2015-10-27T06:48:02Z',
                 'Artist: Dalida',
                 'AlbumArtist: Dalida',
                 'ArtistSort: Dalida',
                 'AlbumArtistSort: Dalida',
                 'Title: Bambino',
                 'Album: Best-of 1956-1965',
                 'Track: 1/23',
                 'Date: 0000',
                 'Genre: Non-Album',
                 'Composer: Nisa',
                 'Disc: 0/0',
                 'AlbumArtistSort: Dalida',
                 'MUSICBRAINZ_ARTISTID: 1598ccda-b164-4bff-9821-f9ff5a8587a8',
                 'MUSICBRAINZ_TRACKID: b4d566aa-46e0-4cbf-95ae-d1bde2c1f076',
                 'Time: 211',
                 'Pos: 4',
                 'Id: 1026'
                 ]

        tracks = c.parse_playlist(lines)

        self.assertEqual(5, len(tracks))
        self.assertEqual('France Inter', tracks[0][1]['Name'])