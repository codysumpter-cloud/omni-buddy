> # ⚠️ This repository is archived and superseded
>
> **omni-buddy has been consolidated into [codysumpter-cloud/prismtek-apps](https://github.com/codysumpter-cloud/prismtek-apps).**
>
> Canonical location: **`packages/omni-adapters and services/omni-buddy`**
>
> - Migration record: [`docs/migrations/omni-buddy.yaml`](https://github.com/codysumpter-cloud/prismtek-apps/blob/main/docs/migrations/omni-buddy.yaml)
> - Consolidation tracker: [prismtek-apps#359](https://github.com/codysumpter-cloud/prismtek-apps/issues/359)
> - prismtek-apps revision at archive time: `f47023186c67e649378734ee80a158a022dbb941`
>
> This repository is kept read-only for history, provenance, issues, and
> releases. Its full commit history was imported into prismtek-apps with
> original authorship preserved, so the commits below also exist there.
> **Do not open new work here.** The tag `pre-archive-final` marks the exact
> final state of the default branch.

# Be More Agent 🤖
**A Customizable, Offline-First AI Agent for Raspberry Pi**

[![Watch the Demo](https://img.youtube.com/vi/l5ggH-YhuAw/maxresdefault.jpg)](https://youtu.be/l5ggH-YhuAw)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red) ![License](https://img.shields.io/badge/License-MIT-green)

This project turns a Raspberry Pi into a fully functional, conversational AI agent. Unlike cloud-based assistants, this agent runs **100% locally** on your device. It listens for a wake word, processes speech, "thinks" using a local Large Language Model (LLM), and speaks back with a low-latency neural voice—all while displaying reactive face animations.

**It is designed as a blank canvas:** You can easily swap the face images and sound effects to create your own character!

## ✨ Features

* **100% Local Intelligence**: Powered by **Ollama** (LLM) and **Whisper.cpp** (Speech-to-Text). No API fees, no cloud data usage.
* **Open Source Wake Word**: Wakes up to your custom model using **OpenWakeWord** (Offline & Free). No access keys required.
* **Hardware-Aware Audio**: Automatically detects your microphone's sample rate and resamples audio on the fly to prevent ALSA errors.
* **Smart Web Search**: Uses DuckDuckGo to find real-time news and information when the LLM doesn't know the answer.
* **Reactive Faces**: The GUI updates the character's face based on its state (Listening, Thinking, Speaking, Idle).
* **Fast Text-to-Speech**: Uses **Piper TTS** for low-latency, high-quality voice generation on the Pi.
* **Vision Capable**: Can "see" and describe the world using a connected camera and the **Moondream** vision model.

## 🛠️ Hardware Requirements

* **Raspberry Pi 5** (Recommended) or Pi 4 (4GB RAM minimum)
* USB Microphone & Speaker
* LCD Screen (DSI or HDMI)
* Raspberry Pi Camera Module

---

## 📂 Project Structure

```text
be-more-agent/
├── agent.py                   # The main brain script
├── setup.sh                   # Auto-installer script
├── wakeword.onnx              # OpenWakeWord model (The "Ear")
├── config.json                # User settings (Models, Prompt, Hardware)
├── chat_memory.json           # Conversation history
├── requirements.txt           # Python dependencies
├── whisper.cpp/               # Speech-to-Text engine
├── piper/                     # Piper TTS engine & voice models
├── sounds/                    # Sound effects folder
│   ├── greeting_sounds/       # Startup .wav files
│   ├── thinking_sounds/       # Looping .wav files
│   ├── ack_sounds/            # "I heard you" .wav files
│   └── error_sounds/          # Error/Confusion .wav files
└── faces/                     # Face images folder
    ├── idle/                  # .png sequence for idle state
    ├── listening/             # .png sequence for listening
    ├── thinking/              # .png sequence for thinking
    ├── speaking/              # .png sequence for speaking
    ├── error/                 # .png sequence for errors
    └── warmup/                # .png sequence for startup
```

---

## 🚀 Installation

### 1. Prerequisites
Ensure your Raspberry Pi OS is up to date.
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git -y
```

### 2. Install Ollama
This agent relies on [Ollama](https://ollama.com) to run the brain.
```bash
curl -fsSL https://ollama.com/install.sh| sh
```
*Pull the required models:*
```bash
ollama pull gemma:2b
ollama pull moondream
```

### 3. Clone & Setup
```bash
git clone https://github.com/brenpoly/be-more-agent.git
cd be-more-agent
chmod +x setup.sh
./setup.sh
```
*The setup script will install system libraries, create necessary folders, download Piper TTS, and set up the Python virtual environment.*

### 4. Configure the Wake Word
The setup script downloads a default wake word ("Hey Jarvis"). To use your own:
1. Train a model at [OpenWakeWord](https://github.com/dscripka/openWakeWord).
2. Place the `.onnx` file in the root folder.
3. Rename it to `wakeword.onnx`.

### 5. Run the Agent
```bash
source venv/bin/activate
python agent.py
```

---

## 📂 Configuration (`config.json`)

You can modify the hardware behavior and personality in `config.json`. The `agent.py` script creates this on the first run if it doesn't exist, but you can create it manually:

```json
{
    "text_model": "gemma3:1b",
    "vision_model": "moondream",
    "voice_model": "piper/en_GB-semaine-medium.onnx",
    "chat_memory": true,
    "camera_rotation": 0,
    "system_prompt_extras": "You are a helpful robot assistant. Keep responses short and cute.",
    "llm_backend": "omni",
    "omni_base_url": "http://127.0.0.1:8799/api/omni",
    "omni_token_env": "PRISMBOT_API_TOKEN",
    "omni_model": "omni-core:phase2",
    "omni_tool_route_mode": "hybrid",
    "omni_stream_chunk_chars": 48,
    "omni_fallback_to_ollama": true,
    "omni_request_timeout_sec": 90,
    "omni_vision_mode": "hybrid"
}
```

Omni-specific knobs:
- `omni_tool_route_mode`: `off|hybrid|direct`
  - `hybrid` = direct route obvious tool intents (time/search/camera), fallback to JSON-action parsing
  - `direct` = strongest bias toward direct routing
- `omni_stream_chunk_chars`: pseudo-stream chunk size for non-stream Omni replies
- `omni_fallback_to_ollama`: if Omni endpoint errors/timeouts, auto-fallback to local Ollama
- `omni_request_timeout_sec`: Omni HTTP timeout
- `omni_vision_mode`: `local|hybrid`
  - `hybrid` = get local vision caption, then answer with Omni text model

Transport knobs (Milestone G/H/J/K):
- `transport_mode`: `online|mesh|reticulum_fallback|auto`
- `mesh_health_check_url`: URL used to detect mesh path health
- `reticulum_bridge_endpoint`: HTTP bridge endpoint for Reticulum relay integration
- `reticulum_bridge_token_env`: env var name for optional bridge bearer token
- `transport_failover_timeout_sec`: timeout budget for transport health checks

Milestone K local bridge mock (for testing):

```bash
python3 adapters/reticulum_bridge_mock.py --host 127.0.0.1 --port 8788
./scripts/test_reticulum_bridge.sh http://127.0.0.1:8788/bridge
```

Reticulum bridge response contract (recommended):

```json
{ "text": "..." }
```

Accepted keys are `text`, `message`, or `result.text`.

Runtime controls (Milestone H):
- Hotkeys:
  - `F6` cycle transport override (`auto -> online -> mesh -> reticulum_fallback`)
  - `F7` run transport doctor summary
- Voice/text commands:
  - `transport` or `/transport` (status)
  - `transport auto|online|mesh|reticulum_fallback` (override)
  - `/doctor` or `/net-doctor` (diagnostics)

Latency / wake / barge-in knobs:
- `wake_word_threshold`
- `ptt_toggle_debounce_sec`
- `adaptive_pre_record_sec`
- `ptt_pre_record_sec`
- `silence_threshold`
- `silence_duration_sec`
- `max_record_time_sec`
- `tts_tail_sec`
- `thinking_sound_initial_delay_sec`

If `llm_backend` is `omni`, export your token env before running:

```bash
export PRISMBOT_API_TOKEN="<your_token>"
```

---

## 🎨 Customizing Your Character

This software is a generic framework. You can give it a new personality by replacing the assets:

1.  **Faces:** The script looks for PNG sequences in `faces/[state]/`. It will loop through all images found in the folder.
2.  **Sounds:** Put multiple `.wav` files in the `sounds/[category]/` folders. The robot will pick one at random each time (e.g., different "thinking" hums or "error" buzzes).

---

## 🚀 BMO × Omni Ops Quickstart

Install K.3.1 dependency bundle (Pi/Ubuntu):

```bash
./scripts/install_k3_deps.sh
```

Run health checks:

```bash
./scripts/bmo_omni_doctor.sh
```

Run validation matrix static checks:

```bash
./scripts/run_validation_matrix.sh
```

Apply runtime profile presets:

```bash
python3 ./scripts/apply_runtime_profile.py dev
python3 ./scripts/apply_runtime_profile.py pi-live
python3 ./scripts/apply_runtime_profile.py field
```

Apply a latency profile:

```bash
python3 ./scripts/apply_latency_profile.py snappy   # snappy|balanced|robust
```

Launch with helper:

```bash
./scripts/bmo_omni_launch.sh
```

Systemd (user) install:

```bash
mkdir -p ~/.config/systemd/user
cp deploy/bmo-omni-agent.service ~/.config/systemd/user/
cp deploy/bmo-omni.env.example ~/.config/bmo-omni.env
# edit token in ~/.config/bmo-omni.env
systemctl --user daemon-reload
systemctl --user enable --now bmo-omni-agent.service
```

See: `docs/BMO_OMNI_UPGRADE_PLAN.md` for milestone roadmap and guardrails.
See: `docs/COMMS_LAYER_PLAN.md` for mesh/Reticulum resilience roadmap.
See: `docs/VALIDATION_MATRIX.md` for release/stability checks.
See: `docs/ATAK_INTEGRATION_PLAN.md` for ATAK bridge roadmap.
See: `docs/OPENMANET_UPSTREAM.md` for upstream tracking policy and repo map.
See: `docs/K3_1_INTERACTIVE_REPORT.md` and `docs/K4_OPERATOR_RUNBOOK.md` for execution/handoff.

## 🧠 Learn-First (before shell build)

We are intentionally in a learning-first phase before any enclosure work.

- Follow: `docs/LEARNING_FIRST_CHECKLIST.md`
- Architecture notes: `OMNI_INTEGRATION_MAP.md`

Upstream sync commands:

```bash
git fetch upstream main
git log --oneline upstream/main..HEAD   # our additions
git log --oneline HEAD..upstream/main   # upstream changes not yet merged
```

## ⚠️ Troubleshooting

* **"No search library found":** If web search fails, ensure you are in the virtual environment and `duckduckgo-search` is installed via pip.
* **Shutdown Errors:** When you exit the script (Ctrl+C), you might see `Expression 'alsa_snd_pcm_mmap_begin' failed`. **This is normal.** It just means the audio stream was cut off mid-sample. It does not affect the functionality.
* **Audio Glitches:** If the voice sounds fast or slow, the script attempts to auto-detect sample rates. Ensure your `config.json` points to a valid `.onnx` voice model in the `piper/` folder.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## ⚖️ Legal Disclaimer
**"BMO"** and **"Adventure Time"** are trademarks of **Cartoon Network** (Warner Bros. Discovery).

This project is a **fan creation** built for educational and hobbyist purposes only. It is **not** affiliated with, endorsed by, or connected to Cartoon Network or the official Adventure Time brand in any way. The software provided here is a generic agent framework; users are responsible for the assets they load into it.
