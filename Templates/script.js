// Example: Adding a project to the list
const projectList = document.getElementById('project-list');
const form = document.querySelector('form');

form.addEventListener('submit', (event) => {
    event.preventDefault();

    const projectName = document.getElementById('project-name').value;
    const startDate = document.getElementById('start-date').value;
    const dueDate = document.getElementById('due-date').value;

    const listItem = document.createElement('li');
    listItem.textContent = `${projectName} (Start: ${startDate}, Due: ${dueDate})`;
    projectList.appendChild(listItem);

    form.reset();
});