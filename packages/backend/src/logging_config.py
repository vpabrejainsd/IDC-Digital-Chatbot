"""
Logging Configuration Module

Centralized logging configuration to suppress unnecessary warnings and clean up terminal output.
"""

import logging
import warnings
import os
from typing import Optional


def setup_clean_logging(log_level: str = "INFO", suppress_warnings: bool = True):
    """
    Configure clean logging for the IDC Chatbot system.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        suppress_warnings: Whether to suppress third-party warnings
    """
    
    # Set up basic logging configuration
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    if suppress_warnings:
        # Suppress specific warning categories
        suppress_third_party_warnings()
        
        # Suppress progress bars in non-interactive mode
        suppress_progress_bars()


def suppress_third_party_warnings():
    """Suppress common third-party library warnings that clutter the terminal."""
    
    # Suppress PIL/Pillow transparency warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="PIL")
    
    # Suppress HuggingFace tokenizer warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="transformers")
    warnings.filterwarnings("ignore", category=UserWarning, module="tokenizers")
    
    # Suppress sentence-transformers warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="sentence_transformers")
    
    # Suppress LangChain deprecation warnings for memory
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain")
    
    # Suppress TensorFlow/PyTorch info messages
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    
    # Suppress specific logger outputs
    logging.getLogger("PIL").setLevel(logging.ERROR)
    logging.getLogger("transformers").setLevel(logging.ERROR)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)


def suppress_progress_bars():
    """Suppress progress bars for cleaner output."""
    
    # Disable transformers progress bars
    os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = 'true'
    
    # Try to disable tqdm progress bars
    try:
        import tqdm
        tqdm.tqdm.disable = True
    except ImportError:
        pass
    
    # Set tokenizers parallelism warning off
    os.environ["TOKENIZERS_PARALLELISM"] = "false"


def create_custom_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Create a custom logger for specific modules.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create console handler with clean format
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


# Configure logging for OCR and PPTX processing
pptx_logger = create_custom_logger("pptx_processor", "WARNING")
ocr_logger = create_custom_logger("ocr_processor", "WARNING")
vlm_logger = create_custom_logger("vlm_processor", "INFO")


def log_processing_summary(file_name: str, total_images: int, successful_ocr: int, 
                         processing_method: str = "OCR"):
    """
    Log a clean processing summary instead of individual errors.
    
    Args:
        file_name: Name of processed file
        total_images: Total number of images found
        successful_ocr: Number of successful OCR extractions
        processing_method: Method used for processing
    """
    if successful_ocr > 0:
        success_rate = (successful_ocr / total_images * 100) if total_images > 0 else 0
        print(f"{file_name}: {successful_ocr}/{total_images} images processed "
              f"({success_rate:.1f}% success rate)")
    else:
        print(f"{file_name}: No processable images found ({total_images} total)")


def log_skipped_formats(file_name: str, skipped_count: int, format_types: list):
    """
    Log summary of skipped image formats instead of individual errors.
    
    Args:
        file_name: Name of processed file
        skipped_count: Number of skipped images
        format_types: List of skipped format types
    """
    if skipped_count > 0:
        unique_formats = list(set(format_types))
        formats_str = ", ".join(unique_formats)
        print(f"{file_name}: Skipped {skipped_count} unsupported images ({formats_str})")


# Initialize clean logging when module is imported
if __name__ != "__main__":
    setup_clean_logging()