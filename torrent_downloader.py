import libtorrent

import downloader

class TorrentDownloader(downloader.Downloader):
    def __init__(self, torrent_src_path, save_path, port):
        if torrent_src_path.startswith("magnet:"):
            raise ValueError("torrent downloader can not get magent links")
        
        super().__init__(torrent_src_path, save_path, port)

    def initiate_torrent_params(self, torrent_src_path):
        return libtorrent.torrent_info(torrent_src_path)

