function showSelectedVideo(input, previewId) {
  const videoPreview = document.getElementById(previewId);
  if (input.files.length > 0) {
    const file = input.files[0];
    videoPreview.src = URL.createObjectURL(file);
    videoPreview.style.display = "block";
  } else {
    videoPreview.src = "";
    videoPreview.style.display = "none";
  }
}

function showSelectedImage(input, previewId) {
  const imagePreview = document.getElementById(previewId);
  if (input.files.length > 0) {
    const file = input.files[0];
    imagePreview.src = URL.createObjectURL(file);
    imagePreview.style.display = "block";
  } else {
    imagePreview.src = "";
    imagePreview.style.display = "none";
  }
}
function showSelectedFile(input, labelId) {
  const fileLabel = document.getElementById(labelId);
  const fileNameSpan = document.getElementById(`${labelId}-name`);

  if (input.files.length > 0) {
    const file = input.files[0];
    fileLabel.innerHTML = `<i class="fas fa-file"></i> ${file.name}`;
    fileNameSpan.textContent = `Selected File: ${file.name}`;
  } else {
    fileLabel.innerHTML = `<i class="fas fa-upload"></i> Choose File`;
    fileNameSpan.textContent = "";
  }
}
function openFile(fileId) {
  const input = document.getElementById(fileId);
  if (input.files.length > 0) {
    const file = input.files[0];

    // Get the file extension
    const extension = file.name.split('.').pop().toLowerCase();

    // Define the supported file types
    const supportedImageTypes = ['jpg', 'jpeg', 'png', 'gif'];
    const supportedVideoTypes = ['mp4', 'avi', 'mov'];
    const supportedPdfTypes = ['pdf'];

    // Check the file type and handle accordingly
    if (supportedImageTypes.includes(extension)) {
      // Display the image
      const imagePreview = document.getElementById('image-preview');
      imagePreview.src = URL.createObjectURL(file);
      imagePreview.style.display = 'block';
    } else if (supportedVideoTypes.includes(extension)) {
      // Display the video
      const videoPreview = document.getElementById('video-preview');
      videoPreview.src = URL.createObjectURL(file);
      videoPreview.style.display = 'block';
    } else if (supportedPdfTypes.includes(extension)) {
      // Open the PDF in a new window or tab
      const fileURL = URL.createObjectURL(file);
      window.open(fileURL);
    } else {
      // Provide a download link for other file types
      const downloadLink = document.createElement('a');
      downloadLink.href = URL.createObjectURL(file);
      downloadLink.download = file.name;
      downloadLink.textContent = 'Download File';
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
    }
  } else {
    alert('No file selected.');
  }
}

