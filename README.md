# Jiakai Tang's academic homepage

Personal academic website for Jiakai Tang (唐嘉凯), hosted at https://tangjiakai.github.io/.

The page is a static, accessible HTML/CSS/JavaScript site. Content works without JavaScript; JavaScript only highlights the current navigation section. No external fonts, trackers, or runtime dependencies are required.

## Update content

- Edit `data/publications.json` for publication titles, authors, venue, year, links, and award badges. Optional `resources` entries contain a `label` and `url`: use the uniform display label `Code` for repository, project, and resource links. Check that the repository matches the paper and is publicly accessible before adding it.
- Edit `data/honors.json` for honors. Chinese award names are retained alongside English translations.
- Edit `scripts/build.py` for the biography, news, experience, education, and service sections.
- Run `python3 scripts/build.py` to regenerate `index.html` and `sitemap.xml`.
- Update the content date in the generator when refreshing the biography or other sections.
- Commit and push to `main`. The publish workflow builds and deploys GitHub Pages.

Publications are grouped by year, newest first. Within a year, awards and first/co-first authorship precede other work, followed by publication status. There are no total-count or author-filter controls. Venue, CCF category, preprint/review status, awards, and oral presentations have separate pill labels. Submission and preprint status must be preserved when editing records.

## Automatic Google Scholar metrics

`.github/workflows/publish.yml` runs after pushes, on demand, and daily at 22:23 UTC (06:23 Singapore/Beijing time). GitHub may delay scheduled runs. It fetches the public profile `7kB-4sEAAAAJ`, validates the profile identity and all-time metrics, saves `data/scholar.json`, builds the page, and deploys it in the same workflow. No Scholar login, paid API, secret, or personal access token is needed at runtime.

The last successful snapshot and timestamp remain unchanged if Scholar returns an error, a challenge, or incomplete data. Such failures produce a workflow warning. The website shows the date of the last successful fetch; it does not claim the numbers are real-time. A failed refresh does not block other site updates. Tests cover parsing, wrong profiles, incomplete responses, and fallback preservation.

Deployment verification on October 23, 2026 found that Scholar was accessible from the owner's computer but refused the GitHub-hosted runner's request. A companion Codex automation therefore refreshes the same snapshot from the owner's computer daily at 06:30 Asia/Singapore, then commits and pushes only successful metric updates. This local fallback requires the computer and Codex to be available. When either source is unavailable, the page continues to show the last successful snapshot and its original date. The cloud workflow still publishes all content changes normally.

GitHub Pages must be configured with **GitHub Actions** as its build source. Deploying in the same workflow is deliberate: commits from `GITHUB_TOKEN` do not trigger another Pages workflow. Only the public site files are included in the deployment artifact.

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/update_scholar.py
python3 scripts/build.py
```

Certificate scans are not published. The additional award titles and dates were transcribed from the owner's supplied certificates; student identifiers and certificate numbers are excluded.

## Local preview

```sh
python3 scripts/build.py
python3 -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765/.

## Design

The organization is inspired by [Changle Qu's academic homepage](https://quchangle1.github.io/): a profile sidebar and a readable sequence of biography, news, publications, honors, education, experience, and service. The implementation and styling here are original; no third-party template code or photographs were copied.

Public-facing academic information and the owner-authorized Chinese CV are included. The CV is available at `assets/Jiakai-Tang-CV.pdf`; replace this file when a new version is supplied. Scholarship forms, award certificates, and recommendation letters are not part of this repository.

## Metric badges

Scholar badges use the existing scheduled snapshot and show its last successful update date; fetching failures retain the previous values. GitHub publication repositories use clickable GitHub icons with accessible Code labels and hover tooltips, without star counters.

## Date sources (checked 2026-10-24)

- RecGPT acceptance: 2026-08-27, from ACM's publication-history assertion deposited with Crossref: https://api.crossref.org/works/10.1145/3846382. Online publication is 2026-10-21; the News entry explicitly describes acceptance.
- ReaRec publication: September 2026, from IEEE's Crossref record: https://api.crossref.org/works/10.1109/TKDE.2026.3694421. The News entry describes publication because the acceptance month is unconfirmed.
- GRIT: December 2026 is the workshop month (https://grit-genir.github.io/workshop-sigir-ap-2026/), explicitly selected by the owner for the award's timeline display.
- CIKM award: October 2022, conference month on https://www.cikmconference.org/2022/best-paper.html.
- Education dates: verified against the owner-supplied CV.
- National Scholarships in 2019–2021: December on all three owner-supplied award certificates. Certificates are not published. December 2026 was explicitly confirmed by the owner on October 24, 2026.
- The 2020 Outstanding Youth League Cadre certificate states the year only; no month is inferred.
- Publication year headings and venue labels intentionally retain year precision; timeline events use months where verified.

### Patents

`data/patents.json` records the seven user-supplied patents. Titles, inventor order, applicants, application numbers and filing dates are transcribed from the CNIPA documents. The three `granted` statuses follow the user-supplied filenames marked 已授权; those PDFs are application publications rather than grant certificates, so no grant date or B publication number is inferred. The four `filed` statuses are supported by application acceptance notices. Filing dates are explicitly labeled in the UI. Source PDFs are not published, and agent contact details, addresses and document serial numbers are excluded.

### Academic service

Maintain `data/service.json` to add workshop editions, open-source projects and reviewing venues. The builder renders dated workshop entries, one entry per software project, and separate conference/journal lists. Roles should describe confirmed contributions only.

### GitHub stars

`scripts/update_github.py` refreshes star counts for repositories linked from publications and open-source service entries using GitHub public repository metadata. The existing daily Pages workflow runs the updater before building. Only counts strictly greater than 30 render a star badge; 30 or fewer and unknown counts remain hidden. Successful decreases below the threshold remove the badge. Failed requests preserve the last verified count and its timestamp. Hover a badge to see its snapshot date. No token is included in public files.
