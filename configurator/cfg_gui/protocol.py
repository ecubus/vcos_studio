import json
import random
import time
import asyncio
import websockets
from typing import Any, Callable, Dict, Optional


class HeartbeatProtocol:

    def __init__(self) -> None:
        self.running = False
        self.last_heartbeat = time.time()  # 上次心跳时间
        self.heartbeat_check_interval = 0.1  # 心跳检查间隔(秒)
        self.heartbeat_base_interval = 30  # 基础心跳间隔(秒)
        self.heartbeat_max_interval = 300  # 最大心跳间隔(秒)
        self.heartbeat_fail_count = 0  # 连续失败次数
        self.heartbeat_max_retries = 5  # 最大重试次数
        self.heartbeat_jitter = 0.1  # 随机抖动系数(10%)

    async def handle_heartbeats(self, result_cb: Callable):
        self.running = True
        while self.running:
            try:
                interval = self._calculate_heartbeat_interval()
                try:
                    await asyncio.wait_for(self._wait_for_heartbeat(time.time()), timeout=min(interval, 10))
                    self.heartbeat_fail_count = 0
                except asyncio.TimeoutError:
                    self.heartbeat_fail_count += 1
                    print(f"Heartbeat timeout, fail count: {self.heartbeat_fail_count}")

                    if self.heartbeat_fail_count >= self.heartbeat_max_retries:
                        print("Max heartbeat retries reached")
                        break

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Heartbeat error: {e}")
                self.heartbeat_fail_count += 1
                if self.heartbeat_fail_count >= self.heartbeat_max_retries:
                    break
        await result_cb()

    def _calculate_heartbeat_interval(self) -> float:
        """
        计算带指数退避和随机抖动的心跳间隔
        公式: interval = min(base * 2^fail_count * (1 ± jitter), max_interval)
        """
        # 计算基础退避时间
        base_interval = self.heartbeat_base_interval * (2**self.heartbeat_fail_count)

        # 应用最大间隔限制
        interval = min(base_interval, self.heartbeat_max_interval)

        # 添加随机抖动避免同步
        jitter_amount = interval * self.heartbeat_jitter
        interval += random.uniform(-jitter_amount, jitter_amount)

        # 确保心跳间隔不小于检测间隔
        return max(interval, self.heartbeat_check_interval * 10)

    async def _wait_for_heartbeat(self, start_time: float):

        while self.running:
            if self.last_heartbeat > start_time:
                return

            await asyncio.sleep(self.heartbeat_check_interval)

    def received_heartbeat(self):
        self.last_heartbeat = time.time()

    def stop(self):
        self.running = False


class Protocol(HeartbeatProtocol):

    def encode_message(self, message_type: str, payload: Dict[str, Any], app_id: str = "") -> bytes:
        message = {
            "type": message_type,
            "appId": app_id,
            "payload": payload,
            "timestamp": time.time(),
        }

        json_data = json.dumps(message).encode("utf-8")

        return json_data

    def decode_message(self, data: websockets.Data, is_client: bool = False) -> Optional[Dict[str, Any]]:
        try:
            message = json.loads(data.strip())
            if not is_client:
                self.received_heartbeat()
            self.valdaite_message(message)
            message["payload"] = message["payload"] or {}
            return message
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Protocol decode error: {e}")
            return None
        except (TypeError, KeyError) as e:
            print(f"Received data validation error: {e}")
            return None

    def valdaite_message(self, message: Dict[str, Any]):
        if not isinstance(message, dict):
            raise TypeError("Received data is not a dictionary")
        if "type" not in message:
            raise KeyError("Received data is missing 'type' key")
        if "payload" not in message:
            raise KeyError("Received data is missing 'payload' key")
