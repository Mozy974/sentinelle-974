# Sentinelle 974 — Pitch & Business Model

> Offre PME / collectivités de La Réunion. Souveraineté des données + posture cyber,
> 100% self-hosted. Aucune donnée métier ne quitte l'île (ni le LAN).

---

## 1. Le problème (pourquoi maintenant)

- **Dépendance cloud US** : les PME 974 envoient leurs données (compta, clients, santé)
  vers des SaaS hébergés hors UE, sans visibilité sur ce qui sort réellement de la machine.
- **Coupure câble / cyclone** : La Réunion dépend de câbles sous-marins (SAFE, METISS, LION).
  Une coupure = SaaS inaccessibles = activité à l'arrêt. Le local continue de tourner.
- **RGPD** : transfert hors UE non maîtrisé = risque de sanction (jusqu'à 4% du CA).
- **Contrat de filière numérique 2026-2028** : cybersécurité + souveraineté des données
  sont **explicitement financés** pour les PME et collectivités réunionnaises.
  → C'est le moment où le budget existe.

## 2. La solution

**Sentinelle 974** = une boîte (ou un serveur) installée chez le client qui :

1. **Inventorie** ce qui tourne (Docker, services, ports, Ollama, bases).
2. **Audite** la posture (CVE, AppArmor, SSH, pare-feu, paquets à jour).
3. **Cartographie** ce qui sort vraiment (DNS, SNI, IPs hors UE / hors 974).
4. **Score** la conformité souveraineté (A→F) avec des règles claires :
   « aucun LLM cloud », « aucune télémétrie ».
5. **Explique** chaque finding en français (et créole) via un agent IA **100% local** (Ollama).
6. **Produit un rapport** PDF/Markdown pour le dirigeant, l'auditeur, la mairie.

**Différenciateur clé** : la donnée ne sort pas. C'est le seul argument qui compte
pour une mairie ou un cabinet médical.

## 3. Cibles

| Segment | Douleur | Offre |
|---|---|---|
| TPE (salon, garage, cabinet) | « je ne sais pas ce qui sort de mon PC » | Audit + rapport 1 page |
| PME (10-50 salariés) | conformité RGPD + dépendance SaaS | Sentinelle installée + suivi mensuel |
| Collectivités (mairies, CCAS) | souveraineté + résilience cyclone | Déploiement flotte + formation |
| Admin sys / ESN locales | flottes Debian à auditer | Licence blanche / marque blanche |

## 4. Pricing (3 offres)

| Offre | Prix / mois | Contenu |
|---|---|---|
| **Audit ponctuel** | 490 € (one-shot) | Scan complet + rapport + 1h de restitution |
| **Sentinelle Standard** | 149 € / mois | Boîte installée, scans quotidiens, score, rapport mensuel, alertes |
| **Sentinelle Collectivité** | 590 € / mois | Flotte (jusqu'à 20 machines), dashboard multi-sites, formation, support prioritaire |

> **Modèle** : matériel (mini-PC ~300 €) + abonnement logiciel. Marge récurrente sur
> l'abonnement, pas sur le hardware. Le financement filière 2026-2028 peut couvrir
> l'installation initiale pour les collectivités.

## 5. Roadmap 8 semaines (MVP)

| Semaine | Livrable |
|---|---|
| 1-2 | Squelette : Compose + FastAPI + agent + AppArmor ✅ (fait) |
| 3 | Module CVE : NVD + changelogs APT, export CSV, mode `--quiet` cron |
| 4 | Module souveraineté : GeoIP local (base MaxMind), carte des destinations |
| 5-6 | Dashboard HTMX (inventaire, score, findings) + agent IA local (Ollama) |
| 7 | Rapport PDF/Markdown + alertes (Telegram/email) |
| 8 | Hardening final, packaging (install.sh), démo client + pitch |

## 6. Ce qu'on ne fait pas

- ❌ Aucun exploit, PoC d'attaque, payload — détection + hardening uniquement.
- ❌ Aucun stockage cloud, aucune télémétrie de notre part.
- ❌ Aucune dépendance à une API US (l'IA est Ollama local).

## 7. Pitch 30 secondes

> « Vos données partent aux États-Unis sans que vous le sachiez. Sentinelle 974
> s'installe chez vous, vous montre exactement ce qui sort de vos machines, et vous
> aide à tout garder à La Réunion — conforme RGPD, résilient en cas de cyclone, et
> financé par le contrat de filière numérique 2026-2028. »

## 8. Prochaines actions concrètes

1. Brancher le module CVE (NVD + APT) — semaine 3.
2. Ajouter GeoIP local (base MaxMind gratuite) pour classer `other` → `eu/us/cn/ru`.
3. Dashboard HTMX minimal (semaine 5).
4. Rédiger le dossier de financement filière numérique (dossier de subvention).
5. Premier client pilote : une mairie ou un cabinet médical volontaire.
