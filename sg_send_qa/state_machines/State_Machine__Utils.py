"""Logic utilities for state machine analysis — separate from data (Rule 5).

All methods are pure functions over state machine data objects.
No state is mutated.  No IO.
"""
from osbot_utils.type_safe.Type_Safe import Type_Safe


class State_Machine__Utils(Type_Safe):

    def validate_transition(self, machine, from_state: str, to_state: str) -> bool:
        """Return True if (from_state → to_state) is a defined edge."""
        return any(
            str(t.from_state) == from_state and str(t.to_state) == to_state
            for t in machine.transitions
        )

    def reachable_states(self, machine, from_state: str) -> list:
        """Return list of states directly reachable from from_state."""
        return [
            str(t.to_state)
            for t in machine.transitions
            if str(t.from_state) == from_state
        ]

    # todo: refactor mermaid code to use MGraph_DB
    def to_mermaid(self, machine) -> str:
        """Render the state machine as a Mermaid stateDiagram-v2 block."""
        lines = ['stateDiagram-v2']
        for t in machine.transitions:
            label = str(t.trigger) if t.trigger else ''
            if t.guard:
                label += f' [{t.guard}]'
            if label:
                lines.append(f'    {t.from_state} --> {t.to_state} : {label}')
            else:
                lines.append(f'    {t.from_state} --> {t.to_state}')
        return '\n'.join(lines)

    def coverage(self, machine, observed_pairs: list) -> dict:
        """Compute transition coverage.

        Args:
            machine:         a State_Machine__* instance
            observed_pairs:  list of (from_state, to_state) tuples actually traversed

        Returns dict with keys:
            total       — total defined transitions
            covered     — transitions in observed_pairs
            missing     — defined transitions not in observed_pairs
            coverage_pct — int 0-100
        """
        defined  = [(str(t.from_state), str(t.to_state)) for t in machine.transitions]
        observed = set(observed_pairs)
        covered  = [pair for pair in defined if pair in observed]
        missing  = [pair for pair in defined if pair not in observed]
        pct      = round(len(covered) / len(defined) * 100) if defined else 0
        return {
            'total'       : len(defined),
            'covered'     : len(covered),
            'missing'     : missing,
            'coverage_pct': pct,
        }

    def missing_transitions(self, machine, observed_pairs: list) -> list:
        """Return list of State_Transition objects not yet observed."""
        observed = set(observed_pairs)
        return [
            t for t in machine.transitions
            if (str(t.from_state), str(t.to_state)) not in observed
        ]

    def security_annotations(self, machine) -> list:
        """Return all transitions that carry a security tag."""
        return [t for t in machine.transitions if t.security]

    def build_snapshot(self, machine, observed_pairs: list, version: str = '') -> 'State_Machine__Snapshot':
        """Build a State_Machine__Snapshot from a machine definition + observed pairs.

        Args:
            machine:         a State_Machine__* instance
            observed_pairs:  list of (from_state, to_state) tuples actually traversed
            version:         QA suite version string (e.g. 'v0.3.0')

        Returns a State_Machine__Snapshot capturing coverage and anomalies.
        """
        from sg_send_qa.state_machines.State_Machine__Snapshot import State_Machine__Snapshot
        from sg_send_qa.state_machines.State_Transition        import State_Transition

        defined_set  = {(str(t.from_state), str(t.to_state)) for t in machine.transitions}
        observed_set = {(f, t) for f, t in observed_pairs}

        states_found = sorted({s for pair in observed_pairs for s in pair})

        transitions_observed = [
            State_Transition(from_state=f, to_state=t)
            for f, t in sorted(observed_set)
        ]
        missing = [
            t for t in machine.transitions
            if (str(t.from_state), str(t.to_state)) not in observed_set
        ]
        unexpected = [
            State_Transition(from_state=f, to_state=t)
            for f, t in sorted(observed_set - defined_set)
        ]

        return State_Machine__Snapshot(
            version              = version,
            state_machine        = str(machine.name),
            states_found         = states_found,
            transitions_observed = transitions_observed,
            transitions_expected = list(machine.transitions),
            missing              = missing,
            unexpected           = unexpected,
        )

    def diff_snapshots(self, snap_a, snap_b) -> 'State_Machine__Snapshot__Diff':
        """Compare two snapshots and return a diff.

        Args:
            snap_a:  older snapshot (baseline)
            snap_b:  newer snapshot (current)

        Returns State_Machine__Snapshot__Diff with four change buckets:
          newly_covered    — new coverage gained in b
          coverage_lost    — coverage that disappeared (regression)
          new_unexpected   — new anomalies in b
          fixed_unexpected — anomalies from a that are gone in b
        """
        from sg_send_qa.state_machines.State_Machine__Snapshot__Diff import State_Machine__Snapshot__Diff

        pairs_a_obs  = {(str(t.from_state), str(t.to_state)) for t in snap_a.transitions_observed}
        pairs_b_obs  = {(str(t.from_state), str(t.to_state)) for t in snap_b.transitions_observed}
        pairs_a_unex = {(str(t.from_state), str(t.to_state)) for t in snap_a.unexpected}
        pairs_b_unex = {(str(t.from_state), str(t.to_state)) for t in snap_b.unexpected}

        def _transitions_for_pairs(snapshot, pairs):
            lookup = {(str(t.from_state), str(t.to_state)): t
                      for t in list(snapshot.transitions_observed) + list(snapshot.unexpected)}
            return [lookup[p] for p in sorted(pairs) if p in lookup]

        newly_covered    = _transitions_for_pairs(snap_b, pairs_b_obs  - pairs_a_obs)
        coverage_lost    = _transitions_for_pairs(snap_a, pairs_a_obs  - pairs_b_obs)
        new_unexpected   = _transitions_for_pairs(snap_b, pairs_b_unex - pairs_a_unex)
        fixed_unexpected = _transitions_for_pairs(snap_a, pairs_a_unex - pairs_b_unex)

        return State_Machine__Snapshot__Diff(
            version_a        = str(snap_a.version),
            version_b        = str(snap_b.version),
            state_machine    = str(snap_a.state_machine),
            newly_covered    = newly_covered,
            coverage_lost    = coverage_lost,
            new_unexpected   = new_unexpected,
            fixed_unexpected = fixed_unexpected,
        )

    def to_mermaid_coverage(self, machine, observed_pairs: list) -> str:
        """Render a coverage-annotated Mermaid stateDiagram-v2.

        States that were visited are coloured green; unvisited states are red.
        All transitions are shown regardless of coverage.

        Args:
            machine:         a State_Machine__* instance
            observed_pairs:  list of (from_state, to_state) tuples actually traversed
        """
        visited   = {s for pair in observed_pairs for s in pair}
        all_states = {str(s) for s in machine.states}
        unvisited  = all_states - visited

        lines = ['stateDiagram-v2']
        lines.append('    classDef covered  fill:#22c55e,color:#fff,font-weight:bold')
        lines.append('    classDef untested fill:#ef4444,color:#fff')

        for t in machine.transitions:
            label = str(t.trigger) if t.trigger else ''
            if t.guard:
                label += f' [{t.guard}]'
            if label:
                lines.append(f'    {t.from_state} --> {t.to_state} : {label}')
            else:
                lines.append(f'    {t.from_state} --> {t.to_state}')

        if visited:
            lines.append(f'    class {",".join(sorted(visited))} covered')
        if unvisited:
            lines.append(f'    class {",".join(sorted(unvisited))} untested')

        return '\n'.join(lines)
