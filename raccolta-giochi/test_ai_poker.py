"""Simula quante volte il PC folda dopo un raise del giocatore."""
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from giochi import texas_holdem as th

N_TRIALS = 10_000


def _decide_cpu_old(stato, mano):
    forza = th._stima_forza(mano["hole_banco"], mano["community"])
    to_call = th._to_call_banco(mano)
    chips_c = stato["chips_c"]
    can_check = to_call == 0
    can_raise = chips_c > to_call

    if mano.get("all_in_p") and to_call > 0:
        return ("all_in" if to_call >= chips_c else "call") if forza > 0.38 else "fold"
    if to_call > 0 and forza < 0.25 and random.random() < 0.75:
        return "fold"
    if chips_c > 0 and forza > 0.75 and (chips_c <= th.BIG_BLIND * 3 or random.random() < 0.25):
        return "all_in"
    if can_raise and forza > 0.7 and random.random() < 0.55:
        return "raise"
    if can_check:
        if can_raise and forza > 0.55 and random.random() < 0.35:
            return "raise"
        return "check"
    if forza > 0.35 or to_call <= th.BIG_BLIND:
        return "all_in" if to_call >= chips_c > 0 else "call"
    return "call" if random.random() < 0.2 else "fold"


def _setup_preflop_after_raise(raise_extra, hole_banco):
    """Replica il flusso reale: blind + raise giocatore (BB)."""
    stato = {"chips_p": th.CHIPS_INIZIALI, "chips_c": th.CHIPS_INIZIALI, "hand_num": 1}
    mano = {
        "mazzo": [],
        "hole_giocatore": ["Ah", "Kd"],
        "hole_banco": hole_banco,
        "community": [],
        "fase": "preflop",
        "pot": 0,
        "street_bet_p": 0,
        "street_bet_c": 0,
        "level": th.BIG_BLIND,
        "player_sb": False,
        "turno": "giocatore",
        "hand_over": False,
        "all_in_p": False,
        "all_in_c": False,
        "acted_p": False,
        "acted_c": False,
    }
    th._applica_puntata("giocatore", th.BIG_BLIND, stato, mano)  # BB giocatore
    th._applica_puntata("banco", th.BIG_BLIND, stato, mano)       # BB banco
    mano["level"] = th.BIG_BLIND
    th._applica_azione("giocatore", "raise", stato, mano, raise_extra)
    return stato, mano


def _setup_flop_after_raise(raise_extra, hole_banco, community):
    """Preflop call/call, flop check giocatore, raise giocatore."""
    stato = {"chips_p": th.CHIPS_INIZIALI, "chips_c": th.CHIPS_INIZIALI, "hand_num": 1}
    mano = {
        "mazzo": [],
        "hole_giocatore": ["Ah", "Kd"],
        "hole_banco": hole_banco,
        "community": community,
        "fase": "flop",
        "pot": th.SMALL_BLIND + th.BIG_BLIND * 2,
        "street_bet_p": th.BIG_BLIND,
        "street_bet_c": th.BIG_BLIND,
        "level": th.BIG_BLIND,
        "player_sb": False,
        "turno": "giocatore",
        "hand_over": False,
        "all_in_p": False,
        "all_in_c": False,
        "acted_p": False,
        "acted_c": False,
    }
    stato["chips_p"] -= th.BIG_BLIND
    stato["chips_c"] -= th.BIG_BLIND
    mano["street_bet_p"] = 0
    mano["street_bet_c"] = 0
    mano["level"] = 0
    th._applica_azione("giocatore", "check", stato, mano)
    th._applica_azione("banco", "check", stato, mano)
    mano["street_bet_p"] = 0
    mano["street_bet_c"] = 0
    mano["level"] = 0
    mano["turno"] = "giocatore"
    th._applica_azione("giocatore", "raise", stato, mano, raise_extra)
    return stato, mano


def _simulate(decide_fn, setup_fn, n=N_TRIALS):
    counts = Counter()
    to_calls = []
    mazzo = th._crea_mazzo()

    for _ in range(n):
        mazzo_copy = mazzo.copy()
        random.shuffle(mazzo_copy)
        hole = random.sample(mazzo_copy, 2)
        rest = [c for c in mazzo_copy if c not in hole]
        community = random.sample(rest, 3) if setup_fn.__name__ == "flop" else []

        if setup_fn.__name__ == "flop":
            stato, mano = _setup_flop_after_raise(th.RAISE_STEP, hole, community)
        else:
            stato, mano = _setup_preflop_after_raise(th.RAISE_STEP, hole)

        to_calls.append(th._to_call_banco(mano))
        azione = decide_fn(stato, mano)
        counts[azione] += 1

    return counts, sum(to_calls) / len(to_calls)


def _simulate_raise_sizes(decide_fn, raise_extras, n=N_TRIALS):
    results = {}
    mazzo = th._crea_mazzo()
    for extra in raise_extras:
        counts = Counter()
        for _ in range(n):
            mazzo_copy = mazzo.copy()
            random.shuffle(mazzo_copy)
            hole = random.sample(mazzo_copy, 2)
            stato, mano = _setup_preflop_after_raise(extra, hole)
            counts[decide_fn(stato, mano)] += 1
        results[extra] = counts
    return results


def main():
    random.seed(42)

    print(f"=== Test AI poker: {N_TRIALS:,} simulazioni per scenario ===\n")

    # Preflop raise standard (+20) con flusso reale
    old_pf, tc_pf = _simulate(_decide_cpu_old, type("preflop", (), {"__name__": "preflop"})())
    new_pf, _ = _simulate(th._decide_cpu, type("preflop", (), {"__name__": "preflop"})())

    print("PREFLOP - raise +20 (flusso reale del gioco)")
    print(f"  to_call medio CPU: {tc_pf:.0f}")
    print(f"  AI VECCHIA: fold {old_pf['fold']/N_TRIALS*100:.1f}% | call {old_pf['call']/N_TRIALS*100:.1f}% | raise {old_pf['raise']/N_TRIALS*100:.1f}%")
    print(f"  AI NUOVA:   fold {new_pf['fold']/N_TRIALS*100:.1f}% | call {new_pf['call']/N_TRIALS*100:.1f}% | raise {new_pf['raise']/N_TRIALS*100:.1f}%")
    print()

    # Flop
    old_fl, tc_fl = _simulate(_decide_cpu_old, type("flop", (), {"__name__": "flop"})())
    new_fl, _ = _simulate(th._decide_cpu, type("flop", (), {"__name__": "flop"})())

    print("FLOP - raise +20 dopo check/check")
    print(f"  to_call medio CPU: {tc_fl:.0f}")
    print(f"  AI VECCHIA: fold {old_fl['fold']/N_TRIALS*100:.1f}% | call {old_fl['call']/N_TRIALS*100:.1f}% | raise {old_fl['raise']/N_TRIALS*100:.1f}%")
    print(f"  AI NUOVA:   fold {new_fl['fold']/N_TRIALS*100:.1f}% | call {new_fl['call']/N_TRIALS*100:.1f}% | raise {new_fl['raise']/N_TRIALS*100:.1f}%")
    print()

    # Raise piu grandi preflop
    print("PREFLOP - fold rate vs dimensione raise (AI NUOVA)")
    for extra in [20, 40, 60, 100, 200]:
        counts = Counter()
        mazzo = th._crea_mazzo()
        for _ in range(N_TRIALS):
            mazzo_copy = mazzo.copy()
            random.shuffle(mazzo_copy)
            hole = random.sample(mazzo_copy, 2)
            stato, mano = _setup_preflop_after_raise(extra, hole)
            tc = th._to_call_banco(mano)
            counts[th._decide_cpu(stato, mano)] += 1
        print(f"  raise +{extra} (to_call ~{tc}): fold {counts['fold']/N_TRIALS*100:.1f}% | call {counts['call']/N_TRIALS*100:.1f}% | raise {counts['raise']/N_TRIALS*100:.1f}%")

    print()
    print("PREFLOP - fold rate vs dimensione raise (AI VECCHIA)")
    for extra in [20, 40, 60, 100, 200]:
        counts = Counter()
        mazzo = th._crea_mazzo()
        for _ in range(N_TRIALS):
            mazzo_copy = mazzo.copy()
            random.shuffle(mazzo_copy)
            hole = random.sample(mazzo_copy, 2)
            stato, mano = _setup_preflop_after_raise(extra, hole)
            tc = th._to_call_banco(mano)
            counts[_decide_cpu_old(stato, mano)] += 1
        print(f"  raise +{extra} (to_call ~{tc}): fold {counts['fold']/N_TRIALS*100:.1f}% | call {counts['call']/N_TRIALS*100:.1f}% | raise {counts['raise']/N_TRIALS*100:.1f}%")


if __name__ == "__main__":
    main()
