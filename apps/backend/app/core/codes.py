from enum import Enum


class SuccessCode(Enum):
    OK = (200, "요청에 성공했습니다.")
    CREATED = (201, "리소스가 생성되었습니다.")

    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message


class ErrorCode(Enum):
    # =================== COMMON ===================
    INVALID_NULL_DATA = (400, "COM_400_001", "빈 값은 허용되지 않습니다.")
    INVALID_MAPPING_PARAMETER = (400, "COM_400_002", "매핑할 수 없는 값입니다.")
    RESOURCE_NOT_FOUND = (404, "COM_404_001", "존재하지 않는 리소스입니다.")
    INTERNAL_SERVER_ERROR = (500, "COM_500_001", "서버 내부 오류가 발생했습니다.")

    # =================== DOCUMENT ===================
    INVALID_FILE_TYPE = (400, "DOC_400_001", "PDF 파일만 업로드할 수 있습니다.")
    INVALID_METADATA = (400, "DOC_400_002", "metadata는 JSON 객체 문자열이어야 합니다.")
    INVALID_SOURCE_TYPE = (400, "DOC_400_003", "지원하지 않는 source_type입니다.")
    EMPTY_TEXT = (400, "DOC_400_004", "text는 비어 있을 수 없습니다.")
    EMPTY_PDF = (400, "DOC_400_005", "PDF 파일이 비어 있습니다.")
    INVALID_PDF = (400, "DOC_400_006", "읽을 수 없는 PDF 파일입니다.")
    ENCRYPTED_PDF = (400, "DOC_400_007", "암호화된 PDF는 지원하지 않습니다.")
    PDF_TEXT_EXTRACTION_FAILED = (400, "DOC_400_008", "PDF 텍스트 추출에 실패했습니다.")
    EMPTY_PDF_TEXT = (400, "DOC_400_009", "PDF에서 추출할 수 있는 텍스트가 없습니다.")
    MISSING_RAW_TEXT = (400, "DOC_400_010", "문서에 원문 텍스트가 없습니다.")
    DOCUMENT_NOT_FOUND = (404, "DOC_404_001", "존재하지 않는 문서입니다.")
    DOCUMENT_PROCESSING_FAILED = (500, "DOC_500_001", "문서 처리에 실패했습니다.")

    # =================== EXPERIENCE ===================
    EXPERIENCE_NOT_FOUND = (404, "EXP_404_001", "존재하지 않는 경험입니다.")

    # =================== QUESTION ===================
    QUESTION_NOT_FOUND = (404, "QST_404_001", "존재하지 않는 질문입니다.")

    # =================== MATCH ===================
    MATCH_NOT_FOUND = (404, "MAT_404_001", "존재하지 않는 매칭 요청입니다.")

    # =================== SELECTION ===================
    SELECTED_NOT_EXPOSED = (400, "SEL_400_001", "선택된 block_id는 노출된 후보 중 하나여야 합니다.")

    # =================== RESUME ===================
    RESUME_NOT_FOUND = (404, "RSM_404_001", "존재하지 않는 이력서입니다.")

    # =================== NOTION ===================
    MISSING_NOTION_TOKEN = (400, "NTN_400_001", "notion_token 또는 NOTION_API_TOKEN이 필요합니다.")
    NOTION_API_ERROR = (502, "NTN_502_001", "Notion API 요청에 실패했습니다.")
    NOTION_API_UNAVAILABLE = (502, "NTN_502_002", "Notion API에 연결할 수 없습니다.")

    def __init__(self, status: int, code: str, message: str):
        self.status = status
        self.code = code
        self.message = message
