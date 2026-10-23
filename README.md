# Jiakai Tang's academic homepage

Personal academic website for Jiakai Tang (唐嘉凯), hosted at https://tangjiakai.github.io/.

The page is a static, accessible HTML/CSS/JavaScript site. Content works without JavaScript; JavaScript only highlights the current navigation section. No external fonts, trackers, or runtime dependencies are required.

## Update content

- Edit `data/publications.json` for publication titles, authors, venue, year, links, and award badges.
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

Only public-facing academic information is included. Scholarship forms, recommendation letters, personal telephone numbers, birth date, and signatures are not part of this repository.
