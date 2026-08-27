import hid
devs = hid.enumerate()
print(f"total HID devices: {len(devs)}\n")
seen = {}
for d in devs:
    vid, pid = d['vendor_id'], d['product_id']
    key = (vid, pid)
    seen.setdefault(key, []).append(d)

for (vid, pid), lst in sorted(seen.items()):
    mfr = (lst[0].get('manufacturer_string') or '').strip()
    prod = (lst[0].get('product_string') or '').strip()
    mark = "  <<< SAYO" if vid == 0x8089 else ""
    if vid == 0x8089 or 'sayo' in (mfr+prod).lower():
        mark = "  <<< SAYO"
    print(f"VID={vid:#06x} PID={pid:#06x}  {mfr!r} / {prod!r}  ifaces={len(lst)}{mark}")
    if mark:
        for d in lst:
            print(f"    usage_page={d['usage_page']:#06x} usage={d['usage']:#06x} "
                  f"iface={d['interface_number']} path={d['path']}")
