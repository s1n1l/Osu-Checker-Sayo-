STRINGS = {
    "app.title": "osu-checker — SayoDevice O3C",
    "app.subtitle": "gameplay analyser for SayoDevice O3C",

    "tab.analysis": "Analysis",
    "tab.record": "Recording",
    "tab.training": "Training",
    "tab.settings": "Settings",

    "analysis.drop_hint": "Drop an .osr here — or press “Open replay”",
    "analysis.open_replay": "Open replay…",
    "analysis.last_replay": "Latest osu! replay",
    "analysis.attach_session": "Attach recording…",
    "analysis.attach_session_tip": (
        "A file from the Recording tab. Adds real key travel depth, which "
        "a replay does not contain."),
    "analysis.attached": "Recording: {name}",
    "analysis.no_replay": "No replay loaded",
    "analysis.analysing": "Analysing {name}…",
    "analysis.error": "Error: {message}",
    "analysis.no_osr_found": "No .osr found in the folders from Settings",
    "analysis.session_unreadable": "Cannot read the recording: {message}",
    "analysis.session_no_presses": (
        "The recording has no key presses with travel data — nothing to "
        "measure depth from"),
    "analysis.no_data": "No data",
    "analysis.map_not_found": (
        "The beatmap for this replay is not in the index. Rebuild the index "
        "in Settings if the map was added recently."),

    "view.overview": "Overview",
    "view.aim": "Aim",
    "view.episodes": "Problem spots",

    "stat.error": "Hit error",
    "stat.error_hint": "minus early / plus late",
    "stat.ur": "UR",
    "stat.ur_hint": "replay records {fps:.0f} frames/s",
    "stat.left": "Left",
    "stat.right": "Right",
    "stat.hand_hint": "UR {ur:.0f} · {n} notes",
    "stat.counts": "300/100/50/miss",
    "stat.counts_hint": "our own count",
    "stat.aim_spread": "Aim spread",
    "stat.aim_spread_hint": "in fractions of the circle radius",

    "plot.hist_title": "Hit error distribution",
    "plot.hist_x": "error (minus early / plus late), ms",
    "plot.timeline_title": "Hit error over the map",
    "plot.timeline_x": "time, s",
    "plot.timeline_y": "error, ms",

    "hand.left": "left",
    "hand.right": "right",

    "col.bpm": "BPM",
    "col.notes": "notes",
    "col.error": "error",
    "col.ur": "UR",
    "col.drift": "drift",
    "col.misses": "misses",
    "col.extras": "extras",

    "aim.plot_title": "Where the cursor landed relative to the circle centre",
    "aim.axis_px": "osu! pixels",
    "aim.by_jump": "By jump distance",
    "aim.by_dir": "By jump direction",
    "aim.col_jump": "jump, px",
    "aim.col_notes": "notes",
    "aim.col_spread": "spread",
    "aim.col_edge": "edge hits",
    "aim.col_over": "overshoot",
    "aim.col_over_pct": "% over",
    "aim.col_dir": "direction",
    "aim.no_data": "This replay has no cursor data.",
    "aim.radius": "Circle radius",
    "aim.bias": "Centre offset",
    "aim.bias_hint": "the yellow cross marks your average hit",
    "aim.spread": "Spread",
    "aim.spread_value": "{value:.2f} of the radius",
    "aim.edge": "Edge hits",
    "aim.overshoot": "Overshoot",
    "aim.overshoot_value": "{px:.1f} px on {pct:.0f}% of jumps",

    "ep.head": "The most expensive stretches of the map — where the points "
               "went and what the numbers say caused it",
    "ep.col_time": "time",
    "ep.col_tempo": "tempo",
    "ep.col_notes": "notes",
    "ep.col_loss": "lost",
    "ep.col_cause": "cause",
    "ep.col_what": "what happened",
    "ep.cause.late": "fell behind",
    "ep.cause.early": "rushed",
    "ep.cause.scatter": "scatter",
    "ep.cause.aim": "aim",
    "ep.cause.mixed": "mixed",
    "ep.what.late": "error crept from {early:+.0f} to {late:+.0f} ms — the "
                    "hand lost the tempo",
    "ep.what.early": "consistently early, mean {mean:+.0f} ms",
    "ep.what.scatter": "centre is fine ({mean:+.0f} ms) but UR is {ur:.0f} — "
                       "uneven tapping",
    "ep.what.aim": "cursor sat {spread:.2f} radius from centre, {edge:.0f}% "
                   "on the edge — aim fell apart, not tapping",
    "ep.what.mixed": "error {mean:+.0f} ms, UR {ur:.0f}",
    "ep.miss": "{n} miss",
    "ep.hundred": "{n}×100",
    "ep.fifty": "{n}×50",
    "ep.none": "—",

    "rec.info": (
        "Three sources at once: key presses from the O3C only (Raw Input "
        "filtered by VID_8089&PID_0009), analogue key travel polled from the "
        "device, and cursor position. Windows key auto-repeat is discarded."),
    "rec.focus_only": "Only while the osu! window is focused",
    "rec.hz_label": "Travel polling rate, Hz:",
    "rec.hz_tip": (
        "1500 means no limit: as fast as the device answers. At 8000 Hz USB "
        "polling that is about 2600 samples per second and ~9% of one core. "
        "The rate actually achieved is shown in the status line."),
    "rec.start": "Start recording",
    "rec.stop": "Stop recording",
    "rec.save": "Save recording…",
    "rec.save_dialog": "Save recording",
    "rec.idle": "Not recording",
    "rec.running": ("Recording… {sec:5.0f} s · presses {presses} · travel "
                    "{travel} ({hz:.0f} Hz) · cursor {cursor} · auto-repeat "
                    "discarded {repeats}"),
    "rec.stopped": ("Stopped. Presses {presses}, auto-repeat discarded "
                    "{repeats}, travel samples {travel} ({hz:.0f} Hz), cursor "
                    "points {cursor}"),
    "rec.failed": "Could not start: {message}",
    "rec.no_analog": "   (no analogue data — device not found)",
    "rec.key": "slot {n} · {name}",
    "rec.saved": "Saved: {path}",
    "rec.depth_head": ("Device thresholds: actuation {trigger:.2f} mm, "
                       "release {release:.2f} mm"),
    "rec.depth_key": "key",
    "rec.depth_n": "presses",
    "rec.depth_median": "median depth",
    "rec.depth_p10": "weakest 10%",
    "rec.depth_margin": "margin to threshold",
    "rec.depth_bottom": "bottomed out",

    "tr.placeholder": ("Analyse a replay on the Analysis tab first — the plan "
                       "is built from its numbers."),
    "tr.none": "This replay did not produce any exercises — everything is "
               "within normal range.",
    "tr.priority": "PRIORITY {n}",
    "tr.scan": "Find maps in my collection",
    "tr.target_bpm": "target BPM:",
    "tr.index_empty": "The beatmap index is empty — build it in Settings.",
    "tr.col_map": "map",
    "tr.col_diff": "difficulty",
    "tr.col_bpm": "stream BPM",
    "tr.col_notes": "notes in stream",
    "tr.col_cs": "CS",
    "tr.col_od": "OD",

    "set.songs": "osu!stable — Songs folder",
    "set.replays": "osu!stable — Replays folder",
    "set.lazer": "osu!lazer — data folder",
    "set.save": "Save settings",
    "set.rebuild": "Rebuild beatmap index",
    "set.saved": "Settings saved",
    "set.scanning": "Scanning… {i}/{total}   {name}",
    "set.done": "Done. Added {added}, {total} in total",
    "set.index_count": "Beatmaps in index: {n}",
    "set.language": "Language",
    "set.language_hint": "applies immediately",
    "set.browse": "Choose folder",

    "sev.high": "IMPORTANT",
    "sev.medium": "WORTH KNOWING",
    "sev.info": "FOR REFERENCE",
    "area.device": "device",
    "area.technique": "technique",
    "area.game": "game settings",

    "find.no_data.title": "No data",
    "find.no_data.detail": "No key presses in this replay could be matched "
                           "to notes.",

    "find.fps.title": "Replay recorded at {fps:.0f} Hz",
    "find.fps.detail": ("A replay frame is written every {ms:.0f} ms, so every "
                        "error here is rounded to that. The measured UR is "
                        "inflated."),
    "find.fps.action": ("Raise the frame limit in osu! (Unlimited). Exact "
                        "timings come from our own recorder, which is accurate "
                        "to about 1 ms."),

    "find.offset.title": "Systematic offset {mean:+.1f} ms ({direction})",
    "find.offset.late": "late",
    "find.offset.early": "early",
    "find.offset.detail": ("Mean error across the whole map is {mean:+.1f} ms. "
                           "An offset this flat is usually not about the hands "
                           "but about audio offset or latency."),
    "find.offset.action": ("Try shifting the universal offset by {shift:+.0f} "
                           "ms. Check it on 5–10 replays first: a single map's "
                           "offset wanders by about ±10 ms and means little on "
                           "its own."),

    "find.hands.title": "Hands are {gap:.1f} ms out of sync",
    "find.hands.detail_left": ("left {left:+.1f} ms, right {right:+.1f} ms. "
                               "The left hand is consistently late."),
    "find.hands.detail_right": ("left {left:+.1f} ms, right {right:+.1f} ms. "
                                "The right hand is consistently late."),
    "find.hands.action_left": ("Device settings cannot fix this — both keys "
                               "have identical thresholds. Metronome work on "
                               "single notes, deliberately pulling the left "
                               "hand forward."),
    "find.hands.action_right": ("Device settings cannot fix this — both keys "
                                "have identical thresholds. Metronome work on "
                                "single notes, deliberately pulling the right "
                                "hand forward."),

    "find.hands_ur.title": "One hand is clearly less consistent ({hand})",
    "find.hands_ur.detail": "Left UR {left:.0f}, right UR {right:.0f}.",
    "find.hands_ur.action": "The {hand} hand has the wider spread — it is what "
                            "caps your accuracy.",

    "find.drift.title": "The hand cannot hold {bpm:.0f} BPM",
    "find.drift.detail": ("Within a stream the error grows by {drift:+.1f} ms "
                          "from start to end ({notes} notes, UR {ur:.0f}, "
                          "{miss:.1f}% misses). Extra presses are only "
                          "{extra:.1f}%, so this is not overstreaming — it is "
                          "a shortfall in speed."),
    "find.drift.action": ("Train stamina at {bpm:.0f} BPM in short bursts. "
                          "Device settings will not help here — they do not "
                          "change how fast a hand moves."),

    "find.overstream.title": "Overstreaming at {bpm:.0f} BPM",
    "find.overstream.detail": ("{extra:.1f}% extra presses with a drift of only "
                               "{drift:+.1f} ms — you are pressing more often "
                               "than there are notes."),
    "find.overstream.action": "Count the notes in a stream instead of chasing "
                              "the rhythm with your fingers.",

    "find.slow_extras.title": "Extra presses in slow sections ({bpm:.0f} BPM)",
    "find.slow_extras.detail": ("{extra:.1f}% of presses land on no note at "
                                "all, even though the tempo is low and the "
                                "hand keeps up (drift {drift:+.1f} ms)."),
    "find.slow_extras.action": ("The problem here is not speed but surplus "
                                "motion — fingers tapping “just in case” "
                                "between notes."),

    "find.double.title": "Looks like double actuation",
    "find.double.detail": ("{n} presses arrived less than 45 ms after the "
                           "previous one on the same key ({pct:.1f}% of all "
                           "presses)."),
    "find.double.action": "Raise RT Release or reduce Rapid Trigger "
                          "sensitivity.",

    "find.no_double.title": "No double actuation detected",
    "find.no_double.detail": ("Repeat presses faster than 45 ms: {n} out of "
                              "{total}. Rapid Trigger is behaving correctly."),
    "find.no_double.action": "There is no reason to change RT.",

    "find.underpress.title": "Presses barely reach the actuation point",
    "find.underpress.detail": ("Typical press depth is {peak:.0f} µm against a "
                               "{trigger:.0f} µm threshold — only "
                               "{margin:.0f} µm of margin."),
    "find.underpress.action": ("Make it more sensitive: lower Trigger from "
                               "{now:.2f} mm to about {suggest:.2f} mm."),

    "tr.ex.stream.title": "Stream stamina at {bpm:.0f} BPM",
    "tr.ex.stream.why": ("At {bpm:.0f} BPM the error grows by {drift:+.1f} ms "
                         "from the start to the end of a stream ({notes} "
                         "notes, UR {ur:.0f}). You start streams on time, so "
                         "the speed is there — what is missing is holding the "
                         "tempo."),
    "tr.ex.stream.how": ("Short bursts: 4 bars of stream at {base:.0f} BPM, "
                         "rest, repeat 10 times. Once drift at {base:.0f} "
                         "falls below 8 ms, raise it by 5 BPM. Long maps at "
                         "your limit hurt here: they train you to tolerate "
                         "dirty tapping rather than to tap cleanly."),
    "tr.ex.stream.check": ("Run a replay through this app and look at the "
                           "{bpm:.0f} BPM row: drift should be under 8 ms."),

    "tr.ex.overstream.title": "Remove extra presses at {bpm:.0f} BPM",
    "tr.ex.overstream.why": ("{extra:.1f}% of presses hit no note at all, even "
                             "though the tempo is low and there is no drift "
                             "({drift:+.1f} ms). Fingers are tapping on spec."),
    "tr.ex.overstream.how": ("Play slow maps deliberately under-tapping: "
                             "better to drop a note than to add a press. "
                             "Counting out loud helps."),
    "tr.ex.overstream.check": "The extras column for this BPM should drop "
                              "below 1%.",

    "tr.ex.aim_jump.title": "Accuracy on jumps from {lo:.0f} px",
    "tr.ex.aim_jump.why": ("On jumps like these {edge:.0f}% of notes are "
                           "caught with the edge of the cursor, and the mean "
                           "overshoot is {over:.1f} px (circle radius "
                           "{radius:.0f} px)."),
    "tr.ex.aim_jump.how": ("Maps with wide spacing at a comfortable BPM, "
                           "deliberately stopping the cursor in the centre "
                           "rather than somewhere inside the circle. A tablet "
                           "helps here: the position is absolute, so the hand "
                           "can memorise the centre."),
    "tr.ex.aim_jump.check": "Edge hits at this distance should fall below 8%.",

    "tr.ex.aim_brake.title": "Cursor braking",
    "tr.ex.aim_brake.why": "{pct:.0f}% of jumps overshoot, by {px:.1f} px on "
                           "average.",
    "tr.ex.aim_brake.how": "Slow maps with wide jumps, focusing on the stop.",
    "tr.ex.aim_brake.check": "Overshoot share should fall below 20%.",

    "tr.ex.hands.title_left": "Hand sync (left is behind)",
    "tr.ex.hands.title_right": "Hand sync (right is behind)",
    "tr.ex.hands.why": "Mean error differs between hands by {gap:.1f} ms.",
    "tr.ex.hands.how_left": ("Metronome, single notes alternating, "
                             "deliberately pulling the left hand forward. "
                             "Device thresholds are irrelevant here — they are "
                             "identical for both keys."),
    "tr.ex.hands.how_right": ("Metronome, single notes alternating, "
                              "deliberately pulling the right hand forward. "
                              "Device thresholds are irrelevant here — they "
                              "are identical for both keys."),
    "tr.ex.hands.check": "Difference between hands under 2 ms.",

    "tr.ex.scatter.title": "Tapping consistency",
    "tr.ex.scatter.why": ("In {n} problem spots the error centre is fine but "
                          "the spread is wide — you hear the tempo, but the "
                          "hand taps unevenly."),
    "tr.ex.scatter.how": "Slow maps with a metronome; the goal is evenness, "
                         "not speed.",
    "tr.ex.scatter.check": "UR on those stretches below 200.",

    "tr.ex.early.title": "Rushing stream starts",
    "tr.ex.early.why": "In {n} spots you were consistently early.",
    "tr.ex.early.how": "Deliberately start streams later than feels right.",
    "tr.ex.early.check": "Mean error on those stretches within ±5 ms.",

    "tab.trainer": "Trainer",
    "view.playback": "Playback",
    "view.tapping": "Tapping",

    "pb.play": "Play",
    "pb.pause": "Pause",
    "pb.jump_placeholder": "Jump to a problem spot…",
    "pb.distance": "cursor {px:.0f} px from centre ({frac:.2f} radius)",
    "pb.error": "hit {ms:+.0f} ms",
    "pb.miss": "MISS",
    "pb.extra": "extra press",

    "tap.hold": "Hold time",
    "tap.hold_value": "{ms:.0f} ms",
    "tap.hold_spread": "spread {spread:.0f} ms",
    "tap.hand_gap": "Hold difference between hands",
    "tap.alternation": "Alternation",
    "tap.single": "Two or more in a row on one hand",
    "tap.max_bpm": "Fastest sustained tempo",
    "tap.fatigue": "Fatigue",
    "tap.fatigue_hint": "UR growth on stream sections, first third to last",
    "tap.repeats": "Repeats under 45 ms on the same key",
    "tap.hist_title": "Interval between presses",
    "tap.hist_x": "interval, ms",
    "tap.roll_title": "Tempo and steadiness over the map",
    "tap.roll_y": "BPM",
    "tap.roll_y2": "UR",
    "tap.runs_title": "How many presses in a row on one hand",
    "tap.col_run": "in a row",
    "tap.col_count": "times",
    "tap.no_data": "Not enough presses in this replay.",

    "aim.speed": "Cursor speed at the press",
    "aim.speed_value": "{v:.2f} px/ms",
    "aim.settle": "Settled in the circle before the press",
    "aim.on_arrival": "Clicked on arrival",
    "aim.on_arrival_hint": "jumps clicked before the cursor settled",
    "aim.col_speed": "speed",
    "aim.col_settle": "settle",

    "trn.info": (
        "Pick a pattern and a tempo: the notes travel to the line and you "
        "answer them. This is not a metronome — there are rests in it, and "
        "entering a run after a rest is what usually costs points. The "
        "metronome still clicks the beat underneath. Presses are read from "
        "the O3C only."),
    "trn.target_bpm": "Target BPM:",
    "trn.duration": "Duration, s:",
    "trn.sound": "Metronome sound",
    "trn.start": "Start",
    "trn.stop": "Stop",
    "trn.card_bpm": "current BPM",
    "trn.card_ur": "UR",
    "trn.card_drift": "drift, ms",
    "trn.card_left": "seconds left",
    "trn.plot_title": "Interval between presses",
    "trn.plot_x": "press",
    "trn.plot_y": "ms",
    "trn.idle": "Set a tempo and press Start.",
    "trn.count_in": "Count-in…",
    "trn.count_in_left": "count-in: {n}",
    "trn.no_device": "Could not start key capture: {message}",
    "trn.too_few": "Too few presses to judge anything.",
    "trn.result_held": (
        "Held it. {hits}/{notes} notes ({acc:.0f}%), hit error {error:+.1f} ms, UR {ur:.0f}, {misses} missed, {extras} extra presses, alternation {alt:.0f}%, around {bpm:.0f} BPM against a target of {target:.0f}."),
    "trn.result_missed": (
        "Not held. {hits}/{notes} notes ({acc:.0f}%), hit error {error:+.1f} ms, UR {ur:.0f}, {misses} missed, {extras} extra presses, alternation {alt:.0f}%, around {bpm:.0f} BPM against a target of {target:.0f}."),

    # --- overview -------------------------------------------------------
    "ov.findings_title": "What we found",
    "ov.summary": "{high} to fix · {medium} worth knowing · {info} "
                  "for reference",
    "ov.fix": "Fix:",
    "ov.legend_title": "How to read this page",
    "ov.legend_body": (
        "<b>Hit error</b> — how far a press was from its note, in "
        "milliseconds. Minus is early, plus is late. One number for a whole "
        "map hides a lot, which is why the table on the right splits it by "
        "tempo.<br><br>"
        "<b>UR</b> — the spread of those errors (ten times their standard "
        "deviation). Lower is steadier: under 150 is tight, over 250 is "
        "loose. It says nothing about early or late, only about how much "
        "you vary.<br><br>"
        "<b>Left and right</b> — the two keys measured apart. A steady "
        "difference between them is a habit, not a device fault: both keys "
        "have the same thresholds.<br><br>"
        "<b>Drift</b> — how much the error grows from the start of a stream "
        "to its end. Past about 8 ms the hand is not holding the tempo: the "
        "notes keep coming and the hand falls behind.<br><br>"
        "<b>Extras</b> — presses that landed on no note at all. Many extras "
        "with little drift is the opposite problem: the fingers are adding "
        "taps rather than running out of speed. Presses during spinners are "
        "not counted here.<br><br>"
        "<b>Misses</b> — notes with no press anywhere inside the 50 "
        "window.<br><br>"
        "<b>300 / 100 / 50 / miss</b> — counted here from the replay against "
        "the beatmap, so a note or two of difference from the score screen "
        "is normal.<br><br>"
        "<b>Severity.</b> IMPORTANT is something to change; WORTH KNOWING "
        "is a real effect that is not costing you much yet; FOR REFERENCE "
        "is a measurement with no action attached."),
    "ov.table_title": "Broken down by tempo",
    "ov.table_hint": "Every stretch of steady spacing in the map, grouped "
                     "into 10 BPM steps. Drift and extras are the two "
                     "columns that tell lack of speed apart from surplus "
                     "taps.",
    "plot.hist_hint": "Green dashes are the edge of the 300 window, amber "
                      "the 100. A hill sitting off the centre line is an "
                      "offset; a wide flat hill is scatter.",
    "plot.timeline_hint": "One dot per note, blue left hand, pink right. "
                          "Bands drifting upwards are stretches where the "
                          "hand fell behind.",

    # --- replay to beatmap alignment ------------------------------------
    "align.suspect": (
        "This replay and this beatmap do not line up — only {pct:.0f}% of "
        "notes have a press anywhere near them. Hit error, aim and playback "
        "below are unreliable. Usually the .osu file was edited after the "
        "play, or the replay is of a different game mode."),
    "align.corrected": (
        "The replay clock was {sec:+.2f} s out against the beatmap and has "
        "been corrected — {pct:.0f}% of notes line up now. osu!stable writes "
        "the first replay frame on a different clock on some plays, and "
        "taken literally it shifts everything by the whole lead-in."),
    "align.searched": (
        "Neither reading of this replay's clock fitted the beatmap, so the "
        "offset was searched for: at {sec:+.2f} s, {pct:.0f}% of notes line "
        "up, and that is what is shown below. It is a guess that fits, not "
        "something the file says — treat the numbers with care."),
    "align.suspect_playback": (
        "The cursor will not follow the notes here: replay and beatmap "
        "agree on only {pct:.0f}% of notes."),
    "align.corrected_playback": (
        "Replay clock corrected by {sec:+.2f} s so the cursor lines up with "
        "the notes."),

    # --- aim ------------------------------------------------------------
    "aim.summary_title": "Numbers",
    "aim.help_title": "Reading the scatter",
    "aim.help_body": (
        "Every dot is one note, drawn where the cursor was relative to the "
        "centre of that note. Up on the plot is up on the playfield.<br><br>"
        "<b>The blue ring</b> is the circle itself at this map's CS. "
        "<b>The dashed ring</b> sits at 0.75 of the radius — dots past it "
        "are edge hits, the ones a small mistake turns into a miss. "
        "<b>The yellow cross</b> is your average dot: if it sits off centre, "
        "your aim is biased in that direction.<br><br>"
        "<b>Dots outside the blue ring are not misses.</b> A replay stores "
        "the cursor only once per frame, so the position used is the one "
        "written nearest the press. On a fast jump the cursor covers a lot "
        "of ground between two frames, and a note hit cleanly can still be "
        "drawn outside the ring. That is why the share outside is shown "
        "next to how far the cursor travels in a single frame: if the frame "
        "rate is low, that share is the recording rather than your aim. "
        "With a high frame rate and a large share, you really are clicking "
        "before the cursor has arrived.<br><br>"
        "<b>Colour</b> is the judgement of the note — blue 300, green 100, "
        "amber 50. Misses are not drawn: there is no press to place them "
        "at. Notes played during a spinner are left out, because a spinner "
        "drags the cursor round the edge of the field."),
    "aim.plot_legend": "blue ring — the circle · dashed ring — 0.75 of the "
                       "radius · yellow cross — your average hit · dot "
                       "colour — 300 / 100 / 50",
    "aim.spread_hint": "mean distance from the centre; under 0.40 is tight, "
                       "over 0.60 means most notes are caught near the edge",
    "aim.edge_hint": "notes caught past 0.75 of the radius — the first ones "
                     "to become misses when the tempo rises",
    "aim.outside": "Outside the circle",
    "aim.outside_hint": "on those notes the cursor was covering about "
                        "{px:.0f} px per replay frame ({ms:.0f} ms), and its "
                        "position is interpolated between frames — enough on "
                        "its own to draw a clean hit just outside. A press "
                        "matched to a note by time alone can also land "
                        "anywhere, where osu! would have wanted the cursor "
                        "inside.",
    "aim.overshoot_hint": "how far past the note the cursor ran before "
                          "coming back — braking late costs both accuracy "
                          "and time",
    "aim.by_jump_hint": "the same numbers split by how far the cursor had "
                        "to travel to reach the note",
    "aim.by_dir_hint": "→ is a jump to the right. One direction clearly "
                       "worse than the rest is usually grip or where the "
                       "device sits on the desk.",

    # --- problem spots --------------------------------------------------
    "ep.causes_hint": "fell behind — the error grew inside the stream · "
                      "rushed — consistently early · scatter — the centre "
                      "is fine but the spread is wide · aim — the cursor, "
                      "not the hands",

    # --- tapping --------------------------------------------------------
    "tap.help_title": "How to read this",
    "tap.help_body": (
        "These numbers describe the presses themselves, not how close they "
        "were to the notes — a hand can be perfectly even and still play "
        "the wrong rhythm.<br><br>"
        "<b>Alternation</b> near 100% means the hands took turns properly. "
        "Every run of two or more on one hand is a moment one hand carried "
        "the stream alone, which is where tempo is usually lost.<br><br>"
        "<b>Fastest sustained tempo</b> is the quickest sixteen presses in "
        "a row anywhere in the map, read as stream BPM. It is a ceiling, "
        "not something you can hold.<br><br>"
        "<b>Fatigue</b> compares UR in the first third of the map to the "
        "last, counting only stretches at stream tempo. A large positive "
        "number means the hands came apart as the map went on.<br><br>"
        "<b>Repeats under 45 ms</b> on the same key are faster than a "
        "finger can move. Anything above zero points at the switch or at "
        "Rapid Trigger, not at you."),
    "tap.hold_hint": "how long a key stays down; the spread matters more "
                     "than the value itself",
    "tap.hand_gap_hint": "left hold minus right hold",
    "tap.alternation_hint": "share of presses that changed hand",
    "tap.single_hint": "share of presses where one hand went twice or more "
                       "in a row",
    "tap.max_bpm_hint": "fastest sixteen presses in a row, as stream BPM",
    "tap.repeats_hint": "the same key twice inside 45 ms — the signature of "
                        "double actuation",
    "tap.runs_hint": "1 means the hands alternated; 2 or more means one "
                     "hand tapped several notes on its own",
    "tap.hist_hint": "each peak is one note spacing used by the map; the "
                     "tallest is the tempo you spent the most time at",
    "tap.roll_hint": "blue — the tempo of your presses, pink — how uneven "
                     "they were at that point",

    # --- playback -------------------------------------------------------
    "pb.keys_hint": "Space — play / pause · ← → — one second · Shift + ← → "
                    "— five seconds · click the strip above to jump",
    "pb.legend": "white dot — the cursor, ringed while a key is held · "
                 "blue and pink dots on the trail — where each press "
                 "landed, left and right · red ring — a press on no note · "
                 "yellow trail — the last 0.4 s · red dashes — from the "
                 "cursor to the note being judged · circle colour — "
                 "300 / 100 / 50 / miss",

    # --- recording ------------------------------------------------------
    "rec.controls_title": "Recording",
    "rec.keys_hint": "Watching keys: {keys} — change them in Settings",
    "rec.travel_title": "Key travel, live",
    "rec.travel_hint": "0 at rest, 4000 µm with the switch at the bottom",
    "rec.depth_title": "How deep you actually press",
    "rec.depth_hint": "Taken after the recording from the analogue samples "
                      "inside each press. The margin column is what is left "
                      "between your weakest presses and the actuation "
                      "point.",

    # --- training plan --------------------------------------------------
    "tr.head_title": "Training plan",
    "tr.head_body": "{n} things came out of this replay. Start with: "
                    "{first}",
    "tr.problem": "What is wrong",
    "tr.drill": "What to play",
    "tr.target": "Done when",
    "tr.open_trainer": "Practise at {bpm:.0f} BPM",
    "tr.maps_title": "Maps in your collection",
    "tr.maps_hint": "Streams at the target tempo, taken from the beatmaps "
                    "in the index.",

    # --- settings -------------------------------------------------------
    "set.general_title": "General",
    "set.keys_title": "Device keys",
    "set.keys_hint": "Press the button, then press the key on your device. "
                     "Only these keys are recorded — nothing else you type "
                     "is ever seen. Esc cancels.",
    "set.key_slot": "Slot {n}",
    "set.key_slot_hint": "analogue channel {n}",
    "set.key_prompt": "press a key…",
    "set.key_taken": "{key} is already bound to another slot",
    "set.keys_now": "Bound: {keys}",
    "set.thresholds_title": "Device thresholds",
    "set.thresholds_hint": "The actuation and release points set in the "
                           "SayoDevice configurator. Nothing is written to "
                           "the device: these are only used to work out how "
                           "much margin your presses leave.",
    "set.trigger": "Actuation",
    "set.release": "Release",
    "set.paths_title": "Folders and beatmap index",
    "set.paths_hint": "Where replays and beatmaps live. The index is what "
                      "turns a replay into the .osu file it was played on.",

    # --- trainer --------------------------------------------------------
    "trn.controls_title": "Settings",
    "trn.keys_hint": "Reading keys: {keys} — change them in Settings",
    "trn.card_bpm_hint": "over the last sixteen presses",
    "trn.card_ur_hint": "spread of the hit error, as the game counts it",
    "trn.card_drift_hint": "how far the tempo sits from the target",
    "trn.card_left_hint": "seconds remaining",
    "trn.plot_hint": "the green line is the interval the target BPM asks "
                     "for; each dot is one press",

    "unit.ms": "ms",
    "trn.result_noise": ("{n} of {total} gaps were under {ms:.0f} ms — closer together than a hand can tap, and left out. The app kept up throughout, so this is the switch bouncing: raise RT Release in the SayoDevice configurator."),
    "trn.result_stalled": ("{n} of {total} gaps were under {ms:.0f} ms and were left out. This machine stalled {stalls} times while reading your presses, worst {worst} ms, so some of those are presses that arrived together rather than doubles you made. Close what else is running and try again."),

    # --- trainer patterns -----------------------------------------------
    "trn.pattern": "Pattern:",
    "trn.pat.stream": "Continuous stream",
    "trn.pat.stream_hint": "No rests at all. Trains stamina and nothing "
                           "else — useful, but it is not what a map asks "
                           "of you.",
    "trn.pat.long": "Long streams",
    "trn.pat.long_hint": "Sixteen notes, then two beats of rest. Long "
                         "enough for the hand to start drifting, short "
                         "enough to recover between them.",
    "trn.pat.burst": "Bursts",
    "trn.pat.burst_hint": "Runs of five to nine notes with a beat and a "
                          "half between them, in a shuffled order so you "
                          "cannot learn the shape. This is the one that "
                          "shows whether you enter a burst on time.",
    "trn.pat.triple": "Triples",
    "trn.pat.triple_hint": "Three notes, one beat of rest, repeat. Short "
                           "enough that the whole run is the entry.",
    "trn.pat.double": "Doubles",
    "trn.pat.double_hint": "Two notes, one beat of rest, repeat. The "
                           "hardest thing to keep clean, because there is "
                           "no run to settle into.",
    "trn.pat.mixed": "Mixed",
    "trn.pat.mixed_hint": "Anything from one note to eight, in random "
                          "order. Closest to an actual map.",

    "trn.lane_idle": "The rhythm appears here once you start",
    "trn.lane_hint": "Notes travel to the white line — press as each one "
                     "crosses it. The larger blue circle opens a run. "
                     "Green, amber, red is how close you were; a dotted "
                     "red circle is a note nothing answered. The ticks "
                     "underneath are your presses, blue for the left key, "
                     "pink for the right.",

    "trn.card_error": "hit error",
    "trn.card_error_hint": "minus early / plus late, against the rhythm",
    "trn.card_hits": "hits",
    "trn.card_hits_hint": "notes answered, out of those gone past",

    "trn.result_opener_late": "Runs are entered {gap:.0f} ms later than "
                              "they are carried — the tempo is there, the "
                              "start is not. Come in earlier than feels "
                              "right after a rest.",
    "trn.result_opener_early": "Runs are entered {gap:.0f} ms earlier than "
                               "they are carried — you are jumping the "
                               "rest, then holding on.",
}
