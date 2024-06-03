# Setup


- Download vimium
```zsh
sh ./vimit.sh
```

- Kill chrome processes (optional for custom browser)
```
pkill -a -i "Google Chrome"
```

- Begin
```
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
python3 main.py
```