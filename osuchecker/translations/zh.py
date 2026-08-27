STRINGS = {
    "app.title": "osu-checker — SayoDevice O3C",
    "app.subtitle": "SayoDevice O3C 游戏分析工具",

    "tab.analysis": "分析",
    "tab.record": "录制",
    "tab.training": "训练",
    "tab.settings": "设置",

    "analysis.drop_hint": "把 .osr 拖到这里，或点击“打开回放”",
    "analysis.open_replay": "打开回放…",
    "analysis.last_replay": "最新的 osu! 回放",
    "analysis.attach_session": "附加录制文件…",
    "analysis.attach_session_tip": (
        "来自“录制”标签页的文件。可加入真实的按键行程深度，这是回放里没有的。"),
    "analysis.attached": "录制：{name}",
    "analysis.no_replay": "尚未载入回放",
    "analysis.analysing": "正在分析 {name}…",
    "analysis.error": "错误：{message}",
    "analysis.no_osr_found": "在设置指定的文件夹中没有找到任何 .osr",
    "analysis.session_unreadable": "无法读取录制文件：{message}",
    "analysis.session_no_presses": "录制中没有带行程数据的按键，无法计算深度",
    "analysis.no_data": "没有数据",
    "analysis.map_not_found": (
        "索引中找不到此回放对应的谱面。如果谱面是最近添加的，请在“设置”中"
        "重建索引。"),

    "view.overview": "总览",
    "view.aim": "瞄准",
    "view.episodes": "问题片段",

    "stat.error": "击打误差",
    "stat.error_hint": "负为偏早 / 正为偏晚",
    "stat.ur": "UR",
    "stat.ur_hint": "回放记录 {fps:.0f} 帧/秒",
    "stat.left": "左手",
    "stat.right": "右手",
    "stat.hand_hint": "UR {ur:.0f} · {n} 个音符",
    "stat.counts": "300/100/50/miss",
    "stat.counts_hint": "本程序的统计",
    "stat.aim_spread": "瞄准离散度",
    "stat.aim_spread_hint": "以圆圈半径为单位",

    "plot.hist_title": "击打误差分布",
    "plot.hist_x": "误差（负为偏早 / 正为偏晚），毫秒",
    "plot.timeline_title": "整张谱面的误差变化",
    "plot.timeline_x": "时间，秒",
    "plot.timeline_y": "误差，毫秒",

    "hand.left": "左手",
    "hand.right": "右手",

    "col.bpm": "BPM",
    "col.notes": "音符",
    "col.error": "误差",
    "col.ur": "UR",
    "col.drift": "漂移",
    "col.misses": "miss",
    "col.extras": "多余",

    "aim.plot_title": "光标相对圆圈中心的落点",
    "aim.axis_px": "osu! 像素",
    "aim.by_jump": "按跳跃距离",
    "aim.by_dir": "按跳跃方向",
    "aim.col_jump": "跳跃，px",
    "aim.col_notes": "音符",
    "aim.col_spread": "离散度",
    "aim.col_edge": "边缘命中",
    "aim.col_over": "过冲",
    "aim.col_over_pct": "过冲占比",
    "aim.col_dir": "方向",
    "aim.no_data": "此回放没有光标数据。",
    "aim.radius": "圆圈半径",
    "aim.bias": "中心偏移",
    "aim.bias_hint": "黄色十字表示你的平均落点",
    "aim.spread": "离散度",
    "aim.spread_value": "半径的 {value:.2f} 倍",
    "aim.edge": "边缘命中",
    "aim.overshoot": "过冲",
    "aim.overshoot_value": "{px:.1f} px，占 {pct:.0f}% 的跳跃",

    "ep.head": "谱面中失分最多的片段，以及数据显示的原因",
    "ep.col_time": "时间",
    "ep.col_tempo": "速度",
    "ep.col_notes": "音符",
    "ep.col_loss": "失分",
    "ep.col_cause": "原因",
    "ep.col_what": "具体情况",
    "ep.cause.late": "跟不上",
    "ep.cause.early": "抢拍",
    "ep.cause.scatter": "离散",
    "ep.cause.aim": "瞄准",
    "ep.cause.mixed": "混合",
    "ep.what.late": "误差从 {early:+.0f} 毫秒漂到 {late:+.0f} 毫秒，手跟不上节奏",
    "ep.what.early": "持续偏早，平均 {mean:+.0f} 毫秒",
    "ep.what.scatter": "中心正常（{mean:+.0f} 毫秒），但 UR 达 {ur:.0f}，敲击不稳",
    "ep.what.aim": "光标距中心 {spread:.2f} 倍半径，{edge:.0f}% 打在边缘，"
                   "问题在瞄准而非敲击",
    "ep.what.mixed": "误差 {mean:+.0f} 毫秒，UR {ur:.0f}",
    "ep.miss": "{n} 个 miss",
    "ep.hundred": "{n}×100",
    "ep.fifty": "{n}×50",
    "ep.none": "—",

    "rec.info": (
        "同时记录三个来源：仅来自 O3C 的按键（Raw Input 按 "
        "VID_8089&PID_0009 过滤）、通过轮询设备得到的模拟键程，以及光标"
        "位置。Windows 的按键自动重复会被过滤掉。"),
    "rec.focus_only": "仅在 osu! 窗口处于前台时记录",
    "rec.hz_label": "键程轮询频率，Hz：",
    "rec.hz_tip": (
        "1500 表示不限制，取决于设备能回应多快。在 8000 Hz USB 轮询下约为"
        "每秒 2600 次采样，占用约 9% 的单核。实际达到的频率显示在状态栏。"),
    "rec.start": "开始录制",
    "rec.stop": "停止录制",
    "rec.save": "保存录制…",
    "rec.save_dialog": "保存录制",
    "rec.idle": "未在录制",
    "rec.running": ("录制中… {sec:5.0f} 秒 · 按键 {presses} · 键程 {travel} "
                    "（{hz:.0f} Hz） · 光标 {cursor} · 已过滤自动重复 "
                    "{repeats}"),
    "rec.stopped": ("已停止。按键 {presses}，已过滤自动重复 {repeats}，"
                    "键程采样 {travel}（{hz:.0f} Hz），光标点 {cursor}"),
    "rec.failed": "无法启动：{message}",
    "rec.no_analog": "   （没有模拟数据，未找到设备）",
    "rec.key": "按键 {name}",
    "rec.saved": "已保存：{path}",
    "rec.depth_head": "设备阈值：触发 {trigger:.2f} 毫米，释放 {release:.2f} 毫米",
    "rec.depth_key": "按键",
    "rec.depth_n": "次数",
    "rec.depth_median": "深度中位数",
    "rec.depth_p10": "最浅的 10%",
    "rec.depth_margin": "距阈值余量",
    "rec.depth_bottom": "触底",

    "tr.placeholder": "请先在“分析”标签页分析一个回放，训练计划由其数据生成。",
    "tr.none": "这个回放没有产生具体的训练项，各项指标都在正常范围内。",
    "tr.priority": "优先级 {n}",
    "tr.why": "原因：",
    "tr.how": "做法：",
    "tr.check": "验收：",
    "tr.scan": "从我的谱面库中挑选",
    "tr.target_bpm": "目标 BPM：",
    "tr.index_empty": "谱面索引为空，请先在“设置”中建立索引。",
    "tr.col_map": "谱面",
    "tr.col_diff": "难度",
    "tr.col_bpm": "连打 BPM",
    "tr.col_notes": "连打音符数",
    "tr.col_cs": "CS",
    "tr.col_od": "OD",

    "set.songs": "osu!stable — Songs 文件夹",
    "set.replays": "osu!stable — Replays 文件夹",
    "set.lazer": "osu!lazer — 数据文件夹",
    "set.save": "保存设置",
    "set.rebuild": "重建谱面索引",
    "set.saved": "设置已保存",
    "set.scanning": "扫描中… {i}/{total}   {name}",
    "set.done": "完成。新增 {added}，共 {total}",
    "set.index_count": "索引中的谱面：{n}",
    "set.language": "语言",
    "set.language_hint": "立即生效",
    "set.browse": "选择文件夹",

    "sev.high": "重要",
    "sev.medium": "值得注意",
    "sev.info": "参考",
    "area.device": "设备",
    "area.technique": "技术",
    "area.game": "游戏设置",

    "find.no_data.title": "没有数据",
    "find.no_data.detail": "回放中没有能与音符对应上的按键。",

    "find.fps.title": "回放以 {fps:.0f} Hz 记录",
    "find.fps.detail": ("回放每 {ms:.0f} 毫秒才写入一帧，因此这里的所有误差都"
                        "被取整到这个精度，测得的 UR 偏高。"),
    "find.fps.action": ("在 osu! 中提高帧数上限（Unlimited）。精确的时间数据"
                        "来自本程序的录制功能，精度约 1 毫秒。"),

    "find.offset.title": "系统性偏移 {mean:+.1f} 毫秒（{direction}）",
    "find.offset.late": "偏晚",
    "find.offset.early": "偏早",
    "find.offset.detail": ("整张谱面的平均误差为 {mean:+.1f} 毫秒。这么平稳的"
                           "偏移通常不是手的问题，而是音频偏移或延迟。"),
    "find.offset.action": ("可以尝试把 universal offset 调整 {shift:+.0f} 毫秒。"
                           "务必用 5–10 个回放验证：单张谱面的偏移会有 ±10 "
                           "毫秒的浮动，单看一张说明不了什么。"),

    "find.hands.title": "两手不同步，相差 {gap:.1f} 毫秒",
    "find.hands.detail_left": ("左手 {left:+.1f} 毫秒，右手 {right:+.1f} 毫秒。"
                               "左手持续偏晚。"),
    "find.hands.detail_right": ("左手 {left:+.1f} 毫秒，右手 {right:+.1f} 毫秒。"
                                "右手持续偏晚。"),
    "find.hands.action_left": ("调设备参数解决不了这个问题，两个键的阈值本来"
                               "就一样。用节拍器练单点，有意识地把左手往前带。"),
    "find.hands.action_right": ("调设备参数解决不了这个问题，两个键的阈值本来"
                                "就一样。用节拍器练单点，有意识地把右手往前带。"),

    "find.hands_ur.title": "有一只手明显更不稳（{hand}）",
    "find.hands_ur.detail": "左手 UR {left:.0f}，右手 UR {right:.0f}。",
    "find.hands_ur.action": "{hand} 的离散度更大，正是它限制了你的精度。",

    "find.drift.title": "手跟不上 {bpm:.0f} BPM 的节奏",
    "find.drift.detail": ("在一段连打之内，误差从头到尾增加了 {drift:+.1f} 毫秒"
                          "（{notes} 个音符，UR {ur:.0f}，miss {miss:.1f}%）。"
                          "多余按键只有 {extra:.1f}%，所以这不是多打，而是"
                          "速度不够。"),
    "find.drift.action": ("用短段落练 {bpm:.0f} BPM 的耐力。设备设置在这里帮"
                          "不上忙，它改变不了手的速度。"),

    "find.overstream.title": "在 {bpm:.0f} BPM 上多打",
    "find.overstream.detail": ("多余按键达 {extra:.1f}%，而漂移只有 "
                               "{drift:+.1f} 毫秒，说明你按的次数比音符还多。"),
    "find.overstream.action": "数清连打里的音符，而不是用手指去追节奏。",

    "find.slow_extras.title": "慢速段落里的多余按键（{bpm:.0f} BPM）",
    "find.slow_extras.detail": ("有 {extra:.1f}% 的按键没有落在任何音符上，"
                                "而这里节奏并不快，手完全跟得上"
                                "（漂移 {drift:+.1f} 毫秒）。"),
    "find.slow_extras.action": "问题不在速度，而在多余动作，手指在音符之间"
                               "“预备性”地敲击。",

    "find.double.title": "疑似双击触发",
    "find.double.detail": ("有 {n} 次按键在同一个键上距上一次不到 45 毫秒"
                           "（占全部按键的 {pct:.1f}%）。"),
    "find.double.action": "提高 RT Release，或降低 Rapid Trigger 灵敏度。",

    "find.no_double.title": "未发现双击触发",
    "find.no_double.detail": ("快于 45 毫秒的重复按键：{total} 次中有 {n} 次。"
                              "Rapid Trigger 工作正常。"),
    "find.no_double.action": "没有理由改动 RT。",

    "find.underpress.title": "按压深度勉强达到触发点",
    "find.underpress.detail": ("典型按压深度为 {peak:.0f} 微米，而阈值是 "
                               "{trigger:.0f} 微米，余量只有 {margin:.0f} 微米。"),
    "find.underpress.action": ("提高灵敏度：把 Trigger 从 {now:.2f} 毫米降到 "
                               "{suggest:.2f} 毫米左右。"),

    "tr.ex.stream.title": "{bpm:.0f} BPM 连打耐力",
    "tr.ex.stream.why": ("在 {bpm:.0f} BPM 上，一段连打从头到尾误差增加 "
                         "{drift:+.1f} 毫秒（{notes} 个音符，UR {ur:.0f}）。"
                         "连打的开头你踩得准，说明速度是够的，缺的是把节奏"
                         "维持住。"),
    "tr.ex.stream.how": ("短段落练习：在 {base:.0f} BPM 上打 4 小节连打，休息，"
                         "重复 10 次。当 {base:.0f} 的漂移降到 8 毫秒以下，"
                         "再加 5 BPM。在极限上刷长图反而有害，那是在训练自己"
                         "忍受脏的敲击，而不是练干净。"),
    "tr.ex.stream.check": ("把回放放进本程序，看 {bpm:.0f} BPM 那一行："
                           "漂移应当小于 8 毫秒。"),

    "tr.ex.overstream.title": "消除 {bpm:.0f} BPM 上的多余按键",
    "tr.ex.overstream.why": ("有 {extra:.1f}% 的按键没有落在任何音符上，而这里"
                             "节奏很慢，也没有漂移（{drift:+.1f} 毫秒）。"
                             "手指在“预备性”地敲。"),
    "tr.ex.overstream.how": ("有意识地少打：宁可漏掉一个音符，也不要多按一下。"
                             "出声数拍会有帮助。"),
    "tr.ex.overstream.check": "该 BPM 的“多余”一列应降到 1% 以下。",

    "tr.ex.aim_jump.title": "{lo:.0f} px 以上跳跃的准度",
    "tr.ex.aim_jump.why": ("这类跳跃中有 {edge:.0f}% 的音符是用边缘蹭到的，"
                           "平均过冲 {over:.1f} px（圆圈半径 {radius:.0f} px）。"),
    "tr.ex.aim_jump.how": ("在舒适的 BPM 下打间距大的图，有意识地把光标停在"
                           "中心，而不是“落在圈里就行”。数位板在这里有优势："
                           "位置是绝对的，手可以记住中心。"),
    "tr.ex.aim_jump.check": "该距离下的“边缘命中”应降到 8% 以下。",

    "tr.ex.aim_brake.title": "光标制动",
    "tr.ex.aim_brake.why": "{pct:.0f}% 的跳跃存在过冲，平均 {px:.1f} px。",
    "tr.ex.aim_brake.how": "打慢速大跳的图，重点放在停住上。",
    "tr.ex.aim_brake.check": "过冲比例应降到 20% 以下。",

    "tr.ex.hands.title_left": "双手同步（左手偏慢）",
    "tr.ex.hands.title_right": "双手同步（右手偏慢）",
    "tr.ex.hands.why": "两手的平均误差相差 {gap:.1f} 毫秒。",
    "tr.ex.hands.how_left": ("节拍器，双手交替单点，有意识地把左手往前带。"
                             "设备阈值与此无关，两个键本来就一样。"),
    "tr.ex.hands.how_right": ("节拍器，双手交替单点，有意识地把右手往前带。"
                              "设备阈值与此无关，两个键本来就一样。"),
    "tr.ex.hands.check": "两手差异小于 2 毫秒。",

    "tr.ex.scatter.title": "敲击稳定性",
    "tr.ex.scatter.why": ("在 {n} 个问题片段中，误差中心是正常的，但离散度很大"
                          "，说明你听得准节奏，只是手敲得不匀。"),
    "tr.ex.scatter.how": "配节拍器打慢图，目标是均匀而不是快。",
    "tr.ex.scatter.check": "这些片段的 UR 低于 200。",

    "tr.ex.early.title": "连打起手抢拍",
    "tr.ex.early.why": "在 {n} 个片段中你持续偏早。",
    "tr.ex.early.how": "有意识地比“感觉该按”的时候更晚一点开始连打。",
    "tr.ex.early.check": "这些片段的平均误差在 ±5 毫秒以内。",
}
