document.addEventListener("DOMContentLoaded", function () {
    let availableFields = document.getElementById("availableFields");
    let selectedFields = document.getElementById("selectedFields");
    let searchAvailable = document.getElementById("searchAvailable");
    let searchSelected = document.getElementById("searchSelected");
    let saveReportBtn = document.getElementById("saveReport");

    let fieldData = {};  // Список всех доступных полей

    // ✅ Загружаем список всех полей из JSON
    fetch("/static/report_fields.json")
        .then(response => response.json())
        .then(data => {
            fieldData = data;
            loadFields();
        });

    // ✅ Загружаем активные поля из отчёта
    function loadFields() {
        availableFields.innerHTML = "";
        selectedFields.innerHTML = "";

        let reportFields = JSON.parse(selectedFields.dataset.fields || "[]");

        for (let field in fieldData) {
            if (reportFields.includes(field)) {
                addSelectedField(field, fieldData[field]); // Активные поля
            } else {
                addAvailableField(field, fieldData[field]); // Доступные поля
            }
        }
    }

    // ✅ Добавить поле в доступные
    function addAvailableField(field, description) {
        let listItem = document.createElement("li");
        listItem.classList.add("list-group-item", "draggable", "d-flex", "justify-content-between", "align-items-center");
        listItem.dataset.value = field;
        listItem.innerHTML = `
            <div class="d-flex align-items-center">
                <span class="field-text">${field}</span>
                <span class="info-btn ms-1" data-bs-toggle="tooltip" title="${description}">❓</span>
            </div>
            <button type="button" class="btn btn-sm btn-primary move-to-selected">➡</button>
        `;
        availableFields.appendChild(listItem);
    }

    // ✅ Добавить поле в список отчёта
    function addSelectedField(field, description) {
        let listItem = document.createElement("li");
        listItem.classList.add("list-group-item", "active-field", "draggable", "d-flex", "justify-content-between", "align-items-center");
        listItem.dataset.value = field;
        listItem.innerHTML = `
            <div class="d-flex align-items-center">
                <span class="field-text">${field}</span>
                <span class="info-btn ms-1" data-bs-toggle="tooltip" title="${description}">❓</span>
            </div>
            <button type="button" class="btn btn-sm btn-danger remove-field">✖</button>
        `;
        selectedFields.appendChild(listItem);
    }

    // ✅ Перемещение через кнопки
    document.addEventListener("click", function (event) {
        let listItem = event.target.closest("li");
        if (!listItem) return;

        if (event.target.classList.contains("move-to-selected")) {
            addSelectedField(listItem.dataset.value, listItem.querySelector(".info-btn").title);
            listItem.remove();
        }

        if (event.target.classList.contains("remove-field")) {
            addAvailableField(listItem.dataset.value, listItem.querySelector(".info-btn").title);
            listItem.remove();
        }

        updateIcons();
    });

    // ✅ Drag-and-Drop (изменение иконки при перемещении)
    new Sortable(availableFields, {
        group: "fields",
        animation: 150,
        onEnd: function () {
            updateIcons();
        }
    });

    new Sortable(selectedFields, {
        group: "fields",
        animation: 150,
        onEnd: function () {
            updateIcons();
        }
    });

    // ✅ Обновляем иконки после перемещения
    function updateIcons() {
        document.querySelectorAll("#availableFields .move-to-selected").forEach(btn => {
            btn.classList.remove("btn-danger");
            btn.classList.add("btn-primary");
            btn.innerHTML = "➡";
        });

        document.querySelectorAll("#selectedFields .remove-field").forEach(btn => {
            btn.classList.remove("btn-primary");
            btn.classList.add("btn-danger");
            btn.innerHTML = "✖";
        });
    }
});
