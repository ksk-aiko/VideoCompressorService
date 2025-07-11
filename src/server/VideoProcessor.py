import subprocess
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('VideoProcessor')

class VideoProcessor:
    def __init__(self, output_dir="processed"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def process(self, input_path: str, options: dict) -> str:
        operation = options.get("operation")
        output_path = os.path.join(self.output_dir, f"processed_{os.path.basename(input_path)}")

        if operation == "compress":
            return self._compress_video(input_path, output_path)
        
        else:
            logger.error(f"Unknown operation: {operation}")
            return None

    def _compress_video(self, input_path: str, output_path: str) -> str:
        logger.info(f"Compressing {input_path} to {output_path}...") 
        command = [
            'ffmpeg',
            '-i', input_path,
            '-vcodec', 'libx264',
            '-crf', '28',
            '-preset', 'fast',
            output_path
        ]

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info(f"FFMPEG output: {result.stdout}")
            logger.info(f"Video compressed successfully: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFMPEG failed to compress video.")
            logger.error(f"Command: {' '.join(command)}")
            logger.error(f"Stderr: {e.stderr}")
            return None
        except FileNotFoundError:
            logger.error("FFMPEG command not found. Please ensure FFMPEG is installed and in your PATH.")
            return None

