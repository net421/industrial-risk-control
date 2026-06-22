# Ubuntu Setup

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip build-essential tmux jq ripgrep
git clone https://github.com/net421/industrial-risk-control.git
cd industrial-risk-control
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
bash scripts/run_local_ci.sh
```

Use `tmux` or systemd for long manual runs. Do not expose notebooks or inbound
services. Keep credentials outside the repository.
