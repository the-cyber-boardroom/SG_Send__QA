"""Snapshot of observed transitions for a single state machine during a test run.

Pure data — no methods (Rule 5).  Produced by State_Machine__Utils.build_snapshot()
after a test run and used for:
  - Coverage reporting (missing transitions = untested paths)
  - Version comparison (unexpected transitions = new behaviour)
  - Security anomaly detection (expected data outputs vs actual)
"""
from typing import List

from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Version  import Safe_Str__Version
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now import Timestamp_Now

from sg_send_qa.state_machines.primitives    import Safe_Str__Machine_Name, Safe_Str__State_Name
from sg_send_qa.state_machines.State_Transition import State_Transition

# todo: refactor to Schema__ class
#       capture how how the comments on this class have been done, (this is how it should  be)
#       map out how this state-machine logic is done, since the whole idea of this is to provide an
#           abstraction layer for some tests, but for that to work this needs to be connected to the actual code
#           which doesn't seem that this how this state_machines is working
class State_Machine__Snapshot(Type_Safe):                   # Observed transitions for one state machine during one test run  .

    version              : Safe_Str__Version                # QA suite version that produced this snapshot (e.g. 'v0.3.0')
    timestamp            : Timestamp_Now                    # UTC milliseconds when snapshot was taken
    state_machine        : Safe_Str__Machine_Name           # name of the machine this snapshot covers
    states_found         : List[Safe_Str__State_Name]       # states actually visited during the run
    transitions_observed : List[State_Transition]           # (from, to, trigger) pairs actually traversed
    transitions_expected : List[State_Transition]           # full set from the state machine definition
    missing              : List[State_Transition]           # expected transitions not observed (coverage gap)
    unexpected           : List[State_Transition]           # observed transitions not in the definition (anomaly)
