# app.py
import os
import sys
import json
import time
import argparse
from datetime import datetime
from typing import Dict, Any
from web3 import Web3

DEFAULT_RPC = os.environ.get("RPC_URL", "https://mainnet.infura.io/v3/YOUR_INFURA_KEY")

def fetch_block_metrics(w3: Web3, block_id: int) -> Dict[str, Any]:
    """Fetch key metrics for a block."""
    block = w3.eth.get_block(block_id)
    tx_count = len(block.transactions)
    gas_used = block.gasUsed
    gas_limit = block.gasLimit
    utilization = round((gas_used / gas_limit) * 100, 2) if gas_limit else 0
    base_fee = block.get("baseFeePerGas", 0)
    return {
        "number": block.number,
        "timestamp": datetime.utcfromtimestamp(block.timestamp).isoformat() + "Z",
        "tx_count": tx_count,
        "gas_used": gas_used,
        "gas_limit": gas_limit,
        "utilization_percent": utilization,
        "base_fee_gwei": round(base_fee / 1e9, 3),
    }

def analyze_chain_health(w3: Web3, block_count: int) -> Dict[str, Any]:
    """Analyze last N blocks for gas trends and utilization soundness."""
    latest = w3.eth.block_number
    blocks = []
    print(f"📡 Fetching {block_count} recent blocks (from {latest - block_count + 1} to {latest})...")
    start_time = time.time()
    for i, num in enumerate(range(latest - block_count + 1, latest + 1), start=1):
        print(f"🔍 Analyzing block {num} ({i}/{block_count})...")
        metrics = fetch_block_metrics(w3, num)
        blocks.append(metrics)
    elapsed = round(time.time() - start_time, 2)

    utilizations = [b["utilization_percent"] for b in blocks]
    avg_util = round(sum(utilizations) / len(utilizations), 2)
    max_util = max(utilizations)
    min_util = min(utilizations)
    avg_base_fee = round(sum(b["base_fee_gwei"] for b in blocks) / len(blocks), 3)
    sound = avg_util > 50 and (max_util - min_util) < 40

    return {
        "block_count": block_count,
        "average_utilization_percent": avg_util,
        "max_utilization_percent": max_util,
        "min_utilization_percent": min_util,
        "average_base_fee_gwei": avg_base_fee,
        "soundness_ok": sound,
        "analyzed_blocks": blocks,
        "elapsed_seconds": elapsed,
    }

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="zk-gashealth-soundness — analyze recent blocks for gas utilization stability and base fee consistency."
    )
    p.add_argument("--rpc", default=DEFAULT_RPC, help="RPC URL (default: env RPC_URL or Infura key)")
    p.add_argument("--count", type=int, default=20, help="Number of recent blocks to analyze (default: 20)")
    p.add_argument("--timeout", type=int, default=30, help="RPC timeout seconds (default: 30)")
    p.add_argument("--json", action="store_true", help="Output results in JSON format")
    return p.parse_args()

def main() -> None:
    args = parse_args()

    if not args.rpc.startswith(("http://", "https://")):
        print("❌ Invalid RPC URL format.")
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(args.rpc, request_kwargs={"timeout": args.timeout}))
    if not w3.is_connected():
        print("❌ Failed to connect to RPC. Check your endpoint or API key.")
        sys.exit(1)

    print("🔧 zk-gashealth-soundness")
    print(f"🔗 RPC: {args.rpc}")
    print(f"🧱 Analyzing last {args.count} blocks...")
    print(f"🕒 Start Time: {datetime.utcnow().isoformat()}Z")

    try:
        result = analyze_chain_health(w3, args.count)
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(2)

    print("\n📊 Summary:")
    print(f"  • Average Utilization: {result['average_utilization_percent']}%")
    print(f"  • Utilization Range: {result['min_utilization_percent']}% → {result['max_utilization_percent']}%")
    print(f"  • Average Base Fee: {result['average_base_fee_gwei']} Gwei")
    status = "✅ Stable Gas Pattern" if result["soundness_ok"] else "⚠️ Unstable Gas Behavior"
    print(f"  • Soundness Status: {status}")
     # ✅ New: Add a visual bar for average gas utilization
    avg_util = result['average_utilization_percent']
    filled_blocks = int(avg_util / 5)  # 20 total segments
    bar = "█" * filled_blocks + "-" * (20 - filled_blocks)
    print(f"  • Utilization Bar: |{bar}| ({avg_util:.1f}%)")
    print(f"⏱️ Duration: {result['elapsed_seconds']}s")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    sys.exit(0 if result["soundness_ok"] else 2)

if __name__ == "__main__":
    main()
