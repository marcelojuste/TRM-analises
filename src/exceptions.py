class AuditAppError(Exception):
    def __init__(self, message: str = "Ocorreu um erro na aplicação de auditoria."):
        self.message = message
        super().__init__(self.message)

class InterruptedException(AuditAppError):
    def __init__(self, message: str = "Operação cancelada pelo usuário."):
        super().__init__(message)

class NoXmlsFoundException(AuditAppError):
    def __init__(self, message: str = "Não foi possível encontrar arquivos XML nos diretórios selecionados."):
        super().__init__(message)

class NoSpedRecordsFoundException(AuditAppError):
    def __init__(self, message: str = "Não foi possível encontrar registros SPED válidos nos arquivos selecionados."):
        super().__init__(message)

class ExportError(AuditAppError):
    pass

class DatabaseSchemaError(AuditAppError):
    pass