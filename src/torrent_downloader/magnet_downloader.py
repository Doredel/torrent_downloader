import libtorrent

import downloader


class MagnetDownloader(downloader.Downloader):
    def __init__(self, torrent_src_path, save_path, port):
        if not torrent_src_path.startswith("magnet:"):
            raise ValueError("magent downloader can get only magent links")

        super().__init__(torrent_src_path, save_path, port)

    def initiate_torrent_params(self, torrent_src_path):
        return libtorrent.parse_magnet_uri(torrent_src_path)
