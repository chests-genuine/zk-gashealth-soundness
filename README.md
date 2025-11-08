# zk-gashealth-soundness

## Overview
**zk-gashealth-soundness** analyzes recent blocks for **gas utilization soundness** and **base fee stability**.  
By evaluating gas usage and base fee volatility, it helps ensure stable proof generation and cost predictability in zk-rollups and EVM-compatible systems.

## Features
- Scans last N blocks and computes gas utilization metrics  
- Calculates average and range of base fees (in Gwei)  
- Detects unstable block utilization patterns  
- JSON output for dashboards and CI pipelines  
- Exit codes for automation (0 for stable, 2 for unstable)  

## Installation
1. Requires Python 3.9+  
2. Install dependency:
   pip install web3  
3. Set your RPC endpoint:
   export RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY  

## Usage
Analyze 20 recent blocks (default):
   python app.py

Specify block count:
   python app.py --count 50

Run on another network:
   python app.py --rpc https://arb1.arbitrum.io/rpc --count 25

Output as JSON for CI:
   python app.py --count 15 --json

Change timeout (for slower RPCs):
   python app.py --count 30 --timeout 60

Monitor hourly gas health:
   0 * * * * python /path/to/app.py --count 50 --json >> gashealth.log

## Example Output
🔧 zk-gashealth-soundness  
🔗 RPC: https://mainnet.infura.io/v3/...  
🧱 Analyzing last 20 blocks...  
🕒 Start Time: 2025-11-08T19:44:00Z  

📊 Summary:  
  • Average Utilization: 83.9%  
  • Utilization Range: 62.1% → 97.5%  
  • Average Base Fee: 19.384 Gwei  
  • Soundness Status: ✅ Stable Gas Pattern  
⏱️ Duration: 3.27s  

## Notes
- **Soundness Rule:** The network is considered stable if average utilization > 50% and volatility (max-min) < 40%.  
- **Base Fee Trends:** Helps identify congestion spikes or lull periods relevant for zk-rollup batching.  
- **EVM Compatibility:** Works on any chain supporting `eth_getBlockByNumber`.  
- **Performance Tip:** Use lower `--count` for quick checks; increase for long-term metrics.  
- **JSON Integration:** Combine with dashboards like Grafana or Prometheus for real-time alerts.  
- **Exit Codes:**  
  - `0` → Gas pattern stable (sound)  
  - `2` → High volatility or unsound utilization pattern  
