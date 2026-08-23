# Synthèse de dépôt — Sentinelle 974

> Document de synthèse (2 pages max) à adapter au formulaire du dispositif retenu.

---

## 1. Identité du projet

| Champ | Valeur |
|---|---|
| Nom | Sentinelle 974 |
| Porteur | Mozy — `[statut : EI / micro-entreprise / SASU à préciser]` |
| Localisation | Saint-Pierre, La Réunion (974) |
| Contact | ismael.pelicot@gmail.com |
| Durée | 8 semaines (MVP) + 12 mois d'exploitation |
| Budget total | 24 000 € HT |
| Subvention demandée | `[60-80% selon dispositif]` |

## 2. Résumé (5 lignes)

Sentinelle 974 est une plateforme **self-hosted** qui donne aux PME et collectivités
réunionnaises une vision claire de leur cybersécurité et de leurs flux de données :
inventaire des services, audit CVE, cartographie des flux sortants (hors UE / hors 974),
score de conformité et rapport lisible. **Tout tourne en local** — aucune donnée ne
quitte l'île, ce qui garantit la conformité RGPD et la résilience en cas de coupure
des câbles sous-marins ou de cyclone.

## 3. Alignement avec la filière numérique 2026-2028

- **Cybersécurité** : détection et remédiation défensive en continu.
- **Souveraineté des données** : 100% local, aucun cloud étranger.
- **Résilience** : fonctionne hors-ligne, indépendant des infrastructures externes.
- **Emploi local** : solution conçue et maintenue à La Réunion.

## 4. État d'avancement (preuve de faisabilité)

Le MVP est **déjà fonctionnel** (voir démonstration sur demande) :

- API FastAPI (10 endpoints) + dashboard + rapport PDF ;
- Module CVE (Debian Security Tracker + NVD + APT) — 423 vulnérabilités détectées
  sur une machine de test réelle ;
- Géolocalisation locale (MaxMind) des destinations réseau ;
- Agent IA local (Ollama) d'explication des findings, en français/créole ;
- Packaging (install.sh) + durcissement AppArmor + cron ;
- Tests automatisés (13 tests) + CI GitHub Actions.

## 5. Livrables du financement

| Semaine | Livrable |
|---|---|
| 1-2 | Squelette technique ✅ |
| 3 | Module CVE ✅ |
| 4 | Géolocalisation locale ✅ |
| 5-6 | Dashboard + agent IA ✅ |
| 7 | Rapport PDF + alertes ✅ |
| 8 | Packaging + démo client ✅ (à valider avec le pilote) |

## 6. Impact attendu

- 10 PME / collectivités équipées la première année (objectif conservateur).
- Données maintenues à La Réunion — conformité RGPD démontrable.
- Continuité d'activité en cas de coupure câble / cyclone.
- Montée en compétence locale (outil auditable, pas une boîte noire).

## 7. Budget

Voir `budget-previsionnel.xlsx` (24 000 € HT, détail des postes).

---

*À compléter : statut juridique, taux de subvention réel, devis matériel, lettre
d'intention signée du client pilote.*
