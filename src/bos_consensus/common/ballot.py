import copy
import enum
import json
import datetime

from ..consensus import get_fba_module
from ..util import get_uuid
from .message import Message


class BallotVotingResult(enum.Enum):
    agree = enum.auto()
    disagree = enum.auto()
    none = enum.auto()      # initialize when message is received by client


class Ballot:
    ballot_id = None
    node_name = None
    message = None
    state = None
    timestamp = None
    result = None

    def __init__(self, ballot_id, node_name, message, state, result=BallotVotingResult.none, timestamp=None):
        assert isinstance(message, Message)
        assert isinstance(state, enum.IntEnum)
        assert isinstance(result, BallotVotingResult)
        self.ballot_id = ballot_id
        self.node_name = node_name
        self.message = message
        self.state = state
        self.result = result

        if timestamp is None:
            self.timestamp = str(datetime.datetime.now())
        else:
            self.timestamp = timestamp

    def __repr__(self):
        return '<Ballot: ballot_id=%(ballot_id)s timestamp=%(timestamp)s node_name=%(node_name)s state=%(state)s message=%(message)s result=%(result)s>' % self.__dict__  # noqa

    def __eq__(self, rhs):
        if rhs is None:
            return False
        assert isinstance(rhs, Ballot)
        return self.ballot_id == rhs.ballot_id and self.state == rhs.state and self.message == rhs.message and self.result == rhs.result and self.timestamp == rhs.timestamp  # noqa

    def eq_id(self, rhs):
        if rhs is None:
            return False
        assert isinstance(rhs, Ballot)
        return self.ballot_id == rhs.ballot_id

    def has_different_ballot_id(self, rhs):
        if rhs is None:
            return False
        assert isinstance(rhs, self.__class__)
        return self.ballot_id != rhs.ballot_id and self.state == rhs.state and self.message == rhs.message and self.result == rhs.result  # noqa

    def __copy__(self):
        return self.__class__(
            self.ballot_id,
            self.node_name,
            copy.copy(self.message),
            self.state,
            self.result,
        )

    def serialize(self, to_string=False):
        o = dict(
            ballot_id=self.ballot_id,
            node_name=self.node_name,
            message=self.message.serialize(to_string=False),
            state=self.state.name,
            timestamp=self.timestamp,
            result=self.result.name,
        )

        if not to_string:
            return o

        return json.dumps(o)

    def _is_from_client(self):
        if self.result is BallotVotingResult.none:
            return True

    def is_validated(self):
        return True

    @classmethod
    def new(cls, node_name, message, state, result=BallotVotingResult.none, timestamp=None):
        assert isinstance(message, Message)

        return cls(
            get_uuid(),
            node_name,
            message,
            state,
            result,
            timestamp
        )

    @classmethod
    def from_dict(cls, o):
        state = get_fba_module('isaac').IsaacState
        ballot = cls(

            o['ballot_id'],
            o['node_name'],
            Message.from_dict(o['message']),
            state[o['state']],
            BallotVotingResult[o['result']],
            o['timestamp']
        )
        # ballot.timestamp = o['timestamp']

        return ballot

    @classmethod
    def from_string(cls, s):
        return cls.from_dict(json.loads(s))

    @property
    def message_id(self):
        return self.message.message_id
