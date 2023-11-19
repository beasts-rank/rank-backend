import os
import time

from rich.prompt import Prompt
from rich.live import Live
from rich.text import Text
from rich.console import Console

from rng_crypto import RNGCrypto
from base64 import b85encode
from pyperclip import copy

console = Console()

seed = int(Prompt.ask("Seed", password=True, default=114514) if not os.getenv("SEED") else os.getenv("SEED"))
name = Prompt.ask("Username")

d = RNGCrypto(seed).encrypt(name.encode())
copy(b85encode(d).decode())

console.print("Copied!", style='blue')

with Live(transient=True) as live:
    live.update(
        Text.assemble(("Your password is ", 'blue'), (b85encode(d).decode(), 'cyan'))
    )
    time.sleep(3)
