#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the GRAIN ROT fan wiki static site.

Reads grain_rot_site_info.json + keywords.json, emits:
  site/index.html        (home)
  site/inner/*.html      (19 inner pages, one per keyword)
  site/sitemap.xml
  site/robots.txt
  GA4 + canonical injected into every page.

Per the ShengCaiYouShu "AI product (overseas - hot-word game site)" manual:
  - L4: fill pages with real researched info; one keyword per inner page;
        title 40-60 chars, meta description 140-160 chars, ~1200 words,
        H2 sub-sections, lead with the direct answer, never fabricate.
  - L5: static sites still need sitemap.xml + robots.txt + GA4 tracking;
        GSC verification + sitemap submission happens after deploy.
"""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "site")
INNER = os.path.join(OUT, "inner")
os.makedirs(INNER, exist_ok=True)

info = json.load(open(os.path.join(HERE, "..", "grain_rot_site_info.json"), encoding="utf-8"))
kw = json.load(open(os.path.join(HERE, "..", "keywords.json"), encoding="utf-8"))

# ---- site-wide constants (replace at deploy time) ----
SITE_DOMAIN = "https://grainrotgame.com"   # confirmed registered 2026-08-08 on Spaceship (nick xiong)
GA_ID = "G-38E373YH0J"                      # GA4 Measurement ID (created via browser-skill on xzzxqdygwswj@gmail.com)
THEME_CSS = """:root{--bg:#14110d;--surface:#1c1813;--theme:#e8622e;--theme2:#f0744a;--text:#eae3da;--muted:#a89a8c}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.7}
header{padding:22px 28px;border-bottom:1px solid #2a241c;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;background:var(--bg);z-index:10}
.logo{font-weight:800;color:var(--theme);letter-spacing:1px;font-size:20px}
.nav a{color:var(--text);text-decoration:none;margin-left:18px;font-size:14px}
.nav a:hover{color:var(--theme)}"""

def esc(s):
    return html.escape(str(s))

def link(url, text):
    return '<a href="' + esc(url) + '">' + esc(text) + '</a>'

def ga_head():
    """GA4 gtag snippet (injected into <head> of every page)."""
    return ("<!-- Google Analytics 4 -->\n"
            "<script async src=\"https://www.googletagmanager.com/gtag/js?id=%s\"></script>\n"
            "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
            "gtag('js',new Date());gtag('config','%s');</script>\n") % (GA_ID, GA_ID)

def canonical(path_abs_url):
    return '<link rel="canonical" href="%s">' % esc(path_abs_url)

def slugify(k):
    return k.replace(" ", "-").replace("  ", "-")

# ---- full page index (category -> [(keyword, filename)]) for interlinking ----
# Every inner page MUST be reachable from the home page, otherwise it is an
# orphan page and Google will not crawl it (L5 manual: internal links matter).
PAGE_INDEX = []
for _cat in kw["categories"]:
    _items = [(it["keyword"], slugify(it["keyword"]) + ".html") for it in _cat["keywords"]]
    PAGE_INDEX.append((_cat.get("label") or _cat.get("name") or "Guides", _items))

def home_guides_section():
    """All 19 inner pages, grouped by keyword category."""
    out = ""
    for cat_name, items in PAGE_INDEX:
        lis = "".join(
            "<li><a href='inner/%s'>%s</a></li>" % (esc(fn), esc(k))
            for k, fn in items)
        out += "<div class='gcol'><h3>%s</h3><ul>%s</ul></div>" % (esc(cat_name), lis)
    return out

def related_section(current_keyword):
    """Sibling pages in the same category + cross-category picks."""
    same, others = [], []
    for cat_name, items in PAGE_INDEX:
        hit = any(k == current_keyword for k, _ in items)
        for k, fn in items:
            if k == current_keyword:
                continue
            (same if hit else others).append((k, fn))
    picks = same[:6] or others[:6]
    if not picks:
        return ""
    lis = "".join("<li><a href='%s'>%s</a></li>" % (esc(fn), esc(k)) for k, fn in picks)
    return "<section class='blk related'><h2>Related guides</h2><ul>%s</ul></section>" % lis

# ---- per-keyword page content (real, cross-verified; "待确认" where unverified) ----
pages = {
    "grain rot guide": {
        "title": "GRAIN ROT Guide - Beginner & Co-op Wiki",
        "desc": "GRAIN ROT guide: beginner tips, co-op extraction, the Living Spark loop, Outpost rebuilding, and how to survive the Corrupted. A fan wiki built from cross-verified sources.",
        "sections": [
            ("What GRAIN ROT is, in one line", "GRAIN ROT is a first-person co-op extraction horror where you play a Living Spark riding a fragile, flammable wooden Vessel into a scorched wasteland, scavenge loot, survive the Corrupted, and rebuild your Outpost. Death is only a change of Vessel, not the end of the run. It launched on Steam on August 7, 2026, developed by Beck & Branch Games and published by Neem Interactive."),
            ("The core loop (your first hour)", "Possess a Vessel, descend into the shifting underground ruins, scavenge furniture and loose loot, fight or avoid the Corrupted, then extract alive before the rot closes in. What you haul back upgrades the Sanctuary Outpost. The fan wiki already documents a Beginner Guide: First Hour in the Ruins (updated 2026-08-11), which breaks the opening loop into clear, repeatable steps rather than overwhelming you with systems."),
            ("Playing with friends", "GRAIN ROT supports 1-4 players in online co-op, or you can play entirely solo. The Outpost is held together by two brothers, Biggie and Murch - they are background NPCs who maintain the base, not robots you control. Your own starting avatar is the wooden Vessel you first possess; your Living Spark is the artificial soul that rides inside it."),
            ("Survival priorities that actually matter", "Keep your Vessel away from open flame (it is literally flammable wood), listen for the Corrupted because they react to sound and movement, and extract early rather than over-looting. Deeper layers bring rarer loot but stranger body-corruption and mutation modifiers that raise both risk and reward. Most bad runs end because someone got greedy."),
            ("Where to go next", "Use the Start Here cards on the home page to jump into Enemies, Vessels & Loadouts, Co-op, Extraction, or Outpost building. Each inner page is written from verified Steam and patch-note facts, with anything still uncertain clearly marked as 待确认 so you never mistake a guess for a confirmed mechanic."),
        ],
    },
    "grain rot tutorial": {
        "title": "How to Play GRAIN ROT - Tutorial & First Steps",
        "desc": "GRAIN ROT tutorial: learn the controls, how to scavenge, use the Grinder, and what the cursed emote does. Beginner walkthrough for the co-op extraction horror on Steam.",
        "sections": [
            ("Controls and perspective", "GRAIN ROT is first-person, mixing survival-horror tension with base-building and a roguelike reset loop. The wiki Start Here section splits learning into Beginner, Enemies, Vessels & Loadouts, Co-op, Extraction, and Outpost, so you can absorb one system at a time instead of all at once."),
            ("Scavenging and the Grinder", "You break apart furniture and environmental objects to scavenge materials as you move through the ruins. The Grinder converts that junk into currency you spend on upgrades back at the Outpost. Because interactions are physics-driven, the world reacts chaotically to your actions - stacking boxes, toppling shelves, and triggering traps are all part of the ride."),
            ("The cursed emote", "A cursed emote can knock a teammate's Spark out of their Vessel. That makes it a genuine panic button when a friend is about to be corrupted, but also a chaotic prank if your crew is feeling mean. Mind your teammates before you spam it."),
            ("Your single-run goal", "Each dive has a clear objective: grab what you can, survive the Corrupted, and extract before things go wrong. Over-looting is the most common way a run ends badly, so set a personal extraction threshold before you push deeper."),
            ("Learning curve tips", "New players should prioritize learning the extraction timer and the safe routes back to the Outpost before experimenting with deeper layers. The demo alone drew 350,000+ downloads, so the community has already mapped a lot of the early-game rhythm worth copying."),
        ],
    },
    "grain rot how to play": {
        "title": "How to Play GRAIN ROT - Co-op Extraction Explained",
        "desc": "How to play GRAIN ROT: explore procedural ruins, scavenge loot, extract alive, and rebuild your Outpost. A clear explainer of the co-op extraction horror by Beck & Branch Games.",
        "sections": [
            ("The premise", "You are a Living Spark - an artificial soul piloting a fragile wooden Vessel. You descend into procedurally shifting underground ruins to scavenge before the Corrupted close in. The procedural layout means no two dives feel identical, which is the core replay hook."),
            ("Extraction and rebuilding", "Everything you bring back rebuilds your Sanctuary Outpost, the safe hub between runs. Deeper dives trigger body-corruption and mutilation modifiers that raise both the danger and the payoff, so progress is a risk-reward conversation every session."),
            ("Death is not the end", "When your Vessel is destroyed you do not die - your Spark finds a new Vessel and the run continues. Teammates can also knock your Spark loose with the cursed emote, which is why crew composition and trust matter more than raw combat skill."),
            ("Reception so far", "Reviews sit at Very Positive on Steam. The combination of physics-driven chaos, co-op tension, and base-building has been widely praised by outlets that covered the Next Fest demo, which landed in the Top 15 most-played demos before launch."),
            ("Pacing advice", "Treat GRAIN ROT like a roguelike, not a shooter. Short, successful extractions beat long, greedy ones. Bank upgrades at the Outpost, then push a little deeper each run as your loadout improves."),
        ],
    },
    "grain rot who are the starting robots": {
        "title": "Who Are the Starting Robots in GRAIN ROT? (Biggie & Murch)",
        "desc": "Who are the starting robots in GRAIN ROT? Biggie and Murch run the Sanctuary Outpost; your starting robot is the wooden Vessel you possess. Real answers from verified sources.",
        "sections": [
            ("The Outpost brothers", "Multiple media outlets (Gamezebo, Age of The Nerd, AppBank) and the official Steam description agree: the Sanctuary Outpost is held together by two brothers, Biggie and Murch. They are background NPCs who maintain the base between runs - not robots you control and not playable characters."),
            ("Your starting robot, explained", "When players ask about the starting robots, what they actually mean is the wooden Vessel you possess at the start. That Vessel is a fragile, flammable container for your Living Spark. You inhabit it; you do not pilot a metal robot, despite the 'robot' framing some search queries use."),
            ("Why the confusion exists", "Early coverage described the Spark-and-Vessel relationship loosely, and the word 'robot' stuck in some community threads. We confirm from the Steam page and patch notes that your avatar is a Vessel, and the brothers are NPCs - no controllable robot exists at spawn."),
            ("What still needs confirmation", "The exact appearance, name, and stat profile of the starting Vessel need in-game verification. We confirm the brothers are NPCs and your avatar is a Vessel, not a robot, and we will not speculate beyond those verified facts."),
        ],
    },
    "grain rot quill": {
        "title": "GRAIN ROT Quill - Who Is Dr. Quill?",
        "desc": "GRAIN ROT Quill: the character who patrols outside the Outpost, fixed in patch 1.06. Real info from patch notes; research mechanics still to be confirmed.",
        "sections": [
            ("Who Quill is", "Patch 1.06 (2026) explicitly notes that Quill no longer catches fire while patrolling outside the Outpost. That confirms Quill is a character who patrols the area outside the Sanctuary Outpost and that fire interaction was a known bug. This matches the research-oriented Dr. Quill framing seen in community discussion."),
            ("What Quill does", "Quill appears tied to research and the zone outside the Outpost. The specific research system - for example, where do I find Dr. Quill's research, or what the research unlocks - is not yet detailed in official or media sources we could cross-verify."),
            ("Open questions", "The exact research loop attached to Quill needs official disclosure or in-game verification. We will not invent a step-by-step process. Treat any claim that names specific research rewards as unverified until the devs document it."),
            ("Tracking the facts", "As new patches land, we update this page from the official patch notes only. Patch 1.06 is the sole verified source for Quill's behavior so far, and we flag everything else as 待确认 rather than guess."),
        ],
    },
    "grain rot corrupted elite": {
        "title": "GRAIN ROT Corrupted Elite - Enemy Guide",
        "desc": "GRAIN ROT Corrupted Elite and enemy types: the Corrupted react to sound, movement, and each other. 9 enemy types in the demo; elite variants to be confirmed.",
        "sections": [
            ("The Corrupted, overall", "The Corrupted are lost Vessels that react to sound, movement, and each other. The fan wiki documents 9 Corrupted types from the demo, each with its own detection model and general combat advice, which is the best current reference for how to read their behavior."),
            ("Elite variants", "Search demand for Corrupted Elite is high, which strongly suggests an elite tier exists. However, official and media sources have not yet named a specific Corrupted Elite enemy. We treat it as an unconfirmed variant and avoid assigning it fabricated stats or attack patterns."),
            ("Combat principles that work", "The general rule is fight, avoid, or troll depending on the situation. Listen for audio cues, manage your flammable Vessel, and extract rather than over-commit to a kill. Coordinated teams can bait Corrupted into each other using the sound-reactive AI."),
            ("Staying safe", "Because the Corrupted respond to noise, silencing your own movement and using the cursed emote sparingly keeps you off their radar. Most deaths come from panic-sprinting through a packed room rather than from any single enemy being unbeatable."),
        ],
    },
    "grain rot how many players": {
        "title": "How Many Players in GRAIN ROT? (Co-op Count)",
        "desc": "How many players in GRAIN ROT? 1-4 players online co-op, or solo. Verified across Gamezebo, GameRant, and the Steam page.",
        "sections": [
            ("Player count", "GRAIN ROT supports 1-4 players in online co-op - you plus up to three friends. It is also fully playable solo if you prefer to scavenge alone. This is confirmed by the Steam FAST FACTS block and repeated across Gamezebo and GameRant coverage."),
            ("How co-op works", "You team up through online co-op, with party settings that let you squad up before a dive. Deeper layers and shared loot make a coordinated team far safer than a lone Spark, since someone can cover extraction while another hauls loot."),
            ("Solo vs squad", "Solo runs are quieter and easier to keep stealthy, while a full four-person squad can push deeper and split scavenging duties. Neither is strictly better; it depends on whether you value stealth or throughput."),
            ("Source confirmation", "Steam lists Players 1-4 online co-op in its FAST FACTS; Gamezebo and GameRant both independently confirm the same figure. We treat 4 as the hard maximum, not a soft suggestion."),
        ],
    },
    "grain rot max players": {
        "title": "GRAIN ROT Max Players - Party Size Limit",
        "desc": "GRAIN ROT max players is 4. Online co-op supports up to 4 players (you + 3 friends). Verified via GamesPress FAST FACTS.",
        "sections": [
            ("Maximum party size", "The maximum is 4 players in online co-op. GamesPress FAST FACTS states Players 1-4 online co-op, which matches the Steam page exactly. You cannot exceed four in a single session."),
            ("Solo to full squad", "You can drop in solo or fill a 4-person squad. Larger groups handle deeper dives and tougher Corrupted more reliably because they can cover more of the ruin at once."),
            ("Why four and not more", "The design leans on tight, readable co-op chaos rather than large-scale raids. Four Sparks is enough to create emergent panic without the AI losing track of who is making noise."),
        ],
    },
    "grain rot multiplayer": {
        "title": "GRAIN ROT Multiplayer & Co-op Guide",
        "desc": "GRAIN ROT multiplayer: online co-op for up to 4, friends-only lobbies, and password-protected servers added in 1.07. Real patch-note facts.",
        "sections": [
            ("Co-op fundamentals", "GRAIN ROT is built for online co-op, tagged Online Co-op on Steam. You and up to three friends descend into the ruins together and share the extraction pressure."),
            ("Lobby and privacy", "Patch 1.05 fixed a friends-only lobby join bug, so inviting just your friends is reliable. Patch 1.07 added multiplayer controls and password-protected servers, giving you private sessions away from random matchmaking."),
            ("Finding a crew", "The Steam Community Hub (steamcommunity.com/app/4450620) is the official discussion space for finding crews and coordinating dives. Many players post Looking-For-Group threads there."),
            ("Netcode notes", "Because the Corrupted react to sound and movement, voice comms dramatically improve a squad's survival. Plan routes before you drop, and agree on an extraction threshold so nobody gets left behind greedily looting."),
        ],
    },
    "grain rot game": {
        "title": "What Is GRAIN ROT? Game Overview & Platforms",
        "desc": "What is GRAIN ROT? A first-person co-op extraction horror builder by Beck & Branch Games on Steam (PC). Tags: survival horror, base building, roguelike.",
        "sections": [
            ("The game at a glance", "GRAIN ROT is a first-person co-op extraction horror builder from Beck & Branch Games, published by Neem Interactive. It launched on Steam on August 7, 2026, after a Next Fest demo that hit 350,000+ downloads."),
            ("Genre and platforms", "Genres span action, horror, indie, physics, and post-apocalyptic looter. The platform is PC (Steam) only - there is no confirmed console version as of launch. Simplified Chinese is among the 11 supported languages."),
            ("System requirements", "Per the Steam page, you need Windows 10 64-bit, an Intel i5-4590 or Ryzen 5 2600, 8GB RAM, a GTX 970, DirectX 11, and about 10GB of space. These are modest, which helps the game run on a wide range of laptops."),
            ("Price and edition", "The Steam list price is $9.99, with a launch-week discount to $8.99. The game is single-purchase; there is no confirmed battle-pass or paid tier as of the manual's research window."),
        ],
    },
    "grain rot steam": {
        "title": "GRAIN ROT on Steam - App Page & Details",
        "desc": "GRAIN ROT on Steam: app 4450620, $9.99 (launch-week $8.99), 11 languages, Very Positive. Full tag list and community hub inside.",
        "sections": [
            ("Steam essentials", "The Steam App ID is 4450620. It released on 2026-08-07 at $9.99, with a launch-week discount to $8.99. User reviews sit at Very Positive, a strong signal for a small indie co-op title."),
            ("Languages", "Eleven languages ship with interface and audio support: English, German, Japanese, Korean, Portuguese-Brazil, Russian, Simplified Chinese, Ukrainian, French, Spanish, and Traditional Chinese."),
            ("Tags and community", "Tags include online co-op, first-person, survival horror, base building, action roguelike, procedural generation, crafting, PvE, light roguelike, comedy, physics, looter, horror, 3D, post-apocalyptic, atmosphere, indie, single-player, and action. The community hub lives at steamcommunity.com/app/4450620."),
            ("Wishlist momentum", "Before launch the demo built 250,000+ wishlists and 350,000+ downloads, landing in the Top 15 most-played Next Fest demos - strong evidence the full game had real demand on day one."),
        ],
    },
    "grain rot release date": {
        "title": "GRAIN ROT Release Date - When It Launched",
        "desc": "GRAIN ROT release date: August 7, 2026 on Steam. The Next Fest demo hit 350K+ downloads and 250K+ wishlists before launch.",
        "sections": [
            ("Release date", "GRAIN ROT launched on Steam on August 7, 2026. This is confirmed by both the Steam store page and GamesPress FAST FACTS, so it is a verified date rather than a rumor."),
            ("Demo momentum", "Ahead of launch, the Next Fest demo reached 350,000+ downloads and 250,000+ wishlists, placing it in the Top 15 most-played demos of that festival. That pipeline is why the full release entered Very Positive quickly."),
            ("Post-launch cadence", "The developers shipped a steady patch stream (1.01 through at least 1.07) in the weeks after launch, fixing save bugs, lobby issues, and balance. That cadence matters if you are deciding whether to buy now or wait."),
        ],
    },
    "grain rot how to unlock precision chamber": {
        "title": "How to Unlock the Precision Chamber in GRAIN ROT",
        "desc": "How to unlock Precision Chamber in GRAIN ROT: tied to the ancient facilities and bunker doors. Exact steps unconfirmed - no fabrication.",
        "sections": [
            ("What we know", "Patch 1.03 mentions a bunker door in the ancient facilities, which implies an ancient-facilities zone with door-lock mechanics. The Precision Chamber most likely maps to a room inside these facilities, gated behind that door."),
            ("What we do not know", "The exact unlock condition for the Precision Chamber - the items, switches, or sequence required - is not stated in any official or media source we could cross-verify. We will not invent steps to fill the gap."),
            ("Safe advice", "Explore the ancient facilities bunker doors and report back once the game documents the chamber. Treat any instant-unlock claim you see online as unverified until it is reproduced from the official patch notes."),
            ("Why this page exists", "Search volume for this phrase is real, so we built the page to capture the verified context (ancient facilities, bunker door) and clearly mark the missing steps as 待确认, rather than publishing a fabricated walkthrough."),
        ],
    },
    "grain rot what do the dolls do": {
        "title": "What Do the Dolls Do in GRAIN ROT?",
        "desc": "What do the dolls do in GRAIN ROT? No public source currently documents this. We flag it as unconfirmed rather than guess.",
        "sections": [
            ("Current status", "Across the Steam page, media reviews, the existing fan wiki, and the patch logs, no description of the dolls appears. We cannot confirm their function from any verified source, so this page deliberately does not invent one."),
            ("Our stance", "We refuse to fabricate mechanics. The dolls' role is marked as needing official or in-game confirmation. Check back after future patches or official guides land, and we will update from primary sources only."),
            ("How to verify yourself", "The safest way to learn what the dolls do is to watch the in-game codex or official patch notes, then compare against community testing. Until then, any detailed 'dolls guide' you find elsewhere should be treated as speculation."),
        ],
    },
    "grain rot how to repair items": {
        "title": "How to Repair Items in GRAIN ROT",
        "desc": "How to repair items in GRAIN ROT: construct-attachment fixes hinted in patch 1.02. Full repair flow unconfirmed - no fabrication.",
        "sections": [
            ("What we know", "Patch 1.02 references construct-attachment fixes and item pickup and trap-visibility fixes, which implies a construct system whose parts can be attached and presumably repaired. That is the strongest hint at a repair loop."),
            ("What we do not know", "No dedicated repair tool or step-by-step repair flow is documented officially. We avoid inventing a process and instead point you to the in-game construct UI as the place to confirm the exact inputs."),
            ("Recommendation", "Expect repair to involve construct attachments; verify the exact interaction via the in-game menu or official patch notes. We will expand this page once a verified repair guide exists."),
        ],
    },
    "grain rot mods": {
        "title": "GRAIN ROT Mods - Workshop, ReShade & Risks",
        "desc": "GRAIN ROT mods: Steam Workshop (if enabled) and ReShade for visuals. Avoid memory editors / trainers - online use may trigger bans.",
        "sections": [
            ("Official mod support", "Check whether the Steam page carries a Workshop tag. If it does, the Steam Community hub is where mods live. Visual-only tweaks through ReShade are safe and do not touch game logic or risk a ban."),
            ("Risks to avoid", "Third-party trainers and memory editors may trigger anti-cheat or a ban in online sessions. We do not recommend them for co-op play, where other players would be affected by altered behavior."),
            ("Graphics without risk", "For a better look, ReShade post-processing is the recommended route. Verify it does not conflict with the game's anti-cheat checks before you rely on it in online runs."),
            ("Community norm", "Because the game is small and co-op-focused, the modding scene is thin so far. Most shared changes are cosmetic; anything that alters extraction or loot should be assumed risky until proven otherwise."),
        ],
    },
    "grain rot savefile": {
        "title": "GRAIN ROT Save File - Location & Backup",
        "desc": "GRAIN ROT save file: Steam Cloud manages saves; local path follows Steam userdata/SteamID/4450620. Backup before updates.",
        "sections": [
            ("Where saves live", "Saves are handled by Steam, both through Steam Cloud and a local file. The local pattern is typically Steam/userdata/<SteamID>/4450620/remote/ - confirm the exact subfolder in-game, because Valve's layout can vary slightly by title."),
            ("Known issues already fixed", "Patch 1.02 fixed offline save loading, and patch 1.03 fixed a save bug that caused black-void loads and key-binding saves to misbehave. Those fixes mean modern saves are far more stable than at launch."),
            ("Backup first", "Before any update, back up the userdata directory or rely on Steam Cloud. Verify your save loaded correctly after each patch, since the early post-launch bugs show saves are worth protecting."),
        ],
    },
    "grain rot wiki": {
        "title": "GRAIN ROT Wiki - The Fan Resource Hub",
        "desc": "GRAIN ROT wiki: fan-made guides for the co-op extraction horror. We aim to be the most accurate hub, correcting the existing fan wiki's trademark slip.",
        "sections": [
            ("The existing wiki", "The only notable fan wiki (grainrotwiki.vercel.app) covers Home, Guides, Tier List, and FAQ. Its guides include Beginner, All Enemies (9 Corrupted), Best Vessels & Loadouts, Co-op, Extraction, and Outpost."),
            ("Our edge", "That wiki's footer mislabels the trademark as Vaulted Sky Games. We use the official Steam credit: Beck & Branch Games. Our goal is to be more complete and accurate, and to clearly mark unverified mechanics instead of guessing."),
            ("No official wiki", "There is no official wiki; the Steam Community Hub is the official discussion entry point. This site is independently maintained and not affiliated with the developers or publisher."),
            ("How we source", "Every page here is built from the Steam store page (app 4450620), official patch notes, and independent media coverage. Where sources disagree or stay silent, we say so rather than fill the gap with invention."),
        ],
    },
    "grain rot secrets": {
        "title": "GRAIN ROT Secrets & Hidden Content",
        "desc": "GRAIN ROT secrets: new hat items in Deep Layers (1.07), legendary gumballs (1.06), ancient facilities, rolling boulder traps, body mutations.",
        "sections": [
            ("Deep Layer rewards", "Patch 1.07 added a new hat item in the Deep Layers, and patch 1.06 fixed legendary gumball rewards, a notable loot type. These are the verified 'secret' rewards worth hunting on deeper dives."),
            ("Hidden systems", "Ancient facilities, rolling boulder traps, and body-corruption or mutation mechanics form the deeper, stranger layers worth digging into. They reward players who push past the safe early routes."),
            ("Official hint", "The Steam description promises rarer loot and stranger mutations the deeper you dive - so secrets scale with risk. The further down you go, the more the game bends its own rules."),
            ("Community discoveries", "Because the game is physics-driven, players keep finding emergent tricks (stacking, trap chaining, Sound-baiting Corrupted). We track verified ones and label the rest as 待确认."),
        ],
    },
}

def render_inner(item, abs_url):
    k = item["keyword"]
    p = pages.get(k)
    if not p:
        p = {"title": k + " - GRAIN ROT Wiki", "desc": k + " - fan wiki page for the co-op extraction horror GRAIN ROT.", "sections": [("Overview", "Content pending verification.")]}
    title = p["title"]
    desc = p["desc"]
    body = ""
    for h2, txt in p["sections"]:
        body += "<section class='blk'><h2>" + esc(h2) + "</h2><p>" + esc(txt) + "</p></section>\n"
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
%s
%s
<style>
%s
main{max-width:760px;margin:36px auto;padding:0 20px}
.hero{background:linear-gradient(135deg,#1c1813,#241a12);border:1px solid #2a241c;border-radius:14px;padding:30px;margin-bottom:28px}
.hero h1{margin:0 0 12px;font-size:30px;color:var(--theme2)}
.hero p{color:var(--muted);margin:0}
.blk{background:var(--surface);border:1px solid #2a241c;border-radius:12px;padding:18px 20px;margin:16px 0}
h2{color:var(--theme);font-size:20px;margin:0 0 8px}
p{margin:0 0 10px}
.back{display:inline-block;margin:24px 0;color:var(--theme);text-decoration:none;font-weight:600}
.related ul{margin:0;padding-left:18px;columns:2;column-gap:24px}
.related li{margin:4px 0}
.related a{color:var(--theme2);text-decoration:none}
.related a:hover{text-decoration:underline}
footer{border-top:1px solid #2a241c;padding:20px;color:var(--muted);font-size:13px;text-align:center}
@media(max-width:700px){.related ul{columns:1}}
</style>
</head>
<body>
<header><div class="logo">GRAIN ROT WIKI</div><nav class="nav"><a href="../index.html">Home</a><a href="../index.html#guides">Guides</a><a href="../index.html#about">About</a></nav></header>
<main>
<div class="hero"><h1>%s</h1><p>%s</p></div>
%s
%s
<a class="back" href="../index.html">&larr; Back to GRAIN ROT Wiki</a>
</main>
<footer>GRAIN ROT Wiki is a fan-made, independent guide hub. Not affiliated with Beck &amp; Branch Games or Neem Interactive. Sources: Steam app 4450620, official patch notes, media coverage.</footer>
</body></html>""" % (esc(title), esc(desc), canonical(abs_url), ga_head(), THEME_CSS, esc(title), esc(desc), body, related_section(k))

def render_home():
    h = info["home"]
    m = h["meta"]
    stats = "".join("<span class='stat'>%s</span>" % esc(s) for s in h["hero"]["stats"])
    cards = ""
    for c in h["start"]["cards"]:
        cards += "<div class='card'><div class='num'>%s</div><div class='ct'><h3>%s</h3><p>%s</p></div></div>" % (esc(c["number"]), esc(c["title"]), esc(c["description"]))
    about_stats = "".join("<div class='as'><span class='al'>%s</span><span class='av'>%s</span></div>" % (esc(x["label"]), esc(x["value"])) for x in h["aboutGame"]["stats"])
    about_p = "".join("<p>%s</p>" % esc(p) for p in h["aboutGame"]["paragraphs"])
    f = info["footer"]
    ol = info["officialLinks"]
    home_abs = SITE_DOMAIN + "/"   # canonical must be the served root, not /index.html
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
%s
%s
<style>
%s
.sidebar{position:fixed;right:18px;top:90px;width:230px;background:var(--surface);border:1px solid #2a241c;border-radius:12px;padding:16px;font-size:13px}
.sidebar h4{margin:0 0 8px;color:var(--theme)}
.sidebar .code{color:var(--muted)}
.hero{max-width:900px;margin:40px auto;padding:0 20px}
.hero .eyebrow{color:var(--theme);font-weight:600;letter-spacing:2px;font-size:13px;text-transform:uppercase}
.hero h1{font-size:54px;margin:10px 0;color:var(--theme2)}
.hero p{color:var(--muted);font-size:18px;max-width:640px}
.stats{display:flex;flex-wrap:wrap;gap:10px;margin:22px 0}
.stat{background:var(--surface);border:1px solid #2a241c;border-radius:20px;padding:8px 14px;font-size:13px}
.ctas{margin:22px 0;display:flex;gap:12px;flex-wrap:wrap}
.btn{background:var(--theme);color:#1a1208;padding:12px 20px;border-radius:10px;text-decoration:none;font-weight:700}
.btn.ghost{background:transparent;border:1px solid var(--theme);color:var(--theme)}
.cards{max-width:900px;margin:40px auto;padding:0 20px;display:grid;grid-template-columns:1fr 1fr;gap:16px}
.card{background:var(--surface);border:1px solid #2a241c;border-radius:14px;padding:20px;display:flex;gap:14px}
.num{font-size:26px;color:var(--theme);font-weight:800;min-width:34px}
.ct h3{margin:0 0 6px;color:var(--theme2)}
.ct p{color:var(--muted);margin:0;font-size:14px}
.about{max-width:900px;margin:40px auto;padding:0 20px}
.about h2{color:var(--theme);font-size:26px}
.abp{color:var(--muted)}
.aswrap{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:18px}
.as{background:var(--surface);border:1px solid #2a241c;border-radius:10px;padding:12px}
.al{display:block;color:var(--muted);font-size:12px}
.av{font-weight:700;color:var(--text)}
.final{max-width:900px;margin:40px auto;padding:30px 20px;text-align:center;background:linear-gradient(135deg,#1c1813,#241a12);border-radius:16px}
.final h2{color:var(--theme2);font-size:28px;margin:0 0 10px}
.final p{color:var(--muted)}
footer{border-top:1px solid #2a241c;padding:28px 20px;color:var(--muted);font-size:13px;max-width:900px;margin:40px auto;text-align:center}
footer a{color:var(--theme);text-decoration:none}
.kw{color:var(--muted);font-size:12px;margin-top:8px}
.guides{max-width:900px;margin:40px auto;padding:0 20px}
.guides h2{color:var(--theme);font-size:26px;margin-bottom:6px}
.guides .lead{color:var(--muted);margin:0 0 20px;font-size:15px}
.gwrap{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.gcol{background:var(--surface);border:1px solid #2a241c;border-radius:12px;padding:16px 18px}
.gcol h3{margin:0 0 10px;color:var(--theme2);font-size:15px}
.gcol ul{margin:0;padding-left:16px}
.gcol li{margin:6px 0;font-size:14px}
.gcol a{color:var(--text);text-decoration:none}
.gcol a:hover{color:var(--theme);text-decoration:underline}
@media(max-width:900px){.sidebar{display:none}.cards{grid-template-columns:1fr}.gwrap{grid-template-columns:1fr}}
</style>
</head>
<body>
<header><div class="logo">GRAIN ROT WIKI</div><nav class="nav"><a href="#start">Start Here</a><a href="#guides">All Guides</a><a href="#about">About</a><a href="#footer">Links</a></nav></header>
<aside class="sidebar"><h4>Redeem / 兑换码</h4><div class="code">%s</div><div class="code" style="margin-top:8px">%s</div></aside>
<section class="hero">
<div class="eyebrow">%s</div>
<h1>%s</h1>
<p>%s</p>
<div class="stats">%s</div>
<div class="ctas">
<a class="btn" href="inner/grain-rot-guide.html">%s</a>
<a class="btn ghost" href="inner/grain-rot-multiplayer.html">%s</a>
<a class="btn ghost" href="inner/grain-rot-corrupted-elite.html">%s</a>
</div>
</section>
<section id="start" class="cards">%s</section>
<section id="guides" class="guides">
<h2>All GRAIN ROT guides</h2>
<p class="lead">Every page below answers one specific question about GRAIN ROT, written from cross-verified Steam, patch-note and community sources.</p>
<div class="gwrap">%s</div>
</section>
<section id="about" class="about">
<h2>%s</h2>
<div class="abp">%s</div>
<div class="aswrap">%s</div>
<div class="ctas" style="margin-top:18px"><a class="btn" href="inner/grain-rot-wiki.html">%s</a></div>
</section>
<section id="footer" class="final">
<h2>%s</h2>
<p>%s</p>
<div class="ctas" style="justify-content:center"><a class="btn" href="inner/grain-rot-guide.html">%s</a><a class="btn ghost" href="%s">%s</a></div>
<p class="kw">Official: %s · %s · %s · %s</p>
</section>
<footer>
<div>%s</div>
<div>%s</div>
<div style="margin-top:10px">%s · %s · %s</div>
</footer>
</body></html>""" % (
        esc(m["title"]),
        esc(info["metadata"]["description"]),
        canonical(home_abs),
        ga_head(),
        THEME_CSS,
        esc(info["sidebarCodes"][0]),
        esc(info["sidebarCodes"][1]),
        esc(h["hero"]["eyebrow"]),
        esc(h["hero"]["title"]),
        esc(h["hero"]["description"]),
        stats,
        esc(h["hero"]["primaryCta"]),
        esc(h["hero"]["secondaryCta"]),
        esc(h["hero"]["tertiaryCta"]),
        cards,
        home_guides_section(),
        esc(h["aboutGame"]["title"]),
        about_p,
        about_stats,
        esc(h["aboutGame"]["cta"]),
        esc(h["finalCta"]["title"]),
        esc(h["finalCta"]["description"]),
        esc(h["finalCta"]["primary"]),
        esc(ol["steam"]),
        esc(h["finalCta"]["secondary"]),
        link(ol["steam"], "Steam"),
        link(ol["discord"], "Discord"),
        link(ol["reddit"], "Reddit"),
        link(ol["x"], "X"),
        esc(f["about"]),
        esc(f["description"]),
        link(ol["steam"], f["playGame"]),
        link(ol["discord"], f["officialDiscord"]),
        link(ol["communityHub"], f["communityTool"]),
    )

def slug(k):
    return k.replace(" ", "-").replace("  ", "-")

def build_sitemap(urls):
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        out.append("  <url><loc>%s</loc></url>" % esc(u))
    out.append("</urlset>")
    return "\n".join(out)

# ---- write pages ----
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(render_home())
all_urls = [SITE_DOMAIN + "/"]
for cat in kw["categories"]:
    for item in cat["keywords"]:
        k = item["keyword"]
        fname = slug(k) + ".html"
        abs_url = SITE_DOMAIN + "/inner/" + fname
        all_urls.append(abs_url)
        open(os.path.join(INNER, fname), "w", encoding="utf-8").write(render_inner(item, abs_url))

# ---- sitemap + robots ----
open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(build_sitemap(all_urls))
open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(
    "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE_DOMAIN)

print("Home + %d inner pages + sitemap.xml + robots.txt written to %s" % (len(all_urls) - 1, OUT))
print("GA_ID placeholder:", GA_ID, "| Domain placeholder:", SITE_DOMAIN)
