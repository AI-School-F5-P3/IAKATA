class ChatError(Exception):
    """Base exception for chat module"""
    pass

class SessionNotFoundError(ChatError):
    """Raised when a chat session is not found"""
    pass

class SessionExpiredError(ChatError):
    """Raised when attempting to use an expired session"""
    pass

class MessageProcessingError(ChatError):
    """Raised when there's an error processing a message"""
    pass

class ContextBuildError(ChatError):
    """Raised when there's an error building the conversation context"""
    pass