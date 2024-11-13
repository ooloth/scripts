import re
import subprocess
import time
from datetime import datetime

from common.sendgrid import send_email

# Configuration
PING_SERVER = "8.8.8.8"
PING_COUNT = 10
SLEEP_INTERVAL = 60  # in seconds
LOG_FILE = "internet/ping_log.txt"
THRESHOLD = 20  # Packet loss percentage threshold
EMAIL_SUBJECT = "Internet Connection Alert: Packet Loss Detected"


def ping_server(server: str, count: int) -> str:
    """Ping the server and return the output."""
    result = subprocess.run(["ping", "-c", str(count), server], capture_output=True, text=True)
    return result.stdout


def extract_packet_loss(ping_output: str) -> int:
    """Extract packet loss percentage from ping output."""
    match = re.search(r"(\d+)% packet loss", ping_output)
    if match:
        return int(match.group(1))
    return 0


def log_ping_result(ping_output: str):
    """Log the ping result to a file."""
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{datetime.now()}\n")
        log_file.write(ping_output)
        log_file.write("\n")


def main():
    while True:
        ping_output = ping_server(PING_SERVER, PING_COUNT)
        log_ping_result(ping_output)

        packet_loss = extract_packet_loss(ping_output)
        if packet_loss >= THRESHOLD:
            send_email(EMAIL_SUBJECT, f"<pre>{ping_output}</pre>")

        time.sleep(SLEEP_INTERVAL)


if __name__ == "__main__":
    main()
