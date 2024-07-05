import libtorrent

LISTEN_INTERFACE = "0.0.0.0"


class Downloader:
    '''
    as long as this object is alive the download would continue
    '''

    def __init__(self, torrent_src_path, save_path, port):

        self._session = libtorrent.session(
            {'listen_interfaces': f'{LISTEN_INTERFACE}:{port}'}
            )

        torrent_params = self.initiate_torrent_params(torrent_src_path)
        torrent_params.save_path = save_path

        self._session.add_torrent(torrent_params)
        
        #TODO: there might be more then one torrent per session
        self._torrent = self._session.get_torrents()[0]

    def initiate_torrent_params(self, torrent_src_path):
        raise NotImplementedError("this is an abstruct class")

    def get_status(self):
        return self._torrent.status()

    def is_seeding(self):
        return self.get_status().is_seeding
    
    def get_name(self):
        return self.get_status().name
    
    def __repr__(self):
        current_status = self.get_status()
        return f"{current_status.name}: {current_status.progress * 100:.2f}% complete (down: {current_status.download_rate / 1000:.1f} kB/s up: {current_status.upload_rate / 1000:.1f} kB/s peers: {current_status.num_peers})"
