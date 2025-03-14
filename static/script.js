const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const preview = document.getElementById('preview');
const processedImage = document.getElementById('processedImage');
const captureButton = document.getElementById('capture');
const uploadButton = document.getElementById('upload');
const downloadButton = document.getElementById('download');

// Access the webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => { video.srcObject = stream; })
    .catch(err => console.error("Error accessing webcam: ", err));

// Capture Image
captureButton.addEventListener('click', () => {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);
    preview.src = canvas.toDataURL('image/jpeg');
});

// Upload Image
uploadButton.addEventListener('click', () => {
    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append('image', blob, 'book.jpg');

        fetch('/upload', {
            method: 'POST',
            body: formData
        }).then(response => response.json())
          .then(data => {
              alert(data.message);
              
              if (data.pdf_url) {
                  downloadButton.style.display = 'block';
                  downloadButton.onclick = () => window.location.href = data.pdf_url;
              }

              // Display the processed image (if available)
              if (data.processed_image_url) {
                  processedImage.src = data.processed_image_url;
              }
          })
          .catch(err => console.error("Upload error: ", err));
    }, 'image/jpeg');
});
