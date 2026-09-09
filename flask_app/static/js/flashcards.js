
// Fonction pour ajouter une ligne de vocab dans la bdd et l'afficher
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("form-ajout");
    const tableBody = document.getElementById("table-cours").querySelector("tbody");

    // ➕ On récupère le course_id depuis l'URL
    const pathParts = window.location.pathname.split("/");
    const course_id = pathParts[pathParts.length - 1];

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const vocabulaire = document.getElementById("vocabulaire").value;
        const traduction = document.getElementById("traduction").value;
        const description = document.getElementById("description-vocab").value;

        const response = await fetch("/add_vocabulaire", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                vocabulaire: vocabulaire,
                traduction: traduction,
                description: description,
                course_id: parseInt(course_id)
            })
        });

        if (response.ok) {
            const data = await response.json();

            const newRow = document.createElement("tr");
            newRow.dataset.courseId = course_id;
            newRow.dataset.vocabulaire = data.vocabulaire;

            newRow.innerHTML = `
                <td>${data.vocabulaire}</td>
                <td>${data.traduction}</td>
                <td>${data.description || 'Aucune'}</td>
                <td class="action-cell">
                    <button class="delete-btn-row">Supprimer</button>
                </td>
            `;

            // Ajoute la ligne dans le tbody
            tableBody.appendChild(newRow);

            // Active le bouton supprimer pour cette nouvelle ligne
            const deleteBtn = newRow.querySelector(".delete-btn-row");
            deleteBtn.addEventListener("click", async () => {
                const confirmDelete = confirm(`Supprimer le vocabulaire : ${data.vocabulaire} ?`);
                if (!confirmDelete) return;

                const res = await fetch("/delete_vocabulaire", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        items: [{ course_id: course_id, vocabulaire: data.vocabulaire }]
                    })
                });

                if (res.ok) {
                    newRow.remove();
                } else {
                    alert("Erreur lors de la suppression.");
                }
            });

            form.reset();
        } else {
            alert("Erreur lors de l'ajout du vocabulaire.");
        }
    });
});



document.addEventListener("DOMContentLoaded", () => {
    const editBtn = document.getElementById("edit-btn");
    
    if (editBtn){ // Si la modification est possible (section mes cours)

        const finishBtn = document.getElementById("finish-btn");
        const formAjout = document.getElementById("form-ajout");
        const shareBtn = document.getElementById("share-btn");
        
        // Affiche les boutons de suppression
        editBtn.addEventListener("click", () => {
            formAjout.style.display = "block";
            document.querySelectorAll(".action-col").forEach(col => col.style.display = "");
            document.querySelectorAll(".action-cell").forEach(cell => cell.style.display = "");
            editBtn.style.display = "none";
            shareBtn.style.display = "inline-block";
            finishBtn.style.display = "inline-block";
        });

        // Cache les boutons de suppression
        finishBtn.addEventListener("click", () => {
            formAjout.style.display = "none";
            document.querySelectorAll(".action-col").forEach(col => col.style.display = "none");
            document.querySelectorAll(".action-cell").forEach(cell => cell.style.display = "none");
            editBtn.style.display = "inline-block";
            shareBtn.style.display = "none";
            finishBtn.style.display = "none";
        });
    }

    // Suppression d'une ligne
    document.querySelectorAll(".delete-btn-row").forEach(button => {
        button.addEventListener("click", async function () {
            const row = this.closest("tr");
            const course_id = row.dataset.courseId;
            const vocabulaire = row.dataset.vocabulaire;

            const confirmDelete = confirm(`Supprimer le vocabulaire : ${vocabulaire} ?`);
            if (!confirmDelete) return;

            const response = await fetch("/delete_vocabulaire", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    items: [{ course_id, vocabulaire }]
                })
            });

            if (response.ok) {
                row.remove();
            } else {
                alert("Erreur lors de la suppression.");
            }
        });
    });
});


// Fonction pour supprimer tout le cours
document.addEventListener("DOMContentLoaded", () => {
    
    let deleteBtn = document.getElementById("delete-cours-btn");

    if (deleteBtn) {

        // Récupération de course_id dans l'URL
        const pathParts = window.location.pathname.split("/");
        const course_id = pathParts[pathParts.length - 1];
 
        deleteBtn.addEventListener("click", async () => {
            const confirmDelete = confirm("Supprimer le cours complet ?");
            if (!confirmDelete) return;
            
            console.log(course_id);
            const res = await fetch("/delete_cours", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ course_id: course_id })
            });

            if (res.ok) {
                return;// loadCourses("personnel");
            } else {
                alert("Erreur lors de la suppression");
            }
        });
    }
});

// Fonction pour partager le cours
document.addEventListener("DOMContentLoaded", () => {
    
    let shareBtn = document.getElementById("share-btn");

    if (shareBtn) {

        // Récupération de course_id dans l'URL
        const pathParts = window.location.pathname.split("/");
        const course_id = pathParts[pathParts.length - 1];
 
        shareBtn.addEventListener("click", async () => {
            const confirmDelete = confirm("Partager le cours ?");
            if (!confirmDelete) return;
            
            console.log(course_id);
            const res = await fetch("/share_cours", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ course_id: course_id })
            });

            if (res.ok) {
                return;
            } else {
                alert("Erreur lors du partage");
            }
        });
    }
});

// Fonction pour rendre le cours privé
document.addEventListener("DOMContentLoaded", () => {
    
    let unshareBtn = document.getElementById("unshare-btn");

    if (unshareBtn) {

        // Récupération de course_id dans l'URL
        const pathParts = window.location.pathname.split("/");
        const course_id = pathParts[pathParts.length - 1];
 
        unshareBtn.addEventListener("click", async () => {
            const confirmDelete = confirm("Vérouiller le cours ?");
            if (!confirmDelete) return;
            
            console.log(course_id);
            const res = await fetch("/unshare_cours", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ course_id: course_id })
            });

            if (res.ok) {
                return;
            } else {
                alert("Erreur lors du Vérouillage");
            }
        });
    }
});
