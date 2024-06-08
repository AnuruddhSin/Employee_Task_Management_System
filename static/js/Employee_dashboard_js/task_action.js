
document.addEventListener("DOMContentLoaded", function () {
    const taskForm = document.getElementById("taskForm");
    const taskTableBody = document.getElementById("taskTableBody");
  
    taskForm.addEventListener("submit", function (event) {
      event.preventDefault();
  
      const taskName = event.target.querySelector('[name="taskName"]').value;
      const workDuration = event.target.querySelector('[name="workDuration"]').value;
      const progress = event.target.querySelector('[name="progress"]').value;
      const status = event.target.querySelector('[name="status"]').value;
      const issues = event.target.querySelector('[name="issues"]').value;
  
      const newRow = `
        <tr>
          <td data-label="Task Name">${taskName}</td>
          <td>${workDuration}</td>
          <td>${progress}</td>
          <td>${status}</td>
          <td>${issues}</td>
        </tr>
      `;
  
      taskTableBody.insertAdjacentHTML("beforeend", newRow);
  
      // Reset form fields
      event.target.reset();
    });
  });
  