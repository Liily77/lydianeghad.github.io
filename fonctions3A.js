/*-----------------------------------------
       ECRITURE DYNAMIQUE DES LISTES
------------------------------------------*/


function writeList(id, variable) {
  let select = document.getElementById(id);
  for (let i = 0; i < variable.length; i++) {
      select.innerHTML += `<option value="${i + 1}">${variable[i][id]}</option>`;     
  }
}


/*-----------------------------------------
       MISE A JOUR DU LOCALSTORAGE
------------------------------------------*/


function getLocalStorage() {
try {
    if (localStorage.getItem("expCond") != null) {
        expCond = JSON.parse(localStorage.getItem("expCond"));
    } else {
        expCond = [];
    }
} catch (error) {
    console.error("Error reading from localStorage", error);
    expCond = [];
}
}

function setLocalStorage() {
try {
    localStorage.setItem("expCond", JSON.stringify(expCond));
} catch (error) {
    console.error("Error writing to localStorage", error);
}
}


/*-----------------------------------------
       VALIDATION DU FORMULAIRE
------------------------------------------*/



function verifForm() {
const message = document.getElementById("message"); 
message.innerHTML = ""; 
message.classList.remove("error", "success"); 

let go = true; 
let count = 0; 

// Affichage des messages d'erreurs

let dateDepart = document.getElementById("dateDepart").value;

if (dateDepart === "") {
    message.innerHTML += "La date de départ est requise.<br>";
    count++;
  
} else {
  
  let today = new Date().setHours(0, 0, 0, 0); 
  let inputDate = new Date(dateDepart).setHours(0, 0, 0, 0); 

  if (inputDate > today) {
      message.innerHTML += "<span class='error-message'>La date de départ doit être inférieure ou égale à la date du jour.</span><br>";
      count++;
  }
}

let heureDepart = document.getElementById("heureDepart").value;

if (heureDepart === "") {
    message.innerHTML += "L'heure de départ est requise.<br>";
    count++;
}

let heureArrivee = document.getElementById("heureArrivee").value;

if (heureArrivee === "") {
    message.innerHTML += "L'heure d'arrivée est requise.<br>";
    count++;
}

let distance = document.getElementById("distance").value;

if (distance === "") {
    message.innerHTML += "La distance est requise.<br>";
    count++;
}

let meteo = document.getElementById("meteo").value;

if (meteo === "") {
    message.innerHTML += "La météo est requise.<br>";
    count++;
}

let trafic = document.getElementById("trafic").value;

if (trafic === "") {
    message.innerHTML += "Le trafic est requis.<br>";
    count++;
}

let typeDeRoute = document.getElementById("typederoute").selectedOptions;

if (typeDeRoute.length === 0) {
    message.innerHTML += "Au moins un type de route est requis.<br>";
    count++;
}

let manoeuvre = document.getElementById("manoeuvre").selectedOptions;
if (manoeuvre.length === 0) {
    message.innerHTML += "Au moins une manœuvre est requise.<br>";
    count++;
}

//Condition que HeureDépart > HeureArrivée

if (count > 0) {
  go = false;
  message.classList.add("error"); 
}


if (count === 0 && !verifHeure()) {
  go = false;
  message.innerHTML = "<span class='error-message'>L'heure d'arrivée doit être postérieure à l'heure de départ.</span><br>";
  message.classList.add("error");
}

if (go) {
  message.classList.add("success");
  message.innerHTML = "Formulaire soumis avec succès !";
  ajouter();
}
}


/*----------------------------------------------
       LES FONCTIONS DATE, HEURE et DISTANCE
-----------------------------------------------*/

/* Définitions des fonctions pour vérifier la bonne saisie des heures et minutes */
  
function verifHeure() {

    let heureArrivee = document.getElementById("heureArrivee").value;
    let heureDepart = document.getElementById("heureDepart").value;

    // Fonction pour convertir l'heure au format HH:MM en minutes
    function getMinutes(heure) {
        let [hours, minutes] = heure.split(":");
        return parseInt(hours) * 60 + parseInt(minutes);
    }

    heureArrivee = getMinutes(heureArrivee);
    heureDepart = getMinutes(heureDepart);

    if (heureArrivee > heureDepart) {
        return true;
    } else {
        alert("L'heure d'arrivée doit être postérieure à l'heure de départ !");
        return false;
    }
}

    
/* Définition de la fonction distance (si entier positif > 0)*/
    
function verifDistance() {
let distanceEntree = Number(distance.value);
let errorMessage = 'Distance parcourue (km) <span class="alerte">Veuillez entrer une valeur entière positive supérieure à 0</span>';
let place = document.querySelector("label[for='distance'");

if (Math.sign(distanceEntree) != 1 || Number.isInteger(distanceEntree) == false) {
  distance.value = "";
  place.innerHTML = errorMessage;

} else {
  place.innerHTML = "Distance parcourue (km)";
}
}   



/*----------------------------------------------
         AJOUT D'UNE NOUVELLE EXPERIENCE
-----------------------------------------------*/

function ajouter() {


let experienceSupplementaire = {}; 
  

experienceSupplementaire["idExpCond"] = expCond.length + 1;

experienceSupplementaire["dateDepart"] = document.getElementById("dateDepart").value;
experienceSupplementaire["heureDepart"] = document.getElementById("heureDepart").value;
experienceSupplementaire["heureArrivee"] = document.getElementById("heureArrivee").value;
experienceSupplementaire["distance"] = document.getElementById("distance").value;
experienceSupplementaire["idMeteo"] = document.getElementById("meteo").value;
experienceSupplementaire["idTrafic"] = document.getElementById("trafic").value;
experienceSupplementaire["idAppreciation"] = document.getElementById("appreciation").value;
  

  experienceSupplementaire["idTypederoute"] = [];
  experienceSupplementaire["idManoeuvre"] = [];
  

let typederoute = document.getElementById("typederoute").selectedOptions;

for (let i = 0; i < typederoute.length; i++) {
      experienceSupplementaire["idTypederoute"].push(typederoute[i].value);
    }
  
let manoeuvre = document.getElementById("manoeuvre").selectedOptions;

for (let i = 0; i < manoeuvre.length; i++) {
      experienceSupplementaire["idManoeuvre"].push(manoeuvre[i].value);
    }
  

expCond.push(experienceSupplementaire);
setLocalStorage();
  

remplirTableau(expCond.length - 1);
calculDistance();

afficherStatistiques();

} 
  

  
/*----------------------------------------------
         REMPLISSAGE DU TABLEAU
-----------------------------------------------*/

  function remplirTableau(i) {
    
    const progression = document.getElementById("tableau-progression").getElementsByTagName('tbody')[0];
    let laligne = progression.insertRow();

    let lacellule = laligne.insertCell();
    lacellule.innerHTML = formatterDate(expCond[i]["dateDepart"]);
  
    lacellule = laligne.insertCell();
    lacellule.innerHTML = expCond[i]["heureDepart"];
  
    lacellule = laligne.insertCell();
    lacellule.innerHTML = expCond[i]["heureArrivee"];
  
    lacellule = laligne.insertCell();
    lacellule.innerHTML = expCond[i]["distance"];
  
    lacellule = laligne.insertCell();
    lacellule.innerHTML = "";
    details(meteo, expCond[i]["idMeteo"], "idMeteo", "meteo", "Météo");
    details(trafic, expCond[i]["idTrafic"], "idTrafic", "trafic", "Trafic");
    details(typederoute, expCond[i]["idTypederoute"], "idTypederoute", "typederoute", "Type(s) de route");
    details(manoeuvre, expCond[i]["idManoeuvre"], "idManoeuvre",  "manoeuvre", "Manœuvre(s)");
    details(appreciation, expCond[i]["idAppreciation"], "idAppreciation", "appreciation", "Appréciation");
  
 /* Fonction pour afficher les variables */

 function details(variable, id, idVariable, libelle, nomVariable) {    
  let libelleVariable = "";

  if (Array.isArray(id)) {  
    id.forEach(elem => {
      libelleVariable += variable.find(v => v[idVariable] == elem)[libelle];
      libelleVariable += ", ";
    });
    libelleVariable = libelleVariable.slice(0, -2); 
  } else {
    libelleVariable = variable.find(v => v[idVariable] == id)[libelle];  
  }
    
  lacellule.innerHTML += `<strong>${nomVariable} :</strong> ${libelleVariable}<br>`
}
    
}   
  
  
/* Formattage de la date */

function formatterDate(date) {
  date = new Date(date);
  let d = date.getDate();
  let month = date.getMonth() + 1;
  let year = date.getFullYear();

  d = d < 10 ? '0' + d : d;
  month = month < 10 ? '0' + month : month;

  return `${d}/${month}/${year}`;
}
  

/*----------------------------------------------
         STATISTIQUES
-----------------------------------------------*/

/*Calcul de la distance */

function calculDistance() {
  let distance = 0;
  for (exp of expCond) {
    distance += Number(exp["distance"]);
  }

  let progressElement = document.getElementById("progress");

  if (progressElement) {
    progressElement.value = distance;

  let spanElement = document.querySelector("#progress > span");

  if (spanElement) {
      spanElement.innerHTML = distance;
    } else {
      console.error("Span element not found.");
    }

  let paragraphElement = document.querySelector("#progress + p span");
    if (paragraphElement) {
      paragraphElement.innerHTML = distance;
    } else {
      console.error("Paragraph element not found.");
    }
    
  } else {
    console.error("Progress element not found.");
  }

  
  if (typeof calculDistanceMoyenne === 'function') {
    calculDistanceMoyenne(distance);
  } else {
    console.error("Function calculDistanceMoyenne is not defined.");
  }
}

/* Calcul de la durée totale de toutes les expériences de conduite*/

function calculDureeTotale() {
  let dureeTotaleMinutes = 0;
  for (exp of expCond) {
      let heureDepart = exp["heureDepart"].split(":");
      let heureArrivee = exp["heureArrivee"].split(":");
      
      let dateDepart = new Date();
      dateDepart.setHours(parseInt(heureDepart[0]), parseInt(heureDepart[1]), 0, 0);
      
      let dateArrivee = new Date();
      dateArrivee.setHours(parseInt(heureArrivee[0]), parseInt(heureArrivee[1]), 0, 0);
      
      let difference = dateArrivee.getTime() - dateDepart.getTime();
      dureeTotaleMinutes += difference / (1000 * 60);
  }
  return dureeTotaleMinutes;
}

/* Affichage des statistiques*/

function afficherStatistiques() {
  let distanceTotale = 0;
  let dureeTotaleMinutes = calculDureeTotale();

  for (exp of expCond) {
      distanceTotale += parseInt(exp["distance"]);
  }

  let distanceMoyenne = distanceTotale / expCond.length;

/* Cette mention c'est pour que cela affiche toujours 0 après le reset et non "NaN" */

if (isNaN(distanceMoyenne) || !isFinite(distanceMoyenne)) {
    distanceMoyenne = 0;
}

let dureeTotaleHeuresMinutes = convertirMinutesEnHeuresMinutes(dureeTotaleMinutes);

document.getElementById("distanceMoyenne").textContent = distanceMoyenne.toFixed(2) + " km";
document.getElementById("dureeTotale").textContent = convertirMinutesEnHeuresMinutes(dureeTotaleMinutes);


 const progressElement = document.getElementById("progress");
 if (progressElement) {
     progressElement.value = distanceTotale;

     const spanElement = progressElement.querySelector("span");
     if (spanElement) {
         spanElement.textContent = distanceTotale;
     } else {
         console.error("Span element not found.");
     }

     const paragraphElement = progressElement.nextElementSibling.querySelector("span");
     if (paragraphElement) {
         paragraphElement.textContent = distanceTotale;
     } else {
         console.error("Paragraph element not found.");
     }
 } else {
     console.error("Progress element not found.");
 }
  remplirTableauBilan();

}

function convertirMinutesEnHeuresMinutes(minutes) {
  let heures = Math.floor(minutes / 60);
  let minutesRestantes = minutes % 60;
  return heures + "h " + minutesRestantes + "min";
}

/*----------------------------------------------
        BILAN : COMPTAGE DES VARIABLES
-----------------------------------------------*/

function compterVariables() {
  let counts = {
    meteo: {},
    trafic: {},
    typederoute: {},
    manoeuvre: {},
    appreciation: {}
  };

  expCond.forEach(exp => {
    
    switch (exp.idMeteo) {
      case "1":
        counts.meteo["éclaircies"] = (counts.meteo["éclaircies"] || 0) + 1;
        break;
      case "2":
        counts.meteo["temps clair"] = (counts.meteo["temps clair"] || 0) + 1;
        break;
        case "3":
          counts.meteo["éclaircies"] = (counts.meteo["éclaircies"] || 0) + 1;
          break;
        case "4":
          counts.meteo["pluie"] = (counts.meteo["pluie"] || 0) + 1;
          break;
        case "5":
          counts.meteo["orage"] = (counts.meteo["orage"] || 0) + 1;
          break;
        case "6":
          counts.meteo["neige"] = (counts.meteo["neige"] || 0) + 1;
          break;
        case "7":
          counts.meteo["brouillard"] = (counts.meteo["brouillard"] || 0) + 1;
          break;
        case "8":
          counts.meteo["verglas"] = (counts.meteo["verglas"] || 0) + 1;
          break;
        case "9":
          counts.meteo["temps chaud"] = (counts.meteo["temps chaud"] || 0) + 1;
          break;
        case "10":
          counts.meteo["temps froid"] = (counts.meteo["temps froid"] || 0) + 1;
          break;
        case "11":
          counts.meteo["vent fort"] = (counts.meteo["vent fort"] || 0) + 1;
          break;
    }

   
    switch (exp.idTrafic) {
      case "1":
        counts.trafic["densité élevée"] = (counts.trafic["densité élevée"] || 0) + 1;
        break;
      case "2":
        counts.trafic["densité faible"] = (counts.trafic["densité faible"] || 0) + 1;
        break;
        case "3":
          counts.trafic["densité élevée"] = (counts.trafic["densité élevée"] || 0) + 1;
          break;
    }

    
    exp.idTypederoute.forEach(id => {
      switch (id) {
        case "1":
          counts.typederoute["autoroute"] = (counts.typederoute["autoroute"] || 0) + 1;
          break;
        case "2":
          counts.typederoute["route nationale"] = (counts.typederoute["route nationale"] || 0) + 1;
          break;
          case "3":
            counts.typederoute["départementale"] = (counts.typederoute["départementale"] || 0) + 1;
            break;
          case "4":
            counts.typederoute["nationale"] = (counts.typederoute["nationale"] || 0) + 1;
            break;
          case "5":
            counts.typederoute["autoroute"] = (counts.typederoute["autoroute"] || 0) + 1;
            break;
          case "6":
            counts.typederoute["étranger"] = (counts.typederoute["étranger"] || 0) + 1;
            break;
      }
    });

    
    exp.idManoeuvre.forEach(id => {
      switch (id) {
        case "1":
          counts.manoeuvre["changement de voie"] = (counts.manoeuvre["changement de voie"] || 0) + 1;
          break;
        case "2":
          counts.manoeuvre["dépassement"] = (counts.manoeuvre["dépassement"] || 0) + 1;
          break;
          case "3":
            counts.manoeuvre["parking en épi"] = (counts.manoeuvre["parking en épi"] || 0) + 1;
            break;
          case "4":
            counts.manoeuvre["créneau"] = (counts.manoeuvre["créneau"] || 0) + 1;
            break;
          case "5":
            counts.manoeuvre["demi-tour"] = (counts.manoeuvre["demi-tour"] || 0) + 1;
            break;
      }
    });

 
    switch (exp.idAppreciation) {
      case "1":
        counts.appreciation["très satisfait"] = (counts.appreciation["très satisfait"] || 0) + 1;
        break;
      case "2":
        counts.appreciation["satisfait"] = (counts.appreciation["satisfait"] || 0) + 1;
        break;
        case "3":
          counts.appreciation["difficulté moyenne"] = (counts.appreciation["difficulté moyenne"] || 0) + 1;
          break;
        case "4":
          counts.appreciation["difficile"] = (counts.appreciation["difficile"] || 0) + 1;
          break;
        case "5":
          counts.appreciation["très difficile"] = (counts.appreciation["très difficile"] || 0) + 1;
          break;
    }
  });

  return counts;
}

/*----------------------------------------------
       BILAN : REMPLISSAGE DU TABLEAU
-----------------------------------------------*/

function remplirTableauBilan() {
  const counts = compterVariables();
  const tableauBilan = document.getElementById("tableau-bilan").getElementsByTagName('tbody')[0];
  tableauBilan.innerHTML = "";

  const categories = {
    meteo: "Météo",
    trafic: "Trafic",
    typederoute: "Type de route",
    manoeuvre: "Manœuvre",
    appreciation: "Appréciation"
  };

  for (let category in categories) {
    let total = 0;
    let rowCategory = tableauBilan.insertRow();

    let cellCategory = rowCategory.insertCell();
    cellCategory.colSpan = 3;
    cellCategory.innerHTML = `<strong>${categories[category]}</strong>`;

    for (let variable in counts[category]) {
      let row = tableauBilan.insertRow();
      let cellVariable = row.insertCell();
      let cellCount = row.insertCell();
      cellVariable.innerHTML = variable;
      cellCount.innerHTML = counts[category][variable];
      if (variable === "nombre") {
        cellCount.classList.add("col-nombre");
      }
      total += counts[category][variable];
    }

  }
}


/*----------------------------------------------
                    RESET
-----------------------------------------------*/
function resetApplication() {
  localStorage.removeItem("expCond");
  expCond = [];
  
  const tableauProgression = document.getElementById("tableau-progression");
  tableauProgression.innerHTML = ""; 

  document.getElementById("distanceMoyenne").textContent = "";
  document.getElementById("dureeTotale").textContent = "";

  document.getElementById("dateDepart").value = "";
  document.getElementById("heureDepart").value = "";
  document.getElementById("heureArrivee").value = "";
  document.getElementById("distance").value = "";

  document.getElementById("meteo").selectedIndex = 0;
  document.getElementById("trafic").selectedIndex = 0;
  document.getElementById("typederoute").selectedIndex = 0; 
  document.getElementById("manoeuvre").selectedIndex = 0; 
  document.getElementById("appreciation").selectedIndex = 0;

  writeList("meteo", meteo);
  writeList("trafic", trafic);
  writeList("typederoute", typederoute);
  writeList("manoeuvre", manoeuvre);
  writeList("appreciation", appreciation);

  afficherStatistiques();
}


