import hashlib

class PieceManager:
    def __init__(self, pieces: bytes, piece_length: int, total_length: int):
        self.hashes = [pieces[i:i+20] for i in range(0, len(pieces), 20)]
        self.piece_length = piece_length
        self.total_length = total_length
        self.num_pieces = len(self.hashes)

    # проверка хеша
    def verify(self, index: int, data: bytes) -> bool:
        return hashlib.sha1(data).digest() == self.hashes[index]

    def get_piece_size(self, index: int) -> int:
        if index == self.num_pieces - 1:
            return self.total_length % self.piece_length or self.piece_length
        return self.piece_length