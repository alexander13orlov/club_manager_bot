\"\"\"Poll service.\"\"\"

from core.models.poll import Poll
from datetime import datetime

class PollService:
    def __init__(self, history_repo):
        self.history_repo = history_repo

    def create_poll(self, chat_id, command, expires_at):
        poll = Poll(chat_id=chat_id, message_id=None, command=command, expires_at=expires_at)
        self.history_repo.add_poll(poll)
        return poll

    def add_vote(self, poll, user):
        if user not in poll.participants:
            poll.participants.append(user)
            self.history_repo.update_poll(poll)
