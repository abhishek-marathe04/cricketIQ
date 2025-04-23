import logging

def get_logger():
    # Create a logger
    logger = logging.getLogger("my_app_logger")
    
    if not logger.hasHandlers():
        # Set up logging
        # logging.basicConfig(level=logging.DEBUG)  # You can set this to INFO if you want less verbosity
        logging.getLogger("urllib3").setLevel(logging.DEBUG)
        # Set the default logging level
        logger.setLevel(logging.DEBUG)

        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Create a stream handler to log to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(console_handler)

    return logger