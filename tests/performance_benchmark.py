#!/usr/bin/env python3
"""
Performance Benchmark for v1 vs v2 SSH MCP Tools

This script provides detailed performance analysis including:
- Response time measurements
- Memory usage comparison
- Throughput testing
- Resource utilization
- Scalability assessment
"""

import asyncio
import gc
import statistics
import sys
import time
import tracemalloc
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import Client
from python_src.python_ssh_mcp import SSHMCPServer
from python_src.python_ssh_mcp.models import SSHConfig


class PerformanceBenchmark:
    """Performance benchmark suite for SSH MCP tools."""

    def __init__(self):
        self.test_configs = {
            "test1": SSHConfig(
                name="test1",
                host="localhost",
                port=22,
                username="testuser",
                password="testpass",
            ),
            "test2": SSHConfig(
                name="test2",
                host="127.0.0.1",
                port=2222,
                username="testuser2",
                password="testpass2",
            ),
        }

    @asynccontextmanager
    async def setup_servers(self):
        """Setup both v1 and v2 servers with mocked SSH."""
        v1_server = SSHMCPServer("benchmark-v1")
        v2_server = SSHMCPServer("benchmark-v2")

        # Mock SSH manager to avoid real connections
        with patch(
            "python_src.python_ssh_mcp.ssh_manager.SSHConnectionManager"
        ) as mock_manager_class:
            mock_manager = AsyncMock()
            mock_manager_class.get_instance.return_value = mock_manager

            # Setup mock responses
            mock_manager.execute_command.return_value = "command output"
            mock_manager.upload_file.return_value = "Upload successful"
            mock_manager.download_file.return_value = "Download successful"
            mock_manager.get_all_server_infos.return_value = [
                type(
                    "ServerInfo",
                    (),
                    {
                        "name": "test1",
                        "host": "localhost",
                        "port": 22,
                        "username": "testuser",
                        "connected": True,
                    },
                )()
            ]

            # Initialize servers
            try:
                await v1_server.initialize(self.test_configs)
            except Exception:
                pass

            # Mock global SSH manager for v2
            with patch(
                "python_src.python_ssh_mcp.tools.v2.ssh_tools._ssh_manager",
                mock_manager,
            ):
                try:
                    await v2_server.initialize(self.test_configs)
                except Exception:
                    pass

                yield v1_server, v2_server

                # Cleanup
                try:
                    await v1_server.cleanup()
                    await v2_server.cleanup()
                except Exception:
                    pass

    async def measure_response_time(
        self, client: Client, tool_name: str, params: dict, iterations: int = 10
    ) -> list[float]:
        """Measure response time for a specific tool call."""
        times = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            try:
                await client.call_tool(tool_name, params)
            except Exception:
                pass  # Continue timing even if call fails
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        return times

    async def measure_memory_usage(
        self, client: Client, tool_name: str, params: dict
    ) -> tuple[float, float]:
        """Measure memory usage before and after tool call."""
        gc.collect()  # Clean up before measurement

        tracemalloc.start()

        # Baseline measurement
        try:
            await client.call_tool(tool_name, params)
        except Exception:
            pass

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return current / 1024 / 1024, peak / 1024 / 1024  # Convert to MB

    async def benchmark_tool_performance(self, v1_server, v2_server) -> dict:
        """Comprehensive tool performance benchmark."""
        results = {}

        test_cases = [
            ("execute-command", {"cmd_string": "ls -la"}),
            ("execute-command", {"cmd_string": "ps aux", "connectionName": "test1"}),
            (
                "upload",
                {"localPath": "/tmp/test.txt", "remotePath": "/home/user/test.txt"},
            ),
            (
                "download",
                {
                    "remotePath": "/home/user/test.txt",
                    "localPath": "/tmp/downloaded.txt",
                },
            ),
            ("list-servers", {}),
        ]

        async with (
            Client(v1_server.mcp) as v1_client,
            Client(v2_server.mcp) as v2_client,
        ):
            for tool_name, params in test_cases:
                print(f"\n📊 Benchmarking {tool_name} with {params}")

                # Response time measurements
                v1_times = await self.measure_response_time(
                    v1_client, tool_name, params, 20
                )
                v2_times = await self.measure_response_time(
                    v2_client, tool_name, params, 20
                )

                # Memory usage measurements
                v1_memory_current, v1_memory_peak = await self.measure_memory_usage(
                    v1_client, tool_name, params
                )
                v2_memory_current, v2_memory_peak = await self.measure_memory_usage(
                    v2_client, tool_name, params
                )

                # Calculate statistics
                v1_stats = {
                    "mean": statistics.mean(v1_times),
                    "median": statistics.median(v1_times),
                    "stdev": statistics.stdev(v1_times) if len(v1_times) > 1 else 0,
                    "min": min(v1_times),
                    "max": max(v1_times),
                    "memory_current": v1_memory_current,
                    "memory_peak": v1_memory_peak,
                }

                v2_stats = {
                    "mean": statistics.mean(v2_times),
                    "median": statistics.median(v2_times),
                    "stdev": statistics.stdev(v2_times) if len(v2_times) > 1 else 0,
                    "min": min(v2_times),
                    "max": max(v2_times),
                    "memory_current": v2_memory_current,
                    "memory_peak": v2_memory_peak,
                }

                # Calculate improvement percentages
                time_improvement = (
                    (v1_stats["mean"] - v2_stats["mean"]) / v1_stats["mean"]
                ) * 100
                memory_improvement = (
                    (
                        (v1_stats["memory_peak"] - v2_stats["memory_peak"])
                        / v1_stats["memory_peak"]
                    )
                    * 100
                    if v1_stats["memory_peak"] > 0
                    else 0
                )

                results[f"{tool_name}_{str(params)[:30]}"] = {
                    "v1": v1_stats,
                    "v2": v2_stats,
                    "time_improvement_percent": time_improvement,
                    "memory_improvement_percent": memory_improvement,
                }

                # Print immediate results
                print(
                    f"  v1: {v1_stats['mean']:.4f}s avg, {v1_stats['memory_peak']:.2f}MB peak"
                )
                print(
                    f"  v2: {v2_stats['mean']:.4f}s avg, {v2_stats['memory_peak']:.2f}MB peak"
                )
                print(
                    f"  Improvement: {time_improvement:+.1f}% time, {memory_improvement:+.1f}% memory"
                )

        return results

    async def throughput_test(self, v1_server, v2_server) -> dict:
        """Test concurrent request handling throughput."""
        print("\n🚀 Throughput Testing")

        concurrent_requests = [5, 10, 20]
        results = {}

        async with (
            Client(v1_server.mcp) as v1_client,
            Client(v2_server.mcp) as v2_client,
        ):
            for concurrency in concurrent_requests:
                print(f"\n📈 Testing {concurrency} concurrent requests")

                # Test v1 throughput
                start_time = time.perf_counter()
                v1_tasks = [
                    v1_client.call_tool(
                        "execute-command", {"cmd_string": f"echo test_{i}"}
                    )
                    for i in range(concurrency)
                ]
                try:
                    await asyncio.gather(*v1_tasks, return_exceptions=True)
                except Exception:
                    pass
                v1_duration = time.perf_counter() - start_time
                v1_rps = concurrency / v1_duration

                # Test v2 throughput
                start_time = time.perf_counter()
                v2_tasks = [
                    v2_client.call_tool(
                        "execute-command", {"cmd_string": f"echo test_{i}"}
                    )
                    for i in range(concurrency)
                ]
                try:
                    await asyncio.gather(*v2_tasks, return_exceptions=True)
                except Exception:
                    pass
                v2_duration = time.perf_counter() - start_time
                v2_rps = concurrency / v2_duration

                throughput_improvement = ((v2_rps - v1_rps) / v1_rps) * 100

                results[f"concurrency_{concurrency}"] = {
                    "v1_rps": v1_rps,
                    "v2_rps": v2_rps,
                    "improvement_percent": throughput_improvement,
                }

                print(f"  v1: {v1_rps:.2f} req/sec")
                print(f"  v2: {v2_rps:.2f} req/sec")
                print(f"  Improvement: {throughput_improvement:+.1f}%")

        return results

    def print_summary_report(self, tool_results: dict, throughput_results: dict):
        """Print comprehensive performance summary."""
        print("\n" + "=" * 80)
        print("📊 PERFORMANCE BENCHMARK SUMMARY REPORT")
        print("=" * 80)

        # Overall statistics
        time_improvements = [
            r["time_improvement_percent"] for r in tool_results.values()
        ]
        memory_improvements = [
            r["memory_improvement_percent"] for r in tool_results.values()
        ]

        avg_time_improvement = statistics.mean(time_improvements)
        avg_memory_improvement = statistics.mean(memory_improvements)

        print("\n🎯 Overall Performance:")
        print(f"  Average response time improvement: {avg_time_improvement:+.1f}%")
        print(f"  Average memory usage improvement: {avg_memory_improvement:+.1f}%")

        # Individual tool results
        print("\n🔧 Individual Tool Performance:")
        for tool_key, data in tool_results.items():
            tool_name = tool_key.split("_")[0]
            time_imp = data["time_improvement_percent"]
            mem_imp = data["memory_improvement_percent"]
            print(
                f"  {tool_name:15} | Time: {time_imp:+6.1f}% | Memory: {mem_imp:+6.1f}%"
            )

        # Throughput results
        print("\n🚀 Throughput Performance:")
        for concurrency_key, data in throughput_results.items():
            concurrency = concurrency_key.split("_")[1]
            improvement = data["improvement_percent"]
            v1_rps = data["v1_rps"]
            v2_rps = data["v2_rps"]
            print(
                f"  {concurrency:2} concurrent | v1: {v1_rps:6.2f} rps | v2: {v2_rps:6.2f} rps | Improvement: {improvement:+6.1f}%"
            )

        # Performance assessment
        print("\n🏆 Performance Assessment:")
        if avg_time_improvement > 0:
            print("  ✅ v2 shows improved response times")
        elif avg_time_improvement > -10:
            print("  ⚡ v2 response times within acceptable range")
        else:
            print("  ⚠️  v2 shows significant response time regression")

        if avg_memory_improvement > 0:
            print("  ✅ v2 shows improved memory efficiency")
        elif avg_memory_improvement > -20:
            print("  ⚡ v2 memory usage within acceptable range")
        else:
            print("  ⚠️  v2 shows significant memory regression")

        # Recommendation
        print("\n💡 Recommendation:")
        if avg_time_improvement >= -5 and avg_memory_improvement >= -10:
            print(
                "  🎉 RECOMMENDED: v2 migration provides good performance characteristics"
            )
        elif avg_time_improvement >= -15 and avg_memory_improvement >= -25:
            print("  ⚡ ACCEPTABLE: v2 migration has minor performance impact")
        else:
            print(
                "  ⚠️  REVIEW NEEDED: v2 migration shows significant performance regression"
            )

        print("=" * 80)

    async def run_full_benchmark(self):
        """Run the complete performance benchmark suite."""
        print("🧪 Starting SSH MCP Tools Performance Benchmark")
        print("=" * 80)

        async with self.setup_servers() as (v1_server, v2_server):
            # Tool performance benchmark
            tool_results = await self.benchmark_tool_performance(v1_server, v2_server)

            # Throughput benchmark
            throughput_results = await self.throughput_test(v1_server, v2_server)

            # Print summary report
            self.print_summary_report(tool_results, throughput_results)

            return {
                "tool_performance": tool_results,
                "throughput_performance": throughput_results,
            }


async def main():
    """Run the performance benchmark."""
    benchmark = PerformanceBenchmark()
    results = await benchmark.run_full_benchmark()
    return results


if __name__ == "__main__":
    asyncio.run(main())
