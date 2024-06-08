document.addEventListener("DOMContentLoaded", function () {
    const parentMenuItems = document.querySelectorAll(".sidebar-menu li");

    parentMenuItems.forEach((menuItem) => {
        menuItem.addEventListener("click", function () {
            const subMenu = this.querySelector("ul");
            if (subMenu) {
                subMenu.classList.toggle("active");
            }
        });
    });
});
const input = document.getElementById('address');

input.addEventListener('input', function() {
  this.style.height = 'auto';
  this.style.height = (this.scrollHeight) + 'px';
});

function filterTasks() {
    var input = document.getElementById("taskSearch");
    var filter = input.value.toLowerCase();
    var table = document.querySelector("table");
    var rows = table.querySelectorAll("tbody tr");

    rows.forEach(function(row) {
        var taskIdCell = row.querySelector("td[data-label='Task ID']");
        if (taskIdCell) {
            var taskId = taskIdCell.textContent.toLowerCase();
            if (taskId.indexOf(filter) > -1) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        }
    });
}

