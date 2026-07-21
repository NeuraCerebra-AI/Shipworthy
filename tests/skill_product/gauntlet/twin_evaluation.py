#!/usr/bin/env python3
"""Pure outcome classification for the four counterfactual twin behaviors."""

from __future__ import annotations


def evaluate_twin_observation(pair: str, observation: dict) -> dict[str, list[str]]:
    findings: list[str] = []
    controls: list[str] = []
    if pair == "persistence":
        if observation.get("feedback") == "success" and observation.get("after_reload") != observation.get("attempted"):
            findings.append("save-loses-data")
    elif pair == "disabled-recovery":
        if observation.get("disabled") and not observation.get("actionable_explanation"):
            findings.append("disabled-without-recovery")
    elif pair == "keyboard-command":
        if observation.get("command_exists"):
            controls.append("keyboard:command-palette")
    elif pair == "truthful-feedback":
        if observation.get("feedback") == "success" and not observation.get("persisted"):
            findings.append("feedback-contradicts-state")
    else:
        raise ValueError("unsupported twin pair")
    return {"findings": findings, "controls": controls}
