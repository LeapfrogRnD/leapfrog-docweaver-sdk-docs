def get_stage_log_message(stage_name: str, status: str) -> str:
    """Generate a standardized log message for stage status.

    Args:
        stage_name: Name of the stage (e.g., "extraction", "ocr")
        status: Status of the stage (e.g., "completed", "started", "failed")

    Returns:
        Formatted log message string
    """
    return f"{stage_name.capitalize()} {status}"
