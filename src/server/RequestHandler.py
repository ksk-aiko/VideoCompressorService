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
from typing import Optional
from .TCPSocketServer import Connection
from .FileReceiver import FileReceiver
from .StorageChecker import StorageChecker
from .StatusResponder import StatusResponder
from .VideoProcessor import VideoProcessor

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
                self.status_responder.send_status(conn, "ERROR")
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
                self.status_responder.send_status(conn, "FULL")
                return False
            
            filename = f"{uuid.uuid4()}.{media_type}"
            saved_path = self.file_receiver.save_payload(filename, payload)

            if saved_path:
                logger.info(f"Handing off {saved_path} to VidoeProcessor with options: {options}")
                processed_path = self.video_processor.process(saved_path, options)
                
                if processed_path:
                    self.status_responder.send_status(conn, "SUCESS")
                    logger.info(f"Successfully processed file: {processed_path}")
                    return True
            else:
                self.status_responder.send_status(conn, "ERROR")
                logger.error(f"Failed to save file from {conn.address}")
                return False
        
        except (json.JSONDecodeError, struct.error) as e:
            logger.error(f"Protocol error handling connection: {e}")
            self.status_responder.send_status(conn, "ERROR")
            return False

        except Exception as e:
            logger.error(f"Error handling connection: {e}")
            try:
                self.status_responder.send_status(conn, "ERROR")
            except:
                logger.error("Failed to send error status")
            return False
        finally:
            conn.close()