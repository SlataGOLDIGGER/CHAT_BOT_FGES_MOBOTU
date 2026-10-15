# Essai de faisabilité : encodage dans un Web Worker

Date : 16/10/2026
Commit : 1ce69b1 
Poste : P2 (Windows 11, i5, 8Go RAM, 2,40Ghz) 
Connexion : WiFi (Orange, 810 Mb/s)


| Navigateur (version) | Premier chargement (ms) | Rechargement (ms) | Encodage (ms) | Dimension | Valeurs finies | Norme |
|---|---|---|---|---|---|---|
| Chrome (155.0.8059.40) | 26091 | 1965 | 74 | 384 | `[-0.004933638498187065, -0.027888035401701927, -0.04535611346364021, -0.04295314475893974, 0.039966754615306854]` | 1.0000000690616602 |
| Edge (155.0.1000.97) | 27559 | 2265 | 127 | 384 | `[-0.004933638498187065, -0.027888035401701927, -0.04535611346364021, -0.04295314475893974, 0.039966754615306854]` | 1.0000000690616602 |


- Taille du modèle téléchargé (onglet Réseau, filtre `onnx`) : 118,374kb ~120Mo .
- Moteur d'exécution: fichiers `ort-wasm-…` servis par `unpkg.com` (22,9 Mo).
- Cache : `transformers-cache`, 3 entrées ; le rechargement ne retélécharge pas le modèle.
- Constat : l'exécution dans le navigateur est faisable


- Taille du modèle téléchargé (onglet Réseau, filtre `onnx`) : 118 374 Ko ≈ 118,4 Mo.
- Moteur d'exécution : ONNX Runtime Web avec backend WebAssembly (WASM). Fichiers `ort-wasm-*` servis depuis `unpkg.com` (22,9 Mo).
- Cache : `transformers-cache`, 3 entrées. Le rechargement réutilise le modèle mis en cache sans nouveau téléchargement observé.
- Constat : l'encodage dans un Web Worker est faisable dans le navigateur. Temps d'encodage : 74 ms (Chrome) et 127 ms (Edge).
