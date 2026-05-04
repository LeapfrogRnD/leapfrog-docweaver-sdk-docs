from services.leapx import leapx_service

task_mapper = {
    "classification": leapx_service.classify_document,
    "extraction": leapx_service.extract_from_document,
    "summarization": leapx_service.generate_summary,
}
