
import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from azure.identity import DefaultAzureCredential
from azure.monitor.query import MetricsQueryClient
from azure.mgmt.compute import ComputeManagementClient
import logging
import asyncio

# Configure logging
logging.basicConfig(
    filename="monitoring_agent.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Hardcoded configuration
MONITORING_INTERVAL_SECONDS = 60  # Interval for monitoring (already set as requested)
SUBSCRIPTION_ID = "a77851f8-c146-41d3-8a76-2708eed4632a"  # From your Azure account
RESOURCE_GROUP = "SMA-Cloud-Project"
LOCATION = "West Europe"

# List of VMs to monitor (consistent with your other scripts)
VMS = [
    {"id": "vm-initiale", "size": None},  # Size will be fetched dynamically
    {"id": "vm-secondary", "size": None}
]

# VM size to memory mapping (in GB)
VM_MEMORY_MAP = {
    "Standard_B1s": 1,    # 1 GB
    "Standard_B2s": 4,    # 4 GB
    "Standard_B4ms": 16   # 16 GB
}

# Azure clients
credential = DefaultAzureCredential()
metrics_client = MetricsQueryClient(credential)
compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)

class MonitoringAgent(Agent):
    class MonitorBehaviour(CyclicBehaviour):
        async def on_start(self):
            # Fetch VM sizes dynamically at startup
            for vm in VMS:
                try:
                    vm_info = compute_client.virtual_machines.get(RESOURCE_GROUP, vm["id"])
                    vm["size"] = vm_info.hardware_profile.vm_size
                    print(f"MonitoringAgent: Detected size for {vm['id']}: {vm['size']}")
                    logging.info(f"MonitoringAgent: Detected size for {vm['id']}: {vm['size']}")
                except Exception as e:
                    print(f"MonitoringAgent: Failed to fetch size for {vm['id']}: {str(e)}")
                    logging.error(f"MonitoringAgent: Failed to fetch size for {vm['id']}: {str(e)}")
                    vm["size"] = "Standard_B1s"  # Fallback to default

        async def run(self):
            for vm in VMS:
                vm_name = vm["id"]
                vm_size = vm["size"]
                print(f"MonitoringAgent: Running on Azure {vm_name} (Size: {vm_size}) in {RESOURCE_GROUP} ({LOCATION})...")
                logging.info(f"MonitoringAgent: Running on Azure {vm_name} (Size: {vm_size}) in {RESOURCE_GROUP} ({LOCATION})")
                
                print(f"MonitoringAgent: Collecting metrics for {vm_name} (CPU, memory, disk, and network)...")
                logging.info(f"MonitoringAgent: Collecting metrics for {vm_name} (CPU, memory, disk, and network)")
                
                try:
                    # Construct resource URI
                    resource_uri = f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}/providers/Microsoft.Compute/virtualMachines/{vm_name}"

                    # Query multiple metrics at once
                    response = metrics_client.query_resource(
                        resource_uri=resource_uri,
                        metric_names=["Percentage CPU", "Available Memory Bytes", "Disk Read Bytes", "Network In Total"],
                        timespan="PT1M"  # Last 1 minute
                    )

                    # Extract metrics
                    cpu_usage = 0.0
                    memory_available = 0.0
                    disk_read_bytes = 0.0
                    network_in_bytes = 0.0

                    for metric in response.metrics:
                        if metric.name.value == "Percentage CPU":
                            cpu_usage = metric.timeseries[0].data[-1].average if metric.timeseries else 0.0
                        elif metric.name.value == "Available Memory Bytes":
                            memory_available = metric.timeseries[0].data[-1].average if metric.timeseries else 0.0
                        elif metric.name.value == "Disk Read Bytes":
                            disk_read_bytes = metric.timeseries[0].data[-1].total if metric.timeseries else 0.0
                        elif metric.name.value == "Network In Total":
                            network_in_bytes = metric.timeseries[0].data[-1].total if metric.timeseries else 0.0

                    # Calculate memory usage percentage
                    total_memory = VM_MEMORY_MAP.get(vm_size, 1) * 1024 * 1024 * 1024  # Convert GB to bytes
                    memory_usage = ((total_memory - memory_available) / total_memory) * 100 if total_memory > 0 else 0.0

                    # Convert disk and network bytes to MB for readability
                    disk_read_mb = disk_read_bytes / (1024 * 1024) if disk_read_bytes else 0.0
                    network_in_mb = network_in_bytes / (1024 * 1024) if network_in_bytes else 0.0

                    print(f"MonitoringAgent: {vm_name} - CPU Usage = {cpu_usage:.2f}%")
                    print(f"MonitoringAgent: {vm_name} - Memory Usage = {memory_usage:.2f}% (Available: {memory_available / (1024*1024):.2f} MB)")
                    print(f"MonitoringAgent: {vm_name} - Disk Read = {disk_read_mb:.2f} MB")
                    print(f"MonitoringAgent: {vm_name} - Network In = {network_in_mb:.2f} MB")
                    logging.info(f"MonitoringAgent: {vm_name} - CPU Usage = {cpu_usage:.2f}%, Memory Usage = {memory_usage:.2f}%, Disk Read = {disk_read_mb:.2f} MB, Network In = {network_in_mb:.2f} MB")

                    # Send metrics to DeciderAgent via XMPP
                    msg = spade.message.Message(
                        to="deciderilyas@jabber.fr",
                        body=f"cpu:{cpu_usage},memory:{memory_usage},disk_read:{disk_read_mb},network_in:{network_in_mb}"
                    )
                    await self.send(msg)
                    print(f"MonitoringAgent: Sent metrics for {vm_name} to DeciderAgent.")
                    logging.info(f"MonitoringAgent: Sent metrics for {vm_name} to DeciderAgent")

                except Exception as e:
                    print(f"MonitoringAgent: Failed to collect metrics for {vm_name}: {str(e)}")
                    logging.error(f"MonitoringAgent: Failed to collect metrics for {vm_name}: {str(e)}")

            await asyncio.sleep(MONITORING_INTERVAL_SECONDS)

    async def setup(self):
        self.add_behaviour(self.MonitorBehaviour())

if __name__ == "__main__":
    # XMPP configuration
    jid = "monitorilyas@jabber.fr"
    password = "monitor123"

    # Create and run the MonitoringAgent
    agent = MonitoringAgent(jid, password)
    agent.start()
    print("MonitoringAgent started. Press CTRL+C to stop.")
    while True:
        try:
            asyncio.sleep(1)
        except KeyboardInterrupt:
            agent.stop()
            break
