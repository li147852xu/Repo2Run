# Copyright (2025) Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Optional Docker integration check (CONTRIBUTING: verify Docker-based builds).

Default CI / ``pytest tests/`` skips these. On a machine with Docker:

  REPO2RUN_DOCKER_IT=1 python -m pytest tests/test_docker_integration.py -v
"""

from __future__ import annotations

import os
import shutil
import subprocess

import pytest

_SKIP = os.environ.get("REPO2RUN_DOCKER_IT") != "1"


@pytest.mark.skipif(_SKIP, reason="Set REPO2RUN_DOCKER_IT=1 to run Docker integration checks")
def test_docker_cli_available() -> None:
    docker = shutil.which("docker")
    assert docker, "docker executable not found on PATH"
    result = subprocess.run(
        [docker, "info"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr or result.stdout
