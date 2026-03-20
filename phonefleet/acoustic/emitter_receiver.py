"""
=============================================================
  STEP 1 — Emitter / Receiver automation via SSH

  BEFORE RUNNING — change the 5 lines marked with  ← CHANGE

  Dependencies:  pip install paramiko
  Run with:      python step1_emitter_receiver.py
=============================================================
"""

import paramiko
import time
import os

#  SETTINGS  

PHONE0_IP         = "192.168.43.1"    # ← CHANGE  (Phone 0 IP from: ifconfig in Termux)
PHONE3_IP         = "192.168.43.100"  # ← CHANGE  (Phone 3 IP from: ifconfig in Termux)
SSH_USER_PHONE0   = "u0_a219"         # ← (Phone 0 username from: whoami in Termux)
SSH_USER_PHONE3   = "u0_a236"         # ← (Phone 3 username from: whoami in Termux)
SSH_PASSWORD_BOTH = "turbotice!"      # ← (SSH password, same on both phones)

#  EXPERIMENT SETTINGS  (change later to test different frequencies)

TONE_FREQ     = 1000   # frequency in Hz — try 500, 1000, 2000, 4000 ...
TONE_DURATION = 3      # duration in seconds
RECORD_EXTRA  = 2      # extra seconds recorded after tone ends (captures the tail)
SSH_PORT      = 8022   # Termux default SSH port — same on both phones

LOCAL_OUTPUT  = "rec.wav"   # name of the file saved on your PC after download

#  HELPER — connect to a phone via SSH

def connect(ip, username, label):
    print(f"\n Connecting to {label} ({username}@{ip})...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=SSH_PORT, username=username, password=SSH_PASSWORD_BOTH)
    print(f" Connected to {label}")
    return client

#  HELPER — run a command on a phone

def run(client, command, label=""):
    print(f"\n[{label}] $ {command}")
    stdin, stdout, stderr = client.exec_command(command)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(f"[{label}] → {out}")
    if err:
        print(f"[{label}] ⚠  {err}")
    return out

#  HELPER — build the tone generation command
#  (runs directly on the phone via python3 -c)

def make_tone_command(freq, duration):
    code = (
        f"import math,wave,struct;"
        f"fs=44100;"
        f"wav=wave.open('test.wav','w');"
        f"wav.setnchannels(1);"
        f"wav.setsampwidth(2);"
        f"wav.setframerate(fs);"
        f"[wav.writeframes(struct.pack('<h',int(32767*math.sin(2*math.pi*{freq}*n/fs)))) for n in range(fs*{duration})];"
        f"wav.close();"
        f"print('test.wav created OK')"
    )
    return f"python3 -c '{code}'"

#  MAIN FLOW

def main():

    # 1. Connect to both phones (each with its own username)
    phone0 = connect(PHONE0_IP, SSH_USER_PHONE0, "Phone 0 (emitter)")
    phone3 = connect(PHONE3_IP, SSH_USER_PHONE3, "Phone 3 (receiver)")

    # 2. Generate the tone file on Phone 0
    print(f"\n🎵 Generating {TONE_FREQ} Hz tone ({TONE_DURATION}s) on Phone 0...")
    run(phone0, make_tone_command(TONE_FREQ, TONE_DURATION), label="Phone0")

    # 3. Clean up any old recording on Phone 3
    run(phone3, "rm -f rec.wav", label="Phone3")

    # 4. Start recording on Phone 3 (& = runs in background so script continues)
    print("\n🎙  Starting recording on Phone 3...")
    run(phone3, "termux-microphone-record -f rec.wav &", label="Phone3")
    time.sleep(1)  # wait 1 second to make sure recording has started

    # 5. Play the tone on Phone 0
    print("\n  Playing tone on Phone 0...")
    run(phone0, "termux-media-player play test.wav", label="Phone0")

    # 6. Wait for tone + extra tail
    wait_time = TONE_DURATION + RECORD_EXTRA
    print(f"\n Waiting {wait_time}s for recording to finish...")
    time.sleep(wait_time)

    # 7. Stop recording on Phone 3
    print("\n  Stopping recording on Phone 3...")
    run(phone3, "termux-microphone-record -q", label="Phone3")
    time.sleep(1)  # let the file finish writing to disk

    # 8. Confirm the file exists on Phone 3
    run(phone3, "ls -lh rec.wav", label="Phone3")

    # 9. Download rec.wav from Phone 3 to your PC
    print(f"\n Downloading rec.wav to your PC as '{LOCAL_OUTPUT}'...")
    sftp = phone3.open_sftp()
    sftp.get("rec.wav", LOCAL_OUTPUT)
    sftp.close()
    print(f" Saved to: {os.path.abspath(LOCAL_OUTPUT)}")

    # 10. Close SSH connections
    phone0.close()
    phone3.close()

    print("\n Done!")
    print(f"   rec.wav is ready on your PC.")
    print(f"   Next step: run the FFT analysis script on it.")

# ─────────────────────────────────────────────

if __name__ == "__main__":
    main()