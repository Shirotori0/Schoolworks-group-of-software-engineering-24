class AppException(Exception):
    def __init__(self, status_code: int, detail: str, code: int = None):
        self.status_code = status_code
        self.detail = detail
        self.code = code if code else status_code