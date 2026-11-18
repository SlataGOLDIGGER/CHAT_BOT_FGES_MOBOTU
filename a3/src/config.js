// Configuration unique du moteur, partagée par le navigateur et le script d'index (Node).
export const MODELES = {
    pre: { depot: 'Xenova/multilingual-e5-small', revision: '761b726dd34fb83930e26aab4e9ac3899aa1fa78', dtype: 'q8' },
    'pre-export': { depot: 'fges-nlp-a3b1/e5-small-stages-fr', revision: 'b83d0779f1aec650fc2599c5d27f6aa5261cb356', dtype: 'q8' },
    affine: { depot: 'fges-nlp-a3b1/e5-small-stages-fr', revision: 'c01f0c20f6fe63133444903d0ece2e392237bfb2', dtype: 'q8' },
};
export const STRATEGIES = ['section', 'fenetre', 'paragraphe'];
export const PRODUCTION = { modele: 'pre', strategie: 'fenetre' };
export const PREFIXES = { requete: 'query: ', passage: 'passage: ' };
export const DIMENSION = 384;
export const NB_RESULTATS = 5;
export const NB_CLASSEMENT_EVALUATION = 50;
export const SEUIL_PERTINENCE = null;