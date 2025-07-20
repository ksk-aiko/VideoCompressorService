import logging
from server.TCPSocketServer import TCPSocketServer
from server.RequestHandler import RequestHandler
from server.FileReceiver import FileReceiver
from server.DiskWriter import DiskWriter
from server.StorageChecker import StorageChecker
from server.VideoProcessor import VideoProcessor
from server.ConnectionManager import ConnectionManager
from server.StatusResponder import StatusResponder

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

HOST = "0.0.0.0"
PORT = 5000
STORAGE_PATH = "uploads"
PROCESSED_PATH = "processed"
MAX_STORAGE_SIZE = 10

def main():
    logger = logging.getLogger('Main')
    logger.info("initializing Video Compressor Service...")

    disk_writer = DiskWriter(STORAGE_PATH)
    file_receiver = FileReceiver(disk_writer)
    storage_checker = StorageChecker(STORAGE_PATH, MAX_STORAGE_SIZE)
    video_processor = VideoProcessor(PROCESSED_PATH)
    connection_manager = ConnectionManager()
    status_responder = StatusResponder()

    def create_request_handler(connection):
        return RequestHander(
            connection=connection,
            file_receiver=file_receiver,
            storage_checker=storage_checker,
            video_processor=video_processor,
            status_responder=status_responder
        )
    
    server = TCPSocketServer(
        host=HOST,
        port=PORT,
        handler_factory=create_request_handler,
        connection_manager=connection_manager
    )

    logger.info(f"Server initializtion complete.Starting now.")
    server.start()

if __name__ == "__main__":
    main()