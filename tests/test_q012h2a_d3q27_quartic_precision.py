"""Full-payload/process/decision controls, separate from real-grid outcomes."""

from copy import deepcopy
from itertools import combinations_with_replacement
from types import SimpleNamespace

import numpy as np
import pytest

from research import d3q27_quartic_lbm as lbm
from research import d3q27_quartic_mp_numbers as numbers
from research import d3q27_quartic_mp_validation as validation
from research import q012h2a_d3q27_quartic_precision as run

BLOCKS = ((0, 1), (2, 3), (4, 5), (6, 7))
GROUP = (0, 1, 2, 3)


@pytest.fixture(scope="module")
def data():
    rng = np.random.default_rng(2026090902)
    n = 8
    indices = {
        d: np.array(list(combinations_with_replacement(range(n), d)), dtype=np.int64)
        for d in (2, 3)
    }

    def random(shape):
        return (rng.standard_normal(shape) + 1j * rng.standard_normal(shape)) / 13

    return lbm.TaylorData(
        size=17,
        omega=1.5,
        eta=0.02,
        power=2,
        waves=np.zeros((n, 3), dtype=np.int64),
        basis=random((27, n)),
        linear=np.diag(np.full(n, 0.7 + 0.1j)),
        indices=indices,
        h={d: random((len(ids), 27)) for d, ids in indices.items()},
        g={d: random((len(ids), n)) for d, ids in indices.items()},
    )


@pytest.fixture(scope="module")
def payloads(data):
    return {
        route: validation.payload(data, GROUP, BLOCKS, route, ("G2",) if route == "primary" else ())
        for route in ("primary", "worker")
    }


def test_full_fixed_selection_and_frozen_preregistration():
    groups = run.selected_groups()
    assert len(groups) == 698
    columns = run.validation.reference.columns
    assert sum(len(columns(group, run.inputs.BLOCK_INDICES, 104)) for group in groups) == 1826
    source = run.metadata()
    assert set(source["files"]) == set(run.FILES)
    assert source["parent_source"] == run.parent.metadata()
    assert source["parent_sha256"] == run.PARENT_SHA
    assert source["preregistration"]["commit"] == run.PREREG_COMMIT
    assert source["GMP_runtime"]["gmpy2"] == "2.3.1"


def test_names_require_both_precision_and_rounded_payloads_for_every_tuple():
    names = run.names(698)
    assert len(names) == len(set(names)) == 1397
    assert "tuple_0697.json" in names and "tuple_0697.npz" in names
    assert "tuple_0698.json" not in names


@pytest.mark.parametrize("route", ["primary", "worker"])
def test_all_values_lossless_roundtrip(tmp_path, payloads, route):
    document, arrays = payloads[route]
    mutations = ("G2",) if route == "primary" else ()
    filename = tmp_path / f"{route}.zip"
    with run.archive.Archive(filename, "x", ("data.json", "data.npz")) as saved:
        saved.put_document("data.json", document)
        saved.put_arrays("data.npz", arrays)
    with run.archive.Archive(filename, "r", ("data.json", "data.npz")) as saved:
        actual, values = saved.document("data.json"), saved.arrays("data.npz")
        decoded, _ = validation.validate_payload(actual, values, GROUP, BLOCKS, 8, route, mutations)
    assert run.same(actual, document) and run.archive.arrays_equal(values, arrays)
    assert decoded[192]["forcing"].shape == (27, 16)
    assert all(numbers.errors(decoded[128]["forcing"], decoded[192]["forcing"])["passed_1e10"])


@pytest.mark.parametrize(
    "kind",
    [
        "last_mp",
        "last_rounded",
        "missing_column",
        "key",
        "precision",
        "moment",
        "mutation",
        "extra",
        "missing_precision",
        "nonfinite",
    ],
)
def test_any_tail_or_schema_tampering_is_rejected(payloads, kind):
    document, arrays = deepcopy(payloads["primary"])
    if kind == "last_mp":
        document["precision"]["192"]["forcing"]["values"][-1][0] = ["1", 0]
    elif kind == "last_rounded":
        arrays["rounded192_forcing"][-1, -1] += 1
    elif kind == "missing_column":
        arrays["rounded192_forcing"] = arrays["rounded192_forcing"][:, :-1]
    elif kind == "key":
        arrays["keys"][-1] = arrays["keys"][0]
    elif kind == "precision":
        document["precision"]["128"]["forcing"]["bits"] = 192
    elif kind == "moment":
        arrays["moment_terms"][-1, -1] += 1
    elif kind == "mutation":
        arrays["without_G2"][-1, -1] += 1
    elif kind == "extra":
        arrays["extra"] = np.ones(1)
    elif kind == "missing_precision":
        del document["precision"]["128"]
    else:
        arrays["rounded192_forcing"][-1, -1] = np.nan
    with pytest.raises(ValueError):
        validation.validate_payload(document, arrays, GROUP, BLOCKS, 8, "primary", ("G2",))


def test_comparison_retains_all_old_errors_and_new_arms(data, payloads):
    doc_a, a = payloads["primary"]
    doc_b, b = payloads["worker"]
    left, _ = validation.validate_payload(doc_a, a, GROUP, BLOCKS, 8, "primary", ("G2",))
    right, _ = validation.validate_payload(doc_b, b, GROUP, BLOCKS, 8, "worker")
    product = lbm.block_product(data, GROUP, BLOCKS)
    terms = lbm.group_terms(data, product)
    old_a = {
        "keys": np.asarray(product.keys, dtype=np.int64),
        "forcing": lbm.forcing(terms),
        "collision": terms[:4].sum(axis=0),
        "composition": terms[4:].sum(axis=0),
    }
    old_b = deepcopy(old_a)
    old_b["forcing"][-1, -1] += 1
    result = validation.compare_columns(GROUP, left, right, a, b, old_a, old_b)
    assert result["columns"] == 16 and result["original_failed_columns"] == [15]
    assert len(result["old_to_high_precision"]) == 8
    assert all(result["agreement_192"]["forcing"]["passed_1e8"])
    assert all(result["moment_only"]["forcing"]["passed_1e8"])


def artificial_comparisons():
    # Exact registered counts, synthetic decisions only; no source/input receipt.
    return [
        {
            "columns": 3 if i < 430 else 2,
            "original_failed_columns": [],
            "agreement_192": {"forcing": {"passed_1e8": [True] * (3 if i < 430 else 2)}},
            "rounded_agreement": {"forcing": [0.0] * (3 if i < 430 else 2)},
            "precision_stability": {
                r: {"forcing": {"passed_1e10": [True] * (3 if i < 430 else 2)}}
                for r in ("primary", "worker")
            },
            "moment_only": {"forcing": {"passed_1e8": [True] * (3 if i < 430 else 2)}},
        }
        for i in range(698)
    ]


@pytest.mark.parametrize(
    "kind", ["agreement", "rounding", "stability", "moment", "physics", "mutation"]
)
def test_scientific_gates_are_distinct_and_tail_sensitive(kind):
    comparisons = artificial_comparisons()
    physics = [{"passed": True} for _ in range(20)]
    witnesses = {name: {"passed": True} for name in run.parent.primary.MUTATIONS}
    last = comparisons[-1]
    if kind == "agreement":
        last["agreement_192"]["forcing"]["passed_1e8"][-1] = False
    elif kind == "rounding":
        last["rounded_agreement"]["forcing"][-1] = 1e-7
    elif kind == "stability":
        last["precision_stability"]["worker"]["forcing"]["passed_1e10"][-1] = False
    elif kind == "moment":
        last["moment_only"]["forcing"]["passed_1e8"][-1] = False
    elif kind == "physics":
        physics[-1]["passed"] = False
    else:
        witnesses["G3"]["passed"] = False
    summary = validation.summarize(comparisons, physics, witnesses)
    assert summary["high_precision_forcing_candidate"] == (kind == "moment")
    assert summary["moment_only_explanation_passed"] == (kind != "moment")


def test_missing_tuple_and_false_quartic_success_rejected():
    with pytest.raises(ValueError, match="all fixed"):
        validation.summarize(artificial_comparisons()[:-1], [{"passed": True}] * 20, {})
    grids = [
        {
            "size": size,
            "summary": {
                "original_failed_columns": count,
                "high_precision_forcing_candidate": True,
                "moment_only_explanation_passed": False,
            },
        }
        for size, count in zip((17, 33, 65), (182, 174, 158), strict=True)
    ]
    decision = validation.decision(grids)
    assert (
        decision["high_precision_forcing_candidate"]
        and not decision["moment_only_explanation_passed"]
    )
    assert not decision["original_H1_passed"]
    assert decision["H2"] == decision["H3_with_solves"] == "not_evaluated"
    grids[-1]["summary"]["original_failed_columns"] = 157
    with pytest.raises(ValueError, match="514"):
        validation.decision(grids)


def test_predeclared_mutations_not_cherry_picked():
    witnesses = {name: {"group": GROUP} for name in run.parent.primary.MUTATIONS}
    assert run.mutations_for(witnesses, GROUP, "primary") == run.parent.primary.MUTATIONS
    assert run.mutations_for(witnesses, GROUP, "worker") == ()
    assert run.mutations_for(witnesses, (0, 0, 0, 0), "primary") == ()


def test_start_resource_failure_keeps_measured_prefix(tmp_path, monkeypatch):
    measurements = [{"stage": "process_start", "available_physical_bytes": 3 * 1024**3}]

    def fail(*args, **kwargs):
        raise run.resources.ResourceLimitError("insufficient starting memory", measurements)

    monkeypatch.setattr(run.resources, "Guard", fail)
    with pytest.raises(run.resources.ResourceLimitError):
        run.run_grid(tmp_path / "precision.json", 17, "primary")
    row = run.common.read_json(tmp_path / "precision_n17_primary_failure.json")
    run.common.unseal(row)
    assert row["resources"] == measurements and row["completed_tuple_prefix"] == 0
    assert row["q012h2a_outcome"] == "inconclusive" and row["q012h2_outcome"] == "not_evaluated"


def test_existing_outputs_remain_untouched(tmp_path):
    path = tmp_path / "precision.json"
    run.common.save_exclusive(path, {"preserved": True})
    with pytest.raises(ValueError, match="existing"):
        run.execute(path)
    assert run.common.read_json(path) == {"preserved": True}
    assert not (tmp_path / "precision_failure.json").exists()


@pytest.mark.parametrize("failure", ["exit", "pid"])
def test_actual_process_identity_and_exit_are_required(tmp_path, monkeypatch, failure):
    process = SimpleNamespace(
        pid=123,
        returncode=1 if failure == "exit" else 0,
        communicate=lambda: ('{"process_id":124}', None),
    )
    monkeypatch.setattr(run.subprocess, "Popen", lambda *a, **kw: process)
    with pytest.raises(ValueError, match="exited 1" if failure == "exit" else "PID"):
        run.call_child(tmp_path / "precision.json", 17, "primary")


def test_resource_disk_prefix_includes_custom_outputs_only(tmp_path):
    run.common.save_exclusive(tmp_path / "diagnosis.json", {"run": 1})
    run.common.save_exclusive(tmp_path / "diagnosis_n17_primary.json", {"run": 1})
    run.common.save_exclusive(tmp_path / "other.json", {"unrelated": True})
    assert run.total_bytes(tmp_path / "diagnosis.json") == sum(
        p.stat().st_size for p in tmp_path.glob("diagnosis*")
    )


def test_retry_disk_accounting_keeps_previous_failed_attempts(tmp_path):
    prefix = run.OUTPUT.stem
    old = tmp_path / f"{prefix}_failure.json"
    retry = tmp_path / f"{prefix}_attempt02.json"
    run.common.save_exclusive(old, {"preserved": True})
    run.common.save_exclusive(retry, {"attempt": 2})
    assert run.resource_output(retry) == tmp_path / prefix
    assert run.total_bytes(retry) == old.stat().st_size + retry.stat().st_size


def test_outer_preflight_retains_measurement_without_starting_parent(tmp_path, monkeypatch):
    measurements = [{"stage": "process_start", "available_physical_bytes": 3 * 1024**3}]

    def fail(*args, **kwargs):
        raise run.resources.ResourceLimitError("insufficient starting memory", measurements)

    def forbidden(*args, **kwargs):
        raise AssertionError("parent audit started despite failed measured preflight")

    monkeypatch.setattr(run, "metadata", lambda: {"files": {}})
    monkeypatch.setattr(run.oracle, "verify_source_commit", lambda *a: None)
    monkeypatch.setattr(run.resources, "Guard", fail)
    monkeypatch.setattr(run, "audit_parent", forbidden)
    with pytest.raises(run.resources.ResourceLimitError):
        run.execute(tmp_path / "precision.json")
    row = run.common.read_json(tmp_path / "precision_failure.json")
    assert row["resources"] == measurements and row["completed_tuple_prefix"] == 0
    assert "not child-start evidence" in row["outer_failure_observation"]["scope"]


def test_unavailable_failure_observation_does_not_erase_original_cause(tmp_path, monkeypatch):
    def fail():
        raise OSError("counter unavailable")

    monkeypatch.setattr(run.resources, "counters", fail)
    path = tmp_path / "failure.json"
    run.save_failure(path, ValueError("original failure"))
    row = run.common.read_json(path)
    assert row["error"] == "original failure"
    assert row["resources"] == []
    assert row["outer_failure_observation"] == {"unavailable": "OSError"}


def test_resource_remediation_does_not_change_scientific_kernels():
    commit = "c007e72bbc3c43f44c80e3addcb7e5d9f093a9f0"
    resource_fix = "95a002e3a932cff18935c54e54361a6f1dc3d2c0"
    for name in run.FILES[:4]:
        # Preserve the historical resource-only claim. The later normalization
        # fix is separate and must not rewrite either previous implementation.
        assert run.oracle.normalized_sha(
            run.oracle.git_bytes("show", f"{resource_fix}:{name}")
        ) == run.oracle.normalized_sha(run.oracle.git_bytes("show", f"{commit}:{name}"))


def test_normalization_fix_preserves_all_other_arithmetic_and_raw_polynomials():
    commit = "95a002e3a932cff18935c54e54361a6f1dc3d2c0"
    for name in run.FILES[:4]:
        current = (run.ROOT / name).read_text(encoding="utf-8")
        previous = run.oracle.git_bytes("show", f"{commit}:{name}").decode("utf-8")
        if name.endswith("_reference.py"):
            current, previous = (value.split("\ndef group(", 1)[0] for value in (current, previous))
        assert run.oracle.normalized_sha(current.encode()) == run.oracle.normalized_sha(
            previous.encode()
        )


@pytest.mark.parametrize("route", ["primary", "worker"])
@pytest.mark.parametrize("group", [(0, 0, 0, 1), (0, 0, 1, 1), (0, 0, 1, 2)])
def test_repeated_block_payload_has_exact_normalized_identity(data, group, route):
    document, arrays = validation.payload(data, group, BLOCKS, route)
    decoded, _ = validation.validate_payload(document, arrays, group, BLOCKS, 8, route)
    for bits in (128, 192):
        with numbers.context(bits):
            value = decoded[bits]
            assert np.array_equal(value["forcing"], value["collision"] - value["composition"])


def test_first_stopped_attempt_is_preserved_without_inventing_missing_measurements():
    path = run.OUTPUT.with_name(run.OUTPUT.stem + "_failure.json")
    assert (
        run.archive.file_sha(path)
        == "9c696615aef6936ca364a326fbfc88aad5320a09650615a5a40cfe25a0034998"
    )
    row = run.common.read_json(path)
    run.common.unseal(row)
    assert row["process_id"] == 28148 and row["error"] == "child 27704 exited 1"
    assert row["resources"] == [] and row["completed_tuple_prefix"] == 0
    assert not row["partial_archive_preserved"]
    assert row["q012h2a_outcome"] == "inconclusive" and row["q012h2_outcome"] == "not_evaluated"
