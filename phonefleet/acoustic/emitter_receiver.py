import paramiko
import time
import os
from datetime import datetime

# ─── SETTINGS ────────────────────────────────────────────────────────────────

PHONE0_IP         = "10.51.13.31"
PHONE3_IP         = "10.22.212.136"
SSH_USER_PHONE0   = "u0_a219"
SSH_USER_PHONE3   = "u0_a236"
SSH_PASSWORD_BOTH = "turbotice!"

PHONE0_LABEL = "Phone0_emitter"
PHONE3_LABEL = "Phone3_receiver"

TONE_DURATION = 15     # seconds — must match actual WAV length
RECORD_EXTRA  = 3      # extra seconds after tone ends
SSH_PORT      = 8022

LOCAL_TONE  = "Sweep_20Hza48kHz.wav"   # file on your PC
REMOTE_TONE = "Sweep_20Hza48kHz.wav"   # file on Phone 0

OUTPUT_FOLDER = "recordings"

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def make_filename(phone_label):
    """YYYY-MM-DD_HH-MM-SS_<label>.wav"""
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{ts}_{phone_label}.wav"


def connect(ip, username, label):
    print(f"\n Connecting to {label} ({username}@{ip})...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, port=SSH_PORT, username=username,
                       password=SSH_PASSWORD_BOTH, timeout=10)
        print(f" Connected to {label}")
    except Exception as e:
        print(f" ERROR: Could not connect to {label}: {e}")
        exit(1)
    return client


def run(client, command, label=""):
    """Run a command and WAIT for it to finish."""
    print(f"[{label}] $ {command}")
    _, stdout, stderr = client.exec_command(command)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(f"[{label}] {out}")
    if err: print(f"[{label}] STDERR: {err}")
    return out


def run_bg(client, command, label=""):
    """Fire-and-forget: launch command in background, return immediately."""
    wrapped = f"nohup {command} > /dev/null 2>&1 &"
    print(f"[{label}] BG$ {command}")
    client.exec_command(wrapped)


def sftp_upload(client, local_path, remote_path, label=""):
    """Upload a file and verify it arrived with the correct size."""
    local_size = os.path.getsize(local_path)
    print(f"\n[{label}] Uploading '{local_path}'  ({local_size:,} bytes)...")

    if local_size == 0:
        print(f" ERROR: local file is 0 bytes — check '{local_path}'")
        exit(1)

    sftp = client.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()

    # verify on remote
    remote_size_str = run(client, f"wc -c < {remote_path}", label=label).strip()
    try:
        remote_size = int(remote_size_str)
    except ValueError:
        remote_size = 0

    if remote_size == 0:
        print(f"\n ERROR: file arrived as 0 bytes on {label}!")
        print("  → Check free space on the phone:  df -h")
        exit(1)

    print(f"[{label}] Upload OK  ({remote_size:,} bytes on phone)")

# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():

    # 0. Output folder
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print(f"\n Output folder : {os.path.abspath(OUTPUT_FOLDER)}/")

    # 1. Check local WAV exists and is not empty
    abs_tone = os.path.abspath(LOCAL_TONE)
    if not os.path.isfile(abs_tone):
        print(f"\n ERROR: '{abs_tone}' not found.")
        print("  Put the WAV file in the SAME folder as this script.")
        exit(1)
    tone_size = os.path.getsize(abs_tone)
    print(f" Source WAV    : {abs_tone}  ({tone_size:,} bytes)")
    if tone_size == 0:
        print(" ERROR: WAV file on your PC is 0 bytes — file is corrupted.")
        exit(1)

    # 2. Timestamped filename for this session
    rec_remote     = "recorded.wav"
    rec_local      = make_filename(PHONE3_LABEL)
    local_out_path = os.path.join(OUTPUT_FOLDER, rec_local)
    print(f" Will save as  : {rec_local}")

    # 3. Connect
    phone0 = connect(PHONE0_IP, SSH_USER_PHONE0, PHONE0_LABEL)
    phone3 = connect(PHONE3_IP, SSH_USER_PHONE3, PHONE3_LABEL)

    # 4. Upload WAV → Phone 0  (with size check)
    sftp_upload(phone0, abs_tone, REMOTE_TONE, label=PHONE0_LABEL)

    # 5. Clean old recording on Phone 3
    run(phone3, f"rm -f {rec_remote}", label=PHONE3_LABEL)

    # 6. Start recording on Phone 3 in BACKGROUND
    print(f"\n Starting recording on {PHONE3_LABEL}...")
    run_bg(phone3, f"termux-microphone-record -f {rec_remote}", label=PHONE3_LABEL)
    time.sleep(1.5)   # give recorder time to start

    # 7. Play tone on Phone 0 in BACKGROUND  ← KEY FIX (was blocking before)
    print(f"\n Playing '{REMOTE_TONE}' on {PHONE0_LABEL}...")
    run_bg(phone0, f"termux-media-player play {REMOTE_TONE}", label=PHONE0_LABEL)

    # 8. Countdown while tone plays + extra tail
    wait_time = TONE_DURATION + RECORD_EXTRA
    print(f"\n Waiting {wait_time}s  ({TONE_DURATION}s tone + {RECORD_EXTRA}s tail)...")
    elapsed = 0
    step    = 5
    while elapsed < wait_time:
        chunk = min(step, wait_time - elapsed)
        time.sleep(chunk)
        elapsed += chunk
        print(f"   {elapsed}/{wait_time}s ...")

    # 9. Stop recording
    print(f"\n Stopping recording on {PHONE3_LABEL}...")
    run(phone3, "termux-microphone-record -q", label=PHONE3_LABEL)
    time.sleep(1.5)

    # 10. Confirm file on Phone 3
    run(phone3, f"ls -lh {rec_remote}", label=PHONE3_LABEL)

    # 11. Download → PC  (timestamped filename)
    print(f"\n Downloading  {rec_remote}  →  {local_out_path}")
    sftp3 = phone3.open_sftp()
    sftp3.get(rec_remote, local_out_path)
    sftp3.close()
    saved_size = os.path.getsize(local_out_path)
    print(f" Saved : {os.path.abspath(local_out_path)}  ({saved_size:,} bytes)")

    # 12. Append to CSV log
    log_path   = os.path.join(OUTPUT_FOLDER, "experiment_log.csv")
    log_exists = os.path.isfile(log_path)
    with open(log_path, "a") as log:
        if not log_exists:
            log.write("date,time,phone_label,phone_ip,ssh_user,"
                      "tone_file,duration_s,file_size_bytes,filename\n")
        now = datetime.now()
        log.write(
            f"{now.strftime('%Y-%m-%d')},"
            
            f"{now.strftime('%H:%M:%S')},"
            f"{PHONE3_LABEL},{PHONE3_IP},{SSH_USER_PHONE3},"
            f"{LOCAL_TONE},{TONE_DURATION + RECORD_EXTRA},"
            f"{saved_size},{rec_local}\n"
        )
    print(f" Log : {os.path.abspath(log_path)}")

    # 13. Close
    phone0.close()
    phone3.close()

    print(f"\n Done!")
    print(f"  Recording : {local_out_path}")
    print(f"  Log       : {log_path}")
    print("  Next step: run the FFT analysis script on it.")

if __name__ == "__main__":
    main()