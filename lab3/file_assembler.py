import os

class FileAssembler:
    def __init__(self, name: str, piece_length: int, total_length: int, files: list = None):
        self.name = name
        self.piece_length = piece_length
        self.total_length = total_length
        with open(name, 'wb') as f:
            f.truncate(total_length)

    def write_piece(self, index: int, data: bytes):
        with open(self.name, 'r+b') as f:
            f.seek(index * self.piece_length)
            f.write(data)