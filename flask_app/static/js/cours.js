
// Fonction pour créer un cours
function showInput() {
    
    let addDiv = document.getElementById('+');
    if (addDiv)
        addDiv.remove();
    
    document.getElementById('inputField').style.display = 'block';
    document.getElementById('inputField').focus();  // Focus on input
}

function handleEnter(event) {
    if (event.key === 'Enter') {
        var enteredText = document.getElementById('inputField').value;

        // Send the entered text to Flask through AJAX
        fetch('/create_cours', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: enteredText })
        }) 
        .then(() => {
            // Optionally clear the input field after submitting
            document.getElementById('inputField').value = '';

            // Retirer l'input
            document.getElementById('inputField').style.display = "none";

            // Rechargement de la page après la création du cours dans la bdd
            loadCourses("personnel");
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
}


function loadCourses(category) {
    fetch(`/get_courses?category=${category}`)
        .then(response => response.json())
        .then(courses => {
           
            let contentDiv = document.getElementById("coursContainer");
            contentDiv.innerHTML = ""; // Clear existing content

            if (courses.length === 0 && category != "personnel") {
                contentDiv.innerHTML = "<p>Aucun cours disponible.</p>";
            } 
            else {
                let baseUrl = document.getElementById("coursContainer").dataset.url; // Get Jinja2 URL
                courses.forEach(course => {
                    let courseUrl = baseUrl.replace("0", course.course_id); // Replace ID in URL
                    
                    let courseItem = `
                    <div class="cours">
                        <a class="linkCours" href="${courseUrl}">
                            <div class="titrecours">
                                <h3>${course.name}</h3>
                            </div>
                        </a>
                    </div>`;
                    
                    

                    contentDiv.innerHTML += courseItem;
                });
                // Ajouter la div de création de cours si la catégorie est personnel
               if (category == "personnel"){

                    contentDiv.innerHTML += ` 
                    <div class="cours">
                        <div class="titrecours" onclick="showInput()">
                            <h3 id ="+" style="font-weight: 600;">+</h3>
                            <input id="inputField" style="display: none;" onkeydown="handleEnter(event)">
                        </div>
                    </div>`;
                }
            }
        })
        .catch(error => console.error("Error fetching courses:", error));
}


