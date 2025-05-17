import hashlib
import bencodepy

class TorrentParserError(Exception):
    pass

def parse_torrent_file(path: str) -> dict:
    with open(path, 'rb') as f:
        data = f.read()
    
    try:
        metadata = bencodepy.decode(data)
    except Exception as e:
        raise TorrentParserError(f"Failed to decode torrent file: {e}")
        
    try:
        announce = metadata[b'announce'].decode('utf-8')
        info = metadata[b'info']
        name = info[b'name'].decode('utf-8')
        pieces = info[b'pieces']
        piece_length = info[b'piece length']
        length = info[b'length'] 
    except KeyError as e:
        raise TorrentParserError(f"Missing required key in torrent file: {e}")
    
    info_hash = hashlib.sha1(bencodepy.encode(info)).digest()

    return {
        'announce': announce,
        'info': info,
        'info_hash': info_hash,
        'name': name,
        'pieces': pieces,
        'piece_length': piece_length,
        'length': length,
        'files': None
    }