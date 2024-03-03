const express = require('express');
const app = express();

const multer = require('multer');
const upload = multer({ dest: 'audio/' });

app.use(express.static("./public/"));

app.get('/', (req, res) => {
  res.sendFile("./public/recorder.js");
});

app.post('/upload', upload.single('recording'), (req, res) => {
  //TODO
});

app.listen(3000, () => {
  console.log("Server is up and running!");
});
