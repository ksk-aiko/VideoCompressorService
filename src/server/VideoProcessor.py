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
        elif operation == "resize":
            width = options.get("width")
            height = options.get("height")
            return self._resize_video(input_path, output_path, width, height)
        elif operation == "change_aspect_ratio":
            aspect_ratio = options.get("aspect_ratio")
            return self._change_aspect_ratio(input_path, output_path, aspect_ratio)
        elif operation == "convert_to_audio":
            audio_output_path = os.path.splitext(output_path)[0] + '.mp3'
            return self._convert_to_audio(input_path, audio_output_path)
        elif operation == "create_clip":
            start_time = options.get("start_time")
            end_time = options.get("end_time")
            output_format = options.get("format", "gif")
            return self._create_clip(input_path, start_time, end_time, output_format)
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
    
    def _resize_video(self, input_path: str, output_path: str, width: int, height: int) -> str:
        if not width or not height:
            logger.error("Resize operation requires 'width' and 'height' options.")
            return None
        logger.info(f"Resizing {input_path} to {width}:{height}...")
        command = [
            'ffmpg',
            '-i', input_path,
            '-vf', f'scale={width}:{height}',
            output_path
        ]

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info(f"FFMPEG output: {result.stdout}")
            logger.info(f"Video resized successfully: {output_path}")
            return output_path
        except subprocess.CalledProccessError as e:
            logger.error(f"FFMPEG failed to resize video.")
            logger.error(f"Command: {' '.join(command)}")
            logger.error(f"Stderr: {e.stderr}")
            return None
        except FileNotFoundError:
            logger.error("FFMPEG command not found.Please ensure FFMPEG is installed in your system's PATH.")
    
    def _change_aspect_ratio(self, input_path: str, output_path: str, aspect_ratio: str) -> str:
        if not aspect_ratio:
            logger.error("Change aspect ratio operation requires 'aspect_ration' option.")
            return None
        
        logger.info(f"Changing aspect ratio of {input_path} to {aspect_ratio}...")
        command = [
            'ffmpeg',
            '-i', input_path,
            '-aspect', aspect_ratio,
            output_path
        ]

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info(f"FFMPEG output: {result.stdout}")
            logger.info(f"Aspect ratio changed successfully: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFMPEG failed to change aspect ratio.")
            logger.error(f"Command: {' '.join(command)}")
            logger.error(f"Stderr: {e.stderr}")
            return None
        except FileNotFoundError:
            logger.error("FFMPEG command not found. Please ensure FFMPEG is installed and in your PATH.")
            return None
    
    def _convert_to_audio(self, input_path: str, output_path: str) -> str:
        logger.info(f"Converting {input_path} to audio {output_path}...")
        command = [
            'ffmpeg',
            '-i', input_path,
            '-vn', # Disable video recording
            '-acodec', 'libmp3lame', # Use the LAME MP# audio encoder
            '-q:a', '2', # Set audio quality
            output_path
        ]

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info(f"FFMPEG output: {result.stdout}")
            logger.info(f"Audio converted successfully: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFMPEG failed to convert video to audio.")
            logger.error(f"Command: {' '.join(command)}")
            logger.error(f"Stderr: {e.stderr}")
            return None
        except FileNotFoundError:
            logger.error("FFMPEG command not found. Please ensure FFMPEG is installed and in your PATH.")
            return None
    
    def _create_clip(self, input_path: str, start_time: str, end_time: str, output_format: str) -> str:
        if not all[start_time, end_time, output_format]:
            logger.error("Create clip operation requires 'start_time', 'end_time', and 'format' options.")
            return None
        
        if output_format not in ['gif', 'webm']:
            logger.error(f"Unsupported output format: {output_format}. Supported formats are 'gif' and 'webm'.")
            return None
        
        base_name = os.path.basename(input_path)
        output_filename = f"clip_{os.path.splitext(base_name)[0]}.{output_format}"
        output_path = os.path.join(self.output_dir, output_filename)

        logger.info(f"Creating clip from {input_path} from {start_time} to {end_time} in {output_format} format...")

        command = [
            'ffmpeg',
            '-i', input_path,
            '-ss', start_time,
            '-to', end_time,
            '-c:v', 'copy',
            '-c:a', 'copy',
            output_path
        ]

        if output_format == 'gif':
            palette_path = os.path.join(self.output_dir, "palette.png")
            palette_command = [
                'ffmpeg',
                '-y',
                '-i', input_path,
                '-ss', start_time,
                '-to', end_time,
                '-vf', 'fps=10,scale=320:-1:flags=lanczos,palettegen',
                palette_path
            ]

            command = [
                'ffmpeg',
                '-y',
                '-i', input_path,
                '-i', palette_path,
                '-ss', start_time,
                '-to', end_time,
                'vf', 'fps=10, scale=320:-1:flags=lanczos[x];[x][1:v]paletteuse',
                output_path
            ]

            try:
                subprocess.rn(palette_command, check=True, capture_output=True, text=True)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                logger.error(f"FFMPEG failed to generate palette for GIF: {getattr(e, 'stderr', e)}")
                return None
            
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info(f"Clip created successfully: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFMPEG failed to create clip.")
            logger.error(f"Command: {' '.join(command)}")
            logger.error(f"Stderr: {e.stderr}")
            return None
        except FileNotFoundError:
            logger.error("FFMPEG command not found. Please ensure FFMPEG is installed and in your PATH.")
            return None





