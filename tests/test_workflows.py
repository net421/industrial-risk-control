from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_github_workflows_parse_as_yaml():
    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    assert workflows
    for workflow in workflows:
        payload = yaml.safe_load(workflow.read_text(encoding="utf-8"))
        assert isinstance(payload, dict), workflow
        assert "jobs" in payload, workflow


def test_dependabot_configuration_parses():
    payload = yaml.safe_load(
        (ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
    )
    assert payload["version"] == 2

