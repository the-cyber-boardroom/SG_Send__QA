"""Download flow state machine — pure data, no methods.

States and transitions derived from:
  - wait_for_download_state() calls in SG_Send__Browser__Pages
  - comment on line 185: 'loading → entry → ready → decrypting → complete → error'
  - test sequences in p0__combined_link, p0__friendly_token, p0__separate_key

Key branching:
  loading → entry   when no hash in URL (manual entry form shown)
  loading → ready   when hash present and transfer fetched successfully
  loading → error   when hash present but fetch fails
  ready   → browse|gallery|viewer via auto-route based on content type
"""
from typing import List

from osbot_utils.type_safe.Type_Safe import Type_Safe

from sg_send_qa.state_machines.primitives       import Safe_Str__Machine_Name, Safe_Str__State_Name
from sg_send_qa.state_machines.State_Transition import State_Transition


class State_Machine__Download(Type_Safe):
    name        : Safe_Str__Machine_Name = 'download_flow'
    states      : List[Safe_Str__State_Name]
    transitions : List[State_Transition]


def download_state_machine() -> State_Machine__Download:
    """Return the canonical download flow state machine instance."""
    return State_Machine__Download(
        states = [
            'loading',
            'entry',
            'ready',
            'decrypting',
            'complete',
            'error',
            'browse',
            'gallery',
            'viewer',
        ],
        transitions = [
            # Initial load — three branches from loading
            State_Transition(
                from_state = 'loading',
                to_state   = 'entry',
                trigger    = 'no_hash',
                guard      = 'url_has_no_fragment',
            ),
            State_Transition(
                from_state = 'loading',
                to_state   = 'ready',
                trigger    = 'hash_resolved',
                guard      = 'transfer_fetch_succeeded',
            ),
            State_Transition(
                from_state = 'loading',
                to_state   = 'error',
                trigger    = 'hash_failed',
                guard      = 'transfer_fetch_failed',
            ),
            # Manual entry form paths
            State_Transition(
                from_state = 'entry',
                to_state   = 'ready',
                trigger    = 'submit_valid_id',
                guard      = 'transfer_id_resolved',
            ),
            State_Transition(
                from_state = 'entry',
                to_state   = 'error',
                trigger    = 'submit_invalid_id',
                guard      = 'transfer_id_not_found',
            ),
            State_Transition(
                from_state = 'entry',
                to_state   = 'entry',
                trigger    = 'submit_bogus',
                guard      = 'inline_error_shown',
            ),
            # Decrypt path
            State_Transition(
                from_state = 'ready',
                to_state   = 'decrypting',
                trigger    = 'click_decrypt',
                security   = 'key_in_memory',
            ),
            # Auto-route from ready based on content type (combined-link mode)
            State_Transition(
                from_state = 'ready',
                to_state   = 'browse',
                trigger    = 'auto_route',
                guard      = 'content_type_is_folder',
            ),
            State_Transition(
                from_state = 'ready',
                to_state   = 'gallery',
                trigger    = 'auto_route',
                guard      = 'content_type_is_multi_image',
            ),
            State_Transition(
                from_state = 'ready',
                to_state   = 'viewer',
                trigger    = 'auto_route',
                guard      = 'content_type_is_single_file',
            ),
            # Decrypt outcomes
            State_Transition(
                from_state = 'decrypting',
                to_state   = 'complete',
                trigger    = 'decrypt_succeeded',
                security   = 'plaintext_in_dom',
            ),
            State_Transition(
                from_state = 'decrypting',
                to_state   = 'error',
                trigger    = 'decrypt_failed',
                guard      = 'wrong_key_or_corrupt',
            ),
        ],
    )
