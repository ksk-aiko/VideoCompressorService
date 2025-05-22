import os

class Validator:
    @staticmethod
    def is_mp4(filename: str) -> bool:
        return filename.lower().endswith('.mp4')
    
    @staticmethod
    def check_file_size(file_path: str, max_size_mb: int = 100) -> bool:
        file_size_bytes = os.path.getsize(file_path)
        max_size_bytes = max_size_mb * 1024 * 1024 # Convert MB to bytes
        return file_size_bytes <= max_size_bytes
