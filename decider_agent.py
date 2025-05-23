
import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import logging
import asyncio

# Configure logging
logging.basicConfig(
    filename="decider_agent.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Hardcoded configuration
CPU_THRESHOLD_UPPER = 80  # Scale up if CPU > 80%
MEMORY_THRESHOLD_UPPER = 80  # Scale up if memory usage > 80%
DISK_READ_THRESHOLD_UPPER = 50  # Scale up if disk read > 50 MB (per minute)
NETWORK_IN_THRESHOLD_UPPER = 500  # Scale up if network in > 500 MB (per minute)
CPU_THRESHOLD_LOWER = 20  # Scale down if CPU < 20%
MEMORY_THRESHOLD_LOWER = 20  # Scale down if memory usage < 20%
DISK_READ_THRESHOLD_LOWER = 10  # Scale down if disk read < 10 MB
NETWORK_IN_THRESHOLD_LOWER = 100  # Scale down if network in < 100 MB
RESOURCE_GROUP = "SMA-Cloud-Project"
LOCATION = "West Europe"

# List of VMs (consistent with MonitoringAgent)
VMS = [
    {"id": "vm-initiale"},
    {"id": "vm-secondary"}
]

class DeciderAgent(Agent):
    class DecideBehaviour(CyclicBehaviour):
        async def run(self):
            for vm in VMS:
                vm_name = vm["id"]
                print(f"DeciderAgent: Running for {vm_name} in {RESOURCE_GROUP} ({LOCATION})...")
                logging.info(f"DeciderAgent: Running for {vm_name} in {RESOURCE_GROUP} ({LOCATION})")
                
                print(f"DeciderAgent: Waiting for metrics from {vm_name}...")
                logging.info(f"DeciderAgent: Waiting for metrics from {vm_name}")
                
                msg = await self.receive(timeout=60)  # Matches the 60-second cycle
                if msg:
                    try:
                        body = msg.body
                        if "cpu:" in body and "memory:" in body and "disk_read:" in body and "network_in:" in body:
                            metrics = body.split(",")
                            cpu_usage = float(metrics[0].split(":")[1])
                            memory_usage = float(metrics[1].split(":")[1])
                            disk_read = float(metrics[2].split(":")[1])
                            network_in = float(metrics[3].split(":")[1])
                            
                            print(f"DeciderAgent: Received data for {vm_name}: CPU Usage = {cpu_usage:.2f}%, "
                                  f"Memory Usage = {memory_usage:.2f}%, Disk Read = {disk_read:.2f} MB, "
                                  f"Network In = {network_in:.2f} MB")
                            logging.info(f"DeciderAgent: Received data for {vm_name}: CPU Usage = {cpu_usage:.2f}%, "
                                         f"Memory Usage = {memory_usage:.2f}%, Disk Read = {disk_read:.2f} MB, "
                                         f"Network In = {network_in:.2f} MB")
                            
                            # Decision logic for scaling up or down
                            if (cpu_usage > CPU_THRESHOLD_UPPER or 
                                memory_usage > MEMORY_THRESHOLD_UPPER or 
                                disk_read > DISK_READ_THRESHOLD_UPPER or 
                                network_in > NETWORK_IN_THRESHOLD_UPPER):
                                decision = "scale_up"
                                print(f"DeciderAgent: {vm_name} - Scaling up required! "
                                      f"CPU > {CPU_THRESHOLD_UPPER}% or Memory > {MEMORY_THRESHOLD_UPPER}% or "
                                      f"Disk Read > {DISK_READ_THRESHOLD_UPPER} MB or Network In > {NETWORK_IN_THRESHOLD_UPPER} MB")
                                logging.info(f"DeciderAgent: {vm_name} - Scaling up required! "
                                             f"CPU > {CPU_THRESHOLD_UPPER}% or Memory > {MEMORY_THRESHOLD_UPPER}% or "
                                             f"Disk Read > {DISK_READ_THRESHOLD_UPPER} MB or Network In > {NETWORK_IN_THRESHOLD_UPPER} MB")
                            elif (cpu_usage < CPU_THRESHOLD_LOWER and 
                                  memory_usage < MEMORY_THRESHOLD_LOWER and 
                                  disk_read < DISK_READ_THRESHOLD_LOWER and 
                                  network_in < NETWORK_IN_THRESHOLD_LOWER):
                                decision = "scale_down"
                                print(f"DeciderAgent: {vm_name} - Scaling down required! "
                                      f"CPU < {CPU_THRESHOLD_LOWER}% and Memory < {MEMORY_THRESHOLD_LOWER}% and "
                                      f"Disk Read < {DISK_READ_THRESHOLD_LOWER} MB and Network In < {NETWORK_IN_THRESHOLD_LOWER} MB")
                                logging.info(f"DeciderAgent: {vm_name} - Scaling down required! "
                                             f"CPU < {CPU_THRESHOLD_LOWER}% and Memory < {MEMORY_THRESHOLD_LOWER}% and "
                                             f"Disk Read < {DISK_READ_THRESHOLD_LOWER} MB and Network In < {NETWORK_IN_THRESHOLD_LOWER} MB")
                            else:
                                decision = "no_action"
                                print(f"DeciderAgent: {vm_name} - Metrics within normal range, no action necessary.")
                                logging.info(f"DeciderAgent: {vm_name} - Metrics within normal range, no action necessary")
                            
                            # Send decision to ExecutorAgent via XMPP
                            action_msg = spade.message.Message(
                                to="executorilyas@jabber.fr",
                                body=f"{vm_name}:{decision}"
                            )
                            await self.send(action_msg)
                            print(f"DeciderAgent: Sent decision ({decision}) for {vm_name} to ExecutorAgent.")
                            logging.info(f"DeciderAgent: Sent decision ({decision}) for {vm_name} to ExecutorAgent")
                        else:
                            print(f"DeciderAgent: Invalid message format received: {body}")
                            logging.warning(f"DeciderAgent: Invalid message format received: {body}")
                    except Exception as e:
                        print(f"DeciderAgent: Error processing message: {str(e)}")
                        logging.error(f"DeciderAgent: Error processing message: {str(e)}")
                else:
                    print(f"DeciderAgent: No metrics received for {vm_name} within timeout.")
                    logging.info(f"DeciderAgent: No metrics received for {vm_name} within timeout")

    async def setup(self):
        self.add_behaviour(self.DecideBehaviour())

if __name__ == "__main__":
    # XMPP configuration
    jid = "deciderilyas@jabber.fr"
    password = "decider123"

    # Create and run the DeciderAgent
    agent = DeciderAgent(jid, password)
    agent.start()
    print("DeciderAgent started. Press CTRL+C to stop.")
    while True:
        try:
            asyncio.sleep(1)
        except KeyboardInterrupt:
            agent.stop()
            break
