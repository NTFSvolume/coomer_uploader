import logging, __main__
from pathlib import Path
from datetime import datetime

# Get the current date and time
current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")

def setup_logger(log_to_file=False):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter("[%(levelname)-7s][%(name)-10s]: %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    if log_to_file:
        log_folder=Path(__main__.__file__).parent / "logs"
        log_folder.mkdir(exist_ok=True)
        project_name = Path(__main__.__file__).parent.name
        log_file= log_folder / f"{project_name}_{current_datetime}.log"
        log_file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)-7s][%(name)-10s]: %(message)s")
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(log_file_formatter)
        logger.addHandler(file_handler)
    
if __name__ == "__main__":
    setup_logger()
