class Validator:
    @staticmethod
    def is_mp4(filename: str) -> bool:
        return filename.lower().endswith('.mp4')