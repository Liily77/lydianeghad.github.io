// src/utils/panier.js

const PANIER_KEY = 'mon_panier_arc_en_ciel';

export function getPanier() {
  const panier = localStorage.getItem(PANIER_KEY);
  return panier ? JSON.parse(panier) : [];
}

function signalerChangementPanier() {
  window.dispatchEvent(new Event('maj-panier'));
}

export function savePanier(panier) {
  localStorage.setItem(PANIER_KEY, JSON.stringify(panier));
  signalerChangementPanier();
}

export function ajouterAuPanier(produit, quantite = 1) {
  const panier = getPanier();
  const produitId = produit._id || produit.id;
  const existant = panier.find(p => (p._id || p.id) === produitId);

  if (existant) {
    existant.quantite += quantite;
  } else {
    const produitAjoute = {
      id: produitId,
      nom: produit.nom,
      description: produit.description,
      prix: produit.prix,
      categorie: produit.categorie,
      images: produit.images || [],
      quantite
    };
    panier.push(produitAjoute);
  }

  savePanier(panier);
}

export function retirerProduit(id) {
  let panier = getPanier();
  panier = panier.filter(p => (p.id !== id && p._id !== id));
  savePanier(panier);
}

export function modifierQuantite(id, delta) {
  const panier = getPanier();
  const produit = panier.find(p => p.id === id || p._id === id);
  if (produit) {
    produit.quantite += delta;
    if (produit.quantite <= 0) {
      return retirerProduit(id);
    }
    savePanier(panier);
  }
}

export function viderPanier() {
  localStorage.removeItem(PANIER_KEY);
  signalerChangementPanier();
}

export function getTotalQuantite() {
  const panier = getPanier();
  return panier.reduce((total, p) => total + (p.quantite || 0), 0);
}
