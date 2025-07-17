"""
RequestHandler class for handling client connections to the video compression service.
This class manages the protocol for file upload requests, validates storage capacity,
receives file data, and communicates status responses back to clients.
The handler implements a simple protocol where:
1. Client sends a 4-byte length of the filename
2. Client sends the filename as UTF-8 encoded string
3. Client sends an 8-byte file size
4. Client sends the file data if space is available
5. Server responds with status code
Attributes:
    file_receiver (FileReceiver): Component that handles receiving and storing files
    storage_checker (StorageChecker): Component that checks if there's enough storage space
    status_responder (StatusResponder): Component that sends status responses to clients
"""

import logging
import struct
import json
import uuid
import os
from typing import Optional
from .TCPSocketServer import Connection
from .FileReceiver import FileReceiver
from .StorageChecker import StorageChecker
from .StatusResponder import StatusResponder
from .VideoProcessor import VideoProcessor

ERROR_PROTOCOL = 1001
ERROR_STORAGE_FULL = 1002
ERROR_RECEIVING = 1003
ERROR_SAVING = 1004
ERROR_PROCESSING = 1005
ERROR_UNEXPECTED = 5000

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('RequestHandler')

class RequestHandler:
    
    def __init__(self, file_receiver: FileReceiver, storage_checker: StorageChecker, status_responder: StatusResponder, video_processor: VideoProcessor):
        self.file_receiver = file_receiver
        self.storage_checker = storage_checker
        self.status_responder = status_responder
        self.video_processor = video_processor

    def handle_connection(self, conn: Connection) -> bool:
        try:
            logger.info(f"Handling connection from {conn.address}")

            # read header data
            header_data = conn.recv(8)
            if not header_data or len(header_data) != 8:
                logger.error("Failed to receive header data")
                self._send_error_response(conn, ERROR_PROTOCOL,  "Header reception failed",  "Ensure the client sends an 8-byte header and try again")
                return False
            
            json_size, media_type_size = struct.unpack('!HB', header_data[:3])
            payload_size = int.from_bytes(header_data[3:], 'big')

            # read JSON data
            json_data = conn.receive(json_size)
            if not json_data or len(json_data) != json_size:
                logger.error("Failed to receive JSON data")
                self.status_responder.send_status(conn, "ERROR")
                return False
            options = json.loads(json_data.decode('utf-8'))

            # read media type
            media_type_data = conn.receive(media_type_size)
            if not media_type_data or len(media_type_data) != media_type_size:
                logger.error("Failed to receive media type data")
                self.status_responder.send_status(conn, "ERROR")
                return False
            media_type = media_type_data.decode('utf-8')

            

            logger.info(f"Request from {conn.address}: options={options}, media_type={media_type}, payload_size={payload_size}bytes")

            if not self.storage_checker.has_capacity(payload_size):
                logger.warning(f"Not enough storage capacity for file from {conn.address}")
                self._send_error_response(conn, ERROR_STORAGE_FULL, "Insufficient storage", "Server is at capacity. Please try again later.")
                return False
            
            filename = f"{uuid.uuid4()}.{media_type}"
            saved_path = self.file_receiver.save_payload(filename, payload)

            if saved_path:
                logger.info(f"Handing off {saved_path} to VidoeProcessor with options: {options}")
                processed_path = self.video_processor.process(saved_path, options)
                
                if processed_path:
                    logger.info(f"Successfully processed file: {processed_path}")
                    self._senf_file_response(conn, processed_path)
                    return True
                else:
                    logger.error(f"Video processing failed for {saved_path}")
                    self._send_error_reponse(conn, ERROR_PROCESSING, "Videoprocessing failed", "The video file may be corrupted or in an unsupported format.")
            else:
                logger.error(f"Failed to save file from {conn.address}")
                self._send_error_response(conn, ERROR_SAVING, "File saving failed", "Ensure the server has write permissions and sufficient space.")
                return False
        
        except (json.JSONDecodeError, struct.error) as e:
            logger.error(f"Protocol error handling connection: {e}")
            self._send_error_reponse(conn, ERROR_PROTOCOL, "Protocol error", "Ensure the client follows the correct protocol for sending requests.")
            return False

        except Exception as e:
            logger.error(f"Unexpected error handling connection: {e}")
            self._send_error_response(conn, ERROR_UNEXPECTED, "Unexpected error", "An unexpected error occurred while processing the request.Please report this issue to the server administrator.")
            return False
        finally:
            conn.close()
            logger.info(f"Connection closed for {conn.address}")
        
    def _senf_file_response(self, conn: Connection, file_path: str):
        try:
            with open(file_path, 'rb') as f:
                payload = f.read()

            payload_size = len(payload)
            media_type = os.path.splitext(file_path)[1].lstrip('.').encode('utf-8')
            media_type_size = len(media_type)

            json_data = b'{}'
            json_size = len(json_data)

            header = struct.pack('!H', json_size) + struct.pack('!B', media_type_size) + payload_size.to_bytes(5, 'big')

            conn.send(header)
            conn.send(json_data)
            conn.send(media_type)
            conn.send(payload)
            logger.info(f"Sent processed file {file_path} to client.")

        except FileNotFoundError:
            logger.error(f"Could not find processed file to senf: {file_path}")
            self.status_responder.send_status(conn, "ERROR")
        except Exception as e:
            logger.error(f"Failed to send file response: {e}")
    
    def _send_error_reponse(self, conn: Connection, code: int, description: str, solution: str):
        error_json = {
            "error": {
                "code": code,
                "description": description,
                "solution": solution
            }
        }
        json_data = json.dumps(error_json).encode('utf-8')
        json_size = len(json_data)

        header = struct.pack('!H', json_size) + struct.pack('!B', 0) + (0).to_bytes(5, 'big')

        try:
            conn.send(header)
            conn.send(json_data)
            logger.info(f"Sent error response to {conn.address}: {error_json}")
        except Exception as e:
            logger.error(f"Failed to send error response to client: {e}")