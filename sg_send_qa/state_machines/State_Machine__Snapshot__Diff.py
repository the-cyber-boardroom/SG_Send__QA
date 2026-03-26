"""Diff between two State_Machine__Snapshot instances.

Pure data — no methods (Rule 5).  Produced by State_Machine__Utils.diff_snapshots().

Semantics:
  version_a / version_b  — the two versions being compared (a = older, b = newer)
  newly_covered          — transitions covered in b but not a  (new test coverage gained)
  coverage_lost          — transitions covered in a but not b  (regression — path no longer tested)
  new_unexpected         — unexpected transitions appearing in b but not a  (new anomaly)
  fixed_unexpected       — unexpected in a but gone in b  (anomaly resolved or model updated)
"""
from typing import List

from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Version  import Safe_Str__Version

from sg_send_qa.state_machines.primitives      import Safe_Str__Machine_Name
from sg_send_qa.state_machines.State_Transition import State_Transition


class State_Machine__Snapshot__Diff(Type_Safe):
    version_a        : Safe_Str__Version
    version_b        : Safe_Str__Version
    state_machine    : Safe_Str__Machine_Name
    newly_covered    : List[State_Transition]   # in b.observed but not a.observed → new coverage
    coverage_lost    : List[State_Transition]   # in a.observed but not b.observed → regression
    new_unexpected   : List[State_Transition]   # in b.unexpected but not a.unexpected → new anomaly
    fixed_unexpected : List[State_Transition]   # in a.unexpected but not b.unexpected → resolved
