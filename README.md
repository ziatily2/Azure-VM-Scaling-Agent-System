Azure VM Scaling Agent System
Overview
This project implements a multi-agent system using the SPADE framework to monitor and dynamically scale Azure virtual machines (VMs) based on real-time metrics such as CPU usage, memory usage, disk read, and network inbound traffic. The system consists of three main agents:

MonitoringAgent: Collects metrics from Azure VMs using the Azure Monitor Query API.
DeciderAgent: Analyzes metrics and decides whether to scale up, scale down, or take no action based on predefined thresholds.
ExecutorAgent: Executes scaling decisions by adjusting VM sizes (e.g., from Standard_B1s to Standard_B2s or Standard_B4ms).

The system is designed for the Azure cloud environment, specifically for VMs in the "SMA-Cloud-Project" resource group located in West Europe.
Features

Monitors CPU, memory, disk read, and network inbound metrics for Azure VMs.
Automatically scales VMs up or down based on threshold-based decision logic.
Logs all agent activities and decisions for debugging and auditing.
Uses SPADE for agent communication via XMPP.
Simulates network latency and handles network failures (as seen in logs).

Repository Structure

monitoring_agent.py: Implements the MonitoringAgent to collect and send VM metrics.
decider_agent.py: Implements the DeciderAgent to analyze metrics and make scaling decisions.
monitor_cpu.py: A simple script to monitor local CPU usage (for testing or standalone use).
test_install.py: Verifies the installation of required Python libraries.
executor_agent.log: Sample log file showing ExecutorAgent activity (scaling actions and costs).
monitoring_agent.log: Log file for MonitoringAgent (generated during runtime).
decider_agent.log: Log file for DeciderAgent (generated during runtime).

Prerequisites

Python 3.8+
Azure Account with access to a subscription and the "SMA-Cloud-Project" resource group.
XMPP Server (e.g., ejabberd or Openfire) for SPADE agent communication.
Azure VMs named vm-initiale and vm-secondary in the specified resource group.

Required Python Libraries
Install the required libraries using pip:
pip install spade azure-identity azure-mgmt-compute azure-monitor-query psutil

Setup Instructions

Clone the Repository:
git clone https://github.com/<your-username>/AzureVMScalingAgentSystem.git
cd AzureVMScalingAgentSystem


Set Up Azure Credentials:

Ensure you have the Azure CLI installed and logged in (az login).
The system uses DefaultAzureCredential for authentication, which supports Azure CLI, environment variables, or managed identities.
Update the SUBSCRIPTION_ID in monitoring_agent.py to match your Azure subscription.


Configure XMPP Server:

Set up an XMPP server (e.g., ejabberd or Openfire).
Create XMPP accounts for the agents with the following JIDs and passwords:
MonitoringAgent: monitorilyas@jabber.fr / monitor123
DeciderAgent: deciderilyas@jabber.fr / decider123
ExecutorAgent: executorilyas@jabber.fr / executor123


Update the JIDs and passwords in monitoring_agent.py and decider_agent.py if necessary.


Verify Dependencies:

Run test_install.py to ensure all required libraries are installed:python test_install.py




Create Azure VMs (if not already created):

Ensure two VMs (vm-initiale and vm-secondary) exist in the "SMA-Cloud-Project" resource group in the "West Europe" region.
The system supports VM sizes: Standard_B1s (1 GB), Standard_B2s (4 GB), and Standard_B4ms (16 GB).



Usage

Start the MonitoringAgent:
python monitoring_agent.py

This agent collects metrics every 60 seconds and sends them to the DeciderAgent.

Start the DeciderAgent:
python decider_agent.py

This agent processes metrics and sends scaling decisions to the ExecutorAgent.

Start the ExecutorAgent:

The executor_agent.py file is not provided but is referenced in the logs. Ensure it is implemented to receive and act on decisions from the DeciderAgent.
Example command (assuming the file exists):python executor_agent.py




Monitor Logs:

Check monitoring_agent.log, decider_agent.log, and executor_agent.log for runtime information.
Logs include metrics, decisions, scaling actions, and costs.


Stop the Agents:

Press CTRL+C to stop each agent gracefully.



Example Workflow

MonitoringAgent collects metrics (e.g., CPU: 85%, Memory: 90%) for vm-initiale.
DeciderAgent receives metrics, determines scaling is needed (e.g., CPU > 80%), and sends scale_up to ExecutorAgent.
ExecutorAgent scales vm-initiale from Standard_B1s to Standard_B2s and logs the cost.
If metrics later drop below thresholds (e.g., CPU < 20%), the system may scale down.

Log Analysis
Based on executor_agent.log (dated May 21, 2025):

Both VMs (vm-initiale and vm-secondary) scaled up from Standard_B1s to Standard_B2s and then to Standard_B4ms within the first two minutes.
After reaching Standard_B4ms (maximum size), further scale_up requests were rejected.
Occasional network failures caused dropped instructions (e.g., at 16:27:17 for vm-secondary).
Costs were tracked per cycle, with a total cost of $0.0286 by 16:33:24.

Notes

The monitor_cpu.py script is a standalone utility for local CPU monitoring and is not integrated with the agent system.
The ExecutorAgent implementation is missing. It should handle scaling actions using the Azure Compute Management API.
Ensure the XMPP server is stable to avoid communication issues between agents.
Adjust thresholds in decider_agent.py (e.g., CPU_THRESHOLD_UPPER) to fine-tune scaling behavior.

Future Improvements

Implement the ExecutorAgent to complete the system.
Add support for scaling down VMs when metrics are consistently low.
Introduce cost optimization logic to balance performance and expenses.
Enhance error handling for Azure API failures.
Add a web interface to visualize metrics and scaling decisions.

License
This project is licensed under the MIT License.
