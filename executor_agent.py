

import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
import logging
import asyncio
import time

# Configure logging
logging.basicConfig(
    filename="executor_agent.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Hardcoded configuration
SUBSCRIPTION_ID = "a77851f8-c146-41d3-8a76-2708eed4632a"
RESOURCE_GROUP = "SMA-Cloud-Project"
LOCATION = "West Europe"
VM_SIZES = ["Standard_B1s", "Standard_B2s", "Standard_B4ms"]
VM_COSTS = {
    "Standard_B1s": 0.02,  # $0.02 per hour
    "Standard_B2s": 0.04,  # $0.04 per hour
    "Standard_B4ms": 0.08  # $0.08 per hour
}

# Azure Compute client
credential = DefaultAzureCredential()
compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)

class ExecutorAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        # Track state for each VM
        self.vms = {
            "vm-initiale": {
                "current_size": "Standard_B1s",
                "last_update_time": time.time(),
                "cost": 0.0
            },
            "vm-secondary": {
                "current_size": "Standard_B1s",
                "last_update_time": time.time(),
                "cost": 0.0
            }
        }
        self.total_cost = 0.0

    class ExecuteBehaviour(CyclicBehaviour):
        async def on_start(self):
            # Fetch initial VM sizes from Azure
            for vm_name in self.agent.vms.keys():
                try:
                    vm = compute_client.virtual_machines.get(RESOURCE_GROUP, vm_name)
                    self.agent.vms[vm_name]["current_size"] = vm.hardware_profile.vm_size
                    print(f"ExecutorAgent: Initial size for {vm_name}: {self.agent.vms[vm_name]['current_size']}")
                    logging.info(f"ExecutorAgent: Initial size for {vm_name}: {self.agent.vms[vm_name]['current_size']}")
                except Exception as e:
                    print(f"ExecutorAgent: Failed to fetch initial size for {vm_name}: {str(e)}")
                    logging.error(f"ExecutorAgent: Failed to fetch initial size for {vm_name}: {str(e)}")

        async def run(self):
            print(f"ExecutorAgent: Running in {RESOURCE_GROUP} ({LOCATION})...")
            logging.info(f"ExecutorAgent: Running in {RESOURCE_GROUP} ({LOCATION})")
            
            # Update costs for all VMs
            for vm_name, vm_state in self.agent.vms.items():
                current_time = time.time()
                time_spent_hours = (current_time - vm_state["last_update_time"]) / 3600
                cost = VM_COSTS[vm_state["current_size"]] * time_spent_hours
                vm_state["cost"] += cost
                self.agent.total_cost += cost
                vm_state["last_update_time"] = current_time
                print(f"ExecutorAgent: {vm_name} - Cost for {vm_state['current_size']} (Last cycle): ${cost:.4f}, "
                      f"VM Total Cost: ${vm_state['cost']:.4f}, Overall Total Cost: ${self.agent.total_cost:.4f}")
                logging.info(f"ExecutorAgent: {vm_name} - Cost for {vm_state['current_size']} (Last cycle): ${cost:.4f}, "
                             f"VM Total Cost: ${vm_state['cost']:.4f}, Overall Total Cost: ${self.agent.total_cost:.4f}")

            print("ExecutorAgent: Waiting for instructions...")
            logging.info("ExecutorAgent: Waiting for instructions")
            
            msg = await self.receive(timeout=60)  # Matches the 60-second cycle
            if msg:
                try:
                    # Parse message format: "vm_name:decision"
                    vm_name, decision = msg.body.split(":")
                    if vm_name not in self.agent.vms:
                        print(f"ExecutorAgent: Unknown VM {vm_name}, ignoring instruction.")
                        logging.warning(f"ExecutorAgent: Unknown VM {vm_name}, ignoring instruction")
                        return

                    print(f"ExecutorAgent: Action received for {vm_name}: {decision}")
                    logging.info(f"ExecutorAgent: Action received for {vm_name}: {decision}")
                    
                    if decision == "scale_up":
                        current_index = VM_SIZES.index(self.agent.vms[vm_name]["current_size"])
                        if current_index < len(VM_SIZES) - 1:
                            new_vm_size = VM_SIZES[current_index + 1]
                            print(f"ExecutorAgent: Scaling up {vm_name} from {self.agent.vms[vm_name]['current_size']} to {new_vm_size}...")
                            logging.info(f"ExecutorAgent: Scaling up {vm_name} from {self.agent.vms[vm_name]['current_size']} to {new_vm_size}")
                            
                            # Update VM size in Azure
                            try:
                                vm = compute_client.virtual_machines.get(RESOURCE_GROUP, vm_name)
                                vm.hardware_profile.vm_size = new_vm_size
                                async_update = compute_client.virtual_machines.begin_update(
                                    RESOURCE_GROUP, vm_name, vm
                                )
                                async_update.wait()
                                print(f"ExecutorAgent: {vm_name} scaled up to {new_vm_size} successfully.")
                                logging.info(f"ExecutorAgent: {vm_name} scaled up to {new_vm_size} successfully")
                                self.agent.vms[vm_name]["current_size"] = new_vm_size
                            except Exception as e:
                                print(f"ExecutorAgent: Failed to scale up {vm_name}: {str(e)}")
                                logging.error(f"ExecutorAgent: Failed to scale up {vm_name}: {str(e)}")
                        else:
                            print(f"ExecutorAgent: {vm_name} already at maximum VM size ({self.agent.vms[vm_name]['current_size']}), cannot scale up further.")
                            logging.info(f"ExecutorAgent: {vm_name} already at maximum VM size ({self.agent.vms[vm_name]['current_size']}), cannot scale up further")
                    elif decision == "scale_down":
                        current_index = VM_SIZES.index(self.agent.vms[vm_name]["current_size"])
                        if current_index > 0:
                            new_vm_size = VM_SIZES[current_index - 1]
                            print(f"ExecutorAgent: Scaling down {vm_name} from {self.agent.vms[vm_name]['current_size']} to {new_vm_size}...")
                            logging.info(f"ExecutorAgent: Scaling down {vm_name} from {self.agent.vms[vm_name]['current_size']} to {new_vm_size}")
                            
                            # Update VM size in Azure
                            try:
                                vm = compute_client.virtual_machines.get(RESOURCE_GROUP, vm_name)
                                vm.hardware_profile.vm_size = new_vm_size
                                async_update = compute_client.virtual_machines.begin_update(
                                    RESOURCE_GROUP, vm_name, vm
                                )
                                async_update.wait()
                                print(f"ExecutorAgent: {vm_name} scaled down to {new_vm_size} successfully.")
                                logging.info(f"ExecutorAgent: {vm_name} scaled down to {new_vm_size} successfully")
                                self.agent.vms[vm_name]["current_size"] = new_vm_size
                            except Exception as e:
                                print(f"ExecutorAgent: Failed to scale down {vm_name}: {str(e)}")
                                logging.error(f"ExecutorAgent: Failed to scale down {vm_name}: {str(e)}")
                        else:
                            print(f"ExecutorAgent: {vm_name} already at minimum VM size ({self.agent.vms[vm_name]['current_size']}), cannot scale down further.")
                            logging.info(f"ExecutorAgent: {vm_name} already at minimum VM size ({self.agent.vms[vm_name]['current_size']}), cannot scale down further")
                    else:
                        print(f"ExecutorAgent: No scaling needed for {vm_name}.")
                        logging.info(f"ExecutorAgent: No scaling needed for {vm_name}")
                except ValueError:
                    print(f"ExecutorAgent: Invalid message format: {msg.body}")
                    logging.warning(f"ExecutorAgent: Invalid message format: {msg.body}")
                except Exception as e:
                    print(f"ExecutorAgent: Error processing instruction: {str(e)}")
                    logging.error(f"ExecutorAgent: Error processing instruction: {str(e)}")
            else:
                print("ExecutorAgent: No instructions received within timeout.")
                logging.info("ExecutorAgent: No instructions received within timeout")

    async def setup(self):
        self.add_behaviour(self.ExecuteBehaviour())

if __name__ == "__main__":
    # XMPP configuration
    jid = "executorilyas@jabber.fr"
    password = "executor123"

    # Create and run the ExecutorAgent
    agent = ExecutorAgent(jid, password)
    agent.start()
    print("ExecutorAgent started. Press CTRL+C to stop.")
    while True:
        try:
            asyncio.sleep(1)
        except KeyboardInterrupt:
            agent.stop()
            break
