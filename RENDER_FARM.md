# Rendering on other machines

A reel is planned on one machine and rendered on another. This file is how to
set that up from scratch, on any mix of Macs and PCs.

Two roles:

- **Planning machine** (a Mac here). Ingests the take, fetches the question,
  builds the caption clock, writes the plan, compiles it and renders the frames
  you review. Light work: nothing here takes longer than a minute.
- **Render worker** (a PC here). Does the one heavy step, then runs the gates
  and delivers. A GPU machine renders a two minute reel in about four minutes;
  an 8 GB laptop takes twenty-two, and often refuses to start at all because
  `machine_guard` will not let a render fill the disk the swap file is growing
  into.

Any number of each. Workers claim jobs from a shared queue, so adding a second
or third PC needs no configuration beyond running the worker on it.

## How the queue works

The queue is a folder. Both roles read and write it, and neither machine ever
talks to the other directly.

```
<queue>/pipeline/        the pipeline code, pushed by a planning machine
<queue>/jobs/<slug>/     payload + job.json   (queued -> running -> done/failed)
<queue>/done/<slug>/     the finished parts, delivery.json and the render log
```

That folder can be:

| Where the machines are | Use | `<queue>` looks like |
|---|---|---|
| Same network | an SMB share | `/Volumes/kitjobs` and `C:\kitjobs` |
| Different networks | an rclone remote | `myremote:kitjobs` |
| Neither, or no permissions | a USB stick | `/Volumes/STICK/kitjobs` and `E:\kitjobs` |

The commands are identical in all three cases; only the path changes.

**Google Drive is the usual answer**, because it needs no networking, no admin
rights and no firewall changes, and either machine can be asleep while the
other works.

## Set up a planning machine

Follow `lab/kit_test/README.md` for the pipeline itself. Then, if the queue is
an rclone remote:

```bash
brew install rclone          # macOS
rclone config                # new remote, type "drive", authorise in a browser
rclone lsd <remote>:         # should list your Drive
```

## Set up a render worker

Follow `lab/kit_test/README.md` for the pipeline, then:

```powershell
# rclone, portable, no admin needed
#   https://downloads.rclone.org/rclone-current-windows-amd64.zip
#   unzip, put rclone.exe at C:\rclone\rclone.exe
[Environment]::SetEnvironmentVariable("RCLONE", "C:\rclone\rclone.exe", "User")
C:\rclone\rclone.exe config          # same remote NAME as the planning machine

cd <repo>
echo worker > .queue-worker          # opt in; see the warning below
.venv-tools\Scripts\python tools\doctor.py
.venv-tools\Scripts\python tools\render_queue.py work <remote>:kitjobs
```

Authorise rclone on the worker in its own browser rather than copying
`rclone.conf` across: that file holds a live token for your Google account.

**`.queue-worker` is an opt-in safety flag.** A worker REPLACES
`projects/<slug>` with whatever the queue sends it. On a render machine that is
correct; on the machine the work was planned on it would destroy it. A machine
without the file refuses to run as a worker.

Whisper being absent is fine on a worker: captions are resolved into
`timeline.js` at compile time, so nothing downstream transcribes anything.

### Keep it running

```powershell
$repo = "<repo path>"
$a = New-ScheduledTaskAction -Execute "$repo\.venv-tools\Scripts\python.exe" `
     -Argument "tools\render_queue.py work <remote>:kitjobs" -WorkingDirectory $repo
$t = New-ScheduledTaskTrigger -AtLogOn
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
     -ExecutionTimeLimit 0 -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName "KitRenderWorker" -Action $a -Trigger $t -Settings $s
```

`-AtLogOn` means a reboot leaves it stopped until somebody logs in. Running it
whether logged on or not needs a stored password, which is a decision about
that machine rather than about this pipeline. Check the sleep settings too: a
machine that sleeps mid-render kills the job.

## Using it

From a planning machine:

```bash
python tools/render_queue.py push-code <queue>              # once, and after any code change
python tools/render_queue.py push      <queue> <slug> ...   # per reel, after you approve its frames
python tools/render_queue.py status    <queue>
python tools/render_queue.py pull      <queue> [<slug> ...]
```

A worker then does everything else by itself: syncs the code, downloads the
job, renders, runs `tools/gates.py`, appends the answer page, copies into its
own Final folder and uploads the result to `<queue>/done/<slug>/`.

### push-code is not optional

"The PC already has the pipeline" is not the same as "the PC has THIS
pipeline". `compose.py`, `stage.html`, `gates.py` and the theme skins change
often, and a render against stale ones either fails or quietly comes out in the
wrong look. A worker therefore syncs the code from the queue before every
batch, and `push-code` is what puts it there.

Over an rclone remote the code push carries about 210 files rather than the
repository: the pipeline itself plus what the stage page loads at render time
(`library/elements/kit`, `assets/fonts`, `assets/character`, `library/sfx`).
Shipping all of `library/` was 7,400 files and measured at roughly two hours,
because Drive charges a round trip per file. Anything a particular reel needs,
such as its theme or its background plate, travels with the job.

## Several workers at once

Workers do not coordinate, so two of them must never render the same reel: the
second would overwrite the first's delivery. Claiming is therefore not
read-state-then-write-state, which is not atomic on a shared folder. Each
worker writes a claim file, waits for the others' to become visible, and the
earliest `(timestamp, name)` wins; the losers delete their claim and look
elsewhere. The wait costs eight seconds against a render of minutes.

A worker also writes a heartbeat every two minutes while it renders. A job left
`running` by a worker that has been silent for thirty minutes becomes
claimable again, so a crash or a reboot does not strand it.

## When something fails

`status` shows `failed` and the reason. The full render log is at
`<queue>/done/<slug>/log.txt` — readable from any machine, which is the point:
a worker can be diagnosed without anyone going to it.

Common first-run problems:

- **Hindi text shaped wrongly.** `doctor.py` reports it. On Windows, put
  FriBiDi's `fribidi-0.dll` on PATH. Skip this and the vowel signs are drawn in
  storage order, every Devanagari label is wrong, and nothing errors.
- **The Final folder lands somewhere odd.** If the Desktop is redirected into
  OneDrive, set `DELIVER_ROOT`.
- **`rclone` not found by the scheduled task.** Set `RCLONE` as a user
  environment variable, not just in the shell you tested in.

## Secrets

This repository is public. `.env` is gitignored and must stay that way: it
holds the question sheets' IDs, which are secrets in practice because the
sheets are readable by link. A render worker needs none of them — the answer
pages are fetched on the planning machine and travel inside the job.
