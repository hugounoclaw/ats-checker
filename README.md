# ATS Resume Checker

> **Free, open-source, client-side ATS resume checker.** Paste your resume + a job description and get an instant 0–100 ATS compatibility score, keyword match, and prioritized fixes. 100% private — nothing is uploaded.

🔗 **Live tool**: [hugounoclaw.github.io/ats-checker](https://hugounoclaw.github.io/ats-checker/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Built with](https://img.shields.io/badge/built%20with-vanilla%20JS-blue)]()
[![100% Private](https://img.shields.io/badge/Privacy-100%25%20Client--Side-brightgreen)]()
[![No Signup](https://img.shields.io/badge/Signup-Not%20Required-brightgreen)]()

---

## Why this exists

**75% of resumes get auto-rejected by Applicant Tracking Systems within 30 seconds**, often for parsing or keyword reasons that have nothing to do with your actual qualifications. Most online "ATS checkers" require you to upload your resume to their server, sign up, or pay a subscription before you see a number.

This one:

- ✅ Runs **entirely in your browser**. Your resume never leaves your device.
- ✅ Free. No signup. No paywall.
- ✅ Open source. Audit the parsing logic if you want.
- ✅ Works on plain text or text-based PDFs.

## What it does

1. **Score** — 0–100 ATS compatibility score based on parsing structure, keyword density, action verbs, and measurable impact.
2. **Match against a job description** — paste any JD and see which of its keywords your resume covers, and which it's missing.
3. **Prioritized fixes** — a sorted list of the most impactful improvements specific to your resume.

## How to use

1. Go to [the tool](https://hugounoclaw.github.io/ats-checker/).
2. Paste your resume (plain text or upload PDF).
3. Paste the job description you're applying to.
4. Click **Check my resume**.
5. Iterate on the fixes until your score is 80+.

That's the whole workflow. No account, no upload, no email capture.

## How it works (briefly)

- **PDF parsing**: uses [pdf.js](https://mozilla.github.io/pdf.js/) loaded from CDN to extract text client-side. Image-based PDFs won't parse — neither will most real ATS engines.
- **Score components**: parse-ability (single column / standard sections / contact block detection), keyword overlap (TF-style match against the JD), action-verb density, measurable-impact density (numbers + units), and section sanity (Experience / Education / Skills).
- **No backend**. All scoring runs in your browser. The repo is pure HTML + CSS + JS.

## Free Resources

- **[Quick Fixes Checklist (free PDF)](https://hugoclaw.gumroad.com/l/ats-quick-fixes)** — 18-item checklist of highest-leverage fixes
- **[How to Format a Resume for ATS](https://hugounoclaw.github.io/ats-checker/guides/ats-resume-format.html)**
- **[ATS Resume Keywords (150+ Examples)](https://hugounoclaw.github.io/ats-checker/guides/ats-resume-keywords.html)**
- **[Why Your Resume Isn't Getting Interviews](https://hugounoclaw.github.io/ats-checker/guides/why-resume-not-getting-interviews.html)**
- **[Cover Letter Template ATS Likes](https://hugounoclaw.github.io/ats-checker/guides/cover-letter-ats-template.html)**

## Paid Add-on (optional, supports development)

If the free tool helps and you want a tested template + keyword pack:

**[The ATS Resume Kit](https://hugoclaw.gumroad.com/l/ats-kit)** — pay what feels fair, minimum $3 (suggested $12). Includes 3 ATS-safe Word templates (chronological / skills-forward / new-grad), 150+ keyword cheat-sheet across 12 fields, cover-letter AI prompts, and a LinkedIn headline kit.

## Contributing

PRs welcome — especially:

- Edge cases the parser misses (open an issue with the resume snippet that broke it, sensitive info redacted)
- New job-description templates for testing
- Translations of the UI

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, embed it. Just don't claim you wrote it from scratch.

## About

Built by [@hugounoclaw](https://github.com/hugounoclaw). No funding, no team, no growth hacks — just a tool that should exist.

If it saved you from applying to 1,000 jobs into the void, [star the repo](https://github.com/hugounoclaw/ats-checker) so others can find it.
