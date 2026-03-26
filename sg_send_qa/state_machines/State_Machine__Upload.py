"""Upload wizard state machine — pure data, no methods.

States and transitions derived from the existing test code:
  - wait_for_upload_state() calls in SG_Send__Browser__Pages
  - test ordering in test_SG_Send__Browser__Pages__Upload.py
  - p0__upload__single_file test sequence

Two branching paths from 'file-ready':
  - needs_delivery_choice  → choosing-delivery (multi-file or folder)
  - single_file_or_text    → choosing-share    (single file or text: skips delivery step)
"""
from typing import List

from osbot_utils.type_safe.Type_Safe import Type_Safe

from sg_send_qa.state_machines.primitives  import Safe_Str__Machine_Name, Safe_Str__State_Name
from sg_send_qa.state_machines.State_Transition import State_Transition


class State_Machine__Upload(Type_Safe):
    name        : Safe_Str__Machine_Name = 'upload_wizard'
    states      : List[Safe_Str__State_Name]
    transitions : List[State_Transition]


def upload_state_machine() -> State_Machine__Upload:
    """Return the canonical upload wizard state machine instance."""
    return State_Machine__Upload(
        states = [
            'idle',
            'file-ready',
            'choosing-delivery',
            'choosing-share',
            'confirming',
            'encrypting',
            'uploading',
            'completing',
            'complete',
        ],
        transitions = [
            State_Transition(
                from_state = 'idle',
                to_state   = 'file-ready',
                trigger    = 'file_selected',
                guard      = 'file_input_has_file',
            ),
            # Branch: multi-file / folder → delivery step shown
            State_Transition(
                from_state = 'file-ready',
                to_state   = 'choosing-delivery',
                trigger    = 'auto_advance',
                guard      = 'needs_delivery_choice',
            ),
            # Branch: single file or text → delivery step skipped
            State_Transition(
                from_state = 'file-ready',
                to_state   = 'choosing-share',
                trigger    = 'auto_advance',
                guard      = 'single_file_or_text',
            ),
            State_Transition(
                from_state = 'choosing-delivery',
                to_state   = 'choosing-share',
                trigger    = 'click_next',
                guard      = 'delivery_mode_selected',
            ),
            State_Transition(
                from_state = 'choosing-share',
                to_state   = 'confirming',
                trigger    = 'select_share_mode',
                guard      = 'share_card_clicked',
            ),
            State_Transition(
                from_state = 'confirming',
                to_state   = 'encrypting',
                trigger    = 'click_encrypt_upload',
                security   = 'plaintext_in_memory',
            ),
            State_Transition(
                from_state = 'encrypting',
                to_state   = 'uploading',
                trigger    = 'auto_advance',
                guard      = 'encryption_complete',
                security   = 'ciphertext_only',
            ),
            State_Transition(
                from_state = 'uploading',
                to_state   = 'completing',
                trigger    = 'auto_advance',
                guard      = 'upload_complete',
            ),
            State_Transition(
                from_state = 'completing',
                to_state   = 'complete',
                trigger    = 'auto_advance',
                guard      = 'finalisation_complete',
                security   = 'key_in_url',    # combined mode — key visible in URL hash
            ),
        ],
    )
