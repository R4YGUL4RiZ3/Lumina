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
      .catch.catch(err => {
        console.error(err);
      });
  }
}
setup();

function setupStream(stream) {
  recorder = new MediaRecorder(stream);

  recorder.ondataavailable = e => {
    chunks.push(e.data);
  }

  recorder.onstop = e => {
    const blob = new Blob(chunks, { type: "audio/ogg; codecs=opus" });  // Set to ogg and opus for now
    chunks = [];
    const audioUrl = window.URL.createObjectURL(blob);
    playback.src = audioUrl;
  }

  can_record = true;
}

function toggleMic() {
  if (!can_record) return;

  is_recording = !is_recording;

  if (is_recording) {
    recorder.start();
    // mic_btn.classList.add("is-recording");
  } else {
    recorder.stop();
    // mic_btn.classList.remove("is-recording");
  }
}
