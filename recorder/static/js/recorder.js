const mic_btn = document.querySelector("#mic-btn");
const playback = document.querySelector(".audio-playback");

mic_btn.addEventListener('click', toggleMic);

let recorder;
let chunks = [];

let can_record = false;
let is_recording = false;

function setup() {
  console.log("setup!")
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices
      .getUserMedia({
        audio: true
      })
      .then(setupStream)
      .catch(err => {
        console.error(err);
      });
  }
}

async function sendAudio(audioBlob) {
  const formData = new FormData();
  dt = new Date();
  formData.append("audio", audioBlob, `recording-${dt.now()}.wav`);

  try {
    const response = await fetch('/upload', {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();
    console.log(data);
  } catch (error) {
    console.log("Error: ", error);
  }
}

function setupStream(stream) {
  recorder = new MediaRecorder(stream);

  recorder.ondataavailable = e => {
    chunks.push(e.data);
  }

  recorder.onstop = async e => {
    const blob = new Blob(chunks, { type: "audio/wav; codecs=opus" });  // Set to ogg and opus for now
    chunks = [];
    const audioUrl = window.URL.createObjectURL(blob);
    playback.src = audioUrl;
    await sendAudio(blob);
  }

  can_record = true;
}

function toggleMic() {
  if (!can_record) return;

  is_recording = !is_recording;

  if (is_recording) {
    recorder.start();
    mic_btn.textContent = "Stop Recording";
  } else {
    recorder.stop();
    mic_btn.textContent = "Start Recording";
  }
}

setup();
