"""
WebSocket Load Testing Script

This script tests WebSocket server performance under high load:
- 10,000 concurrent connections
- Real-time message broadcasting
- Connection stability
- Memory and CPU usage

Requirements:
    pip install websockets asyncio aiohttp psutil

Usage:
    python websocket_load_test.py --url ws://localhost:8000/v1/ws --connections 10000
"""

import argparse
import asyncio
import json
import time
from collections import defaultdict
from datetime import datetime
from typing import List

import psutil
import websockets


class LoadTestStats:
    """Track load test statistics"""

    def __init__(self):
        self.connections_established = 0
        self.connections_failed = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.errors = defaultdict(int)
        self.latencies: List[float] = []
        self.start_time = None
        self.end_time = None

    def add_latency(self, latency: float):
        """Add message latency measurement"""
        self.latencies.append(latency)

    def get_percentile(self, p: float) -> float:
        """Get latency percentile"""
        if not self.latencies:
            return 0.0
        sorted_latencies = sorted(self.latencies)
        index = int(len(sorted_latencies) * p)
        return sorted_latencies[min(index, len(sorted_latencies) - 1)]

    def print_summary(self):
        """Print test summary"""
        duration = (self.end_time - self.start_time).total_seconds()

        print("\n" + "=" * 60)
        print("WEBSOCKET LOAD TEST SUMMARY")
        print("=" * 60)
        print(f"Duration: {duration:.2f} seconds")
        print("\nConnections:")
        print(f"  - Established: {self.connections_established}")
        print(f"  - Failed: {self.connections_failed}")
        success_rate = (
            self.connections_established
            / (self.connections_established + self.connections_failed)
            * 100
        )
        print(f"  - Success Rate: {success_rate:.2f}%")
        print("\nMessages:")
        print(f"  - Sent: {self.messages_sent}")
        print(f"  - Received: {self.messages_received}")
        print(f"  - Rate: {self.messages_received / duration:.2f} msg/s")

        if self.latencies:
            print("\nLatency (ms):")
            print(f"  - Min: {min(self.latencies) * 1000:.2f}")
            print(f"  - Max: {max(self.latencies) * 1000:.2f}")
            print(f"  - Mean: {sum(self.latencies) / len(self.latencies) * 1000:.2f}")
            print(f"  - p50: {self.get_percentile(0.5) * 1000:.2f}")
            print(f"  - p95: {self.get_percentile(0.95) * 1000:.2f}")
            print(f"  - p99: {self.get_percentile(0.99) * 1000:.2f}")

        if self.errors:
            print("\nErrors:")
            for error_type, count in self.errors.items():
                print(f"  - {error_type}: {count}")

        print("=" * 60 + "\n")


class WebSocketClient:
    """Single WebSocket client for load testing"""

    def __init__(self, url: str, client_id: int, stats: LoadTestStats):
        self.url = url
        self.client_id = client_id
        self.stats = stats
        self.websocket = None
        self.running = False

    async def connect(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(
                self.url,
                compression=None,  # Disable compression for baseline test
            )
            self.stats.connections_established += 1
            return True
        except Exception as e:
            self.stats.connections_failed += 1
            self.stats.errors[type(e).__name__] += 1
            return False

    async def send_subscribe(self):
        """Subscribe to stock updates"""
        try:
            message = {
                "type": "subscribe",
                "subscription_type": "stock",
                "targets": ["005930", "000660", "035720"],
            }
            await self.websocket.send(json.dumps(message))
            self.stats.messages_sent += 1
        except Exception as e:
            self.stats.errors[f"send_{type(e).__name__}"] += 1

    async def receive_messages(self, duration: int):
        """Receive messages for specified duration"""
        self.running = True
        start_time = time.time()

        try:
            while self.running and (time.time() - start_time < duration):
                try:
                    # Set timeout to check running flag periodically
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)

                    # Record receive time
                    receive_time = time.time()
                    self.stats.messages_received += 1

                    # Parse message to get send time
                    try:
                        data = json.loads(message)
                        if "timestamp" in data:
                            send_time = datetime.fromisoformat(
                                data["timestamp"].replace("Z", "+00:00")
                            ).timestamp()
                            latency = receive_time - send_time
                            if latency > 0:  # Only positive latencies
                                self.stats.add_latency(latency)
                    except (json.JSONDecodeError, ValueError):
                        pass

                except asyncio.TimeoutError:
                    continue
                except websockets.exceptions.ConnectionClosed:
                    break

        except Exception as e:
            self.stats.errors[f"receive_{type(e).__name__}"] += 1

        finally:
            self.running = False

    async def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception:
                pass


async def run_client(url: str, client_id: int, stats: LoadTestStats, duration: int):
    """Run a single client"""
    client = WebSocketClient(url, client_id, stats)

    # Connect
    if not await client.connect():
        return

    try:
        # Subscribe to updates
        await client.send_subscribe()

        # Receive messages
        await client.receive_messages(duration)

    finally:
        await client.disconnect()


async def run_load_test(
    url: str,
    num_connections: int,
    duration: int,
    ramp_up_time: int,
    batch_size: int,
):
    """
    Run load test with specified parameters.

    Args:
        url: WebSocket URL
        num_connections: Total number of connections
        duration: Test duration in seconds
        ramp_up_time: Time to ramp up connections in seconds
        batch_size: Number of connections to create per batch
    """
    stats = LoadTestStats()
    stats.start_time = datetime.utcnow()

    print(f"\n{'=' * 60}")
    print("Starting WebSocket Load Test")
    print(f"{'=' * 60}")
    print(f"URL: {url}")
    print(f"Connections: {num_connections}")
    print(f"Duration: {duration}s")
    print(f"Ramp-up time: {ramp_up_time}s")
    print(f"Batch size: {batch_size}")
    print(f"{'=' * 60}\n")

    # Monitor system resources
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Create connections in batches
    tasks = []
    delay_between_batches = ramp_up_time / (num_connections / batch_size)

    for i in range(0, num_connections, batch_size):
        batch_end = min(i + batch_size, num_connections)
        print(f"Creating connections {i + 1} to {batch_end}...")

        # Create batch of clients
        batch_tasks = [
            run_client(url, client_id, stats, duration)
            for client_id in range(i, batch_end)
        ]
        tasks.extend(batch_tasks)

        # Start batch
        for task in batch_tasks:
            asyncio.create_task(task)

        # Wait before next batch (except for last batch)
        if batch_end < num_connections:
            await asyncio.sleep(delay_between_batches)

    print(f"\nAll {num_connections} connections created.")
    print(f"Running test for {duration} seconds...\n")

    # Wait for all clients to complete
    await asyncio.gather(*tasks, return_exceptions=True)

    # Finish stats
    stats.end_time = datetime.utcnow()

    # System resources at end
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_used = final_memory - initial_memory

    # Print results
    stats.print_summary()

    print("System Resources:")
    print(f"  - Memory used: {memory_used:.2f} MB")
    print(f"  - Memory per connection: {memory_used / num_connections:.2f} MB")
    print(f"  - CPU percent: {process.cpu_percent()}%\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="WebSocket Load Testing")
    parser.add_argument(
        "--url",
        default="ws://localhost:8000/v1/ws",
        help="WebSocket URL (default: ws://localhost:8000/v1/ws)",
    )
    parser.add_argument(
        "--connections",
        type=int,
        default=1000,
        help="Number of concurrent connections (default: 1000)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Test duration in seconds (default: 60)",
    )
    parser.add_argument(
        "--ramp-up",
        type=int,
        default=10,
        help="Ramp-up time in seconds (default: 10)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of connections per batch (default: 100)",
    )

    args = parser.parse_args()

    # Run load test
    asyncio.run(
        run_load_test(
            url=args.url,
            num_connections=args.connections,
            duration=args.duration,
            ramp_up_time=args.ramp_up,
            batch_size=args.batch_size,
        )
    )


if __name__ == "__main__":
    main()
