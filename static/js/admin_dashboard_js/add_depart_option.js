const selectElement = document.querySelector('.department-select');
const contentElements = document.querySelectorAll('.content');

selectElement.addEventListener('change', () => {
  const selectedValue = selectElement.value;

  // Hide all content elements
  contentElements.forEach(content => {
    content.style.display = 'none';
  });

  // Show the selected content
  if (selectedValue) {
    const selectedContent = document.getElementById(`content-${selectedValue}`);
    if (selectedContent) {
      selectedContent.style.display = 'block';
    }
  }
});