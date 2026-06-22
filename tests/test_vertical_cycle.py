from scripts.run_vertical_cycle import evidence_count


def test_evidence_count_is_transparent_and_deterministic():
    text = "critical inventory threshold and threshold control"
    assert evidence_count(text, "critical inventory threshold") == 4
