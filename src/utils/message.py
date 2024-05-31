from utils.person import Participant

class BaseMessage:
    def __init__(
        self,
        message_content: str,
        depth: int = 0,
    ) -> None:
        self.message_content = message_content
        self.depth = depth

class Message(BaseMessage):
    def __init__(
        self, 
        message_content: str, 
        sender: Participant,
        receivers: set[Participant] = set(),
        depth: int = 0
    ) -> None:
        super().__init__(message_content, depth)
        self.sender = sender
        self.receivers = receivers

class UpcomingMessage(BaseMessage):
    def __init__(
        self,
        message_content: str,
        receiver: Participant,
        depth: int,
        hold: bool = False,
    ) -> None:
        super().__init__(message_content, depth)
        self.receiver = receiver
        self.hold = hold