// Configuration unique du moteur, partagée par le navigateur et le script d'index (Node).
export const MODELES = {
    pre: { depot: 'Xenova/multilingual-e5-small', revision: '761b726dd34fb83930e26aab4e9ac3899aa1fa78', dtype: 'q8' },
};
export const STRATEGIES = ['section', 'fenetre', 'paragraphe'];
export const PRODUCTION = { modele: 'pre', strategie: 'fenetre' };
export const PREFIXES = { requete: 'query: ', passage: 'passage: ' };
export const DIMENSION = 384;
export const NB_RESULTATS = 5;
export const NB_CLASSEMENT_EVALUATION = 50;
export const SEUIL_PERTINENCE = null;