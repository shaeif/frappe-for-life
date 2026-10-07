// Copies self-hosted fonts and builds the icon sprite into labqubit/public.
// Runs as part of `yarn build` / `yarn dev`, so `bench build` and Docker builds get it too.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const pub = path.join(root, "labqubit", "public");
const nm = path.join(root, "node_modules");

// Fonts: only the subsets the site uses (Latin + Latin-ext for Inter, Arabic for Plex)
const fonts = [
	["@fontsource-variable/inter/files/inter-latin-wght-normal.woff2", "inter-latin.woff2"],
	["@fontsource-variable/inter/files/inter-latin-ext-wght-normal.woff2", "inter-latin-ext.woff2"],
	...[400, 500, 600, 700].map((w) => [
		`@fontsource/ibm-plex-sans-arabic/files/ibm-plex-sans-arabic-arabic-${w}-normal.woff2`,
		`plex-arabic-${w}.woff2`,
	]),
];
fs.mkdirSync(path.join(pub, "fonts"), { recursive: true });
for (const [src, dest] of fonts) fs.copyFileSync(path.join(nm, src), path.join(pub, "fonts", dest));

// Icons: editor-selectable list + every icon("name") used in templates and Python
const names = new Set(JSON.parse(fs.readFileSync(path.join(root, "styles", "icons.json"))).selectable);
const iconCall = /icon\(\s*["']([a-z0-9-]+)["']/g;
(function scan(dir) {
	for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
		const p = path.join(dir, entry.name);
		if (entry.isDirectory()) {
			if (!["node_modules", "public", "__pycache__"].includes(entry.name)) scan(p);
		} else if (/\.(html|py|js)$/.test(entry.name)) {
			for (const m of fs.readFileSync(p, "utf8").matchAll(iconCall)) names.add(m[1]);
		}
	}
})(path.join(root, "labqubit"));

const symbols = [];
for (const name of [...names].sort()) {
	const custom = path.join(root, "styles", "icons", `${name}.svg`);
	const lucide = path.join(nm, "lucide-static", "icons", `${name}.svg`);
	const file = fs.existsSync(custom) ? custom : lucide;
	if (!fs.existsSync(file)) throw new Error(`Unknown icon "${name}" (not in lucide-static or styles/icons)`);
	const svg = fs.readFileSync(file, "utf8");
	const inner = svg.slice(svg.indexOf(">", svg.indexOf("<svg")) + 1, svg.lastIndexOf("</svg>"));
	symbols.push(`<symbol id="${name}" viewBox="0 0 24 24">${inner.replace(/\s+/g, " ").trim()}</symbol>`);
}
fs.mkdirSync(path.join(pub, "icons"), { recursive: true });
fs.writeFileSync(
	path.join(pub, "icons", "sprite.svg"),
	`<!-- Lucide icons, ISC License, https://lucide.dev/license -->\n<svg xmlns="http://www.w3.org/2000/svg">${symbols.join("")}</svg>\n`,
);
console.log(`vendor-assets: ${fonts.length} fonts, ${symbols.length} icons`);
