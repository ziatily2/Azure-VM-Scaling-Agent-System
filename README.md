
# Azure VM Scaling Agent System

## 🧠 Overview

This project implements a **multi-agent system** for dynamic Azure VM scaling using the [SPADE](https://spade-mas.readthedocs.io/en/latest/) framework. Agents monitor real-time metrics such as CPU, memory, disk I/O, and network traffic, then make autonomous decisions to scale VMs up or down using the Azure Compute Management API.

### 👨‍💻 System Components

- **MonitoringAgent** – Gathers metrics from Azure Monitor.
- **DeciderAgent** – Analyzes metrics and decides to scale up/down or maintain.
- **ExecutorAgent** – (To be implemented) Executes scale actions on Azure VMs.

> Built for Azure's `SMA-Cloud-Project` resource group in the `West Europe` region.

---

## 🚀 Features

- ⏱ Real-time monitoring of Azure VMs (CPU, memory, disk read, network).
- 📈 Automatic VM scaling based on threshold logic.
- 🗂 SPADE-powered agent communication over XMPP.
- 🧾 Logging of all metrics, decisions, and actions.
- ⚠ Simulated network latency & error resilience.

---

## 📁 Repository Structure

```bash
AzureVMScalingAgentSystem/
├── monitoring_agent.py       # Collects and sends VM metrics
├── decider_agent.py          # Makes scaling decisions
├── monitor_cpu.py            # Local CPU monitoring (standalone)
├── test_install.py           # Checks Python dependencies
├── executor_agent.log        # Example ExecutorAgent log
├── monitoring_agent.log      # Runtime logs for MonitoringAgent
├── decider_agent.log         # Runtime logs for DeciderAgent
````

---

## ⚙️ Prerequisites

* Python 3.8+
* Azure Subscription with access to `SMA-Cloud-Project` (West Europe)
* XMPP Server (e.g., ejabberd, Openfire)
* Azure VMs:

  * `vm-initiale`
  * `vm-secondary`

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/AzureVMScalingAgentSystem.git
cd AzureVMScalingAgentSystem

# Install required Python libraries
pip install spade azure-identity azure-mgmt-compute azure-monitor-query psutil
```

---

## 🔐 Azure & XMPP Setup

### 1. Azure Configuration

* Install Azure CLI: [https://learn.microsoft.com/en-us/cli/azure/install-azure-cli](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
* Login with `az login`
* Ensure `DefaultAzureCredential` is authorized
* Update `SUBSCRIPTION_ID` in `monitoring_agent.py`

### 2. XMPP Agent Accounts

Create XMPP accounts for agents:

| Agent      | JID                       | Password      |
| ---------- | ------------------------- | ------------- |
| Monitoring | `monitorilyas@jabber.fr`  | `monitor123`  |
| Decider    | `deciderilyas@jabber.fr`  | `decider123`  |
| Executor   | `executorilyas@jabber.fr` | `executor123` |

Update credentials in the respective Python files.

---

## ✅ Dependency Check

```bash
python test_install.py
```

---

## 💡 Usage

1. **Start Monitoring Agent**

   ```bash
   python monitoring_agent.py
   ```

2. **Start Decider Agent**

   ```bash
   python decider_agent.py
   ```

3. **Start Executor Agent** (if implemented)

   ```bash
   python executor_agent.py
   ```

4. **Monitor Logs**

   * `monitoring_agent.log`
   * `decider_agent.log`
   * `executor_agent.log`

5. **Stop Agents**

   Use `CTRL + C` to gracefully shut down each agent.

---

## 📊 Example Workflow

1. MonitoringAgent detects `CPU = 85%` on `vm-initiale`.
2. DeciderAgent triggers a `scale_up` action.
3. ExecutorAgent scales the VM from `Standard_B1s` → `Standard_B2s`.
4. Logs show action success and cost tracking.

---

## 📈 Log Insight (Sample)

From `executor_agent.log` (May 21, 2025):

* VMs were scaled from `B1s → B2s → B4ms`.
* Max size (`B4ms`) reached within 2 minutes.
* Scale-ups after reaching the limit were rejected.
* Cost tracked: **\$0.0286** at `16:33:24`.

---

## ⚠ Notes

* `monitor_cpu.py` is for local CPU monitoring only.
* `executor_agent.py` must be implemented to complete the system.
* Stable XMPP connection is critical for agent communication.
* Thresholds can be tuned in `decider_agent.py`.

---

## 🔮 Future Improvements

* Implement full **ExecutorAgent** logic using Azure SDK.
* Add **scale-down** logic based on usage drops.
* Introduce **cost optimization** strategies.
* Improve error handling for API/network issues.
* Add a **dashboard** for real-time visualization.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🤝 Contributing

Contributions and feedback are welcome! Please submit issues or pull requests.

---
