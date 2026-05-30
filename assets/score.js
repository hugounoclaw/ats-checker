// AUTO-GENERATED from the ats-check CLI core (cli/src/score.js).
// DO NOT EDIT BY HAND. Regenerate with `npm run sync-site` in the cli/ dir.
// This is the website's copy of the single source of truth — same algorithm
// the `ats-check` CLI and GitHub Action use, so the site never drifts.

// ats-check shared scoring core — THE single source of truth.
//
// This module is canonical. The website (a separate static repo deployed to
// GitHub Pages) consumes an identical copy at repo/assets/score.js, which is
// generated from THIS file by `npm run sync-site` (see scripts/sync-site.js).
// Edit the algorithm here, then run sync — never edit the site copy by hand.
// `npm run sync-site -- --check` fails if the two have drifted (CI/pre-commit).

export const ACTION = ["led","managed","developed","designed","implemented","created","built","launched","increased","reduced","improved","optimized","delivered","achieved","drove","spearheaded","coordinated","executed","established","generated","negotiated","streamlined","automated","analyzed","architected","scaled","mentored","directed","oversaw","produced","accelerated","transformed","initiated","founded","restructured","consolidated","pioneered","orchestrated","facilitated","resolved","engineered","deployed","migrated","integrated","forecasted","budgeted","audited","secured","expanded","boosted","grew","exceeded","surpassed","owned","shipped","redesigned"];

export const STOP = new Set("a an the and or of to in for with on at by from as is are be we our you your they their this that will can role job work team years experience strong ability skills using etc must have has had who which what when into across over per plus more most all any new other than then them it its".split(/\s+/));

export function tokens(s) {
	// Match word-ish tokens, then strip trailing punctuation (".", "-") that the
	// char class can otherwise leave attached (e.g. "terraform." / "back-end-").
	// Internal/leading dots & hyphens and trailing "+"/"#" are preserved so
	// "node.js", "full-stack", "c++", "c#" survive intact.
	return (s.toLowerCase().match(/[a-z][a-z+#.\-]{1,}/g) || [])
		.map(w => w.replace(/[.\-]+$/, ''))
		.filter(Boolean);
}

// analyze(resumeText, jobDescriptionText?) -> {total, cats, kw, wc}
export function analyze(resume, jd) {
	const text = resume.trim();
	const lower = text.toLowerCase();
	const words = text.split(/\s+/).filter(Boolean);
	const wc = words.length;
	const cats = [];

	// 1 contact (15)
	const hasEmail = /[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}/i.test(text);
	const hasPhone = /(\+?\d[\d\s().\-]{7,}\d)/.test(text);
	const c1 = (hasEmail ? 9 : 0) + (hasPhone ? 6 : 0);
	cats.push({ key: 'Contact info', score: c1, max: 15,
		tips: [!hasEmail && { p: 'hi', t: 'No email detected. Put a plain-text email in the top section (not in a header/footer).' },
			!hasPhone && { p: 'me', t: 'No phone number detected. Add a phone number near your name.' }].filter(Boolean) });

	// 2 sections (20)
	const sec = { Experience: /(work experience|professional experience|employment|experience)/i.test(text),
		Education: /education/i.test(text),
		Skills: /(skills|technical skills|core competencies)/i.test(text) };
	const c2 = (sec.Experience ? 8 : 0) + (sec.Education ? 6 : 0) + (sec.Skills ? 6 : 0);
	cats.push({ key: 'Standard sections', score: c2, max: 20,
		tips: [!sec.Experience && { p: 'hi', t: 'Add a clearly labeled "Experience" or "Work Experience" heading — ATS keys on standard section names.' },
			!sec.Education && { p: 'me', t: 'Add an "Education" section heading.' },
			!sec.Skills && { p: 'me', t: 'Add a "Skills" section so the parser can extract your hard skills.' }].filter(Boolean) });

	// 3 parseability (15) — penalize signals of tables/columns/odd chars
	const tabCols = (text.match(/\t/g) || []).length + (text.match(/ {3,}\S+ {3,}\S/g) || []).length;
	const weird = (text.match(/[^\x00-\x7F]/g) || []).length;
	let c3 = 15;
	if (tabCols > 6) c3 -= 7; else if (tabCols > 2) c3 -= 3;
	if (weird > 25) c3 -= 6; else if (weird > 10) c3 -= 3;
	c3 = Math.max(0, c3);
	cats.push({ key: 'Parse-friendly formatting', score: c3, max: 15,
		tips: [tabCols > 2 && { p: 'hi', t: 'Looks like multi-column or tab-aligned layout. ATS scramble columns/tables — switch to a single-column layout.' },
			weird > 10 && { p: 'me', t: 'Many non-standard characters/symbols detected. Replace fancy bullets/icons with plain text and a hyphen or • bullet.' }].filter(Boolean) });

	// 4 action verbs (15)
	const tks = tokens(lower);
	const setTk = new Set(tks);
	const av = ACTION.filter(v => setTk.has(v)).length;
	const c4 = Math.min(15, Math.round(av / 8 * 15));
	cats.push({ key: 'Action verbs', score: c4, max: 15,
		tips: [av < 8 && { p: 'me', t: 'Start bullets with strong action verbs (Led, Built, Increased, Reduced…). Found ' + av + '; aim for 8+ distinct.' }].filter(Boolean) });

	// 5 quantified impact (15)
	const nums = (text.match(/(\$\s?\d|\d+\s?%|\b\d{2,}\b)/g) || []).length;
	const c5 = Math.min(15, Math.round(nums / 8 * 15));
	cats.push({ key: 'Quantified impact', score: c5, max: 15,
		tips: [nums < 6 && { p: 'hi', t: 'Add numbers to your wins (%, $, headcount, time saved). Recruiters & ATS-ranked resumes show measurable impact. Found ' + nums + ' figures.' }].filter(Boolean) });

	// 6 length (10)
	let c6 = 10, lenTip = null;
	if (wc < 200) { c6 = 3; lenTip = { p: 'me', t: 'Resume looks short (' + wc + ' words). Most strong resumes run 400–800 words.' }; }
	else if (wc < 400) { c6 = 7; lenTip = { p: 'lo', t: 'A bit short (' + wc + ' words) — consider adding measurable bullets.' }; }
	else if (wc > 1100) { c6 = 6; lenTip = { p: 'lo', t: 'Long (' + wc + ' words). Trim to the most relevant 1–2 pages.' }; }
	cats.push({ key: 'Length', score: c6, max: 10, tips: [lenTip].filter(Boolean) });

	// 7 dates (10)
	const dates = (text.match(/((19|20)\d{2})|(\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4})|(\d{1,2}\/\d{4})/gi) || []).length;
	const c7 = dates >= 2 ? 10 : (dates === 1 ? 5 : 0);
	cats.push({ key: 'Dates present', score: c7, max: 10,
		tips: [dates < 2 && { p: 'me', t: 'Add consistent employment dates (e.g., "Jan 2021 – Mar 2024"). ATS use them to build your timeline.' }].filter(Boolean) });

	const total = cats.reduce((a, c) => a + c.score, 0);

	// keyword match vs JD
	let kw = null;
	if (jd && jd.trim().length > 40) {
		const jdTk = tokens(jd).filter(w => w.length > 2 && !STOP.has(w));
		const freq = {};
		jdTk.forEach(w => freq[w] = (freq[w] || 0) + 1);
		let cand = [...new Set(jdTk)].filter(w => freq[w] >= 1);
		cand = cand.filter(w => freq[w] >= 2 || w.length >= 5);
		cand = cand.sort((a, b) => freq[b] - freq[a]).slice(0, 30);
		const hit = cand.filter(w => setTk.has(w));
		const miss = cand.filter(w => !setTk.has(w));
		kw = { pct: cand.length ? Math.round(hit.length / cand.length * 100) : 0, hit, miss };
	}

	return { total, cats, kw, wc };
}
