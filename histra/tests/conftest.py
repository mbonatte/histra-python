"""Pytest configuration and shared fixtures for HiStrA test suite."""
import pytest
from histra.tests.csharp_runner_client import CSharpRunnerClient, get_csharp_runner


@pytest.fixture(scope="session")
def csharp_runner() -> CSharpRunnerClient:
    """Session fixture providing CSharpRunnerClient, skipping if the binary is absent."""
    client = get_csharp_runner()
    if not client.is_available():
        pytest.skip("C# HiStrA .NET MicroRunner binary is not available in this environment")
    return client
