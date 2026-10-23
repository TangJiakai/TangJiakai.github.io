# Jiakai Tang's academic homepage

Personal academic website for Jiakai Tang (唐嘉凯), hosted at https://tangjiakai.github.io/.

The page is a static, accessible HTML/CSS/JavaScript site. It works without JavaScript; JavaScript adds publication search and author filters. No external fonts, trackers, or runtime dependencies are required.

## Update content

- Edit `data/publications.json` for publication titles, authors, venue, year, links, and award badges.
- Edit `scripts/build.py` for the biography, news, experience, education, and service sections.
- Run `python3 scripts/build.py` to regenerate `index.html` and `sitemap.xml`.
- Update the date in the generator and scholarly metrics when refreshing the page.
- Commit the generated files and push to `main`. GitHub Pages publishes from the repository root.

Publication ordering prioritizes awards, then research papers over workshop organization papers, first/co-first authorship, and recent years. Published/accepted papers precede preprints within the same year and authorship group. All publications appear by default. Submission and preprint status must be preserved when editing records.

## Local preview

```sh
python3 scripts/build.py
python3 -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765/.

## Design

The organization is inspired by [Changle Qu's academic homepage](https://quchangle1.github.io/): a profile sidebar and a readable sequence of biography, news, publications, honors, education, experience, and service. The implementation and styling here are original; no third-party template code or photographs were copied.

Only public-facing academic information is included. Scholarship forms, recommendation letters, personal telephone numbers, birth date, and signatures are not part of this repository.
