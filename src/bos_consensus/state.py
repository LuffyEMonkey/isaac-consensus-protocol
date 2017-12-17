import logging

from .ballot import Ballot
from .statekind import StateKind


log = logging.getLogger(__name__)


class State:
    def __init__(self, node, kind=StateKind.NONE):
        self.node = node
        self.kind = kind

    def handle_ballot(self, ballot):
        assert isinstance(ballot, Ballot)
        self.handle_ballot_impl(ballot)

    def init_node(self):
        raise NotImplementedError()

    def handle_ballot_impl(self, ballot):
        raise NotImplementedError()

    def __eq__(self, state):
        assert isinstance(state, State)
        return self.kind == state.kind

    def __str__(self):
        return self.kind.name


class NoneState(State):
    def __init__(self, node):
        super(NoneState, self).__init__(node, StateKind.NONE)

    def init_node(self):
        self.node.set_state_init()

    def handle_ballot_impl(self, ballot):
        pass


class InitState(State):
    def __init__(self, node):
        super(InitState, self).__init__(node, StateKind.INIT)

    def init_node(self):
        pass

    def handle_ballot_impl(self, ballot):
        self.node.broadcast(ballot.message)
        self.node.store(ballot)
        if ballot.node_state_kind == self.kind:
            ballots = self.node.validator_ballots
            validator_th = self.node.minimum_number_of_agreement

            for node_id, node_ballot in ballots.items():
                if node_ballot.node_state_kind == self.kind and ballot.message == node_ballot.message:
                    validator_th -= 1

            if validator_th == 0:
                self.node.set_state_sign()
                self.node.broadcast(ballot.message)


class SignState(State):
    def __init__(self, node):
        super(SignState, self).__init__(node, StateKind.SIGN)

    def init_node(self):
        pass

    def handle_ballot_impl(self, ballot):
        self.node.store(ballot)
        if ballot.node_state_kind == self.kind:
            ballots = self.node.validator_ballots
            validator_th = self.node.minimum_number_of_agreement

            for node_id, node_ballot in ballots.items():
                if node_ballot.node_state_kind == self.kind and ballot.message == node_ballot.message:
                    validator_th -= 1

            if validator_th == 0:
                self.node.set_state_accept()
                self.node.broadcast(ballot.message)


class AcceptState(State):
    def __init__(self, node):
        super(AcceptState, self).__init__(node, StateKind.ACCEPT)

    def init_node(self):
        pass

    def handle_ballot_impl(self, ballot):
        self.node.store(ballot)
        if ballot.node_state_kind == self.kind:
            ballots = self.node.validator_ballots
            validator_th = self.node.minimum_number_of_agreement
            for node_id, node_ballot in ballots.items():
                if node_ballot.node_state_kind == self.kind and ballot.message == node_ballot.message:
                    validator_th -= 1

            if validator_th == 0:
                self.node.set_state_all_confirm()


class AllConfirmState(State):
    def __init__(self, node):
        super(AllConfirmState, self).__init__(node, StateKind.ALLCONFIRM)

    def init_node(self):
        pass

    def handle_ballot_impl(self, ballot):
        # 다른 메시지가 들어오면 INIT 으로 변경
        if (not self.node.messages) or (self.node.messages[-1] != ballot.message):
            self.node.set_state_init()
            ballot.node_state_kind = StateKind.INIT
            self.node.receive_ballot(ballot)

        # 같은 메시지가 들어오면 pass
        else:
            pass
        return
