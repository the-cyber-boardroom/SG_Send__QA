"""Pure data class representing a single state machine transition.

Shared by all machines.  No methods — Rule 5: schemas are pure data.
Logic (validate, render, diff) lives on State_Machine__Utils.
"""
from osbot_utils.type_safe.Type_Safe import Type_Safe

from sg_send_qa.state_machines.primitives import (Safe_Str__State_Name,
                                                    Safe_Str__Trigger_Name,
                                                    Safe_Str__Guard_Expr,
                                                    Safe_Str__Security_Tag)


class State_Transition(Type_Safe):
    from_state : Safe_Str__State_Name    # source state, e.g. 'idle'
    to_state   : Safe_Str__State_Name    # destination state, e.g. 'file-ready'
    trigger    : Safe_Str__Trigger_Name  # action that fires this edge, e.g. 'file_selected'
    guard      : Safe_Str__Guard_Expr    # pre-condition expression, e.g. 'file_input_has_file'
    security   : Safe_Str__Security_Tag  # data sensitivity at this edge, e.g. 'plaintext_in_memory'
