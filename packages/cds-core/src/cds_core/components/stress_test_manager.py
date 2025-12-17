import solara
import multiprocessing as mp
import psutil
import time
from threading import Thread, Event
import atexit

# Module-level state that persists across page navigation
class StressTestManager:
    def __init__(self):
        self.cpu_processes = []
        self.cpu_stop_event = None
        self.cpu_running = False
        self.memory_data = []
        self.memory_running = False

    def stop_all_cpu(self):
        self.cpu_running = False
        if self.cpu_stop_event:
            self.cpu_stop_event.set()
        for p in self.cpu_processes:
            p.kill()
            p.join(timeout=1)
        self.cpu_processes = []

    def stop_all_memory(self):
        self.memory_running = False
        self.memory_data = []

    def cleanup_all(self):
        self.stop_all_cpu()
        self.stop_all_memory()

# Global manager instance
_manager = StressTestManager()

# Register cleanup on kernel shutdown
atexit.register(_manager.cleanup_all)


@solara.component
def CPUStressTester():
    cpu_target = solara.use_reactive(50)
    current_cpu = solara.use_reactive(0.0)
    is_running = solara.use_reactive(_manager.cpu_running)

    def cpu_worker(stop_event):
        while not stop_event.is_set():
            _ = sum(i*i for i in range(10000))

    def monitor_and_control():
        try:
            while is_running.value:
                cpu_usage = psutil.cpu_percent(interval=0.5)
                current_cpu.set(cpu_usage)

                target = cpu_target.value
                num_cores = mp.cpu_count()
                desired_workers = max(1, int((target / 100) * num_cores))
                current_workers = len(_manager.cpu_processes)

                if current_workers < desired_workers:
                    for _ in range(desired_workers - current_workers):
                        p = mp.Process(target=cpu_worker, args=(_manager.cpu_stop_event,))
                        p.start()
                        _manager.cpu_processes.append(p)
                elif current_workers > desired_workers:
                    for _ in range(current_workers - desired_workers):
                        if _manager.cpu_processes:
                            p = _manager.cpu_processes.pop()
                            p.kill()
                            p.join(timeout=1)

                time.sleep(1)
        finally:
            current_cpu.value = 0.0

    def start_stress():
        _manager.cpu_stop_event = Event()
        _manager.cpu_running = True
        is_running.value = True
        thread = Thread(target=monitor_and_control, daemon=True)
        thread.start()

    def stop_stress():
        _manager.stop_all_cpu()
        is_running.set(False)
        current_cpu.set(0.0)

    with solara.Card("CPU Stress Tester"):
        if _manager.cpu_running and not is_running.value:
            solara.Warning("CPU test is running from another session")

        solara.Markdown(f"**Current CPU Usage:** {current_cpu.value:.1f}%")
        solara.Markdown(f"**Available Cores:** {mp.cpu_count()}")

        solara.SliderInt(
            "Target CPU %",
            value=cpu_target,
            min=0,
            max=100,
            disabled=is_running.value
        )

        with solara.Row():
            solara.Button(
                "Start Stress Test",
                on_click=start_stress,
                disabled=is_running.value,
                color="primary"
            )
            solara.Button(
                "Stop",
                on_click=stop_stress,
                disabled=not is_running.value,
                color="error"
            )


@solara.component
def MemoryStressTester():
    memory_target_mb = solara.use_reactive(500)
    current_memory_mb = solara.use_reactive(0.0)
    is_running = solara.use_reactive(_manager.memory_running)

    def monitor_memory():
        try:
            while is_running.value:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / (1024 * 1024)
                current_memory_mb.set(memory_mb)

                target_mb = memory_target_mb.value

                if memory_mb < target_mb - 50:
                    chunk = bytearray(10 * 1024 * 1024)
                    _manager.memory_data.append(chunk)
                    time.sleep(0.1)
                elif memory_mb > target_mb + 50:
                    if _manager.memory_data:
                        _manager.memory_data.pop()
                    time.sleep(0.1)
                else:
                    time.sleep(1)
        except Exception as e:
            print(f"Memory monitor error: {e}")
        finally:
            current_memory_mb.set(0.0)

    def start_stress():
        _manager.memory_running = True
        is_running.set(True)
        thread = Thread(target=monitor_memory, daemon=True)
        thread.start()

    def stop_stress():
        _manager.stop_all_memory()
        is_running.set(False)
        current_memory_mb.set(0.0)

    total_memory_mb = psutil.virtual_memory().total / (1024 * 1024)

    with solara.Card("Memory Stress Tester"):
        if _manager.memory_running and not is_running.value:
            solara.Warning("Memory test is running from another session")

        solara.Markdown(f"**Current Memory Usage:** {current_memory_mb.value:.1f} MB")
        solara.Markdown(f"**Total System Memory:** {total_memory_mb:.0f} MB")

        solara.SliderInt(
            "Target Memory (MB)",
            value=memory_target_mb,
            min=0,
            max=int(total_memory_mb * 0.8),
            step=100,
            disabled=is_running.value
        )

        with solara.Row():
            solara.Button(
                "Start Memory Test",
                on_click=start_stress,
                disabled=is_running.value,
                color="primary"
            )
            solara.Button(
                "Stop",
                on_click=stop_stress,
                disabled=not is_running.value,
                color="error"
            )


@solara.component
def StressTester():
    with solara.Column():
        # Emergency stop for all tests
        def emergency_stop():
            _manager.cleanup_all()

        solara.Button(
            "STOP ALL TESTS",
            on_click=emergency_stop,
            color="error",
            style="margin-bottom: 20px;"
        )

        CPUStressTester()
        MemoryStressTester()