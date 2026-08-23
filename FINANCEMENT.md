# Dossier de financement — Sentinelle 974

> **Contrat de filière numérique 2026-2028 — La Réunion**
> Axe : cybersécurité + souveraineté des données (PME & collectivités)
>
> ⚠️ **À vérifier avant dépôt** : les montants, taux d'intervention et pièces
> justificatives exacts dépendent de l'appel à projets réel (Région Réunion /
> ADIR / French Tech Réunion / BPI). Ce dossier fournit la structure et les
> arguments ; adapter les chiffres au règlement en vigueur.

---

## 1. Fiche projet

| Champ | Valeur |
|---|---|
| **Nom du projet** | Sentinelle 974 — plateforme souveraine de cybersécurité & souveraineté des données |
| **Porteur** | Mozy (indépendant, Saint-Pierre 974) |
| **Statut** | Micro-entreprise / EI (à préciser) |
| **Durée** | 8 semaines (MVP) + 12 mois d'exploitation |
| **Budget total** | 24 000 € (voir §5) |
| **Subvention demandée** | 60-80% selon dispositif |
| **Territoire** | La Réunion (974) |

## 2. Contexte & problème

La Réunion dépend de **câbles sous-marins** (SAFE, METISS, LION) pour l'essentiel
de ses services numériques. Conséquences :

1. **Dépendance cloud US** : les PME et collectivités envoient leurs données
   (compta, santé, état-civil) vers des SaaS hébergés hors UE, sans visibilité
   sur ce qui sort réellement de leurs machines.
2. **Résilience** : une coupure de câble (cyclone, avarie) met à l'arrêt les
   services hébergés hors de l'île. Le local continue de tourner.
3. **RGPD** : transfert hors UE non maîtrisé = risque de sanction (jusqu'à 4% du CA).
4. **Manque d'offre locale** : peu d'acteurs réunionnais proposent une solution
   de souveraineté clé-en-main, auditable, en français/créole.

## 3. Solution proposée

**Sentinelle 974** = une solution **100% self-hosted** installée chez le client :

- **Inventaire** des services locaux (Docker, systemd, ports, Ollama, bases).
- **Audit CVE** (Debian Security Tracker + NVD + APT) avec export CSV.
- **Cartographie des flux** sortants (DNS, SNI, IPs hors UE / hors 974).
- **Score de conformité** (A→F) sur des règles claires : « aucun LLM cloud »,
  « aucune télémétrie ».
- **Agent IA local** (Ollama) qui explique chaque finding en français/créole.
- **Rapport** PDF/Markdown pour le dirigeant, l'auditeur, la mairie.

**Différenciateur** : la donnée ne sort pas. C'est l'argument décisif pour une
mairie ou un cabinet médical.

## 4. Alignement avec le contrat de filière 2026-2028

| Objectif du contrat | Contribution de Sentinelle 974 |
|---|---|
| Cybersécurité des PME | Audit continu, détection, remédiation défensive |
| Souveraineté des données | 100% local, aucune donnée hors de l'île |
| Résilience (cyclone/câble) | Fonctionne hors-ligne, indépendant du cloud |
| Emploi local / filière | Solution conçue et maintenue à La Réunion |
| Inclusion (créole) | Agent IA bilingue FR/créole |

## 5. Budget prévisionnel (8 semaines MVP)

| Poste | Montant | Détail |
|---|---|---|
| Développement (8 semaines) | 16 000 € | 200 €/jour × 80 jours |
| Matériel de test (mini-PC × 2) | 1 200 € | 600 €/unité |
| Licences / bases (MaxMind, etc.) | 400 € | GeoLite2 gratuite + divers |
| Hébergement / infra de test | 800 € | VPS local / NAS |
| Communication & démo client | 1 600 € | maquette, démo, dossier |
| **Sous-total** | **20 000 €** | |
| Imprévus (20%) | 4 000 € | |
| **TOTAL** | **24 000 €** | |

## 6. Livrables & jalons

| Semaine | Livrable | Vérifiable |
|---|---|---|
| 1-2 | Squelette (Compose + API + agent + AppArmor) | ✅ **fait** |
| 3 | Module CVE (NVD + Debian tracker + CSV) | ✅ **fait** (423 CVE détectées sur Kali) |
| 4 | GeoIP local + carte des destinations | ✅ **fait** (classement eu/us/cn/ru) |
| 5-6 | Dashboard + agent IA local | ✅ dashboard **fait** |
| 7 | Rapport PDF + alertes | à faire |
| 8 | Packaging + démo client pilote | à faire |

> **Preuve de faisabilité** : le MVP tourne déjà. Le squelette, le module CVE,
> le GeoIP et le dashboard sont fonctionnels et testés sur une machine Kali/Debian
> réelle (4630 paquets audités, 423 CVE détectées, score de conformité calculé).

## 7. Impact attendu

- **10 PME / collectivités équipées** la première année (objectif conservateur).
- **Données maintenues à La Réunion** : conformité RGPD démontrable.
- **Résilience** : continuité d'activité en cas de coupure câble.
- **Montée en compétence locale** : un outil auditable, pas une boîte noire.

## 8. Pièces à joindre (checklist)

- [ ] Kbis / statut du porteur
- [ ] RIB
- [ ] Devis matériel (mini-PC)
- [ ] Démonstration / capture du MVP (fournie sur demande)
- [ ] Lettre d'intention d'un client pilote (mairie / cabinet médical)
- [ ] Attestation sur l'honneur (régularité fiscale et sociale)

## 9. Prochaines actions

1. Identifier le **bon dispositif** : Région Réunion, ADIR, French Tech Réunion,
   BPI (prêt d'honneur / subvention innovation), ou appel à projets filière.
2. Obtenir le **règlement exact** (taux, plafond, éligibilité EI/micro).
3. Trouver **1 client pilote** (mairie ou cabinet médical volontaire) pour la
   lettre d'intention.
4. Finaliser le **budget** avec devis réels.
5. Déposer le dossier.

---

## 10. Dispositifs concrets (à vérifier — liste indicative)

⚠️ **Les intitulés, montants et conditions évoluent. Vérifier chaque lien avant dépôt.**

### Région Réunion — Contrat de filière numérique 2026-2028
- **Cible** : PME, collectivités, associations du numérique réunionnais.
- **Axe** : cybersécurité, souveraineté des données, cloud de confiance.
- **Action** : contacter le service « Filière Numérique » de la Région Réunion
  (ou la Technopole de La Réunion) pour le règlement exact et les guichets.
- **Doc** : https://www.regionreunion.com (rechercher « filière numérique »).

### ADIR — Association pour le Développement Industriel de La Réunion
- **Cible** : porteurs de projets innovants (dont le numérique).
- **Action** : accompagnement au montage du dossier + mise en relation financeurs.
- **Doc** : https://www.adir.re

### French Tech La Réunion
- **Cible** : startups et scale-ups (label, réseau, mentorat).
- **Action** : intégrer le réseau pour la visibilité et l'accès aux dispositifs.
- **Doc** : https://lafrenchtech-lareunion.com

### Bpifrance
- **Dispositifs possibles** :
  - **Bourse French Tech** (subvention, jusqu'à ~30-90 k€ selon les éditions).
  - **Prêt d'honneur** via Initiative Réunion / Réseau Entreprendre.
  - **Aide à l'innovation** (subvention + avance récupérable).
- **Doc** : https://www.bpifrance.fr

### FEDER / Europe (2021-2027)
- **Cible** : projets de transformation numérique des PME et collectivités.
- **Action** : via la Région Réunion (autorité de gestion FEDER).
- **Doc** : https://www.regionreunion.com (rubrique « fonds européens »).

### Checklist de dépôt (selon le dispositif)
- [ ] Statut juridique à jour (EI / micro-entreprise / SASU).
- [ ] RIB + attestations fiscales et sociales.
- [ ] Business plan court (PITCH.md + FINANCEMENT.md).
- [ ] Devis matériel (mini-PC, licences).
- [ ] Lettre d'intention d'un client pilote.
- [ ] Démo fonctionnelle (dashboard + rapport PDF + capture).

> **Conseil** : commencer par l'ADIR ou la French Tech La Réunion — ce sont les
> portes d'entrée locales qui orientent vers le bon guichet et aident à la
> rédaction du dossier.
