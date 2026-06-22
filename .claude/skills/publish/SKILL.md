---
name: publish
description: Commit and publish changes to the Astronomical calendar project, then confirm the GitHub Pages deploy. Use this whenever the user asks to commit, publish, ship, deploy, or push in this repo — it handles feed regeneration, the GitHub author-email quirk, and deploy verification that a plain `git commit && git push` would miss.
---

# Publish the Astronomical calendar

This repo is a static GitHub Pages site (`divinetomedy/astronomical`). Publishing
means: rebuild the `.ics` feeds if needed, commit, push to `main`, and confirm the
live site updated. There are two non-obvious gotchas baked into the steps below —
follow them and the publish "just works."

## Steps

### 1. Regenerate feeds — only if the generator changed

The four `.ics` files are produced by `generate.py`. They're deterministic, so they
only need rebuilding when `generate.py` (event definitions, formatting, timezones,
year ranges) changed. Check the working tree:

```bash
git status --porcelain
```

- If `generate.py` is among the changes, regenerate (rebuilding the 1000-year feeds
  takes ~45s, so it's worth skipping when unnecessary):
  ```bash
  python3 generate.py
  ```
- If only `index.html`, `README.md`, or other non-generator files changed, skip this.

### 2. Stage everything

```bash
git add -A
```

### 3. Commit with the GitHub noreply author

The `divinetomedy` account has email privacy turned on, so GitHub **rejects** any
push whose commit author email is a normal address (e.g. the one in git config).
Always author the commit with the account's `noreply` address. Compute it from the
GitHub API so it stays correct:

```bash
GHID=$(gh api user --jq .id)
LOGIN=$(gh api user --jq .login)
NOREPLY="${GHID}+${LOGIN}@users.noreply.github.com"
git -c user.name="$LOGIN" -c user.email="$NOREPLY" commit -m "<message>"
```

Two things to keep in mind:
- **Don't name the variable `UID`** — it's read-only in zsh and the assignment fails
  with "operation not permitted." `GHID` (as above) is safe.
- Write a concise, specific commit message describing the change, and end it with the
  Co-Authored-By trailer the environment expects:
  ```
  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
  ```

### 4. Push

```bash
git push
```

### 5. Verify the deploy

GitHub Pages redeploys automatically, usually within ~30s, and the CDN serves the old
version until it flips. Don't claim success off the push alone — poll the live site for
a string unique to this change so you know the new version is actually live:

```bash
for i in $(seq 1 20); do
  curl -s https://divinetomedy.github.io/astronomical/ | grep -q "<unique snippet>" \
    && { echo "DEPLOYED"; break; }
  sleep 15
done
```

Pick `<unique snippet>` from whatever you just changed — a new line of copy on the
landing page, or for a feed change, fetch the relevant `.ics` instead, e.g.
`https://divinetomedy.github.io/astronomical/astronomical-pacific-100yr.ics`.

## Notes

- Only commit and push when the user has asked to — invoking this skill is that ask.
- Site root: https://divinetomedy.github.io/astronomical/
- Feeds: `astronomical-{pacific,utc}.ics` (1000-yr) and `astronomical-{pacific,utc}-100yr.ics`.
