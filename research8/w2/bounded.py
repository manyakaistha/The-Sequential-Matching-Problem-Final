"""Finite B1 public-belief continuation; this is not the full-action oracle.

Every public decision epoch optimizes the existing <=12-action local menu,
including its parent and empty local replacement. Hidden clocks affect Bayesian
transition probabilities only: the menu sees a PublicView, never a particle.
The horizon includes today's reward and at most twelve *future* daily epochs.
No reward beyond that horizon is assigned a terminal value. This lower estimate
can bias decisions toward early commitment and cannot certify full-horizon
regret. Day 59 and a zero future horizon nevertheless book today's full q.

All caps abort the entire comparison to a validated current parent. A future
region overflow is unsupported evaluation, not an exact parent continuation.
Successful values are rational expectations for this finite menu/horizon only.
This module imports neither simulator/private code nor fitted model assets.
"""

from dataclasses import dataclass
from fractions import Fraction
from time import monotonic
from typing import Optional

from research8.planner import (
    Action, Belief, Caps, ExactPlanner, LimitExceeded, Model, PublicView,
    ScenarioState, _rational, bounded_action_menu,
)


@dataclass(frozen=True)
class BoundedConfig:
    future_steps: int = 12
    parent: str = "max_reward"
    max_states: int = 2000
    max_support_entries: int = 10000
    max_transitions: int = 50000
    max_joint_branches: int = 128
    wall_seconds: Optional[float] = None

    def __post_init__(self):
        if type(self.future_steps) is not int or not 0 <= self.future_steps <= 12:
            raise ValueError("future_steps must be an integer in [0,12]")
        if self.parent not in ("max_reward", "greedy"):
            raise ValueError("parent must be max_reward or greedy")
        for name, maximum in (("max_states", 2000), ("max_support_entries", 10000),
                              ("max_transitions", 50000), ("max_joint_branches", 128)):
            value = getattr(self, name)
            if type(value) is not int or not 0 < value <= maximum:
                raise ValueError(f"{name} must be a positive integer <={maximum}")
        if self.wall_seconds is not None:
            if type(self.wall_seconds) not in (int, float) or not 0 < self.wall_seconds <= .75:
                raise ValueError("wall_seconds must be positive and <=.75, or None")


@dataclass(frozen=True)
class BoundedResult:
    action: Action
    value: Optional[Fraction]
    fallback_reason: Optional[str]
    states: int
    transitions: int
    support_entries: int
    action_values: tuple[tuple[Action, Fraction], ...] = ()

    @property
    def used_fallback(self):
        return self.fallback_reason is not None


class _UnsupportedMenu(RuntimeError):
    pass


class BoundedPlanner(ExactPlanner):
    """B1 search over declared 4--8 actor toy laws, with fail-closed limits.

    ``solve(state, parent=action)`` can retain an explicit legal current control.
    Future parents use the fixed config rule and public observations only.
    Input/model validation errors are errors, rather than scientific estimates.
    A single instance is intended for sequential calls, not concurrent use.
    """

    def __init__(self, model: Model, config: BoundedConfig = BoundedConfig()):
        if not isinstance(config, BoundedConfig):
            raise ValueError("config must be BoundedConfig")
        self.config = config
        self._deadline = None
        super().__init__(model, Caps(
            max_states=config.max_states,
            max_transitions=config.max_transitions,
            max_joint_branches=config.max_joint_branches,
            max_support_entries=config.max_support_entries,
        ))

    def _guard(self):
        if self._deadline is not None and monotonic() >= self._deadline:
            raise LimitExceeded("wall guard exceeded")

    def _tick(self):
        self._guard()
        if self._transitions >= self.caps.max_transitions:
            raise LimitExceeded("transition cap exceeded")
        self._transitions += 1

    def _menu(self, view: PublicView, parent):
        self._guard()
        # Deliberately pass only a PublicView to the action construction code.
        menu = bounded_action_menu(self, view, parent=parent)
        self._guard()
        if menu.reason not in ("ok", "empty_parent"):
            raise _UnsupportedMenu(f"unsupported menu at day {view.day}: {menu.reason}")
        if len(menu.actions) > 12 or menu.parent not in menu.actions:
            raise _UnsupportedMenu("unsupported menu contract")
        return menu

    def _account(self, belief):
        self._guard()
        if self._states >= self.caps.max_states:
            raise LimitExceeded("state cap exceeded")
        if self._support_entries + len(belief.particles) > self.caps.max_support_entries:
            raise LimitExceeded("cumulative belief support cap exceeded")
        self._states += 1
        self._support_entries += len(belief.particles)

    def _value(self, belief, stop, controller):
        if controller != "bounded":
            # Retain the independent inherited oracle/rollout methods' semantics.
            return super()._value(belief, stop, controller)
        self._guard()
        key = (belief, stop, controller)
        if key in self._cache:
            return self._cache[key]
        self._account(belief)
        menu = self._menu(self.public_view(belief), self.config.parent)
        # _q_value groups latent branches by public observation, normalizes the
        # posterior, then calls this method once per public group before max.
        value = max(self._q_value(belief, action, stop, controller) for action in menu.actions)
        self._guard()
        self._cache[key] = value
        return value

    def solve(self, state, *, parent=None):
        """Return a complete bounded comparison or a parent-only fallback.

        A fallback has value=None and action_values=(), even if some candidates
        were completed before an unsupported branch or cap. Initial belief
        support overflow also falls back without pretending to normalize it.
        The returned parent is independently checked against today's full legal
        matchings; invalid explicit controls never enter the fallback path.
        """
        self._reset()
        started = monotonic()
        self._deadline = None
        # A current public view is needed to validate a lawful fallback even
        # when the finite prior itself exceeds the configured branch cap.
        if isinstance(state, Belief):
            if not state.particles:
                raise ValueError("a nonempty declared finite belief is required")
            # A capped calculation may not assume that an unchecked later
            # particle shares the first particle's public action legality.
            # Bound input validation independently of posterior search: larger
            # inputs are unsupported input errors, rather than an unvalidated
            # parent fallback. No hidden clock is sent to the menu.
            if len(state.particles) > 10000:
                raise ValueError("initial prior exceeds the 10000-entry input validation limit")
            view = self.public_view(state.particles[0][1])
            total = Fraction(0)
            for probability, particle in state.particles:
                probability = _rational(probability, "belief probability")
                if probability <= 0:
                    raise ValueError("belief probabilities must be positive")
                if self.public_view(particle) != view:
                    raise ValueError("belief particles must share the same current public observation")
                total += probability
            if total != 1:
                raise ValueError("belief probabilities must sum exactly to one")
        elif isinstance(state, ScenarioState):
            view = self.public_view(state)
        else:
            raise ValueError("state must be ScenarioState or Belief")
        root_menu = bounded_action_menu(self, view, parent=self.config.parent if parent is None else parent)
        fallback = root_menu.parent
        if fallback not in self.legal_actions(view):
            raise ValueError("fallback parent must be a legal whole matching")
        self._deadline = (started + self.config.wall_seconds
                          if self.config.wall_seconds is not None else None)
        try:
            self._guard()
            belief = self._belief(state)
            if root_menu.reason not in ("ok", "empty_parent"):
                raise _UnsupportedMenu(f"unsupported menu at day {view.day}: {root_menu.reason}")
            self._account(belief)
            stop = min(self.model.end_day, view.day + self.config.future_steps)
            values = tuple((action, self._q_value(belief, action, stop, "bounded"))
                           for action in root_menu.actions)
            self._guard()
            best = max(value for _, value in values)
            tied = tuple(action for action, value in values if value == best)
            chosen = fallback if fallback in tied else min(tied)
            result = BoundedResult(chosen, best, None, self._states, self._transitions,
                                   self._support_entries, values)
        except (LimitExceeded, _UnsupportedMenu) as error:
            # Never expose partial values as a completed action maximum.
            result = BoundedResult(fallback, None, str(error), self._states,
                                   self._transitions, self._support_entries)
        finally:
            self._deadline = None
        return result

